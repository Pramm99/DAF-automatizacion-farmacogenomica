import pandas as pd
import json
import os
import logging  

# CONFIGURACIÓN DE LOGS
logging.basicConfig(
    filename='error_carga_datos.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Saca la ruta exacta y completa de la carpeta donde está guardado este script
DIRECTORIO_BASE = os.path.dirname(os.path.abspath(__file__))

# Ahora construimos las rutas pegando la ruta base con el nombre de tu carpeta
input_dir = os.path.join(DIRECTORIO_BASE, "splits_CYP2C19_CYP2D6") 
clean_dir = os.path.join(DIRECTORIO_BASE, "clean_tab")
clean_json = os.path.join(DIRECTORIO_BASE, "clean_json")

os.makedirs(clean_dir, exist_ok=True)
os.makedirs(clean_json, exist_ok=True)


# configuraciones por medicamento
RSIDS_CLOPIDOGREL = ["rs12248560", "rs28399504", "rs12769205", "rs58973490", "rs4986893", "rs4244285", "rs3758581"]
#RSIDS_OTRO_MEDICAMENTO = ["rsXXXXXXX", ...]
 
cols_to_keep = ["Gene.RefSeq", "Start","avsnp157", "Alt", "Zygosity"]
#"avsnp157" -> columna del rsID

def clean_single_data(ruta_original, nombre_archivo, medicamento):
    """Procesamiento individual seguro (Modo Bajo Demanda)"""
    try:
        df = pd.read_csv(ruta_original, sep="\t")

        if medicamento == "Clopidogrel":
            df_filtered = df[(df["Gene.RefSeq"] == "CYP2C19") & (df["avsnp157"].isin(RSIDS_CLOPIDOGREL))]
        
        df_clean = df_filtered[cols_to_keep]

        json_path = os.path.join(clean_json, nombre_archivo.replace(".tab", ".json"))
        df_clean.to_json(json_path, orient="records", indent=4)
        return json_path
    except Exception as e:
        logging.error(f"Error procesando archivo individual {nombre_archivo}: {str(e)}")
        return None


if __name__ == "__main__":
    """Procesamiento masivo de una carpeta entera (Modo Batch)"""
    
    for filename in os.listdir(input_dir):
        if filename.endswith(".tab"):
            try:
                # cargar arhivo (separación de tabulador)
                df = pd.read_csv(os.path.join(input_dir, filename), sep="\t")

                # filtrar por gen CYP2C19
                df_filtered = df[(df["Gene.RefSeq"] == "CYP2C19") & (df["avsnp157"].isin(["rs12248560", "rs28399504", "rs12769205", "rs58973490",
                                                                                          "rs4986893", "rs4244285", "rs3758581"]))]

                # Selección de columnas
                df_clean = df_filtered[cols_to_keep]

                # guardamos el .tab limpio
                clean_path = os.path.join(clean_dir, filename)
                df_clean.to_csv(clean_path, sep="\t", index=False)

                # guardamos json
                json_path = os.path.join(clean_json, filename.replace(".tab", ".json"))
                df_clean.to_json(json_path, orient="records", indent=4)
                
            except Exception as e:
                # Si un archivo falla, guarda el error y pasa al siguiente sin detener el script
                logging.error(f"Error procesando {filename} en modo batch: {str(e)}")
                print(f"Error en {filename}. Revisa proceso.log para más detalles.")




