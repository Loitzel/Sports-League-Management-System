-- Create sports table
CREATE TABLE IF NOT EXISTS public.sports (
    sport_id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add sport_id column to leagues table
ALTER TABLE public.leagues ADD COLUMN IF NOT EXISTS sport_id INTEGER;

-- Update existing leagues to associate with a default sport (creating a default sport if needed)
INSERT INTO sports (name, description) 
SELECT 'Football', 'Association Football/Soccer'
WHERE NOT EXISTS (SELECT 1 FROM sports WHERE name = 'Football');

-- Set sport_id for existing leagues
UPDATE public.leagues 
SET sport_id = (SELECT sport_id FROM sports WHERE name = 'Football')
WHERE sport_id IS NULL;

-- Add foreign key constraint
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'leagues_sport_id_fkey') THEN
        ALTER TABLE public.leagues ADD CONSTRAINT leagues_sport_id_fkey 
        FOREIGN KEY (sport_id) REFERENCES public.sports(sport_id);
    END IF;
END $$;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_leagues_sport_id ON public.leagues(sport_id);