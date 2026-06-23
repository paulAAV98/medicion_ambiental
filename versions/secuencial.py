import time
from core.controlador import ControladorMonitoreo


class SimulacionSecuencial(ControladorMonitoreo):

    def __init__(self, num_ciclos: int = 10, num_estaciones: int = 4):
        super().__init__(num_ciclos, num_estaciones)
        self.modo = "Secuencial"

    def ejecutar(self):
        print(f"\n[SECUENCIAL] Iniciando simulación con {len(self.estaciones)} estaciones, {self.num_ciclos} ciclos...")
        inicio_total = time.time()

        for ciclo in range(1, self.num_ciclos + 1):
            print(f"  Ciclo {ciclo:02d}...", end=" ")
            mediciones_ciclo = []

            for estacion in self.estaciones:
                mediciones = estacion.generar_ciclo(ciclo)
                mediciones_ciclo.extend(mediciones)

            self.mediciones.extend(mediciones_ciclo)
            alertas_ciclo = self._verificar_alertas(mediciones_ciclo)
            resultado = self.analizador.procesar(mediciones_ciclo, alertas_ciclo)
            self.resultados_por_ciclo.append(resultado)

            print(f"✓ {len(mediciones_ciclo)} mediciones, {len(alertas_ciclo)} alertas")

        self.tiempo_total = time.time() - inicio_total
        self.imprimir_resumen()