import json
import os
from durable.lang import *


diagnosticos_pacientes = {}
memoria_datos_limpios = {} #JSON a salvo del motor C


def registrar_diagnostico(id_paciente, nombre_alelo, nombre_gen, rsids_implicados, datos_limpios_paciente):
    # Si el paciente no existe, creamos su diccionario
    if id_paciente not in diagnosticos_pacientes:
        diagnosticos_pacientes[id_paciente] = {}
        
    # Si es la primera vez que vemos este gen en este paciente creamos su lista
    if nombre_gen not in diagnosticos_pacientes[id_paciente]:
        diagnosticos_pacientes[id_paciente][nombre_gen] = []

    # Extraemos el diccionario del gen directamente de los datos limpios de Python
    # (Ej: {'rs4986893': 'A', 'rs3758581': 'GG', 'total_mutaciones': 2})
    datos_del_gen = datos_limpios_paciente.get(nombre_gen, {})
    
    #  Este bucle funciona como un escudo contra una mutación con homocigosis en un rsid que no queremos
    for rsid, valor in datos_del_gen.items():
        if rsid not in rsids_implicados:
            # Si un rsID ajeno a esta regla ocupa ambos cromosomas, abortamos
            if len(valor) == 2:
                # Opcional: print para depurar
                # print(f"    [Filtro] Se ignora {nombre_alelo} en {id_paciente} por {rsid} homocigoto.")
                return
                

    # Comprobamos si todos los rsIDs implicados en esta regla tienen un valor de longitud 2 en el JSON real.
    es_homocigoto_total = True
    # NOTA CLÍNICA: Si un rsID no está en datos_del_gen, asumimos que el paciente tiene un genotipo de referencia homocigoto
    for rsid in rsids_implicados:
        if rsid in datos_del_gen:
            # CASO A: Hay mutación. Para ser homocigoto, debe tener longitud 2 (ej: 'AA')
            valor_mutacion = datos_del_gen.get(rsid, "")  # .get para evitar errores si no lo encuentra devuelve ""
            if len(valor_mutacion) != 2:
                es_homocigoto_total = False
                break # Si encontramos uno solo que no sea 2, ya no es homocigoto estricto
            # CASO B (Implícito): Si no está en datos_del_gen, no hacemos nada (pasa como True)


    # Control de seguridad para evitar fallo con el numero de disparos de las reglas:

    # ¿Cuántas veces está este diagnóstico ya en la lista del paciente?
    # El count impide que entre el gen concreto veces a mayores que no debería pero no influye en alelos distintos
    conteo_actual = diagnosticos_pacientes[id_paciente][nombre_gen].count(nombre_alelo)
    # ¿Cuántas veces debería haber?
    max_copias = 2 if es_homocigoto_total else 1
    
    # Mientras falten copias, las añadimos.
    # Si el motor dispara la regla 1 sola vez, este bucle dará 2 vueltas para un homocigoto
    # Si el motor se tiene algun fallo y dispara la regla varias veces,el bucle no llenara alelos de mas
    while conteo_actual < max_copias:
        diagnosticos_pacientes[id_paciente][nombre_gen].append(nombre_alelo)
        conteo_actual += 1 # Actualizamos el contador para que el bucle avance


# El ruleset "CYP2C19" comprueba las reglas de combinaciones para el gen CYP2C19
with ruleset('CYP2C19'):
    # Definimos el antecedente de las reglas
    @when_all(
        ((m.CYP2C19.rs12769205 == 'G') | (m.CYP2C19.rs12769205 == 'GG')) &
        ((m.CYP2C19.rs4244285  == 'A') | (m.CYP2C19.rs4244285  == 'AA')) &
        ((m.CYP2C19.rs3758581  == 'G') | (m.CYP2C19.rs3758581  == 'GG')) 
    )
    #Definimos el consecuente de las reglas
    def alelo2(c):             #c es el contexto
        nombres_rsids = ["rs12769205", "rs58973490", "rs4244285", "rs3758581"]

        # Recuperamos el JSON intacto de la memoria global
        datos_intactos = memoria_datos_limpios.get(c.m.id_paciente, {})
        datos_del_gen = datos_intactos.get("CYP2C19", {})

        # Filtro manual para comprobar que tenga o la mutacion deseada o que no esté mutada
        # Extraemos el valor del rs58973490 (si no existe, devuelve None)
        mut_rs58 = datos_del_gen.get("rs58973490", None)

        # Comprobamos si el rsID existe y además si es o no una de las letras permitidas
        if mut_rs58 is not None and mut_rs58 not in ['A', 'AA']:
            # Abortamos la ejecución
            # Con el return, la función muere aquí y no se registra el diagnóstico.
            return

        registrar_diagnostico(
            id_paciente = c.m.id_paciente, 
            nombre_alelo = "*2", 
            nombre_gen = "CYP2C19", 
            rsids_implicados = nombres_rsids, 
            datos_limpios_paciente = datos_intactos
        )


    @when_all(
        ((m.CYP2C19.rs4986893 == 'A') | (m.CYP2C19.rs4986893 == 'AA')) &
        ((m.CYP2C19.rs3758581 == 'G') | (m.CYP2C19.rs3758581 == 'GG')) 
    )
    def alelo3(c):
        nombres_rsids = ["rs4986893", "rs3758581"]

        datos_intactos = memoria_datos_limpios.get(c.m.id_paciente, {})

        registrar_diagnostico(
            id_paciente = c.m.id_paciente, 
            nombre_alelo = "*3", 
            nombre_gen = "CYP2C19", 
            rsids_implicados = nombres_rsids, 
            datos_limpios_paciente = datos_intactos
        )



    @when_all(
        ((m.CYP2C19.rs28399504 == 'G') | (m.CYP2C19.rs28399504 == 'GG')) &
        ((m.CYP2C19.rs3758581  == 'G') | (m.CYP2C19.rs3758581  == 'GG')) 
    )
    def alelo4(c):
        nombres_rsids = ["rs12248560", "rs28399504", "rs3758581"]

        datos_intactos = memoria_datos_limpios.get(c.m.id_paciente, {})
        datos_del_gen = datos_intactos.get("CYP2C19", {})

        mut_rs60 = datos_del_gen.get("rs12248560", None)

        if mut_rs60 is not None and mut_rs60 not in ['T', 'TT']:
            return

        registrar_diagnostico(
            id_paciente = c.m.id_paciente, 
            nombre_alelo = "*4", 
            nombre_gen = "CYP2C19", 
            rsids_implicados = nombres_rsids, 
            datos_limpios_paciente = datos_intactos
        )



    @when_all(
        ((m.CYP2C19.rs12248560 == 'T') | (m.CYP2C19.rs12248560 == 'TT')) &
        ((m.CYP2C19.rs3758581  == 'G') | (m.CYP2C19.rs3758581  == 'GG')) 
    )
    def alelo17(c):
        nombres_rsids = ["rs12248560", "rs3758581"]

        datos_intactos = memoria_datos_limpios.get(c.m.id_paciente, {})

        registrar_diagnostico(
            id_paciente = c.m.id_paciente, 
            nombre_alelo = "*17", 
            nombre_gen = "CYP2C19", 
            rsids_implicados = nombres_rsids, 
            datos_limpios_paciente = datos_intactos
        )


# (Aquí en el futuro podrías añadir otro ruleset para otro gen)
# with ruleset('Otrogen'):....

# Actualizamos el json para que nos quede de una forma más eficiente
def preparar_datos_para_reglas(lista_variantes, id_paciente):
    """"
    Toma una lista plana de diccionarios y la transforma
    en un diccionario anidado optimizado para el motor de
    reglas
    """
    #Le introducimos de id_paciente el nombre del archivo
    paciente_formateado = {"id_paciente": id_paciente}

    #Recorremos cada variante de la lista original una por una
    for variante in lista_variantes:
        gen = variante.get("Gene.RefSeq") # Usamos .get() en vez de ["clave"] para evitar un error en el caso de no existir
        rsid = variante.get("avsnp157")
        alt = variante.get("Alt")
        cigosidad = variante.get("Zygosity")

        if gen and rsid:
            if gen not in paciente_formateado:
                #Si es la primera vez que vemos un gen concreto en el paciente creamos un diccionario vacío para ese gen
                paciente_formateado[gen] = {}

            # Si es homocigoto ('hom'), la mutación está en ambos alelos
            if cigosidad == 'hom':
                valor_alelo = alt * 2 
            # Si es heterocigoto ('het') o cualquier otro caso, la mutación está en un solo alelo
            else:
                valor_alelo = alt

            # Almacenamos la información de la forma que nos interesa
            paciente_formateado[gen][rsid] = valor_alelo  # {"id_paciente": "paciente", "gen1": {"rsID1": "alt", "rsiD2":"altalt", ...}

    return paciente_formateado


def analizar_genoma(paciente_json, nombre_gen):
    """
    Ejecuta el ruleset específico para el gen solicitado
    """
    
    id_pac = paciente_json.get("id_paciente", "Desconocido") # Parametro "Desconocido" en el caso de un error con el nombre, así usará ese valor
    print(f"  -> Iniciando búsqueda ({nombre_gen}) para el paciente: {id_pac}")

    # Bloque de seguridad porque la librería Durable Rules trabaja en memoria con C y puede ser delicado
    try:
        # Le pegamos una mochila temporal al json con sus propios datos
        memoria_datos_limpios[id_pac] = paciente_json
        # Creamos un hecho para que se puedan disparar las reglas del gen concreto
        assert_fact(nombre_gen, paciente_json)

    except Exception as e:
        # assert_fact lanza un error si el paciente ya estaba en la memoria
        if "MessageNotHandledException" in str(type(e)):
            pass
        else:
            # Si es un error real del motor, que grite
            print(f"\n[!!!] ERROR CRÍTICO EN EL MOTOR PARA: {id_pac} [!!!]")
            import traceback
            traceback.print_exc()

    finally:
        # Eliminamos el hecho una vez revisada cada regla
        # Esto ayuda a que la RAM no se sature cuando analicemos muchos elementos
        try:
            retract_fact(nombre_gen, paciente_json)
        except:
            pass
        memoria_datos_limpios.pop(id_pac, None)

def imprimir_informe_laboratorio(diagnosticos):
    """
    Toma el diccionario de diagnósticos y lo imprime por consola 
    en un formato de tabla clínica alineada.
    """
    # Si el diccionario está vacío, avisamos y salimos de la función
    if not diagnosticos:
        print("\n=== RESUMEN FINAL DE DIAGNÓSTICOS ===")
        print("No se encontraron alteraciones en ningún paciente (Todos son *38/*38).")
        return

    # Dibujamos la cabecera de la tabla
    print('\nPacientes con mutaciones detectadas:')
    print("\n" + "="*85)
    print(f"    {'PACIENTE':<45} | {'GEN':<20} | {'GENOTIPO':<15}")
    print("="*85)

    # Recorremos los datos y dibujamos las filas
    for paciente, genes in diagnosticos.items():
        nombre_limpio = paciente.replace('.split', '').strip('.')
        
        for gen, alelos in genes.items():
            # Formateamos el genotipo
            if len(alelos) == 1:
                genotipo = f"{alelos[0]}/*38"
            elif len(alelos) == 2:
                genotipo = f"{alelos[0]}/{alelos[1]}"
            elif len(alelos) > 2:
                # Indecisión heterocigótica o error de lectura
                mezcla = ", ".join(alelos)
                genotipo = f" ANOMALÍA: [{mezcla}]"
            else:
                genotipo =  "*38/*38 (Filtrado seguro)"
                
            # Imprimimos la fila alineada
            print(f"    {nombre_limpio:<45} | {gen:<15} | {genotipo:<15}")
            
    # Cerramos la tabla
    print("="*85 + "\n")

if __name__ == "__main__":

    #Carpeta que tiene los pacientes en formato JSON tras ejecutar data_processor
    carpeta_datos = "splits_CYP2C19_CYP2D6_clean_json"

    print(f"=== SISTEMA DE DIAGNÓSTICO GENÓMICO ===")
    print(f"Buscando pacientes en la carpeta '{carpeta_datos}'...\n")

    if not os.path.exists(carpeta_datos):
        print(f"Error: No se encontró la carpeta '{carpeta_datos}'.")
    else:
        # Lista los archivos del directorio
        archivos_en_carpeta = os.listdir(carpeta_datos)

        # Archivo a archivo, da igual si tiene mayúsculas o minúsculas, coge el nombre sin la extensión
        for nombre_archivo in archivos_en_carpeta:
            if nombre_archivo.lower().endswith('.json'):

                id_del_paciente = os.path.splitext(nombre_archivo)[0]
                ruta_completa = os.path.join(carpeta_datos, nombre_archivo)

                try:
                    # Leemos el archivo
                    with open(ruta_completa, 'r', encoding='utf-8') as archivo:
                        datos_crudos = json.load(archivo)
                    # Formateamos datos                
                    datos_listos = preparar_datos_para_reglas(datos_crudos, id_del_paciente)

                    # Analizamos el genoma
                    # Se puede cambiar "completa" por el nombre de un gen concreto como "CYP2C19" si quieres ejecutar una búsqueda específica
                    analizar_genoma(datos_listos, nombre_gen="CYP2C19")

                except json.JSONDecodeError:
                    print(f"  [Error] El archivo {nombre_archivo} está corrupto.")
                except Exception as e:
                    print(f"  [Error] Ocurrió un problema con {nombre_archivo}: {e}")

        # Resumen Final
        imprimir_informe_laboratorio(diagnosticos_pacientes)