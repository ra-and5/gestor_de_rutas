import requests
import json
from datetime import datetime

# URL base de la API
BASE_URL = "https://ra55.pythonanywhere.com"

def test_database_connection():
    print("\n🔍 Iniciando pruebas de conexión a la base de datos...")
    
    # 1. Probar el endpoint de test de base de datos
    print("\n1️⃣ Probando conexión básica a la base de datos")
    response = requests.get(f"{BASE_URL}/api/test_db")
    print(f"Status Code: {response.status_code}")
    print(f"Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 2. Intentar crear un usuario de prueba
    print("\n2️⃣ Probando creación de usuario en la base de datos")
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    usuario_prueba = {
        "nombre": "Test",
        "apellido": "DB",
        "email": f"db_test_{timestamp}@test.com",
        "username": f"db_user_{timestamp}",
        "password": "test123",
        "telefono": "123456789",
        "fecha_nacimiento": "1990-01-01",
        "ciudad": "Madrid"
    }
    
    response = requests.post(f"{BASE_URL}/api/usuarios/registro", json=usuario_prueba)
    print(f"Status Code: {response.status_code}")
    print(f"Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 3. Intentar hacer login con el usuario creado
    print("\n3️⃣ Probando login con el usuario creado")
    login_data = {
        "username": usuario_prueba["username"],
        "password": usuario_prueba["password"]
    }
    response = requests.post(f"{BASE_URL}/api/usuarios/login", json=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 4. Intentar hacer login con credenciales incorrectas
    print("\n4️⃣ Probando login con credenciales incorrectas")
    login_data_incorrecto = {
        "username": usuario_prueba["username"],
        "password": "password_incorrecto"
    }
    response = requests.post(f"{BASE_URL}/api/usuarios/login", json=login_data_incorrecto)
    print(f"Status Code: {response.status_code}")
    print(f"Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    print("\n✨ Pruebas de conexión a la base de datos completadas!")

if __name__ == "__main__":
    test_database_connection() 