Claro, aquí tienes una versión mejorada del README.md con estilos que se verán bien en GitHub:
markdownCopy# 🛰️ SensorDataApp - TULCAN-SAT

<p align="center">
  <img src="Logo TUL-CAN SAT (1).png" alt="TULCAN-SAT Logo" width="200"/>
</p>

<p align="center">
  <em>Una aplicación de visualización de datos en tiempo real para el proyecto TULCAN-SAT</em>
</p>

<p align="center">
  <a href="#características">Características</a> •
  <a href="#requisitos">Requisitos</a> •
  <a href="#instalación">Instalación</a> •
  <a href="#uso">Uso</a> •
  <a href="#estructura-del-proyecto">Estructura</a> •
  <a href="#personalización">Personalización</a> •
  <a href="#contribución">Contribución</a> •
  <a href="#licencia">Licencia</a>
</p>

---

## 🌟 Características

- 🗺️ **Visualización de mapa en tiempo real** con la ubicación actual del dispositivo
- 📊 **Gráficos en tiempo real** para:
  - Aceleración (X, Y, Z)
  - Giroscopio (X, Y, Z)
  - Magnetómetro (X, Y, Z)
  - Temperatura
  - Presión
  - Altitud (BMP280, Relativa, GPS)
- 🔢 **Visualización de valores en tiempo real** para todos los sensores
- 📸 **Captura de pantalla automática** de la interfaz al cerrar la aplicación
- 🖼️ **Guardado de gráficos individuales** como imágenes
- 📁 **Exportación de datos** a un archivo CSV

## 🛠️ Requisitos

- Python 3.x
- Bibliotecas:
  - tkinter
  - tkintermapview
  - matplotlib
  - serial
  - PIL (Pillow)
  - csv

## 📥 Instalación

1. Clona este repositorio:
git clone https://github.com/tu-usuario/SensorDataApp.git
Copy2. Navega al directorio del proyecto:
cd SensorDataApp
Copy3. Instala las dependencias necesarias:
pip install tkintermapview matplotlib pyserial Pillow
Copy
## 🚀 Uso

1. Conecta tu dispositivo TULCAN-SAT al puerto COM3 (o modifica el código para usar el puerto correcto).
2. Ejecuta el script:
python sensor_data_app.py
Copy3. La aplicación se iniciará y comenzará a recopilar y mostrar datos en tiempo real.
4. Al cerrar la aplicación, se guardarán automáticamente:
- Una captura de pantalla de la interfaz completa
- Imágenes individuales de cada gráfico
- Un archivo CSV con todos los datos recopilados

## 📂 Estructura del Proyecto
SensorDataApp/
│
├── sensor_data_app.py     # Script principal
├── Logo TUL-CAN SAT (1).png  # Logo de TULCAN-SAT
│
└── capturas/              # Directorio para capturas y datos
├── captura_interfaz.png
├── Aceleracion.png
├── Giroscopio.png
├── ...
└── datos_sensor.csv
Copy
## ⚙️ Personalización

- Modifica las constantes al inicio del script para ajustar los cálculos de altitud.
- Ajusta la frecuencia de actualización del mapa cambiando `self.map_update_interval`.
- Personaliza los colores de la interfaz modificando los valores de `bg` en los widgets.

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor, abre un issue para discutir cambios mayores antes de hacer un pull request.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - vea el archivo [LICENSE](LICENSE) para más detalles.

---

<p align="center">
  Desarrollado con ❤️ por el equipo TULCAN-SAT
</p>
