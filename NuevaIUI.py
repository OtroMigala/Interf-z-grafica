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

class SensorDataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sensor Data Visualization")
        self.root.geometry("1200x800")

        # Configurar el mapa
        self.map_widget = TkinterMapView(self.root, width=400, height=300, corner_radius=0)
        self.map_widget.pack(side=tk.LEFT, padx=10, pady=10)
        self.map_widget.set_position(2.441111, -76.618056)  # Coordenadas de Popayán
        self.map_widget.set_zoom(12)

        # Configurar las gráficas
        self.fig, self.axs = plt.subplots(3, 2, figsize=(8, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, padx=10, pady=10)

        # Inicializar datos
        self.times = []
        self.acc_data = {'x': [], 'y': [], 'z': []}
        self.gyro_data = {'x': [], 'y': [], 'z': []}
        self.mag_data = {'x': [], 'y': [], 'z': []}
        self.temp_data = []
        self.press_data = []
        self.alt_data = []

        # Iniciar la lectura del puerto serial
        self.serial_thread = threading.Thread(target=self.read_serial_data)
        self.serial_thread.daemon = True
        self.serial_thread.start()

    def read_serial_data(self):
        ser = serial.Serial('COM3', 115200)
        buffer = ""
        while True:
            try:
                line = ser.readline().decode('utf-8').strip()
                if line.startswith('+RCV='):
                    buffer = line
                elif buffer.startswith('+RCV=') and line[0].isdigit():
                    buffer += line
                    data = buffer.split(',')
                    if len(data) >= 20:
                        time_str = data[2].split('=')[1]
                        lat = float(data[3].split('=')[1])
                        lon = float(data[4].split('=')[1])
                        temp = float(data[5].split('=')[1].replace('C', ''))
                        press = float(data[6].split('=')[1].replace('Pa', ''))
                        rel_alt = float(data[7].split('=')[1].replace('m', ''))
                        acc_x = float(data[8].split('=')[1])
                        acc_y = float(data[9].split('=')[1])
                        acc_z = float(data[10].split('=')[1])
                        gyro_x = float(data[11].split('=')[1])
                        gyro_y = float(data[12].split('=')[1])
                        gyro_z = float(data[13].split('=')[1])
                        mag_x = float(data[14].split('=')[1])
                        mag_y = float(data[15].split('=')[1])
                        mag_z = float(data[16].split('=')[1])

                        self.update_data(time_str, lat, lon, temp, press, rel_alt, 
                                         acc_x, acc_y, acc_z, 
                                         gyro_x, gyro_y, gyro_z, 
                                         mag_x, mag_y, mag_z)
                    buffer = ""
            except Exception as e:
                print(f"Error reading serial data: {e}")
            time.sleep(0.1)

    def update_data(self, time_str, lat, lon, temp, press, rel_alt, 
                    acc_x, acc_y, acc_z, 
                    gyro_x, gyro_y, gyro_z, 
                    mag_x, mag_y, mag_z):
        # Convertir time_str a segundos desde el inicio
        time_obj = datetime.strptime(time_str, "%H:%M:%S.%f")
        if not self.times:
            self.start_time = time_obj
        seconds = (time_obj - self.start_time).total_seconds()

        self.times.append(seconds)
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
        self.alt_data.append(rel_alt)

        self.root.after(0, self.update_plots)
        self.root.after(0, self.update_map, lat, lon)

    def update_plots(self):
        for ax in self.axs.flat:
            ax.clear()

        self.axs[0, 0].plot(self.times, self.acc_data['x'], label='X')
        self.axs[0, 0].plot(self.times, self.acc_data['y'], label='Y')
        self.axs[0, 0].plot(self.times, self.acc_data['z'], label='Z')
        self.axs[0, 0].set_title('Acceleration')
        self.axs[0, 0].legend()

        self.axs[0, 1].plot(self.times, self.gyro_data['x'], label='X')
        self.axs[0, 1].plot(self.times, self.gyro_data['y'], label='Y')
        self.axs[0, 1].plot(self.times, self.gyro_data['z'], label='Z')
        self.axs[0, 1].set_title('Gyroscope')
        self.axs[0, 1].legend()

        self.axs[1, 0].plot(self.times, self.mag_data['x'], label='X')
        self.axs[1, 0].plot(self.times, self.mag_data['y'], label='Y')
        self.axs[1, 0].plot(self.times, self.mag_data['z'], label='Z')
        self.axs[1, 0].set_title('Magnetometer')
        self.axs[1, 0].legend()

        self.axs[1, 1].plot(self.times, self.temp_data)
        self.axs[1, 1].set_title('Temperature')

        self.axs[2, 0].plot(self.times, self.press_data)
        self.axs[2, 0].set_title('Pressure')

        self.axs[2, 1].plot(self.times, self.alt_data)
        self.axs[2, 1].set_title('Relative Altitude')

        for ax in self.axs.flat:
            ax.set_xlabel('Time (s)')

        self.fig.tight_layout()
        self.canvas.draw()

    def update_map(self, lat, lon):
        if lat != 0 and lon != 0:
            self.map_widget.set_position(lat, lon)

if __name__ == "__main__":
    root = tk.Tk()
    app = SensorDataApp(root)
    root.mainloop()