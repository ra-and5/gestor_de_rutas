import os
import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser
import json
import requests
from tkinter.font import Font
import time
from PIL import Image, ImageTk 
import sqlite3

class Interfaz:
    """
    Clase principal de la interfaz gráfica para el gestor de rutas.

    Esta clase gestiona la autenticación del usuario, el menú principal,
    la creación de rutas manuales y automáticas, la consulta del clima,
    y la visualización de rutas propias y de amigos.

    Parameters
    ----------
    root : tkinter.Tk
        Ventana principal de la aplicación.
    """
    
    # URL base de la API
    API_URL = "https://ra55.pythonanywhere.com"
    
    # Colores y estilos
    COLOR_PRIMARIO = "#3498db"
    COLOR_SECUNDARIO = "#2ecc71"
    COLOR_FONDO = "#f5f5f5"
    COLOR_TEXTO = "#333333"
    COLOR_BOTON = "#3498db"
    COLOR_BOTON_HOVER = "#2980b9"
    COLOR_ERROR = "#e74c3c"
    COLOR_EXITO = "#2ecc71"
    COLOR_BORDE = "#dcdcdc"
    
    # Fuentes
    FUENTE_TITULO = ("Arial", 18, "bold")
    FUENTE_SUBTITULO = ("Arial", 14, "bold")
    FUENTE_NORMAL = ("Arial", 12)
    FUENTE_PEQUEÑA = ("Arial", 10)

    def __init__(self, root):
        """Inicializa la interfaz y muestra la pantalla de login."""
        self.root = root
        self.root.title("Gestor de Rutas - Login")
        self.root.configure(bg=self.COLOR_FONDO)
        
        # Configurar estilo para ttk
        self.configurar_estilos()
        
        self.usuario = None
        self.datos_usuario = None

        self.pantalla_login()
    
    def configurar_estilos(self):
        """Configura los estilos para los widgets ttk."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Estilo para botones
        style.configure('TButton', 
                        font=self.FUENTE_NORMAL,
                        background=self.COLOR_BOTON,
                        foreground="white",
                        padding=10,
                        relief="flat")
        
        # Estilo para etiquetas
        style.configure('TLabel', 
                        font=self.FUENTE_NORMAL,
                        background=self.COLOR_FONDO,
                        foreground=self.COLOR_TEXTO)
        
        # Estilo para entradas
        style.configure('TEntry', 
                        font=self.FUENTE_NORMAL,
                        fieldbackground="white",
                        padding=5)
        
    def crear_frame_con_borde(self, parent, padding=10):
        """Crea un frame con borde redondeado y sombra."""
        frame = tk.Frame(parent, bg="white", bd=1, relief="solid", padx=padding, pady=padding)
        return frame
        
    def crear_boton_estilizado(self, parent, texto, comando, ancho=20, color=None):
        """Crea un botón con estilo moderno."""
        if color is None:
            color = self.COLOR_BOTON
            
        btn = tk.Button(parent, 
                        text=texto, 
                        command=comando,
                        width=ancho,
                        font=self.FUENTE_NORMAL,
                        bg=color,
                        fg="white",
                        relief="flat",
                        bd=0,
                        padx=10,
                        pady=5)
        
        # Efecto hover
        btn.bind("<Enter>", lambda e: btn.config(bg=self.COLOR_BOTON_HOVER))
        btn.bind("<Leave>", lambda e: btn.config(bg=color))
        
        return btn
        
    def crear_entrada_estilizada(self, parent, ancho=30, mostrar=None):
        """Crea un campo de entrada con estilo moderno."""
        entry = tk.Entry(parent, 
                        width=ancho,
                        font=self.FUENTE_NORMAL,
                        bd=1,
                        relief="solid",
                        show=mostrar)
        return entry
        
    def crear_etiqueta_estilizada(self, parent, texto, tamaño=None):
        """Crea una etiqueta con estilo moderno."""
        if tamaño is None:
            fuente = self.FUENTE_NORMAL
        elif tamaño == "titulo":
            fuente = self.FUENTE_TITULO
        elif tamaño == "subtitulo":
            fuente = self.FUENTE_SUBTITULO
        else:
            fuente = self.FUENTE_PEQUEÑA
            
        label = tk.Label(parent, 
                        text=texto,
                        font=fuente,
                        bg=self.COLOR_FONDO,
                        fg=self.COLOR_TEXTO)
        return label
        
    def hacer_peticion(self, endpoint, metodo="GET", datos=None, params=None):
        """
        Realiza una petición a la API.
        
        Parameters
        ----------
        endpoint : str
            Ruta del endpoint a consultar.
        metodo : str, optional
            Método HTTP a utilizar (GET, POST, etc.)
        datos : dict, optional
            Datos a enviar en formato JSON.
        params : dict, optional
            Parámetros de consulta.
            
        Returns
        -------
        dict
            Respuesta de la API en formato JSON.
        """
        url = f"{self.API_URL}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if metodo == "GET":
                respuesta = requests.get(url, params=params, headers=headers, timeout=10)
            elif metodo == "POST":
                respuesta = requests.post(url, json=datos, headers=headers, timeout=10)
            else:
                raise ValueError(f"Método HTTP no soportado: {metodo}")
                
            if respuesta.status_code >= 400:
                error_msg = respuesta.json().get("message", "Error desconocido")
                raise Exception(f"Error en la API (código {respuesta.status_code}): {error_msg}")
                
            return respuesta.json()
        except requests.RequestException as e:
            raise Exception(f"Error de conexión: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("Error al procesar la respuesta del servidor")
        except Exception as e:
            raise Exception(f"Error inesperado: {str(e)}")

    def pantalla_login(self):
        """Muestra la pantalla de inicio de sesión con campos de usuario y contraseña."""
        self.limpiar_pantalla()
        self.root.geometry("400x500")
        self.root.configure(bg="#f0f4f8")
        # Logo
        try:
            logo_image = Image.open("logo.png")
            logo_image = logo_image.resize((150, 150))
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            tk.Label(self.root, image=self.logo_photo, bg="#f0f4f8").pack(pady=10)
        except Exception as e:
            print("⚠️ No se pudo cargar el logo:", e)
        tk.Label(self.root, text="🔐 Iniciar sesión", font=("Arial", 16, "bold"), bg="#f0f4f8", fg="#333333").pack(pady=10)
        tk.Label(self.root, text="👤 Usuario:", bg="#f0f4f8").pack()
        self.entry_usuario = tk.Entry(self.root)
        self.entry_usuario.pack(pady=5)
        tk.Label(self.root, text="🔒 Contraseña:", bg="#f0f4f8").pack()
        self.entry_password = tk.Entry(self.root, show="*")
        self.entry_password.pack(pady=5)
        # Frame para los botones
        frame_botones = tk.Frame(self.root, bg="#f0f4f8")
        frame_botones.pack(pady=20)
        self.crear_boton_estilizado(frame_botones, "🚀 Entrar", self.verificar_login, ancho=30).pack(pady=5)
        # Botón de registro más visible pero no tan llamativo
        def on_enter(e):
            btn_registro.config(bg="#ffa500")
        def on_leave(e):
            btn_registro.config(bg="#ffcc80")
        btn_registro = tk.Button(
            frame_botones,
            text="📝 ¿No tienes cuenta? Regístrate",
            command=self.abrir_ventana_registro,
            width=30,
            font=("Arial", 13, "bold"),
            bg="#ffcc80",  # Naranja medio opaco
            fg="#333333",
            activebackground="#ffa500",
            relief="raised",
            bd=2,
            cursor="hand2",
            pady=8
        )
        btn_registro.bind("<Enter>", on_enter)
        btn_registro.bind("<Leave>", on_leave)
        btn_registro.pack(pady=5)

    def verificar_login(self):
        """
        Verifica las credenciales ingresadas por el usuario a través de la API.

        Si las credenciales son válidas, redirige a la pantalla principal.
        Si no, muestra un mensaje de error.
        """
        username = self.entry_usuario.get().strip()
        password = self.entry_password.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Por favor, complete todos los campos.")
            return

        try:
            datos = {
                "username": username,
                "password": password
            }
            respuesta = self.hacer_peticion("/api/usuarios/login", metodo="POST", datos=datos)
            
            if respuesta["status"] == "success":
                self.datos_usuario = respuesta["data"]
                self.usuario = self.datos_usuario["username"]
                messagebox.showinfo("Bienvenido", f"Hola {self.datos_usuario['nombre']}, ¡has iniciado sesión!")
                self.pantalla_principal()
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def abrir_ventana_registro(self):
        """Muestra el formulario de registro para nuevos usuarios."""
        self.limpiar_pantalla()
        self.root.configure(bg="#f0f4f8")
        tk.Label(self.root, text="🆕 Registro de Usuario", font=("Arial", 18, "bold"), bg="#f0f4f8").pack(pady=20)
        campos = ["Nombre", "Apellido", "Email", "Usuario", "Teléfono", "Fecha de nacimiento (YYYY-MM-DD)", "Ciudad", "Contraseña"]
        self.entries_registro = []
        for campo in campos:
            tk.Label(self.root, text=f"{campo}:", bg="#f0f4f8").pack()
            entry = tk.Entry(self.root, show="*" if campo == "Contraseña" else None)
            entry.pack()
            self.entries_registro.append(entry)
        tk.Button(self.root, text="✅ Registrar", width=20, command=self.registrar_usuario, bg="#007acc", fg="white", font=("Arial", 12, "bold"), height=2).pack(pady=15)
        tk.Button(self.root, text="↩️ Volver", command=self.pantalla_login, bg="#e0e0e0", fg="#333333", font=("Arial", 11), height=2, width=20).pack()

    def registrar_usuario(self):
        """
        Registra al usuario con los datos ingresados en el formulario a través de la API.

        Si los campos están completos y el nombre de usuario no existe, se registra correctamente.
        """
        datos = [e.get().strip() for e in self.entries_registro]

        if not all(datos):
            messagebox.showerror("Error", "Por favor, complete todos los campos.")
            return

        nombre, apellido, email, username, telefono, fecha_nacimiento, ciudad, password = datos

        try:
            datos_registro = {
                "nombre": nombre,
                "apellido": apellido,
                "email": email,
                "username": username,
                "telefono": telefono,
                "fecha_nacimiento": fecha_nacimiento,
                "ciudad": ciudad,
                "password": password
            }
            
            respuesta = self.hacer_peticion("/api/usuarios/registro", metodo="POST", datos=datos_registro)
            
            if respuesta["status"] == "success":
                messagebox.showinfo("Registro exitoso", "¡Te has registrado correctamente!")
                self.pantalla_login()
            else:
                messagebox.showerror("Error", respuesta.get("message", "Error desconocido durante el registro"))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def pantalla_principal(self):
        """Muestra el menú principal con botones para cada funcionalidad del sistema."""
        self.limpiar_pantalla()
        self.root.geometry("700x800")
        self.root.title(f"🏠 Bienvenido {self.datos_usuario['nombre']}")
        self.root.configure(bg="#f0f4f8")
        tk.Label(self.root, text=f"👋 ¡Hola, {self.datos_usuario['nombre']}!", font=("Arial", 16, "bold"), bg="#f0f4f8", fg="#333333").pack(pady=20)
        botones = [
            ("📍 Ver mis rutas", self.ver_rutas),
            ("👥 Ver mis amigos", self.ver_amigos),
            ("☁️ Consultar el clima", self.ver_clima),
            ("🛠 Crear ruta manual", self.pantalla_crear_ruta_manual),
            ("⚙️ Crear rutas automáticas", self.pantalla_crear_ruta_auto),
            ("🔍 Ver todas las rutas", self.ver_todas_las_rutas),
            ("🔎 Buscar usuarios", self.buscar_usuarios),
            ("✏️ Editar perfil", self.editar_perfil),
            ("🗑️ Borrar cuenta", self.borrar_cuenta),
            ("🔒 Cerrar sesión", self.cerrar_sesion)
        ]
        for texto, comando in botones:
            color = "#e74c3c" if "Cerrar sesión" in texto or "Borrar" in texto else ("#007acc" if "Ver" in texto or "Crear" in texto or "Buscar" in texto or "Editar" in texto else "#e0e0e0")
            fg = "white" if color in ["#007acc", "#e74c3c"] else "#333333"
            tk.Button(self.root, text=texto, command=comando, bg=color, fg=fg, activebackground="#005f99", font=("Arial", 12, "bold"), height=2, width=35).pack(pady=7)

    def pantalla_crear_ruta_manual(self):
        """Muestra un formulario para crear rutas manualmente con campos de entrada."""
        self.limpiar_pantalla()
        self.root.geometry("900x900")
        frame_principal = self.crear_frame_con_borde(self.root, padding=20)
        frame_principal.pack(expand=True, fill="both", padx=30, pady=30)
        self.crear_etiqueta_estilizada(frame_principal, "Crear Ruta Manual", "titulo").pack(pady=(0, 20), anchor="center")
        frame_campos = tk.Frame(frame_principal, bg="white")
        frame_campos.pack(fill="x", pady=10)
        labels = [
            "Origen:",
            "Puntos intermedios (separados por comas):",
            "Destino:",
            "Modo de transporte (walk/bike/drive):",
            "Nombre de la ruta (opcional):"
        ]
        self.entries_ruta_manual = []
        for texto in labels:
            self.crear_etiqueta_estilizada(frame_campos, texto).pack(anchor="w")
            entry = self.crear_entrada_estilizada(frame_campos, ancho=50)
            entry.pack(fill="x", pady=(0, 10))
            self.entries_ruta_manual.append(entry)
        self.crear_boton_estilizado(frame_principal, "Crear Ruta", self.crear_ruta_manual, ancho=20).pack(pady=10, anchor="center")
        self.crear_boton_estilizado(frame_principal, "Volver", self.pantalla_principal, ancho=20, color=self.COLOR_SECUNDARIO).pack(pady=5, anchor="center")

    def crear_ruta_manual(self):
        """Recoge los datos del formulario y crea una ruta manual."""
        try:
            origen = self.entries_ruta_manual[0].get().strip()
            intermedios_texto = self.entries_ruta_manual[1].get().strip()
            intermedios = [p.strip() for p in intermedios_texto.split(",") if p.strip()] if intermedios_texto else []
            destino = self.entries_ruta_manual[2].get().strip()
            modo = self.entries_ruta_manual[3].get().strip().lower()
            nombre = self.entries_ruta_manual[4].get().strip() or f"ruta_manual_{int(time.time())}"

            # Validación de campos obligatorios
            if not (origen and destino):
                messagebox.showerror("Error", "Origen y destino son obligatorios.")
                return

            # Validación del modo de transporte
            modos_validos = ["walk", "bike", "drive"]
            if not modo:
                modo = "walk"  # valor por defecto
            elif modo not in modos_validos:
                messagebox.showerror("Error", "Modo de transporte debe ser 'walk', 'bike' o 'drive'.")
                return

            # Preparar datos para la API
            datos = {
                "origen": {"direccion": origen},
                "destino": {"direccion": destino},
                "puntos_intermedios": [{"direccion": p} for p in intermedios],
                "modo": modo,
                "nombre": nombre,
                "username": self.usuario
            }
            
            respuesta = self.hacer_peticion("/api/rutas", metodo="POST", datos=datos)
            
            if respuesta["status"] == "success":
                messagebox.showinfo("Éxito", "Ruta creada correctamente")
                self.pantalla_principal()
            else:
                messagebox.showerror("Error", respuesta.get("message", "Error al crear la ruta"))
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear la ruta: {str(e)}")

    def pantalla_crear_ruta_auto(self):
        """Muestra un formulario para crear múltiples rutas automáticas."""
        self.limpiar_pantalla()
        self.root.geometry("900x900")
        frame_principal = self.crear_frame_con_borde(self.root, padding=20)
        frame_principal.pack(expand=True, fill="both", padx=30, pady=30)
        self.crear_etiqueta_estilizada(frame_principal, "Crear Rutas Automáticas", "titulo").pack(pady=(0, 20), anchor="center")
        frame_campos = tk.Frame(frame_principal, bg="white")
        frame_campos.pack(fill="x", pady=10)
        self.crear_etiqueta_estilizada(frame_campos, "Direcciones (separadas por comas):").pack(anchor="w")
        self.entry_direcciones_auto = self.crear_entrada_estilizada(frame_campos, ancho=60)
        self.entry_direcciones_auto.pack(fill="x", pady=(0, 10))
        self.crear_etiqueta_estilizada(frame_campos, "Cantidad de rutas a generar:").pack(anchor="w")
        self.entry_cantidad_auto = self.crear_entrada_estilizada(frame_campos, ancho=10)
        self.entry_cantidad_auto.insert(0, "5")
        self.entry_cantidad_auto.pack(fill="x", pady=(0, 20))
        self.crear_boton_estilizado(frame_principal, "Generar Rutas", self.crear_rutas_automaticas, ancho=20).pack(pady=10, anchor="center")
        self.crear_boton_estilizado(frame_principal, "Volver", self.pantalla_principal, ancho=20, color=self.COLOR_SECUNDARIO).pack(pady=5, anchor="center")

    def crear_rutas_automaticas(self):
        """Genera rutas automáticas basadas en direcciones introducidas por el usuario."""
        direcciones_texto = self.entry_direcciones_auto.get().strip()
        direcciones = [d.strip() for d in direcciones_texto.split(",") if d.strip()]
        cantidad_texto = self.entry_cantidad_auto.get().strip()

        try:
            cantidad = int(cantidad_texto)
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero.")
            return

        if len(direcciones) < 2:
            messagebox.showerror("Error", "Introduce al menos dos direcciones válidas separadas por comas.")
            return

        try:
            datos = {
                "direcciones": direcciones,
                "cantidad": cantidad,
                "username": self.usuario
            }
            
            respuesta = self.hacer_peticion("/api/rutas/auto", metodo="POST", datos=datos)
            
            if respuesta["status"] == "success":
                messagebox.showinfo("Éxito", "Rutas automáticas creadas correctamente")
                self.pantalla_principal()
            else:
                messagebox.showerror("Error", respuesta.get("message", "Error al crear las rutas automáticas"))
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear las rutas automáticas: {str(e)}")

    def ver_rutas(self):
        """Muestra todas las rutas asociadas al usuario con opciones para visualizar archivos."""
        self.limpiar_pantalla()
        frame_principal = tk.Frame(self.root, bg="white")
        frame_principal.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        self.crear_etiqueta_estilizada(frame_principal, "Mis Rutas", "titulo").pack(pady=10)

        # Frame scrollable para las rutas
        canvas = tk.Canvas(frame_principal, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(frame_principal, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        try:
            # Obtener rutas desde la API
            respuesta = self.hacer_peticion(f"/api/usuarios/{self.usuario}/rutas")
            if respuesta["status"] == "success":
                rutas = respuesta.get("data", [])
                if rutas:
                    for ruta in rutas:
                        # Crear frame para cada ruta
                        frame_ruta = self.crear_frame_con_borde(scrollable_frame, padding=12)
                        frame_ruta.pack(fill="x", pady=8, padx=8)

                        # Acceso seguro a origen y destino
                        origen = ruta.get('origen', '')
                        if isinstance(origen, dict):
                            origen = origen.get('direccion', '')
                        destino = ruta.get('destino', '')
                        if isinstance(destino, dict):
                            destino = destino.get('direccion', '')
                        # Acceso seguro a puntos intermedios
                        puntos = []
                        for p in ruta.get('puntos_intermedios', []):
                            if isinstance(p, dict):
                                puntos.append(p.get('direccion', ''))
                            else:
                                puntos.append(p)
                        puntos_str = ', '.join(puntos)

                        info_ruta = f"🛣️ {ruta.get('nombre','')}\n"
                        info_ruta += f"📍 Origen: {origen}\n"
                        info_ruta += f"🎯 Destino: {destino}\n"
                        info_ruta += f"🛤️ Intermedios: {puntos_str}\n" if puntos_str else ''
                        info_ruta += f"🚶 Modo: {ruta.get('modo','') or ruta.get('modo_transporte','')}\n"
                        info_ruta += f"📏 Distancia: {ruta.get('distancia_km','N/A')} km\n"
                        info_ruta += f"⏱️ Duración: {ruta.get('duracion_horas','N/A')} h"

                        label_info = tk.Label(
                            frame_ruta, 
                            text=info_ruta, 
                            font=self.FUENTE_NORMAL, 
                            bg="white", 
                            fg=self.COLOR_TEXTO, 
                            anchor="w", 
                            justify="left", 
                            width=60, 
                            wraplength=600
                        )
                        label_info.pack(side="left", padx=10, fill="x", expand=True)

                        # Frame para botones
                        btn_frame = tk.Frame(frame_ruta, bg="white")
                        btn_frame.pack(side="right", padx=5, anchor="e")

                        # Obtener nombre de la ruta
                        nombre_ruta = ruta.get('nombre','')

                        # URLs remotas
                        pdf_url = f"{self.API_URL}/static/{nombre_ruta}.pdf"
                        html_url = f"{self.API_URL}/static/rutas_{nombre_ruta}.html"

                        # Estilo de botones
                        style_btn = {
                            'bg': "#3498db",
                            'fg': "white",
                            'activebackground': "#217dbb",
                            'font': ("Arial", 10, "bold"),
                            'width': 14,
                            'relief': "groove",
                            'bd': 0,
                            'highlightthickness': 0,
                            'cursor': "hand2",
                            'padx': 6,
                            'pady': 4
                        }

                        # Botón PDF (siempre visible)
                        btn_pdf = tk.Button(
                            btn_frame, 
                            text="📄 Ver PDF", 
                            command=lambda p=pdf_url: webbrowser.open(p), 
                            **style_btn
                        )
                        btn_pdf.pack(side="top", pady=3, padx=2, fill="x")

                        # Botón HTML (siempre visible)
                        style_btn_html = style_btn.copy()
                        style_btn_html['bg'] = "#2ecc71"
                        style_btn_html['activebackground'] = "#27ae60"

                        btn_html = tk.Button(
                            btn_frame, 
                            text="🌐 Ver HTML", 
                            command=lambda h=html_url: webbrowser.open(h), 
                            **style_btn_html
                        )
                        btn_html.pack(side="top", pady=3, padx=2, fill="x")
                else:
                    self.crear_etiqueta_estilizada(scrollable_frame, "No tienes rutas asignadas aún.").pack(pady=20)
            else:
                messagebox.showerror("Error", respuesta.get("message", "No se pudieron obtener las rutas"))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar las rutas: {str(e)}")

        self.crear_boton_estilizado(frame_principal, "Volver", self.pantalla_principal, ancho=20, color=self.COLOR_SECUNDARIO).pack(pady=10, anchor="center")

    def ver_amigos(self):
        """Muestra los amigos del usuario y las rutas en común con ellos."""
        self.limpiar_pantalla()
        self.root.geometry("900x900")
        frame_principal = self.crear_frame_con_borde(self.root, padding=20)
        frame_principal.pack(expand=True, fill="both", padx=30, pady=30)
        self.crear_etiqueta_estilizada(frame_principal, "Rutas en común con amigos", "titulo").pack(pady=(0, 20), anchor="center")
        frame_amigos = tk.Frame(frame_principal, bg="white")
        frame_amigos.pack(fill="both", expand=True, pady=10)
        canvas = tk.Canvas(frame_amigos, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_amigos, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        try:
            respuesta = self.hacer_peticion(f"/api/usuarios/amigos?username={self.usuario}")
            if respuesta["status"] == "success":
                amigos_data = respuesta["data"]
                if amigos_data:
                    for amigo, info in amigos_data.items():
                        frame_amigo = tk.Frame(scrollable_frame, bg="#f8fafd", bd=2, relief="ridge", padx=12, pady=10, highlightbackground="#dcdcdc", highlightthickness=1)
                        frame_amigo.pack(fill="x", pady=10, padx=12)
                        tk.Label(frame_amigo, text=f"Amigo: {amigo}", font=("Arial", 13, "bold"), bg="#f8fafd", fg="#222", anchor="w", justify="left", width=60, wraplength=700).pack(anchor="w", pady=2, fill="x", expand=True)
                        rutas_comunes = info.get("rutas_comunes", [])
                        if rutas_comunes:
                            for ruta in rutas_comunes:
                                frame_ruta = tk.Frame(frame_amigo, bg="#f8fafd")
                                frame_ruta.pack(fill="x", pady=4)
                                tk.Label(frame_ruta, text=f"Ruta en común: {ruta}", bg="#f8fafd", font=("Arial", 11), anchor="w", justify="left", width=50, wraplength=600).pack(side="left", padx=10, fill="x", expand=True)
                                btn_frame = tk.Frame(frame_ruta, bg="#f8fafd")
                                btn_frame.pack(side="left", padx=16, anchor="e")
                                pdf_url = f"{self.API_URL}/static/{ruta}.pdf"
                                style_btn = {
                                    'bg': "#3498db",
                                    'fg': "white",
                                    'activebackground': "#217dbb",
                                    'font': ("Arial", 10, "bold"),
                                    'width': 14,
                                    'relief': "groove",
                                    'bd': 0,
                                    'highlightthickness': 0,
                                    'cursor': "hand2",
                                    'padx': 6,
                                    'pady': 4
                                }
                                btn_pdf = tk.Button(btn_frame, text="📄 Ver PDF", command=lambda p=pdf_url: webbrowser.open(p), **style_btn)
                                btn_pdf.pack(side="top", pady=3, padx=2, fill="x")
                        else:
                            tk.Label(frame_amigo, text="No tienen rutas en común.", bg="#f8fafd", font=("Arial", 10, "italic"), fg="#888", anchor="w", justify="left", width=50, wraplength=600).pack(pady=5, fill="x", expand=True)
                else:
                    self.crear_etiqueta_estilizada(scrollable_frame, "No tienes amigos registrados o rutas en común.").pack(pady=20)
            else:
                messagebox.showerror("Error", respuesta.get("message", "No se pudieron obtener los amigos"))
        except Exception as e:
            import traceback
            error_detalle = traceback.format_exc()
            messagebox.showerror("Error", f"No se pudieron cargar los amigos: {str(e)}\n\nDetalles: {error_detalle}")
        self.crear_boton_estilizado(frame_principal, "Volver", self.pantalla_principal, ancho=20, color=self.COLOR_SECUNDARIO).pack(pady=10, anchor="center")

    def ver_clima(self):
        """Muestra un formulario para consultar el clima en una ciudad específica."""
        self.limpiar_pantalla()
        self.root.geometry("900x900")
        frame_principal = self.crear_frame_con_borde(self.root, padding=20)
        frame_principal.pack(expand=True, fill="both", padx=30, pady=30)
        self.crear_etiqueta_estilizada(frame_principal, "Consultar el Clima", "titulo").pack(pady=(0, 20), anchor="center")
        frame_campos = tk.Frame(frame_principal, bg="white")
        frame_campos.pack(fill="x", pady=10)
        self.crear_etiqueta_estilizada(frame_campos, "Ingresa la ciudad para consultar el clima").pack(anchor="w")
        self.entry_ciudad_clima = self.crear_entrada_estilizada(frame_campos)
        self.entry_ciudad_clima.pack(fill="x", pady=(0, 20))
        self.crear_boton_estilizado(frame_principal, "Consultar Clima", self.consultar_clima, ancho=20).pack(pady=10, anchor="center")
        self.crear_boton_estilizado(frame_principal, "Volver", self.pantalla_principal, ancho=20, color=self.COLOR_SECUNDARIO).pack(pady=5, anchor="center")

    def consultar_clima(self):
        """Consulta el clima actual para la ciudad ingresada por el usuario a través de la API."""
        ciudad = self.entry_ciudad_clima.get().strip()

        if not ciudad:
            messagebox.showerror("Error", "Por favor, ingresa el nombre de una ciudad.")
            return

        try:
            respuesta = self.hacer_peticion("/api/clima", params={"ciudad": ciudad})
            
            if respuesta["status"] == "success":
                clima = respuesta["data"]
                clima_info = f"Ciudad: {clima.get('ciudad', 'N/A')}\n" \
                             f"Temperatura: {clima.get('temperatura', 'N/A')}°C\n" \
                             f"Humedad: {clima.get('humedad', 'N/A')}%\n" \
                             f"Descripción: {clima.get('descripcion', 'N/A')}\n" \
                             f"Viento: {clima.get('viento', 'N/A')} m/s\n" \
                             f"Fecha: {clima.get('fecha', 'N/A')}"
                messagebox.showinfo("Clima", clima_info)
            else:
                messagebox.showerror("Error", respuesta.get("message", "No se pudo obtener el clima"))
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener el clima: {str(e)}")

    def ver_todas_las_rutas(self):
        """
        Muestra todas las rutas del sistema con filtros aplicables.
        Permite filtrar por dificultad, distancia, duración y modo de transporte.
        Las rutas se muestran en un panel scrollable con botones para ver PDF y HTML.
        """
        self.limpiar_pantalla()
        self.root.geometry("900x900")
        frame_principal = self.crear_frame_con_borde(self.root, padding=20)
        frame_principal.pack(expand=True, fill="both", padx=30, pady=30)
        self.crear_etiqueta_estilizada(frame_principal, "🧭 Filtrar Rutas del Sistema", "titulo").pack(pady=(0, 20), anchor="center")
        filtro_frame = self.crear_frame_con_borde(frame_principal, padding=15)
        filtro_frame.pack(fill="x", pady=10)
        self.crear_etiqueta_estilizada(filtro_frame, "Dificultad (bajo, medio, alto):").grid(row=0, column=0, sticky="w", pady=5)
        self.filtro_dificultad = self.crear_entrada_estilizada(filtro_frame, ancho=20)
        self.filtro_dificultad.grid(row=0, column=1, padx=10, pady=5)
        self.crear_etiqueta_estilizada(filtro_frame, "Distancia máx (km):").grid(row=1, column=0, sticky="w", pady=5)
        self.filtro_distancia = self.crear_entrada_estilizada(filtro_frame, ancho=20)
        self.filtro_distancia.grid(row=1, column=1, padx=10, pady=5)
        self.crear_etiqueta_estilizada(filtro_frame, "Duración máx (h):").grid(row=2, column=0, sticky="w", pady=5)
        self.filtro_duracion = self.crear_entrada_estilizada(filtro_frame, ancho=20)
        self.filtro_duracion.grid(row=2, column=1, padx=10, pady=5)
        self.crear_etiqueta_estilizada(filtro_frame, "Medio de transporte (walk, bike, drive):").grid(row=3, column=0, sticky="w", pady=5)
        self.filtro_modo = self.crear_entrada_estilizada(filtro_frame, ancho=20)
        self.filtro_modo.grid(row=3, column=1, padx=10, pady=5)
        control_frame = tk.Frame(frame_principal, bg="white")
        control_frame.pack(pady=10)
        self.crear_boton_estilizado(control_frame, "Aplicar filtros", lambda: self.aplicar_filtros_rutas(), ancho=15).pack(side="left", padx=10)
        self.crear_boton_estilizado(control_frame, "Volver", self.pantalla_principal, ancho=15, color=self.COLOR_SECUNDARIO).pack(side="left", padx=10)
        frame_rutas = tk.Frame(frame_principal, bg="white")
        frame_rutas.pack(fill="both", expand=True, pady=10)
        canvas = tk.Canvas(frame_rutas, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_rutas, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg="white")
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.aplicar_filtros_rutas()

    def aplicar_filtros_rutas(self):
        """
        Aplica los filtros introducidos por el usuario a las rutas a través de la API.

        Usa dificultad, distancia, duración y modo de transporte como filtros.
        """
        dificultad = self.filtro_dificultad.get().strip().lower()
        distancia = self.filtro_distancia.get().strip()
        duracion = self.filtro_duracion.get().strip()
        modo = self.filtro_modo.get().strip().lower()

        # Limpiar el panel de rutas
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        try:
            params = {}
            if dificultad:
                params["dificultad"] = dificultad
            if distancia:
                params["max_km"] = float(distancia)
            if duracion:
                params["max_horas"] = float(duracion)
            if modo:
                params["modo_transporte"] = modo
                
            respuesta = self.hacer_peticion("/api/rutas/filtrar", params=params)
            
            if respuesta["status"] == "success":
                self.mostrar_rutas(respuesta["data"])
            else:
                messagebox.showerror("Error", respuesta.get("message", "No se pudieron filtrar las rutas"))
        except ValueError as e:
            messagebox.showerror("Error de formato", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las rutas: {str(e)}")

    def mostrar_rutas(self, rutas):
        """
        Muestra visualmente las rutas en el panel scrollable.

        Parameters
        ----------
        rutas : list
            Lista de rutas en formato diccionario.
        """
        if not rutas:
            self.crear_etiqueta_estilizada(self.scroll_frame, "No se encontraron rutas con los filtros aplicados.").pack(pady=10)
            return

        for r in rutas:
            frame = self.crear_frame_con_borde(self.scroll_frame, padding=10)
            frame.pack(padx=10, pady=5, fill="x")

            texto = f"📍 {r.get('nombre', 'Sin nombre')} | {r.get('distancia', 'N/A')} | {r.get('duracion', 'N/A')} | Dificultad: {r.get('dificultad', 'N/A')}\n{r.get('origen', 'N/A')} → {r.get('destino', 'N/A')} ({r.get('modo_transporte', 'N/A')})"
            self.crear_etiqueta_estilizada(frame, texto, "pequeña").pack(anchor="w")

            # Botones de exportación
            nombre_archivo = r.get("nombre", "")
            btn_frame = tk.Frame(frame, bg="white")
            btn_frame.pack(anchor="e", pady=5)

            pdf_url = f"{self.API_URL}/static/{nombre_archivo}.pdf"
            html_url = f"{self.API_URL}/static/rutas_{nombre_archivo}.html"

            self.crear_boton_estilizado(btn_frame, "📄 Ver PDF", lambda p=pdf_url: webbrowser.open(p), ancho=10).pack(side="left", padx=5)
            self.crear_boton_estilizado(btn_frame, "🌐 Ver HTML", lambda h=html_url: webbrowser.open(h), ancho=10).pack(side="left", padx=5)

    def cerrar_sesion(self):
        """Cierra la sesión del usuario actual y vuelve al login."""
        self.usuario = None
        self.datos_usuario = None
        self.root.title("Gestor de Rutas - Login")
        self.pantalla_login()

    def limpiar_pantalla(self):
        """Elimina todos los elementos visibles de la ventana actual."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def buscar_usuarios(self):
        """
        Permite buscar usuarios por nombre de usuario y ver sus rutas.
        Muestra una interfaz en la que se puede introducir un nombre de usuario.
        """
        self.limpiar_pantalla()
        self.root.geometry("900x900")
        frame_principal = self.crear_frame_con_borde(self.root, padding=20)
        frame_principal.pack(expand=True, fill="both", padx=30, pady=30)
        self.crear_etiqueta_estilizada(frame_principal, "🔎 Buscar Usuarios", "titulo").pack(pady=(0, 20), anchor="center")
        frame_busqueda = self.crear_frame_con_borde(frame_principal, padding=15)
        frame_busqueda.pack(fill="x", pady=10)
        self.crear_etiqueta_estilizada(frame_busqueda, "Nombre de usuario:").pack(anchor="w")
        entry = self.crear_entrada_estilizada(frame_busqueda, ancho=30)
        entry.pack(fill="x", pady=5)
        self.frame_resultados = self.crear_frame_con_borde(frame_principal, padding=15)
        self.frame_resultados.pack(fill="both", expand=True, pady=10)
        def buscar():
            for widget in self.frame_resultados.winfo_children():
                widget.destroy()
            nombre = entry.get().strip()
            if not nombre:
                messagebox.showerror("Error", "Introduce un nombre de usuario.")
                return
            try:
                respuesta = self.hacer_peticion("/api/usuarios/buscar", params={"nombre": nombre})
                if respuesta["status"] == "success":
                    usuarios = respuesta.get("resultados", [])
                    if not usuarios:
                        self.crear_etiqueta_estilizada(self.frame_resultados, "🙁 No se encontraron usuarios.").pack()
                    else:
                        self.crear_etiqueta_estilizada(self.frame_resultados, "👥 Coincidencias:").pack()
                        for username in usuarios:
                            usuario_frame = self.crear_frame_con_borde(self.frame_resultados, padding=10)
                            usuario_frame.pack(fill="x", pady=5)
                            self.crear_etiqueta_estilizada(usuario_frame, f"🔹 {username}").pack(side="left")
                            def ver_rutas_pdf_html(user=username):
                                try:
                                    respuesta = self.hacer_peticion(f"/api/usuarios/{user}/rutas")
                                    if respuesta["status"] == "success":
                                        rutas = respuesta.get("data", [])
                                        if not rutas:
                                            messagebox.showinfo("ℹ️", f"El usuario {user} no tiene rutas.")
                                            return
                                        rutas_win = tk.Toplevel(self.root)
                                        rutas_win.title(f"Rutas de {user}")
                                        rutas_win.geometry("600x700")
                                        for ruta in rutas:
                                            ruta_frame = self.crear_frame_con_borde(rutas_win, padding=10)
                                            ruta_frame.pack(fill="x", pady=5)
                                            info = f"🛣️ {ruta.get('nombre', 'Sin nombre')}\n"
                                            info += f"📏 Distancia: {ruta.get('distancia_km', 'N/A')} km\n"
                                            info += f"⏱️ Duración: {ruta.get('duracion_horas', 'N/A')} h"
                                            tk.Label(ruta_frame, text=info, anchor="w", justify="left", width=50, wraplength=500).pack(anchor="w", fill="x", expand=True)
                                            botonera = tk.Frame(ruta_frame)
                                            botonera.pack(pady=5)
                                            nombre = ruta.get("nombre", "")
                                            pdf_path = f"{self.API_URL}/static/{nombre}.pdf"
                                            html_path = f"{self.API_URL}/static/rutas_{nombre}.html"
                                            tk.Button(botonera, text="📄 PDF", command=lambda p=pdf_path: webbrowser.open(p)).pack(side="left", padx=5)
                                            tk.Button(botonera, text="🌐 HTML", command=lambda h=html_path: webbrowser.open(h)).pack(side="left", padx=5)
                                except Exception as e:
                                    messagebox.showerror("Error", f"Error al cargar las rutas: {str(e)}")
                            tk.Button(usuario_frame, text="👁️ Ver rutas", command=lambda u=username: ver_rutas_pdf_html(u)).pack(side="right")
                else:
                    messagebox.showerror("Error", respuesta.get("message", "Error al buscar usuarios"))
            except Exception as e:
                messagebox.showerror("Error", f"Error al buscar usuarios: {str(e)}")
        self.crear_boton_estilizado(frame_busqueda, "🔍 Buscar", buscar).pack(pady=10, anchor="center")
        self.crear_boton_estilizado(frame_principal, "↩️ Volver", self.pantalla_principal).pack(pady=5, anchor="center")

    def editar_perfil(self):
        """
        Permite al usuario editar su información de perfil.
        """
        self.limpiar_pantalla()
        self.root.geometry("900x900")
        frame_principal = self.crear_frame_con_borde(self.root, padding=20)
        frame_principal.pack(expand=True, fill="both", padx=30, pady=30)
        self.crear_etiqueta_estilizada(frame_principal, "✏️ Editar Perfil", "titulo").pack(pady=(0, 20), anchor="center")
        frame_campos = self.crear_frame_con_borde(frame_principal, padding=15)
        frame_campos.pack(fill="x", pady=10)
        campos = [
            ("Nombre", "nombre"),
            ("Apellido", "apellido"),
            ("Email", "email"),
            ("Teléfono", "telefono"),
            ("Fecha de nacimiento (YYYY-MM-DD)", "fecha_nacimiento"),
            ("Ciudad", "ciudad")
        ]
        self.entries_edicion = {}
        for label, key in campos:
            self.crear_etiqueta_estilizada(frame_campos, f"{label}:").pack(anchor="w")
            entry = self.crear_entrada_estilizada(frame_campos, ancho=30)
            entry.insert(0, self.datos_usuario.get(key, ""))
            entry.pack(fill="x", pady=5)
            self.entries_edicion[key] = entry
        def guardar_cambios():
            datos = {key: entry.get().strip() for key, entry in self.entries_edicion.items()}
            datos["username"] = self.usuario
            try:
                respuesta = self.hacer_peticion("/api/usuarios/editar", metodo="POST", datos=datos)
                if respuesta["status"] == "success":
                    self.datos_usuario.update(datos)
                    messagebox.showinfo("Éxito", "Perfil actualizado correctamente")
                    self.pantalla_principal()
                else:
                    messagebox.showerror("Error", respuesta.get("message", "Error al actualizar el perfil"))
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar el perfil: {str(e)}")
        self.crear_boton_estilizado(frame_principal, "💾 Guardar cambios", guardar_cambios).pack(pady=10, anchor="center")
        self.crear_boton_estilizado(frame_principal, "↩️ Volver", self.pantalla_principal).pack(pady=5, anchor="center")

    def borrar_cuenta(self):
        """
        Permite al usuario eliminar su cuenta del sistema.
        """
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar tu cuenta? Esta acción no se puede deshacer."):
            try:
                # Usar POST en vez de DELETE para máxima compatibilidad
                respuesta = self.hacer_peticion(f"/api/usuarios/{self.usuario}", metodo="POST", datos={"accion": "eliminar"})
                if respuesta["status"] == "success":
                    messagebox.showinfo("Éxito", "Cuenta eliminada correctamente")
                    self.cerrar_sesion()
                else:
                    messagebox.showerror("Error", respuesta.get("message", "Error al eliminar la cuenta"))
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar la cuenta: {str(e)}")

    def borrar_ruta_usuario(self):
        """
        Permite al usuario eliminar una de sus rutas.
        """
        self.limpiar_pantalla()
        self.root.geometry("900x900")
        frame_principal = self.crear_frame_con_borde(self.root, padding=20)
        frame_principal.pack(expand=True, fill="both", padx=30, pady=30)
        self.crear_etiqueta_estilizada(frame_principal, "🗑️ Eliminar Ruta", "titulo").pack(pady=(0, 20), anchor="center")
        frame_entrada = self.crear_frame_con_borde(frame_principal, padding=15)
        frame_entrada.pack(fill="x", pady=10)
        self.crear_etiqueta_estilizada(frame_entrada, "Nombre de la ruta a eliminar:").pack(anchor="w")
        entry = self.crear_entrada_estilizada(frame_entrada, ancho=30)
        entry.pack(fill="x", pady=5)
        def eliminar():
            ruta = entry.get().strip()
            if not ruta:
                messagebox.showerror("Error", "Escribe el nombre de la ruta.")
                return
            if messagebox.askyesno("Confirmar", f"¿Estás seguro de que quieres eliminar la ruta '{ruta}'?"):
                try:
                    respuesta = self.hacer_peticion(f"/api/usuarios/{self.usuario}/rutas/{ruta}", metodo="DELETE")
                    if respuesta["status"] == "success":
                        messagebox.showinfo("Éxito", f"Ruta '{ruta}' eliminada correctamente")
                        self.pantalla_principal()
                    else:
                        messagebox.showerror("Error", respuesta.get("message", "Error al eliminar la ruta"))
                except Exception as e:
                    messagebox.showerror("Error", f"Error al eliminar la ruta: {str(e)}")
        self.crear_boton_estilizado(frame_principal, "🗑️ Eliminar", eliminar).pack(pady=10, anchor="center")
        self.crear_boton_estilizado(frame_principal, "↩️ Volver", self.pantalla_principal).pack(pady=5, anchor="center")
