import folium
import gpxpy
import gpxpy.gpx
from fpdf import FPDF
import os
from typing import List, Tuple
import networkx as nx
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime


def generar_mapa(
    origen: Tuple[float, float],
    intermedios: List[Tuple[float, float]],
    destino: Tuple[float, float],
    rutas: List[List[int]],
    grafo: nx.MultiDiGraph,
    timestamp: int
) -> str:
    """
    Genera un archivo HTML con el mapa y las rutas dibujadas.

    Parámetros:
    -----------
    origen : Tuple[float, float]
        Coordenadas (latitud, longitud) del punto de inicio.

    intermedios : List[Tuple[float, float]]
        Lista de coordenadas de los puntos intermedios.

    destino : Tuple[float, float]
        Coordenadas (latitud, longitud) del destino.

    rutas : List[List[int]]
        Lista de rutas, cada una representada por nodos del grafo.

    grafo : nx.MultiDiGraph
        Grafo de calles generado por OSMnx.

    timestamp : int
        Marca de tiempo usada para nombrar el archivo generado.

    Devuelve:
    ---------
    str
        Ruta del archivo HTML generado.
    """
    mapa = folium.Map(location=origen, zoom_start=14)

    folium.Marker(origen, popup="Origen", icon=folium.Icon(color='green')).add_to(mapa)
    for punto in intermedios:
        folium.Marker(punto, popup="Intermedio", icon=folium.Icon(color='orange')).add_to(mapa)
    folium.Marker(destino, popup="Destino", icon=folium.Icon(color='red')).add_to(mapa)

    for ruta in rutas:
        puntos: List[Tuple[float, float]] = [(grafo.nodes[n]['y'], grafo.nodes[n]['x']) for n in ruta]
        folium.PolyLine(puntos, color='blue', weight=5, opacity=0.7).add_to(mapa)

    if not os.path.exists("static"):
        os.makedirs("static")

    html_filename: str = f"static/rutas_{timestamp}.html"
    mapa.save(html_filename)
    return html_filename


def exportar_gpx(
    rutas: List[List[int]],
    grafo: nx.MultiDiGraph,
    timestamp: int
) -> str:
    """
    Exporta la ruta generada en formato GPX.

    Parámetros:
    -----------
    rutas : List[List[int]]
        Lista de rutas representadas por nodos del grafo.

    grafo : nx.MultiDiGraph
        Grafo de calles generado por OSMnx.

    timestamp : int
        Marca de tiempo usada para nombrar el archivo generado.

    Devuelve:
    ---------
    str
        Ruta del archivo GPX generado.
    """
    gpx = gpxpy.gpx.GPX()

    for i, ruta in enumerate(rutas):
        track = gpxpy.gpx.GPXTrack(name=f"Ruta {i + 1}")
        gpx.tracks.append(track)
        segment = gpxpy.gpx.GPXTrackSegment()
        track.segments.append(segment)

        for node in ruta:
            lat: float = grafo.nodes[node]['y']
            lon: float = grafo.nodes[node]['x']
            elevation: float = grafo.nodes[node].get('elevation', 0)
            segment.points.append(gpxpy.gpx.GPXTrackPoint(lat, lon, elevation=elevation))

    if not os.path.exists("static"):
        os.makedirs("static")

    gpx_filename: str = f"static/rutas_{timestamp}.gpx"
    with open(gpx_filename, "w") as f:
        f.write(gpx.to_xml())

    return gpx_filename

def exportar_pdf(
    distancias: List[float],
    tiempos_estimados: List[float],
    modo_transporte: str,
    nombre: str,
    origen: str,
    puntos_intermedios: List[str],
    destino: str
) -> str:
    """
    Genera un resumen visual completo de la ruta en formato PDF.

    Parámetros:
    -----------
    distancias : List[float]
        Lista de distancias en kilómetros por tramo.

    tiempos_estimados : List[float]
        Lista de tiempos estimados (en horas) por tramo.

    modo_transporte : str
        Medio de transporte utilizado (walk, bike, drive).

    nombre : str
        Nombre de la ruta (se usa para guardar el archivo PDF).

    origen : str
        Nombre del origen de la ruta.

    puntos_intermedios : List[str]
        Lista de puntos intermedios.

    destino : str
        Nombre del destino de la ruta.

    Devuelve:
    ---------
    str
        Ruta al archivo PDF generado.
    """
    # Asignar velocidad según modo de transporte
    velocidad_map = {'walk': 5, 'bike': 15, 'drive': 30}
    velocidad = velocidad_map.get(modo_transporte, '?')

    # Calcular distancias y tiempos totales
    distancia_total = sum(distancias)
    tiempo_total = sum(tiempos_estimados)
    h_tot = int(tiempo_total)
    m_tot = int((tiempo_total - h_tot) * 60)

    # Crear el PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"Resumen de la Ruta: {nombre}", ln=True, align="C")
    pdf.ln(5)

    # Información general
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Modo de transporte: {modo_transporte} (velocidad media: {velocidad} km/h)", ln=True)
    pdf.cell(0, 10, f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(5)

    # Información de origen, puntos intermedios y destino
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Ruta:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"- Origen: {origen}", ln=True)
    pdf.cell(0, 10, f"- Puntos intermedios: {', '.join(str(p) for p in puntos_intermedios)}", ln=True)
    pdf.cell(0, 10, f"- Destino: {destino}", ln=True)
    pdf.ln(5)

    # Tabla de tramos
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(20, 10, "Tramo", 1, 0, 'C', fill=True)
    pdf.cell(50, 10, "Distancia (km)", 1, 0, 'C', fill=True)
    pdf.cell(50, 10, "Duración estimada", 1, 1, 'C', fill=True)

    pdf.set_font("Arial", '', 12)
    for i, (distancia, tiempo) in enumerate(zip(distancias, tiempos_estimados)):
        h = int(tiempo)
        m = int((tiempo - h) * 60)
        tiempo_str = f"{h}h {m}m" if h > 0 else f"{m}m"

        pdf.cell(20, 10, f"{i + 1}", 1, 0, 'C')
        pdf.cell(50, 10, f"{distancia:.2f}", 1, 0, 'C')
        pdf.cell(50, 10, tiempo_str, 1, 1, 'C')

    # Resumen total
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Resumen Total:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"- Distancia total: {distancia_total:.2f} km", ln=True)
    pdf.cell(0, 10, f"- Tiempo total estimado: {h_tot}h {m_tot}m", ln=True)

    # Guardar PDF
    if not os.path.exists("static"):
        os.makedirs("static")
    pdf_filename = f"static/{nombre}.pdf"
    pdf.output(pdf_filename)

    return pdf_filename

def exportar_png_desde_html(html_path: str, output_path: str, delay: int = 3) -> None:
    """
    Versión deshabilitada de la función para evitar dependencia de Selenium/Chrome.
    
    Esta función ha sido modificada para evitar errores con ChromeDriver.
    """
    print(f"Generación de PNG deshabilitada para: {output_path}")
    # Crear un archivo de texto vacío con el mismo nombre para mantener compatibilidad
    with open(output_path, "w") as f:
        f.write("PNG generation disabled")
    return


