import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import tkinter as tk
from tkintermapview import TkinterMapView
import os
from PIL import ImageGrab
import time
import folium # Importar la librería folium
from folium import plugins

# Definir la ruta de salida
OUTPUT_PATH = r"C:\Users\juan_\Documents\Unicauca\TULCAN-SAT UMNG 2024\Interfáz grafica\Informe"

# Cargar los datos
df = pd.read_csv('C:/Users/juan_/Documents/Unicauca/TULCAN-SAT UMNG 2024/Interfáz grafica/capturas/datos_sensor.csv')

# Convertir 'Tiempo(s)' a numérico, reemplazando cadenas vacías con NaN
df['Tiempo(s)'] = pd.to_numeric(df['Tiempo(s)'], errors='coerce')

# Funciones de análisis y generación de gráficos (mantener las funciones anteriores)

def get_stats(column):
    return {
        'mean': df[column].mean(),
        'median': df[column].median(),
        'std': df[column].std(),
        'min': df[column].min(),
        'max': df[column].max()
    }

def generate_report():
    report = "CanSat Data Analysis Report\n"
    report += "===========================\n\n"
    
    report += "1. Basic Statistics:\n"
    for column in df.columns:
        if df[column].dtype in ['float64', 'int64']:
            stats = get_stats(column)
            report += f"\n{column}:\n"
            for stat, value in stats.items():
                report += f"  {stat}: {value:.2f}\n"
    
    report += "\n2. Altitude Analysis:\n"
    alt_columns = ['Altitud_BMP280(m)', 'Altitud_Relativa(m)', 'Altitud_GPS(m)']
    for col in alt_columns:
        if col in df.columns:
            report += f"\n{col}:\n"
            report += f"  Max altitude: {df[col].max():.2f} m\n"
            report += f"  Min altitude: {df[col].min():.2f} m\n"
            report += f"  Average altitude: {df[col].mean():.2f} m\n"
    
    report += "\n3. Temperature and Pressure Correlation:\n"
    correlation = df['Temperatura(°C)'].corr(df['Presión(Pa)'])
    report += f"Correlation coefficient: {correlation:.2f}\n"
    
    report += "\n4. Acceleration Analysis:\n"
    acc_columns = ['AccX(g)', 'AccY(g)', 'AccZ(g)']
    total_acc = (df[acc_columns]**2).sum(axis=1)**0.5
    report += f"Max total acceleration: {total_acc.max():.2f} g\n"
    report += f"Average total acceleration: {total_acc.mean():.2f} g\n"
    
    report += "\n5. GPS Data:\n"
    report += f"Starting coordinates: Lat {df['Latitud'].iloc[0]:.6f}, Lon {df['Longitud'].iloc[0]:.6f}\n"
    report += f"Ending coordinates: Lat {df['Latitud'].iloc[-1]:.6f}, Lon {df['Longitud'].iloc[-1]:.6f}\n"
    
    report += "\n6. Data Completeness:\n"
    missing_data = df.isnull().sum()
    report += "Number of missing values per column:\n"
    report += str(missing_data[missing_data > 0])
    
    return report

def generate_plots():
    # Altitude vs Time plot
    plt.figure(figsize=(12, 6))
    plt.plot(df['Tiempo(s)'], df['Altitud_BMP280(m)'], label='BMP280')
    plt.plot(df['Tiempo(s)'], df['Altitud_Relativa(m)'], label='Relative')
    if 'Altitud_GPS(m)' in df.columns:
        plt.plot(df['Tiempo(s)'], df['Altitud_GPS(m)'], label='GPS')
    plt.xlabel('Time (s)')
    plt.ylabel('Altitude (m)')
    plt.title('Altitude vs Time')
    plt.legend()
    plt.savefig(os.path.join(OUTPUT_PATH, 'altitude_vs_time.png'))
    plt.close()

    # Temperature vs Pressure scatter plot
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='Presión(Pa)', y='Temperatura(°C)', data=df)
    plt.title('Temperature vs Pressure')
    plt.savefig(os.path.join(OUTPUT_PATH, 'temperature_vs_pressure.png'))
    plt.close()

    # Acceleration plot
    acc_columns = ['AccX(g)', 'AccY(g)', 'AccZ(g)']
    plt.figure(figsize=(12, 6))
    for col in acc_columns:
        plt.plot(df['Tiempo(s)'], df[col], label=col)
    plt.xlabel('Time (s)')
    plt.ylabel('Acceleration (g)')
    plt.title('Acceleration vs Time')
    plt.legend()
    plt.savefig(os.path.join(OUTPUT_PATH, 'acceleration_vs_time.png'))
    plt.close()

def generate_gps_map():
    # Filtrar coordenadas válidas
    valid_coords = df[(df['Latitud'] != 0) & (df['Longitud'] != 0)]

    if len(valid_coords) > 0:
        # Crear un mapa centrado en la primera coordenada válida
        m = folium.Map(location=[valid_coords.iloc[0]['Latitud'], valid_coords.iloc[0]['Longitud']], zoom_start=14)

        # Añadir el recorrido
        points = valid_coords[['Latitud', 'Longitud']].values.tolist()
        folium.PolyLine(points, weight=2, color='blue', opacity=0.8).add_to(m)

        # Añadir marcadores para el inicio y fin del recorrido
        folium.Marker(
            location=[valid_coords.iloc[0]['Latitud'], valid_coords.iloc[0]['Longitud']],
            popup='Inicio',
            icon=folium.Icon(color='green', icon='play')
        ).add_to(m)

        folium.Marker(
            location=[valid_coords.iloc[-1]['Latitud'], valid_coords.iloc[-1]['Longitud']],
            popup='Fin',
            icon=folium.Icon(color='red', icon='stop')
        ).add_to(m)

        # Añadir minimap
        minimap = plugins.MiniMap()
        m.add_child(minimap)

        # Añadir control de escala
        folium.plugins.MousePosition().add_to(m)
        folium.plugins.MeasureControl().add_to(m)

        # Guardar el mapa como archivo HTML
        map_path = os.path.join(OUTPUT_PATH, "gps_trajectory_map.html")
        m.save(map_path)
        print(f"Mapa GPS guardado en: {map_path}")
    else:
        print("No se encontraron coordenadas GPS válidas en los datos.")
if __name__ == "__main__":
    # Generar y guardar el informe
    report = generate_report()
    with open(os.path.join(OUTPUT_PATH, 'cansat_analysis_report.txt'), 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Generar y guardar gráficos
    generate_plots()
    
    # Generar y guardar mapa GPS
    generate_gps_map()
    
    # Guardar datos estadísticos en formato CSV
    stats_df = pd.DataFrame()
    for column in df.select_dtypes(include=['float64', 'int64']).columns:
        stats = get_stats(column)
        stats_df[column] = pd.Series(stats)
    stats_df.to_csv(os.path.join(OUTPUT_PATH, 'cansat_statistics.csv'))
    
    print(f"Análisis completo. Los resultados se han guardado en: {OUTPUT_PATH}")
    # Generar y guardar el informe
    report = generate_report()
    with open(os.path.join(OUTPUT_PATH, 'cansat_analysis_report.txt'), 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Generar y guardar gráficos
    generate_plots()
    
    # Generar y guardar mapa GPS
    generate_gps_map()
    
    # Guardar datos estadísticos en formato CSV
    stats_df = pd.DataFrame()
    for column in df.select_dtypes(include=['float64', 'int64']).columns:
        stats = get_stats(column)
        stats_df[column] = pd.Series(stats)
    stats_df.to_csv(os.path.join(OUTPUT_PATH, 'cansat_statistics.csv'))
    
    print(f"Análisis completo. Los resultados se han guardado en: {OUTPUT_PATH}")