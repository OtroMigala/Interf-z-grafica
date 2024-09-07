import serial

def main():
    # Configura el puerto serial
    try:
        ser = serial.Serial('COM3', 115200, timeout=1)
        print(f"Conectado al puerto: {ser.portstr}")

        while True:
            # Lee la línea desde el puerto serial
            line = ser.readline().decode('utf-8').strip()
            if line:
                print(f"Datos recibidos: {line}")
                
    except serial.SerialException as e:
        print(f"Error al abrir el puerto serial: {e}")
    except KeyboardInterrupt:
        print("Finalizando la lectura...")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Puerto serial cerrado.")

if __name__ == "__main__":
    main()
