# DAF (Detección Automática de Fenotipos) -automatizacion-farmacogenomica

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat&logo=python&logoColor=white)
![Windows](https://img.shields.io/badge/OS-Windows-blue?style=flat&logo=windows&logoColor=white)
![HealthTech](https://img.shields.io/badge/HealthTech-CDSS-10b981?style=flat&logo=health&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-f59e0b?style=flat)

Sistema de automatización de respuesta farmacogenómica desarrollado para la **Fundación Pública Galega de Medicina Xenómica (FPGMX)**. 

DAF procesa, analiza y automatiza la detección de fenotipos basándose en los datos de secuenciación de los pacientes para el fármaco Clopidogrel y a mayores devuelve las recomendaciones clínicas asociadas, integrando motores de reglas lógicas complejas en una aplicación de escritorio de un solo clic.

---

##  Nota sobre Privacidad de Datos (HealthTech Compliance)
**Todos los datos y archivos de muestra incluidos en este repositorio han sido generados artificialmente para fines de demostración.** Ningún archivo contiene Información de Salud Protegida (PHI), ni datos reales de pacientes de la FPGMX.

---
## Aviso Legal (Medical Disclaimer)
DAF es una **herramienta de apoyo a la decisión clínica** (Clinical Decision Support System - CDSS). Los resultados y recomendaciones generados por este software no sustituyen en ningún caso el juicio, diagnóstico o tratamiento de un profesional médico cualificado. El uso de esta herramienta está destinado exclusivamente a profesionales de la salud e investigadores.

---

##  Características Principales y UX/UI

Este proyecto fue diseñado priorizando la experiencia del personal médico y la optimización de recursos hospitalarios:

* **Análisis en Lote:** Carga simultánea de archivos `.split.tab` para procesar múltiples pacientes.
* **Motor de Reglas en C++:** Implementación de `durable_rules` para la inferencia de fenotipos, pre-compilado en el entorno de despliegue.
* **Integración con API Abierta:** Conexión con el repositorio **ClinPGx** para el cruce de datos farmacogenómicos.
* **Despliegue Nativo Inteligente:** El instalador (`.bat`) esquiva conflictos con servicios en la nube (como OneDrive) instalando la aplicación directamente en `%LocalAppData%\DAF_APP`. Además, genera accesos directos dinámicos en el escritorio usando PowerShell.
* **Inicio Silencioso:** La ejecución del entorno pre-empaquetado se realiza mediante un script oculto (`Lanzador.vbs`) para evitar consolas molestas de cara al usuario.
* **Filtros Clínicos Visuales:** Herramientas de UI como **"Ocultar Sanos"** para mostrar exclusivamente a los pacientes que no sean "Normal Metabolizers", agilizando la toma de decisiones médicas.

---

##  Arquitectura Modular (Para Desarrolladores)

El sistema se divide en módulos independientes para garantizar la escalabilidad:

* `data_processor_v1_1.py`: Extrae y limpia los datos en bruto (`.tab`), filtrando únicamente los genes y rsIDs relevantes para el análisis clínico.
* `genetics_engine_v1_0.py`: Motor de inferencia basado en C++ (`durable_rules`) que detecta combinaciones alélicas (*2, *3, *4, *17) y emite diagnósticos.
* `main_gui_v1_3.py`: Interfaz gráfica construida con `CustomTkinter` que orquesta los hilos de procesamiento (Threading) para no congelar la pantalla.
* `mantenimiento_API_v1_0.py`: Script de auditoría clínica que conecta con la API oficial del CPIC para sincronizar las guías médicas.

---

## Protocolo de Mantenimiento y Auditoría

Tratándose de software clínico, el sistema requiere validaciones periódicas para asegurar su precisión médica:

1. **Auditoría Trimestral:** Es obligatorio ejecutar el módulo `mantenimiento_API.py` al menos una vez cada 3 meses para asegurar que el sistema se mantiene actualizado. Este script contrastará el diccionario de reglas local con las guías oficiales actualizadas.
2. **Control de Nomenclatura:** Debido a las fuertes dependencias arquitectónicas, si se realiza algún cambio en el nombre de un archivo principal (ej. actualizar la versión del `main_gui`), este debe actualizarse manualmente en los demás scripts que lo invocan, como el `Lanzador.vbs`.

---
### Requisitos del Sistema
* Sistema Operativo: Windows 10 / Windows 11 (Debido a la automatización nativa de PowerShell y VBScript).

* Permisos: No requiere permisos de Administrador (se instala en %LocalAppData%).

---

##  Instalación (Para Usuarios Finales)

1. Ve a la sección de **[Releases](../../releases)**.
2. Descarga la **Versión 1.0**.
3. Descomprime y ejecuta el Instalador_DAF.bat. 
4. Inicia DAF desde el acceso directo de tu escritorio. *(Nota: La primera vez que se ejecuta la aplicación puede tardar varios segundos en responder puesto que está desempaquetando el entorno, creando carpetas e inicializando variables. No lo inicie varias veces consecutivas).*

---
## Guía Rápida de Uso
Inicia la aplicación desde el acceso directo del escritorio.

En el panel izquierdo, haz clic en "Subir archivos (.tab)" y selecciona uno o varios pacientes.

Visualiza los resultados. Puedes usar el botón "Ocultar Sanos" (⚠️) para filtrar inmediatamente a los pacientes que presenten alteraciones metabólicas y requieran revisión de su pauta de Clopidogrel.

---

## 👤 Autores del proyecto
* **Pablo Rey Mariño** *  💼 LinkedIn: 'https://www.linkedin.com/in/pablo-rey-mariño/'
*  **Iria  Varela Palmas** 
*  **Luis Pérez Jiménez** 💼 LinkedIn:'https://www.linkedin.com/in/luis-pj-524135268/'
* 🏢 Proyecto desarrollado para la Fundación Pública Galega de Medicina Xenómica.
