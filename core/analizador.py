import time
import numpy as np
from typing import List, Dict
from models.medicion import Medicion
from models.alerta import AlertaAmbiental


class AnalizadorDatos:

    def __init__(self):
        self.total_mediciones_procesadas = 0
        self.total_alertas = 0
        self.tiempos_procesamiento = []
        self.historial: Dict[str, Dict[str, List[float]]] = {}

    def procesar(self, mediciones: List[Medicion], alertas: List[AlertaAmbiental]) -> dict:
        inicio = time.time()

        self._actualizar_historial(mediciones)
        estadisticas = self._calcular_estadisticas()
        carga = self._carga_computacional(mediciones)
        zona_riesgo = self._zona_mayor_riesgo(alertas)

        tiempo = time.time() - inicio
        self.tiempos_procesamiento.append(tiempo)
        self.total_mediciones_procesadas += len(mediciones)
        self.total_alertas += len(alertas)

        return {
            "estadisticas": estadisticas,
            "zona_mayor_riesgo": zona_riesgo,
            "indice_ambiental": carga,
            "tiempo_procesamiento": tiempo,
            "total_mediciones": self.total_mediciones_procesadas,
            "total_alertas": self.total_alertas,
        }

    def _actualizar_historial(self, mediciones: List[Medicion]):
        for m in mediciones:
            if m.variable not in self.historial:
                self.historial[m.variable] = {}
            if m.estacion not in self.historial[m.variable]:
                self.historial[m.variable][m.estacion] = []
            self.historial[m.variable][m.estacion].append(m.valor)

    def _calcular_estadisticas(self) -> dict:
        estadisticas = {}
        for variable, estaciones in self.historial.items():
            todos_los_valores = []
            for valores in estaciones.values():
                todos_los_valores.extend(valores)
            if todos_los_valores:
                arr = np.array(todos_los_valores)
                estadisticas[variable] = {
                    "promedio": round(float(np.mean(arr)), 2),
                    "maximo":   round(float(np.max(arr)), 2),
                    "minimo":   round(float(np.min(arr)), 2),
                    "cantidad": len(arr),
                }
        return estadisticas

    def _carga_computacional(self, mediciones: List[Medicion]) -> float:
        if not mediciones:
            return 0.0
        valores = np.array([m.valor for m in mediciones])
        resultado = 0.0
        for _ in range(500):
            resultado = np.sum(np.sqrt(np.abs(np.sin(valores) * np.cos(valores))))
            resultado += np.std(valores) * np.mean(valores)
        return round(float(resultado), 4)

    def _zona_mayor_riesgo(self, alertas: List[AlertaAmbiental]) -> str:
        if not alertas:
            return "Ninguna"
        conteo = {}
        for alerta in alertas:
            conteo[alerta.zona] = conteo.get(alerta.zona, 0) + 1
        return max(conteo, key=conteo.get)

    def tiempo_promedio_procesamiento(self) -> float:
        if not self.tiempos_procesamiento:
            return 0.0
        return round(sum(self.tiempos_procesamiento) / len(self.tiempos_procesamiento), 4)