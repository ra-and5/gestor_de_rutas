import os
import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser
import json
import requests
from tkinter.font import Font
import time
from PIL import Image, ImageTk 

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
    API_URL = "http://127.0.0.1:5000"
    
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
        self.root.geometry("500x600")
        self.root.configure(bg=self.COLOR_FONDO)
        self.root.resizable(False, False)
        
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
        
        try:
            if metodo == "GET":
                respuesta = requests.get(url, params=params)
            elif metodo == "POST":
                respuesta = requests.post(url, json=datos)
            else:
                raise ValueError(f"Método HTTP no soportado: {metodo}")
                
            if respuesta.status_code >= 400:
                error_msg = respuesta.json().get("message", "Error desconocido")
                raise Exception(f"Error en la API (código {respuesta.status_code}): {error_msg}")
                
            return respuesta.json()
        except requests.RequestException as e:
            raise Exception(f"Error de conexión: {str(e)}")

    def pantalla_login(self):
        """Muestra la pantalla de inicio de sesión con campos de usuario y contraseña."""
        self.limpiar_pantalla()
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
        tk.Button(self.root, text="🚀 Entrar", command=self.verificar_login,
                  bg="#007acc", fg="white", activebackground="#005f99", font=("Arial", 12, "bold"), height=2, width=20).pack(pady=15)
        tk.Button(self.root, text="📝 ¿No tienes cuenta? Regístrate", command=self.abrir_ventana_registro,
                  bg="#e0e0e0", fg="#333333", activebackground="#cccccc", font=("Arial", 11), height=2, width=30).pack(pady=5)

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
            ("🔒 Cerrar sesión", self.cerrar_sesion)
        ]
        for texto, comando in botones:
            color = "#e74c3c" if "Cerrar sesión" in texto else ("#007acc" if "Ver" in texto or "Crear" in texto else "#e0e0e0")
            fg = "white" if color in ["#007acc", "#e74c3c"] else "#333333"
            tk.Button(self.root, text=texto, command=comando, bg=color, fg=fg, activebackground="#005f99", font=("Arial", 12, "bold"), height=2, width=35).pack(pady=7)

    def pantalla_crear_ruta_manual(self):
        """Muestra un formulario para crear rutas manualmente con campos de entrada."""
        self.limpiar_pantalla()
        
        # Frame principal con borde
        frame_principal = self.crear_frame_con_borde(self.root, padding=20)
        frame_principal.pack(expand=True, fill="both", padx=30, pady=30)
        
        # Título
        self.crear_etiqueta_estilizada(frame_principal, "Crear Ruta Manual", "titulo").pack(pady=(0, 20))
        
        # Frame para los campos
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

        # Botones
        self.crear_boton_estilizado(frame_principal, "Crear Ruta", self.crear_ruta_manual, ancho=20).pack(pady=10)
        self.crear_boton_estilizado(frame_principal, "Volver", self.pantalla_principal, ancho=15, color=self.COLOR_SECUNDARIO).pack(pady=5)

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

            datos = {
                "origen": origen,
                "puntos_intermedios": intermedios,
                "destino": destino,
                "modo": modo,
                "nombre": nombre,
                "username": self.usuario
            }
            
            # Cambiado de /api/ruta_manual a /api/rutas para coincidir con miapp.py
            respuesta = self.hacer_peticion("/api/rutas", metodo="POST", datos=datos)
            
            if respuesta["status"] == "success":
                archivos = respuesta["data"]["archivos"]
                mensaje = f"Ruta creada con éxito.\nPDF: {archivos['pdf']}\nGPX: {archivos['gpx']}\nHTML: {archivos['html']}"
                messagebox.showinfo("Ruta creada", mensaje)
                self.pantalla_principal()
            else:
                mensaje_error = respuesta.get("message", "Error desconocido al crear la ruta")
                messagebox.showerror("Error", mensaje_error)
        except Exception as e:
            error_msg = str(e)
            messagebox.showerror("Error", f"No se pudo crear la ruta: {error_msg}")

    def pantalla_crear_ruta_auto(self):
        """Muestra un formulario para crear múltiples rutas automáticas."""
        self.limpiar_pantalla()
        
        # Frame principal con borde
        frame_principal = self.crear_frame_con_borde(self.root, padding=20)
        frame_principal.pack(expand=True, fill="both", padx=30, pady=30)
        
        # Título
        self.crear_etiqueta_estilizada(frame_principal, "Crear Rutas Automáticas", "titulo").pack(pady=(0, 20))
        
        # Frame para los campos
        frame_campos = tk.Frame(frame_principal, bg="white")
        frame_campos.pack(fill="x", pady=10)
        
        self.crear_etiqueta_estilizada(frame_campos, "Direcciones (separadas por comas):").pack(anchor="w")
        self.entry_direcciones_auto = self.crear_entrada_estilizada(frame_campos, ancho=60)
        self.entry_direcciones_auto.pack(fill="x", pady=(0, 10))
        
        self.crear_etiqueta_estilizada(frame_campos, "Cantidad de rutas a generar:").pack(anchor="w")
        self.entry_cantidad_auto = self.crear_entrada_estilizada(frame_campos, ancho=10)
        self.entry_cantidad_auto.insert(0, "5")
        self.entry_cantidad_auto.pack(fill="x", pady=(0, 20))

        # Botones
        self.crear_boton_estilizado(frame_principal, "Generar Rutas", self.crear_rutas_automaticas, ancho=20).pack(pady=10)
        self.crear_boton_estilizado(frame_principal, "Volver", self.pantalla_principal, ancho=15, color=self.COLOR_SECUNDARIO).pack(pady=5)

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
                resultados = respuesta["data"]
                if isinstance(resultados, list):
                    rutas_creadas = len(resultados)
                    mensaje = f"Se crearon {rutas_creadas} rutas automáticamente:\n\n"
                    for ruta in resultados[:5]:  # Mostrar solo las primeras 5 para no sobrecargar el mensaje
                        mensaje += f"- {ruta}\n"
                    if rutas_creadas > 5:
                        mensaje += f"... y {rutas_creadas - 5} más."
                    messagebox.showinfo("Rutas creadas", mensaje)
                else:
                    messagebox.showinfo("Rutas creadas", "Las rutas se han creado correctamente.")
                self.pantalla_principal()
            else:
                messagebox.showerror("Error", respuesta.get("message", "No se pudieron generar las rutas"))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar las rutas: {str(e)}")

    def ver_rutas(self):
        """Muestra todas las rutas asociadas al usuario con opciones para visualizar archivos."""
        self.limpiar_pantalla()
        
        # Frame principal con borde
        frame_principal = self.crear_frame_con_borde(self.root, padding=20)
        frame_principal.pack(expand=True, fill="both", padx=30, pady=30)
        
        # Título
        self.crear_etiqueta_estilizada(frame_principal, "Mis Rutas", "titulo").pack(pady=(0, 20))
        
        # Frame para las rutas
        frame_rutas = tk.Frame(frame_principal, bg="white")
        frame_rutas.pack(fill="both", expand=True, pady=10)
        
        # Canvas para scroll
        canvas = tk.Canvas(frame_rutas, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_rutas, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_reqwidth())
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        try:
            respuesta = self.hacer_peticion(f"/api/usuarios/{self.usuario}/rutas")
            
            if respuesta["status"] == "success":
                rutas = respuesta["data"]
                
                if rutas:
                    for ruta in rutas:
                        frame_ruta = self.crear_frame_con_borde(scrollable_frame, padding=10)
                        frame_ruta.pack(fill="x", pady=5, padx=5)
                        
                        self.crear_etiqueta_estilizada(frame_ruta, ruta, "subtitulo").pack(side="left", padx=10)
                        
                        pdf_url = f"{self.API_URL}/static/{ruta}.pdf"
                        html_url = f"{self.API_URL}/static/rutas_{ruta}.html"
                        
                        self.crear_boton_estilizado(frame_ruta, "📄 Ver PDF", lambda p=pdf_url: webbrowser.open(p), ancho=10).pack(side="left", padx=5)
                        self.crear_boton_estilizado(frame_ruta, "🌐 Ver HTML", lambda h=html_url: webbrowser.open(h), ancho=10).pack(side="left", padx=5)
                else:
                    self.crear_etiqueta_estilizada(scrollable_frame, "No tienes rutas asignadas aún.").pack(pady=20)
            else:
                messagebox.showerror("Error", respuesta.get("message", "No se pudieron obtener las rutas"))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las rutas: {str(e)}")

        # Botón para volver
        self.crear_boton_estilizado(frame_principal, "Volver", self.pantalla_principal, ancho=15, color=self.COLOR_SECUNDARIO).pack(pady=10)

    def ver_amigos(self):
        """Muestra los amigos del usuario y las rutas en común con ellos."""
        self.limpiar_pantalla()
        
        # Frame principal con borde
        frame_principal = self.crear_frame_con_borde(self.root, padding=20)
        frame_principal.pack(expand=True, fill="both", padx=30, pady=30)
        
        # Título
        self.crear_etiqueta_estilizada(frame_principal, "Rutas en común con amigos", "titulo").pack(pady=(0, 20))
        
        # Frame para los amigos
        frame_amigos = tk.Frame(frame_principal, bg="white")
        frame_amigos.pack(fill="both", expand=True, pady=10)
        
        # Canvas para scroll
        canvas = tk.Canvas(frame_amigos, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_amigos, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_reqwidth())
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        try:
            # Petición al endpoint de amigos con el username como parámetro
            respuesta = self.hacer_peticion(f"/api/usuarios/amigos?username={self.usuario}")
            
            if respuesta["status"] == "success":
                amigos_data = respuesta["data"]
                
                # Verificar si hay datos de amigos para el usuario actual
                if amigos_data:
                    for amigo, rutas_comunes in amigos_data.items():
                        frame_amigo = tk.Frame(scrollable_frame, bg="#f8fafd", bd=2, relief="ridge", padx=12, pady=10, highlightbackground="#dcdcdc", highlightthickness=1)
                        frame_amigo.pack(fill="x", pady=10, padx=12)

                        tk.Label(frame_amigo, text=f"Amigo: {amigo}", font=("Arial", 13, "bold"), bg="#f8fafd", fg="#222").pack(anchor="w", pady=2)

                        if rutas_comunes:
                            for ruta in rutas_comunes:
                                frame_ruta = tk.Frame(frame_amigo, bg="#f8fafd")
                                frame_ruta.pack(fill="x", pady=4)
                                tk.Label(frame_ruta, text=f"Ruta en común: {ruta}", bg="#f8fafd", font=("Arial", 11)).pack(side="left", padx=10)

                                # Frame horizontal para los botones
                                btn_frame = tk.Frame(frame_ruta, bg="#f8fafd")
                                btn_frame.pack(side="left", padx=16)

                                pdf_url = f"{self.API_URL}/static/{ruta}.pdf"
                                html_url = f"{self.API_URL}/static/rutas_{ruta}.html"

                                style_btn = {
                                    'bg': "#3498db",
                                    'fg': "white",
                                    'activebackground': "#217dbb",
                                    'font': ("Arial", 10, "bold"),
                                    'width': 11,
                                    'relief': "groove",
                                    'bd': 0,
                                    'highlightthickness': 0,
                                    'cursor': "hand2"
                                }
                                style_btn_html = style_btn.copy()
                                style_btn_html['bg'] = "#2ecc71"
                                style_btn_html['activebackground'] = "#27ae60"

                                btn_pdf = tk.Button(btn_frame, text="📄 Ver PDF", command=lambda p=pdf_url: webbrowser.open(p), **style_btn)
                                btn_pdf.pack(side="left", padx=4, ipadx=4, ipady=2)
                                btn_html = tk.Button(btn_frame, text="🌐 Ver HTML", command=lambda h=html_url: webbrowser.open(h), **style_btn_html)
                                btn_html.pack(side="left", padx=4, ipadx=4, ipady=2)
                        else:
                            tk.Label(frame_amigo, text="No tienen rutas en común.", bg="#f8fafd", font=("Arial", 10, "italic"), fg="#888").pack(pady=5)
                else:
                    self.crear_etiqueta_estilizada(scrollable_frame, "No tienes amigos registrados o rutas en común.").pack(pady=20)
            else:
                messagebox.showerror("Error", respuesta.get("message", "No se pudieron obtener los amigos"))
        except Exception as e:
            # Mostrar mensaje de error más detallado para depuración
            import traceback
            error_detalle = traceback.format_exc()
            messagebox.showerror("Error", f"No se pudieron cargar los amigos: {str(e)}\n\nDetalles: {error_detalle}")

        # Botón para volver
        self.crear_boton_estilizado(frame_principal, "Volver", self.pantalla_principal, ancho=15, color=self.COLOR_SECUNDARIO).pack(pady=10)

    def ver_clima(self):
        """Muestra un formulario para consultar el clima en una ciudad específica."""
        self.limpiar_pantalla()
        
        # Frame principal con borde
        frame_principal = self.crear_frame_con_borde(self.root, padding=20)
        frame_principal.pack(expand=True, fill="both", padx=30, pady=30)
        
        # Título
        self.crear_etiqueta_estilizada(frame_principal, "Consultar el Clima", "titulo").pack(pady=(0, 20))
        
        # Frame para los campos
        frame_campos = tk.Frame(frame_principal, bg="white")
        frame_campos.pack(fill="x", pady=10)
        
        self.crear_etiqueta_estilizada(frame_campos, "Ingresa la ciudad para consultar el clima").pack(anchor="w")
        self.entry_ciudad_clima = self.crear_entrada_estilizada(frame_campos)
        self.entry_ciudad_clima.pack(fill="x", pady=(0, 20))

        # Botones
        self.crear_boton_estilizado(frame_principal, "Consultar Clima", self.consultar_clima, ancho=20).pack(pady=10)
        self.crear_boton_estilizado(frame_principal, "Volver", self.pantalla_principal, ancho=15, color=self.COLOR_SECUNDARIO).pack(pady=5)

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
            messagebox.showerror("Error", f"No se pudo obtener el clima: {str(e)}")

    def ver_todas_las_rutas(self):
        """
        Muestra todas las rutas del sistema con filtros aplicables.

        Permite filtrar por dificultad, distancia, duración y modo de transporte.
        Las rutas se muestran en un panel scrollable con botones para ver PDF y HTML.
        """
        self.limpiar_pantalla()
        
        # Frame principal con borde
        frame_principal = self.crear_frame_con_borde(self.root, padding=20)
        frame_principal.pack(expand=True, fill="both", padx=30, pady=30)
        
        # Título
        self.crear_etiqueta_estilizada(frame_principal, "🧭 Filtrar Rutas del Sistema", "titulo").pack(pady=(0, 20))

        # Filtros
        filtro_frame = self.crear_frame_con_borde(frame_principal, padding=15)
        filtro_frame.pack(fill="x", pady=10)
        
        # Grid para los filtros
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

        # Botones de control
        control_frame = tk.Frame(frame_principal, bg="white")
        control_frame.pack(pady=10)
        self.crear_boton_estilizado(control_frame, "Aplicar filtros", lambda: self.aplicar_filtros_rutas(), ancho=15).pack(side="left", padx=10)
        self.crear_boton_estilizado(control_frame, "Volver", self.pantalla_principal, ancho=15, color=self.COLOR_SECUNDARIO).pack(side="left", padx=10)

        # Frame para las rutas
        frame_rutas = tk.Frame(frame_principal, bg="white")
        frame_rutas.pack(fill="both", expand=True, pady=10)
        
        # Canvas para scroll
        canvas = tk.Canvas(frame_rutas, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_rutas, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg="white")

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw", width=canvas.winfo_reqwidth())
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Cargar todas las rutas al inicio
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
