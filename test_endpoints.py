import requests
import json
from datetime import datetime

# URL base de la API
BASE_URL = "https://ra55.pythonanywhere.com"

def test_endpoint(endpoint, method="GET", data=None, params=None):
    """
    Función auxiliar para probar endpoints
    """
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            raise ValueError(f"Método no soportado: {method}")

        print(f"\n🔍 Probando {method} {endpoint}")
        print(f"📡 Status Code: {response.status_code}")
        print(f"📦 Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error en {endpoint}: {str(e)}")
        return False

def main():
    print("🚀 Iniciando pruebas de endpoints...")
    
    # 1. Probar endpoint principal
    print("\n1️⃣ Probando endpoint principal")
    test_endpoint("/")

    # 2. Probar registro de usuario
    print("\n2️⃣ Probando registro de usuario")
    usuario_prueba = {
        "nombre": "Usuario",
        "apellido": "Prueba",
        "email": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com",
        "username": f"test_user_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "password": "test123",
        "telefono": "123456789",
        "fecha_nacimiento": "1990-01-01",
        "ciudad": "Madrid"
    }
    test_endpoint("/api/usuarios/registro", method="POST", data=usuario_prueba)

    # 3. Probar login
    print("\n3️⃣ Probando login")
    login_data = {
        "username": usuario_prueba["username"],
        "password": usuario_prueba["password"]
    }
    test_endpoint("/api/usuarios/login", method="POST", data=login_data)

    # 4. Probar creación de ruta manual
    print("\n4️⃣ Probando creación de ruta manual")
    ruta_data = {
        "origen": {"lat": 40.4168, "lng": -3.7038, "direccion": "Madrid"},
        "destino": {"lat": 41.3851, "lng": 2.1734, "direccion": "Barcelona"},
        "modo": "drive",
        "nombre": f"Ruta_Test_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "username": usuario_prueba["username"]
    }
    test_endpoint("/api/rutas", method="POST", data=ruta_data)

    # 5. Probar creación de rutas automáticas
    print("\n5️⃣ Probando creación de rutas automáticas")
    rutas_auto_data = {
        "direcciones": ["Madrid", "Barcelona", "Valencia"],
        "cantidad": 2,
        "username": usuario_prueba["username"]
    }
    test_endpoint("/api/rutas/auto", method="POST", data=rutas_auto_data)

    # 6. Probar obtener rutas del usuario
    print("\n6️⃣ Probando obtener rutas del usuario")
    test_endpoint(f"/api/usuarios/{usuario_prueba['username']}/rutas")

    # 7. Probar obtener amigos
    print("\n7️⃣ Probando obtener amigos")
    test_endpoint("/api/usuarios/amigos", params={"username": usuario_prueba["username"]})

    # 8. Probar filtrar rutas
    print("\n8️⃣ Probando filtrar rutas")
    test_endpoint("/api/rutas/filtrar", params={
        "dificultad": "bajo",
        "max_km": 100,
        "max_horas": 2,
        "modo_transporte": "drive"
    })

    # 9. Probar consulta de clima
    print("\n9️⃣ Probando consulta de clima")
    test_endpoint("/api/clima", params={"ciudad": "Madrid"})

    # 10. Probar test de base de datos
    print("\n🔟 Probando test de base de datos")
    test_endpoint("/api/test_db")

    print("\n✨ Pruebas completadas!")

if __name__ == "__main__":
    main() 