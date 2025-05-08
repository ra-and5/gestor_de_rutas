from app_instance import app
from flask import request, jsonify
from run import clima_gestor  # importar la instancia desde run.py

# Obtener clima actual
@app.route("/api/clima", methods=["GET"])
def obtener_clima():
    """
    Endpoint para obtener el clima actual de una ciudad.

    Este endpoint recibe el nombre de la ciudad como parámetro de consulta
    y devuelve los detalles del clima de esa ciudad, incluyendo temperatura,
    humedad, descripción del clima, velocidad del viento y la fecha en que se
    obtuvo la información.

    Parameters
    ----------
    ciudad : str
        Nombre de la ciudad para la cual se desea obtener la información del clima.

    Returns
    -------
    dict
        Un diccionario JSON con los detalles del clima de la ciudad solicitada,
        incluyendo:
            - ciudad: nombre de la ciudad.
            - temperatura: temperatura en grados Celsius.
            - humedad: porcentaje de humedad.
            - descripcion: descripción del clima.
            - viento: velocidad del viento en m/s.
            - fecha: fecha y hora en formato ISO.
    -------
    500
        Si ocurre un error durante la obtención de la información del clima, se
        devuelve un error 500 con el mensaje de error.
    """
    ciudad = request.args.get("ciudad")
    try:
        # Obtener los datos del clima de la ciudad usando el objeto clima_gestor
        clima = clima_gestor.consultar_clima(ciudad)
        
        # Devolver los datos del clima en formato JSON
        return jsonify({
            "ciudad": clima.ciudad,
            "temperatura": clima.temperatura,
            "humedad": clima.humedad,
            "descripcion": clima.descripcion,
            "viento": clima.viento,
            "fecha": clima.fecha.isoformat()
        })
    
    except Exception as e:
        # En caso de error, devolver el mensaje de error con código 500
        return jsonify({"error": str(e)}), 500
