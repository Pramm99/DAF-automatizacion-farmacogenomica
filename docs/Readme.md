1. Hay que realizar un mantenimiento cada 3 meses y por protocolo recomendamos añadir una entrada al inicio del historial de mantenimiento para mantener control de la última vez que se revisó, y si se realizaron modificaciones o no.

2. Si se realizan cambios en el main\_gui y se actualiza el nombre hay que actualizarlo también en el Lanzador.vbs.

3. Guía de uso :



* Al iniciar la aplicación tienes varios elementos que seleccionar en la barra lateral izquierda. 



* Para cargar un paciente hay que seleccionar subir archivos (se encuentra debajo de Carga de Datos), ahí toca seleccionar el/los archivo/s de datos .split.tab con los datos genómicos de los pacientes.



* Automáticamente va a inferir el genotipo detectado y su recomendación clínica apropiada, además de una bandera con el estado del metabolizador.



* En "Gen a analizar" y "Medicamento" son elementos que aun no están disponibles pero en un futuro permitirán analizar otros medicamentos.



* En "Acciones Visuales" puedes marcar el elemento "Ocultar Sanos" para hacer que no se muestren en pantalla los pacientes con un estado de "Normal Metabolizer". Una vez presionado, el elemento se convierte en "Mostrar Todos", pulsarlo provoca que vuelvan aparecer en pantalla todos los pacientes analizados. También puedes marcar "Limpiar Pantalla" que elimina los resultados inferidos previamente.



4. Recomendaciones de uso:



* Puesto que cada paciente analizado queda guardado en memoria RAM, la carga de un gran número de pacientes puede ralentizar el uso de la aplicacion. Por esto mismo recomendamos no cargar más de 50 pacientes a la vez.



5. Avisos:



* La primera vez que se ejecuta la aplicación puede tardar varios segundos en responder puesto que está creando carpetas e inicializando variables, entonces se recomienda no iniciarlo varias veces a la vez para evitar errores.











