import sqlite3

DB_PATH = 'miapp.db'

def buscar_usuario(username):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
    usuario = cursor.fetchone()
    conn.close()
    return usuario

def rutas_de_usuario(username):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.nombre
        FROM rutas r
        JOIN rutas_usuario ru ON r.id = ru.ruta_id
        JOIN usuarios u ON ru.usuario_id = u.id
        WHERE u.username = ?
    """, (username,))
    rutas = [row['nombre'] for row in cursor.fetchall()]
    conn.close()
    return rutas

def amigos_de_usuario(username):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE username = ?", (username,))
    usuario = cursor.fetchone()
    if not usuario:
        return []
    user_id = usuario['id']
    cursor.execute("""
        SELECT u.username
        FROM usuarios u
        JOIN amistades a ON a.amigo_id = u.id
        WHERE a.usuario_id = ?
    """, (user_id,))
    amigos = [row['username'] for row in cursor.fetchall()]
    conn.close()
    return amigos

def insertar_usuario(nombre, apellido, email, username, telefono, fecha_nacimiento, ciudad, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO usuarios (nombre, apellido, email, username, password, telefono, fecha_nacimiento, ciudad, fecha_registro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ''', (nombre, apellido, email, username, password, telefono, fecha_nacimiento, ciudad))
        conn.commit()
        print(f"Usuario '{username}' insertado correctamente.")
    except sqlite3.IntegrityError as e:
        print(f"No se pudo insertar el usuario: {e}")
    finally:
        conn.close()

def borrar_usuario(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE username = ?", (username,))
    conn.commit()
    print(f"Usuario '{username}' borrado correctamente.")
    conn.close()

if __name__ == "__main__":
    print("--- TEST: Buscar usuario existente (rare) ---")
    usuario = buscar_usuario("rare")
    if usuario:
        print("Usuario encontrado:")
        for campo in usuario.keys():
            print(f"  {campo}: {usuario[campo]}")
    else:
        print("Usuario no encontrado")

    print("\n--- TEST: Mostrar rutas de usuario (rare) ---")
    print(rutas_de_usuario("rare"))

    print("\n--- TEST: Mostrar amigos de usuario (rare) ---")
    print(amigos_de_usuario("rare"))

    print("\n--- TEST: Insertar usuario nuevo (testuser) ---")
    insertar_usuario(
        nombre="Test",
        apellido="User",
        email="testuser@example.com",
        username="testuser",
        telefono="600000000",
        fecha_nacimiento="2000-01-01",
        ciudad="TestCity",
        password="testpass"
    )

    print("\n--- TEST: Comprobar que testuser aparece ---")
    usuario = buscar_usuario("testuser")
    if usuario:
        print("Usuario testuser encontrado:")
        for campo in usuario.keys():
            print(f"  {campo}: {usuario[campo]}")
    else:
        print("Usuario testuser NO encontrado")

    print("\n--- TEST: Borrar usuario testuser ---")
    borrar_usuario("testuser")

    print("\n--- TEST: Comprobar que testuser ya NO aparece ---")
    usuario = buscar_usuario("testuser")
    if usuario:
        print("ERROR: testuser sigue en la base de datos")
    else:
        print("OK: testuser ya no está en la base de datos") 