import os
import json
from typing import List, Dict, Any

class GestorRutas:
    """
    Clase para gestionar rutas almacenadas en archivos JSON dentro de rutas/.

    Parameters
    ----------
    directorio : str, optional
        Ruta del directorio donde se encuentran los archivos JSON de las rutas (por defecto 'rutas').

    Attributes
    ----------
    directorio : str
        Ruta del directorio de rutas.
    rutas : List[Dict[str, Any]]
        Lista de rutas cargadas desde archivos JSON.
    """

    def __init__(self, directorio: str = "rutas"):
        """Inicializa el gestor de rutas cargando todas las rutas desde el directorio indicado."""
        self.directorio = directorio
        self.rutas = self.cargar_rutas_desde_carpeta()

    def cargar_rutas_desde_carpeta(self) -> List[Dict[str, Any]]:
        """
        Carga todas las rutas desde archivos JSON en el directorio indicado.

        Returns
        -------
        List[Dict[str, Any]]
            Lista de rutas representadas como diccionarios.
        """
        rutas = []

        if not os.path.exists(self.directorio):
            print(f"⚠️ La carpeta '{self.directorio}' no existe. Creándola...")
            os.makedirs(self.directorio)
            return rutas

        archivos = [f for f in os.listdir(self.directorio) if f.endswith(".json")]
        for archivo in archivos:
            ruta_path = os.path.join(self.directorio, archivo)
            try:
                with open(ruta_path, "r") as f:
                    ruta = json.load(f)
                    rutas.append(ruta)
            except Exception as e:
                print(f"❌ Error al leer {archivo}: {e}")
        return rutas

    def filtrar_por_dificultad(self, dificultad: str) -> List[Dict[str, Any]]:
        """
        Filtra las rutas por nivel de dificultad.

        Parameters
        ----------
        dificultad : str
            Dificultad a filtrar ('bajo', 'medio', 'alto').

        Returns
        -------
        List[Dict[str, Any]]
        """
        return [r for r in self.rutas if r.get("dificultad", "").lower() == dificultad.lower()]

    def filtrar_por_distancia(self, max_km: float) -> List[Dict[str, Any]]:
        """
        Filtra las rutas por distancia máxima en kilómetros.

        Parameters
        ----------
        max_km : float
            Distancia máxima permitida en kilómetros.

        Returns
        -------
        List[Dict[str, Any]]
        """
        filtradas = []
        for r in self.rutas:
            try:
                distancia = float(r["distancia"].replace(",", ".").split()[0])
                if distancia <= max_km:
                    filtradas.append(r)
            except:
                continue
        return filtradas

    def filtrar_por_duracion(self, max_horas: float) -> List[Dict[str, Any]]:
        """
        Filtra las rutas por duración máxima en horas.

        Parameters
        ----------
        max_horas : float
            Duración máxima permitida en horas.

        Returns
        -------
        List[Dict[str, Any]]
        """
        filtradas = []
        for r in self.rutas:
            try:
                duracion = r["duracion"].lower()
                h, m = 0, 0
                if "h" in duracion:
                    partes = duracion.replace("min", "").replace("h", "").split()
                    if len(partes) == 2:
                        h, m = int(partes[0]), int(partes[1])
                    elif len(partes) == 1:
                        h = int(partes[0])
                elif "min" in duracion:
                    m = int(duracion.replace("min", "").strip())
                total_h = h + m / 60
                if total_h <= max_horas:
                    filtradas.append(r)
            except:
                continue
        return filtradas

    def filtrar_por_transporte(self, modo_transporte: str) -> List[Dict[str, Any]]:
        """
        Devuelve una lista de rutas que usan el medio de transporte especificado.

        Parameters
        ----------
        modo_transporte : str
            El medio de transporte a filtrar (por ejemplo: 'walk', 'bike', 'drive').

        Returns
        -------
        list
            Lista de rutas que coinciden con ese modo de transporte.
        """
        modo_transporte = modo_transporte.lower()
        modos_disponibles = {ruta.get("modo_transporte", "").lower() for ruta in self.rutas}
        
        if modo_transporte not in modos_disponibles:
            raise ValueError(f"Modo de transporte '{modo_transporte}' no válido. Modos disponibles: {', '.join(modos_disponibles)}")
        
        return [ruta for ruta in self.rutas if ruta.get("modo_transporte", "").lower() == modo_transporte]
