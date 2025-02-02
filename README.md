
# Backend para una arquitectura de tolerancia a fallas

Esta guía detalla cómo configurar un backend en Django con balanceo de carga usando Nginx.

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

3. Configurar la conexion con la base de datos en settings.py cambiando a las bases correspondientes:
   ```bash
      DATABASES = {
         'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'tolerancia_db',
            'USER': 'postgres',
            'PASSWORD': '0000',
            'HOST': '127.0.0.1', 
            'PORT': '5432',
         },  
         'otra_db': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'correos_db',
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

   python manage.py migrate --database=otra_db
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
Para probar tu aplicación en un entorno de desarrollo local, ejecuta el siguiente comando en la terminal:
   ```bash
   python manage.py runserver
   ```
Si deseas que otras máquinas en tu red puedan acceder a tu servidor de desarrollo, ejecuta el siguiente comando:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

# Configuracion Nginx
1. Descarga de Nginx
Descargamos la última versión disponible desde su página oficial 
https://nginx.org/download/nginx-1.27.3.zip.

2. nstalación en el disco raíz
Descomprimimos o instalamos Nginx en la ubicación deseada, por ejemplo:
```nginx
C:\nginx\nginx-1.26.2
```
3. Edición del archivo de configuración
Ingresamos a la carpeta de configuración:
```nginx
C:\nginx\nginx-1.26.2\conf
```

Aquí se encuentra el archivo nginx.conf:
```nginx
C:\nginx\nginx-1.26.2\conf\nginx.conf
```
Procedemos a editarlo de la siguiente forma:
```nginx
   # Definición de procesos de trabajo
   worker_processes  1;

   # Registro de errores
   error_log  logs/error.log  warn;

   events {
      worker_connections  1024;
   }

   http {
      include       mime.types;
      default_type  application/octet-stream;

      sendfile        on;
      keepalive_timeout  65;

      # Definición de upstream para el balanceo hacia los servidores de Django
      upstream django_backends {
         server 127.0.0.1:8000;       # IP de servidor de Django
         server 192.168.0.101:8000;   # IP de servidor de Django
      }

      server {
         listen 80;
         server_name 192.168.0.151;   # IP de servidor de Nginx

         # Bloque para servir el frontend
         location / {
               root "C:/nginx/html/dist";
               try_files $uri /index.html;
         }

         # Bloque para balancear las solicitudes /api
         location /api/ {
               proxy_pass http://django_backends;
               proxy_http_version 1.1;
               proxy_set_header Host $host;
         }

         # Páginas de error
         error_page   500 502 503 504  /50x.html;
         location = /50x.html {
               root   html;
         }
      }
   }
```


