# from django.shortcuts import render, redirect # type: ignore
# from .forms import ImagenForm
# from .models import Imagen
# from django.core.files.storage import default_storage # type: ignore
# from google.cloud import storage
# from backend_django.settings import bucket
from django.http import JsonResponse
from .models import Imagen, PersonaImagen, Persona
from backend_django.settings import bucket
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import PersonaSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import PersonaSerializer, ImagenSerializer
from django.contrib.auth.hashers import check_password



@api_view(['POST'])
def subir_imagen(request):
    try:
        archivo = request.FILES['archivo']
        blob_name = archivo.name
        blob = bucket.blob(blob_name)
        blob.upload_from_file(archivo.file, content_type=archivo.content_type)

        data = request.data
        data['url'] = blob.public_url
        serializer = ImagenSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            serializer.save()
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

            # Crear la relación en PersonaImagen
            relacion = PersonaImagen.objects.create(persona=persona, imagen=imagen)

            return JsonResponse({
                'mensaje': 'Imagen subida y relación creada exitosamente.',
                'imagen': serializer.data,
                'relacion': {
                    'persona': relacion.persona.id,
                    'imagen': relacion.imagen.id,
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

        # Eliminar la relación y la imagen de la base de datos
        relacion.delete()
        imagen.delete()

        return JsonResponse({'mensaje': 'Imagen eliminada exitosamente.'}, status=200)
    except Imagen.DoesNotExist:
        return JsonResponse({'error': 'Imagen no encontrada'}, status=404)
    except PersonaImagen.DoesNotExist:
        return JsonResponse({'error': 'La imagen no le pertenece'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# def subir_imagen(request):
#     if request.method == 'POST':
#         form = ImagenForm(request.POST)
#         if form.is_valid():
#             try:
#                 # Configuración del cliente de Google Cloud Storage

#                 # Subir la imagen al bucket
#                 archivo = request.FILES['archivo']  # El archivo subido por el usuario
#                 blob_name = archivo.name
#                 blob = bucket.blob(blob_name)

#                 # Subir el archivo al bucket
#                 blob.upload_from_file(archivo.file, content_type=archivo.content_type)

#                 # Guardar la URL pública en el modelo
#                 imagen = form.save(commit=False)  # Guarda el modelo pero no en la BD
#                 imagen.url = blob.public_url  # Asigna la URL pública generada
#                 imagen.save()  # Guarda en la base de datos

#                 print("Imagen subida y guardada correctamente.")
#                 return redirect('lista_imagenes')
#             except Exception as e:
#                 print(f"Error al guardar la imagen: {e}")
#         else:
#             print(f"Errores del formulario: {form.errors}")
#     else:
#         form = ImagenForm()
#     return render(request, 'database/subir_imagen.html', {'form': form})


# def lista_imagenes(request):
#     imagenes = Imagen.objects.all()
#     return render(request, 'database/lista_imagenes.html', {'imagenes': imagenes})


