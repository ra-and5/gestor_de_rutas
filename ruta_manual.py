import random
from ruta import Ruta
from utils import *
import json 
import time

class RutaManual:
    @staticmethod
    def crear_ruta_desde_datos(origen, puntos_intermedios, destino, modo, nombre=None, username=None):
        """
        Crea una ruta desde los datos proporcionados.
        
        Parameters
        ----------
        origen : str
            El origen de la ruta.
        puntos_intermedios : List[str]
            Lista de puntos intermedios en la ruta.
        destino : str
            El destino de la ruta.
        modo : str
            El modo de transporte (walk, bike, drive).
        nombre : str, optional
            El nombre de la ruta (se genera automáticamente si no se proporciona).
        username : str, optional
            El nombre de usuario que está creando la ruta.
        
        Returns
        -------
        dict
            Diccionario con la información de la ruta creada.
        """
        try:
            # Generar nombre único si no se proporciona
            if not nombre:
                nombre = f"ruta_manual_{int(time.time())}"

            # Crear objeto Ruta
            ruta = Ruta(
                nombre=nombre,
                ubicacion=(random.uniform(38.3, 38.4), random.uniform(-0.5, -0.3)),
                distancia=0.0,
                duracion=0.0,
                dificultad="bajo",
                alt_max=0,
                alt_min=0,
                origen=origen,
                puntos_intermedios=puntos_intermedios,
                destino=destino,
                modo_transporte=modo
            )

            # Guardar la ruta en formato JSON
            ruta.guardar_en_json()

            # Exportar archivos
            pdf_filename = exportar_pdf(
                ruta.distancias,
                ruta.tiempos_estimados,
                ruta.modo_transporte,
                ruta.nombre,
                ruta.origen,
                ruta.puntos_intermedios,
                ruta.destino
            )
            
            gpx_filename = exportar_gpx(ruta.rutas, ruta.grafo, ruta.timestamp)
            html_filename = generar_mapa(
                ruta.origen,
                ruta.puntos_intermedios,
                ruta.destino,
                ruta.rutas,
                ruta.grafo,
                ruta.timestamp
            )

            # Asociar la ruta al usuario si se proporciona username
            if username:
                usuarios = Usuario.cargar_usuarios()
                for usuario in usuarios:
                    if usuario['username'] == username:
                        if 'rutas' not in usuario:
                            usuario['rutas'] = []
                        usuario['rutas'].append(nombre)
                        Usuario.guardar_usuarios(usuarios)
                        break

            return {
                "nombre": nombre,
                "origen": origen,
                "destino": destino,
                "modo": modo,
                "puntos_intermedios": puntos_intermedios,
                "archivos": {
                    "pdf": pdf_filename,
                    "gpx": gpx_filename,
                    "html": html_filename
                }
            }

        except Exception as e:
            raise Exception(f"Error al crear la ruta: {str(e)}")
