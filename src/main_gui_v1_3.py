"""
comando de ejecución EN LA CONSOLA DEL IDE O DESDE LA CARPETA DONDE ESTÁN LOS .PY:
python main_gui_v0_2.py
"""

import os
import io
import ctypes
import json
import threading 
import customtkinter as ctk 
from tkinter import filedialog #  Para abrir la ventana de Windows de seleccionar archivos
from tkinter import messagebox

import data_processor_v1_1 as dp
import genetics_engine_v1_0 as ge
import mantenimiento_api_v1_0 as tr

#  Configuramos el tema general de la aplicación (Modo claro/oscuro automático)
ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue") 

#  Desvincular la app del icono genérico de Python en la barra de tareas
try:
    myappid = 'DAF' # Identificador único de tu app
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

# Encontrar la ruta exacta de logo.ico basándose en la estructura de carpetas
# __file__ es main_gui_v1_0.py. dirname saca 'src'. El segundo dirname saca 'DAF_APP'.
ruta_src = os.path.dirname(os.path.abspath(__file__))
ruta_base = os.path.dirname(ruta_src)
ruta_icono = os.path.join(ruta_base, "logo.ico")



def mostrar_splash():
    splash = ctk.CTk()
    splash.title("Iniciando DAF")
    
    # Hacer la ventana pequeña y centrarla
    ancho, alto = 400, 200
    x = (splash.winfo_screenwidth() // 2) - (ancho // 2)
    y = (splash.winfo_screenheight() // 2) - (alto // 2)
    splash.geometry(f"{ancho}x{alto}+{x}+{y}")
    
    # Quitar los bordes de la ventana para que parezca profesional
    splash.overrideredirect(True)
    
    label = ctk.CTkLabel(splash, text="DAF\nCargando sistema clínico...", font=("Arial", 20, "bold"))
    label.pack(expand=True)
    
    # Barra de progreso visual (opcional)
    progreso = ctk.CTkProgressBar(splash)
    progreso.pack(pady=20)
    progreso.start()
    
    # Cerramos el splash después de 3 segundos (o cuando decidas)
    splash.after(3000, splash.destroy)
    splash.mainloop()

def ejecutar_analisis(ruta_archivo, file_name, gene_target, medicamento):
    # guardar archivo subido
    json_path = dp.clean_single_data(ruta_archivo, file_name, medicamento)


    with open(json_path, "r", encoding="utf-8") as f:
        datos_crudos = json.load(f)

    paciente_id = file_name.replace('.tab', '')
    datos_listos = ge.preparar_datos_para_reglas(datos_crudos, paciente_id)

    ge.analizar_genoma(datos_listos, nombre_gen=gene_target)

    return ge.diagnosticos_pacientes.get(paciente_id, {}).get(gene_target, [])


class AplicacionXenoma(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🧬 Detección Automática de Fenotipos - DAF")
        self.geometry("1100x700")

        #  Variables para gestionar los filtros y las tarjetas
        self.mostrar_solo_anormales = False 
        self.lista_tarjetas = [] # Aquí guardaremos (tarjeta_widget, es_anormal_booleano)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        
        # --- barra lateral
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar_frame, text="🧬 DAF", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 5))
        ctk.CTkLabel(self.sidebar_frame, text="Detección Automática de Fenotipos", font=ctk.CTkFont(size=12)).pack(pady=(0, 20))

        ctk.CTkLabel(self.sidebar_frame, text="Carga de Datos", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))
        
        self.btn_cargar = ctk.CTkButton(self.sidebar_frame, text="Subir archivos (.tab)", command=self.cargar_archivos)
        self.btn_cargar.pack(pady=10, padx=20)

        ctk.CTkLabel(self.sidebar_frame, text="Gen a analizar:").pack(pady=(20, 0))
        self.gene_target_menu = ctk.CTkOptionMenu(self.sidebar_frame, values=["CYP2C19"], state="disabled")
        self.gene_target_menu.pack(pady=5, padx=20)

        ctk.CTkLabel(self.sidebar_frame, text="Medicamento:").pack(pady=(10, 0))
        self.drug_target_menu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Clopidogrel"], state="disabled")
        self.drug_target_menu.pack(pady=5, padx=20)

        # --- Sección de filtros en la barra lateral
        ctk.CTkLabel(self.sidebar_frame, text="Acciones Visuales", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(40, 10))

        self.btn_filtro = ctk.CTkButton(
            self.sidebar_frame,
            text="⚠️ Ocultar Sanos",
            command=self.alternar_filtro,
            fg_color="#ffc107",
            text_color="black",
            hover_color="#e0a800",
            state="disabled"  # bloquea el boton al inicio
        )
        self.btn_filtro.pack(pady=10, padx=20)

        self.btn_limpiar = ctk.CTkButton(self.sidebar_frame, text="🗑️ Limpiar Pantalla", command=self.limpiar_pantalla, fg_color="#dc3545", hover_color="#c82333")
        self.btn_limpiar.pack(pady=10, padx=20)

        
        # --- Zona principal

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.texto_estado = ctk.CTkLabel(self.main_frame, text="Sube uno o varios archivos en el panel izquierdo para comenzar.", font=ctk.CTkFont(size=14))
        self.texto_estado.pack(anchor="w", pady=(0, 10))

        self.barra_progreso = ctk.CTkProgressBar(self.main_frame)
        self.barra_progreso.pack(fill="x", pady=(0, 20))
        self.barra_progreso.set(0)

        self.scroll_resultados = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.scroll_resultados.pack(fill="both", expand=True)


    # --- Funciones de filtrado y limpieza

    def alternar_filtro(self):
        """Activa o desactiva la visualización exclusiva de pacientes con problemas"""
        self.mostrar_solo_anormales = not self.mostrar_solo_anormales

        if self.mostrar_solo_anormales:
            self.btn_filtro.configure(text="👁️ Mostrar Todos", fg_color="#17a2b8", text_color="white", hover_color="#138496")
        else:
            self.btn_filtro.configure(text="⚠️ Ocultar Sanos", fg_color="#ffc107", text_color="black", hover_color="#e0a800")
        
        self.actualizar_vista_tarjetas()

    def actualizar_vista_tarjetas(self):
        """Oculta o muestra las tarjetas sin eliminarlas de la memoria según el filtro"""
        try:
            self.scroll_resultados._parent_canvas.yview_moveto(0)
        except Exception:
            pass
        
        # Ocultamos todas las tarjetas visualmente (pack_forget no las borra, solo las esconde)
        for tarjeta, _ in self.lista_tarjetas:
            if tarjeta.winfo_exists(): # Si no ha sido destruida por la "X"
                tarjeta.pack_forget()
        
        # Volvemos a colocar (pack) solo las que correspondan, en su orden original
        for tarjeta, es_anormal in self.lista_tarjetas:
            if tarjeta.winfo_exists():
                if self.mostrar_solo_anormales and not es_anormal:
                    continue # Saltamos a los sanos
                tarjeta.pack(fill="x", pady=5, padx=5)

    def limpiar_pantalla(self):
        if not self.lista_tarjetas:
            return

        confirmar = messagebox.askyesno(
            "DAF - Confirmación",
            "¿Confirmas que deseas limpiar todos los resultados de la pantalla?"
        )

        if confirmar:  # El código de borrado SOLO se ejecuta si la respuesta es True
            for tarjeta, _ in self.lista_tarjetas:
                if tarjeta.winfo_exists():
                    tarjeta.destroy()

            self.lista_tarjetas.clear()
            self.texto_estado.configure(text="Pantalla limpia. Listo para nueva carga.")
            self.barra_progreso.set(0)
            self.btn_filtro.configure(state="disabled")
            self.update_idletasks()
    # --- Logica del procesamiento

    def cargar_archivos(self):
        rutas_archivos = filedialog.askopenfilenames(
            title="Seleccionar archivos de secuenciación",
            filetypes=[("Archivos TAB", "*.tab"), ("Archivos de texto", "*.txt")]
        )

        if not rutas_archivos:
            return

        # Validación de carga masiva
        if len(rutas_archivos) > 50:
            # Importante: messagebox detiene la ejecución del hilo principal
            continuar = messagebox.askokcancel(
                "Aviso de Seguridad",
                f"Has seleccionado {len(rutas_archivos)} archivos.\n Tanta cantidad de archivos puede ralentizar el procesamiento, se recomiendan un máximo de 50\n ¿Quieres continuar de todos modos?"
            )
            if not continuar:
                return  # Si el usuario cancela, la función muere aquí

        # Bloqueo visual forzado
        self.btn_filtro.configure(state="disabled")
        self.update_idletasks()  # Fuerza a Windows a redibujar el botón bloqueado

        hilo_analisis = threading.Thread(target=self.procesar_lote, args=(rutas_archivos,))
        hilo_analisis.start()

    def procesar_lote(self, rutas_archivos):
        total_archivos = len(rutas_archivos)

        #Reiniciamos la barra de progreso para el nuevo lote
        self.barra_progreso.set(0)

        # 2. Cambiamos el mensaje para que sea más descriptivo
        self.texto_estado.configure(
            text=f"### Añadiendo {total_archivos} nuevo(s) paciente(s) al análisis...", 
            text_color=("black", "white")
        )
        
        gene_target = self.gene_target_menu.get()
        # Capturamos el medicamento seleccionado en la interfaz
        medicamento_target = self.drug_target_menu.get()

        for i, ruta in enumerate(rutas_archivos):
            file_name = os.path.basename(ruta)
            paciente_id = file_name.replace('.tab', '')

            # Comprobar si ya existe una tarjeta para este ID (Evita duplicados visuales)
            # Buscamos en el atributo .paciente_id que creamos arriba
            ya_existe = any(paciente_id == getattr(t[0], 'paciente_id', None) 
                            for t in self.lista_tarjetas if t[0].winfo_exists())
            if ya_existe:
                print(f"  [Info] El paciente {paciente_id} ya está en pantalla. Saltando...")
                continue # Pasa al siguiente archivo del bucle sin hacer nada más
            
            # Si NO existe, procedemos con el análisis normal
            self.texto_estado.configure(text=f"⏳ Procesando {i+1}/{total_archivos}: {paciente_id}...")

            try:
                alelos_detectados = ejecutar_analisis(ruta, file_name, gene_target, medicamento= self.drug_target_menu.get())
                
                if medicamento_target == "Clopidogrel":
                    genotipo, fenotipo = tr.traduccion_clopy(alelos_detectados)
                # elif medicamento_target == "otro_medicamento":
                #     genotipo, fenotipo = tr.traduccion_otro_medicamento(alelos_detectados)
                else:
                    genotipo = "Desconocido"
                    fenotipo = "Medicamento no implementado"

                self.crear_tarjeta_paciente(paciente_id, genotipo, fenotipo)

            except Exception as e:
                self.crear_tarjeta_error(paciente_id, str(e))

            self.barra_progreso.set((i + 1) / total_archivos)

        self.texto_estado.configure(text=f"✅ ¡Análisis de {total_archivos} paciente(s) completado con éxito!", text_color="#198754")
        self.btn_filtro.configure(state="normal") # desbloquea el boton de filtro
        self.update_idletasks()
        # Una vez termina el análisis, forzamos la actualización de vista por si el filtro estaba activo
        self.actualizar_vista_tarjetas()

    # --- Creación de tarjetas visuales

    def crear_tarjeta_paciente(self, paciente_id, genotipo, fenotipo):
        card = ctk.CTkFrame(self.scroll_resultados, fg_color=("gray95", "gray15"), corner_radius=8)
        card.paciente_id = paciente_id

        # Botón de la "X" para cerrar esta tarjeta específica
        btn_x = ctk.CTkButton(card, text="✖", width=25, height=25, fg_color="transparent", text_color="gray", hover_color="#dc3545", command=card.destroy)
        btn_x.grid(row=0, column=1, sticky="e", padx=10, pady=(10, 5))

        entry_id = ctk.CTkEntry(card, font=ctk.CTkFont(weight="bold"), fg_color="transparent", border_width=0, width=400)
        entry_id.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        entry_id.insert(0, f"👤 Resultados para: {paciente_id}")
        entry_id.configure(state="readonly")

        col1 = ctk.CTkFrame(card, fg_color="transparent")
        col1.grid(row=1, column=0, sticky="nw", padx=15, pady=10)
        
        ctk.CTkLabel(col1, text="Genotipo Detectado", font=ctk.CTkFont(size=12)).pack(anchor="w")
        
        entry_geno = ctk.CTkEntry(col1, font=ctk.CTkFont(size=20, weight="bold"), fg_color="transparent", border_width=0, width=350)
        entry_geno.pack(anchor="w", pady=(0, 10))
        entry_geno.insert(0, genotipo)
        entry_geno.configure(state="readonly")

        medicamento =self.drug_target_menu.get()


        # --- ENRUTADOR DE MEDICAMENTOS PARA LAS RECOMENDACIONES 
        if medicamento == "Clopidogrel":
            color_fondo, color_texto, color_borde, alerta, es_anormal = tr.respuestas_clopy(fenotipo)
        # elif medicamento == "otro_medicamento":
        #     color_fondo, color_texto, color_borde, alerta, es_anormal = tr.respuestas_otro_medicamento(fenotipo)

        
        else:
            # Por si en el futuro se selecciona un medicamento a medio programar
            color_fondo = "#e2e3e5" 
            color_texto = "#41464b" 
            color_borde = "#6c757d"
            alerta = f"No hay módulo de respuestas configurado para {medicamento}."
            es_anormal = True

        entry_estado = ctk.CTkEntry(col1, font=ctk.CTkFont(weight="bold"), fg_color=color_fondo, text_color=color_texto, border_width=0, width=250)
        entry_estado.pack(anchor="w", ipadx=5, ipady=2)
        entry_estado.insert(0, f"ESTADO: {fenotipo}")
        entry_estado.configure(state="readonly")

        col2 = ctk.CTkFrame(card, fg_color=("white", "gray20"), border_width=2, border_color=color_borde, corner_radius=8)
        col2.grid(row=1, column=1, sticky="nsew", padx=15, pady=10)
        card.grid_columnconfigure(1, weight=1) 

        ctk.CTkLabel(col2, text="Recomendación Clínica", font=ctk.CTkFont(weight="bold"), text_color=color_texto).pack(anchor="w", padx=15, pady=(10, 0))
        
        txt_recomendacion = ctk.CTkTextbox(col2, fg_color="transparent", text_color=("black", "white"), height=60, wrap="word")
        txt_recomendacion.pack(fill="both", expand=True, padx=10, pady=5)
        txt_recomendacion.insert("0.0", alerta)
        txt_recomendacion.configure(state="disabled") 

        # Guardamos la tarjeta en memoria
        self.lista_tarjetas.append((card, es_anormal))
        
        # Se dibujan las tarjetas en tiempo real
        # Si el filtro de ocultar sanos está activado y el paciente es sano, no lo dibujamos aún.
        if not (self.mostrar_solo_anormales and not es_anormal):
            card.pack(fill="x", pady=5, padx=5)

    def crear_tarjeta_error(self, paciente_id, error_msg):
        card = ctk.CTkFrame(self.scroll_resultados, fg_color="#f8d7da", corner_radius=8)
        
        lbl = ctk.CTkLabel(card, text=f"❌ Error en {paciente_id}: {error_msg}", text_color="#842029", font=ctk.CTkFont(weight="bold"))
        lbl.pack(side="left", padx=15, pady=10)

        btn_x = ctk.CTkButton(card, text="✖", width=25, height=25, fg_color="transparent", text_color="#842029", hover_color="#c82333", command=card.destroy)
        btn_x.pack(side="right", padx=15, pady=10)

        self.lista_tarjetas.append((card, True))
        
        #  Los errores se dibujan siempre en tiempo real
        card.pack(fill="x", pady=5, padx=5)

if __name__ == "__main__":
    mostrar_splash()
    app = AplicacionXenoma()
    # Aplicar el icono (Asegúrate de que tu variable principal se llame 'app' o 'root', 
    app.iconbitmap(ruta_icono)
    app.mainloop()
