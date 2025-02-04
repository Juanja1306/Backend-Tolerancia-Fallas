import os
import requests
import time
import subprocess

BASE_URL = "http://localhost:8000"  # URL base de tu aplicación
HEALTHCHECK_ENDPOINT = "/api/healtcheck/"
HEALTHCHECK_URL = f"{BASE_URL}{HEALTHCHECK_ENDPOINT}"

FAIL_THRESHOLD = 3         # Número de fallos consecutivos para disparar la acción
SLEEP_INTERVAL = 5       # Intervalo entre comprobaciones en segundos

def start_new_backend_instance():
    """
    Abre una nueva terminal y ejecuta el comando para iniciar una nueva instancia local del backend.
    En Windows se abre una ventana de CMD que ejecuta: `python manage.py runserver 8001`
    """
    print("=== Se ha detectado fallo en el healthcheck por 3 veces consecutivas ===")
    print("Iniciando una nueva instancia del backend en terminal...")

    try:
        if os.name == 'nt':
            # Windows: abre una nueva ventana de CMD y ejecuta el comando.
            # El comando 'start' es interno de cmd, por eso usamos shell=True.
            subprocess.Popen('start cmd /k "python manage.py runserver 0.0.0.0:8000"', shell=True)
        else:
            # En sistemas tipo Unix (Linux, macOS) se puede usar gnome-terminal o xterm.
            subprocess.Popen([
                "gnome-terminal", 
                "--", 
                "bash", 
                "-c", 
                "python manage.py runserver 8000; exec bash"
            ])
    except Exception as e:
        print(f"Error al intentar iniciar la nueva instancia: {e}")

def check_health():
    """
    Realiza una petición GET al endpoint de healthcheck.
    Retorna True si el servicio responde con status 200 y JSON {'status': 'ok'}, False en caso contrario.
    """
    try:
        response = requests.get(HEALTHCHECK_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status", "").strip().lower() == "ok":
                return True
    except Exception as e:
        print(f"Error en healthcheck: {e}")
    return False

def main():
    consecutive_failures = 0
    while True:
        if check_health():
            print("Healthcheck OK.")
            consecutive_failures = 0
        else:
            consecutive_failures += 1
            print(f"Fallo en healthcheck. Fallos consecutivos: {consecutive_failures}")
            if consecutive_failures >= FAIL_THRESHOLD:
                start_new_backend_instance()
                # Reiniciamos el contador de fallos tras lanzar la nueva instancia
                consecutive_failures = 0
        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main()
