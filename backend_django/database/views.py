from django.http import JsonResponse
from .models import Imagen, PersonaImagen, Persona, Changes
from backend_django.settings import bucket
from rest_framework.decorators import api_view #type: ignore
from rest_framework.response import Response#type: ignore
from rest_framework import status #type: ignore
from .serializers import PersonaSerializer
from rest_framework_simplejwt.tokens import RefreshToken#type: ignore
from .serializers import PersonaSerializer, ImagenSerializer
from django.contrib.auth.hashers import check_password
from .models import PersonaLite

def log_change(metodo, tabla, descripcion):
    """
    Registra un cambio en el modelo Changes.
    
    :param metodo: Método de la operación ('INSERT', 'DELETE', 'UPDATE', etc.)
    :param tabla: Nombre de la tabla afectada.
    :param descripcion: Diccionario con los detalles del cambio.
    """
    Changes.objects.create(metodo=metodo, tabla=tabla, descripcion=descripcion)


@api_view(['GET'])
def lista_imagenes(request):
    if request.method == 'GET':
        imagenes = Imagen.objects.all()
        data = [
            {
                'id': imagen.id,
                'titulo': imagen.titulo,
                'descripcion': imagen.descripcion,
                'url': imagen.url,
                'fecha_subida': imagen.fecha_subida,
            }
            for imagen in imagenes
        ]
        return JsonResponse({'imagenes': data}, status=200)  # Respuesta exitosa
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@api_view(['POST'])
def crear_persona(request):
    try:
        # Serializar los datos enviados en la solicitud
        serializer = PersonaSerializer(data=request.data)

        if serializer.is_valid():
            # Guardar la nueva persona
            persona = serializer.save()
            log_change(
                metodo='INSERT',
                tabla='Persona',
                descripcion={
                    'id': persona.id,
                    'nombre': persona.nombre,
                    'apellido': persona.apellido,
                    'tipo_sangre': persona.tipo_sangre,
                    'email': persona.email,
                    'contrasenia': persona.contrasenia,
                    # Nota: la contraseña ya se guarda hasheada.
                }
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # Respuesta exitosa
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Errores de validación
    except Exception as e:
        print(e)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  # Error del servidor

@api_view(['POST'])
def login_usuario(request):
    email = request.data.get('email')
    contrasenia = request.data.get('contrasenia')

    try:
        user = Persona.objects.get(email=email)  # Busca al usuario por email
        if check_password(contrasenia, user.contrasenia):  # Verifica la contraseña
            return JsonResponse({'mensaje': 'Inicio de sesión exitoso', 'ID': user.id}, status=200)
        else:
            return JsonResponse({'error': 'Contraseña incorrecta'}, status=401)
    except Persona.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

@api_view(['GET'])
def health_check(request):
    return JsonResponse({'status': ' ok'}, status=200)

@api_view(['POST'])
def subir_imagen_y_asociar(request):
    email = request.data.get('email')
    contrasenia = request.data.get('contrasenia')

    # Verificar las credenciales del usuario
    try:
        persona = Persona.objects.get(email=email)
        if not check_password(contrasenia, persona.contrasenia):
            return JsonResponse({'error': 'Credenciales inválidas'}, status=401)
    except Persona.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

    try:
        # Subir el archivo al bucket de Google Cloud Storage
        archivo = request.FILES['archivo']
        blob_name = archivo.name
        blob = bucket.blob(blob_name)
        blob.upload_from_file(archivo.file, content_type=archivo.content_type)

        # Crear la entrada de la imagen
        data = request.data
        data['url'] = blob.public_url
        serializer = ImagenSerializer(data=data)

        if serializer.is_valid():
            imagen = serializer.save()
            log_change(
                metodo='INSERT',
                tabla='Imagen',
                descripcion={
                    'id': imagen.id,
                    'titulo': imagen.titulo,
                    'descripcion': imagen.descripcion,
                    'url': imagen.url,
                    'fecha_subida': imagen.fecha_subida.isoformat() if imagen.fecha_subida else None
                }
            )

            # Crear la relación en PersonaImagen
            relacion = PersonaImagen.objects.create(persona=persona, imagen=imagen)
            log_change(
                metodo='INSERT',
                tabla='PersonaImagen',
                descripcion={
                    'id': relacion.id,
                    'persona_id': persona.id,
                    'imagen_id': imagen.id,
                    'fecha_asociacion': relacion.fecha_asociacion.isoformat() if relacion.fecha_asociacion else None
                }
            )
            
            persona_lite = PersonaLite.objects.create(email=email, url=blob.public_url, nombre=persona.nombre)

            return JsonResponse({
                'mensaje': 'Imagen subida y relación creada exitosamente.',
                'imagen': serializer.data,
                'relacion': {
                    'persona': relacion.persona.id,
                    'imagen': relacion.imagen.id,
                },
                'persona_lite': {
                    'id': persona_lite.id,
                    'email': persona_lite.email,
                    'url': persona_lite.url,
                    'nombre': persona_lite.nombre,
                    
                }
            }, status=201)
        return JsonResponse(serializer.errors, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
def obtener_imagenes_por_usuario(request, usuario_id):
    try:
        # Buscar al usuario por ID
        persona = Persona.objects.get(id=usuario_id)

        # Obtener las relaciones PersonaImagen
        relaciones = PersonaImagen.objects.filter(persona=persona)

        # Obtener las imágenes asociadas
        imagenes = [relacion.imagen for relacion in relaciones]

        # Serializar las imágenes
        data = [
            {
                'id': imagen.id,
                'titulo': imagen.titulo,
                'descripcion': imagen.descripcion,
                'url': imagen.url,
                'fecha_subida': imagen.fecha_subida,
            }
            for imagen in imagenes
        ]

        return JsonResponse({'imagenes': data}, status=200)
    except Persona.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['DELETE'])
def eliminar_imagen(request):
    email = request.data.get('email')
    contrasenia = request.data.get('contrasenia')
    imagen_id = request.data.get('imagen_id')

    # Verificar las credenciales del usuario
    try:
        persona = Persona.objects.get(email=email)
        if not check_password(contrasenia, persona.contrasenia):
            return JsonResponse({'error': 'Credenciales inválidas'}, status=401)
    except Persona.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

    try:
        # Obtener la imagen y la relación
        imagen = Imagen.objects.get(id=imagen_id)
        relacion = PersonaImagen.objects.get(persona=persona, imagen=imagen)

        # Eliminar la imagen del bucket de Google Cloud Storage
        blob_name = imagen.url.split('/')[-1]
        blob = bucket.blob(blob_name)
        blob.delete()
        log_change(
            metodo='DELETE',
            tabla='PersonaImagen',
            descripcion={
                'id': relacion.id,
                'persona_id': persona.id,
                'imagen_id': imagen.id,
                'fecha_asociacion': relacion.fecha_asociacion.isoformat() if relacion.fecha_asociacion else None
            }
        )

        # Eliminar la relación y la imagen de la base de datos
        relacion.delete()
        log_change(
            metodo='DELETE',
            tabla='Imagen',
            descripcion={
                'id': imagen.id,
                'titulo': imagen.titulo,
                'descripcion': imagen.descripcion,
                'url': imagen.url,
                'fecha_subida': imagen.fecha_subida.isoformat() if imagen.fecha_subida else None
            }
        )
        imagen.delete()

        return JsonResponse({'mensaje': 'Imagen eliminada exitosamente.'}, status=200)
    except Imagen.DoesNotExist:
        return JsonResponse({'error': 'Imagen no encontrada'}, status=404)
    except PersonaImagen.DoesNotExist:
        return JsonResponse({'error': 'La imagen no le pertenece'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ----------------------------------------------

@api_view(['GET', 'POST','DELETE'])
def persona_lite_view(request):
    if request.method == 'GET':
        # Esto se enruta automáticamente a 'otra_db' por el router
        personas_lite = PersonaLite.objects.all()
        data = [{"id": p.id, "email": p.email, "url": p.url,"nombre": p.nombre,} for p in personas_lite]
        return Response(data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        email = request.data.get('email')
        url = request.data.get('url')
        nombre = request.data.get('nombre')
        if not email:
            return Response({"error": "Falta el email"}, status=status.HTTP_400_BAD_REQUEST)

        # Se enruta automáticamente a 'otra_db'
        persona_lite = PersonaLite.objects.create(email=email, url=url, nombre=nombre)
        return Response(
            {"id": persona_lite.id, "email": persona_lite.email, "url": persona_lite.url, "nombre": persona_lite.nombre},
            status=status.HTTP_201_CREATED
        )
    elif request.method == 'DELETE':
        email = request.data.get('email')
        if not email:
            return Response({"error": "Falta el email"}, status=status.HTTP_400_BAD_REQUEST)

        # Se enruta automáticamente a 'otra_db'
        try:
            persona_lite = PersonaLite.objects.get(email=email)
            persona_lite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except PersonaLite.DoesNotExist:
            return Response({"error": "PersonaLite no encontrada"}, status=status.HTTP_404_NOT_FOUND)
