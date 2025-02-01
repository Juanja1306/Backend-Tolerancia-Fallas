
from django.contrib import admin # type: ignore
from django.urls import path # type: ignore
from database import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/crear_persona/', views.crear_persona, name='crear_persona'),
    
    #path('api/subir_imagen/', views.subir_imagen, name='subir_imagen'),
    path('api/lista_imagenes/', views.lista_imagenes, name='lista_imagenes'),
    
    path('api/login/', views.login_usuario, name='login_usuario'),
    
    path('api/subir_imagen/', views.subir_imagen_y_asociar, name='subir_imagen_y_asociar'),
    
    path('api/imagenes/<int:usuario_id>/', views.obtener_imagenes_por_usuario, name='obtener_imagenes_por_usuario'),
    
    path('api/healtcheck/', views.health_check, name='healthcheck'),
    
    path('api/eliminar_imagen/', views.eliminar_imagen, name='eliminar_imagen'),
]
