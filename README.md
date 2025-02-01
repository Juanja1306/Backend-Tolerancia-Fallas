
# Backend para una arquitectura de tolerancia a fallas

Esta guía detalla cómo configurar un backend en Django sobre una VM de Google Cloud, incluyendo la configuración de HTTP y HTTPS.

---

# Configuracion del Backend

1. Crea un entorno virtual:
   ```bash
   python -m venv .venv
   ```

2. Activa el entorno virtual e instala las dependencias:
   ```bash
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configurar la conexion con la base de datos en settings.py:
   ```bash
      DATABASES = {
         'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'tolerancia_db',
            'USER': 'postgres',
            'PASSWORD': '0000',
            'HOST': '127.0.0.1', 
            'PORT': '5432',
         }  
      }

   ```

4. Forzar makemigrations
   ```bash
   python manage.py makemigrations database -v 3
   python manage.py migrate
   ```

5. Crea el archivo de credenciales:
   ```bash
   nano inspiring-bonus-445203-p0-d3aab7b05921.json
   ```

6. Configura las credenciales en el archivo `settings.py`:
   - Abre `/home/usuario/backend-django-virtualizacion/backend_django/backend_django/settings.py`.
   - Añade lo siguiente, reemplazando la ruta del archivo:
     ```python
     GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
         r"/home/usuario/backend-django-virtualizacion/inspiring-bonus-445203-p0-d3aab7b05921.json"
     )
     ```

---

# Correr al servidor

1. Ejecuta el servidor:
   ```bash
   python manage.py runserver
   ```