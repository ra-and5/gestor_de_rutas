import os
from ruta_manual import RutaManual
import json
import time
from datetime import datetime

# Rutas en PythonAnywhere
PYTHONANYWHERE_BASE = "https://ra55.pythonanywhere.com/"
RUTAS_DIR = os.path.join(PYTHONANYWHERE_BASE, "rutas")
STATIC_DIR = os.path.join(PYTHONANYWHERE_BASE, "static")

def verificar_estructura_carpetas():
    """Verifica que las carpetas necesarias existan en PythonAnywhere."""
    carpetas = [RUTAS_DIR, STATIC_DIR]
    for carpeta in carpetas:
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
            print(f"✅ Carpeta '{carpeta}' creada en PythonAnywhere")
        else:
            print(f"✅ Carpeta '{carpeta}' ya existe en PythonAnywhere")

def crear_ruta_prueba():
    """Crea una ruta de prueba directamente en PythonAnywhere."""
    nombre_ruta = f"Ruta_Test_{int(time.time())}"
    
    # Crear ruta manual
    ruta = RutaManual.crear_ruta_desde_datos(
        origen='Plaza de los Luceros',
        destino='Calle San Vicente',
        puntos_intermedios=['Playa del Postiguet'],
        modo='bike',
        nombre=nombre_ruta,
        username='rare'
    )
    
    return nombre_ruta, ruta

def verificar_archivos(nombre_ruta):
    """Verifica que todos los archivos se hayan creado correctamente en PythonAnywhere."""
    archivos = {
        'json': {
            'ruta': os.path.join(RUTAS_DIR, f"{nombre_ruta}.json"),
            'descripcion': 'Archivo JSON de la ruta',
            'url': None
        },
        'pdf': {
            'ruta': os.path.join(STATIC_DIR, f"{nombre_ruta}.pdf"),
            'descripcion': 'Archivo PDF de la ruta',
            'url': f"https://ra55.pythonanywhere.com/static/{nombre_ruta}.pdf"
        },
        'html': {
            'ruta': os.path.join(STATIC_DIR, f"rutas_{nombre_ruta}.html"),
            'descripcion': 'Archivo HTML del mapa',
            'url': f"https://ra55.pythonanywhere.com/static/rutas_{nombre_ruta}.html"
        }
    }
    
    print("\n=== Verificación de archivos en PythonAnywhere ===")
    for tipo, info in archivos.items():
        ruta = info['ruta']
        existe = os.path.exists(ruta)
        tamaño = os.path.getsize(ruta) if existe else 0
        
        print(f"\n{tipo.upper()} ({info['descripcion']}):")
        print(f"- Ruta en servidor: {ruta}")
        if info['url']:
            print(f"- URL de acceso: {info['url']}")
        print(f"- Existe: {'✅' if existe else '❌'}")
        if existe:
            print(f"- Tamaño: {tamaño} bytes")
            
            # Verificar contenido del JSON
            if tipo == 'json':
                try:
                    with open(ruta, 'r', encoding='utf-8') as f:
                        datos = json.load(f)
                    print("- Contenido JSON válido: ✅")
                    print(f"- Datos principales:")
                    print(f"  * Nombre: {datos.get('nombre')}")
                    print(f"  * Origen: {datos.get('origen')}")
                    print(f"  * Destino: {datos.get('destino')}")
                    print(f"  * Modo: {datos.get('modo_transporte')}")
                except Exception as e:
                    print(f"- Error al leer JSON: {str(e)}")
    
    return archivos

if __name__ == '__main__':
    print("=== Iniciando verificación de rutas en PythonAnywhere ===")
    
    # Verificar estructura de carpetas
    verificar_estructura_carpetas()
    
    # Crear ruta de prueba
    nombre_ruta, ruta = crear_ruta_prueba()
    print(f"\n✅ Ruta creada: {nombre_ruta}")
    
    # Verificar archivos
    archivos = verificar_archivos(nombre_ruta)
    
    print("\n=== Instrucciones de acceso ===")
    print("1. Los archivos se han creado directamente en PythonAnywhere:")
    print(f"   - JSON: {os.path.join(RUTAS_DIR, f'{nombre_ruta}.json')}")
    print(f"   - PDF: {os.path.join(STATIC_DIR, f'{nombre_ruta}.pdf')}")
    print(f"   - HTML: {os.path.join(STATIC_DIR, f'rutas_{nombre_ruta}.html')}")
    print("\n2. Puedes acceder a los archivos a través de las URLs:")
    print(f"   - PDF: https://ra55.pythonanywhere.com/static/{nombre_ruta}.pdf")
    print(f"   - HTML: https://ra55.pythonanywhere.com/static/rutas_{nombre_ruta}.html") 