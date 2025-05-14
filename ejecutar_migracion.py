import os
import sys
from migracion_db import migrar_datos

def verificar_ambiente():
    """Verifica que el ambiente esté correctamente configurado."""
    print("🔍 Verificando ambiente...")
    
    # Verificar directorio actual
    directorio_actual = os.getcwd()
    print(f"📁 Directorio actual: {directorio_actual}")
    
    # Verificar permisos
    archivos_necesarios = ['migracion_db.py', 'usuarios.json']
    for archivo in archivos_necesarios:
        if os.path.exists(archivo):
            print(f"✅ Archivo {archivo} encontrado")
            if os.access(archivo, os.R_OK):
                print(f"✅ Permisos de lectura en {archivo}")
            else:
                print(f"❌ Sin permisos de lectura en {archivo}")
        else:
            print(f"❌ Archivo {archivo} no encontrado")
    
    # Verificar directorio de la base de datos
    if os.access(directorio_actual, os.W_OK):
        print("✅ Permisos de escritura en el directorio")
    else:
        print("❌ Sin permisos de escritura en el directorio")

def main():
    """Función principal para ejecutar la migración."""
    print("\n🚀 Iniciando proceso de migración en PythonAnywhere")
    
    # Verificar ambiente
    verificar_ambiente()
    
    # Confirmar con el usuario
    print("\n⚠️ ADVERTENCIA: Este proceso sobrescribirá la base de datos existente.")
    respuesta = input("¿Desea continuar? (s/n): ")
    
    if respuesta.lower() != 's':
        print("❌ Migración cancelada por el usuario")
        sys.exit(0)
    
    # Ejecutar migración
    print("\n🔄 Iniciando migración...")
    if migrar_datos():
        print("\n✨ Migración completada exitosamente")
    else:
        print("\n❌ La migración no se completó correctamente")
        sys.exit(1)

if __name__ == "__main__":
    main() 