import tkinter as tk
from tkinter import ttk
import threading
import time
import platform
import sys
import os
from datetime import datetime


VERDE = "#00ff41"
VERDE_DIM = "#00aa2a"
VERDE_OSCURO = "#003010"
NEGRO = "#000000"
NEGRO_PANEL = "#050f05"
AMBER = "#ffb000"
ROJO = "#ff2020"
CYAN = "#00ffcc"


class PanelDesplegable(tk.Frame):

    def __init__(self, parent, titulo, color_titulo=CYAN):
        super().__init__(parent, bg=NEGRO)
        self.expandido = False

        self.header = tk.Frame(self, bg=NEGRO_PANEL, cursor="hand2")
        self.header.pack(fill=tk.X)
        self.header.bind("<Button-1>", self._toggle)

        self.lbl_titulo = tk.Label(self.header,
                                    text=f"┌─[ {titulo} ]  [+]",
                                    bg=NEGRO_PANEL, fg=color_titulo,
                                    font=("Courier", 9, "bold"),
                                    cursor="hand2")
        self.lbl_titulo.pack(anchor=tk.W, padx=8, pady=4)
        self.lbl_titulo.bind("<Button-1>", self._toggle)

        self.contenido = tk.Frame(self, bg=NEGRO)

    def _toggle(self, event=None):
        self.expandido = not self.expandido
        if self.expandido:
            self.contenido.pack(fill=tk.X, padx=4)
            self.lbl_titulo.config(
                text=self.lbl_titulo.cget("text").replace("[+]", "[-]"))
        else:
            self.contenido.pack_forget()
            self.lbl_titulo.config(
                text=self.lbl_titulo.cget("text").replace("[-]", "[+]"))

    def actualizar(self, alertas):
        for w in self.contenido.winfo_children():
            w.destroy()

        if not alertas:
            tk.Label(self.contenido, text="  Sin alertas registradas",
                     bg=NEGRO, fg=VERDE_DIM,
                     font=("Courier", 8)).pack(anchor=tk.W, padx=8, pady=4)
            return

        por_zona = {}
        for a in alertas:
            if a.zona not in por_zona:
                por_zona[a.zona] = []
            por_zona[a.zona].append(a)

        zonas_ordenadas = sorted(por_zona.items(),
                                  key=lambda x: len(x[1]), reverse=True)

        for zona, alertas_zona in zonas_ordenadas:
            zona_frame = tk.Frame(self.contenido, bg=NEGRO)
            zona_frame.pack(fill=tk.X, pady=1)

            expandido_zona = tk.BooleanVar(value=False)
            detalle_frame = tk.Frame(self.contenido, bg=NEGRO)

            def hacer_toggle(df=detalle_frame, ev=expandido_zona, zf=zona_frame):
                ev.set(not ev.get())
                if ev.get():
                    df.pack(fill=tk.X, padx=16)
                    for w in zf.winfo_children():
                        if isinstance(w, tk.Label):
                            txt = w.cget("text")
                            if "▶" in txt:
                                w.config(text=txt.replace("▶", "▼"))
                else:
                    df.pack_forget()
                    for w in zf.winfo_children():
                        if isinstance(w, tk.Label):
                            txt = w.cget("text")
                            if "▼" in txt:
                                w.config(text=txt.replace("▼", "▶"))

            color_zona = ROJO if len(alertas_zona) >= 5 else AMBER if len(alertas_zona) >= 3 else VERDE_DIM
            lbl_zona = tk.Label(zona_frame,
                                text=f"  ▶ {zona:<20} ({len(alertas_zona)} alertas)",
                                bg=NEGRO, fg=color_zona,
                                font=("Courier", 8, "bold"),
                                cursor="hand2")
            lbl_zona.pack(anchor=tk.W)
            lbl_zona.bind("<Button-1>", lambda e, t=hacer_toggle: t())
            zona_frame.bind("<Button-1>", lambda e, t=hacer_toggle: t())

            for a in alertas_zona:
                tk.Label(detalle_frame,
                         text=f"    [{a.timestamp.strftime('%H:%M:%S')}] {a.variable}: {a.valor:.1f} {a.unidad} (max:{a.umbral:.0f}) — {a.estacion}",
                         bg=NEGRO, fg=ROJO,
                         font=("Courier", 8)).pack(anchor=tk.W)


class AplicacionGUI:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("SISMAU v1.0 — Sistema de Monitoreo Ambiental Urbano")
        self.root.geometry("1500x900")
        self.root.configure(bg=NEGRO)
        self.root.resizable(True, True)

        self.modo_var = tk.StringVar(value="secuencial")
        self.ciclos_var = tk.IntVar(value=10)
        self.estaciones_var = tk.IntVar(value=4)
        self.ejecutando = False
        self.tiempo_inicio = None
        self.hora_inicio = None
        self.tarjetas = {}

        self._construir_ui()
        self._actualizar_reloj()

    def _construir_ui(self):
        header = tk.Frame(self.root, bg=NEGRO_PANEL, pady=6)
        header.pack(fill=tk.X)

        tk.Label(header,
                 text="█▀▀ █▀ █▀ █▀▄▀█ ▄▀█ █ █ ░ █▀ █ █▀ ▀█▀ █▀▀ █▀▄▀█ ▄▀█",
                 bg=NEGRO_PANEL, fg=VERDE_OSCURO,
                 font=("Courier", 7)).pack()
        tk.Label(header,
                 text="[ SISMAU v1.0 — SISTEMA DE MONITOREO AMBIENTAL URBANO — CUENCA, ECUADOR ]",
                 bg=NEGRO_PANEL, fg=VERDE,
                 font=("Courier", 12, "bold")).pack()

        fila_info = tk.Frame(header, bg=NEGRO_PANEL)
        fila_info.pack(fill=tk.X, padx=20)

        self.lbl_estado_sys = tk.Label(fila_info, text="● SISTEMA EN ESPERA",
                                        bg=NEGRO_PANEL, fg=VERDE_DIM,
                                        font=("Courier", 9))
        self.lbl_estado_sys.pack(side=tk.LEFT)

        self.lbl_tiempo = tk.Label(fila_info, text="[ 00:00.00 ]",
                                    bg=NEGRO_PANEL, fg=AMBER,
                                    font=("Courier", 12, "bold"))
        self.lbl_tiempo.pack(side=tk.RIGHT)

        ctrl = tk.Frame(self.root, bg=NEGRO_PANEL, pady=6,
                        highlightbackground=VERDE_OSCURO, highlightthickness=1)
        ctrl.pack(fill=tk.X)

        tk.Label(ctrl, text=" > MODO:", bg=NEGRO_PANEL, fg=VERDE_DIM,
                 font=("Courier", 9)).pack(side=tk.LEFT, padx=(10, 4))

        for modo, color in [("SECUENCIAL", VERDE),
                             ("HILOS",      CYAN),
                             ("PROCESOS",   AMBER)]:
            tk.Radiobutton(ctrl, text=f"[{modo}]",
                           variable=self.modo_var, value=modo.lower(),
                           font=("Courier", 9, "bold"),
                           bg=NEGRO_PANEL, fg=color,
                           selectcolor=NEGRO,
                           activebackground=NEGRO_PANEL,
                           activeforeground=color,
                           indicatoron=0,
                           relief=tk.FLAT,
                           padx=6).pack(side=tk.LEFT, padx=3)

        tk.Label(ctrl, text="  CICLOS:", bg=NEGRO_PANEL, fg=VERDE_DIM,
                 font=("Courier", 9)).pack(side=tk.LEFT, padx=(10, 4))
        tk.Spinbox(ctrl, from_=10, to=30, textvariable=self.ciclos_var,
                   width=3, font=("Courier", 10, "bold"),
                   bg=NEGRO, fg=VERDE,
                   buttonbackground=NEGRO_PANEL,
                   relief=tk.FLAT).pack(side=tk.LEFT)

        tk.Label(ctrl, text="  ESTACIONES:", bg=NEGRO_PANEL, fg=VERDE_DIM,
                 font=("Courier", 9)).pack(side=tk.LEFT, padx=(10, 4))
        tk.Spinbox(ctrl, from_=4, to=12, textvariable=self.estaciones_var,
                   width=3, font=("Courier", 10, "bold"),
                   bg=NEGRO, fg=VERDE,
                   buttonbackground=NEGRO_PANEL,
                   relief=tk.FLAT).pack(side=tk.LEFT)

        self.btn = tk.Button(ctrl, text="[ EJECUTAR ]",
                             font=("Courier", 10, "bold"),
                             bg=NEGRO, fg=VERDE,
                             activebackground=VERDE_OSCURO,
                             activeforeground=VERDE,
                             relief=tk.FLAT, padx=12, pady=2,
                             cursor="hand2",
                             command=self._iniciar)
        self.btn.pack(side=tk.LEFT, padx=20)

        self.lbl_ciclo = tk.Label(ctrl, text="",
                                   font=("Courier", 9),
                                   bg=NEGRO_PANEL, fg=VERDE_DIM)
        self.lbl_ciclo.pack(side=tk.LEFT)

        cuerpo = tk.Frame(self.root, bg=NEGRO)
        cuerpo.pack(fill=tk.BOTH, expand=True)

        col_izq = tk.Frame(cuerpo, bg=NEGRO_PANEL,
                           highlightbackground=VERDE_OSCURO,
                           highlightthickness=1)
        col_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 1))

        tk.Label(col_izq, text="┌─[ ESTACIONES ACTIVAS ]",
                 bg=NEGRO_PANEL, fg=VERDE,
                 font=("Courier", 9, "bold")).pack(anchor=tk.W, padx=8, pady=(6, 2))

        self.canvas = tk.Canvas(col_izq, bg=NEGRO_PANEL, highlightthickness=0)
        self.frame_estaciones = tk.Frame(self.canvas, bg=NEGRO_PANEL)
        self.frame_estaciones.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.frame_estaciones, anchor=tk.NW)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        tk.Label(col_izq, text="┌─[ ALERTAS DEL SISTEMA ]",
                 bg=NEGRO_PANEL, fg=ROJO,
                 font=("Courier", 9, "bold")).pack(anchor=tk.W, padx=8, pady=(8, 2))

        self.lista_alertas = tk.Listbox(col_izq,
                                         bg=NEGRO, fg=ROJO,
                                         font=("Courier", 11, "bold"),
                                         selectbackground=VERDE_OSCURO,
                                         highlightthickness=0,
                                         relief=tk.FLAT,
                                         height=7)
        self.lista_alertas.pack(fill=tk.X, padx=6, pady=(0, 8))

        col_der = tk.Frame(cuerpo, bg=NEGRO_PANEL, width=400,
                           highlightbackground=VERDE_OSCURO,
                           highlightthickness=1)
        col_der.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(1, 0))
        col_der.pack_propagate(False)

        canvas_der = tk.Canvas(col_der, bg=NEGRO_PANEL, highlightthickness=0)
        scroll_der = ttk.Scrollbar(col_der, orient=tk.VERTICAL,
                                    command=canvas_der.yview)
        frame_der = tk.Frame(canvas_der, bg=NEGRO_PANEL)
        frame_der.bind("<Configure>", lambda e: canvas_der.configure(
            scrollregion=canvas_der.bbox("all")))
        canvas_der.create_window((0, 0), window=frame_der, anchor=tk.NW)
        canvas_der.configure(yscrollcommand=scroll_der.set)
        scroll_der.pack(side=tk.RIGHT, fill=tk.Y)
        canvas_der.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(frame_der, text="┌─[ ESTADÍSTICAS POR VARIABLE ]",
                 bg=NEGRO_PANEL, fg=CYAN,
                 font=("Courier", 9, "bold")).pack(anchor=tk.W, padx=8, pady=(6, 2))

        tabla_frame = tk.Frame(frame_der, bg=NEGRO)
        tabla_frame.pack(fill=tk.X, padx=8, pady=(0, 6))

        encabezados = ["VARIABLE", "PROM", "MÁX", "MÍN", "N"]
        anchos = [12, 8, 8, 8, 6]
        fila_enc = tk.Frame(tabla_frame, bg=NEGRO_PANEL)
        fila_enc.pack(fill=tk.X)
        for enc, ancho in zip(encabezados, anchos):
            tk.Label(fila_enc, text=enc, font=("Courier", 8, "bold"),
                     bg=NEGRO_PANEL, fg=CYAN,
                     width=ancho, anchor=tk.W).pack(side=tk.LEFT, padx=2)

        self.filas_tabla = {}
        for var in ["temperatura", "humedad", "ruido", "CO2", "PM2.5"]:
            fila = tk.Frame(tabla_frame, bg=NEGRO)
            fila.pack(fill=tk.X, pady=1)
            labels = []
            tk.Label(fila, text=var.upper(), font=("Courier", 8),
                     bg=NEGRO, fg=VERDE_DIM,
                     width=12, anchor=tk.W).pack(side=tk.LEFT, padx=2)
            for ancho in [8, 8, 8, 6]:
                lbl = tk.Label(fila, text="---", font=("Courier", 8, "bold"),
                               bg=NEGRO, fg=VERDE,
                               width=ancho, anchor=tk.W)
                lbl.pack(side=tk.LEFT, padx=2)
                labels.append(lbl)
            self.filas_tabla[var] = labels

        tk.Label(frame_der, text="┌─[ UMBRALES DE REFERENCIA ]",
                 bg=NEGRO_PANEL, fg=AMBER,
                 font=("Courier", 9, "bold")).pack(anchor=tk.W, padx=8, pady=(8, 2))

        umbrales_frame = tk.Frame(frame_der, bg=NEGRO)
        umbrales_frame.pack(fill=tk.X, padx=8, pady=(0, 6))

        for var, limite in [
            ("TEMPERATURA", "> 22.0 °C"),
            ("HUMEDAD",     "> 85.0 %"),
            ("RUIDO",       "> 75.0 dB"),
            ("CO2",         "> 600.0 ppm"),
            ("PM2.5",       "> 25.0 µg/m³"),
        ]:
            fila = tk.Frame(umbrales_frame, bg=NEGRO)
            fila.pack(fill=tk.X, pady=1)
            tk.Label(fila, text=f"  {var:<14}",
                     bg=NEGRO, fg=VERDE_DIM,
                     font=("Courier", 8)).pack(side=tk.LEFT)
            tk.Label(fila, text=limite,
                     bg=NEGRO, fg=AMBER,
                     font=("Courier", 8, "bold")).pack(side=tk.LEFT)

        tk.Label(frame_der, text="┌─[ MÉTRICAS DE EJECUCIÓN ]",
                 bg=NEGRO_PANEL, fg=CYAN,
                 font=("Courier", 9, "bold")).pack(anchor=tk.W, padx=8, pady=(8, 2))

        self.frame_stats = tk.Frame(frame_der, bg=NEGRO)
        self.frame_stats.pack(fill=tk.X, padx=8, pady=(0, 2))

        self.stats_labels = {}
        for key, label in [
            ("modo",       "MODO"),
            ("estaciones", "ESTACIONES"),
            ("ciclos",     "CICLOS"),
            ("mediciones", "MEDICIONES"),
            ("alertas",    "ALERTAS"),
            ("tiempo",     "TIEMPO TOTAL"),
            ("med_seg",    "MED/SEGUNDO"),
            ("zona",       "ZONA RIESGO"),
        ]:
            fila = tk.Frame(self.frame_stats, bg=NEGRO)
            fila.pack(fill=tk.X, pady=1)
            tk.Label(fila, text=f"  {label:<14}:",
                     bg=NEGRO, fg=VERDE_DIM,
                     font=("Courier", 8),
                     width=18, anchor=tk.W).pack(side=tk.LEFT)
            lbl = tk.Label(fila, text="---",
                           font=("Courier", 9, "bold"),
                           bg=NEGRO, fg=VERDE, anchor=tk.W)
            lbl.pack(side=tk.LEFT)
            self.stats_labels[key] = lbl

        self.panel_desplegable = PanelDesplegable(
            frame_der, "DETALLE DE ALERTAS POR ZONA", ROJO)
        self.panel_desplegable.pack(fill=tk.X, padx=4, pady=(8, 4))

        footer = tk.Frame(self.root, bg=NEGRO, pady=3)
        footer.pack(fill=tk.X, side=tk.BOTTOM)

        info = (
            f"  Python {sys.version.split()[0]}  |  "
            f"{platform.system()} {platform.release()}  |  "
            f"CPU: {os.cpu_count()} núcleos  |  "
            f"GIL: {'ACTIVO' if not getattr(sys.flags, 'nogil', False) else 'DESACTIVADO'}"
        )
        tk.Label(footer, text=info, font=("Courier", 8),
                 bg=NEGRO, fg=VERDE_DIM).pack(side=tk.LEFT)

    def _crear_tarjetas(self, estaciones):
        for w in self.frame_estaciones.winfo_children():
            w.destroy()
        self.tarjetas = {}

        cols = 4
        for i, e in enumerate(estaciones):
            frame = tk.Frame(self.frame_estaciones, bg=NEGRO,
                              highlightbackground=VERDE_OSCURO,
                              highlightthickness=1,
                              padx=8, pady=6)
            frame.grid(row=i // cols, column=i % cols,
                       padx=4, pady=4, sticky=tk.NSEW)

            tk.Label(frame, text=f"[ {e.nombre} ]",
                     bg=NEGRO, fg=VERDE,
                     font=("Courier", 9, "bold")).pack(anchor=tk.W)
            tk.Label(frame, text=f"  {e.zona}",
                     bg=NEGRO, fg=VERDE_DIM,
                     font=("Courier", 8)).pack(anchor=tk.W)

            lbl_estado = tk.Label(frame, text="  ○ INACTIVA",
                                   bg=NEGRO, fg=VERDE_DIM,
                                   font=("Courier", 8, "bold"))
            lbl_estado.pack(anchor=tk.W, pady=(2, 4))

            tk.Label(frame, text="  " + "·" * 20,
                     bg=NEGRO, fg=VERDE_OSCURO,
                     font=("Courier", 7)).pack(anchor=tk.W)

            var_labels = {}
            for var in e.variables:
                fila = tk.Frame(frame, bg=NEGRO)
                fila.pack(fill=tk.X)
                tk.Label(fila, text=f"  {var.upper():<12}",
                         bg=NEGRO, fg=VERDE_DIM,
                         font=("Courier", 8)).pack(side=tk.LEFT)
                lbl_val = tk.Label(fila, text="---",
                                   bg=NEGRO, fg=VERDE,
                                   font=("Courier", 9, "bold"))
                lbl_val.pack(side=tk.LEFT)
                var_labels[var] = lbl_val

            self.tarjetas[e.nombre] = (lbl_estado, var_labels)

        for c in range(cols):
            self.frame_estaciones.columnconfigure(c, weight=1)

    def actualizar_estaciones(self, estaciones, alertas_set=None):
        alertas_set = alertas_set or set()
        estados_texto = {
            "activa":     ("● ACTIVA",     VERDE),
            "esperando":  ("○ ESPERANDO",  CYAN),
            "procesando": ("◉ PROCESANDO", AMBER),
            "finalizada": ("□ FINALIZADA", VERDE_DIM),
            "inactiva":   ("○ INACTIVA",   VERDE_DIM),
        }
        for e in estaciones:
            if e.nombre not in self.tarjetas:
                continue
            lbl_estado, var_labels = self.tarjetas[e.nombre]
            texto, color = estados_texto.get(e.estado, ("○ INACTIVA", VERDE_DIM))
            lbl_estado.config(text=f"  {texto}", fg=color)
            for var, lbl in var_labels.items():
                m = e.get_ultima_medicion(var)
                if m:
                    tiene_alerta = (e.nombre, var) in alertas_set
                    lbl.config(text=f"{m.valor:.1f} {m.unidad}",
                               fg=ROJO if tiene_alerta else VERDE)

    def actualizar_alertas(self, alertas):
        self.lista_alertas.delete(0, tk.END)
        for a in alertas[-20:]:
            self.lista_alertas.insert(tk.END,
                f" [{a.timestamp.strftime('%H:%M:%S')}] {a.zona} | {a.variable}: {a.valor:.1f} {a.unidad} (max:{a.umbral:.0f})")
        if alertas:
            self.lista_alertas.see(tk.END)

    def actualizar_tabla_stats(self, estadisticas: dict):
        for var, labels in self.filas_tabla.items():
            if var in estadisticas:
                s = estadisticas[var]
                labels[0].config(text=f"{s['promedio']:.2f}")
                labels[1].config(text=f"{s['maximo']:.2f}")
                labels[2].config(text=f"{s['minimo']:.2f}")
                labels[3].config(text=str(s['cantidad']))

    def actualizar_stats(self, stats: dict):
        self.stats_labels["modo"].config(text=stats.get("modo", "").upper())
        self.stats_labels["estaciones"].config(text=str(self.estaciones_var.get()))
        self.stats_labels["ciclos"].config(text=str(stats.get("num_ciclos", 0)))
        self.stats_labels["mediciones"].config(text=str(stats.get("total_mediciones", 0)))
        alertas = stats.get("total_alertas", 0)
        self.stats_labels["alertas"].config(
            text=str(alertas), fg=ROJO if alertas > 0 else VERDE)
        self.stats_labels["tiempo"].config(
            text=f"{stats.get('tiempo_total', 0):.3f}s")
        self.stats_labels["med_seg"].config(
            text=str(stats.get("mediciones_por_segundo", 0)))
        zona = stats.get("zona_mayor_riesgo", "---")
        self.stats_labels["zona"].config(
            text=zona, fg=ROJO if zona not in ("Ninguna", "---") else VERDE)

        alertas_lista = stats.get("_alertas", [])
        self.panel_desplegable.actualizar(alertas_lista)

    def _actualizar_reloj(self):
        if self.ejecutando and self.tiempo_inicio:
            elapsed = time.time() - self.tiempo_inicio
            mins = int(elapsed // 60)
            segs = elapsed % 60
            self.lbl_tiempo.config(text=f"[ {mins:02d}:{segs:05.2f} ]")
        self.root.after(100, self._actualizar_reloj)

    def _iniciar(self):
        if self.ejecutando:
            return
        self.ejecutando = True
        self.tiempo_inicio = time.time()
        self.hora_inicio = datetime.now().strftime("%H:%M:%S")
        self.btn.config(state=tk.DISABLED, text="[ CORRIENDO... ]")
        self.lbl_estado_sys.config(text="● SIMULACIÓN EN CURSO", fg=VERDE)
        hilo = threading.Thread(target=self._correr_simulacion, daemon=True)
        hilo.start()

    def _correr_simulacion(self):
        from versions.secuencial import SimulacionSecuencial
        from versions.hilos import SimulacionHilos
        from versions.procesos import SimulacionProcesos

        modo = self.modo_var.get()
        ciclos = self.ciclos_var.get()
        estaciones = self.estaciones_var.get()

        if modo == "secuencial":
            sim = SimulacionSecuencial(num_ciclos=ciclos, num_estaciones=estaciones)
        elif modo == "hilos":
            sim = SimulacionHilos(num_ciclos=ciclos, num_estaciones=estaciones)
        else:
            sim = SimulacionProcesos(num_ciclos=ciclos, num_estaciones=estaciones)

        self.root.after(0, lambda: self._crear_tarjetas(sim.estaciones))
        time.sleep(0.1)

        if modo == "secuencial":
            import time as t
            inicio = t.time()
            for ciclo in range(1, sim.num_ciclos + 1):
                self.root.after(0, lambda c=ciclo: self.lbl_ciclo.config(
                    text=f"CICLO {c:02d}/{ciclos}"))
                mediciones_ciclo = []
                for estacion in sim.estaciones:
                    mediciones = estacion.generar_ciclo(ciclo)
                    mediciones_ciclo.extend(mediciones)
                sim.mediciones.extend(mediciones_ciclo)
                alertas_ciclo = sim._verificar_alertas(mediciones_ciclo)
                resultado = sim.analizador.procesar(mediciones_ciclo, alertas_ciclo)
                sim.resultados_por_ciclo.append(resultado)
                alertas_set = {(a.estacion, a.variable) for a in sim.alertas}
                self.root.after(0, lambda: self.actualizar_estaciones(
                    sim.estaciones, alertas_set))
                self.root.after(0, lambda: self.actualizar_alertas(sim.alertas))
                self.root.after(0, lambda r=resultado: self.actualizar_tabla_stats(
                    r.get("estadisticas", {})))
                print(f"  Ciclo {ciclo:02d}... ✓")
            sim.tiempo_total = t.time() - inicio
            sim.imprimir_resumen()
        else:
            sim.ejecutar()
            alertas_set = {(a.estacion, a.variable) for a in sim.alertas}
            self.root.after(0, lambda: self.actualizar_estaciones(
                sim.estaciones, alertas_set))
            self.root.after(0, lambda: self.actualizar_alertas(sim.alertas))
            if sim.resultados_por_ciclo:
                ultimo = sim.resultados_por_ciclo[-1]
                self.root.after(0, lambda: self.actualizar_tabla_stats(
                    ultimo.get("estadisticas", {})))

        stats = sim.get_estadisticas_finales()
        stats["zona_mayor_riesgo"] = sim.analizador._zona_mayor_riesgo(sim.alertas)
        stats["_alertas"] = sim.alertas
        hora_fin = datetime.now().strftime("%H:%M:%S")

        self.root.after(0, lambda: self.actualizar_stats(stats))
        self.root.after(0, lambda: self.lbl_ciclo.config(text="[ COMPLETADO ]"))
        self.root.after(0, lambda hf=hora_fin: self.lbl_estado_sys.config(
            text=f"● FINALIZADA | INICIO: {self.hora_inicio} — FIN: {hf}", fg=CYAN))
        self.root.after(0, lambda: self.btn.config(
            state=tk.NORMAL, text="[ EJECUTAR ]"))
        self.ejecutando = False