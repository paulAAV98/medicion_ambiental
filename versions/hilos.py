import time
import threading
from core.controlador import ControladorMonitoreo


class EstacionHilo(threading.Thread):

    def __init__(self, estacion, ciclo: int, buffer: list, lock: threading.Lock):
        super().__init__()
        self.estacion = estacion
        self.ciclo = ciclo
        self.buffer = buffer
        self.lock = lock

    def run(self):
        self.estacion.estado = "activa"
        mediciones = self.estacion.generar_ciclo(self.ciclo)
        with self.lock:
            self.buffer.extend(mediciones)
        self.estacion.estado = "esperando"


class SimulacionHilos(ControladorMonitoreo):

    def __init__(self, num_ciclos: int = 10, num_estaciones: int = 4):
        super().__init__(num_ciclos, num_estaciones)
        self.modo = "Hilos (Lock + Barrier)"
        self.lock = threading.Lock()
        self.barrier = threading.Barrier(len(self.estaciones))

    def ejecutar(self):
        print(f"\n[HILOS] Iniciando simulación con {len(self.estaciones)} estaciones, {self.num_ciclos} ciclos...")
        inicio_total = time.time()

        for ciclo in range(1, self.num_ciclos + 1):
            print(f"  Ciclo {ciclo:02d}...", end=" ")
            buffer_ciclo = []
            hilos = []

            for estacion in self.estaciones:
                hilo = EstacionHilo(estacion, ciclo, buffer_ciclo, self.lock)
                hilos.append(hilo)

            for hilo in hilos:
                hilo.start()

            for hilo in hilos:
                hilo.join()

            self.mediciones.extend(buffer_ciclo)
            alertas_ciclo = self._verificar_alertas(buffer_ciclo)
            resultado = self.analizador.procesar(buffer_ciclo, alertas_ciclo)
            self.resultados_por_ciclo.append(resultado)

            print(f"✓ {len(buffer_ciclo)} mediciones, {len(alertas_ciclo)} alertas")

        self.tiempo_total = time.time() - inicio_total
        self.imprimir_resumen()