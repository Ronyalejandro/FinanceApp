import PyInstaller.__main__
import os
import sys

# Definir los datos a incluir (formato: "origen;destino")
# En Windows se usa ";", en otros ":"
separator = ";" if sys.platform == "win32" else ":"

data = [
    (f"ui{separator}ui"),
    (f"db{separator}db"),
    (f"utils{separator}utils"),
    (f"assets{separator}assets"),
    (f"app_logo.ico{separator}."),
    (f"app_logo.png{separator}."),
    (f"fondo.jpg{separator}."),
    (f"config.py{separator}."),
]

params = [
    'main.py',                       # Script principal
    '--name=FinanceApp',             # Nombre del executable
    '--windowed',                    # Ocultar consola
    '--onefile',                     # Un solo archivo .exe
    '--icon=app_logo.ico',           # Icono del executable
    '--collect-all=customtkinter',   # Asegurar que customtkinter se incluya completo
    '--clean',                       # Limpiar cache antes de compilar
]

# Añadir datos al comando
for item in data:
    params.append(f'--add-data={item}')

if __name__ == "__main__":
    print("--- Configuración de Compilación de FinanceApp ---")
    print(f"Plataforma: {sys.platform}")
    print("Ejecutando PyInstaller...")
    
    try:
        PyInstaller.__main__.run(params)
        print("\n¡Éxito! El ejecutable se encuentra en la carpeta 'dist'.")
    except Exception as e:
        print(f"\nError durante la compilación: {e}")
        print("Asegúrate de tener PyInstaller instalado: pip install pyinstaller")
