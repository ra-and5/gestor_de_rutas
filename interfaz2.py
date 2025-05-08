import tkinter as tk
from tkinter import messagebox
import requests
import webbrowser
import os
from PIL import Image, ImageTk

class Interfaz:
    """
    Clase que define la interfaz gráfica de la aplicación utilizando Tkinter.
    Proporciona todas las funcionalidades de la aplicación como login, registro de usuarios,
    consulta de clima, creación de rutas, y más.
    """
      # URL base de la API
    API_URL = "http://127.0.0.1:5000" 
    def __init__(self, root):
        """
        Inicializa la interfaz, configura la ventana principal y llama a la pantalla de login.

        Parameters
        ----------
        root : tkinter.Tk
            Instancia principal de la ventana de Tkinter.
        """
        self.root = root
        self.root.title("🌍 Gestor de Rutas - Login")
        self.root.geometry("600x700")
        self.usuario = None
        self.api_url = "http://127.0.0.1:5000"
        self.root.configure(bg="#f0f4f8")  # Fondo general
        self.pantalla_login()

    def pantalla_login(self):
        """
        Muestra la pantalla de login donde el usuario introduce su nombre de usuario y contraseña
        para acceder a la aplicación.

        Llama a la función `verificar_login` para autenticar al usuario.
        """
        self.limpiar_pantalla()
        self.root.configure(bg="#f0f4f8")

        # Mostrar el logo redondo
        try:
            logo_image = Image.open("logo.png")
            logo_image = logo_image.resize((150, 150))  # Tamaño ajustable
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            tk.Label(self.root, image=self.logo_photo).pack(pady=10)
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
                  bg="#007acc", fg="white", activebackground="#005f99").pack(pady=15)

        tk.Button(self.root, text="📝 ¿No tienes cuenta? Regístrate", command=self.abrir_ventana_registro,
                  bg="#e0e0e0", fg="#333333", activebackground="#cccccc").pack(pady=5)

    def verificar_login(self):
        """
        Verifica las credenciales del usuario con la API y, si son correctas, carga la pantalla principal.

        Si la conexión a la API falla o las credenciales son incorrectas, muestra un mensaje de error.

        Raises
        ------
        Exception
            Si no se puede conectar al servidor o las credenciales son incorrectas.
        """
        username = self.entry_usuario.get().strip()
        password = self.entry_password.get().strip()
        try:
            res = requests.post(f"{self.api_url}/login", json={"username": username, "password": password})
            if res.status_code == 200:
                self.usuario = {'username': username, 'password': password}
                messagebox.showinfo("Bienvenido", f"Hola {username}, ¡has iniciado sesión!")
                self.pantalla_principal()
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
        except Exception as e:
            messagebox.showerror("Error de conexión", f"No se pudo conectar con el servidor:\n{e}")

    def abrir_ventana_registro(self):
        """
        Muestra la ventana de registro donde el usuario puede ingresar sus datos para crear una nueva cuenta.

        Llama a la función `registrar_usuario` para registrar el usuario con los datos ingresados.
        """
        self.limpiar_pantalla()
        tk.Label(self.root, text="🆕 Registro de Usuario", font=("Arial", 18, "bold")).pack(pady=20)
        campos = ["Nombre", "Apellido", "Email", "Usuario", "Teléfono", "Fecha de nacimiento (YYYY-MM-DD)", "Ciudad", "Contraseña"]
        self.entries_registro = []
        for campo in campos:
            tk.Label(self.root, text=f"{campo}:").pack()
            entry = tk.Entry(self.root, show="*" if campo == "Contraseña" else None)
            entry.pack()
            self.entries_registro.append(entry)
        tk.Button(self.root, text="✅ Registrar", width=20, command=self.registrar_usuario).pack(pady=15)
        tk.Button(self.root, text="↩️ Volver", command=self.pantalla_login).pack()

    def registrar_usuario(self):
        """
        Registra un nuevo usuario en el sistema. Los datos ingresados se envían a la API para ser almacenados.

        Parameters
        ----------
        No recibe parámetros directamente. Obtiene los valores desde los campos de la interfaz.

        Raises
        ------
        ValueError
            Si faltan datos en algún campo del formulario.
        """
        datos = [e.get().strip() for e in self.entries_registro]
        if not all(datos):
            messagebox.showerror("Error", "Por favor, complete todos los campos.")
            return
        keys = ["nombre", "apellido", "email", "username", "telefono", "fecha_nacimiento", "ciudad", "password"]
        data = dict(zip(keys, datos))
        res = requests.post(f"{self.api_url}/registro", json=data)
        if res.status_code == 200:
            messagebox.showinfo("Registro exitoso", "¡Te has registrado correctamente!")
            self.pantalla_login()
        else:
            messagebox.showerror("Error", "El nombre de usuario ya existe.")

    def pantalla_principal(self):
        """
        Muestra la pantalla principal después de que el usuario haya iniciado sesión correctamente.

        Los botones disponibles permiten al usuario acceder a diferentes funcionalidades de la aplicación:
        consultar el clima, crear rutas, ver rutas compartidas, etc.
        """
        self.limpiar_pantalla()
        self.root.title(f"🏠 Bienvenido {self.usuario['username']}")
        tk.Label(self.root, text=f"👋 ¡Hola, {self.usuario['username']}!", font=("Arial", 16, "bold")).pack(pady=20)
        botones = [
            ("☁️ Consultar el clima", self.ver_clima),
            ("📍 Crear ruta manual", self.pantalla_crear_ruta_manual),
            ("⚙️ Crear rutas automáticas", self.pantalla_crear_ruta_auto),
            ("📂 Ver mis rutas (PDF/HTML)", self.ver_rutas),
            ("🗑️ Borrar una de mis rutas", self.borrar_ruta_usuario),      
            ("👥 Ver rutas compartidas con amigos", self.ver_amigos_y_rutas),
            ("🔎 Buscar usuarios", self.buscar_usuarios),
            ("✏️ Editar perfil", self.editar_perfil),
            ("🗑️ Borrar cuenta", self.borrar_cuenta),             
            ("🔒 Cerrar sesión", self.cerrar_sesion)
        ]
        for texto, comando in botones:
            tk.Button(self.root, text=texto, width=40, height=2, command=comando).pack(pady=5)

    def ver_amigos_y_rutas(self):
        """
        Muestra las rutas compartidas con los amigos del usuario.

        Realiza una petición a la API para obtener las rutas comunes entre el usuario y sus amigos.
        """
        self.limpiar_pantalla()
        tk.Label(self.root, text="👥 Amigos con rutas compartidas", font=("Arial", 16, "bold")).pack(pady=10)
        res = requests.get(f"{self.api_url}/usuarios/{self.usuario['username']}/amigos_comunes")
        if res.status_code == 200:
            amigos = res.json().get("amigos", {})
            if not amigos:
                tk.Label(self.root, text="🙁 No compartes rutas con nadie aún.").pack(pady=10)
            for amigo, rutas in amigos.items():
                tk.Label(self.root, text=f"👤 {amigo}", font=("Arial", 14, "bold")).pack(pady=5)
                for ruta in rutas:
                    self._mostrar_ruta_con_botones(ruta)
        else:
            messagebox.showerror("Error", "No se pudo obtener la información.")
        tk.Button(self.root, text="↩️ Volver", command=self.pantalla_principal).pack(pady=15)

    def _mostrar_ruta_con_botones(self, ruta):
        """
        Muestra una ruta específica con botones para descargar en PDF o HTML.

        Parameters
        ----------
        ruta : str
            Nombre de la ruta a mostrar y con la que crear los botones de descarga.
        """
        frame = tk.Frame(self.root)
        frame.pack(pady=2)
        tk.Label(frame, text=f"🛣️ {ruta}", font=("Arial", 12)).pack(side="left", padx=10)
        pdf_path = os.path.join("static", f"{ruta}.pdf")
        html_path = os.path.join("static", f"rutas_{ruta}.html")
        if os.path.exists(pdf_path):
            tk.Button(frame, text="📄 PDF", command=lambda p=pdf_path: webbrowser.open(p)).pack(side="left", padx=5)
        if os.path.exists(html_path):
            tk.Button(frame, text="🌐 HTML", command=lambda h=html_path: webbrowser.open(h)).pack(side="left", padx=5)

    def ver_rutas(self):
        """
        Muestra las rutas del usuario (PDF y HTML).

        Hace una petición a la API para obtener todas las rutas asociadas al usuario y las muestra en la interfaz.
        """
        self.limpiar_pantalla()
        tk.Label(self.root, text="📂 Mis Rutas", font=("Arial", 16, "bold")).pack(pady=10)
        res = requests.get(f"{self.api_url}/usuarios/{self.usuario['username']}/rutas")
        if res.status_code == 200:
            rutas = res.json().get("rutas", [])
            for ruta in rutas:
                self._mostrar_ruta_con_botones(ruta)
        else:
            messagebox.showerror("Error", "No se pudieron obtener las rutas.")
        tk.Button(self.root, text="↩️ Volver", command=self.pantalla_principal).pack(pady=10)

    def ver_clima(self):
        """
        Muestra la interfaz para consultar el clima en una ciudad especificada.

        Permite al usuario ingresar una ciudad y realizar la consulta del clima utilizando la API.
        """
        self.limpiar_pantalla()
        tk.Label(self.root, text="🌤️ Consulta del Clima", font=("Arial", 16, "bold")).pack(pady=20)
        
        tk.Label(self.root, text="📍 Introduzca la ciudad a buscar:").pack(pady=5)
        
        self.entry_ciudad_clima = tk.Entry(self.root)
        self.entry_ciudad_clima.pack(pady=5)
        
        tk.Button(self.root, text="🔍 Consultar", command=self.consultar_clima).pack(pady=10)
        tk.Button(self.root, text="↩️ Volver", command=self.pantalla_principal).pack(pady=10)

    def consultar_clima(self):
        """
        Consulta el clima de la ciudad ingresada utilizando la API.

        Realiza una petición GET a la API de clima, mostrando los datos del clima o un mensaje de error.
        """
        ciudad = self.entry_ciudad_clima.get().strip()
        if not ciudad:
            messagebox.showerror("Error", "Por favor, ingresa una ciudad.")
            return
        res = requests.get(f"{self.api_url}/clima", params={"ciudad": ciudad})
        if res.status_code == 200:
            clima = res.json()
            clima_info = f"🌆 Ciudad: {clima['ciudad']}\n🌡️ Temp: {clima['temperatura']}°C\n💧 Humedad: {clima['humedad']}%\n☁️ Descripción: {clima['descripcion']}\n💨 Viento: {clima['viento']} m/s"
            messagebox.showinfo("🌍 Clima Actual", clima_info)
        else:
            messagebox.showerror("Error", f"No se pudo obtener el clima: {res.json().get('error')}")


    def pantalla_crear_ruta_manual(self):
        """
        Muestra la pantalla para crear una ruta manual donde el usuario introduce los datos necesarios
        para crear una ruta personalizada (origen, puntos intermedios, destino, etc.).

        Este método crea la interfaz de usuario con campos de texto para que el usuario ingrese los
        parámetros de la ruta manual.
        """
        self.limpiar_pantalla()
        tk.Label(self.root, text="📝 Crear Ruta Manual", font=("Arial", 16, "bold")).pack(pady=15)
        labels = ["📍 Origen:", "🔁 Puntos intermedios (separados por comas):", "🎯 Destino:", "🚗 Modo de transporte (walk, bike, drive):", "🆔 Nombre de la ruta:"]
        self.entries_ruta_manual = []
        for texto in labels:
            tk.Label(self.root, text=texto).pack()
            entry = tk.Entry(self.root, width=50)
            entry.pack(pady=2)
            self.entries_ruta_manual.append(entry)
        tk.Button(self.root, text="➕ Crear Ruta", command=self.crear_ruta_manual).pack(pady=10)
        tk.Button(self.root, text="↩️ Volver", command=self.pantalla_principal).pack(pady=5)

    def crear_ruta_manual(self):
        """
        Crea una ruta manual a partir de los datos proporcionados por el usuario. Los datos se envían
        a la API para su procesamiento y creación en el sistema.

        Parameters
        ----------
        origen : str
            El punto de inicio de la ruta.
        intermedios : list of str
            Los puntos intermedios en la ruta, separados por comas.
        destino : str
            El destino final de la ruta.
        modo : str
            El modo de transporte (por ejemplo, "walk", "bike", "drive").
        nombre : str, optional
            El nombre de la ruta, si se proporciona. Si no, se asigna como None.

        Returns
        -------
        None
            La respuesta del servidor se muestra en un mensaje de información con los archivos generados (PDF, GPX, HTML).
        """
        origen = self.entries_ruta_manual[0].get().strip()
        intermedios = self.entries_ruta_manual[1].get().strip().split(",") if self.entries_ruta_manual[1].get().strip() else []
        destino = self.entries_ruta_manual[2].get().strip()
        modo = self.entries_ruta_manual[3].get().strip().lower()
        nombre = self.entries_ruta_manual[4].get().strip() or None
        data = {
            "username": self.usuario["username"],
            "password": self.usuario["password"],
            "origen": origen,
            "intermedios": intermedios,
            "destino": destino,
            "modo": modo,
            "nombre": nombre
        }
        res = requests.post(f"{self.api_url}/ruta_manual", json=data)
        if res.status_code == 200:
            r = res.json()
            messagebox.showinfo("✅ Ruta creada", f"Ruta creada con éxito.\nPDF: {r['pdf']}\nGPX: {r['gpx']}\nHTML: {r['html']}")
            self.pantalla_principal()
        else:
            messagebox.showerror("❌ Error", f"No se pudo crear la ruta (seguramente por una dirección inválida): {res.json().get('error')}")

    def pantalla_crear_ruta_auto(self):
        """
        Muestra la pantalla para crear rutas automáticas a partir de un conjunto de direcciones. El usuario
        puede ingresar varias direcciones y especificar la cantidad de rutas a generar.

        Parameters
        ----------
        None

        Returns
        -------
        None
            Crea la interfaz con los campos necesarios para que el usuario ingrese las direcciones y la cantidad.
        """
        self.limpiar_pantalla()
        tk.Label(self.root, text="🤖 Crear Rutas Automáticas", font=("Arial", 16, "bold")).pack(pady=15)
        tk.Label(self.root, text="🏘️ Direcciones (separadas por comas):").pack()
        self.entry_direcciones_auto = tk.Entry(self.root, width=60)
        self.entry_direcciones_auto.pack(pady=5)
        tk.Label(self.root, text="🔢 Cantidad de rutas:").pack()
        self.entry_cantidad_auto = tk.Entry(self.root, width=10)
        self.entry_cantidad_auto.insert(0, "5")
        self.entry_cantidad_auto.pack(pady=5)
        tk.Button(self.root, text="🛠️ Generar Rutas", command=self.crear_rutas_automaticas).pack(pady=10)
        tk.Button(self.root, text="↩️ Volver", command=self.pantalla_principal).pack(pady=5)

    def crear_rutas_automaticas(self):
        """
        Genera rutas automáticas a partir de un conjunto de direcciones y una cantidad especificada por el usuario.
        Los datos se envían a la API para su procesamiento.

        Parameters
        ----------
        None

        Returns
        -------
        None
            La respuesta del servidor se muestra en un mensaje de información con las rutas generadas.
        """
        direcciones = self.entry_direcciones_auto.get().strip().split(",")
        cantidad = self.entry_cantidad_auto.get().strip()
        data = {
            "username": self.usuario["username"],
            "password": self.usuario["password"],
            "direcciones": [d.strip() for d in direcciones if d.strip()],
            "cantidad": cantidad
        }
        res = requests.post(f"{self.api_url}/ruta_auto", json=data)
        if res.status_code == 200:
            rutas = res.json().get("rutas", [])
            messagebox.showinfo("✅ Rutas creadas", "\n".join(rutas))
        else:
            messagebox.showerror("❌ Error", f"No se pudo generar las rutas (seguramente por una dirección inválida): {res.json().get('error')}")

    def explorar_rutas(self):
        """
        Muestra la interfaz para explorar rutas disponibles con filtros como dificultad, distancia, duración y modo de transporte.

        Muestra las rutas disponibles según los filtros definidos por el usuario.

        Parameters
        ----------
        None

        Returns
        -------
        None
            La interfaz permite filtrar y buscar rutas según los parámetros introducidos.
        """
        self.limpiar_pantalla()
        tk.Label(self.root, text="🔎 Explorar rutas disponibles", font=("Arial", 16, "bold")).pack(pady=10)

        filtros = {
            "dificultad": tk.StringVar(),
            "max_km": tk.StringVar(),
            "max_horas": tk.StringVar(),
            "transporte": tk.StringVar()
        }

        campos = [
            ("🎚️ Dificultad (bajo, medio, alto)", "dificultad"),
            ("📏 Distancia máxima (km)", "max_km"),
            ("⏱️ Duración máxima (h)", "max_horas"),
            ("🚗 Medio de transporte (walk, bike, drive)", "transporte")
        ]

        self.entries_filtros = {}

        for label, key in campos:
            tk.Label(self.root, text=label).pack()
            entry = tk.Entry(self.root, textvariable=filtros[key])
            entry.pack(pady=3)
            self.entries_filtros[key] = entry

        tk.Button(self.root, text="🔍 Buscar rutas", command=self.buscar_rutas_filtradas).pack(pady=10)
        tk.Button(self.root, text="↩️ Volver", command=self.pantalla_principal).pack(pady=5)

        # Scrollable area
        contenedor_scroll = tk.Frame(self.root)
        contenedor_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = tk.Canvas(contenedor_scroll)
        scrollbar = tk.Scrollbar(contenedor_scroll, orient="vertical", command=canvas.yview)
        self.frame_resultados = tk.Frame(canvas)

        self.frame_resultados.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.frame_resultados, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mostrar todas las rutas al cargar
        self.buscar_rutas_filtradas()


    def buscar_rutas_filtradas(self):
        """
        Realiza una consulta a la API para obtener las rutas filtradas según los criterios definidos
        por el usuario en los campos de entrada.

        La función destruye los resultados previos (si existen), genera los parámetros de búsqueda 
        a partir de los filtros, y luego consulta la API para obtener las rutas correspondientes.
        Si no se encuentran rutas, muestra un mensaje indicativo. Si hay rutas disponibles, las
        muestra en la interfaz.

        Parameters
        ----------
        None

        Returns
        -------
        None
            La función no devuelve nada. Los resultados de la búsqueda se muestran directamente 
            en la interfaz gráfica.
        """
        for widget in self.frame_resultados.winfo_children():
            widget.destroy()

        params = {}
        for key, entry in self.entries_filtros.items():
            val = entry.get().strip()
            if val:
                params[key] = val

        try:
            res = requests.get(f"{self.api_url}/rutas", params=params)
            if res.status_code == 200:
                rutas = res.json().get("rutas", [])
                if not rutas:
                    tk.Label(self.frame_resultados, text="😕 No se encontraron rutas con esos filtros.").pack()
                for ruta in rutas:
                    self.mostrar_ruta_explorada(ruta)
            else:
                tk.Label(self.frame_resultados, text="❌ Error al consultar las rutas.").pack()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar con la API: {e}")

    def mostrar_ruta_explorada(self, ruta):
        """
        Muestra una ruta específica en la interfaz gráfica con la información relacionada, como nombre,
        dificultad, modo de transporte, distancia y duración. Además, si existen archivos PDF y HTML asociados
        con la ruta, se muestran botones para permitir su descarga.

        Parameters
        ----------
        ruta : dict
            Diccionario que contiene los datos de una ruta, incluyendo el nombre, dificultad, modo de transporte,
            distancia y duración.

        Returns
        -------
        None
            La ruta y sus botones de descarga se muestran directamente en la interfaz gráfica.
        """
        frame = tk.Frame(self.frame_resultados, relief="groove", borderwidth=2)
        frame.pack(pady=5, fill="x", padx=10)

        info = f"🛣️ {ruta.get('nombre', 'Sin nombre')} | 🧭 Dificultad: {ruta.get('dificultad')} | 🚶‍♂️ Modo: {ruta.get('modo_transporte')}\n"
        info += f"📏 Distancia: {ruta.get('distancia')} | ⏱️ Duración: {ruta.get('duracion')}"

        tk.Label(frame, text=info, justify="left", font=("Arial", 10)).pack(anchor="w", padx=10, pady=5)

        nombre = ruta.get("nombre", "")
        pdf_path = os.path.join("static", f"{nombre}.pdf")
        html_path = os.path.join("static", f"rutas_{nombre}.html")

        botonera = tk.Frame(frame)
        botonera.pack(pady=2)

        if os.path.exists(pdf_path):
            tk.Button(botonera, text="📄 PDF", command=lambda p=pdf_path: webbrowser.open(p)).pack(side="left", padx=5)
        if os.path.exists(html_path):
            tk.Button(botonera, text="🌐 HTML", command=lambda h=html_path: webbrowser.open(h)).pack(side="left", padx=5)

    def cerrar_sesion(self):
        """
        Cierra la sesión del usuario, eliminando los datos del usuario actual y redirigiendo a la pantalla
        de inicio de sesión.

        Parameters
        ----------
        None

        Returns
        -------
        None
            La función no devuelve nada. La interfaz cambia a la pantalla de inicio de sesión.
        """
        self.usuario = None
        self.root.title("Gestor de Rutas - Login")
        self.pantalla_login()

    def limpiar_pantalla(self):
        """
        Limpia todos los widgets de la pantalla actual, eliminando todos los elementos visuales
        para cargar una nueva pantalla o funcionalidad.

        Parameters
        ----------
        None

        Returns
        -------
        None
            La función no devuelve nada. Simplemente elimina todos los widgets de la pantalla actual.
        """
        for widget in self.root.winfo_children():
            widget.destroy()

    def borrar_ruta_usuario(self):
        """
        Muestra una interfaz para eliminar una ruta del usuario actual.

        Permite al usuario introducir el nombre de una ruta que desea eliminar.
        Si el nombre es válido, se realiza una petición DELETE a la API para 
        eliminar dicha ruta del usuario.

        Parameters
        ----------
        self : Interfaz
            Instancia actual de la clase Interfaz.

        Returns
        -------
        None
        """
        self.limpiar_pantalla()
        tk.Label(self.root, text="🗑️ Eliminar Ruta", font=("Arial", 16, "bold")).pack(pady=15)
        tk.Label(self.root, text="🛣️ Nombre de la ruta a eliminar:").pack()
        entry = tk.Entry(self.root)
        entry.pack(pady=5)

        def eliminar():
            ruta = entry.get().strip()
            if not ruta:
                messagebox.showerror("Error", "Escribe el nombre de la ruta.")
                return
            res = requests.delete(f"{self.api_url}/usuarios/{self.usuario['username']}/rutas/{ruta}")
            if res.status_code == 200:
                messagebox.showinfo("✅ Ruta eliminada", f"{ruta} fue eliminada.")
            else:
                messagebox.showerror("❌ Error", res.json().get("error", "No se pudo borrar."))

        tk.Button(self.root, text="🗑️ Eliminar", command=eliminar).pack(pady=10)
        tk.Button(self.root, text="↩️ Volver", command=self.pantalla_principal).pack(pady=5)

    def buscar_usuarios(self):
        """
        Permite buscar usuarios por nombre de usuario y ver sus rutas.

        Muestra una interfaz en la que se puede introducir un nombre de usuario.
        La aplicación realiza una búsqueda en el servidor y muestra una lista de 
        coincidencias. Para cada usuario encontrado, se puede visualizar sus rutas 
        en formato PDF o HTML si están disponibles.

        Parameters
        ----------
        self : Interfaz
            Instancia actual de la clase Interfaz.

        Returns
        -------
        None
        """
        self.limpiar_pantalla()
        tk.Label(self.root, text="🔎 Buscar Usuarios", font=("Arial", 16, "bold")).pack(pady=15)
        tk.Label(self.root, text="🔤 Nombre de usuario:").pack()
        entry = tk.Entry(self.root)
        entry.pack(pady=5)

        resultados_frame = tk.Frame(self.root)
        resultados_frame.pack(pady=10)

        def buscar():
            for widget in resultados_frame.winfo_children():
                widget.destroy()

            nombre = entry.get().strip()
            if not nombre:
                messagebox.showerror("Error", "Introduce un nombre de usuario.")
                return

            try:
                res = requests.get(f"{self.api_url}/usuarios/buscar", params={"nombre": nombre}, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    usuarios = data.get("resultados", [])
                    if not usuarios:
                        tk.Label(resultados_frame, text="🙁 No se encontraron usuarios.").pack()
                    else:
                        tk.Label(resultados_frame, text="👥 Coincidencias:").pack()
                        for username in usuarios:
                            usuario_frame = tk.Frame(resultados_frame)
                            usuario_frame.pack(pady=5)
                            tk.Label(usuario_frame, text=f"🔹 {username}").pack()

                            def ver_rutas_pdf_html(user=username):
                                try:
                                    res_rutas = requests.get(f"{self.api_url}/usuarios/{user}/rutas", timeout=10)
                                    if res_rutas.status_code == 200:
                                        rutas = res_rutas.json().get("rutas", [])
                                        if not rutas:
                                            messagebox.showinfo("ℹ️", f"El usuario {user} no tiene rutas.")
                                            return

                                        rutas_win = tk.Toplevel(self.root)
                                        rutas_win.title(f"Rutas de {user}")

                                        for ruta in rutas:
                                            ruta_frame = tk.Frame(rutas_win)
                                            ruta_frame.pack(pady=2)
                                            tk.Label(ruta_frame, text=ruta).pack(side="left")

                                            def abrir_pdf(r=ruta):
                                                path_pdf = os.path.join("static", f"{r}.pdf")
                                                if os.path.exists(path_pdf):
                                                    webbrowser.open(f"file://{os.path.abspath(path_pdf)}")
                                                else:
                                                    messagebox.showerror("Error", f"No se encuentra el PDF de {r}.")

                                            def abrir_html(r=ruta):
                                                path_html = os.path.join("static", f"rutas_{r}.html")
                                                if os.path.exists(path_html):
                                                    webbrowser.open(f"file://{os.path.abspath(path_html)}")
                                                else:
                                                    messagebox.showerror("Error", f"No se encuentra el HTML de {r}.")

                                            btn_pdf = tk.Button(ruta_frame, text="📄 PDF", command=abrir_pdf)
                                            btn_pdf.pack(side="left", padx=5)

                                            btn_html = tk.Button(ruta_frame, text="🌐 HTML", command=abrir_html)
                                            btn_html.pack(side="left", padx=5)

                                    else:
                                        messagebox.showerror("Error", f"No se pudieron obtener las rutas de {user}.")
                                except Exception as e:
                                    print("ERROR AL CARGAR RUTAS DE OTRO USUARIO:", e)
                                    messagebox.showerror("Error", "Error inesperado al cargar rutas")

                            tk.Button(usuario_frame, text="📁 Ver rutas", command=ver_rutas_pdf_html).pack(pady=2)
                else:
                    messagebox.showerror("❌ Error", f"Error {res.status_code}")
            except Exception as e:
                print("ERROR:", e)
                messagebox.showerror("❌ Error", f"Error inesperado: {e}")

        tk.Button(self.root, text="🔍 Buscar", command=buscar).pack(pady=10)
        tk.Button(self.root, text="↩️ Volver", command=self.pantalla_principal).pack(pady=5)

    def borrar_cuenta(self):
        """
        Elimina la cuenta del usuario actual del sistema.

        Solicita confirmación al usuario mediante una ventana emergente.
        Si se confirma, envía una solicitud DELETE al servidor para eliminar 
        al usuario del sistema. Si tiene éxito, cierra la sesión del usuario.

        Parameters
        ----------
        self : Interfaz
            Instancia actual de la clase Interfaz.

        Returns
        -------
        None
        """
        confirmar = messagebox.askyesno("⚠️ Confirmación", "¿Estás seguro de que quieres borrar tu cuenta?")
        if confirmar:
            try:
                res = requests.delete(f"{self.api_url}/usuarios/{self.usuario['username']}", timeout=10)
                if res.status_code == 200:
                    messagebox.showinfo("✅ Cuenta eliminada", "Tu cuenta ha sido borrada exitosamente.")
                    self.usuario = None
                    self.pantalla_login()
                else:
                    try:
                        error_msg = res.json().get("error", "No se pudo borrar la cuenta.")
                    except:
                        error_msg = res.text or "Error desconocido"
                    messagebox.showerror("❌ Error", error_msg)
            except Exception as e:
                print("ERROR EN BORRADO:", e)
                messagebox.showerror("❌ Error", f"Error inesperado: {e}")

    def editar_perfil(self):
        """
        Permite al usuario editar sus datos personales.

        Muestra un formulario con campos editables como nombre, apellido, 
        email, teléfono y ciudad. Al guardar, se envía una solicitud PUT 
        al servidor con los datos actualizados. Si la operación es exitosa, 
        se actualiza la información local del usuario.

        Parameters
        ----------
        self : Interfaz
            Instancia actual de la clase Interfaz.

        Returns
        -------
        None
        """
        self.limpiar_pantalla()
        tk.Label(self.root, text="✏️ Editar Perfil", font=("Arial", 16, "bold")).pack(pady=10)

        campos = {
            "nombre": tk.StringVar(value=self.usuario.get("nombre", "")),
            "apellido": tk.StringVar(value=self.usuario.get("apellido", "")),
            "email": tk.StringVar(value=self.usuario.get("email", "")),
            "telefono": tk.StringVar(value=self.usuario.get("telefono", "")),
            "ciudad": tk.StringVar(value=self.usuario.get("ciudad", ""))
        }

        for campo, var in campos.items():
            tk.Label(self.root, text=campo.capitalize()).pack()
            tk.Entry(self.root, textvariable=var).pack(pady=3)

        def guardar():
            data = {key: var.get() for key, var in campos.items()}
            try:
                res = requests.put(f"{self.api_url}/usuarios/{self.usuario['username']}", json=data, timeout=10)
                if res.status_code == 200:
                    messagebox.showinfo("✅ Éxito", "Datos actualizados correctamente.")
                    self.usuario.update(data)
                    self.pantalla_principal()
                else:
                    try:
                        error_msg = res.json().get("error", "No se pudo actualizar el perfil.")
                    except:
                        error_msg = res.text or "Error desconocido"
                    messagebox.showerror("❌ Error", error_msg)
            except Exception as e:
                print("ERROR EN ACTUALIZACIÓN:", e)
                messagebox.showerror("❌ Error", f"Error inesperado: {e}")

        tk.Button(self.root, text="💾 Guardar cambios", command=guardar).pack(pady=10)
        tk.Button(self.root, text="↩️ Volver", command=self.pantalla_principal).pack(pady=5)
