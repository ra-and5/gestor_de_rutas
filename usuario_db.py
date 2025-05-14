import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json
import os

class Usuario:
    def __init__(self, nombre: str, apellido: str, email: str, username: str, telefono: str, 
                 fecha_nacimiento: str, ciudad: str, password: str, fecha_registro: Optional[str] = None) -> None:
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.username = username
        self.telefono = telefono
        self.fecha_nacimiento = fecha_nacimiento
        self.ciudad = ciudad
        self.password = password
        self.fecha_registro = fecha_registro or datetime.now().isoformat()

    @staticmethod
    def get_db_connection():
        """Obtiene una conexión a la base de datos SQLite."""
        conn = sqlite3.connect('usuarios.db')
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def registrar_usuario(nombre: str, apellido: str, email: str, username: str, telefono: str, 
                         fecha_nacimiento: str, ciudad: str, password: str) -> bool:
        """Registra un nuevo usuario en la base de datos."""
        try:
            conn = Usuario.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO usuarios (nombre, apellido, email, username, telefono, 
                                fecha_nacimiento, ciudad, password, fecha_registro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nombre, apellido, email, username, telefono, fecha_nacimiento, 
                  ciudad, password, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    @staticmethod
    def iniciar_sesion(username: str, password: str) -> Optional['Usuario']:
        """Inicia sesión verificando las credenciales en la base de datos."""
        try:
            conn = Usuario.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM usuarios WHERE username = ? AND password = ?
            ''', (username, password))
            
            usuario_data = cursor.fetchone()
            conn.close()
            
            if usuario_data:
                return Usuario(
                    nombre=usuario_data['nombre'],
                    apellido=usuario_data['apellido'],
                    email=usuario_data['email'],
                    username=usuario_data['username'],
                    telefono=usuario_data['telefono'],
                    fecha_nacimiento=usuario_data['fecha_nacimiento'],
                    ciudad=usuario_data['ciudad'],
                    password=usuario_data['password'],
                    fecha_registro=usuario_data['fecha_registro']
                )
            return None
        except Exception as e:
            print(f"Error al iniciar sesión: {e}")
            return None

    @staticmethod
    def obtener_rutas(username: str) -> List[Dict]:
        """Obtiene todas las rutas asociadas a un usuario."""
        try:
            conn = Usuario.get_db_connection()
            cursor = conn.cursor()
            
            # Obtener el ID del usuario
            cursor.execute('SELECT id FROM usuarios WHERE username = ?', (username,))
            usuario = cursor.fetchone()
            
            if not usuario:
                return []
            
            # Obtener las rutas del usuario
            cursor.execute('''
                SELECT r.* 
                FROM rutas r
                JOIN usuario_rutas ur ON r.nombre = ur.nombre_ruta
                WHERE ur.usuario_id = ?
            ''', (usuario['id'],))
            
            rutas = []
            for ruta in cursor.fetchall():
                ruta_dict = {
                    'nombre': ruta['nombre'],
                    'origen': json.loads(ruta['origen']),
                    'destino': json.loads(ruta['destino']),
                    'puntos_intermedios': json.loads(ruta['puntos_intermedios']),
                    'modo': ruta['modo'],
                    'distancia_km': ruta['distancia_km'],
                    'duracion_horas': ruta['duracion_horas'],
                    'dificultad': ruta['dificultad'],
                    'created_at': ruta['created_at']
                }
                rutas.append(ruta_dict)
            
            conn.close()
            return rutas
        except Exception as e:
            print(f"Error al obtener rutas: {e}")
            return []

    @staticmethod
    def agregar_ruta(username: str, nombre_ruta: str, datos_ruta: Dict) -> bool:
        """Agrega una nueva ruta y la asocia al usuario."""
        try:
            conn = Usuario.get_db_connection()
            cursor = conn.cursor()
            
            # Obtener ID del usuario
            cursor.execute('SELECT id FROM usuarios WHERE username = ?', (username,))
            usuario = cursor.fetchone()
            if not usuario:
                return False
            
            # Insertar la ruta
            cursor.execute('''
                INSERT OR REPLACE INTO rutas (
                    nombre, origen, destino, puntos_intermedios,
                    modo, distancia_km, duracion_horas, dificultad,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                nombre_ruta,
                json.dumps(datos_ruta.get('origen', {})),
                json.dumps(datos_ruta.get('destino', {})),
                json.dumps(datos_ruta.get('puntos_intermedios', [])),
                datos_ruta.get('modo', 'walk'),
                float(datos_ruta.get('distancia', 0)),
                float(datos_ruta.get('duracion', 0)),
                datos_ruta.get('dificultad', 'media'),
                datetime.now().isoformat()
            ))
            
            # Asociar la ruta al usuario
            cursor.execute('''
                INSERT OR REPLACE INTO usuario_rutas (
                    usuario_id, nombre_ruta, created_at
                ) VALUES (?, ?, ?)
            ''', (
                usuario['id'],
                nombre_ruta,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error al agregar ruta: {e}")
            return False

    @staticmethod
    def obtener_amigos(username: str) -> Dict[str, List[str]]:
        """Obtiene los amigos del usuario basado en rutas compartidas."""
        try:
            conn = Usuario.get_db_connection()
            cursor = conn.cursor()
            
            # Obtener el ID del usuario
            cursor.execute('SELECT id FROM usuarios WHERE username = ?', (username,))
            usuario = cursor.fetchone()
            if not usuario:
                return {}
            
            # Obtener amigos basados en rutas compartidas
            cursor.execute('''
                SELECT u.username, GROUP_CONCAT(r.nombre) as rutas_comunes
                FROM usuarios u
                JOIN usuario_rutas ur1 ON ur1.usuario_id = u.id
                JOIN usuario_rutas ur2 ON ur2.nombre_ruta = ur1.nombre_ruta
                JOIN usuarios u2 ON ur2.usuario_id = u2.id
                JOIN rutas r ON r.nombre = ur1.nombre_ruta
                WHERE u2.username = ? AND u.username != ?
                GROUP BY u.username
            ''', (username, username))
            
            amigos = {}
            for row in cursor.fetchall():
                rutas = row['rutas_comunes'].split(',') if row['rutas_comunes'] else []
                amigos[row['username']] = rutas
            
            conn.close()
            return amigos
        except Exception as e:
            print(f"Error al obtener amigos: {e}")
            return {}

    @staticmethod
    def eliminar_ruta(username: str, nombre_ruta: str) -> bool:
        """Elimina una ruta asociada a un usuario."""
        try:
            conn = Usuario.get_db_connection()
            cursor = conn.cursor()
            
            # Obtener el ID del usuario
            cursor.execute('SELECT id FROM usuarios WHERE username = ?', (username,))
            usuario = cursor.fetchone()
            if not usuario:
                return False
            
            # Eliminar la relación usuario-ruta
            cursor.execute('''
                DELETE FROM usuario_rutas 
                WHERE usuario_id = ? AND nombre_ruta = ?
            ''', (usuario['id'], nombre_ruta))
            
            # Verificar si otros usuarios tienen esta ruta
            cursor.execute('''
                SELECT COUNT(*) FROM usuario_rutas 
                WHERE nombre_ruta = ?
            ''', (nombre_ruta,))
            
            count = cursor.fetchone()[0]
            
            # Si ningún usuario tiene esta ruta, eliminar la ruta
            if count == 0:
                cursor.execute('DELETE FROM rutas WHERE nombre = ?', (nombre_ruta,))
                
                # Eliminar archivos asociados
                for ext in ['.json', '.pdf', '.html', '.gpx']:
                    file_path = os.path.join('rutas', f"{nombre_ruta}{ext}")
                    if os.path.exists(file_path):
                        os.remove(file_path)
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error al eliminar ruta: {e}")
            return False 
        
    @staticmethod
    def guardar_usuario(usuario):
        conn = Usuario.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO usuarios (
                nombre, apellido, email, username, password_hash,
                telefono, fecha_nacimiento, ciudad, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            usuario.nombre,
            usuario.apellido,
            usuario.email,
            usuario.username,
            usuario.password,  # o usuario.password_hash según tu modelo
            usuario.telefono,
            usuario.fecha_nacimiento,
            usuario.ciudad,
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()