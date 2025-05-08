from ruta import Ruta
import random
import os
from typing import List

class RutaAuto:
    def __init__(self, directorio: str = "rutas") -> None:
        self.directorio = directorio
        if not os.path.exists(self.directorio):
            os.makedirs(self.directorio)

    def generar_rutas_desde_direcciones(self, direcciones: List[str], cantidad: int = 5) -> None:
        """
        Genera rutas aleatorias entre las direcciones proporcionadas y las exporta en varios formatos.

        Parámetros:
        -----------
        direcciones : List[str]
            Lista de direcciones reales introducidas por el usuario.

        cantidad : int
            Número de rutas aleatorias a generar (por defecto 5).
        """
        if len(direcciones) < 2:
            return "⚠️ Se necesitan al menos dos direcciones para generar rutas."

        rutas_creadas = []  # Guardar las rutas generadas

        for i in range(cantidad):
            origen, destino = random.sample(direcciones, 2)
            puntos_intermedios = random.sample([d for d in direcciones if d != origen and d != destino], k=min(2, len(direcciones) - 2))
            modo = random.choice(["walk", "bike", "drive"])
            nombre = f"ruta_auto_{i+1}"

            # Coordenadas aleatorias como referencia inicial
            ubicacion = (random.uniform(38.3, 38.4), random.uniform(-0.5, -0.3))

            ruta = Ruta(
                nombre=nombre,
                ubicacion=ubicacion,
                distancia=0.0,
                duracion=0.0,
                dificultad="bajo",
                alt_max=0,
                alt_min=0,
                origen=origen,
                puntos_intermedios=puntos_intermedios,
                destino=destino,
                modo_transporte=modo
            )

            ruta.guardar_en_json()
            rutas_creadas.append(f"✅ Ruta '{nombre}' creada y exportada exitosamente.")
        
        return rutas_creadas  # Retornamos las rutas generadas