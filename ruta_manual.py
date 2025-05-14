import random
from ruta import Ruta
from utils import *
import json 
import time
import os
from datetime import datetime
from typing import List, Optional
import sqlite3

# Rutas en PythonAnywhere
PYTHONANYWHERE_BASE = "/home/RA55/gestor_de_rutas"
RUTAS_DIR = os.path.join(PYTHONANYWHERE_BASE, "rutas")
STATIC_DIR = os.path.join(PYTHONANYWHERE_BASE, "static")

class RutaManual(Ruta):
    """
    Clase que representa una ruta manual, heredando de la clase Ruta.
    """

    def __init__(self, nombre: str, ubicacion: tuple, distancia: float, duracion: float,
                 dificultad: str, alt_max: int, alt_min: int,
                 origen: str, puntos_intermedios: list, destino: str, modo_transporte: str) -> None:
        super().__init__(nombre, ubicacion, distancia, duracion, dificultad, alt_max, alt_min,
                         origen, puntos_intermedios, destino, modo_transporte)

    def guardar_en_json(self) -> None:
        """
        Guarda la ruta manual en formato JSON y exporta archivos adicionales directamente en PythonAnywhere.
        """
        try:
            # Formatear distancia y duración
            distancia_str = f"{self.distancia:.2f} km"
            horas = int(self.duracion)
            minutos = int((self.duracion - horas) * 60)
            duracion_str = f"{horas} h {minutos} min" if horas > 0 else f"{minutos} min"
            
            # Datos de la ruta
            datos_ruta = {
                "nombre": self.nombre,
                "origen": {"direccion": self.origen} if isinstance(self.origen, str) else self.origen,
                "destino": {"direccion": self.destino} if isinstance(self.destino, str) else self.destino,
                "puntos_intermedios": [{"direccion": p} if isinstance(p, str) else p for p in self.puntos_intermedios],
                "modo": self.modo_transporte,
                "distancia_km": self.distancia,
                "duracion_horas": self.duracion,
                "dificultad": self.dificultad,
                "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Asegurar que los directorios existen
            os.makedirs(RUTAS_DIR, exist_ok=True)
            os.makedirs(STATIC_DIR, exist_ok=True)
            
            # Guardar el JSON de la ruta
            json_path = os.path.join(RUTAS_DIR, f"{self.nombre}.json")
            with open(json_path, "w", encoding="utf-8") as archivo:
                json.dump(datos_ruta, archivo, indent=4, ensure_ascii=False)

            # Exportar PDF y HTML a la carpeta static
            try:
                # Obtener las direcciones para el PDF
                origen_direccion = self.origen if isinstance(self.origen, str) else self.origen.get('direccion', '')
                destino_direccion = self.destino if isinstance(self.destino, str) else self.destino.get('direccion', '')
                puntos_intermedios_direcciones = [p if isinstance(p, str) else p.get('direccion', '') for p in self.puntos_intermedios]

                # Exportar PDF
                pdf_path = os.path.join(STATIC_DIR, f"{self.nombre}.pdf")
                pdf = exportar_pdf(
                    [self.distancia],
                    [self.duracion],
                    self.modo_transporte,
                    self.nombre,
                    origen_direccion,
                    puntos_intermedios_direcciones,
                    destino_direccion
                )
                with open(pdf_path, "wb") as f:
                    f.write(pdf)
                print(f"✅ PDF guardado en: {pdf_path}")
                
                # Exportar HTML
                html_path = os.path.join(STATIC_DIR, f"rutas_{self.nombre}.html")
                html = generar_mapa(
                    self.origen if isinstance(self.origen, tuple) else (0, 0),
                    [p if isinstance(p, tuple) else (0, 0) for p in self.puntos_intermedios],
                    self.destino if isinstance(self.destino, tuple) else (0, 0),
                    [[0, 1]],  # Ruta de ejemplo
                    None,      # Sin grafo
                    self.nombre
                )
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"✅ HTML guardado en: {html_path}")
                
                # Actualizar el JSON con las URLs de los archivos
                datos_ruta["archivos"] = {
                    "pdf": f"https://ra55.pythonanywhere.com/static/{self.nombre}.pdf",
                    "html": f"https://ra55.pythonanywhere.com/static/rutas_{self.nombre}.html"
                }
                
                # Guardar el JSON actualizado
                with open(json_path, "w", encoding="utf-8") as archivo:
                    json.dump(datos_ruta, archivo, indent=4, ensure_ascii=False)
                    
            except Exception as e:
                print(f"⚠️ Error al exportar archivos: {str(e)}")
                raise

        except Exception as e:
            raise Exception(f"Error al guardar la ruta: {str(e)}")

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
            # Validar parámetros
            if not origen or not destino:
                raise ValueError("El origen y destino son obligatorios")
            
            if not isinstance(puntos_intermedios, list):
                puntos_intermedios = []
            
            # Validar modo de transporte
            modos_validos = ["walk", "bike", "drive"]
            if modo not in modos_validos:
                modo = "walk"  # valor por defecto
            
            # Generar nombre único si no se proporciona
            if not nombre:
                nombre = f"Ruta_{int(time.time())}"

            # Crear objeto RutaManual
            ruta = RutaManual(
                nombre=nombre,
                ubicacion=(random.uniform(38.3, 38.4), random.uniform(-0.5, -0.3)),
                distancia=10.0,  # Valor de ejemplo
                duracion=0.5,    # Valor de ejemplo
                dificultad="medio",
                alt_max=0,
                alt_min=0,
                origen=origen,
                puntos_intermedios=puntos_intermedios,
                destino=destino,
                modo_transporte=modo
            )

            # Guardar la ruta y exportar archivos
            ruta.guardar_en_json()

            # Asociar la ruta al usuario en la base de datos SQLite
            if username:
                conn = sqlite3.connect('usuarios.db')
                cursor = conn.cursor()
                
                # Obtener el ID del usuario
                cursor.execute('SELECT id FROM usuarios WHERE username = ?', (username,))
                usuario = cursor.fetchone()
                
                if usuario:
                    # Insertar la relación usuario-ruta
                    cursor.execute('''
                        INSERT OR REPLACE INTO usuario_rutas (
                            usuario_id, nombre_ruta, created_at
                        ) VALUES (?, ?, ?)
                    ''', (
                        usuario[0],
                        nombre,
                        datetime.now().isoformat()
                    ))
                    
                    conn.commit()
                conn.close()

            return {
                "nombre": nombre,
                "origen": origen,
                "destino": destino,
                "modo": modo,
                "puntos_intermedios": puntos_intermedios,
                "archivos": {
                    "pdf": f"https://ra55.pythonanywhere.com/static/{nombre}.pdf",
                    "html": f"https://ra55.pythonanywhere.com/static/rutas_{nombre}.html"
                }
            }

        except Exception as e:
            raise Exception(f"Error al crear la ruta: {str(e)}")
