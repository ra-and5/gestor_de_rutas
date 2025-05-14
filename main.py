import os
import tkinter as tk
from interfaz import Interfaz
import sqlite3
from PIL import Image, ImageTk
import sys

def get_resource_path(relative_path):
    """Obtiene la ruta absoluta del recurso, funciona para desarrollo y para PyInstaller"""
    try:
        # PyInstaller crea un directorio temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def crear_directorios_necesarios():
    """Crea los directorios necesarios para el funcionamiento de la aplicación."""
    directorios = ['static', 'rutas']
    for directorio in directorios:
        if not os.path.exists(directorio):
            os.makedirs(directorio)

def mostrar_splash(root):
    """Muestra una pantalla de inicio con el logo."""
    # Crear ventana de splash
    splash = tk.Toplevel(root)
    splash.overrideredirect(True)  # Quita la barra de título
    
    # Obtener dimensiones de la pantalla
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Cargar y redimensionar el logo
    try:
        # Usar la función get_resource_path para obtener la ruta correcta del logo
        logo_path = get_resource_path('logo.png')
        logo_img = Image.open(logo_path)
        # Redimensionar manteniendo la proporción
        logo_img.thumbnail((400, 400))
        logo_photo = ImageTk.PhotoImage(logo_img)
        
        # Crear label con el logo
        logo_label = tk.Label(splash, image=logo_photo)
        logo_label.image = logo_photo  # Mantener referencia
        logo_label.pack(padx=20, pady=20)
        
        # Centrar la ventana
        splash_width = logo_img.width + 40
        splash_height = logo_img.height + 40
        x = (screen_width - splash_width) // 2
        y = (screen_height - splash_height) // 2
        splash.geometry(f'{splash_width}x{splash_height}+{x}+{y}')
        
        # Programar el cierre del splash después de 2 segundos
        root.after(2000, splash.destroy)
    except Exception as e:
        print(f"Error al cargar el logo: {e}")
        splash.destroy()

def main():
    """Función principal que inicia la aplicación."""
    # Crear directorios necesarios
    crear_directorios_necesarios()
    
    # Iniciar la interfaz gráfica
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal temporalmente
    
    # Mostrar splash screen
    mostrar_splash(root)
    
    # Configurar la ventana principal
    root.deiconify()  # Mostrar la ventana principal
    root.geometry("800x800")
    app = Interfaz(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    