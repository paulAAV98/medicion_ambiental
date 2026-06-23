import time
from typing import List
from models.estacion import EstacionAmbiental, RANGOS_VARIABLES
from models.medicion import Medicion
from models.alerta import AlertaAmbiental
from core.analizador import AnalizadorDatos


ZONAS = [
    ("Centro Histórico", ["temperatura", "CO2", "ruido"]),
    ("Totoracocha",      ["temperatura", "humedad", "PM2.5"]),
    ("Miraflores",       ["CO2", "ruido", "PM2.5"]),
    ("El Vecino",        ["temperatura", "humedad", "CO2"]),
    ("Ricaurte",         ["temperatura", "ruido", "CO2"]),
    ("Yanuncay",         ["humedad", "PM2.5", "CO2"]),
    ("El Batán",         ["temperatura", "ruido", "humedad"]),
    ("Monay",            ["CO2", "PM2.5", "temperatura"]),
    ("Machángara",       ["ruido", "humedad", "CO2"]),
    ("San Sebastián",    ["temperatura", "PM2.5", "ruido"]),
    ("Cañaribamba",      ["CO2", "humedad", "temperatura"]),
    ("Gil Ramírez",      ["ruido", "CO2", "PM2.5"]),
]


class ControladorMonitoreo:

    def __init__(self, num_ciclos: int = 10, num_estaciones: int = 4):
        self.num_ciclos = num_ciclos
        self.estaciones: List[EstacionAmbiental] = []
        self.mediciones: List[Medicion] = []
        self.alertas: List[AlertaAmbiental] = []
        self.analizador = AnalizadorDatos()
        self.resultados_por_ciclo = []
        self.tiempo_total = 0.0
        self.modo = "secuencial"
        self._inicializar_estaciones(num_estaciones)

    def _inicializar_estaciones(self, num_estaciones: int):
        self.estaciones = []
        for i in range(num_estaciones):
            zona, variables = ZONAS[i % len(ZONAS)]
            self.estaciones.append(
                EstacionAmbiental(f"Estacion-{chr(65+i)}", zona, variables)
            )

    def _verificar_alertas(self, mediciones: List[Medicion]) -> List[AlertaAmbiental]:
        alertas_ciclo = []
        for m in mediciones:
            umbral = RANGOS_VARIABLES[m.variable]["umbral_alerta"]
            if m.valor > umbral:
                alerta = AlertaAmbiental(
                    estacion=m.estacion,
                    zona=m.zona,
                    variable=m.variable,
                    valor=m.valor,
                    umbral=umbral,
                    unidad=m.unidad,
                    ciclo=m.ciclo,
                )
                alertas_ciclo.append(alerta)
                self.alertas.append(alerta)
        return alertas_ciclo

    def get_estadisticas_finales(self) -> dict:
        return {
            "modo": self.modo,
            "num_ciclos": self.num_ciclos,
            "total_mediciones": len(self.mediciones),
            "total_alertas": len(self.alertas),
            "tiempo_total": round(self.tiempo_total, 4),
            "tiempo_promedio_ciclo": round(
                self.tiempo_total / self.num_ciclos, 4
            ),
            "tiempo_promedio_procesamiento": self.analizador.tiempo_promedio_procesamiento(),
            "mediciones_por_segundo": round(
                len(self.mediciones) / self.tiempo_total, 2
            ) if self.tiempo_total > 0 else 0,
        }

    def imprimir_resumen(self):
        stats = self.get_estadisticas_finales()
        print(f"\n{'='*60}")
        print(f"  RESUMEN - Modo: {stats['modo'].upper()}")
        print(f"{'='*60}")
        print(f"  Ciclos ejecutados:        {stats['num_ciclos']}")
        print(f"  Total mediciones:         {stats['total_mediciones']}")
        print(f"  Total alertas:            {stats['total_alertas']}")
        print(f"  Tiempo total:             {stats['tiempo_total']} s")
        print(f"  Tiempo promedio/ciclo:    {stats['tiempo_promedio_ciclo']} s")
        print(f"  Mediciones/segundo:       {stats['mediciones_por_segundo']}")
        print(f"{'='*60}\n")