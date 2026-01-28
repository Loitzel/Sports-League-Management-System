-- Paso 1: Renombrar tablas
ALTER TABLE leagues RENAME TO sports;
ALTER TABLE countries RENAME TO faculties;

-- Paso 2: Renombrar las claves primarias para que coincidan con la nueva semántica
ALTER TABLE faculties RENAME COLUMN country_id TO faculty_id;
ALTER TABLE sports RENAME COLUMN league_id TO sport_id;

-- Paso 3: Eliminar columnas innecesarias
ALTER TABLE sports
    DROP COLUMN IF EXISTS country,
    DROP COLUMN IF EXISTS country_id,
    DROP COLUMN IF EXISTS icon_url,
    DROP COLUMN IF EXISTS cl_spot,
    DROP COLUMN IF EXISTS uel_spot,
    DROP COLUMN IF EXISTS relegation_spot;

ALTER TABLE faculties
    DROP COLUMN IF EXISTS flag_url;

-- Paso 4: Eliminar nacionalidad en entidades personales
ALTER TABLE coaches DROP COLUMN IF EXISTS nationality;
ALTER TABLE players DROP COLUMN IF EXISTS nationality;
ALTER TABLE referees DROP COLUMN IF EXISTS nationality;

-- Paso 5: Añadir faculty_id a teams (ahora sí existe faculties.faculty_id)
ALTER TABLE teams
    ADD COLUMN IF NOT EXISTS faculty_id INTEGER REFERENCES faculties(faculty_id);

-- Paso 6: Renombrar league_id → sport_id en todas las tablas relacionadas
ALTER TABLE seasons RENAME COLUMN league_id TO sport_id;
ALTER TABLE teams RENAME COLUMN league_id TO sport_id;
ALTER TABLE matches RENAME COLUMN league_id TO sport_id;
ALTER TABLE scorers RENAME COLUMN league_id TO sport_id;

-- Paso 7: Eliminar league_id de standings (ya no se necesita)
ALTER TABLE standings DROP COLUMN IF EXISTS league_id;

-- Paso 8: Crear índices
CREATE INDEX IF NOT EXISTS idx_teams_sport ON teams(sport_id);
CREATE INDEX IF NOT EXISTS idx_teams_faculty ON teams(faculty_id);
CREATE INDEX IF NOT EXISTS idx_matches_sport_season ON matches(sport_id, season_id);
CREATE INDEX IF NOT EXISTS idx_standings_season ON standings(season_id);
CREATE INDEX IF NOT EXISTS idx_scorers_season_sport ON scorers(season_id, sport_id);