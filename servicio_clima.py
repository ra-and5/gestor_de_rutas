"""
Módulo para consulta de información meteorológica.

Este módulo implementa un servicio de consulta de clima utilizando la API de OpenWeatherMap.

"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime
import requests
from dataclasses import dataclass

@dataclass
class DatosClima:
    """
    Clase para almacenar los datos del clima de manera estructurada.
    
    Attributes
    ----------
    ciudad : str
        Nombre de la ciudad
    temperatura : float
        Temperatura en grados Celsius
    humedad : int
        Humedad en porcentaje
    descripcion : str
        Descripción del clima
    viento : float
        Velocidad del viento en m/s
    fecha : datetime
        Fecha y hora de la medición
    """
    ciudad: str
    temperatura: float
    humedad: int
    descripcion: str
    viento: float
    fecha: datetime

class ServicioClimaInterface(ABC):
    """
    Interfaz abstracta para el servicio de clima.
    
    Esta interfaz define el contrato que deben implementar todos los servicios de clima.
    
    Methods
    -------
    obtener_clima(ciudad: str) -> DatosClima
        Obtiene información del clima para una ciudad específica
    """
    
    @abstractmethod
    def obtener_clima(self, ciudad: str) -> DatosClima:
        """
        Obtiene información del clima para una ciudad específica.
        
        Parameters
        ----------
        ciudad : str
            Nombre de la ciudad para la que se desea obtener el clima
            
        Returns
        -------
        DatosClima
            Objeto con la información del clima
            
        Raises
        ------
        Exception
            Si hay un error al obtener los datos del clima
        """
        pass

class ServicioOpenWeatherMap(ServicioClimaInterface):
    """
    Implementación concreta del servicio de clima usando OpenWeatherMap API.
    
    Esta clase implementa la interfaz ServicioClimaInterface y proporciona
    la funcionalidad específica para obtener datos de OpenWeatherMap.
    
    Attributes
    ----------
    clave_api : str
        Clave de API para acceder a OpenWeatherMap
    url_base : str
        URL base de la API de OpenWeatherMap
    """
    
    def __init__(self, clave_api: str = "5ead714f2ad83f23daf51c47124fd500") -> None:
        """
        Inicializa el servicio de OpenWeatherMap.
        
        Parameters
        ----------
        clave_api : str
            Clave de API para acceder a OpenWeatherMap
        """
        self.clave_api: str = clave_api
        self.url_base: str = "http://api.openweathermap.org/data/2.5/weather"

    def obtener_clima(self, ciudad: str) -> DatosClima:
        """
        Obtiene información del clima para una ciudad específica.
        
        Parameters
        ----------
        ciudad : str
            Nombre de la ciudad para la que se desea obtener el clima
            
        Returns
        -------
        DatosClima
            Objeto con la información del clima
            
        Raises
        ------
        requests.RequestException
            Si hay un error en la petición HTTP
        """
        try:
            parametros: Dict[str, str] = {
                "q": ciudad,
                "appid": self.clave_api,
                "units": "metric",
                "lang": "es"
            }
            
            respuesta = requests.get(self.url_base, params=parametros)
            respuesta.raise_for_status()
            
            datos: Dict[str, Any] = respuesta.json()
            return self._formatear_datos(datos)
            
        except requests.RequestException as e:
            raise Exception(f"Error al obtener el clima: {str(e)}")
    
    def _formatear_datos(self, datos: Dict[str, Any]) -> DatosClima:
        """
        Formatea los datos del clima en un objeto DatosClima.
        
        Parameters
        ----------
        datos : Dict[str, Any]
            Datos crudos de la API
            
        Returns
        -------
        DatosClima
            Objeto formateado con la información del clima
        """
        return DatosClima(
            ciudad=datos["name"],
            temperatura=datos["main"]["temp"],
            humedad=datos["main"]["humidity"],
            descripcion=datos["weather"][0]["description"],
            viento=datos["wind"]["speed"],
            fecha=datetime.fromtimestamp(datos["dt"])
        )

class GestorClima:
    """
    Clase que gestiona el servicio de clima.
    
    Attributes
    ----------
    servicio : ServicioClimaInterface
        Servicio de clima a utilizar
    """
    
    def __init__(self, servicio: ServicioClimaInterface) -> None:
        """
        Inicializa el gestor de clima.
        
        Parameters
        ----------
        servicio : ServicioClimaInterface
            Servicio de clima a utilizar
        """
        self.servicio: ServicioClimaInterface = servicio
    
    def consultar_clima(self, ciudad: str) -> DatosClima:
        """
        Consulta el clima para una ciudad específica.
        
        Parameters
        ----------
        ciudad : str
            Nombre de la ciudad para la que se desea obtener el clima
            
        Returns
        -------
        DatosClima
            Objeto con la información del clima
        """
        return self.servicio.obtener_clima(ciudad)
