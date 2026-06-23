# SISMAU v1.0 — Sistema de Monitoreo Ambiental Urbano

Simulación de un sistema urbano de monitoreo ambiental para la ciudad de Cuenca, Ecuador. Implementado con tres versiones de ejecución: secuencial, hilos y procesos.

**Práctica 04 — Computación Paralela — Universidad Politécnica Salesiana**

## Requisitos

- Python 3.13
- numpy

## Instalación

```bash
git clone https://github.com/paulAAV98/medicion_ambiental.git
cd medicion_ambiental
python3.13 -m venv env --without-pip
source env/bin/activate
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.13 - --target env/lib/python3.13/site-packages
env/lib/python3.13/site-packages/bin/pip install numpy --target env/lib/python3.13/site-packages
sudo apt install python3.13-tk
```

## Ejecución

```bash
python3.13 main.py
```

## Modos de ejecución

| Modo | Mecanismos | Descripción |
|------|-----------|-------------|
| Secuencial | Ninguno | Línea base sin concurrencia |
| Hilos | Lock + Barrier | Paralelismo basado en threading |
| Procesos | Queue + Semaphore | Paralelismo basado en multiprocessing |

## Estructura del proyecto

medicion_ambiental/

├── models/

│   ├── medicion.py

│   ├── alerta.py

│   └── estacion.py

├── core/

│   ├── analizador.py

│   └── controlador.py

├── versions/

│   ├── secuencial.py

│   ├── hilos.py

│   └── procesos.py

├── gui/

│   └── app.py

└── main.py

## Variables monitoreadas

| Variable | Unidad | Umbral de alerta |
|----------|--------|-----------------|
| Temperatura | °C | > 22.0 |
| Humedad | % | > 85.0 |
| Ruido | dB | > 75.0 |
| CO2 | ppm | > 600.0 |
| PM2.5 | µg/m³ | > 25.0 |


