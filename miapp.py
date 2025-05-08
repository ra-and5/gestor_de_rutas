# app.py
# -*- coding: utf-8 -*-

"""
Aplicación Flask para la gestión de rutas geográficas.

Este módulo implementa una API RESTful para gestionar rutas geográficas,
usuarios y servicios relacionados como el clima. 
"""

from flask import Flask, jsonify, request, send_from_directory
from gestor_rutas import GestorRutas
from usuario_db import Usuario
from ruta_manual import RutaManual
from ruta_auto import RutaAuto
import os

# Importación condicional del servicio de clima
try:
    from servicio_clima import ServicioOpenWeatherMap as ServicioClima
    servicio_clima_disponible = True
except ImportError:
    servicio_clima_disponible = False

app = Flask(__name__, static_folder='static')
gestor = GestorRutas()

# Configuración de CORS para permitir peticiones desde cualquier origen
@app.after_request
def after_request(response):
    """
    Configura los encabezados CORS para permitir peticiones desde cualquier origen.
    
    Parameters
    ----------
    response : Response
        Objeto de respuesta Flask.
    
    Returns
    -------
    Response
        Objeto de respuesta modificado con los encabezados CORS.
    """
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Ruta principal
@app.route('/')
def home():
    """
    Ruta principal que verifica que la API está funcionando.
    
    Returns
    -------
    Response
        Respuesta JSON con información sobre el estado de la API.
    """
    return jsonify({
        "status": "success",
        "message": "API funcionando correctamente",
        "version": "1.0.0"
    })

# Endpoints estáticos
@app.route('/static/<path:filename>')
def serve_static(filename):
    """
    Sirve archivos estáticos (HTML, PDF, GPX, PNG).
    
    Parameters
    ----------
    filename : str
        Nombre del archivo a servir.
    
    Returns
    -------
    Response
        Archivo estático solicitado.
    """
    return send_from_directory('static', filename)

# Endpoints de Usuarios
@app.route('/api/usuarios/login', methods=['POST'])
def login():
    """
    Endpoint para iniciar sesión.
    
    Requiere un JSON con username y password.
    
    Returns
    -------
    Response
        Datos del usuario o mensaje de error.
    """
    try:
        datos = request.json
        usuario = Usuario.iniciar_sesion(datos['username'], datos['password'])
        
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
            "message": str(e)
        }), 500

@app.route('/api/usuarios/registro', methods=['POST'])
def registro():
    """
    Endpoint para registrar un nuevo usuario.
    
    Requiere un JSON con los datos del usuario.
    
    Returns
    -------
    Response
        Mensaje de éxito o error.
    """
    try:
        datos = request.json
        if Usuario.registrar_usuario(
            nombre=datos['nombre'],
            apellido=datos['apellido'],
            email=datos['email'],
            username=datos['username'],
            telefono=datos['telefono'],
            fecha_nacimiento=datos['fecha_nacimiento'],
            ciudad=datos['ciudad'],
            password=datos['password']
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
            "message": str(e)
        }), 500

@app.route('/api/usuarios/amigos', methods=['GET'])
def obtener_amigos():
    """
    Endpoint para obtener las relaciones de amistad entre usuarios.
    
    La amistad se determina por rutas en común.
    
    Returns
    -------
    Response
        Diccionario de relaciones de amistad.
    """
    try:
        username = request.args.get('username')
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
            "message": str(e)
        }), 500

@app.route('/api/usuarios/<username>/rutas', methods=['GET'])
def obtener_rutas_usuario(username):
    """
    Endpoint para obtener las rutas asociadas a un usuario específico.
    
    Parameters
    ----------
    username : str
        Nombre de usuario.
    
    Returns
    -------
    Response
        Lista de rutas del usuario.
    """
    try:
        rutas = Usuario.obtener_rutas(username)
        return jsonify({
            "status": "success",
            "data": rutas
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Endpoints de Rutas
@app.route('/api/rutas', methods=['GET'])
def obtener_rutas():
    """
    Endpoint para obtener todas las rutas disponibles.
    
    Returns
    -------
    Response
        Lista de todas las rutas.
    """
    try:
        # Correción: utilizamos cargar_rutas_desde_carpeta en lugar de obtener_rutas
        rutas = gestor.cargar_rutas_desde_carpeta()
        return jsonify({
            "status": "success",
            "data": rutas
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/rutas/filtrar', methods=['GET'])
def filtrar_rutas():
    """
    Endpoint para filtrar rutas según diversos criterios.
    
    Parámetros de filtrado (query):
    - dificultad: bajo, medio, alto
    - max_km: distancia máxima en kilómetros
    - max_horas: duración máxima en horas
    - modo_transporte: walk, bike, drive
    
    Returns
    -------
    Response
        Lista de rutas filtradas.
    """
    try:
        dificultad = request.args.get('dificultad')
        max_km = request.args.get('max_km', type=float)
        max_horas = request.args.get('max_horas', type=float)
        modo_transporte = request.args.get('modo_transporte')

        # Recargamos las rutas para asegurar que estamos trabajando con los datos más recientes
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
            "message": str(e)
        }), 500

@app.route('/api/rutas', methods=['POST'])
def crear_ruta():
    """
    Endpoint para crear una ruta manual.
    
    Requiere un JSON con los datos de la ruta.
    
    Returns
    -------
    Response
        Datos de la ruta creada.
    """
    try:
        datos = request.json
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
            "message": str(e)
        }), 500

@app.route('/api/rutas/auto', methods=['POST'])
def crear_rutas_automaticas():
    """
    Endpoint para crear rutas automáticas.
    
    Requiere un JSON con las direcciones y opciones.
    
    Returns
    -------
    Response
        Lista de rutas creadas.
    """
    try:
        datos = request.json
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
            "message": str(e)
        }), 500

# Endpoint de Clima
@app.route('/api/clima', methods=['GET'])
def consultar_clima():
    """
    Endpoint para consultar el clima de una ciudad.
    
    Requiere el parámetro de consulta 'ciudad'.
    
    Returns
    -------
    Response
        Datos del clima para la ciudad especificada.
    """
    try:
        if not servicio_clima_disponible:
            return jsonify({
                "status": "error",
                "message": "Servicio de clima no disponible"
            }), 503

        ciudad = request.args.get('ciudad')
        if not ciudad:
            return jsonify({
                "status": "error",
                "message": "Se requiere el parámetro 'ciudad'"
            }), 400

        servicio = ServicioClima()
        clima = servicio.obtener_clima(ciudad)
        return jsonify({
            "status": "success",
            "data": clima
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Punto de entrada para ejecución local
if __name__ == '__main__':
    # Asegurar que existan los directorios necesarios
    for directory in ['static', 'rutas']:
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    # Iniciar el servidor Flask
    app.run(debug=True, port=5000)