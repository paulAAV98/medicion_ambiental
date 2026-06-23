import random
import time
from typing import List

from models.medicion import Medicion


RANGOS_VARIABLES = {
    "temperatura": {
        "base": 16.0,
        "variacion": 6.0,
        "unidad": "°C",
        "umbral_alerta": 22.0,
    },
    "humedad": {
        "base": 65.0,
        "variacion": 20.0,
        "unidad": "%",
        "umbral_alerta": 85.0,
    },
    "ruido": {
        "base": 55.0,
        "variacion": 25.0,
        "unidad": "dB",
        "umbral_alerta": 75.0,
    },
    "CO2": {
        "base": 420.0,
        "variacion": 180.0,
        "unidad": "ppm",
        "umbral_alerta": 600.0,
    },
    "PM2.5": {
        "base": 15.0,
        "variacion": 20.0,
        "unidad": "µg/m³",
        "umbral_alerta": 25.0,
    },
}


class EstacionAmbiental:

    def __init__(
        self,
        nombre: str,
        zona: str,
        variables: List[str],
        delay_simulacion: float = 0.05,
    ):
        for v in variables:
            if v not in RANGOS_VARIABLES:
                raise ValueError(f"Variable '{v}' no reconocida.")

        self.nombre = nombre
        self.zona = zona
        self.variables = variables
        self.delay_simulacion = delay_simulacion
        self.estado = "inactiva"
        self.total_mediciones = 0
        self._ultima_medicion = {}

    def generar_medicion(self, variable: str, ciclo: int) -> Medicion:
        config = RANGOS_VARIABLES[variable]
        valor = random.gauss(config["base"], config["variacion"] * 0.3)
        valor += random.uniform(-config["variacion"] * 0.2, config["variacion"] * 0.4)
        valor = max(0.0, round(valor, 2))

        time.sleep(self.delay_simulacion)

        medicion = Medicion(
            estacion=self.nombre,
            zona=self.zona,
            variable=variable,
            valor=valor,
            unidad=config["unidad"],
            ciclo=ciclo,
        )

        self._ultima_medicion[variable] = medicion
        self.total_mediciones += 1
        return medicion

    def generar_ciclo(self, ciclo: int) -> List[Medicion]:
        self.estado = "activa"
        mediciones = []
        for variable in self.variables:
            medicion = self.generar_medicion(variable, ciclo)
            mediciones.append(medicion)
        self.estado = "esperando"
        return mediciones

    def get_umbral(self, variable: str) -> float:
        return RANGOS_VARIABLES[variable]["umbral_alerta"]

    def get_ultima_medicion(self, variable: str):
        return self._ultima_medicion.get(variable)

    def __str__(self) -> str:
        return f"EstacionAmbiental({self.nombre}, zona={self.zona})"