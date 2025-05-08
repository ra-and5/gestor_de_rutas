from flask import request, jsonify, send_from_directory
from app_instance import app
from ruta_manual import RutaManual
from ruta_auto import RutaAuto
from usuario import Usuario
from ruta import Ruta
from gestor_rutas import GestorRutas
import os
import json

# Crear ruta manual
@app.route("/api/ruta_manual", methods=["POST"])
def crear_manual():
    """
    Crea una ruta manual a partir de los datos proporcionados por el usuario.

    Recibe los datos de la ruta, incluidos el origen, los puntos intermedios, el destino,
    el modo de transporte y el nombre de la ruta. Si la creación es exitosa, devuelve los enlaces
    a los archivos PDF, GPX y HTML generados. Si ocurre algún error, se retorna un mensaje de error.

    Parameters
    ----------
    None

    Returns
    -------
    Response
        Retorna un JSON con el mensaje de éxito y los archivos generados, o un mensaje de error.
    """
    data = request.json
    usuario = Usuario.iniciar_sesion(data["username"], data["password"])
    if not usuario:
        return jsonify({"error": "Credenciales inválidas"}), 403
    try:
        pdf, gpx, html = RutaManual.crear_ruta_desde_datos(
            data["origen"], data["intermedios"], data["destino"],
            data["modo"], data.get("nombre"), usuario
        )
        return jsonify({"mensaje": "Ruta creada", "pdf": pdf, "gpx": gpx, "html": html})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Crear rutas automáticas
@app.route("/api/ruta_auto", methods=["POST"])
def crear_auto():
    """
    Crea rutas automáticas basadas en un conjunto de direcciones proporcionadas por el usuario.

    Recibe un conjunto de direcciones y una cantidad de rutas a generar. Si la creación es exitosa,
    devuelve un JSON con los enlaces a las rutas generadas. En caso de error, se retorna un mensaje de error.

    Parameters
    ----------
    None

    Returns
    -------
    Response
        Retorna un JSON con el mensaje de éxito y las rutas generadas, o un mensaje de error.
    """
    data = request.json
    usuario = Usuario.iniciar_sesion(data["username"], data["password"])
    if not usuario:
        return jsonify({"error": "Credenciales inválidas"}), 403
    try:
        generador = RutaAuto()
        resultado = generador.generar_rutas_desde_direcciones(data["direcciones"], int(data["cantidad"]))
        return jsonify({"mensaje": "Rutas automáticas generadas", "rutas": resultado})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/rutas", methods=["GET"])
def obtener_rutas_filtradas():
    """
    Obtiene rutas filtradas según los parámetros proporcionados por el usuario.

    Este endpoint recibe varios parámetros de filtro, como la dificultad, la distancia máxima,
    la duración máxima y el modo de transporte. Retorna un JSON con las rutas que cumplen con los filtros,
    o un mensaje de error si ocurre algún problema al aplicar los filtros.

    Parameters
    ----------
    dificultad : str, opcional
        La dificultad de las rutas a filtrar (bajo, medio, alto).
    max_km : float, opcional
        La distancia máxima de las rutas a filtrar.
    max_horas : float, opcional
        La duración máxima de las rutas a filtrar.
    transporte : str, opcional
        El medio de transporte a filtrar (walk, bike, drive).

    Returns
    -------
    Response
        Retorna un JSON con las rutas filtradas, o un mensaje de error si ocurre un problema.
    """
    gestor = GestorRutas()
    rutas_filtradas = gestor.rutas

    # Aplicar filtros individualmente
    dificultad = request.args.get("dificultad")
    if dificultad:
        rutas_filtradas = gestor.filtrar_por_dificultad(dificultad)

    max_km = request.args.get("max_km")
    if max_km:
        rutas_filtradas = [r for r in rutas_filtradas if r in gestor.filtrar_por_distancia(float(max_km))]

    max_horas = request.args.get("max_horas")
    if max_horas:
        rutas_filtradas = [r for r in rutas_filtradas if r in gestor.filtrar_por_duracion(float(max_horas))]

    transporte = request.args.get("transporte")
    if transporte:
        try:
            rutas_filtradas = [r for r in rutas_filtradas if r in gestor.filtrar_por_transporte(transporte)]
        except ValueError:
            return jsonify({"error": "Modo de transporte no válido"}), 400

    return jsonify({"rutas": rutas_filtradas})


# Descargar PDF de ruta
@app.route("/api/rutas/<nombre>/pdf", methods=["GET"])
def descargar_pdf(nombre):
    """
    Permite descargar el archivo PDF de la ruta especificada por nombre.

    Recibe el nombre de la ruta y busca el archivo PDF correspondiente en el directorio estático.
    Si el archivo existe, se envía como respuesta, de lo contrario se muestra un error.

    Parameters
    ----------
    nombre : str
        El nombre de la ruta para la que se desea descargar el archivo PDF.

    Returns
    -------
    Response
        Retorna el archivo PDF correspondiente a la ruta, o un mensaje de error si no se encuentra el archivo.
    """
    path = f"{nombre}.pdf"
    return send_from_directory("static", path, as_attachment=True)

# Descargar HTML de ruta
@app.route("/api/rutas/<nombre>/html", methods=["GET"])
def descargar_html(nombre):
    """
    Permite descargar el archivo HTML de la ruta especificada por nombre.

    Recibe el nombre de la ruta y busca el archivo HTML correspondiente en el directorio estático.
    Si el archivo existe, se envía como respuesta, de lo contrario se muestra un error.

    Parameters
    ----------
    nombre : str
        El nombre de la ruta para la que se desea descargar el archivo HTML.

    Returns
    -------
    Response
        Retorna el archivo HTML correspondiente a la ruta, o un mensaje de error si no se encuentra el archivo.
    """
    path = f"rutas_{nombre}.html"
    return send_from_directory("static", path, as_attachment=True)
