"""
Script para migrar la base de datos y agregar la funcionalidad de deportes
"""
import psycopg2
from db import get_db
import sys
from flask import Flask
from config import Config

def migrate_database():
    """Realiza la migración de la base de datos para agregar soporte de deportes"""
    try:
        # Obtener conexión a la base de datos
        db = get_db()
        cur = db.cursor()
        
        # Crear tabla de deportes si no existe
        cur.execute("""
            CREATE TABLE IF NOT EXISTS public.sports (
                sport_id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                icon_url VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Añadir columna sport_id a la tabla leagues si no existe
        cur.execute("""
            ALTER TABLE public.leagues 
            ADD COLUMN IF NOT EXISTS sport_id INTEGER;
        """)
        
        # Crear deporte por defecto si no existe
        cur.execute("""
            INSERT INTO sports (name, description) 
            SELECT 'Football', 'Association Football/Soccer'
            WHERE NOT EXISTS (SELECT 1 FROM sports WHERE name = 'Football');
        """)
        
        # Asociar ligas existentes al deporte por defecto
        cur.execute("""
            UPDATE public.leagues 
            SET sport_id = (SELECT sport_id FROM sports WHERE name = 'Football')
            WHERE sport_id IS NULL;
        """)
        
        # Añadir restricción de clave foránea
        try:
            cur.execute("""
                ALTER TABLE public.leagues 
                ADD CONSTRAINT leagues_sport_id_fkey 
                FOREIGN KEY (sport_id) REFERENCES public.sports(sport_id);
            """)
        except psycopg2.errors.DuplicateObject:
            # La restricción ya existe
            pass
        
        # Crear índice
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_leagues_sport_id ON public.leagues(sport_id);
        """)
        
        # Confirmar cambios
        db.commit()
        cur.close()
        
        print("Migración completada exitosamente.")
        
    except Exception as e:
        print(f"Error durante la migración: {str(e)}")
        if 'db' in locals():
            db.rollback()
        return False
    
    return True

if __name__ == "__main__":
    success = migrate_database()
    if not success:
        sys.exit(1)