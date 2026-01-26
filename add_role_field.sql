-- Script para añadir un nuevo campo de rol a la tabla users
-- Reemplaza el campo is_admin boolean con un campo role que puede tener múltiples valores

-- Añadir nueva columna role con valor predeterminado 'user'
ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user';

-- Actualizar los roles existentes basados en el valor de is_admin
-- Los administradores actuales seguirán siendo administradores
UPDATE users SET role = 'admin' WHERE is_admin = true;
-- Los usuarios no administradores serán 'user' por defecto
UPDATE users SET role = 'user' WHERE is_admin = false;

-- Eliminar la columna is_admin ya que ahora usaremos el campo role
ALTER TABLE users DROP COLUMN is_admin;

-- Agregar restricción para limitar los valores posibles del campo role
ALTER TABLE users ADD CONSTRAINT valid_role CHECK (role IN ('user', 'editor', 'admin'));

-- Opcional: Asignar algunos usuarios como editores si se desea
-- UPDATE users SET role = 'editor' WHERE user_id IN (lista_de_ids);