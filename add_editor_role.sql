-- SQL script to add editor role to the system
-- Add is_editor column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_editor BOOLEAN DEFAULT FALSE;

-- Create a new function to check if user is editor
-- We'll also update the admin_required decorator logic in Python code

-- Grant appropriate permissions to editors (data modification but not structural changes)
-- Editors can SELECT, INSERT, UPDATE, DELETE but cannot ALTER, CREATE, DROP tables
-- This will be handled through application logic since we're using a simple permission model