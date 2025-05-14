import json
from datetime import datetime
from typing import List, Optional
import osmnx as ox
import networkx as nx
import time
from geocodificador import Geocodificador
from utils import *
import os

class Ruta:
    """
    Clase que representa una ruta geográfica compuesta por un origen, puntos intermedios y un destino,
    junto con propiedades como distancia, duración, dificultad y exportaciones en varios formatos.

    Attributes
    ----------
    nombre : str
        Nombre de la ruta.
    ubicacion : tuple
        Coordenadas aproximadas de la ubicación central de la ruta.
    distancia : float
        Distancia total de la ruta (en km).
    duracion : float
        Duración estimada de la ruta (en horas).
    dificultad : str
        Nivel de dificultad ("bajo", "medio" o "alto").
    alt_max : int
        Altitud máxima (placeholder, no se calcula).
    alt_min : int
        Altitud mínima (placeholder, no se calcula).
    origen : tuple
        Coordenadas del punto de inicio.
    destino : tuple
        Coordenadas del punto de destino.
    puntos_intermedios : list
        Lista de coordenadas de puntos intermedios.
    modo_transporte : str
        Modo de transporte: "walk", "bike" o "drive".
    fecha_registro : datetime
        Fecha y hora de creación de la ruta.
    grafo : nx.MultiDiGraph
        Grafo de calles generado por OSMnx.
    rutas : list
        Lista de subrutas (cada una una lista de nodos).
    distancias : list
        Lista de distancias por tramo (en km).
    tiempos_estimados : list
        Lista de tiempos estimados por tramo (en horas).
    """

    def __init__(self, nombre: str, ubicacion: tuple, distancia: float, duracion: float,
                 dificultad: str, alt_max: int, alt_min: int,
                 origen: str, puntos_intermedios: list, destino: str, modo_transporte: str) -> None:
        """
        Inicializa una nueva instancia de Ruta, obteniendo coordenadas y preparando atributos.

        Parameters
        ----------
        nombre : str
            Nombre de la ruta.
        ubicacion : tuple
            Coordenadas iniciales aproximadas.
        distancia : float
            Distancia inicial (se recalcula después).
        duracion : float
            Duración inicial (se recalcula después).
        dificultad : str
            Nivel de dificultad (se recalcula después).
        alt_max : int
            Altitud máxima (no se usa actualmente).
        alt_min : int
            Altitud mínima (no se usa actualmente).
        origen : str
            Dirección de inicio.
        puntos_intermedios : list
            Lista de direcciones intermedias.
        destino : str
            Dirección final.
        modo_transporte : str
            "walk", "bike" o "drive".
        """
        self.nombre = nombre
        self.ubicacion = ubicacion
        self.distancia = distancia
        self.duracion = duracion
        self.dificultad = dificultad
        self.alt_max = alt_max
        self.alt_min = alt_min
        self.fecha_registro = datetime.now()
        self.modo_transporte = modo_transporte
        self.geocodificador: Geocodificador = Geocodificador()
        self.timestamp = int(time.time())

        # Nombres originales para guardar en JSON
        self.origen_nombre = origen
        self.destino_nombre = destino
        self.puntos_intermedios_nombres = puntos_intermedios.copy() if puntos_intermedios else []

        # Obtener coordenadas
        try:
            self.origen = self.geocodificador.obtener_coordenadas(origen)
            if not self.origen:
                raise ValueError(f"No se pudo geocodificar el origen: {origen}")
            
            self.destino = self.geocodificador.obtener_coordenadas(destino)
            if not self.destino:
                raise ValueError(f"No se pudo geocodificar el destino: {destino}")
            
            self.puntos_intermedios = []
            for punto in self.puntos_intermedios_nombres:
                coords = self.geocodificador.obtener_coordenadas(punto)
                if coords:
                    self.puntos_intermedios.append(coords)
                else:
                    print(f"Advertencia: No se pudo geocodificar el punto intermedio: {punto}")
            
            # Calcular rutas y grafo
            self.calcular_rutas_y_grafo()
            
        except Exception as e:
            raise Exception(f"Error al inicializar la ruta: {str(e)}")

    def calcular_rutas_y_grafo(self):
        """Calcula el grafo y las rutas óptimas entre los puntos."""
        try:
            # Crear grafo centrado en el origen
            self.grafo = ox.graph_from_point(self.origen, dist=5000, network_type=self.modo_transporte)
            nodo_origen = ox.nearest_nodes(self.grafo, self.origen[1], self.origen[0])
            nodo_destino = ox.nearest_nodes(self.grafo, self.destino[1], self.destino[0])
            nodos_intermedios = [ox.nearest_nodes(self.grafo, p[1], p[0]) for p in self.puntos_intermedios]
            ruta_nodos = [nodo_origen] + nodos_intermedios + [nodo_destino]
            self.rutas = []
            self.distancias = []
            self.tiempos_estimados = []
            for i in range(len(ruta_nodos) - 1):
                subruta = nx.shortest_path(self.grafo, ruta_nodos[i], ruta_nodos[i + 1], weight='length')
                self.rutas.append(subruta)
                distancia_km = nx.shortest_path_length(self.grafo, ruta_nodos[i], ruta_nodos[i + 1], weight='length') / 1000
                self.distancias.append(distancia_km)
                velocidad = {'walk': 5, 'bike': 15, 'drive': 60}
                tiempo_horas = distancia_km / velocidad[self.modo_transporte]
                self.tiempos_estimados.append(tiempo_horas)
        except Exception as e:
            print(f"⚠️ Error al calcular rutas y grafo: {str(e)}")
            self.grafo = None
            self.rutas = []
            self.distancias = []
            self.tiempos_estimados = []

    def calcular_metricas(self):
        """Calcula la distancia y duración de la ruta."""
        try:
            self.distancia = sum(self.distancias) if hasattr(self, 'distancias') else 0
            velocidades = {'walk': 5, 'bike': 15, 'drive': 60}
            velocidad = velocidades.get(self.modo_transporte, 5)
            self.duracion = self.distancia / velocidad if velocidad > 0 else 0
            if self.distancia < 2:
                self.dificultad = "bajo"
            elif self.distancia < 5:
                self.dificultad = "medio"
            else:
                self.dificultad = "alto"
                
        except Exception as e:
            raise Exception(f"Error al calcular métricas: {str(e)}")

    def calcular_distancia(self, punto1, punto2):
        """Calcula la distancia en kilómetros entre dos puntos."""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Radio de la Tierra en km
        
        lat1, lon1 = punto1
        lat2, lon2 = punto2
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distancia = R * c
        
        return distancia

    def calcular_dificultad(self) -> str:
        """
        Asigna una dificultad según la distancia total.

        Returns
        -------
        str
            "bajo", "medio" o "alto"
        """
        if self.distancia < 10:
            return 'bajo'
        elif self.distancia < 20:
            return 'medio'
        else:
            return 'alto'

    def calcular_duracion(self) -> float:
        """
        Estima el tiempo de recorrido total según la velocidad del modo de transporte.

        Returns
        -------
        float
            Tiempo estimado en horas.

        Raises
        ------
        ValueError
            Si el modo de transporte no es válido.
        """
        velocidad = {'walk': 5, 'bike': 15, 'drive': 30}
        if self.modo_transporte not in velocidad:
            raise ValueError("Modo de transporte no válido. Usa 'walk', 'bike' o 'drive'.")
        return self.distancia / velocidad[self.modo_transporte]

    def guardar_en_json(self) -> None:
        """
        Calcula propiedades de la ruta y guarda los datos en un archivo JSON.
        Además, genera los archivos GPX, HTML, PDF y PNG correspondientes.
        """
        try:
            # Formatear distancia y duración
            distancia_str = f"{self.distancia:.2f} km"
            horas = int(self.duracion)
            minutos = int((self.duracion - horas) * 60)
            duracion_str = f"{horas} h {minutos} min" if horas > 0 else f"{minutos} min"

            datos_ruta = {
                "nombre": self.nombre,
                "ubicacion": self.ubicacion,
                "distancia": distancia_str,
                "duracion": duracion_str,
                "dificultad": self.dificultad,
                "fecha_registro": self.fecha_registro.strftime("%Y-%m-%d %H:%M:%S"),
                "origen": self.origen_nombre,
                "puntos_intermedios": self.puntos_intermedios_nombres,
                "destino": self.destino_nombre,
                "modo_transporte": self.modo_transporte
            }

            # Asegurar que el directorio existe
            try:
                os.makedirs("rutas", exist_ok=True)
            except Exception as e:
                print(f"⚠️ Error al crear el directorio 'rutas': {str(e)}")
                raise

            # Guardar archivo JSON
            try:
                with open(f"rutas/{self.nombre}.json", "w", encoding="utf-8") as archivo:
                    json.dump(datos_ruta, archivo, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"⚠️ Error al guardar el archivo JSON: {str(e)}")
                raise

            # Exportar archivos adicionales SOLO si el grafo y rutas existen
            if hasattr(self, 'grafo') and self.grafo and hasattr(self, 'rutas') and self.rutas:
                try:
                    if 'exportar_gpx' in globals():
                        exportar_gpx(self.puntos_intermedios, self.nombre)
                    else:
                        print("⚠️ Función exportar_gpx no disponible.")
                    if 'generar_mapa' in globals():
                        generar_mapa(
                            self.origen,
                            self.puntos_intermedios,
                            self.destino,
                            self.rutas,
                            self.grafo,
                            self.nombre
                        )
                    else:
                        print("⚠️ Función generar_mapa no disponible.")
                    if 'exportar_pdf' in globals():
                        exportar_pdf(
                            self.distancias,
                            self.tiempos_estimados,
                            self.modo_transporte,
                            self.nombre,
                            self.origen_nombre,
                            self.puntos_intermedios_nombres,
                            self.destino_nombre
                        )
                    else:
                        print("⚠️ Función exportar_pdf no disponible.")
                except Exception as e:
                    print(f"⚠️ Error al exportar archivos adicionales: {str(e)}")

        except Exception as e:
            print(f"❌ Error al guardar la ruta: {str(e)}")
            raise Exception(f"Error al guardar la ruta: {str(e)}")

    @staticmethod
    def listar_rutas() -> List[dict]:
        """
        Lista todas las rutas almacenadas en formato JSON dentro del directorio 'rutas/'.

        Recorre todos los archivos `.json` de la carpeta `rutas`, los carga como diccionarios
        y los agrega a una lista que es devuelta al final.

        Returns
        -------
        List[dict]
            Lista de rutas representadas como diccionarios.
            Si no existe la carpeta o no hay archivos válidos, devuelve una lista vacía.
        """
        rutas = []
        if not os.path.exists("rutas"):
            return rutas
        for filename in os.listdir("rutas"):
            if filename.endswith(".json"):
                with open(os.path.join("rutas", filename), "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        rutas.append(data)
                    except Exception:
                        continue
        return rutas
    
    def to_dict(self):
        """
        Convierte la instancia de la clase `Ruta` en un diccionario con sus atributos relevantes.

        Este método crea un diccionario con los valores de los atributos de la ruta, incluyendo
        el nombre, modo de transporte, distancia, duración y dificultad. Los métodos `distancia_str()` 
        y `duracion_str()` son utilizados para obtener las representaciones en cadena de los atributos 
        `distancia` y `duracion`.

        Returns
        -------
        dict
            Un diccionario con los siguientes campos:
            - "nombre" (str): Nombre de la ruta.
            - "modo_transporte" (str): Modo de transporte utilizado en la ruta.
            - "distancia" (str): Distancia de la ruta, representada como cadena.
            - "duracion" (str): Duración estimada de la ruta, representada como cadena.
            - "dificultad" (str): Nivel de dificultad de la ruta.
        """
        return {
            "nombre": self.nombre,
            "modo_transporte": self.modo_transporte,
            "distancia": f"{self.distancia:.2f} km",
            "duracion": f"{int(self.duracion)}h {int((self.duracion-int(self.duracion))*60)}m",
            "dificultad": self.dificultad
        }


