SensorDataApp es una aplicación de interfaz gráfica de usuario (GUI) desarrollada en Python para visualizar y registrar datos de sensores en tiempo real. Está diseñada específicamente para el proyecto TULCAN-SAT, utilizando datos de diversos sensores como GPS, acelerómetro, giroscopio, magnetómetro, barómetro y termómetro.
Características

Visualización de mapa en tiempo real con la ubicación actual del dispositivo
Gráficos en tiempo real para:

Aceleración (X, Y, Z)
Giroscopio (X, Y, Z)
Magnetómetro (X, Y, Z)
Temperatura
Presión
Altitud (BMP280, Relativa, GPS)


Visualización de valores en tiempo real para todos los sensores
Captura de pantalla automática de la interfaz al cerrar la aplicación
Guardado de gráficos individuales como imágenes
Exportación de datos a un archivo CSV

Requisitos

Python 3.x
Bibliotecas:

tkinter
tkintermapview
matplotlib
serial
PIL (Pillow)
csv



Instalación

Clona este repositorio o descarga el archivo Python.
Instala las dependencias necesarias:

Copypip install tkintermapview matplotlib pyserial Pillow
Uso

Conecta tu dispositivo TULCAN-SAT al puerto COM3 (o modifica el código para usar el puerto correcto).
Ejecuta el script:

Copypython sensor_data_app.py

La aplicación se iniciará y comenzará a recopilar y mostrar datos en tiempo real.
Al cerrar la aplicación, se guardarán automáticamente:

Una captura de pantalla de la interfaz completa
Imágenes individuales de cada gráfico
Un archivo CSV con todos los datos recopilados



Estructura del Proyecto

sensor_data_app.py: El script principal que contiene toda la lógica de la aplicación.
capturas/: Directorio donde se guardan las capturas de pantalla y los datos al cerrar la aplicación.
Logo TUL-CAN SAT (1).png: Logo de TULCAN-SAT utilizado en la interfaz (asegúrate de que este archivo esté en la ubicación correcta).

Personalización

Modifica las constantes al inicio del script para ajustar los cálculos de altitud si es necesario.
Ajusta la frecuencia de actualización del mapa cambiando el valor de self.map_update_interval.
Personaliza los colores de la interfaz modificando los valores de bg en los diferentes widgets.

Contribución
Las contribuciones son bienvenidas. Por favor, abre un issue para discutir cambios mayores antes de hacer un pull request.
Licencia
