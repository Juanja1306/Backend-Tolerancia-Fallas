from django.db import models # type: ignore

from django.utils.crypto import get_random_string # type: ignore
from django.contrib.auth.hashers import make_password # type: ignore

class Persona(models.Model):
    # ID autoincremental se crea automáticamente si no especificas un campo primary key
    nombre = models.CharField(max_length=50, null=False)
    apellido = models.CharField(max_length=50, null=False)
    tipo_sangre = models.CharField(max_length=3, null=False)  # Ejemplo: "O+", "AB-"
    email = models.EmailField(unique=True, null=False)
    contrasenia = models.CharField(max_length=128, null=False)

    def save(self, *args, **kwargs):
        """
        Sobreescribe el método save para hashear la contraseña antes de guardar.
        """
        if not self.contrasenia.startswith("pbkdf2_sha256$"):
            self.contrasenia = make_password(self.contrasenia)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Imagen(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    url = models.URLField(max_length=500, null=False, blank=False)  
    def __str__(self):
        return self.titulo


class PersonaImagen(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name="imagenes")
    imagen = models.ForeignKey(Imagen, on_delete=models.CASCADE, related_name="personas")
    fecha_asociacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.persona} - {self.imagen}"


class PersonaLite(models.Model):
    email = models.EmailField(unique=False)
    url = models.URLField(max_length=500, null=False, blank=False, default='https://www.google.com') 
    nombre = models.CharField(max_length=50, null=False, default='Nombre predeterminado')

    def __str__(self):
        return self.email
