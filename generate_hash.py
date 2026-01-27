import bcrypt

# Generar hash para "editor"
editor_hash = bcrypt.hashpw("editor".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print("Editor hash:", editor_hash)

# Generar hash para "admin"
admin_hash = bcrypt.hashpw("admin".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print("Admin hash:", admin_hash)