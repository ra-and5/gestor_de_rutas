from ruta_manual import RutaManual
import os
import json
from datetime import datetime

def test_crear_ruta_manual():
    try:
        print("🚀 Iniciando prueba de creación de ruta manual...")
        
        # Datos de prueba
        nombre = f"Test_Ruta_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        origen = "Calle San Vicente"
        puntos_intermedios = ["Calle Belando", "Plaza de los Luceros"]
        destino = "Calle San Vicente"
        modo = "bike"
        username = "test_user"
        
        print(f"📝 Creando ruta con nombre: {nombre}")
        print(f"📍 Origen: {origen}")
        print(f"📍 Puntos intermedios: {puntos_intermedios}")
        print(f"📍 Destino: {destino}")
        print(f"🚲 Modo de transporte: {modo}")
        
        # Crear la ruta
        ruta = RutaManual.crear_ruta_desde_datos(
            origen=origen,
            puntos_intermedios=puntos_intermedios,
            destino=destino,
            modo=modo,
            nombre=nombre,
            username=username
        )
        
        # Verificar que se crearon los archivos
        print("\n🔍 Verificando archivos generados...")
        
        # Verificar JSON
        json_path = f"/home/RA55/gestor_de_rutas/rutas/{nombre}.json"
        if os.path.exists(json_path):
            print("✅ JSON creado correctamente")
            with open(json_path, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                print(f"📄 Contenido del JSON:")
                print(json.dumps(datos, indent=2, ensure_ascii=False))
        else:
            print("❌ Error: No se encontró el archivo JSON")
        
        # Verificar PDF
        pdf_path = f"/home/RA55/gestor_de_rutas/static/{nombre}.pdf"
        if os.path.exists(pdf_path):
            print("✅ PDF creado correctamente")
            print(f"📄 Tamaño del PDF: {os.path.getsize(pdf_path)} bytes")
        else:
            print("❌ Error: No se encontró el archivo PDF")
        
        # Verificar HTML
        html_path = f"/home/RA55/gestor_de_rutas/static/rutas_{nombre}.html"
        if os.path.exists(html_path):
            print("✅ HTML creado correctamente")
            print(f"📄 Tamaño del HTML: {os.path.getsize(html_path)} bytes")
        else:
            print("❌ Error: No se encontró el archivo HTML")
        
        # Verificar URLs
        print("\n🔗 URLs generadas:")
        print(f"PDF: https://ra55.pythonanywhere.com/static/{nombre}.pdf")
        print(f"HTML: https://ra55.pythonanywhere.com/static/rutas_{nombre}.html")
        
        print("\n✨ Prueba completada!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Iniciando pruebas de ruta manual...")
    test_crear_ruta_manual() 