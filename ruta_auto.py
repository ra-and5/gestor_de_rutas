from ruta import Ruta
import random
import os
from typing import List
import time
import sqlite3
from datetime import datetime
from utils import exportar_pdf, generar_mapa

# Rutas en PythonAnywhere
PYTHONANYWHERE_BASE = "/home/RA55/gestor_de_rutas"
RUTAS_DIR = os.path.join(PYTHONANYWHERE_BASE, "rutas")
STATIC_DIR = os.path.join(PYTHONANYWHERE_BASE, "static")

class RutaAuto:
    def __init__(self, directorio: str = RUTAS_DIR) -> None:
        self.directorio = directorio
        os.makedirs(self.directorio, exist_ok=True)
        self.rutas = []
        self.grafo = None
        self.timestamp = None

    def generar_rutas_desde_direcciones(self, direcciones: List[str], cantidad: int = 5, username: str = None) -> List[str]:
        try:
            if len(direcciones) < 2:
                raise ValueError("Se necesitan al menos 2 direcciones para generar una ruta")

            rutas_generadas = []
            for i in range(cantidad):
                direcciones_mezcladas = direcciones.copy()
                random.shuffle(direcciones_mezcladas)
                nombre_ruta = f"Ruta_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i+1}"

                # Crear objeto RutaManual
                ruta = Ruta(
                    nombre=nombre_ruta,
                    ubicacion=(random.uniform(38.3, 38.4), random.uniform(-0.5, -0.3)),
                    distancia=10.0,
                    duracion=2.0,
                    dificultad="medio",
                    alt_max=0,
                    alt_min=0,
                    origen=direcciones_mezcladas[0],
                    puntos_intermedios=[],
                    destino=direcciones_mezcladas[-1],
                    modo_transporte="walk"
                )

                # Simular datos mínimos para exportar PDF y HTML
                ruta.rutas = [[0, 1]]
                ruta.distancias = [ruta.distancia]
                ruta.tiempos_estimados = [ruta.duracion]
                ruta.grafo = None  # No se usa en el HTML de ejemplo

                # Guardar el JSON y exportar archivos
                ruta.guardar_en_json()

                # Exportar PDF y HTML a la carpeta static de PythonAnywhere
                try:
                    # Asegurar que los directorios existen
                    os.makedirs(STATIC_DIR, exist_ok=True)
                    
                    # Exportar PDF
                    pdf_path = os.path.join(STATIC_DIR, f"{nombre_ruta}.pdf")
                    pdf = exportar_pdf(
                        ruta.distancias,
                        ruta.tiempos_estimados,
                        ruta.modo_transporte,
                        ruta.nombre,
                        ruta.origen,
                        ruta.puntos_intermedios,
                        ruta.destino
                    )
                    with open(pdf_path, "wb") as f:
                        f.write(pdf)
                    
                    # Exportar HTML
                    html_path = os.path.join(STATIC_DIR, f"rutas_{nombre_ruta}.html")
                    html = generar_mapa(
                        ruta.origen,
                        ruta.puntos_intermedios,
                        ruta.destino,
                        ruta.rutas,
                        ruta.grafo,
                        ruta.nombre
                    )
                    with open(html_path, "w", encoding="utf-8") as f:
                        f.write(html)

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
                                nombre_ruta,
                                datetime.now().isoformat()
                            ))
                            
                            conn.commit()
                        conn.close()

                    rutas_generadas.append({
                        "nombre": nombre_ruta,
                        "archivos": {
                            "pdf": f"https://ra55.pythonanywhere.com/static/{nombre_ruta}.pdf",
                            "html": f"https://ra55.pythonanywhere.com/static/rutas_{nombre_ruta}.html"
                        }
                    })
                except Exception as e:
                    print(f"⚠️ Error al exportar archivos: {str(e)}")
                    rutas_generadas.append(f"❌ Error al exportar archivos para '{nombre_ruta}': {str(e)}")

            return rutas_generadas

        except Exception as e:
            return [f"❌ Error general: {str(e)}"]

    def generar_rutas_desde_direcciones_old(self, direcciones: List[str], cantidad: int = 5) -> List[str]:
        """
        Genera rutas aleatorias entre las direcciones proporcionadas y las exporta en varios formatos.

        Parámetros:
        -----------
        direcciones : List[str]
            Lista de direcciones reales introducidas por el usuario.

        cantidad : int
            Número de rutas aleatorias a generar (por defecto 5).

        Returns:
        --------
        List[str]
            Lista de mensajes indicando el resultado de cada ruta generada.
        """
        try:
            # Validar parámetros
            if not direcciones or len(direcciones) < 2:
                return ["⚠️ Se necesitan al menos dos direcciones para generar rutas."]

            if cantidad < 1:
                cantidad = 1
            elif cantidad > 10:
                cantidad = 10  # Límite máximo de rutas

            rutas_creadas = []  # Guardar las rutas generadas
            direcciones_validas = [d.strip() for d in direcciones if d.strip()]

            if len(direcciones_validas) < 2:
                return ["⚠️ No hay suficientes direcciones válidas para generar rutas."]

            for i in range(cantidad):
                try:
                    # Seleccionar puntos aleatorios
                    origen, destino = random.sample(direcciones_validas, 2)
                    puntos_intermedios = random.sample(
                        [d for d in direcciones_validas if d != origen and d != destino],
                        k=min(2, len(direcciones_validas) - 2)
                    ) if len(direcciones_validas) > 2 else []
                    
                    modo = random.choice(["walk", "bike", "drive"])
                    nombre = f"ruta_auto_{int(time.time())}_{i+1}"

                    # Coordenadas aleatorias como referencia inicial
                    ubicacion = (random.uniform(38.3, 38.4), random.uniform(-0.5, -0.3))

                    ruta = Ruta(
                        nombre=nombre,
                        ubicacion=ubicacion,
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

                    ruta.guardar_en_json()
                    rutas_creadas.append(f"✅ Ruta '{nombre}' creada y exportada exitosamente.")
                    
                except Exception as e:
                    rutas_creadas.append(f"❌ Error al crear ruta {i+1}: {str(e)}")
                    continue

            return rutas_creadas

        except Exception as e:
            return [f"❌ Error general: {str(e)}"]