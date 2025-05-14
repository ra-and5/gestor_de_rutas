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

# Rutas en PythonAnywhere
PYTHONANYWHERE_BASE = "/home/RA55/gestor_de_rutas"
STATIC_DIR = os.path.join(PYTHONANYWHERE_BASE, "static")

def generar_mapa(
    origen: Tuple[float, float],
    intermedios: List[Tuple[float, float]],
    destino: Tuple[float, float],
    rutas: List[List[int]],
    grafo: nx.MultiDiGraph,
    nombre_ruta: str
) -> str:
    """
    Genera un archivo HTML con el mapa y las rutas dibujadas directamente en PythonAnywhere.
    """
    # Asegurar que el directorio static existe
    os.makedirs(STATIC_DIR, exist_ok=True)
    
    # Si no hay grafo ni rutas reales, crear un HTML de ejemplo
    if not grafo or not rutas:
        html_filename = os.path.join(STATIC_DIR, f"rutas_{nombre_ruta}.html")
        with open(html_filename, "w", encoding="utf-8") as f:
            f.write(f"""<html>
<head>
    <title>Ruta {nombre_ruta}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .info {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>Ruta: {nombre_ruta}</h1>
    <div class="info">
        <p>Esta es una ruta de ejemplo generada automáticamente.</p>
        <p>Origen: {origen}</p>
        <p>Destino: {destino}</p>
        <p>Puntos intermedios: {intermedios}</p>
    </div>
</body>
</html>""")
        return html_filename

    # Crear mapa con Folium
    mapa = folium.Map(location=origen, zoom_start=14)

    # Añadir marcadores
    folium.Marker(origen, popup="Origen", icon=folium.Icon(color='green')).add_to(mapa)
    for punto in intermedios:
        folium.Marker(punto, popup="Intermedio", icon=folium.Icon(color='orange')).add_to(mapa)
    folium.Marker(destino, popup="Destino", icon=folium.Icon(color='red')).add_to(mapa)

    # Añadir rutas
    for ruta in rutas:
        puntos: List[Tuple[float, float]] = [(grafo.nodes[n]['y'], grafo.nodes[n]['x']) for n in ruta]
        folium.PolyLine(puntos, color='blue', weight=5, opacity=0.7).add_to(mapa)

    # Guardar el mapa
    html_filename = os.path.join(STATIC_DIR, f"rutas_{nombre_ruta}.html")
    mapa.save(html_filename)
    return html_filename

def exportar_gpx(puntos_intermedios, nombre):
    """
    Exporta la ruta en formato GPX directamente en PythonAnywhere.
    """
    try:
        # Asegurar que el directorio existe
        gpx_dir = os.path.join(STATIC_DIR, "gpx")
        os.makedirs(gpx_dir, exist_ok=True)
        
        # Crear archivo GPX
        gpx_filename = os.path.join(gpx_dir, f"{nombre}.gpx")
        
        # Crear contenido GPX básico
        gpx_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Rutas Alicante">
  <metadata>
    <name>{nombre}</name>
    <time>{datetime.now().isoformat()}</time>
  </metadata>
  <trk>
    <name>{nombre}</name>
    <trkseg>
"""
        
        # Agregar puntos intermedios
        for punto in puntos_intermedios:
            if isinstance(punto, tuple) and len(punto) == 2:
                lat, lon = punto
                gpx_content += f"      <trkpt lat='{lat}' lon='{lon}'></trkpt>\n"
        
        gpx_content += """    </trkseg>
  </trk>
</gpx>"""
        
        # Guardar archivo
        with open(gpx_filename, "w", encoding="utf-8") as f:
            f.write(gpx_content)
            
        return gpx_filename
        
    except Exception as e:
        raise Exception(f"Error al exportar GPX: {str(e)}")

def exportar_pdf(
    distancias: List[float],
    tiempos_estimados: List[float],
    modo_transporte: str,
    nombre: str,
    origen: str,
    puntos_intermedios: List[str],
    destino: str
) -> bytes:
    """
    Genera un resumen visual completo de la ruta en formato PDF.
    Devuelve los bytes del PDF para guardarlo en PythonAnywhere.
    """
    try:
        # Valores por defecto si no hay datos
        if not distancias or not tiempos_estimados:
            distancias = [1.0]
            tiempos_estimados = [0.5]

        # Crear PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Título
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, f"Resumen de la Ruta: {nombre}", ln=True, align="C")
        pdf.ln(5)

        # Información básica
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Modo de transporte: {modo_transporte}", ln=True)
        pdf.cell(0, 10, f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.ln(5)

        # Ruta
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Ruta:", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"- Origen: {origen}", ln=True)
        for punto in puntos_intermedios:
            pdf.cell(0, 10, f"- Punto intermedio: {punto}", ln=True)
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
        pdf.cell(0, 10, f"- Distancia total: {sum(distancias):.2f} km", ln=True)
        pdf.cell(0, 10, f"- Tiempo total estimado: {int(sum(tiempos_estimados))}h {int((sum(tiempos_estimados)-int(sum(tiempos_estimados)))*60)}m", ln=True)

        # Devolver los bytes del PDF
        return pdf.output(dest='S').encode('latin1')
    except Exception as e:
        print(f"⚠️ Error al generar PDF: {str(e)}")
        raise

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


