import os
import tkinter as tk
from interfaz import Interfaz

def crear_directorios_necesarios():
    """Crea los directorios necesarios para el funcionamiento de la aplicación."""
    directorios = ['static', 'rutas']
    for directorio in directorios:
        if not os.path.exists(directorio):
            os.makedirs(directorio)

def main():
    """Función principal que inicia la aplicación."""
    # Crear directorios necesarios
    crear_directorios_necesarios()
    
    # Iniciar la interfaz gráfica
    root = tk.Tk()
    root.geometry("800x600")  # Establece el tamaño inicial de la ventana.
    app = Interfaz(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    