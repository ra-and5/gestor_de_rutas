"""Clase para manejar la geocodificación de direcciones usando Nominatim de OpenStreetMap."""
import time
from typing import Optional, Tuple
from geopy.geocoders import Nominatim
from geopy.location import Location

class Geocodificador:
    """Convierte direcciones en coordenadas geográficas (latitud y longitud)."""

    def __init__(self, user_agent: str = "PII_UA", timeout: int = 10) -> None:
        """
        Inicializa el geocodificador con un user agent y un tiempo de espera.

        Parámetros:
        -----------
        user_agent : str
            Nombre identificador para las peticiones a Nominatim.

        timeout : int
            Tiempo máximo de espera en segundos para una petición.

        Devuelve:
        ---------
        None
        """
        self.geolocator: Nominatim = Nominatim(user_agent=user_agent, timeout=timeout)

    def obtener_coordenadas(self, direccion: str) -> Optional[Tuple[float, float]]:
        """
        Devuelve una tupla (lat, lon) para una dirección dada en Alicante, España.

        - Filtra resultados fuera del rango de coordenadas esperadas para Alicante.
        - Devuelve None en caso de error o si la dirección no se encuentra.

        Parámetros:
        -----------
        direccion : str
            Dirección textual que se desea geocodificar.

        Devuelve:
        ---------
        Optional[Tuple[float, float]]
            Tupla con (latitud, longitud) si se encuentra, o None si falla.
        """
        query: str = f"{direccion}, Alicante, Spain"
        try:
            ubicacion: Optional[Location] = self.geolocator.geocode(query)
            time.sleep(1)  # Evita bloqueos por exceso de peticiones

            if ubicacion:
                lat: float = ubicacion.latitude
                lon: float = ubicacion.longitude

                if 38.22 <= lat <= 38.40 and -0.51 <= lon <= -0.43:
                    return (lat, lon)

        except Exception as e:
            print(f"Error en la geocodificación de '{direccion}': {e}")

        return None
