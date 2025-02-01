from django.contrib import admin # type: ignore
from .models import Persona

@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'apellido', 'email', 'tipo_sangre')
