from flask import Flask, render_template, request, redirect, session, url_for, flash
from db import get_db, close_db
from admin_routes import admin_bp
from user_routes import user_bp
from config import Config
import bcrypt
from ldap_auth import authenticate_user, get_user_info
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__) 
app.secret_key = Config.SECRET_KEY

app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

@app.teardown_appcontext
def teardown_db(exception):
    close_db()

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.route('/')
def landing():
    if 'user_id' in session:
        session.clear()
    return render_template('landing.html')

@app.route('/home')
def home():
    if 'user_id' in session:
        if session.get('is_admin'):
            return redirect(url_for('admin'))
        elif session.get('is_editor'):
            return redirect(url_for('admin'))  # TODO: Create separate editor homepage
        else:
            return redirect(url_for('user'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        logger.info(f"Login attempt initiated for user: {username}")
        
        # Verificar si el usuario existe en la BD local (requerido para login)
        db = get_db()
        cur = db.cursor()
        cur.execute(
        'SELECT user_id, username, password, is_admin, is_editor, is_commentator FROM users WHERE username = %s',
        (username, ))
        user = cur.fetchone()
        cur.close()
        
        if not user:
            logger.warning(f"User {username} not found in local database - access denied")
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
        
        # Intentar autenticación LDAP primero
        ldap_authenticated = authenticate_user(username, password)
        
        if ldap_authenticated:
            logger.info(f"LDAP authentication successful for user: {username}")
            # Login exitoso vía LDAP
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['is_admin'] = user[3]          
            session['is_editor'] = user[4]         
            session['is_commentator'] = user[5]   
            return redirect(url_for('home'))
        else:
            # Si falla LDAP, intentar con contraseña local (bcrypt)
            if user[2] and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
                logger.info(f"Local authentication successful for user: {username}")
                session['user_id'] = user[0]
                session['username'] = user[1]
                session['is_admin'] = user[3]
                session['is_editor'] = user[4]
                session['is_commentator'] = user[5]  
                return redirect(url_for('home'))
            else:
                logger.warning(f"Authentication failed for user: {username} - invalid credentials")
                flash('Invalid username or password', 'error')
                return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            db = get_db()
            cur = db.cursor()
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']

            # Check if the username already exists
            cur.execute('SELECT * FROM users WHERE username = %s',
                        (username, ))
            existing_user = cur.fetchone()
            if existing_user:
                flash('Username already taken', 'error')
                return redirect(url_for('register'))

            # Check if the email already exists
            cur.execute('SELECT * FROM users WHERE email = %s', (email, ))
            existing_email = cur.fetchone()
            if existing_email:
                flash('Email already registered', 'error')
                return redirect(url_for('register'))

            # Hash the password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            cur.execute(
                'INSERT INTO users (username, password, email, is_admin, is_editor) VALUES (%s, %s, %s, %s, %s)',
                (username, hashed_password, email, False, False))
            db.commit()
            cur.close()
            flash('Registration successful', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.rollback()
            print("Error: ", str(e))
            flash('Registration failed', 'error')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user_id' not in session:
        flash('You need to log in to search', 'error')
        return redirect(url_for('login'))

    results = []
    query = ""
    if request.method == 'POST':
        query = request.form['query']
        db = get_db()
        cur = db.cursor()

        # Search in teams
        cur.execute(
            "SELECT team_id, name, 'team' AS source FROM teams WHERE name ILIKE %s",
            ('%' + query + '%', ))
        results.extend(cur.fetchall())

        # Search in coaches
        cur.execute(
            "SELECT coach_id, name, 'coach' AS source FROM coaches WHERE name ILIKE %s",
            ('%' + query + '%', ))
        results.extend(cur.fetchall())

        # Search in players
        cur.execute(
            "SELECT player_id, name, 'player' AS source FROM players WHERE name ILIKE %s",
            ('%' + query + '%', ))
        results.extend(cur.fetchall())

        # Search in stadiums
        cur.execute(
            "SELECT stadium_id, name, 'stadium' AS source FROM stadiums WHERE name ILIKE %s",
            ('%' + query + '%', ))
        results.extend(cur.fetchall())

        # Search in sports
        cur.execute(
            "SELECT sport_id, name, 'sport' AS source FROM sports WHERE name ILIKE %s",
            ('%' + query + '%', ))
        results.extend(cur.fetchall())

        cur.close()

    return render_template('search.html', results=results, query=query)

@app.route('/admin')
def admin():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # TODO: Separate admin and editor homepages
    # For now, both admins and editors use the same page but with different permissions
    if not session.get('is_admin') and not session.get('is_editor'):
        flash('Access denied. Admin or editor privileges required.', 'error')
        return redirect(url_for('user'))
    
    return render_template('admin.html')

@app.route('/editor')
def editor():
    # TODO: Create separate editor homepage
    # Temporarily redirecting editors to admin page with limited permissions
    if 'user_id' not in session or not session.get('is_editor'):
        return redirect(url_for('login'))
    return redirect(url_for('admin'))

@app.route('/user')
def user():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Check if user is admin or editor and redirect accordingly
    if session.get('is_admin'):
        return redirect(url_for('admin'))
    elif session.get('is_editor'):
        return redirect(url_for('admin'))  # TODO: Redirect to editor homepage when created
    
    # Regular user logic
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT * FROM users;')
    users = cur.fetchall()
    cur.close()
    return render_template('user.html', users=users)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    # TODO: Restrict this route to admins only
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            db = get_db()
            cur = db.cursor()
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']

            # Hash the password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            cur.execute(
                'INSERT INTO users (username, password, email, is_admin, is_editor) VALUES (%s, %s, %s, %s, %s)',
                (username, hashed_password, email, False, False))
            db.commit()
            cur.close()
            flash('User added successfully', 'success')
            return redirect(url_for('user'))
        except Exception as e:
            db.rollback()
            print("Error: ", str(e))
            flash('Failed to add user', 'error')
            return redirect(url_for('add_user'))
    return render_template('add_user.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    user_id = session['user_id']

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if the username already exists
        cur.execute(
            'SELECT * FROM users WHERE username = %s AND user_id != %s',
            (username, user_id))
        existing_user = cur.fetchone()
        if existing_user:
            flash('Username already taken', 'error')
            return redirect(url_for('profile'))

        # Check if the email already exists
        cur.execute('SELECT * FROM users WHERE email = %s AND user_id != %s',
                    (email, user_id))
        existing_email = cur.fetchone()
        if existing_email:
            flash('Email already registered', 'error')
            return redirect(url_for('profile'))

        # Hash the password if it is updated
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        cur.execute(
            'UPDATE users SET username = %s, email = %s, password = %s WHERE user_id = %s',
            (username, email, hashed_password, user_id))
        db.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))

    cur.execute('SELECT username, email FROM users WHERE user_id = %s',
                (user_id, ))
    user = cur.fetchone()
    cur.close()

    return render_template('profile.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)