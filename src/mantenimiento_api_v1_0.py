import requests


# Así Python puede leerla y compararla automáticamente con la API
TRADUCCION_FENOTIPOS_LOCAL = {
    "*38/*38": "Normal Metabolizer",
    "*38/*2": "Intermediate Metabolizer",
    "*38/*3": "Intermediate Metabolizer",
    "*38/*4": "Intermediate Metabolizer",
    "*38/*17": "Rapid Metabolizer",
    
    "*2/*2": "Poor Metabolizer",
    "*2/*3": "Poor Metabolizer",
    "*2/*4": "Poor Metabolizer",              
    "*2/*17": "Intermediate Metabolizer",     
    
    "*3/*3": "Poor Metabolizer",
    "*3/*4": "Poor Metabolizer",              
    "*3/*17": "Intermediate Metabolizer",     
    
    "*4/*4": "Poor Metabolizer",             
    "*4/*17": "Intermediate Metabolizer",    
    
    "*17/*17": "Ultrarapid Metabolizer"
}



def traduccion_clopy(alelos_detectados):
    """Traduce usando el diccionario local (búsqueda ultrarrápida)"""
    if len(alelos_detectados) == 0:
        genotipo = "*38/*38" 
    elif len(alelos_detectados) == 1:
        genotipo = f"{alelos_detectados[0]}/*38"
    elif len(alelos_detectados) == 2:
        genotipo = f"{alelos_detectados[0]}/{alelos_detectados[1]}"
    else:
        mezcla = ", ".join(alelos_detectados)
        return f"⚠️ ANOMALÍA: [{mezcla}]", "Revisión Manual Requerida"
    
    # Buscamos en nuestro diccionario. Si no existe, devolvemos No Determinado
    
    a, b = genotipo.split("/")

    # Buscamos el genotipo. Si no está, Python evalúa el segundo .get() con el inverso
    fenotipo = TRADUCCION_FENOTIPOS_LOCAL.get(genotipo, 
               TRADUCCION_FENOTIPOS_LOCAL.get(f"{b}/{a}", "No determinado"))
    return genotipo, fenotipo

def respuestas_clopy(fenotipo):
    """Devuelve los colores y la alerta (Se queda igual porque esto es UI visual en español)"""
    es_anormal = True
    
    if "Poor" in fenotipo:
        # ROJO - Peligro clínico alto
        color_fondo = "#f8d7da" 
        color_texto = "#842029" 
        color_borde = "#dc3545"
        alerta = "La etiqueta de clopidogrel (Plavix) indica: 'Considere el uso de otro inhibidor plaquetario P2Y12 en pacientes identificados como metabolizadores pobres de CYP2C19.' Consulte la etiqueta."
        
    elif "Intermediate" in fenotipo:
        # AZUL OSCURO - Intermedios
        color_fondo = "#ecb6fe" 
        color_texto = "#523572" 
        color_borde = "#b70aca" 
        alerta = "Metabolizador Intermedio: Presenta una función enzimática reducida. Considere una terapia antiplaquetaria alternativa (ej. prasugrel o ticagrelor) si no hay contraindicaciones."

    elif "Ultrarapid" in fenotipo or "Rapid" in fenotipo:
        # MORADO - Rápidos y Ultrarrápidos
        color_fondo = "#0c0a10" 
        color_texto = "#877E99" 
        color_borde = "#342354" 
        alerta = "Metabolizador Rápido/Ultrarrápido: Función enzimática aumentada. Uso de clopidogrel a dosis estándar recomendado según guías actuales, pero considere riesgo potencial de sangrado."

    elif "Anomalía" in fenotipo or "Revisión" in fenotipo:
        # AMARILLO - Errores y combinaciones raras
        color_fondo = "#fff3cd" 
        color_texto = "#664d03" 
        color_borde = "#ffc107"
        alerta = "Se han detectado más de 2 alelos o una combinación ambigua. Se requiere revisión bioinformática."
        
    elif "No determinado" in fenotipo:
        # GRIS - Faltan datos o combinaciones desconocidas
        color_fondo = "#e2e3e5" 
        color_texto = "#41464b" 
        color_borde = "#6c757d" 
        alerta = "No se ha podido determinar el fenotipo exacto. Se recomienda consultar las guías actualizadas (CPIC)."
        
    else:
        # AZUL CLARO - Normal Metabolizer 
        color_fondo = "#cfe2ff" 
        color_texto = "#084298" 
        color_borde = "#0d6efd" # Borde azul estándar
        alerta = "Este genotipo/fenotipo no tiene recomendación especial (Respuesta esperada normal)."
        es_anormal = False 
        
    return color_fondo, color_texto, color_borde, alerta, es_anormal

# subfunciones de auditoria

def _comprobar_cambios_conocidos(datos_api):
    """
    Verifica si las traducciones que ya tenemos en TRADUCCION_FENOTIPOS_LOCAL
    siguen coincidiendo con la base de datos oficial de CPIC.
    """
    cambios = []

    # Recorremos nuestro diccionario local de referencia
    for genotipo_local, fenotipo_local in TRADUCCION_FENOTIPOS_LOCAL.items():
        # Separamos los alelos para comprobar también la combinación inversa (ej: *2/*17 y *17/*2)
        alelos = genotipo_local.split("/")
        inverso = f"{alelos[1]}/{alelos[0]}" if len(alelos) == 2 else genotipo_local
        
        # Buscamos en los datos de la API si existe este diplotipo o su versión inversa
        match_api = next((item for item in datos_api if item["diplotype"] in [genotipo_local, inverso]), None)
        
        if match_api:
            fenotipo_oficial = match_api.get("generesult", "")

            # Filtro de Seguridad: Ignoramos fenotipos "Likely" (probables) por falta de evidencia sólida
            if "Likely" in fenotipo_oficial:
                continue

            # Si el fenotipo oficial ha cambiado respecto a nuestra base local, lo registramos
            if fenotipo_oficial != fenotipo_local:
                cambios.append(f"  - MODIFICADO: {genotipo_local} pasó de '{fenotipo_local}' a '{fenotipo_oficial}'")
    return cambios



# duncion principal auditoria 
def auditar_conocimiento_con_cpic():
    """
    Punto de entrada principal para la sincronización científica con CPIC.
    Realiza la conexión con la API y coordina las tareas de auditoría.
    """
    # URL oficial de CPIC para el gen CYP2C19
    # Si se introdujese otro gen habria que modificar la api
    api_url = "https://api.cpicpgx.org/v1/diplotype?genesymbol=eq.CYP2C19"
    alelos_rastreados = ["*2", "*3", "*4", "*17", "*38"]
    
    try:
        #Petición a la API con timeout de 5 segundos para no bloquear el inicio de la App
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 200:
            datos_api = response.json()
            
            # Ejecutamos las dos tareas de análisis
            cambios_detectados = _comprobar_cambios_conocidos(datos_api)

            # Si hay cambios o nuevos descubrimientos conflictivos, lanzamos la alerta
            if cambios_detectados :
                imprimir_alerta_mantenimiento(cambios_detectados)
            else:
                print("✅ [Auditoría Clínica]: Conocimiento sincronizado. Los alelos no rastreados se comportan según lo esperado.")
        else:
            print(f"⚠️ [Auditoría Clínica]: Error de API - Código {response.status_code}")        
    except requests.exceptions.RequestException:
        print("⚠️ [Auditoría Clínica]: Sin conexión a internet. Usando base de conocimiento local.")
        
def imprimir_alerta_mantenimiento(cambios):
    print("\n" + "="*80)
    print(" 🚨 ATENCIÓN - NOVEDADES EN LAS GUÍAS CLÍNICAS (CPIC) DETECTADAS 🚨")
    print("="*80)
    
    
    print("\n🔄 CAMBIOS EN COMBINACIONES QUE YA CONOCEMOS:")
    for c in cambios:
        print(c)
            
    print("\nTRABAJO REQUERIDO:")
    print("Por favor, revisa el diccionario 'TRADUCCION_FENOTIPOS_LOCAL' para incluir las")
    print("novedades que consideres relevantes para el panel de tu hospital.")
    print("="*80 + "\n")

if __name__ == "__main__":
    auditar_conocimiento_con_cpic()