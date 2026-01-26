-- Script para cambiar el concepto de "liga" a "deporte"
-- Se creará una nueva tabla "sports" y se modificarán las relaciones existentes

-- 1. Crear la tabla de deportes
CREATE TABLE IF NOT EXISTS public.sports (
    sport_id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Agregar la columna sport_id a la tabla leagues
ALTER TABLE public.leagues ADD COLUMN IF NOT EXISTS sport_id INTEGER;

-- 3. Actualizar los registros existentes en leagues para asociarlos a deportes
-- Primero creamos deportes basados en las ligas existentes
INSERT INTO public.sports (name, description)
SELECT DISTINCT 'Fútbol', 'Deporte de fútbol'
WHERE EXISTS (SELECT 1 FROM public.leagues LIMIT 1);

-- Luego asociamos cada liga existente a un deporte (todas las ligas serán de fútbol inicialmente)
UPDATE public.leagues 
SET sport_id = (SELECT sport_id FROM public.sports WHERE name = 'Fútbol')
WHERE sport_id IS NULL;

-- 4. Agregar la clave foránea
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'leagues_sport_id_fkey') THEN
        ALTER TABLE public.leagues ADD CONSTRAINT leagues_sport_id_fkey 
        FOREIGN KEY (sport_id) REFERENCES public.sports(sport_id);
    END IF;
END $$;

-- 5. Crear índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_leagues_sport_id ON public.leagues(sport_id);