# SISMAU v1.0 — Sistema de Monitoreo Ambiental Urbano

Simulación de un sistema urbano de monitoreo ambiental para la ciudad de Cuenca, Ecuador.
Implementado con tres versiones de ejecución: secuencial, hilos y procesos.

**Práctica 04 — Computación Paralela — Universidad Politécnica Salesiana**

## Requisitos

- Python 3.13
- numpy

## Instalación

```bash
git clone https://github.com/paulAAV98/medicion_ambiental.git
cd medicion_ambiental
python3.13 -m venv env
source env/bin/activate
pip install numpy
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
## Variables monitoreadas

| Variable | Unidad | Umbral de alerta |
|----------|--------|-----------------|
| Temperatura | °C | > 22.0 |
| Humedad | % | > 85.0 |
| Ruido | dB | > 75.0 |
| CO2 | ppm | > 600.0 |
| PM2.5 | µg/m³ | > 25.0 |
