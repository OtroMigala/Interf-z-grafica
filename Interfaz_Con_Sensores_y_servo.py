import tkinter as tk
from tkintermapview import TkinterMapView
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial
import threading
import time
import math
from datetime import datetime, timedelta
import os 
import shutil
from PIL import ImageGrab
from PIL import Image, ImageTk
import csv
# Constantes para el cálculo de altitud
PRESSURE_SEA_LEVEL = 101325  # Presión al nivel del mar en Pa
TEMPERATURE_LAPSE_RATE = 0.0065  # K/m
GAS_CONSTANT = 287.05  # J/(kg*K)
GRAVITY = 9.80665  # m/s^2

# Coordenadas y altitud de Popayán
POPAYAN_LAT = 2.441111
POPAYAN_LON = -76.618056
POPAYAN_ALTITUDE = 1720  # metros

class SensorDataApp:
    
    def __init__(self, root):
        self.root = root
        root.configure(bg='#8e8dab')
        root.geometry("1200x800")  # Ajusta el tamaño según tus preferencias
        
        self.root.title("INTERFAZ TULCAN-SAT")
        
        if os.path.exists('capturas'):
            shutil.rmtree('capturas')
        os.makedirs('capturas')

        # Frame principal
        main_frame = tk.Frame(self.root, bg='#8e8dab')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        #Titulo
        title_frame = tk.Frame(main_frame, bg='#8e8dab')
        title_frame.pack(side=tk.TOP, fill=tk.X, pady=10)
        title_label = tk.Label(title_frame, text="TULCAN-SAT", font=("Arial", 24, "bold"), fg='yellow', bg='#8e8dab')
        title_label.pack(side=tk.LEFT, padx=20)
        
        # Logo
        logo_path = r"C:\Users\juan_\Downloads\Logo TUL-CAN SAT (1).png"
        if os.path.exists(logo_path):
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((100, 100))  # Ajusta el tamaño según necesites
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(title_frame, image=logo_photo, bg='#8e8dab')
            logo_label.image = logo_photo
            logo_label.pack(side=tk.RIGHT, padx=20)
        
        # Frame izquierdo para el mapa y valores en tiempo real
        left_frame = tk.Frame(main_frame, bg='#8e8dab')
        left_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Configuración del mapa
        self.map_widget = TkinterMapView(left_frame, width=600, height=400, corner_radius=0)
        self.map_widget.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.map_widget.set_position(POPAYAN_LAT, POPAYAN_LON)
        self.map_widget.set_zoom(15)
        self.marker = None

        # Frame para valores en tiempo real
        self.real_time_frame = tk.Frame(left_frame, bg='#8e8dab', width=600, height=400)
        self.real_time_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.real_time_frame.pack_propagate(False)  # Esto evita que el frame se encoja

        # Inicializar self.labels
        self.labels = {}

        # Etiquetas para valores en tiempo real
        variables = ['Latitud', 'Longitud', 'Presión', 'Temperatura', 'Humedad', 'Altitud BMP280', 'Altitud Relativa', 'Altitud GPS', 
                    'Aceleración X', 'Aceleración Y', 'Aceleración Z',
                    'Giroscopio X', 'Giroscopio Y', 'Giroscopio Z', 
                    'Magnetómetro X', 'Magnetómetro Y', 'Magnetómetro Z']

        for i, variable in enumerate(variables):
            col = i % 2
            row = i // 2
            label = tk.Label(self.real_time_frame, text=f"{variable}: --", font=("Arial", 12), bg='#8e8dab', fg='white', anchor='w')
            label.grid(row=row, column=col, sticky='ew', padx=10, pady=5)
            self.real_time_frame.grid_columnconfigure(col, weight=1)
            self.labels[variable] = label
            
        # Configurar el grid para que se expanda
        for i in range(9):  # Aumentado para acomodar más variables
            self.real_time_frame.grid_rowconfigure(i, weight=1)

        # Configuración de los gráficos
        self.fig, self.axs = plt.subplots(3, 2, figsize=(12, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Inicialización de datos
        self.start_time = None
        self.times = []
        self.acc_data = {'x': [], 'y': [], 'z': []}
        self.gyro_data = {'x': [], 'y': [], 'z': []}
        self.mag_data = {'x': [], 'y': [], 'z': []}
        self.temp_data = []
        self.press_data = []
        self.hum_data = []
        self.altitude_data = []
        self.rel_altitude_data = []
        self.gps_altitude_data = []
        self.lat_data = []
        self.lon_data = []

        # Iniciar la lectura del puerto serial
        self.serial_thread = threading.Thread(target=self.read_serial_data)
        self.serial_thread.daemon = True
        self.serial_thread.start()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.last_map_update = 0
        self.map_update_interval = 2
        
    def on_closing(self):
        # Guardar captura de pantalla de la interfaz completa
        self.save_screenshot()
        
        # Guardar gráficas individuales
        self.save_individual_plots()
        
        # Guardar datos en un archivo de texto
        self.save_data_to_file()
        
        # Cerrar la aplicación
        self.root.destroy()

    def save_screenshot(self):
        if not os.path.exists('capturas'):
            os.makedirs('capturas')
        
        x = self.root.winfo_rootx()
        y = self.root.winfo_rooty()
        x1 = x + self.root.winfo_width()
        y1 = y + self.root.winfo_height()
        ImageGrab.grab().crop((x, y, x1, y1)).save("capturas/captura_interfaz.png")

    def save_individual_plots(self):
        if not os.path.exists('capturas'):
            os.makedirs('capturas')
        
        plot_names = ['Aceleracion', 'Giroscopio', 'Magnetometro', 'Temperatura', 'Presion', 'Altitud']
        for i, ax in enumerate(self.axs.flat):
            fig = plt.figure(figsize=(10, 6))
            new_ax = fig.add_subplot(111)
            new_ax.plot(*ax.lines[0].get_data())
            if len(ax.lines) > 1:
                new_ax.plot(*ax.lines[1].get_data())
                if len(ax.lines) > 2:
                    new_ax.plot(*ax.lines[2].get_data())
            new_ax.set_title(ax.get_title())
            new_ax.set_xlabel('Tiempo (s)')
            new_ax.legend(ax.get_legend_handles_labels()[1])
            plt.tight_layout()
            plt.savefig(f"capturas/{plot_names[i]}.png", dpi=300)
            plt.close(fig)

    def save_data_to_file(self):
        if not os.path.exists('capturas'):
            os.makedirs('capturas')
    
        with open('capturas/datos_sensor.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Tiempo(s)", "Latitud", "Longitud", "Presión(Pa)", "Temperatura(°C)", "Humedad(%)",
                             "Altitud_BMP280(m)", "Altitud_Relativa(m)", "Altitud_GPS(m)",
                             "AccX(g)", "AccY(g)", "AccZ(g)", "GyroX(°/s)", "GyroY(°/s)", "GyroZ(°/s)",
                             "MagX(μT)", "MagY(μT)", "MagZ(μT)"])
            for i in range(len(self.times)):
                writer.writerow([
                    f"{self.times[i]:.2f}", f"{self.lat_data[i]:.6f}", f"{self.lon_data[i]:.6f}",
                    f"{self.press_data[i]:.2f}", f"{self.temp_data[i]:.2f}", f"{self.hum_data[i]:.2f}",
                    f"{self.altitude_data[i]:.2f}", f"{self.rel_altitude_data[i]:.2f}", f"{self.gps_altitude_data[i]:.2f}",
                    f"{self.acc_data['x'][i]:.2f}", f"{self.acc_data['y'][i]:.2f}", f"{self.acc_data['z'][i]:.2f}",
                    f"{self.gyro_data['x'][i]:.2f}", f"{self.gyro_data['y'][i]:.2f}", f"{self.gyro_data['z'][i]:.2f}",
                    f"{self.mag_data['x'][i]:.2f}", f"{self.mag_data['y'][i]:.2f}", f"{self.mag_data['z'][i]:.2f}"
                ])

    def read_serial_data(self):
        ser = serial.Serial('COM3', 115200)  # revisarq que el  de que el puerto COM sea el correcto
        while True:
            try:
                line = ser.readline().decode('utf-8').strip()
                if line.startswith('+RCV='):
                    data = line.split(',')
                    time_str = data[2].split('=')[1]
                    lat = float(data[3].split('=')[1])
                    lon = float(data[4].split('=')[1])
                    temp = float(data[5].split('=')[1].replace('C', ''))
                    press = float(data[6].split('=')[1].replace('Pa', ''))
                    hum = float(data[7].split('=')[1].replace('%', ''))
                    bmp280_alt = float(data[8].split('=')[1].replace('m', ''))
                    rel_alt = float(data[9].split('=')[1].replace('m', ''))
                    gps_alt = float(data[10].split('=')[1].replace('m', ''))
                    acc_x = float(data[11].split('=')[1])
                    acc_y = float(data[12].split('=')[1])
                    acc_z = float(data[13].split('=')[1])
                    gyro_x = float(data[14].split('=')[1])
                    gyro_y = float(data[15].split('=')[1])
                    gyro_z = float(data[16].split('=')[1])
                    mag_x = float(data[17].split('=')[1])
                    mag_y = float(data[18].split('=')[1])
                    mag_z = float(data[19].split('=')[1])
                    
                    if lat != 0 and lon != 0:
                        self.root.after(0, self.update_map, lat, lon)
                
                    self.update_data(time_str, lat, lon, temp, press, hum, bmp280_alt, rel_alt, gps_alt,
                                    acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z)
            except Exception as e:
                print(f"Error reading serial data: {e}")
                print(f"Problematic line: {line}")
            
    def update_data(self, time_str, lat, lon, temp, press, hum, bmp280_alt, rel_alt, gps_alt,
                    acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z):
        if self.start_time is None:
            self.start_time = time.time()
        
        elapsed_time = time.time() - self.start_time
        
        self.times.append(elapsed_time)
        self.lat_data.append(lat)
        self.lon_data.append(lon)
        self.acc_data['x'].append(acc_x)
        self.acc_data['y'].append(acc_y)
        self.acc_data['z'].append(acc_z)
        self.gyro_data['x'].append(gyro_x)
        self.gyro_data['y'].append(gyro_y)
        self.gyro_data['z'].append(gyro_z)
        self.mag_data['x'].append(mag_x)
        self.mag_data['y'].append(mag_y)
        self.mag_data['z'].append(mag_z)
        self.temp_data.append(temp)
        self.press_data.append(press)
        self.hum_data.append(hum)
        self.altitude_data.append(bmp280_alt)
        self.rel_altitude_data.append(rel_alt)
        self.gps_altitude_data.append(gps_alt)

        current_time = time.time()
        if lat != 0 and lon != 0 and current_time - self.last_map_update > self.map_update_interval:
            self.root.after(0, self.update_map, lat, lon)
            self.last_map_update = current_time
            
        self.root.after(0, self.update_plots)
        self.root.after(0, self.update_real_time_values, lat, lon, press, temp, hum, bmp280_alt, rel_alt, gps_alt,
                    acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z)  
         
    def update_map(self, lat, lon):
        if self.marker:
            self.marker.delete()
        self.marker = self.map_widget.set_marker(lat, lon)
            
    def update_plots(self):
        for ax in self.axs.flat:
            ax.clear()
        
        self.axs[0, 0].plot(self.times, self.acc_data['x'], label='X')
        self.axs[0, 0].plot(self.times, self.acc_data['y'], label='Y')
        self.axs[0, 0].plot(self.times, self.acc_data['z'], label='Z')
        self.axs[0, 0].set_title('Aceleración')
        self.axs[0, 0].legend()

        self.axs[0, 1].plot(self.times, self.gyro_data['x'], label='X')
        self.axs[0, 1].plot(self.times, self.gyro_data['y'], label='Y')
        self.axs[0, 1].plot(self.times, self.gyro_data['z'], label='Z')
        self.axs[0, 1].set_title('Giroscopio')
        self.axs[0, 1].legend()

        self.axs[1, 0].plot(self.times, self.mag_data['x'], label='X')
        self.axs[1, 0].plot(self.times, self.mag_data['y'], label='Y')
        self.axs[1, 0].plot(self.times, self.mag_data['z'], label='Z')
        self.axs[1, 0].set_title('Magnetómetro')
        self.axs[1, 0].legend()

        self.axs[1, 1].plot(self.times, self.temp_data)
        self.axs[1, 1].set_title('Temperatura')

        self.axs[2, 0].plot(self.times, self.press_data)
        self.axs[2, 0].set_title('Presión')

        self.axs[2, 1].plot(self.times, self.altitude_data, label='BMP280')
        self.axs[2, 1].plot(self.times, self.rel_altitude_data, label='Relativa')
        self.axs[2, 1].plot(self.times, self.gps_altitude_data, label='GPS')
        self.axs[2, 1].set_title('Altitud')
        self.axs[2, 1].legend()

        for ax in self.axs.flat:
            ax.set_xlabel('Tiempo (s)')
            ax.set_facecolor('#a9a8c3')    
        
        self.fig.patch.set_facecolor('#8e8dab')    
        self.fig.tight_layout()
        self.canvas.draw()

    def update_real_time_values(self, lat, lon, press, temp, hum, bmp280_alt, rel_alt, gps_alt, 
                                acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, 
                                mag_x, mag_y, mag_z):
        self.labels['Latitud'].config(text=f"Latitud: {lat:.6f}")
        self.labels['Longitud'].config(text=f"Longitud: {lon:.6f}")
        self.labels['Presión'].config(text=f"Presión: {press:.2f} Pa")
        self.labels['Temperatura'].config(text=f"Temperatura: {temp:.2f} °C")
        self.labels['Humedad'].config(text=f"Humedad: {hum:.2f} %")
        self.labels['Altitud BMP280'].config(text=f"Altitud BMP280: {bmp280_alt:.2f} m")
        self.labels['Altitud Relativa'].config(text=f"Altitud Rel: {rel_alt:.2f} m")
        self.labels['Altitud GPS'].config(text=f"Altitud GPS: {gps_alt:.2f} m")
        self.labels['Aceleración X'].config(text=f"Aceleración X: {acc_x:.2f} g")
        self.labels['Aceleración Y'].config(text=f"Aceleración Y: {acc_y:.2f} g")
        self.labels['Aceleración Z'].config(text=f"Aceleración Z: {acc_z:.2f} g")
        self.labels['Giroscopio X'].config(text=f"Giroscopio X: {gyro_x:.2f} °/s")
        self.labels['Giroscopio Y'].config(text=f"Giroscopio Y: {gyro_y:.2f} °/s")
        self.labels['Giroscopio Z'].config(text=f"Giroscopio Z: {gyro_z:.2f} °/s")
        self.labels['Magnetómetro X'].config(text=f"Magnetómetro X: {mag_x:.2f} μT")
        self.labels['Magnetómetro Y'].config(text=f"Magnetómetro Y: {mag_y:.2f} μT")
        self.labels['Magnetómetro Z'].config(text=f"Magnetómetro Z: {mag_z:.2f} μT")
if __name__ == "__main__":
    root = tk.Tk()
    app = SensorDataApp(root)
    root.mainloop()
    root = tk.Tk()
    app = SensorDataApp(root)
    root.mainloop()