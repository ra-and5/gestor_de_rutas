import json
import sqlite3
from datetime import datetime

def crear_tablas():
    conn = sqlite3.connect('miapp.db')
    cursor = conn.cursor()
    
    # Eliminar tablas existentes si existen
    cursor.execute('DROP TABLE IF EXISTS amistades')
    cursor.execute('DROP TABLE IF EXISTS rutas')
    cursor.execute('DROP TABLE IF EXISTS usuarios')
    
    # Crear tabla de usuarios
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        telefono TEXT NOT NULL,
        fecha_nacimiento TEXT NOT NULL,
        ciudad TEXT NOT NULL,
        fecha_registro TEXT NOT NULL
    )
    ''')
    
    # Crear tabla de rutas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rutas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL,
        descripcion TEXT,
        distancia REAL,
        duracion INTEGER,
        dificultad TEXT,
        puntos_interes TEXT,
        origen TEXT,
        destino TEXT,
        modo_transporte TEXT,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Crear tabla de amistades
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS amistades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        amigo_id INTEGER NOT NULL,
        fecha_amistad TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
        FOREIGN KEY (amigo_id) REFERENCES usuarios (id),
        UNIQUE(usuario_id, amigo_id)
    )
    ''')
    
    # Crear tabla de rutas de usuario (relación muchos a muchos)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rutas_usuario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        ruta_id INTEGER NOT NULL,
        fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
        FOREIGN KEY (ruta_id) REFERENCES rutas (id),
        UNIQUE(usuario_id, ruta_id)
    )
    ''')
    
    conn.commit()
    return conn

def migrar_datos():
    try:
        # Leer el archivo JSON
        with open('usuarios.json', 'r', encoding='utf-8') as f:
            usuarios = json.load(f)
        
        conn = crear_tablas()
        cursor = conn.cursor()
        
        # Diccionario para mapear usernames a IDs
        username_to_id = {}
        
        # Migrar usuarios
        for usuario in usuarios:
            try:
                # Obtener valores con valores por defecto
                nombre = usuario.get('nombre', '')
                apellido = usuario.get('apellido', '')
                email = usuario.get('email', '')
                username = usuario.get('username', '')
                password = usuario.get('password', '')
                telefono = usuario.get('telefono', '')
                fecha_nacimiento = usuario.get('fecha_nacimiento', datetime.now().isoformat())
                ciudad = usuario.get('ciudad', '')
                fecha_registro = usuario.get('fecha_registro') or datetime.now().isoformat()
                
                cursor.execute('''
                INSERT INTO usuarios (
                    nombre, apellido, email, username, password, telefono,
                    fecha_nacimiento, ciudad, fecha_registro
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    nombre,
                    apellido,
                    email,
                    username,
                    password,
                    telefono,
                    fecha_nacimiento,
                    ciudad,
                    fecha_registro
                ))
                
                # Guardar el ID del usuario
                user_id = cursor.lastrowid
                username_to_id[username] = user_id
                
                # Migrar rutas del usuario
                rutas = usuario.get('rutas', [])
                for ruta_nombre in rutas:
                    try:
                        # Verificar si la ruta ya existe
                        cursor.execute('SELECT id FROM rutas WHERE nombre = ?', (ruta_nombre,))
                        ruta_existente = cursor.fetchone()
                        
                        if not ruta_existente:
                            # Crear la ruta si no existe
                            cursor.execute('''
                            INSERT INTO rutas (
                                nombre, descripcion, distancia, duracion,
                                dificultad, puntos_interes, origen, destino, modo_transporte
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                ruta_nombre,
                                f"Descripción de {ruta_nombre}",
                                0.0,  # distancia por defecto
                                0,    # duración por defecto
                                'media',  # dificultad por defecto
                                json.dumps([]),  # puntos de interés vacíos
                                'Origen',  # origen por defecto
                                'Destino',  # destino por defecto
                                'walk'  # modo de transporte por defecto
                            ))
                            ruta_id = cursor.lastrowid
                        else:
                            ruta_id = ruta_existente[0]
                        
                        # Asignar la ruta al usuario
                        cursor.execute('''
                        INSERT OR IGNORE INTO rutas_usuario (usuario_id, ruta_id)
                        VALUES (?, ?)
                        ''', (user_id, ruta_id))
                        
                    except sqlite3.IntegrityError as e:
                        print(f"Error al insertar ruta {ruta_nombre}: {e}")
                
                print(f"Usuario {username} migrado exitosamente")
                
            except sqlite3.IntegrityError as e:
                print(f"Error al insertar usuario {username}: {e}")
            except Exception as e:
                print(f"Error inesperado con usuario {username}: {e}")
        
        # Migrar amistades
        for usuario in usuarios:
            username = usuario.get('username')
            if username in username_to_id:
                user_id = username_to_id[username]
                amigos = usuario.get('amigos', [])
                
                for amigo_username in amigos:
                    if amigo_username in username_to_id:
                        amigo_id = username_to_id[amigo_username]
                        try:
                            cursor.execute('''
                            INSERT OR IGNORE INTO amistades (usuario_id, amigo_id)
                            VALUES (?, ?)
                            ''', (user_id, amigo_id))
                        except sqlite3.IntegrityError as e:
                            print(f"Error al insertar amistad entre {username} y {amigo_username}: {e}")
        
        conn.commit()
        conn.close()
        print("Migración completada exitosamente!")
        
    except Exception as e:
        print(f"Error general durante la migración: {e}")

if __name__ == "__main__":
    migrar_datos() 