from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from functools import wraps
from db import get_db
import logging
import sys

admin_bp = Blueprint('admin', __name__)

# Configurar logger específico para el módulo admin
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(funcName)s]')
handler.setFormatter(formatter)
logger.addHandler(handler)

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        logger.debug(f"Verificando acceso a ruta protegida: {request.path}")
        if 'user_id' not in session:
            logger.warning(f"Intento de acceso sin sesión a: {request.path}")
            flash('You need to be logged in to access this page', 'error')
            return redirect(url_for('login'))
        if not session.get('is_admin') and not session.get('is_editor'):
            user_id = session.get('user_id', 'desconocido')
            logger.warning(f"Usuario {user_id} sin permisos intentó acceder a: {request.path}")
            flash('You need to be an admin or editor to access this page', 'error')
            return redirect(url_for('login'))
        logger.info(f"Acceso concedido para usuario {session.get('user_id')} a {request.path}")
        return f(*args, **kwargs)
    return wrap

def is_admin():
    admin_status = session.get('is_admin', False)
    logger.debug(f"Verificando si es admin: {admin_status}")
    return admin_status

def is_editor():
    editor_status = session.get('is_editor', False)
    logger.debug(f"Verificando si es editor: {editor_status}")
    return editor_status

# --- Gestión de FACULTADES ---
@admin_bp.route('/manage_faculties', methods=['GET', 'POST'])
@admin_required
def manage_faculties():
    logger.info(f"Iniciando gestión de facultades - Método: {request.method}")
    db = get_db()
    cur = db.cursor()
    if request.method == 'POST':
        try:
            faculty_id = request.form.get('faculty_id')
            name = request.form['name']
            logger.info(f"Procesando facultad - ID: {faculty_id}, Nombre: {name}")
            if 'submit' in request.form:
                if faculty_id:
                    logger.info(f"Editando facultad ID: {faculty_id}")
                    cur.execute('UPDATE faculties SET name = %s WHERE faculty_id = %s', (name, faculty_id))
                    flash('Faculty updated successfully', 'success')
                else:
                    if not is_admin():
                        logger.warning(f"Editor intentó agregar facultad sin permisos: {session.get('user_id')}")
                        flash('Only administrators can add new faculties', 'error')
                        return redirect(url_for('admin.manage_faculties'))
                    cur.execute('INSERT INTO faculties (name) VALUES (%s)', (name,))
                    logger.info(f"Facultad agregada: {name}")
                    flash('Faculty added successfully', 'success')
            elif 'delete' in request.form:
                if not is_admin():
                    logger.warning(f"Editor intentó eliminar facultad sin permisos: {session.get('user_id')}")
                    flash('Only administrators can delete faculties', 'error')
                    return redirect(url_for('admin.manage_faculties'))
                faculty_id = request.form['deleteEntityId']
                logger.info(f"Eliminando facultad ID: {faculty_id}")
                cur.execute('DELETE FROM faculties WHERE faculty_id = %s', (faculty_id,))
                flash('Faculty deleted successfully', 'success')
            db.commit()
            logger.debug("Transacción de facultades completada exitosamente")
        except Exception as e:
            db.rollback()
            logger.error(f"Error en gestión de facultades: {str(e)}", exc_info=True)
            flash('An error occurred: ' + str(e), 'error')
        finally:
            cur.close()
        return redirect(url_for('admin.manage_faculties'))

    # GET
    try:
        cur.execute('SELECT faculty_id, name FROM faculties')
        faculties = cur.fetchall()
        logger.debug(f"Obtenidas {len(faculties)} facultades para mostrar")
    except Exception as e:
        logger.error(f"Error al obtener facultades: {str(e)}")
        faculties = []
    finally:
        cur.close()
    return render_template('manage_faculties.html', faculties=faculties, is_admin=is_admin(), is_editor=is_editor())

# --- Gestión de DEPORTES ---
@admin_bp.route('/manage_sports', methods=['GET', 'POST'])
@admin_required
def manage_sports():
    logger.info(f"Iniciando gestión de deportes - Método: {request.method}")
    db = get_db()
    cur = db.cursor()
    if request.method == 'POST':
        try:
            sport_id = request.form.get('sport_id')
            name = request.form['name']
            logger.info(f"Procesando deporte - ID: {sport_id}, Nombre: {name}")
            if 'submit' in request.form:
                if sport_id:
                    logger.info(f"Editando deporte ID: {sport_id}")
                    cur.execute('UPDATE sports SET name = %s WHERE sport_id = %s', (name, sport_id))
                    flash('Sport updated successfully', 'success')
                else:
                    if not is_admin():
                        logger.warning(f"Editor intentó agregar deporte sin permisos: {session.get('user_id')}")
                        flash('Only administrators can add new sports', 'error')
                        return redirect(url_for('admin.manage_sports'))
                    cur.execute('INSERT INTO sports (name) VALUES (%s)', (name,))
                    logger.info(f"Deporte agregado: {name}")
                    flash('Sport added successfully', 'success')
            elif 'delete' in request.form:
                if not is_admin():
                    logger.warning(f"Editor intentó eliminar deporte sin permisos: {session.get('user_id')}")
                    flash('Only administrators can delete sports', 'error')
                    return redirect(url_for('admin.manage_sports'))
                sport_id = request.form['deleteEntityId']
                logger.info(f"Eliminando deporte ID: {sport_id}")
                cur.execute('DELETE FROM sports WHERE sport_id = %s', (sport_id,))
                flash('Sport deleted successfully', 'success')
            db.commit()
            logger.debug("Transacción de deportes completada exitosamente")
        except Exception as e:
            db.rollback()
            logger.error(f"Error en gestión de deportes: {str(e)}", exc_info=True)
            flash('An error occurred: ' + str(e), 'error')
        finally:
            cur.close()
        return redirect(url_for('admin.manage_sports'))

    # GET
    try:
        cur.execute('SELECT sport_id, name FROM sports')
        sports = cur.fetchall()
        logger.debug(f"Obtenidos {len(sports)} deportes para mostrar")
    except Exception as e:
        logger.error(f"Error al obtener deportes: {str(e)}")
        sports = []
    finally:
        cur.close()
    return render_template('manage_sports.html', sports=sports, is_admin=is_admin(), is_editor=is_editor())

# --- Gestión de TEMPORADAS ---
@admin_bp.route('/manage_seasons', methods=['GET', 'POST'])
@admin_required
def manage_seasons():
    logger.info(f"Iniciando gestión de temporadas - Método: {request.method}")
    db = get_db()
    cur = db.cursor()
    if request.method == 'POST':
        try:
            season_id = request.form.get('season_id')
            sport_id = request.form['sport_id']
            year = request.form['year']
            logger.info(f"Procesando temporada - ID: {season_id}, Año: {year}, Deporte ID: {sport_id}")
            if 'add' in request.form:
                if not is_admin():
                    logger.warning(f"Editor intentó agregar temporada sin permisos: {session.get('user_id')}")
                    flash('Only administrators can add new seasons', 'error')
                    return redirect(url_for('admin.manage_seasons'))
                cur.execute('INSERT INTO seasons (sport_id, year) VALUES (%s, %s)', (sport_id, year))
                logger.info(f"Temporada agregada: Año {year} para deporte {sport_id}")
                flash('Season added successfully', 'success')
            elif 'edit' in request.form and season_id:
                logger.info(f"Editando temporada ID: {season_id}")
                cur.execute('UPDATE seasons SET sport_id = %s, year = %s WHERE season_id = %s', (sport_id, year, season_id))
                flash('Season updated successfully', 'success')
            elif 'delete' in request.form:
                if not is_admin():
                    logger.warning(f"Editor intentó eliminar temporada sin permisos: {session.get('user_id')}")
                    flash('Only administrators can delete seasons', 'error')
                    return redirect(url_for('admin.manage_seasons'))
                season_id = request.form['deleteItemId']
                logger.info(f"Eliminando temporada ID: {season_id}")
                cur.execute('DELETE FROM seasons WHERE season_id = %s', (season_id,))
                flash('Season deleted successfully', 'success')
            db.commit()
            logger.debug("Transacción de temporadas completada exitosamente")
        except Exception as e:
            db.rollback()
            logger.error(f"Error en gestión de temporadas: {str(e)}", exc_info=True)
            flash('An error occurred: ' + str(e), 'error')
        finally:
            cur.close()
        return redirect(url_for('admin.manage_seasons'))

    # GET
    try:
        cur.execute('''
            SELECT s.season_id, s.sport_id, s.year, sp.name
            FROM seasons s
            JOIN sports sp ON s.sport_id = sp.sport_id
        ''')
        seasons = cur.fetchall()
        cur.execute('SELECT sport_id, name FROM sports')
        sports = cur.fetchall()
        logger.debug(f"Obtenidas {len(seasons)} temporadas y {len(sports)} deportes")
    except Exception as e:
        logger.error(f"Error al obtener temporadas/deportes: {str(e)}")
        seasons = []
        sports = []
    finally:
        cur.close()
    return render_template('manage_seasons.html', seasons=seasons, sports=sports, is_admin=is_admin(), is_editor=is_editor())

@admin_bp.route('/manage_teams', methods=['GET', 'POST'])
@admin_required
def manage_teams():
    logger.info(f"Iniciando gestión de equipos - Método: {request.method}")
    db = get_db()
    cur = db.cursor()
    if request.method == 'POST':
        try:
            team_id = request.form.get('team_id')
            name = request.form['name']
            sport_id = request.form['sport_id']
            coach_id = request.form['coach_id']
            faculty_id = request.form['faculty_id']
            player_ids = request.form.getlist('player_ids')  # Lista de IDs de jugadores seleccionados

            logger.info(f"Procesando equipo - ID: {team_id}, Nombre: {name}, Jugadores: {len(player_ids)}")

            if 'add' in request.form:
                if not is_admin():
                    flash('Only administrators can add new teams', 'error')
                    return redirect(url_for('admin.manage_teams'))
                # Insertar equipo
                cur.execute(
                    'INSERT INTO teams (name, sport_id, coach_id, faculty_id) VALUES (%s, %s, %s, %s) RETURNING team_id',
                    (name, sport_id, coach_id, faculty_id)
                )
                new_team_id = cur.fetchone()[0]

                # Asignar jugadores
                for pid in player_ids:
                    cur.execute('UPDATE players SET team_id = %s WHERE player_id = %s', (new_team_id, pid))

                logger.info(f"Equipo agregado: {name} con {len(player_ids)} jugadores")
                flash('Team added successfully', 'success')

            elif 'edit' in request.form and team_id:
                # Actualizar equipo
                cur.execute(
                    'UPDATE teams SET name = %s, sport_id = %s, coach_id = %s, faculty_id = %s WHERE team_id = %s',
                    (name, sport_id, coach_id, faculty_id, team_id)
                )

                # Reasignar jugadores: primero desvincular todos del equipo
                cur.execute('UPDATE players SET team_id = NULL WHERE team_id = %s', (team_id,))
                # Luego asignar los nuevos
                for pid in player_ids:
                    cur.execute('UPDATE players SET team_id = %s WHERE player_id = %s', (team_id, pid))

                logger.info(f"Equipo actualizado: {name} con {len(player_ids)} jugadores")
                flash('Team updated successfully', 'success')

            elif 'delete' in request.form and team_id:
                if not is_admin():
                    flash('Only administrators can delete teams', 'error')
                    return redirect(url_for('admin.manage_teams'))
                # Desvincular jugadores antes de eliminar
                cur.execute('UPDATE players SET team_id = NULL WHERE team_id = %s', (team_id,))
                cur.execute('DELETE FROM teams WHERE team_id = %s', (team_id,))
                flash('Team deleted successfully', 'success')

            db.commit()
            logger.debug("Transacción de equipos completada exitosamente")
        except Exception as e:
            db.rollback()
            logger.error(f"Error en gestión de equipos: {str(e)}", exc_info=True)
            flash('An error occurred: ' + str(e), 'error')
        finally:
            cur.close()
        return redirect(url_for('admin.manage_teams'))

    # GET
    try:
        cur.execute('SELECT team_id, name, sport_id, coach_id, faculty_id FROM teams')
        teams = cur.fetchall()

        cur.execute('SELECT sport_id, name FROM sports')
        sports = cur.fetchall()

        cur.execute('SELECT coach_id, name FROM coaches')
        coaches = cur.fetchall()

        cur.execute('SELECT faculty_id, name FROM faculties')
        faculties = cur.fetchall()

        # Jugadores sin equipo (disponibles) + todos los jugadores (para edición)
        cur.execute('''
            SELECT player_id, name, position
            FROM players
            ORDER BY name
        ''')
        all_players = cur.fetchall()

        logger.debug(f"Equipos: {len(teams)}, Deportes: {len(sports)}, Entrenadores: {len(coaches)}, Facultades: {len(faculties)}, Jugadores: {len(all_players)}")
    except Exception as e:
        logger.error(f"Error al obtener datos de equipos: {str(e)}")
        teams, sports, coaches, faculties, all_players = [], [], [], [], []
    finally:
        cur.close()
    return render_template('manage_teams.html', teams=teams, sports=sports, coaches=coaches, faculties=faculties, all_players=all_players, is_admin=is_admin(), is_editor=is_editor())

# --- Gestión de ENTRENADORES ---
@admin_bp.route('/manage_coaches', methods=['GET', 'POST'])
@admin_required
def manage_coaches():
    logger.info(f"Iniciando gestión de entrenadores - Método: {request.method}")
    db = get_db()
    cur = db.cursor()
    if request.method == 'POST':
        try:
            coach_id = request.form.get('coach_id')
            name = request.form['name']
            team_id = request.form['team_id']
            logger.info(f"Procesando entrenador - ID: {coach_id}, Nombre: {name}")
            if 'add' in request.form:
                if not is_admin():
                    logger.warning(f"Editor intentó agregar entrenador sin permisos: {session.get('user_id')}")
                    flash('Only administrators can add new coaches', 'error')
                    return redirect(url_for('admin.manage_coaches'))
                cur.execute('INSERT INTO coaches (name, team_id) VALUES (%s, %s)', (name, team_id))
                logger.info(f"Entrenador agregado: {name}")
                flash('Coach added successfully', 'success')
            elif 'submit' in request.form and coach_id:
                logger.info(f"Editando entrenador ID: {coach_id}")
                cur.execute('UPDATE coaches SET name = %s, team_id = %s WHERE coach_id = %s', (name, team_id, coach_id))
                flash('Coach updated successfully', 'success')
            elif 'delete' in request.form:
                if not is_admin():
                    logger.warning(f"Editor intentó eliminar entrenador sin permisos: {session.get('user_id')}")
                    flash('Only administrators can delete coaches', 'error')
                    return redirect(url_for('admin.manage_coaches'))
                coach_id = request.form['deleteEntityId']
                logger.info(f"Eliminando entrenador ID: {coach_id}")
                cur.execute('DELETE FROM coaches WHERE coach_id = %s', (coach_id,))
                flash('Coach deleted successfully', 'success')
            db.commit()
            logger.debug("Transacción de entrenadores completada exitosamente")
        except Exception as e:
            db.rollback()
            logger.error(f"Error en gestión de entrenadores: {str(e)}", exc_info=True)
            flash('An error occurred: ' + str(e), 'error')
        finally:
            cur.close()
        return redirect(url_for('admin.manage_coaches'))

    # GET
    try:
        cur.execute('''
            SELECT c.coach_id, c.name, c.team_id, t.name AS team_name
            FROM coaches c
            LEFT JOIN teams t ON c.team_id = t.team_id
        ''')
        coaches = cur.fetchall()
        cur.execute('SELECT team_id, name FROM teams')
        teams = cur.fetchall()
        logger.debug(f"Obtenidos {len(coaches)} entrenadores y {len(teams)} equipos")
    except Exception as e:
        logger.error(f"Error al obtener entrenadores/equipos: {str(e)}")
        coaches, teams = [], []
    finally:
        cur.close()
    return render_template('manage_coaches.html', coaches=coaches, teams=teams, is_admin=is_admin(), is_editor=is_editor())

# --- Gestión de JUGADORES ---
@admin_bp.route('/manage_players', methods=['GET', 'POST'])
@admin_required
def manage_players():
    logger.info(f"Iniciando gestión de jugadores - Método: {request.method}")
    db = get_db()
    cur = db.cursor()
    if request.method == 'POST':
        try:
            player_id = request.form.get('player_id')
            team_id = request.form['team_id']
            name = request.form['name']
            position = request.form['position']
            date_of_birth = request.form['date_of_birth']
            logger.info(f"Procesando jugador - ID: {player_id}, Nombre: {name}, Posición: {position}")
            if 'submit' in request.form:
                if player_id:
                    logger.info(f"Editando jugador ID: {player_id}")
                    cur.execute(
                        'UPDATE players SET team_id = %s, name = %s, position = %s, date_of_birth = %s WHERE player_id = %s',
                        (team_id, name, position, date_of_birth, player_id)
                    )
                    flash('Player updated successfully', 'success')
                else:
                    if not is_admin():
                        logger.warning(f"Editor intentó agregar jugador sin permisos: {session.get('user_id')}")
                        flash('Only administrators can add new players', 'error')
                        return redirect(url_for('admin.manage_players'))
                    cur.execute(
                        'INSERT INTO players (team_id, name, position, date_of_birth) VALUES (%s, %s, %s, %s)',
                        (team_id, name, position, date_of_birth)
                    )
                    logger.info(f"Jugador agregado: {name} ({position})")
                    flash('Player added successfully', 'success')
            elif 'delete' in request.form:
                if not is_admin():
                    logger.warning(f"Editor intentó eliminar jugador sin permisos: {session.get('user_id')}")
                    flash('Only administrators can delete players', 'error')
                    return redirect(url_for('admin.manage_players'))
                player_id = request.form['deleteEntityId']
                logger.info(f"Eliminando jugador ID: {player_id}")
                cur.execute('DELETE FROM players WHERE player_id = %s', (player_id,))
                flash('Player deleted successfully', 'success')
            db.commit()
            logger.debug("Transacción de jugadores completada exitosamente")
        except Exception as e:
            db.rollback()
            logger.error(f"Error en gestión de jugadores: {str(e)}", exc_info=True)
            flash('An error occurred: ' + str(e), 'error')
        finally:
            cur.close()
        return redirect(url_for('admin.manage_players'))

    # GET
    try:
        cur.execute('''
            SELECT p.player_id, t.name AS team, p.name, p.position, p.date_of_birth, p.team_id
            FROM players p
            JOIN teams t ON p.team_id = t.team_id
        ''')
        players = cur.fetchall()
        cur.execute('SELECT team_id, name FROM teams')
        teams = cur.fetchall()
        logger.debug(f"Obtenidos {len(players)} jugadores y {len(teams)} equipos")
    except Exception as e:
        logger.error(f"Error al obtener jugadores/equipos: {str(e)}")
        players, teams = [], []
    finally:
        cur.close()
    return render_template('manage_players.html', players=players, teams=teams, is_admin=is_admin(), is_editor=is_editor())

@admin_bp.route('/manage_referees', methods=['GET', 'POST'])
@admin_required
def manage_referees():
    logger.info(f"Iniciando gestión de árbitros - Método: {request.method}")
    db = get_db()
    cur = db.cursor()
    
    if request.method == 'POST':
        try:
            referee_id = request.form.get('referee_id')
            name = request.form['name']
            logger.info(f"Procesando árbitro - ID: {referee_id}, Nombre: {name}")
            
            if 'add' in request.form:
                if not is_admin():
                    logger.warning(f"Editor intentó agregar árbitro sin permisos: {session.get('user_id')}")
                    flash('Only administrators can add new referees', 'error')
                    return redirect(url_for('admin.manage_referees'))
                
                # 👇 Generar el próximo ID automáticamente
                cur.execute('SELECT COALESCE(MAX(referee_id), 0) + 1 FROM referees')
                next_id = cur.fetchone()[0]
                
                cur.execute('INSERT INTO referees (referee_id, name) VALUES (%s, %s)', (next_id, name))
                logger.info(f"Árbitro agregado: {name} con ID {next_id}")
                flash('Referee added successfully', 'success')
            
            elif 'submit' in request.form and referee_id:
                logger.info(f"Editando árbitro ID: {referee_id}")
                cur.execute('UPDATE referees SET name = %s WHERE referee_id = %s', (name, referee_id))
                flash('Referee updated successfully', 'success')
            
            elif 'delete' in request.form:
                if not is_admin():
                    logger.warning(f"Editor intentó eliminar árbitro sin permisos: {session.get('user_id')}")
                    flash('Only administrators can delete referees', 'error')
                    return redirect(url_for('admin.manage_referees'))
                referee_id = request.form['deleteEntityId']
                logger.info(f"Eliminando árbitro ID: {referee_id}")
                cur.execute('DELETE FROM referees WHERE referee_id = %s', (referee_id,))
                flash('Referee deleted successfully', 'success')
            
            db.commit()
            logger.debug("Transacción de árbitros completada exitosamente")
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error en gestión de árbitros: {str(e)}", exc_info=True)
            flash('An error occurred: ' + str(e), 'error')
        finally:
            cur.close()
        
        return redirect(url_for('admin.manage_referees'))

    # GET
    try:
        cur.execute('SELECT referee_id, name FROM referees')
        referees = cur.fetchall()
        logger.debug(f"Obtenidos {len(referees)} árbitros para mostrar")
    except Exception as e:
        logger.error(f"Error al obtener árbitros: {str(e)}")
        referees = []
    finally:
        cur.close()
    
    return render_template('manage_referees.html', referees=referees, is_admin=is_admin(), is_editor=is_editor())

@admin_bp.route('/manage_matches', methods=['GET', 'POST'])
@admin_required
def manage_matches():
    logger.info(f"Iniciando gestión de partidos - Método: {request.method}")
    db = get_db()
    cur = db.cursor()
    
    if request.method == 'POST':
        try:
            match_id = request.form.get('match_id')
            date = request.form['date']
            team1_id = request.form['team1_id']
            team2_id = request.form['team2_id']
            season_id = request.form['season_id']
            sport_id = request.form['sport_id']
            stadium_id = request.form.get('stadium_id')  # 👈 NUEVO: obtener stadium_id
            
            logger.info(f"Procesando partido - ID: {match_id}, Estadio ID: {stadium_id}")
            
            if 'submit' in request.form:
                if match_id:
                    # 👇 ACTUALIZADO: incluir stadium_id en UPDATE
                    cur.execute('''
                        UPDATE matches 
                        SET utc_date = %s, home_team_id = %s, away_team_id = %s, 
                            season_id = %s, sport_id = %s, stadium_id = %s 
                        WHERE match_id = %s
                    ''', (date, team1_id, team2_id, season_id, sport_id, stadium_id, match_id))
                    flash('Match updated successfully', 'success')
                else:
                    if not is_admin():
                        flash('Only administrators can add new matches', 'error')
                        return redirect(url_for('admin.manage_matches'))
                    # 👇 ACTUALIZADO: incluir stadium_id en INSERT
                    cur.execute('''
                        INSERT INTO matches 
                        (utc_date, home_team_id, away_team_id, season_id, sport_id, stadium_id) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (date, team1_id, team2_id, season_id, sport_id, stadium_id))
                    flash('Match added successfully', 'success')
            
            elif 'delete' in request.form:
                if not is_admin():
                    flash('Only administrators can delete matches', 'error')
                    return redirect(url_for('admin.manage_matches'))
                match_id = request.form['deleteEntityId']
                logger.info(f"Eliminando partido ID: {match_id}")
                cur.execute('DELETE FROM matches WHERE match_id = %s', (match_id,))
                flash('Match deleted successfully', 'success')
            
            db.commit()
            logger.debug("Transacción de partidos completada exitosamente")
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error en gestión de partidos: {str(e)}", exc_info=True)
            flash('An error occurred: ' + str(e), 'error')
        finally:
            cur.close()
        return redirect(url_for('admin.manage_matches'))
    
    # GET - obtener datos para mostrar en el formulario
    try:
        # 👇 ACTUALIZADO: incluir stadium_id en la consulta
        cur.execute('''
            SELECT m.match_id, m.utc_date, m.home_team_id, m.away_team_id, 
                   m.season_id, m.sport_id, m.stadium_id,
                   ht.name AS home_team_name, at.name AS away_team_name,
                   s.name AS stadium_name
            FROM matches m
            LEFT JOIN teams ht ON m.home_team_id = ht.team_id
            LEFT JOIN teams at ON m.away_team_id = at.team_id
            LEFT JOIN stadiums s ON m.stadium_id = s.stadium_id
            ORDER BY m.utc_date DESC
        ''')
        matches = cur.fetchall()
        
        cur.execute('SELECT team_id, name FROM teams ORDER BY name')
        teams = cur.fetchall()
        
        cur.execute('SELECT season_id, year FROM seasons ORDER BY year DESC')
        seasons = cur.fetchall()
        
        cur.execute('SELECT sport_id, name FROM sports ORDER BY name')
        sports = cur.fetchall()
        
        # 👇 NUEVO: obtener lista de estadios para el dropdown
        cur.execute('SELECT stadium_id, name, location FROM stadiums ORDER BY name')
        stadiums = cur.fetchall()
        
        logger.debug(f"Obtenidos {len(matches)} partidos, {len(teams)} equipos, {len(stadiums)} estadios")
    
    except Exception as e:
        logger.error(f"Error al obtener datos de partidos: {str(e)}")
        matches, teams, seasons, sports, stadiums = [], [], [], [], []  # 👈 stadiums incluido
    finally:
        cur.close()
    
    # 👇 ACTUALIZADO: pasar stadiums al template
    return render_template(
        'manage_matches.html', 
        matches=matches, 
        teams=teams, 
        seasons=seasons, 
        sports=sports, 
        stadiums=stadiums,  # 👈 NUEVO parámetro
        is_admin=is_admin(), 
        is_editor=is_editor()
    )
    
# --- Gestión de ESTADIOS ---
@admin_bp.route('/manage_stadiums', methods=['GET', 'POST'])
@admin_required
def manage_stadiums():
    logger.info(f"Iniciando gestión de estadios - Método: {request.method}")
    db = get_db()
    cur = db.cursor()
    if request.method == 'POST':
        try:
            stadium_id = request.form.get('stadium_id')
            name = request.form['name']
            location = request.form['location']
            capacity = request.form['capacity']
            logger.info(f"Procesando estadio - ID: {stadium_id}, Nombre: {name}")
            if 'add' in request.form:
                if not is_admin():
                    logger.warning(f"Editor intentó agregar estadio sin permisos: {session.get('user_id')}")
                    flash('Only administrators can add new stadiums', 'error')
                    return redirect(url_for('admin.manage_stadiums'))
                cur.execute('INSERT INTO stadiums (name, location, capacity) VALUES (%s, %s, %s)',
                            (name, location, capacity))
                logger.info(f"Estadio agregado: {name} en {location}")
                flash('Stadium added successfully', 'success')
            elif 'edit' in request.form and stadium_id:
                logger.info(f"Editando estadio ID: {stadium_id}")
                cur.execute('UPDATE stadiums SET name = %s, location = %s, capacity = %s WHERE stadium_id = %s',
                            (name, location, capacity, stadium_id))
                flash('Stadium updated successfully', 'success')
            elif 'delete' in request.form and stadium_id:
                if not is_admin():
                    logger.warning(f"Editor intentó eliminar estadio sin permisos: {session.get('user_id')}")
                    flash('Only administrators can delete stadiums', 'error')
                    return redirect(url_for('admin.manage_stadiums'))
                logger.info(f"Eliminando estadio ID: {stadium_id}")
                cur.execute('DELETE FROM stadiums WHERE stadium_id = %s', (stadium_id,))
                flash('Stadium deleted successfully', 'success')
            db.commit()
            logger.debug("Transacción de estadios completada exitosamente")
        except Exception as e:
            db.rollback()
            logger.error(f"Error en gestión de estadios: {str(e)}", exc_info=True)
            flash('An error occurred: ' + str(e), 'error')
        finally:
            cur.close()
        return redirect(url_for('admin.manage_stadiums'))

    # GET
    try:
        cur.execute('SELECT stadium_id, name, location, capacity FROM stadiums')
        stadiums = cur.fetchall()
        logger.debug(f"Obtenidos {len(stadiums)} estadios para mostrar")
    except Exception as e:
        logger.error(f"Error al obtener estadios: {str(e)}")
        stadiums = []
    finally:
        cur.close()
    return render_template('manage_stadiums.html', stadiums=stadiums, is_admin=is_admin(), is_editor=is_editor())

@admin_bp.route('/manage_standings', methods=['GET', 'POST'])
@admin_required
def manage_standings():
    logger.info(f"Iniciando gestión de posiciones - Método: {request.method}")
    db = get_db()
    cur = db.cursor()
    
    if request.method == 'POST':
        try:
            standing_id = request.form.get('standing_id')
            season_id = request.form['season_id']  # 👈 NUEVO
            position = request.form['position']
            team_id = request.form['team_id']
            played_games = request.form['played_games']
            won = request.form['won']
            draw = request.form['draw']
            lost = request.form['lost']
            points = request.form['points']
            goals_for = request.form['goals_for']
            goals_against = request.form['goals_against']
            goal_difference = request.form['goal_difference']
            form_str = request.form['form']
            
            # Convertir string a array de caracteres: "WWLD" → ['W','W','L','D']
            form_array = list(form_str) if form_str else []
            
            logger.info(f"Procesando standing - ID: {standing_id}, Season: {season_id}, Equipo: {team_id}, Form: {form_array}")
            
            if 'add' in request.form:
                if not is_admin():
                    logger.warning(f"Editor intentó agregar standing sin permisos: {session.get('user_id')}")
                    flash('Only administrators can add new standings', 'error')
                    return redirect(url_for('admin.manage_standings'))
                
                cur.execute('''
                    INSERT INTO standings 
                    (season_id, position, team_id, played_games, won, draw, lost, points, 
                     goals_for, goals_against, goal_difference, form)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (season_id, position, team_id, played_games, won, draw, lost, points,
                      goals_for, goals_against, goal_difference, form_array))
                
                logger.info(f"Standing agregado para temporada {season_id}, equipo {team_id}")
                flash('Standing added successfully', 'success')
            
            elif 'edit' in request.form and standing_id:
                logger.info(f"Editando standing ID: {standing_id}")
                cur.execute('''
                    UPDATE standings 
                    SET season_id = %s, position = %s, team_id = %s, played_games = %s, won = %s, 
                        draw = %s, lost = %s, points = %s, goals_for = %s, 
                        goals_against = %s, goal_difference = %s, form = %s
                    WHERE standing_id = %s
                ''', (season_id, position, team_id, played_games, won, draw, lost, points,
                      goals_for, goals_against, goal_difference, form_array, standing_id))
                flash('Standing updated successfully', 'success')
            
            elif 'delete' in request.form:
                if not is_admin():
                    logger.warning(f"Editor intentó eliminar standing sin permisos: {session.get('user_id')}")
                    flash('Only administrators can delete standings', 'error')
                    return redirect(url_for('admin.manage_standings'))
                standing_id = request.form['deleteItemId']
                logger.info(f"Eliminando standing ID: {standing_id}")
                cur.execute('DELETE FROM standings WHERE standing_id = %s', (standing_id,))
                flash('Standing deleted successfully', 'success')
            
            db.commit()
            logger.debug("Transacción de standings completada exitosamente")
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error en gestión de standings: {str(e)}", exc_info=True)
            flash('An error occurred: ' + str(e), 'error')
        finally:
            cur.close()
        
        return redirect(url_for('admin.manage_standings'))

    # GET
    try:
        cur.execute('''
            SELECT standing_id, season_id, position, team_id, played_games, won, draw, lost, 
                   points, goals_for, goals_against, goal_difference, form
            FROM standings
            ORDER BY season_id DESC, position ASC
        ''')
        standings = cur.fetchall()
        
        cur.execute('SELECT team_id, name FROM teams ORDER BY name')
        teams = cur.fetchall()
        
        # 👈 NUEVO: obtener temporadas
        cur.execute('SELECT season_id, year FROM seasons ORDER BY year DESC')
        seasons = cur.fetchall()
        
        logger.debug(f"Obtenidos {len(standings)} standings, {len(teams)} equipos, {len(seasons)} temporadas")
    except Exception as e:
        logger.error(f"Error al obtener standings: {str(e)}")
        standings, teams, seasons = [], [], []
    finally:
        cur.close()
    
    return render_template('manage_standings.html', standings=standings, teams=teams, seasons=seasons, is_admin=is_admin(), is_editor=is_editor())

# --- Gestión de GOLEADORES ---
@admin_bp.route('/manage_scorers', methods=['GET', 'POST'])
@admin_required
def manage_scorers():
    logger.info(f"Iniciando gestión de goleadores - Método: {request.method}")
    db = get_db()
    cur = db.cursor()
    if request.method == 'POST':
        try:
            scorer_id = request.form.get('scorer_id')
            player_id = request.form['player_id']
            season_id = request.form['season_id']
            sport_id = request.form['sport_id']
            goals = request.form['goals']
            assists = request.form['assists']
            penalties = request.form['penalties']
            logger.info(f"Procesando goleador - ID: {scorer_id}, Goles: {goals}, Asistencias: {assists}")
            if 'submit' in request.form:
                if scorer_id:
                    logger.info(f"Editando goleador ID: {scorer_id}")
                    cur.execute('UPDATE scorers SET player_id = %s, season_id = %s, sport_id = %s, goals = %s, assists = %s, penalties = %s WHERE scorer_id = %s',
                                (player_id, season_id, sport_id, goals, assists, penalties, scorer_id))
                    flash('Scorer updated successfully', 'success')
                else:
                    if not is_admin():
                        logger.warning(f"Editor intentó agregar goleador sin permisos: {session.get('user_id')}")
                        flash('Only administrators can add new scorers', 'error')
                        return redirect(url_for('admin.manage_scorers'))
                    cur.execute('INSERT INTO scorers (player_id, season_id, sport_id, goals, assists, penalties) VALUES (%s, %s, %s, %s, %s, %s)',
                                (player_id, season_id, sport_id, goals, assists, penalties))
                    logger.info(f"Goleador agregado: Jugador {player_id} - {goals} goles")
                    flash('Scorer added successfully', 'success')
            elif 'delete' in request.form:
                if not is_admin():
                    logger.warning(f"Editor intentó eliminar goleador sin permisos: {session.get('user_id')}")
                    flash('Only administrators can delete scorers', 'error')
                    return redirect(url_for('admin.manage_scorers'))
                scorer_id = request.form['deleteEntityId']
                logger.info(f"Eliminando goleador ID: {scorer_id}")
                cur.execute('DELETE FROM scorers WHERE scorer_id = %s', (scorer_id,))
                flash('Scorer deleted successfully', 'success')
            db.commit()
            logger.debug("Transacción de goleadores completada exitosamente")
        except Exception as e:
            db.rollback()
            logger.error(f"Error en gestión de goleadores: {str(e)}", exc_info=True)
            flash('An error occurred: ' + str(e), 'error')
        finally:
            cur.close()
        return redirect(url_for('admin.manage_scorers'))

    # GET
    try:
        cur.execute('''
            SELECT s.scorer_id, p.name, se.year, sp.name, s.goals, s.assists, s.penalties
            FROM scorers s
            JOIN players p ON s.player_id = p.player_id
            JOIN seasons se ON s.season_id = se.season_id
            JOIN sports sp ON s.sport_id = sp.sport_id
        ''')
        scorers = cur.fetchall()
        cur.execute('SELECT player_id, name FROM players')
        players = cur.fetchall()
        cur.execute('SELECT season_id, year FROM seasons')
        seasons = cur.fetchall()
        cur.execute('SELECT sport_id, name FROM sports')
        sports = cur.fetchall()
        logger.debug(f"Datos obtenidos: {len(players)} jugadores, {len(seasons)} temporadas, {len(sports)} deportes")
    except Exception as e:
        logger.error(f"Error al obtener datos de goleadores: {str(e)}")
        scorers = []
        players = []
        seasons = []
        sports = []
    finally:
        cur.close()
    return render_template('manage_scorers.html', scorers=scorers, players=players, seasons=seasons, sports=sports, is_admin=is_admin(), is_editor=is_editor())

# --- Gestión de RESULTADOS (SCORES) ---
@admin_bp.route('/manage_scores', methods=['GET', 'POST'])
@admin_required
def manage_scores():
    logger.info(f"Iniciando gestión de resultados - Método: {request.method}")
    db = get_db()
    cur = db.cursor()
    if request.method == 'POST':
        try:
            score_id = request.form.get('score_id')
            match_id = request.form['match_id']
            full_time_home = request.form['full_time_home']
            full_time_away = request.form['full_time_away']
            half_time_home = request.form['half_time_home']
            half_time_away = request.form['half_time_away']
            logger.info(f"Procesando resultado - ID: {score_id}, Marcador: {full_time_home}-{full_time_away}")
            if 'submit' in request.form:
                if score_id:
                    logger.info(f"Editando resultado ID: {score_id}")
                    cur.execute('UPDATE scores SET match_id = %s, full_time_home = %s, full_time_away = %s, half_time_home = %s, half_time_away = %s WHERE score_id = %s',
                                (match_id, full_time_home, full_time_away, half_time_home, half_time_away, score_id))
                    flash('Score updated successfully', 'success')
                else:
                    if not is_admin():
                        logger.warning(f"Editor intentó agregar resultado sin permisos: {session.get('user_id')}")
                        flash('Only administrators can add new scores', 'error')
                        return redirect(url_for('admin.manage_scores'))
                    cur.execute('INSERT INTO scores (match_id, full_time_home, full_time_away, half_time_home, half_time_away) VALUES (%s, %s, %s, %s, %s)',
                                (match_id, full_time_home, full_time_away, half_time_home, half_time_away))
                    logger.info(f"Resultado agregado para partido {match_id}: {full_time_home}-{full_time_away}")
                    flash('Score added successfully', 'success')
            elif 'delete' in request.form:
                if not is_admin():
                    logger.warning(f"Editor intentó eliminar resultado sin permisos: {session.get('user_id')}")
                    flash('Only administrators can delete scores', 'error')
                    return redirect(url_for('admin.manage_scores'))
                score_id = request.form['deleteEntityId']
                logger.info(f"Eliminando resultado ID: {score_id}")
                cur.execute('DELETE FROM scores WHERE score_id = %s', (score_id,))
                flash('Score deleted successfully', 'success')
            db.commit()
            logger.debug("Transacción de resultados completada exitosamente")
        except Exception as e:
            db.rollback()
            logger.error(f"Error en gestión de resultados: {str(e)}", exc_info=True)
            flash('An error occurred: ' + str(e), 'error')
        finally:
            cur.close()
        return redirect(url_for('admin.manage_scores'))

    # GET
    try:
        cur.execute('SELECT s.score_id, m.utc_date, s.full_time_home, s.full_time_away, s.half_time_home, s.half_time_away FROM scores s JOIN matches m ON s.match_id = m.match_id')
        scores = cur.fetchall()
        cur.execute('SELECT match_id, utc_date FROM matches')
        matches = cur.fetchall()
        logger.debug(f"Obtenidos {len(scores)} resultados para mostrar")
    except Exception as e:
        logger.error(f"Error al obtener resultados/partidos: {str(e)}")
        scores = []
        matches = []
    finally:
        cur.close()
    return render_template('manage_scores.html', scores=scores, matches=matches, is_admin=is_admin(), is_editor=is_editor())

@admin_bp.route('/manage_users', methods=['GET', 'POST'])
@admin_required
def manage_users():
    logger.info(f"Iniciando gestión de usuarios - Método: {request.method}")
    db = get_db()
    cur = db.cursor()
    
    if request.method == 'POST':
        try:
            if not session.get('is_admin'):
                logger.warning(f"Editor intentó modificar privilegios de usuario: {session.get('user_id')}")
                flash('Only administrators can modify user privileges', 'error')
                return redirect(url_for('admin.manage_users'))
            
            user_id = request.form.get('user_id')
            role = request.form.get('role')  # "user", "editor", o "admin"
            
            logger.info(f"Actualizando usuario ID: {user_id} - Rol: {role}")
            
            if role == 'admin':
                cur.execute('UPDATE users SET is_admin = 1, is_editor = 0 WHERE user_id = %s', (user_id,))
                flash('User role updated to Administrator', 'success')
            elif role == 'editor':
                cur.execute('UPDATE users SET is_admin = 0, is_editor = 1 WHERE user_id = %s', (user_id,))
                flash('User role updated to Editor', 'success')
            else:  # 'user' o cualquier otro valor
                cur.execute('UPDATE users SET is_admin = 0, is_editor = 0 WHERE user_id = %s', (user_id,))
                flash('User role updated to Usuario', 'success')
            
            db.commit()
            logger.info(f"Rol actualizado para usuario {user_id}")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error en gestión de usuarios: {str(e)}", exc_info=True)
            flash('An error occurred: ' + str(e), 'error')
        finally:
            cur.close()
        
        return redirect(url_for('admin.manage_users'))
    
    # GET
    try:
        cur.execute('SELECT user_id, username, email, is_admin, is_editor FROM users')
        users = cur.fetchall()
        logger.debug(users)
        logger.debug(f"Obtenidos {len(users)} usuarios para mostrar")
    except Exception as e:
        logger.error(f"Error al obtener usuarios: {str(e)}")
        users = []
    finally:
        cur.close()
    
    return render_template('manage_users.html', users=users, is_admin=is_admin())

from datetime import datetime, timedelta

from datetime import datetime, timedelta

@admin_bp.route('/calendar')
@admin_bp.route('/calendar/<int:year>/<int:month>/<int:day>')
def calendar(year=None, month=None, day=None):
    logger.info("Accediendo al calendario deportivo público")
    db = get_db()
    cur = db.cursor()
    
    # Determinar fecha de inicio (lunes de la semana actual o especificada)
    if year and month and day:
        target_date = datetime(year, month, day)
        # Encontrar el lunes de esa semana
        start_date = target_date - timedelta(days=target_date.weekday())
    else:
        today = datetime.now()
        start_date = today - timedelta(days=today.weekday())  # Lunes actual
    
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=7)
    
    # Fechas para navegación
    prev_week = start_date - timedelta(days=7)
    next_week = start_date + timedelta(days=7)
    
    try:
        # Obtener partidos por fecha (solo DATE)
        cur.execute('''
            SELECT 
                m.match_id,
                m.utc_date::date,
                ht.name AS home_team,
                at.name AS away_team,
                s.name AS sport_name,
                st.name AS stadium_name
            FROM matches m
            LEFT JOIN teams ht ON m.home_team_id = ht.team_id
            LEFT JOIN teams at ON m.away_team_id = at.team_id
            LEFT JOIN sports s ON m.sport_id = s.sport_id
            LEFT JOIN stadiums st ON m.stadium_id = st.stadium_id
            WHERE m.utc_date::date >= %s AND m.utc_date::date < %s
            ORDER BY m.utc_date::date ASC
        ''', (start_date, end_date))
        matches = cur.fetchall()
        
        # Obtener deportes únicos para la leyenda
        cur.execute('SELECT sport_id, name FROM sports ORDER BY name')
        sports = cur.fetchall()
        
        logger.debug(f"Calendario: {len(matches)} partidos, {len(sports)} deportes")
    except Exception as e:
        logger.error(f"Error al obtener datos del calendario: {str(e)}")
        matches, sports = [], []
    finally:
        cur.close()
    
    # Agrupar partidos por fecha
    matches_by_date = {}
    for match in matches:
        date_str = match[1].strftime('%Y-%m-%d')
        if date_str not in matches_by_date:
            matches_by_date[date_str] = []
        matches_by_date[date_str].append({
            'match_id': match[0],
            'date': match[1].strftime('%Y-%m-%d'),
            'home_team': match[2] or 'TBD',
            'away_team': match[3] or 'TBD',
            'sport_name': match[4] or 'Unknown',
            'stadium_name': match[5] or 'TBD'
        })
    
    # Generar fechas de la semana (Lun-Dom)
    week_dates = []
    for i in range(7):
        current_date = start_date + timedelta(days=i)
        week_dates.append({
            'date_str': current_date.strftime('%Y-%m-%d'),
            'day_num': current_date.strftime('%d'),
            'day_name': current_date.strftime('%a'),
            'is_weekend': current_date.weekday() >= 5
        })
    
    # Nombre del mes en español
    month_names = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                   "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    current_month_name = month_names[start_date.month]
    
    return render_template(
        'calendar.html',
        matches_by_date=matches_by_date,
        sports=sports,
        week_dates=week_dates,
        start_date=start_date.strftime('%Y-%m-%d'),
        current_month_name=current_month_name,
        prev_week={'year': prev_week.year, 'month': prev_week.month, 'day': prev_week.day},
        next_week={'year': next_week.year, 'month': next_week.month, 'day': next_week.day},
        is_admin=is_admin(),
        is_editor=is_editor()
    )

@admin_bp.route('/add_user', methods=['GET', 'POST'])
@admin_required
def add_user():
    """
    Permite a los administradores añadir nuevos usuarios usando su username de LDAP.
    Los usuarios se crean como editores por defecto y se obtiene su email desde LDAP.
    """
    if not session.get('is_admin'):
        flash('Only administrators can add new users', 'error')
        return redirect(url_for('admin.manage_users'))
    
    if request.method == 'POST':
        try:
            username = request.form['username'].strip()
            
            if not username:
                flash('Username is required', 'error')
                return redirect(url_for('admin.add_user'))
            
            db = get_db()
            cur = db.cursor()
            
            # Verificar si el usuario ya existe en la base de datos local
            cur.execute('SELECT user_id FROM users WHERE username = %s', (username,))
            existing_user = cur.fetchone()
            
            if existing_user:
                flash('User already exists in the system', 'error')
                return redirect(url_for('admin.add_user'))
            
            # Obtener información del usuario desde LDAP
            from ldap_auth import get_user_info
            user_info = get_user_info(username)

            if not user_info:
                flash('User not found in LDAP. Only existing LDAP users can be added.', 'error')
                return redirect(url_for('admin.add_user'))

            email = user_info.get('email', f'{username}@uh.cu') if user_info else f'{username}@uh.cu'
            
            # Crear usuario como editor por defecto (sin contraseña local para autenticación LDAP)
            cur.execute(
                'INSERT INTO users (username, password, email, is_admin, is_editor) VALUES (%s, %s, %s, %s, %s)',
                (username, '', email, False, True)
            )
            db.commit()
            cur.close()
            
            logger.info(f"Admin {session.get('user_id')} created new editor user: {username}")
            flash(f'User {username} added successfully as editor', 'success')
            return redirect(url_for('admin.add_user'))
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user {username}: {str(e)}", exc_info=True)
            flash('Failed to add user. Please check the username and try again.', 'error')
            return redirect(url_for('admin.add_user'))
    
    # GET: mostrar formulario
    return render_template('add_user.html')