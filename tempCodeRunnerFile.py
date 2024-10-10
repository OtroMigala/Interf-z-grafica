    def read_serial_data(self):
        ser = serial.Serial('COM3', 115200)  # Asegúrate de que el puerto COM sea el correcto
        print("Conectado al puerto serial COM3")
        buffer = ""
        while True:
            try:
                line = ser.readline().decode('utf-8').strip()
                print(f"Datos recibidos: {line}")  # Imprime cada línea recibida
                
                if line.startswith('+RCV='):
                    buffer = line
                elif buffer.startswith('+RCV=') and not line.startswith('+RCV='):
                    buffer += line
                    parts = buffer.split(',')
                    if len(parts) >= 20:  # Asegúrate de que tenemos todos los datos
                        time_str = parts[2].split('=')[1]
                        lat = float(parts[3].split('=')[1])
                        lon = float(parts[4].split('=')[1])
                        temp = float(parts[5].split('=')[1].replace('C', ''))
                        press = float(parts[6].split('=')[1].replace('Pa', ''))
                        rel_alt = float(parts[7].split('=')[1].replace('m', ''))
                        acc_x = float(parts[8].split('=')[1])
                        acc_y = float(parts[9].split('=')[1])
                        acc_z = float(parts[10].split('=')[1])
                        gyro_x = float(parts[11].split('=')[1])
                        gyro_y = float(parts[12].split('=')[1])
                        gyro_z = float(parts[13].split('=')[1])
                        mag_x = float(parts[14].split('=')[1])
                        mag_y = float(parts[15].split('=')[1])
                        mag_z = float(parts[16].split('=')[1])
                        
                        print(f"Datos procesados: Time={time_str}, Lat={lat}, Lon={lon}, Temp={temp}, Press={press}, RelAlt={rel_alt}")
                        
                        self.update_data(time_str, lat, lon, temp, press, rel_alt, 
                                        acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, 
                                        mag_x, mag_y, mag_z)
                    else:
                        print(f"Formato de datos inesperado: {buffer}")
                    buffer = ""  # Limpiar el buffer después de procesar
            except Exception as e:
                print(f"Error leyendo datos seriales: {e}")
                print(f"Línea problemática: {line}")
            
            time.sleep(0.1)  # Pequeña pausa para evitar sobrecarga del CPU