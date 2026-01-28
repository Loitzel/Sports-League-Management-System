from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from functools import wraps
from db import get_db
import logging
import sys

admin_bp = Blueprint('admin', __name__)

# Configurar logger específico para el módulo admin
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Configurar handler para stdout (Docker captura stdout/stderr)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)

# Formato detallado para Docker logs
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(funcName)s]'
)
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
        
        # Verificar si es admin o editor
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

def get_existing_data(table_name):
    logger.info(f"Obteniendo datos de tabla: {table_name}")
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute(f'SELECT * FROM {table_name}')
        data = cur.fetchall()
        cur.close()
        logger.debug(f"Datos obtenidos de {table_name}: {len(data)} registros")
        return data
    except Exception as e:
        logger.error(f"Error al obtener datos de {table_name}: {str(e)}")
        raise

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

    # GET request
    try:
        cur.execute('SELECT stadium_id, name, location, capacity FROM stadiums')
        stadiums = cur.fetchall()
        logger.debug(f"Obtenidos {len(stadiums)} estadios para mostrar")
    except Exception as e:
        logger.error(f"Error al obtener estadios: {str(e)}")
        stadiums = []
    finally:
        cur.close()
    
    logger.info("Renderizando plantilla de gestión de estadios")
    return render_template('manage_stadiums.html', stadiums=stadiums, is_admin=is_admin(), is_editor=is_editor())

@admin_bp.route('/manage_leagues', methods=['GET', 'POST'])
@admin_required
def manage_leagues():
    logger.info(f"Iniciando gestión de ligas - Método: {request.method}")
    db = get_db()
    cur = db.cursor()

    if request.method == 'POST':
        try:
            league_id = request.form.get('league_id')
            name = request.form['name']
            country = request.form['country']

            logger.info(f"Procesando liga - ID: {league_id}, Nombre: {name}")

            if 'add' in request.form:
                if not is_admin():
                    logger.warning(f"Editor intentó agregar liga sin permisos: {session.get('user_id')}")
                    flash('Only administrators can add new leagues', 'error')
                    return redirect(url_for('admin.manage_leagues'))
                
                cur.execute('INSERT INTO leagues (name, country) VALUES (%s, %s)', 
                            (name, country))
                logger.info(f"Liga agregada: {name} ({country})")
                flash('League added successfully', 'success')
                
            elif 'edit' in request.form and league_id:
                logger.info(f"Editando liga ID: {league_id}")
                cur.execute('UPDATE leagues SET name = %s, country = %s WHERE league_id = %s', 
                            (name, country, league_id))
                flash('League updated successfully', 'success')
                
            elif 'delete' in request.form and league_id:
                if not is_admin():
                    logger.warning(f"Editor intentó eliminar liga sin permisos: {session.get('user_id')}")
                    flash('Only administrators can delete leagues', 'error')
                    return redirect(url_for('admin.manage_leagues'))
                
                logger.info(f"Eliminando liga ID: {league_id}")
                cur.execute('DELETE FROM leagues WHERE league_id = %s', (league_id,))
                flash('League deleted successfully', 'success')
                
            db.commit()
            logger.debug("Transacción de ligas completada exitosamente")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error en gestión de ligas: {str(e)}", exc_info=True)
            flash('An error occurred: ' + str(e), 'error')
        finally:
            cur.close()
            
        return redirect(url_for('admin.manage_leagues'))

    # GET request
    try:
        cur.execute('SELECT league_id, name, country FROM leagues')
        leagues = cur.fetchall()
        logger.debug(f"Obtenidas {len(leagues)} ligas para mostrar")
    except Exception as e:
        logger.error(f"Error al obtener ligas: {str(e)}")
        leagues = []
    finally:
        cur.close()
        
    logger.info("Renderizando plantilla de gestión de ligas")
    return render_template('manage_leagues.html', leagues=leagues, is_admin=is_admin(), is_editor=is_editor())

@admin_bp.route('/manage_seasons', methods=['GET', 'POST'])
@admin_required
def manage_seasons():
    logger.info(f"Iniciando gestión de temporadas - Método: {request.method}")
    db = get_db()
    cur = db.cursor()

    if request.method == 'POST':
        try:
            season_id = request.form.get('season_id')
            league_id = request.form['league_id']
            year = request.form['year']

            logger.info(f"Procesando temporada - ID: {season_id}, Año: {year}, Liga ID: {league_id}")

            if 'add' in request.form:
                if not is_admin():
                    logger.warning(f"Editor intentó agregar temporada sin permisos: {session.get('user_id')}")
                    flash('Only administrators can add new seasons', 'error')
                    return redirect(url_for('admin.manage_seasons'))
                
                cur.execute('INSERT INTO seasons (league_id, year) VALUES (%s, %s)', (league_id, year))
                logger.info(f"Temporada agregada: Año {year} para liga {league_id}")
                flash('Season added successfully', 'success')
                
            elif 'edit' in request.form and season_id:
                logger.info(f"Editando temporada ID: {season_id}")
                cur.execute('UPDATE seasons SET league_id = %s, year = %s WHERE season_id = %s', 
                            (league_id, year, season_id))
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

    # GET request
    try:
        cur.execute('''
            SELECT s.season_id, s.league_id, s.year, l.name
            FROM seasons s
            JOIN leagues l ON s.league_id = l.league_id
        ''')
        seasons = cur.fetchall()
        logger.debug(f"Obtenidas {len(seasons)} temporadas para mostrar")
        
        cur.execute('SELECT league_id, name FROM leagues')
        leagues = cur.fetchall()
        logger.debug(f"Obtenidas {len(leagues)} ligas para formulario")
    except Exception as e:
        logger.error(f"Error al obtener temporadas/ligas: {str(e)}")
        seasons = []
        leagues = []
    finally:
        cur.close()
        
    logger.info("Renderizando plantilla de gestión de temporadas")
    return render_template('manage_seasons.html', seasons=seasons, leagues=leagues, 
                          is_admin=is_admin(), is_editor=is_editor())

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
            founded_year = request.form['founded_year']
            stadium_id = request.form['stadium_id']
            league_id = request.form['league_id']
            coach_id = request.form['coach_id']

            logger.info(f"Procesando equipo - ID: {team_id}, Nombre: {name}")

            if 'add' in request.form:
                if not is_admin():
                    logger.warning(f"Editor intentó agregar equipo sin permisos: {session.get('user_id')}")
                    flash('Only administrators can add new teams', 'error')
                    return redirect(url_for('admin.manage_teams'))
                
                cur.execute('INSERT INTO teams (name, founded_year, stadium_id, league_id, coach_id) VALUES (%s, %s, %s, %s, %s)', 
                            (name, founded_year, stadium_id, league_id, coach_id))
                logger.info(f"Equipo agregado: {name} (Año fundación: {founded_year})")
                flash('Team added successfully', 'success')
                
            elif 'edit' in request.form and team_id:
                logger.info(f"Editando equipo ID: {team_id}")
                cur.execute('UPDATE teams SET name = %s, founded_year = %s, stadium_id = %s, league_id = %s, coach_id = %s WHERE team_id = %s', 
                            (name, founded_year, stadium_id, league_id, coach_id, team_id))
                flash('Team updated successfully', 'success')
                
            elif 'delete' in request.form and team_id:
                if not is_admin():
                    logger.warning(f"Editor intentó eliminar equipo sin permisos: {session.get('user_id')}")
                    flash('Only administrators can delete teams', 'error')
                    return redirect(url_for('admin.manage_teams'))
                
                logger.info(f"Eliminando equipo ID: {team_id}")
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

    # GET request
    try:
        cur.execute('SELECT team_id, name, founded_year, stadium_id, league_id, coach_id FROM teams')
        teams = cur.fetchall()
        logger.debug(f"Obtenidos {len(teams)} equipos para mostrar")
        
        cur.execute('SELECT stadium_id, name FROM stadiums')
        stadiums = cur.fetchall()
        
        cur.execute('SELECT league_id, name FROM leagues')
        leagues = cur.fetchall()
        
        cur.execute('SELECT coach_id, name FROM coaches')
        coaches = cur.fetchall()
        
        logger.debug(f"Datos obtenidos: {len(stadiums)} estadios, {len(leagues)} ligas, {len(coaches)} entrenadores")
    except Exception as e:
        logger.error(f"Error al obtener datos de equipos: {str(e)}")
        teams = []
        stadiums = []
        leagues = []
        coaches = []
    finally:
        cur.close()
        
    logger.info("Renderizando plantilla de gestión de equipos")
    return render_template('manage_teams.html', teams=teams, stadiums=stadiums, leagues=leagues, 
                          coaches=coaches, is_admin=is_admin(), is_editor=is_editor())

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
            nationality = request.form['nationality']
            team_id = request.form['team_id']

            logger.info(f"Procesando entrenador - ID: {coach_id}, Nombre: {name}")

            if 'add' in request.form:
                if not is_admin():
                    logger.warning(f"Editor intentó agregar entrenador sin permisos: {session.get('user_id')}")
                    flash('Only administrators can add new coaches', 'error')
                    return redirect(url_for('admin.manage_coaches'))
                
                cur.execute('INSERT INTO coaches (name, nationality, team_id) VALUES (%s, %s, %s)', 
                            (name, nationality, team_id))
                logger.info(f"Entrenador agregado: {name} ({nationality})")
                flash('Coach added successfully', 'success')
                
            elif 'submit' in request.form and coach_id:
                logger.info(f"Editando entrenador ID: {coach_id}")
                cur.execute('UPDATE coaches SET name = %s, nationality = %s, team_id = %s WHERE coach_id = %s', 
                            (name, nationality, team_id, coach_id))
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

    # GET request
    try:
        cur.execute('''
            SELECT c.coach_id, c.name, c.team_id, c.nationality, t.name AS team_name
            FROM coaches c
            JOIN teams t ON c.team_id = t.team_id
        ''')
        coaches = cur.fetchall()
        logger.debug(f"Obtenidos {len(coaches)} entrenadores para mostrar")
        
        cur.execute('SELECT team_id, name FROM teams')
        teams = cur.fetchall()
        logger.debug(f"Obtenidos {len(teams)} equipos para formulario")
    except Exception as e:
        logger.error(f"Error al obtener entrenadores/equipos: {str(e)}")
        coaches = []
        teams = []
    finally:
        cur.close()
        
    logger.info("Renderizando plantilla de gestión de entrenadores")
    return render_template('manage_coaches.html', coaches=coaches, teams=teams, 
                          is_admin=is_admin(), is_editor=is_editor())

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
            nationality = request.form['nationality']

            logger.info(f"Procesando jugador - ID: {player_id}, Nombre: {name}, Posición: {position}")

            if 'submit' in request.form:
                if player_id:
                    # Editar jugador existente
                    logger.info(f"Editando jugador ID: {player_id}")
                    cur.execute('UPDATE players SET team_id = %s, name = %s, position = %s, date_of_birth = %s, nationality = %s WHERE player_id = %s', 
                                (team_id, name, position, date_of_birth, nationality, player_id))
                    flash('Player updated successfully', 'success')
                else:
                    # Agregar nuevo jugador
                    if not is_admin():
                        logger.warning(f"Editor intentó agregar jugador sin permisos: {session.get('user_id')}")
                        flash('Only administrators can add new players', 'error')
                        return redirect(url_for('admin.manage_players'))
                    
                    cur.execute('INSERT INTO players (team_id, name, position, date_of_birth, nationality) VALUES (%s, %s, %s, %s, %s)', 
                                (team_id, name, position, date_of_birth, nationality))
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

    # GET request
    try:
        cur.execute('SELECT p.player_id, t.name AS team, p.name, p.position, p.date_of_birth, p.nationality, p.team_id FROM players p JOIN teams t ON p.team_id = t.team_id')
        players = cur.fetchall()
        logger.debug(f"Obtenidos {len(players)} jugadores para mostrar")
        
        cur.execute('SELECT team_id, name FROM teams')
        teams = cur.fetchall()
        logger.debug(f"Obtenidos {len(teams)} equipos para formulario")
    except Exception as e:
        logger.error(f"Error al obtener jugadores/equipos: {str(e)}")
        players = []
        teams = []
    finally:
        cur.close()
        
    logger.info("Renderizando plantilla de gestión de jugadores")
    return render_template('manage_players.html', players=players, teams=teams, 
                          is_admin=is_admin(), is_editor=is_editor())

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
            league_id = request.form['league_id']

            logger.info(f"Procesando partido - ID: {match_id}, Fecha: {date}, Equipos: {team1_id} vs {team2_id}")

            if 'submit' in request.form:
                if match_id:
                    # Editar partido existente
                    logger.info(f"Editando partido ID: {match_id}")
                    cur.execute('UPDATE matches SET utc_date = %s, home_team_id = %s, away_team_id = %s, season_id = %s, league_id = %s WHERE match_id = %s', 
                                (date, team1_id, team2_id, season_id, league_id, match_id))
                    flash('Match updated successfully', 'success')
                else:
                    # Agregar nuevo partido
                    if not is_admin():
                        logger.warning(f"Editor intentó agregar partido sin permisos: {session.get('user_id')}")
                        flash('Only administrators can add new matches', 'error')
                        return redirect(url_for('admin.manage_matches'))
                    
                    cur.execute('INSERT INTO matches (utc_date, home_team_id, away_team_id, season_id, league_id) VALUES (%s, %s, %s, %s, %s)', 
                                (date, team1_id, team2_id, season_id, league_id))
                    logger.info(f"Partido agregado: {date} - Liga {league_id}")
                    flash('Match added successfully', 'success')
                    
            elif 'delete' in request.form:
                if not is_admin():
                    logger.warning(f"Editor intentó eliminar partido sin permisos: {session.get('user_id')}")
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

    # GET request
    try:
        cur.execute('''
            SELECT m.match_id, m.utc_date, t1.name AS team1, t2.name AS team2, s.year AS season, l.name AS league,
                   m.home_team_id, m.away_team_id
            FROM matches m
            JOIN teams t1 ON m.home_team_id = t1.team_id
            JOIN teams t2 ON m.away_team_id = t2.team_id
            JOIN seasons s ON m.season_id = s.season_id
            JOIN leagues l ON m.league_id = l.league_id
        ''')
        matches = cur.fetchall()
        logger.debug(f"Obtenidos {len(matches)} partidos para mostrar")
        
        cur.execute('SELECT team_id, name FROM teams')
        teams = cur.fetchall()
        
        cur.execute('SELECT season_id, year FROM seasons')
        seasons = cur.fetchall()
        
        cur.execute('SELECT league_id, name FROM leagues')
        leagues = cur.fetchall()
        
        logger.debug(f"Datos obtenidos: {len(teams)} equipos, {len(seasons)} temporadas, {len(leagues)} ligas")
    except Exception as e:
        logger.error(f"Error al obtener datos de partidos: {str(e)}")
        matches = []
        teams = []
        seasons = []
        leagues = []
    finally:
        cur.close()
        
    logger.info("Renderizando plantilla de gestión de partidos")
    return render_template('manage_matches.html', matches=matches, teams=teams, seasons=seasons, 
                          leagues=leagues, is_admin=is_admin(), is_editor=is_editor())

@admin_bp.route('/manage_countries', methods=['GET', 'POST'])
@admin_required
def manage_countries():
    logger.info(f"Iniciando gestión de países - Método: {request.method}")
    db = get_db()
    cur = db.cursor()

    if request.method == 'POST':
        try:
            country_id = request.form.get('country_id')
            name = request.form['name']
            flag_url = request.form['flag_url']

            logger.info(f"Procesando país - ID: {country_id}, Nombre: {name}")

            if 'submit' in request.form:
                if country_id:
                    # Editar país existente
                    logger.info(f"Editando país ID: {country_id}")
                    cur.execute('UPDATE countries SET name = %s, flag_url = %s WHERE country_id = %s', 
                                (name, flag_url, country_id))
                    flash('Country updated successfully', 'success')
                else:
                    # Agregar nuevo país
                    if not is_admin():
                        logger.warning(f"Editor intentó agregar país sin permisos: {session.get('user_id')}")
                        flash('Only administrators can add new countries', 'error')
                        return redirect(url_for('admin.manage_countries'))
                    
                    cur.execute('INSERT INTO countries (name, flag_url) VALUES (%s, %s)', 
                                (name, flag_url))
                    logger.info(f"País agregado: {name}")
                    flash('Country added successfully', 'success')
                    
            elif 'delete' in request.form:
                if not is_admin():
                    logger.warning(f"Editor intentó eliminar país sin permisos: {session.get('user_id')}")
                    flash('Only administrators can delete countries', 'error')
                    return redirect(url_for('admin.manage_countries'))
                
                country_id = request.form['deleteEntityId']
                logger.info(f"Eliminando país ID: {country_id}")
                cur.execute('DELETE FROM countries WHERE country_id = %s', (country_id,))
                flash('Country deleted successfully', 'success')
                
            db.commit()
            logger.debug("Transacción de países completada exitosamente")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error en gestión de países: {str(e)}", exc_info=True)
            flash('An error occurred: ' + str(e), 'error')
        finally:
            cur.close()
            
        return redirect(url_for('admin.manage_countries'))

    # GET request
    try:
        cur.execute('SELECT country_id, name, flag_url FROM countries')
        countries = cur.fetchall()
        logger.debug(f"Obtenidos {len(countries)} países para mostrar")
    except Exception as e:
        logger.error(f"Error al obtener países: {str(e)}")
        countries = []
    finally:
        cur.close()
        
    logger.info("Renderizando plantilla de gestión de países")
    return render_template('manage_countries.html', countries=countries, 
                          is_admin=is_admin(), is_editor=is_editor())

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
            nationality = request.form['nationality']

            logger.info(f"Procesando árbitro - ID: {referee_id}, Nombre: {name}")

            if 'submit' in request.form:
                if referee_id:
                    # Editar árbitro existente
                    logger.info(f"Editando árbitro ID: {referee_id}")
                    cur.execute('UPDATE referees SET name = %s, nationality = %s WHERE referee_id = %s', 
                                (name, nationality, referee_id))
                    flash('Referee updated successfully', 'success')
                else:
                    # Agregar nuevo árbitro
                    if not is_admin():
                        logger.warning(f"Editor intentó agregar árbitro sin permisos: {session.get('user_id')}")
                        flash('Only administrators can add new referees', 'error')
                        return redirect(url_for('admin.manage_referees'))
                    
                    cur.execute('INSERT INTO referees (name, nationality) VALUES (%s, %s)', 
                                (name, nationality))
                    logger.info(f"Árbitro agregado: {name} ({nationality})")
                    flash('Referee added successfully', 'success')
                    
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

    # GET request
    try:
        cur.execute('SELECT referee_id, name, nationality FROM referees')
        referees = cur.fetchall()
        logger.debug(f"Obtenidos {len(referees)} árbitros para mostrar")
    except Exception as e:
        logger.error(f"Error al obtener árbitros: {str(e)}")
        referees = []
    finally:
        cur.close()
        
    logger.info("Renderizando plantilla de gestión de árbitros")
    return render_template('manage_referees.html', referees=referees, 
                          is_admin=is_admin(), is_editor=is_editor())

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
            league_id = request.form['league_id']
            goals = request.form['goals']
            assists = request.form['assists']
            penalties = request.form['penalties']

            logger.info(f"Procesando goleador - ID: {scorer_id}, Goles: {goals}, Asistencias: {assists}")

            if 'submit' in request.form:
                if scorer_id:
                    # Editar goleador existente
                    logger.info(f"Editando goleador ID: {scorer_id}")
                    cur.execute('UPDATE scorers SET player_id = %s, season_id = %s, league_id = %s, goals = %s, assists = %s, penalties = %s WHERE scorer_id = %s',
                                (player_id, season_id, league_id, goals, assists, penalties, scorer_id))
                    flash('Scorer updated successfully', 'success')
                else:
                    # Agregar nuevo goleador
                    if not is_admin():
                        logger.warning(f"Editor intentó agregar goleador sin permisos: {session.get('user_id')}")
                        flash('Only administrators can add new scorers', 'error')
                        return redirect(url_for('admin.manage_scorers'))
                    
                    cur.execute('INSERT INTO scorers (player_id, season_id, league_id, goals, assists, penalties) VALUES (%s, %s, %s, %s, %s, %s)',
                                (player_id, season_id, league_id, goals, assists, penalties))
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

    # GET request
    try:
        cur.execute('''
            SELECT s.scorer_id, p.name, se.year, l.name, s.goals, s.assists, s.penalties 
            FROM scorers s 
            JOIN players p ON s.player_id = p.player_id 
            JOIN seasons se ON s.season_id = se.season_id 
            JOIN leagues l ON s.league_id = l.league_id
        ''')
        scorers = cur.fetchall()
        logger.debug(f"Obtenidos {len(scorers)} goleadores para mostrar")
        
        cur.execute('SELECT player_id, name FROM players')
        players = cur.fetchall()
        
        cur.execute('SELECT season_id, year FROM seasons')
        seasons = cur.fetchall()
        
        cur.execute('SELECT league_id, name FROM leagues')
        leagues = cur.fetchall()
        
        logger.debug(f"Datos obtenidos: {len(players)} jugadores, {len(seasons)} temporadas, {len(leagues)} ligas")
    except Exception as e:
        logger.error(f"Error al obtener datos de goleadores: {str(e)}")
        scorers = []
        players = []
        seasons = []
        leagues = []
    finally:
        cur.close()
        
    logger.info("Renderizando plantilla de gestión de goleadores")
    return render_template('manage_scorers.html', scorers=scorers, players=players, 
                          seasons=seasons, leagues=leagues, is_admin=is_admin(), 
                          is_editor=is_editor())

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
                    # Editar score existente
                    logger.info(f"Editando resultado ID: {score_id}")
                    cur.execute('UPDATE scores SET match_id = %s, full_time_home = %s, full_time_away = %s, half_time_home = %s, half_time_away = %s WHERE score_id = %s',
                                (match_id, full_time_home, full_time_away, half_time_home, half_time_away, score_id))
                    flash('Score updated successfully', 'success')
                else:
                    # Agregar nuevo score
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

    # GET request
    try:
        cur.execute('SELECT s.score_id, m.utc_date, s.full_time_home, s.full_time_away, s.half_time_home, s.half_time_away FROM scores s JOIN matches m ON s.match_id = m.match_id')
        scores = cur.fetchall()
        logger.debug(f"Obtenidos {len(scores)} resultados para mostrar")
        
        cur.execute('SELECT match_id, utc_date FROM matches')
        matches = cur.fetchall()
        logger.debug(f"Obtenidos {len(matches)} partidos para formulario")
    except Exception as e:
        logger.error(f"Error al obtener resultados/partidos: {str(e)}")
        scores = []
        matches = []
    finally:
        cur.close()
        
    logger.info("Renderizando plantilla de gestión de resultados")
    return render_template('manage_scores.html', scores=scores, matches=matches, 
                          is_admin=is_admin(), is_editor=is_editor())

@admin_bp.route('/manage_standings', methods=['GET', 'POST'])
@admin_required
def manage_standings():
    logger.info(f"Iniciando gestión de posiciones - Método: {request.method}")
    db = get_db()
    cur = db.cursor()

    if request.method == 'POST':
        try:
            standing_id = request.form.get('standing_id')
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
            form = request.form['form']

            logger.info(f"Procesando posición - ID: {standing_id}, Equipo: {team_id}, Puntos: {points}")

            if 'add' in request.form:
                if not is_admin():
                    logger.warning(f"Editor intentó agregar posición sin permisos: {session.get('user_id')}")
                    flash('Only administrators can add new standings', 'error')
                    return redirect(url_for('admin.manage_standings'))
                
                cur.execute('''
                    INSERT INTO standings (position, team_id, played_games, won, draw, lost, points, goals_for, goals_against, goal_difference, form)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (position, team_id, played_games, won, draw, lost, points, goals_for, goals_against, goal_difference, form))
                logger.info(f"Posición agregada para equipo {team_id}: Posición {position}, {points} puntos")
                flash('Standing added successfully', 'success')
                
            elif 'edit' in request.form and standing_id:
                logger.info(f"Editando posición ID: {standing_id}")
                cur.execute('''
                    UPDATE standings
                    SET position = %s, team_id = %s, played_games = %s, won = %s, draw = %s, lost = %s, points = %s, goals_for = %s, goals_against = %s, goal_difference = %s, form = %s
                    WHERE standing_id = %s
                ''', (position, team_id, played_games, won, draw, lost, points, goals_for, goals_against, goal_difference, form, standing_id))
                flash('Standing updated successfully', 'success')
                
            elif 'delete' in request.form:
                if not is_admin():
                    logger.warning(f"Editor intentó eliminar posición sin permisos: {session.get('user_id')}")
                    flash('Only administrators can delete standings', 'error')
                    return redirect(url_for('admin.manage_standings'))
                
                standing_id = request.form['deleteItemId']
                logger.info(f"Eliminando posición ID: {standing_id}")
                cur.execute('DELETE FROM standings WHERE standing_id = %s', (standing_id,))
                flash('Standing deleted successfully', 'success')
                
            db.commit()
            logger.debug("Transacción de posiciones completada exitosamente")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error en gestión de posiciones: {str(e)}", exc_info=True)
            flash('An error occurred: ' + str(e), 'error')
        finally:
            cur.close()
            
        return redirect(url_for('admin.manage_standings'))

    # GET request
    try:
        cur.execute('''
            SELECT s.standing_id, s.position, t.name, s.played_games, s.won, s.draw, s.lost, s.points, s.goals_for, s.goals_against, s.goal_difference, s.form, s.team_id
            FROM standings s
            JOIN teams t ON s.team_id = t.team_id
        ''')
        standings = cur.fetchall()
        logger.debug(f"Obtenidas {len(standings)} posiciones para mostrar")
        
        cur.execute('SELECT team_id, name FROM teams')
        teams = cur.fetchall()
        logger.debug(f"Obtenidos {len(teams)} equipos para formulario")
    except Exception as e:
        logger.error(f"Error al obtener posiciones/equipos: {str(e)}")
        standings = []
        teams = []
    finally:
        cur.close()
        
    logger.info("Renderizando plantilla de gestión de posiciones")
    return render_template('manage_standings.html', standings=standings, teams=teams, 
                          is_admin=is_admin(), is_editor=is_editor())

@admin_bp.route('/manage_users', methods=['GET', 'POST'])
@admin_required
def manage_users():
    logger.info(f"Iniciando gestión de usuarios - Método: {request.method}")
    db = get_db()
    cur = db.cursor()

    if request.method == 'POST':
        try:
            user_id = request.form.get('user_id')
            admin_status = request.form.get('is_admin') == 'true'
            editor_status = request.form.get('is_editor') == 'true'

            logger.info(f"Actualizando usuario ID: {user_id} - Admin: {admin_status}, Editor: {editor_status}")

            # Solo admins pueden modificar privilegios
            if not session.get('is_admin'):
                logger.warning(f"Editor intentó modificar privilegios de usuario: {session.get('user_id')}")
                flash('Only administrators can modify user privileges', 'error')
                return redirect(url_for('admin.manage_users'))
                
            cur.execute('UPDATE users SET is_admin = %s, is_editor = %s WHERE user_id = %s', 
                       (admin_status, editor_status, user_id))
            db.commit()
            logger.info(f"Privilegios actualizados para usuario {user_id}")
            flash('User privilege updated successfully', 'success')
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error en gestión de usuarios: {str(e)}", exc_info=True)
            flash('An error occurred: ' + str(e), 'error')
        finally:
            cur.close()
            
        return redirect(url_for('admin.manage_users'))

    # GET request
    try:
        cur.execute('SELECT user_id, username, is_admin, is_editor FROM users')
        users = cur.fetchall()
        logger.debug(f"Obtenidos {len(users)} usuarios para mostrar")
    except Exception as e:
        logger.error(f"Error al obtener usuarios: {str(e)}")
        users = []
    finally:
        cur.close()

    logger.info("Renderizando plantilla de gestión de usuarios")
    return render_template('manage_users.html', users=users, 
                          is_admin=is_admin(), is_editor=is_editor())