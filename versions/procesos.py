import time
import multiprocessing
from core.controlador import ControladorMonitoreo
from models.medicion import Medicion


def ejecutar_estacion(estacion, ciclo: int, queue: multiprocessing.Queue, semaforo: multiprocessing.Semaphore):
    semaforo.acquire()
    try:
        mediciones = estacion.generar_ciclo(ciclo)
        for m in mediciones:
            queue.put(m.to_dict())
    finally:
        semaforo.release()


class SimulacionProcesos(ControladorMonitoreo):

    def __init__(self, num_ciclos: int = 10, num_estaciones: int = 4):
        super().__init__(num_ciclos, num_estaciones)
        self.modo = "Procesos (Queue + Semaphore)"
        self.semaforo = multiprocessing.Semaphore(len(self.estaciones))

    def ejecutar(self):
        print(f"\n[PROCESOS] Iniciando simulación con {len(self.estaciones)} estaciones, {self.num_ciclos} ciclos...")
        inicio_total = time.time()

        for ciclo in range(1, self.num_ciclos + 1):
            print(f"  Ciclo {ciclo:02d}...", end=" ")
            queue = multiprocessing.Queue()
            procesos = []

            for estacion in self.estaciones:
                p = multiprocessing.Process(
                    target=ejecutar_estacion,
                    args=(estacion, ciclo, queue, self.semaforo)
                )
                procesos.append(p)

            for p in procesos:
                p.start()

            for p in procesos:
                p.join()

            mediciones_ciclo = []
            while not queue.empty():
                data = queue.get()
                medicion = Medicion.from_dict(data)
                mediciones_ciclo.append(medicion)

            self.mediciones.extend(mediciones_ciclo)
            alertas_ciclo = self._verificar_alertas(mediciones_ciclo)
            resultado = self.analizador.procesar(mediciones_ciclo, alertas_ciclo)
            self.resultados_por_ciclo.append(resultado)

            print(f"✓ {len(mediciones_ciclo)} mediciones, {len(alertas_ciclo)} alertas")

        self.tiempo_total = time.time() - inicio_total
        self.imprimir_resumen()