import requests
import json
from datetime import datetime
import sqlite3
import os

# URL base de la API
BASE_URL = "https://ra55.pythonanywhere.com"

def test_sqlite_operations():
    print("\n🔍 Iniciando pruebas de SQLite y usuarios...")
    
    # 1. Crear un usuario de prueba
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    usuario_prueba = {
        "nombre": "Test",
        "apellido": "SQLite",
        "email": f"sqlite_test_{timestamp}@test.com",
        "username": f"sqlite_user_{timestamp}",
        "password": "test123",
        "telefono": "987654321",
        "fecha_nacimiento": "1995-01-01",
        "ciudad": "Barcelona"
    }
    
    print("\n1️⃣ Probando registro de usuario en SQLite")
    response = requests.post(f"{BASE_URL}/api/usuarios/registro", json=usuario_prueba)
    print(f"Status Code: {response.status_code}")
    print(f"Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 2. Verificar login del usuario creado
    print("\n2️⃣ Probando login del usuario creado")
    login_data = {
        "username": usuario_prueba["username"],
        "password": usuario_prueba["password"]
    }
    response = requests.post(f"{BASE_URL}/api/usuarios/login", json=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 3. Crear una ruta para el usuario
    print("\n3️⃣ Probando creación de ruta para el usuario")
    ruta_data = {
        "origen": {"lat": 41.3851, "lng": 2.1734, "direccion": "Barcelona"},
        "destino": {"lat": 40.4168, "lng": -3.7038, "direccion": "Madrid"},
        "modo": "drive",
        "nombre": f"Ruta_SQLite_Test_{timestamp}",
        "username": usuario_prueba["username"]
    }
    response = requests.post(f"{BASE_URL}/api/rutas", json=ruta_data)
    print(f"Status Code: {response.status_code}")
    print(f"Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 4. Verificar que la ruta se asoció al usuario
    print("\n4️⃣ Verificando rutas del usuario")
    response = requests.get(f"{BASE_URL}/api/usuarios/{usuario_prueba['username']}/rutas")
    print(f"Status Code: {response.status_code}")
    print(f"Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 5. Crear otro usuario para probar relaciones
    print("\n5️⃣ Creando segundo usuario para probar relaciones")
    usuario2_prueba = {
        "nombre": "Test2",
        "apellido": "SQLite2",
        "email": f"sqlite_test2_{timestamp}@test.com",
        "username": f"sqlite_user2_{timestamp}",
        "password": "test123",
        "telefono": "987654322",
        "fecha_nacimiento": "1995-01-02",
        "ciudad": "Madrid"
    }
    response = requests.post(f"{BASE_URL}/api/usuarios/registro", json=usuario2_prueba)
    print(f"Status Code: {response.status_code}")
    print(f"Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 6. Asociar la misma ruta al segundo usuario
    print("\n6️⃣ Asociando la misma ruta al segundo usuario")
    ruta_data2 = {
        "origen": {"lat": 41.3851, "lng": 2.1734, "direccion": "Barcelona"},
        "destino": {"lat": 40.4168, "lng": -3.7038, "direccion": "Madrid"},
        "modo": "drive",
        "nombre": f"Ruta_SQLite_Test_{timestamp}",
        "username": usuario2_prueba["username"]
    }
    response = requests.post(f"{BASE_URL}/api/rutas", json=ruta_data2)
    print(f"Status Code: {response.status_code}")
    print(f"Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 7. Verificar relaciones de amistad
    print("\n7️⃣ Verificando relaciones de amistad")
    response = requests.get(f"{BASE_URL}/api/usuarios/amigos", params={"username": usuario_prueba["username"]})
    print(f"Status Code: {response.status_code}")
    print(f"Respuesta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    

if __name__ == "__main__":
    test_sqlite_operations() 