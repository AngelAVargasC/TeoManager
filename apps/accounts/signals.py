from django.db.models.signals import post_delete
from django.dispatch import receiver
from apps.productservice.models import Servicio
import os
from django.contrib.auth.signals import user_logged_in
from django.contrib import messages

# El signal para Producto se elimina porque las imágenes se gestionan en ImagenProducto y en el método delete de Producto

@receiver(post_delete, sender=Servicio)
def eliminar_imagen_servicio(sender, instance, **kwargs):
    if instance.imagen and instance.imagen.path and os.path.isfile(instance.imagen.path):
        os.remove(instance.imagen.path)

@receiver(user_logged_in)
def mostrar_mensaje_login(sender, user, request, **kwargs):
    messages.success(request, '¡Has iniciado sesión correctamente!') 