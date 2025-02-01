from rest_framework import serializers # type: ignore
from .models import Persona, Imagen

class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = ['id', 'nombre', 'apellido', 'tipo_sangre', 'email', 'contrasenia']  # Incluye todos los campos necesarios

    # Opcional: Validación adicional para tipo_sangre
    def validate_tipo_sangre(self, value):
        valid_types = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']
        if value not in valid_types:
            raise serializers.ValidationError("Tipo de sangre inválido.")
        return value

class ImagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imagen
        fields = ['id', 'titulo', 'descripcion', 'url', 'fecha_subida']
