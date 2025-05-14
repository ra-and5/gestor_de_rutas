"""
Aplicación Flask para la gestión de rutas geográficas - Versión PythonAnywhere.

Este módulo implementa una API RESTful para gestionar rutas geográficas,
usuarios y servicios relacionados como el clima. Adaptado para despliegue en PythonAnywhere.
"""

from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import datetime
import sqlite3
import requests
from flask_cors import CORS

# Configuración de rutas 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'usuarios.db')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
RUTAS_DIR = os.path.join(BASE_DIR, 'rutas')

# Crear directorios necesarios si no existen
for directory in [STATIC_DIR, RUTAS_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Inicialización de la aplicación Flask
app = Flask(__name__, static_folder=STATIC_DIR)
CORS(app)  # Habilitar CORS para todas las rutas

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'connect_args': {'timeout': 30}
}
db = SQLAlchemy(app)

# Modelos de base de datos
class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    telefono = db.Column(db.String(20))
    fecha_nacimiento = db.Column(db.String(20))
    ciudad = db.Column(db.String(100))

    def __repr__(self):
        return f'<Usuario {self.username}>'

    @staticmethod
    def iniciar_sesion(username, password):
        usuario = Usuario.query.filter_by(username=username).first()
        if usuario and usuario.password_hash == password:
            return usuario
        return None

    @staticmethod
    def registrar_usuario(nombre, apellido, email, username, password, telefono=None, fecha_nacimiento=None, ciudad=None):
        if Usuario.query.filter_by(username=username).first() or Usuario.query.filter_by(email=email).first():
            return False

        nuevo_usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            email=email,
            username=username,
            password_hash=password,
            telefono=telefono,
            fecha_nacimiento=fecha_nacimiento,
            ciudad=ciudad
        )

        db.session.add(nuevo_usuario)
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

    @staticmethod
    def obtener_rutas(username):
        usuario = Usuario.query.filter_by(username=username).first()
        if not usuario:
            return []

        rutas = UsuarioRuta.query.filter_by(usuario_id=usuario.id).all()
        nombres_rutas = [ur.nombre_ruta for ur in rutas]

        resultado = []
        for nombre_ruta in nombres_rutas:
            ruta_path = os.path.join(RUTAS_DIR, f"{nombre_ruta}.json")
            if os.path.exists(ruta_path):
                try:
                    with open(ruta_path, 'r', encoding='utf-8') as f:
                        datos_ruta = json.load(f)
                        # Adaptar origen y destino si son string
                        if isinstance(datos_ruta.get('origen'), str):
                            datos_ruta['origen'] = {"direccion": datos_ruta['origen']}
                        if isinstance(datos_ruta.get('destino'), str):
                            datos_ruta['destino'] = {"direccion": datos_ruta['destino']}
                        # Adaptar puntos_intermedios si es lista de strings
                        if 'puntos_intermedios' in datos_ruta and isinstance(datos_ruta['puntos_intermedios'], list):
                            if datos_ruta['puntos_intermedios'] and isinstance(datos_ruta['puntos_intermedios'][0], str):
                                datos_ruta['puntos_intermedios'] = [{"direccion": p} for p in datos_ruta['puntos_intermedios']]
                        resultado.append(datos_ruta)
                except Exception as e:
                    print(f"Error al cargar la ruta {nombre_ruta}: {str(e)}")

        return resultado

    @staticmethod
    def agregar_ruta(username, nombre_ruta):
        usuario = Usuario.query.filter_by(username=username).first()
        if not usuario:
            return False

        relacion = UsuarioRuta.query.filter_by(usuario_id=usuario.id, nombre_ruta=nombre_ruta).first()
        if relacion:
            return True

        nueva_relacion = UsuarioRuta(
            usuario_id=usuario.id,
            nombre_ruta=nombre_ruta,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        db.session.add(nueva_relacion)
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

    @staticmethod
    def obtener_amigos(username):
        usuario = Usuario.query.filter_by(username=username).first()
        if not usuario:
            return {}

        rutas_usuario = UsuarioRuta.query.filter_by(usuario_id=usuario.id).all()
        nombres_rutas = [ur.nombre_ruta for ur in rutas_usuario]

        amigos = {}
        for nombre_ruta in nombres_rutas:
            relaciones = UsuarioRuta.query.filter_by(nombre_ruta=nombre_ruta).all()
            for rel in relaciones:
                if rel.usuario_id != usuario.id:
                    amigo = Usuario.query.get(rel.usuario_id)
                    if amigo:
                        if amigo.username not in amigos:
                            amigos[amigo.username] = {
                                "nombre": amigo.nombre,
                                "apellido": amigo.apellido,
                                "rutas_comunes": []
                            }
                        amigos[amigo.username]["rutas_comunes"].append(nombre_ruta)

        return amigos

class UsuarioRuta(db.Model):
    __tablename__ = 'usuario_rutas'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    nombre_ruta = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<UsuarioRuta {self.usuario_id}:{self.nombre_ruta}>'

class GestorRutas:
    def __init__(self):
        self.rutas = []
        self.rutas_dir = RUTAS_DIR

    def cargar_rutas_desde_carpeta(self):
        rutas = []
        if os.path.exists(self.rutas_dir):
            for archivo in os.listdir(self.rutas_dir):
                if archivo.endswith('.json'):
                    ruta_path = os.path.join(self.rutas_dir, archivo)
                    try:
                        with open(ruta_path, 'r', encoding='utf-8') as f:
                            datos_ruta = json.load(f)
                            rutas.append(datos_ruta)
                    except Exception as e:
                        print(f"Error al cargar la ruta {archivo}: {str(e)}")

        self.rutas = rutas
        return rutas

    def filtrar_por_dificultad(self, dificultad):
        return [ruta for ruta in self.rutas if ruta.get('dificultad', '').lower() == dificultad.lower()]

    def filtrar_por_distancia(self, max_km):
        return [ruta for ruta in self.rutas if float(ruta.get('distancia_km', 0)) <= max_km]

    def filtrar_por_duracion(self, max_horas):
        return [ruta for ruta in self.rutas if float(ruta.get('duracion_horas', 0)) <= max_horas]

    def filtrar_por_transporte(self, modo):
        return [ruta for ruta in self.rutas if ruta.get('modo', '').lower() == modo.lower()]

class RutaManual:
    @staticmethod
    def crear_ruta_desde_datos(origen, destino, modo='walk', nombre=None, puntos_intermedios=None, username=None):
        if not puntos_intermedios:
            puntos_intermedios = []

        if not nombre:
            ahora = datetime.now().strftime("%Y%m%d%H%M%S")
            nombre = f"Ruta_{ahora}"

        distancia_km = 10.0  # Valor de ejemplo
        velocidades = {'walk': 5, 'bike': 15, 'drive': 60}  # km/h
        duracion_horas = distancia_km / velocidades.get(modo, 5)

        if distancia_km < 5:
            dificultad = 'bajo'
        elif distancia_km < 15:
            dificultad = 'medio'
        else:
            dificultad = 'alto'

        ruta = {
            'nombre': nombre,
            'origen': origen,
            'destino': destino,
            'puntos_intermedios': puntos_intermedios,
            'modo': modo,
            'distancia_km': distancia_km,
            'duracion_horas': duracion_horas,
            'dificultad': dificultad,
            'fecha_creacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'creador': username
        }

        ruta_path = os.path.join(RUTAS_DIR, f"{nombre}.json")
        with open(ruta_path, 'w', encoding='utf-8') as f:
            json.dump(ruta, f, ensure_ascii=False, indent=4)

        return ruta

class RutaAuto:
    def generar_rutas_desde_direcciones(self, direcciones, cantidad=5):
        if not direcciones or len(direcciones) < 2:
            return ["Se requieren al menos dos direcciones"]

        rutas_generadas = []

        for i in range(min(cantidad, len(direcciones) - 1)):
            origen = {'lat': 0, 'lng': 0, 'direccion': direcciones[i]}
            destino = {'lat': 0, 'lng': 0, 'direccion': direcciones[i+1]}

            ahora = datetime.now().strftime("%Y%m%d%H%M%S")
            nombre = f"RutaAuto_{ahora}_{i}"

            ruta = RutaManual.crear_ruta_desde_datos(
                origen=origen,
                destino=destino,
                modo='walk',
                nombre=nombre
            )

            rutas_generadas.append(f"Ruta '{nombre}' creada exitosamente")

        return rutas_generadas

# Configuración de CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Instancia del gestor de rutas
gestor = GestorRutas()

# Ruta principal
@app.route('/')
def home():
    return jsonify({
        "status": "success",
        "message": "API funcionando correctamente en PythonAnywhere",
        "version": "1.1.0"
    })

# Endpoint para servir archivos estáticos 
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(STATIC_DIR, filename)

# Endpoint para servir archivos HTML desde la carpeta 'static'
@app.route('/html/<path:filename>')
def serve_html(filename):
    return send_from_directory(STATIC_DIR, filename)

# Endpoints de Usuarios
@app.route('/api/usuarios/login', methods=['POST'])
def login():
    try:
        datos = request.get_json(force=True)
        username = datos.get('username', '').strip()
        password = datos.get('password', '').strip()
        
        if not username or not password:
            return jsonify({
                "status": "error",
                "message": "Usuario y contraseña son obligatorios"
            }), 400
            
        usuario = Usuario.iniciar_sesion(username, password)
        if usuario:
            return jsonify({
                "status": "success",
                "data": {
                    "nombre": usuario.nombre,
                    "apellido": usuario.apellido,
                    "email": usuario.email,
                    "username": usuario.username,
                    "telefono": usuario.telefono,
                    "fecha_nacimiento": usuario.fecha_nacimiento,
                    "ciudad": usuario.ciudad
                }
            })
        return jsonify({
            "status": "error",
            "message": "Usuario o contraseña incorrectos"
        }), 401
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error en login: {str(e)}"
        }), 500

@app.route('/api/usuarios/registro', methods=['POST'])
def registro():
    try:
        datos = request.get_json(force=True)
        campos = ['nombre', 'apellido', 'email', 'username', 'password']
        for campo in campos:
            if not datos.get(campo, '').strip():
                return jsonify({
                    "status": "error",
                    "message": f"El campo '{campo}' es obligatorio"
                }), 400
                
        if Usuario.registrar_usuario(
            nombre=datos['nombre'].strip(),
            apellido=datos['apellido'].strip(),
            email=datos['email'].strip(),
            username=datos['username'].strip(),
            password=datos['password'].strip(),
            telefono=datos.get('telefono', '').strip(),
            fecha_nacimiento=datos.get('fecha_nacimiento', '').strip(),
            ciudad=datos.get('ciudad', '').strip()
        ):
            return jsonify({
                "status": "success",
                "message": "Usuario registrado exitosamente"
            })
        return jsonify({
            "status": "error",
            "message": "El usuario ya existe"
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error en registro: {str(e)}"
        }), 500

@app.route('/api/usuarios/<username>', methods=['DELETE', 'POST'])
def eliminar_usuario(username):
    try:
        if request.method == 'POST':
            datos = request.get_json(force=True)
            if not datos or datos.get('accion') != 'eliminar':
                return jsonify({
                    "status": "error",
                    "message": "Acción no permitida"
                }), 400
        usuario = Usuario.query.filter_by(username=username).first()
        if not usuario:
            return jsonify({
                "status": "error",
                "message": "Usuario no encontrado"
            }), 404
        # Eliminar todas las rutas asociadas
        rutas = UsuarioRuta.query.filter_by(usuario_id=usuario.id).all()
        for ruta in rutas:
            ruta_path = os.path.join(RUTAS_DIR, f"{ruta.nombre_ruta}.json")
            if os.path.exists(ruta_path):
                os.remove(ruta_path)
            db.session.delete(ruta)
        # Eliminar el usuario
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Usuario eliminado correctamente"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"Error al eliminar usuario: {str(e)}"
        }), 500

@app.route('/api/usuarios/editar', methods=['PUT', 'POST'])
def editar_usuario():
    try:
        datos = request.get_json(force=True)
        username = datos.get('username')
        if not username:
            return jsonify({
                "status": "error",
                "message": "Se requiere el username"
            }), 400
            
        usuario = Usuario.query.filter_by(username=username).first()
        if not usuario:
            return jsonify({
                "status": "error",
                "message": "Usuario no encontrado"
            }), 404
            
        # Actualizar campos
        campos = ['nombre', 'apellido', 'email', 'telefono', 'fecha_nacimiento', 'ciudad']
        for campo in campos:
            if campo in datos:
                setattr(usuario, campo, datos[campo].strip())
                
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": "Usuario actualizado correctamente"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"Error al actualizar usuario: {str(e)}"
        }), 500

@app.route('/api/usuarios/buscar', methods=['GET'])
def buscar_usuarios():
    try:
        nombre = request.args.get('nombre', '').strip()
        if not nombre:
            return jsonify({
                "status": "error",
                "message": "Se requiere el parámetro 'nombre'"
            }), 400
            
        usuarios = Usuario.query.filter(Usuario.username.like(f'%{nombre}%')).all()
        resultados = [usuario.username for usuario in usuarios]
        
        return jsonify({
            "status": "success",
            "resultados": resultados
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al buscar usuarios: {str(e)}"
        }), 500

@app.route('/api/usuarios/<username>/rutas/<nombre_ruta>', methods=['DELETE'])
def eliminar_ruta_usuario(username, nombre_ruta):
    try:
        usuario = Usuario.query.filter_by(username=username).first()
        if not usuario:
            return jsonify({
                "status": "error",
                "message": "Usuario no encontrado"
            }), 404
            
        relacion = UsuarioRuta.query.filter_by(
            usuario_id=usuario.id,
            nombre_ruta=nombre_ruta
        ).first()
        
        if not relacion:
            return jsonify({
                "status": "error",
                "message": "Ruta no encontrada para este usuario"
            }), 404
            
        # Eliminar archivos asociados
        ruta_path = os.path.join(RUTAS_DIR, f"{nombre_ruta}.json")
        if os.path.exists(ruta_path):
            os.remove(ruta_path)
            
        # Eliminar archivos PDF y HTML si existen
        pdf_path = os.path.join(STATIC_DIR, f"{nombre_ruta}.pdf")
        html_path = os.path.join(STATIC_DIR, f"rutas_{nombre_ruta}.html")
        
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        if os.path.exists(html_path):
            os.remove(html_path)
            
        # Eliminar la relación
        db.session.delete(relacion)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "Ruta eliminada correctamente"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"Error al eliminar ruta: {str(e)}"
        }), 500

@app.route('/api/usuarios/<username>/rutas', methods=['GET'])
def obtener_rutas_usuario(username):
    try:
        rutas = []
        usuario = Usuario.query.filter_by(username=username.strip()).first()
        if usuario:
            relaciones = UsuarioRuta.query.filter_by(usuario_id=usuario.id).all()
            for rel in relaciones:
                ruta_path = os.path.join(RUTAS_DIR, f"{rel.nombre_ruta}.json")
                if os.path.exists(ruta_path):
                    try:
                        with open(ruta_path, 'r', encoding='utf-8') as f:
                            datos_ruta = json.load(f)
                            if isinstance(datos_ruta, dict):
                                # Adaptar origen y destino si son string
                                if isinstance(datos_ruta.get('origen'), str):
                                    datos_ruta['origen'] = {"direccion": datos_ruta['origen']}
                                if isinstance(datos_ruta.get('destino'), str):
                                    datos_ruta['destino'] = {"direccion": datos_ruta['destino']}
                                # Adaptar puntos_intermedios si es lista de strings
                                if 'puntos_intermedios' in datos_ruta and isinstance(datos_ruta['puntos_intermedios'], list):
                                    if datos_ruta['puntos_intermedios'] and isinstance(datos_ruta['puntos_intermedios'][0], str):
                                        datos_ruta['puntos_intermedios'] = [{"direccion": p} for p in datos_ruta['puntos_intermedios']]
                                # Adaptar distancia y duración
                                if 'distancia' in datos_ruta and 'distancia_km' not in datos_ruta:
                                    try:
                                        datos_ruta['distancia_km'] = float(str(datos_ruta['distancia']).replace('km','').strip())
                                    except:
                                        datos_ruta['distancia_km'] = 0
                                if 'duracion' in datos_ruta and 'duracion_horas' not in datos_ruta:
                                    try:
                                        minutos = 0
                                        if 'h' in datos_ruta['duracion']:
                                            partes = datos_ruta['duracion'].split('h')
                                            horas = int(partes[0].strip())
                                            minutos = int(partes[1].replace('min','').strip()) if 'min' in partes[1] else 0
                                            datos_ruta['duracion_horas'] = horas + minutos/60
                                        else:
                                            datos_ruta['duracion_horas'] = float(str(datos_ruta['duracion']).replace('min','').strip())/60
                                    except:
                                        datos_ruta['duracion_horas'] = 0
                                # Adaptar modo
                                if 'modo_transporte' in datos_ruta and 'modo' not in datos_ruta:
                                    datos_ruta['modo'] = datos_ruta['modo_transporte']
                                rutas.append(datos_ruta)
                    except Exception as e:
                        print(f"Error al cargar la ruta {rel.nombre_ruta}: {str(e)}")
        return jsonify({"status": "success", "data": rutas})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al obtener rutas: {str(e)}"}), 500

@app.route('/api/usuarios/amigos', methods=['GET'])
def obtener_amigos():
    try:
        username = request.args.get('username', '').strip()
        if not username:
            return jsonify({
                "status": "error",
                "message": "Se requiere el parámetro username"
            }), 400
        amigos = Usuario.obtener_amigos(username)
        return jsonify({
            "status": "success",
            "data": amigos
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al obtener amigos: {str(e)}"
        }), 500

# Endpoints de Rutas
@app.route('/api/rutas', methods=['GET'])
def obtener_rutas():
    try:
        rutas = gestor.cargar_rutas_desde_carpeta()
        return jsonify({
            "status": "success",
            "data": rutas
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al obtener rutas: {str(e)}"
        }), 500

@app.route('/api/rutas/filtrar', methods=['GET'])
def filtrar_rutas():
    try:
        dificultad = request.args.get('dificultad')
        max_km = request.args.get('max_km', type=float)
        max_horas = request.args.get('max_horas', type=float)
        modo_transporte = request.args.get('modo_transporte')
        
        gestor.rutas = gestor.cargar_rutas_desde_carpeta()
        rutas = gestor.rutas
        
        if dificultad:
            rutas = gestor.filtrar_por_dificultad(dificultad)
        if max_km:
            rutas = gestor.filtrar_por_distancia(max_km)
        if max_horas:
            rutas = gestor.filtrar_por_duracion(max_horas)
        if modo_transporte:
            rutas = gestor.filtrar_por_transporte(modo_transporte)
            
        return jsonify({
            "status": "success",
            "data": rutas
        })
    except ValueError as ve:
        return jsonify({
            "status": "error",
            "message": str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al filtrar rutas: {str(e)}"
        }), 500

@app.route('/api/rutas', methods=['POST'])
def crear_ruta():
    try:
        datos = request.get_json(force=True)
        ruta = RutaManual.crear_ruta_desde_datos(
            origen=datos['origen'],
            puntos_intermedios=datos.get('puntos_intermedios', []),
            destino=datos['destino'],
            modo=datos.get('modo', 'walk'),
            nombre=datos.get('nombre'),
            username=datos.get('username')
        )
        
        if ruta and datos.get('username'):
            Usuario.agregar_ruta(datos['username'], ruta['nombre'])
            
        return jsonify({
            "status": "success",
            "data": ruta
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al crear ruta: {str(e)}"
        }), 500

@app.route('/api/rutas/auto', methods=['POST'])
def crear_rutas_automaticas():
    try:
        datos = request.get_json(force=True)
        ruta_auto = RutaAuto()
        rutas = ruta_auto.generar_rutas_desde_direcciones(
            direcciones=datos['direcciones'],
            cantidad=datos.get('cantidad', 5)
        )
        
        if rutas and datos.get('username'):
            for ruta in rutas:
                if isinstance(ruta, str) and "creada" in ruta:
                    nombre_ruta = ruta.split("'")[1]
                    Usuario.agregar_ruta(datos['username'], nombre_ruta)
                    
        return jsonify({
            "status": "success",
            "data": rutas
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al crear rutas automáticas: {str(e)}"
        }), 500

# Endpoint de Clima
@app.route('/api/clima', methods=['GET'])
def consultar_clima():
    try:
        ciudad = request.args.get('ciudad', '').strip()
        if not ciudad:
            return jsonify({
                "status": "error",
                "message": "Se requiere el parámetro 'ciudad'"
            }), 400
            
        # Simulación de datos del clima para pruebas
        clima = {
            "ciudad": ciudad,
            "temperatura": 25,
            "humedad": 60,
            "descripcion": "Soleado",
            "viento": 5,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return jsonify({
            "status": "success",
            "data": clima
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al consultar clima: {str(e)}"
        }), 500

# Endpoint para comprobar la base de datos
@app.route('/api/test_db', methods=['GET'])
def test_db():
    try:
        # Verificar si la base de datos existe
        if not os.path.exists('usuarios.db'):
            return jsonify({
                "status": "error",
                "message": "La base de datos no existe",
                "details": {
                    "database_uri": app.config['SQLALCHEMY_DATABASE_URI'],
                    "action": "Se intentará crear la base de datos"
                }
            }), 500

        # Intentar una consulta simple
        with app.app_context():
            db.session.execute('SELECT 1')
            db.session.commit()
            
            # Obtener información de las tablas
            inspector = db.inspect(db.engine)
            tablas = inspector.get_table_names()
            
            return jsonify({
                "status": "success",
                "message": "Base de datos funcionando correctamente",
                "details": {
                    "database_uri": app.config['SQLALCHEMY_DATABASE_URI'],
                    "tables": tablas,
                    "connection_status": "active"
                }
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error en la base de datos: {str(e)}",
            "details": {
                "database_uri": app.config['SQLALCHEMY_DATABASE_URI'],
                "error_type": type(e).__name__
            }
        }), 500

# Crear las tablas en la base de datos si no existen
def inicializar_db():
    """Inicializa la base de datos creando todas las tablas necesarias."""
    with app.app_context():
        try:
            # Verificar si la base de datos existe
            if not os.path.exists('usuarios.db'):
                print("📝 Creando nueva base de datos...")
            
            # Crear las tablas
            db.create_all()
            print("✅ Base de datos inicializada correctamente")
            
            # Verificar las tablas creadas
            inspector = db.inspect(db.engine)
            tablas = inspector.get_table_names()
            print(f"📊 Tablas creadas: {', '.join(tablas)}")
            
        except Exception as e:
            print(f"❌ Error al inicializar la base de datos: {str(e)}")
            raise


if __name__ == '__main__':
    inicializar_db()
    #Ejecución local (descomentar)
    #app.run(debug=True, port=5000)
else:
    inicializar_db()