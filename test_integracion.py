import requests
import os

# Cambia esto por tu usuario de PythonAnywhere
API_URL = "https://ra55.pythonanywhere.com"
USERNAME = "test_user"  # Cambia por un usuario real que tenga rutas

def test_rutas_usuario(username):
    print(f"🔍 Comprobando rutas para el usuario: {username}")

    # 1. Obtener rutas del usuario desde la API
    try:
        resp = requests.get(f"{API_URL}/api/usuarios/{username}/rutas")
        data = resp.json()
        if data.get("status") != "success":
            print("❌ Error al obtener rutas desde la API:", data.get("message"))
            return
        rutas = data.get("data", [])
        if not rutas:
            print("❌ El usuario no tiene rutas.")
            return
        print(f"✅ El usuario tiene {len(rutas)} rutas.")
    except Exception as e:
        print("❌ Error al consultar la API:", e)
        return

    # 2. Comprobar archivos PDF y HTML en la URL pública
    for ruta in rutas:
        nombre = ruta.get("nombre")
        pdf_url = f"{API_URL}/static/{nombre}.pdf"
        html_url = f"{API_URL}/static/rutas_{nombre}.html"
        print(f"\nRuta: {nombre}")

        # Comprobar PDF
        try:
            resp_pdf = requests.get(pdf_url)
            if resp_pdf.status_code == 200 and resp_pdf.headers.get("Content-Type", "").startswith("application/pdf"):
                print(f"   ✅ PDF accesible: {pdf_url}")
            else:
                print(f"   ❌ PDF NO accesible ({resp_pdf.status_code}): {pdf_url}")
        except Exception as e:
            print(f"   ❌ Error accediendo al PDF: {e}")

        # Comprobar HTML
        try:
            resp_html = requests.get(html_url)
            if resp_html.status_code == 200 and "html" in resp_html.headers.get("Content-Type", ""):
                print(f"   ✅ HTML accesible: {html_url}")
            else:
                print(f"   ❌ HTML NO accesible ({resp_html.status_code}): {html_url}")
        except Exception as e:
            print(f"   ❌ Error accediendo al HTML: {e}")

if __name__ == "__main__":
    test_rutas_usuario(USERNAME)