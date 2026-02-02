from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from functools import wraps
from db import get_db

user_bp = Blueprint('user', __name__)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to be logged in to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrap

@user_bp.route('/user')
@login_required
def user_dashboard():
    return render_template('user_dashboard.html')

@user_bp.route('/user/teams')
@login_required
def user_teams():
    db = get_db()
    cur = db.cursor()

    # Get filter parameters from the request
    sport_id = request.args.get('sport_id')
    faculty_id = request.args.get('faculty_id')

    # Fetch available sports and faculties for filtering
    cur.execute('SELECT sport_id, name FROM sports')
    sports = cur.fetchall()

    cur.execute('SELECT faculty_id, name FROM faculties ORDER BY faculty_id ASC')
    faculties = cur.fetchall()

    # Build the base query
    query = """
        SELECT team_id, name, crestURL 
        FROM teams
        WHERE 1=1
    """
    filters = []

    # Add filters based on the selected values
    if sport_id:
        query += " AND sport_id = %s"
        filters.append(sport_id)
    if faculty_id:
        query += " AND faculty_id = %s"
        filters.append(faculty_id)

    query += " LIMIT %s OFFSET %s"
    filters.append(20)
    filters.append((request.args.get('page', 1, type=int) - 1) * 20)

    cur.execute(query, filters)
    teams = cur.fetchall()

    count_query = 'SELECT COUNT(*) FROM teams WHERE 1=1'
    count_filters = []
    if sport_id:
        count_query += " AND sport_id = %s"
        count_filters.append(sport_id)
    if faculty_id:
        count_query += " AND faculty_id = %s"
        count_filters.append(faculty_id)

    cur.execute(count_query, count_filters)
    total_teams = cur.fetchone()[0]
    cur.close()

    total_pages = (total_teams + 19) // 20

    return render_template('user_teams.html', teams=teams, page=request.args.get('page', 1, type=int),
                           total_pages=total_pages, sports=sports, faculties=faculties, max=max, min=min, str=str)

@user_bp.route('/user/players')
@login_required
def user_players():
    db = get_db()
    cur = db.cursor()

    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page

    # Get filter parameters from the request
    sport_id = request.args.get('sport_id')
    faculty_id = request.args.get('faculty_id')
    team_id = request.args.get('team_id')
    position = request.args.get('position')

    # Fetch available sports, faculties, teams, and positions for filtering
    cur.execute('SELECT sport_id, name FROM sports')
    sports = cur.fetchall()

    cur.execute('SELECT faculty_id, name FROM faculties ORDER BY faculty_id ASC')
    faculties = cur.fetchall()

    cur.execute('SELECT team_id, name FROM teams')
    teams = cur.fetchall()

    positions = ['Goalkeeper', 'Defence', 'Midfield', 'Offence']

    # Build the base query
    query = """
        SELECT p.player_id, p.name, p.position, t.crestURL, t.name
        FROM players p
        JOIN teams t ON p.team_id = t.team_id
        WHERE 1=1
    """
    filters = []

    # Add filters based on the selected values
    if sport_id:
        query += " AND t.sport_id = %s"
        filters.append(sport_id)
    if faculty_id:
        query += " AND t.faculty_id = %s"
        filters.append(faculty_id)
    if team_id:
        query += " AND p.team_id = %s"
        filters.append(team_id)
    if position:
        query += " AND p.position = %s"
        filters.append(position)

    query += " LIMIT %s OFFSET %s"
    filters.append(per_page)
    filters.append(offset)

    cur.execute(query, filters)
    players = cur.fetchall()

    count_query = '''
        SELECT COUNT(*) 
        FROM players p 
        JOIN teams t ON p.team_id = t.team_id 
        WHERE 1=1
    '''
    count_filters = []
    if sport_id:
        count_query += " AND t.sport_id = %s"
        count_filters.append(sport_id)
    if faculty_id:
        count_query += " AND t.faculty_id = %s"
        count_filters.append(faculty_id)
    if team_id:
        count_query += " AND p.team_id = %s"
        count_filters.append(team_id)
    if position:
        count_query += " AND p.position = %s"
        count_filters.append(position)

    cur.execute(count_query, count_filters)
    total_players = cur.fetchone()[0]
    cur.close()

    total_pages = (total_players + per_page - 1) // per_page

    return render_template('user_players.html', players=players, page=page, total_pages=total_pages,
                           sports=sports, faculties=faculties, teams=teams, positions=positions,
                           max=max, min=min, str=str)

@user_bp.route('/user/sports')
@login_required
def user_sports():
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT sport_id, name FROM sports')
    sports = cur.fetchall()
    cur.close()

    return render_template('user_sports.html', sports=sports)

@user_bp.route('/user/matches')
@login_required
def user_matches():
    db = get_db()
    cur = db.cursor()

    # Get filter parameters from the request
    sport_id = request.args.get('sport_id')
    team_id = request.args.get('team_id')
    matchday = request.args.get('matchday')

    # Fetch available sports and teams for filtering
    cur.execute('SELECT sport_id, name FROM sports')
    sports = cur.fetchall()

    cur.execute('SELECT team_id, name FROM teams')
    teams = cur.fetchall()

    matchdays = [i for i in range(1, 39)]  # Assuming matchdays from 1 to 38

    # Build the base query
    query = """
        SELECT m.match_id, 
               t1.name AS home_team_name, 
               t2.name AS away_team_name, 
               s.full_time_home AS home_score, 
               s.full_time_away AS away_score,
               TO_CHAR(m.utc_date, 'Month DD, YYYY') AS formatted_date,
               t1.crestURL AS home_team_logo,
               t2.crestURL AS away_team_logo,
               m.matchday
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.team_id
        JOIN teams t2 ON m.away_team_id = t2.team_id
        LEFT JOIN scores s ON m.match_id = s.match_id
        WHERE 1=1
    """
    filters = []

    # Add filters based on the selected values
    if sport_id:
        query += " AND m.sport_id = %s"
        filters.append(sport_id)
    if team_id:
        query += " AND (m.home_team_id = %s OR m.away_team_id = %s)"
        filters.append(team_id)
        filters.append(team_id)
    if matchday:
        query += " AND m.matchday = %s"
        filters.append(matchday)

    query += " ORDER BY m.utc_date DESC"

    cur.execute(query, filters)
    matches = cur.fetchall()
    cur.close()

    return render_template('user_matches.html', matches=matches, sports=sports, teams=teams,
                           matchdays=matchdays, str=str)

@user_bp.route('/team/<int:team_id>')
@login_required
def profile_team(team_id):
    db = get_db()
    cur = db.cursor()

    # Get team details along with stadium, coach, sport, and crestURL
    cur.execute("""
        SELECT t.name, t.founded_year, s.name AS stadium_name, c.name AS coach_name, sp.name AS sport_name, t.crestURL
        FROM teams t 
        JOIN stadiums s ON t.stadium_id = s.stadium_id 
        JOIN coaches c ON t.coach_id = c.coach_id 
        JOIN sports sp ON t.sport_id = sp.sport_id
        WHERE t.team_id = %s
    """, (team_id,))
    team = cur.fetchone()

    # Get players
    cur.execute("""
        SELECT p.player_id, p.name, p.date_of_birth, p.position
        FROM players p 
        WHERE p.team_id = %s
    """, (team_id,))
    players = cur.fetchall()

    # Get match scores
    cur.execute("""
        SELECT 
            m.match_id,
            TO_CHAR(m.utc_date, 'Mon, DD YYYY') AS utc_date, 
            t1.name AS home_team_name, 
            t2.name AS away_team_name, 
            s.full_time_home, 
            s.full_time_away,
            t1.crestURL AS home_team_logo,
            t2.crestURL AS away_team_logo,
            m.matchday
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.team_id
        JOIN teams t2 ON m.away_team_id = t2.team_id
        LEFT JOIN scores s ON m.match_id = s.match_id
        WHERE m.home_team_id = %s OR m.away_team_id = %s
        ORDER BY m.utc_date DESC
    """, (team_id, team_id))
    scores = cur.fetchall()

    cur.close()

    if team:
        return render_template('profile_team.html',
                               team=team,
                               players=players,
                               scores=scores,
                               logo_url=team[5])
    else:
        flash('Team not found', 'error')
        return redirect(url_for('user.user_dashboard'))

@user_bp.route('/player/<int:player_id>')
@login_required
def profile_player(player_id):
    db = get_db()
    cur = db.cursor()

    # Fetch player details
    cur.execute("""
        SELECT p.name, p.date_of_birth, p.position, t.team_id, t.name AS team_name
        FROM players p 
        JOIN teams t ON p.team_id = t.team_id 
        WHERE p.player_id = %s
    """, (player_id,))
    player = cur.fetchone()

    # Fetch player statistics if they are in the top scorers list
    cur.execute("""
        SELECT sc.goals, sc.assists, sc.penalties
        FROM scorers sc
        WHERE sc.player_id = %s
    """, (player_id,))
    statistics = cur.fetchone()

    cur.close()

    if player:
        return render_template('profile_player.html', player=player, statistics=statistics)
    else:
        flash('Player not found', 'error')
        return redirect(url_for('user.user_dashboard'))

@user_bp.route('/match/<int:match_id>')
@login_required
def profile_match(match_id):
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        SELECT m.match_id, 
               t1.name AS home_team_name, 
               t2.name AS away_team_name, 
               s.full_time_home AS home_score, 
               s.full_time_away AS away_score,
               TO_CHAR(m.utc_date, 'Month DD, YYYY') AS formatted_date,
               m.matchday,
               t1.crestURL AS home_team_logo,
               t2.crestURL AS away_team_logo,
               st.name AS stadium_name,
               st.location AS stadium_location,
               r.name AS referee_name,
               t1.team_id AS home_team_id,
               t2.team_id AS away_team_id
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.team_id
        JOIN teams t2 ON m.away_team_id = t2.team_id
        LEFT JOIN scores s ON m.match_id = s.match_id
        JOIN stadiums st ON t1.stadium_id = st.stadium_id
        JOIN match_referees mr ON m.match_id = mr.match_id
        JOIN referees r ON mr.referee_id = r.referee_id
        WHERE m.match_id = %s
    """, (match_id,))
    match = cur.fetchone()

    cur.execute("""
        SELECT s.full_time_home, s.full_time_away, s.half_time_home, s.half_time_away
        FROM scores s
        WHERE s.match_id = %s
    """, (match_id,))
    scores = cur.fetchall()

    cur.close()

    if match:
        return render_template('profile_match.html', match=match, scores=scores)
    else:
        flash('Match not found', 'error')
        return redirect(url_for('user.user_dashboard'))

@user_bp.route('/sport/<int:sport_id>')
@login_required
def profile_sport(sport_id):
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        SELECT name
        FROM sports
        WHERE sport_id = %s
    """, (sport_id,))
    sport = cur.fetchone()

    cur.execute('SELECT team_id, name, cresturl FROM teams WHERE sport_id = %s', (sport_id,))
    teams = cur.fetchall()

    cur.execute("""
        SELECT s.position, s.team_id, t.name AS team_name, s.played_games, s.won, s.draw, s.lost, 
               s.points, s.goals_for, s.goals_against, s.goal_difference, s.form, t.crestURL
        FROM standings s
        JOIN teams t ON s.team_id = t.team_id
        WHERE t.sport_id = %s
        ORDER BY s.position
    """, (sport_id,))
    standings = cur.fetchall()

    cur.close()

    return render_template('profile_sport.html', sport=sport, teams=teams, standings=standings)

@user_bp.route('/user/scorers')
@login_required
def user_scorers():
    db = get_db()
    cur = db.cursor()

    # Get filter parameters from the request
    sport_id = request.args.get('sport_id')
    team_id = request.args.get('team_id')

    # Fetch available sports and teams for filtering
    cur.execute('SELECT sport_id, name FROM sports')
    sports = cur.fetchall()

    cur.execute('SELECT team_id, name FROM teams')
    teams = cur.fetchall()

    # Build the base query
    query = """
        SELECT sc.player_id, p.name, sc.goals, sc.assists, sc.penalties, t.crestURL
        FROM scorers sc
        JOIN players p ON sc.player_id = p.player_id
        JOIN teams t ON p.team_id = t.team_id
        WHERE 1=1
    """
    filters = []

    # Add filters based on the selected values
    if sport_id:
        query += " AND sc.sport_id = %s"
        filters.append(sport_id)
    if team_id:
        query += " AND p.team_id = %s"
        filters.append(team_id)

    query += " ORDER BY sc.goals DESC"

    cur.execute(query, filters)
    scorers = cur.fetchall()
    cur.close()

    return render_template('user_scorers.html', scorers=scorers, sports=sports, teams=teams, str=str)


@user_bp.route('/calendar')
@login_required
def calendar():
    db = get_db()
    cur = db.cursor()

    # Fetch available sports and teams for filtering
    cur.execute('SELECT sport_id, name FROM sports')
    sports = cur.fetchall()

    cur.execute('SELECT team_id, name FROM teams')
    teams = cur.fetchall()

    cur.close()

    return render_template('calendar.html', sports=sports, teams=teams)


@user_bp.route('/api/matches')
@login_required
def api_matches():
    db = get_db()
    cur = db.cursor()

    # Get filter parameters from the request
    sport_id = request.args.get('sport_id')
    team_id = request.args.get('team_id')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    # Build the base query
    query = """
        SELECT m.match_id, 
               t1.name AS home_team_name, 
               t2.name AS away_team_name, 
               s.full_time_home AS home_score, 
               s.full_time_away AS away_score,
               TO_CHAR(m.utc_date, 'YYYY-MM-DD') AS formatted_date,
               m.matchday
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.team_id
        JOIN teams t2 ON m.away_team_id = t2.team_id
        LEFT JOIN scores s ON m.match_id = s.match_id
        WHERE 1=1
    """
    filters = []

    # Add filters based on the selected values
    if sport_id:
        query += " AND m.sport_id = %s"
        filters.append(sport_id)
    if team_id:
        query += " AND (m.home_team_id = %s OR m.away_team_id = %s)"
        filters.append(team_id)
        filters.append(team_id)
    if date_from:
        query += " AND m.utc_date >= %s::date"
        filters.append(date_from)
    if date_to:
        query += " AND m.utc_date <= %s::date"
        filters.append(date_to)

    query += " ORDER BY m.utc_date"

    cur.execute(query, filters)
    matches = cur.fetchall()
    cur.close()

    # Convert to JSON format for FullCalendar
    matches_json = []
    for match in matches:
        matches_json.append({
            'match_id': match[0],
            'home_team_name': match[1],
            'away_team_name': match[2],
            'home_score': match[3],
            'away_score': match[4],
            'utc_date': match[5],
            'matchday': match[6]
        })

    from flask import jsonify
    return jsonify(matches_json)