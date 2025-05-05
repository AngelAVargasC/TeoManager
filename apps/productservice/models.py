from django.db import models
from django.contrib.auth.models import User
import os
from django.utils import timezone

# Modelo que representa un producto creado por un usuario.
class Producto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Usuario propietario del producto
    nombre = models.CharField(max_length=100)  # Nombre del producto
    descripcion = models.TextField()  # Descripción del producto
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # Precio
    stock = models.IntegerField(default=0)  # Stock disponible
    categoria = models.CharField(max_length=50)  # Categoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    activo = models.BooleanField(default=True)  # Si el producto está activo

    def __str__(self):
        return f"{self.nombre} - {self.usuario.username}"

    def delete(self, *args, **kwargs):
        # Elimina todas las imágenes asociadas al producto al eliminarlo
        for img in self.imagenes.all():
            img.delete()
        if hasattr(self, 'imagen') and self.imagen:
            if self.imagen.path and os.path.isfile(self.imagen.path):
                os.remove(self.imagen.path)
        super().delete(*args, **kwargs)

    @property
    def imagen_principal(self):
        """Devuelve la URL de la imagen principal del producto, si existe."""
        principal = self.imagenes.filter(principal=True).first()
        if principal:
            return principal.imagen.url
        primera = self.imagenes.first()
        if primera:
            return primera.imagen.url
        return None

# Modelo que representa una imagen asociada a un producto.
class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')  # Producto asociado
    imagen = models.ImageField(upload_to='productos/', null=False, blank=False)  # Archivo de imagen
    fecha_subida = models.DateTimeField(auto_now_add=True)  # Fecha de subida
    principal = models.BooleanField(default=False)  # Si es la imagen principal

    def __str__(self):
        return f"Imagen de {self.producto.nombre} ({self.id})"

    def delete(self, *args, **kwargs):
        # Elimina el archivo físico de la imagen al eliminar la instancia
        if self.imagen and self.imagen.path and os.path.isfile(self.imagen.path):
            os.remove(self.imagen.path)
        super().delete(*args, **kwargs)

# Modelo que representa un servicio creado por un usuario.
class Servicio(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Usuario propietario del servicio
    nombre = models.CharField(max_length=100)  # Nombre del servicio
    descripcion = models.TextField()  # Descripción del servicio
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # Precio
    duracion = models.CharField(max_length=50)  # Duración del servicio
    categoria = models.CharField(max_length=50)  # Categoría
    imagen = models.ImageField(upload_to='servicios/', null=True, blank=True)  # Imagen principal (opcional)
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    activo = models.BooleanField(default=True)  # Si el servicio está activo

    def __str__(self):
        return f"{self.nombre} - {self.usuario.username}"

    def delete(self, *args, **kwargs):
        # Elimina el archivo físico de la imagen al eliminar el servicio
        if self.imagen:
            if self.imagen.path and os.path.isfile(self.imagen.path):
                os.remove(self.imagen.path)
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        # Elimina la imagen anterior si se reemplaza
        try:
            this = Servicio.objects.get(pk=self.pk)
            if this.imagen != self.imagen and this.imagen and os.path.isfile(this.imagen.path):
                os.remove(this.imagen.path)
        except Exception:
            pass
        super().save(*args, **kwargs)

    @property
    def imagen_principal(self):
        """Devuelve la URL de la imagen principal del servicio, si existe."""
        principal = self.imagenes.filter(principal=True).first()
        if principal:
            return principal.imagen.url
        primera = self.imagenes.first()
        if primera:
            return primera.imagen.url
        return None

# Modelo que representa una imagen asociada a un servicio.
class ImagenServicio(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='imagenes')  # Servicio asociado
    imagen = models.ImageField(upload_to='servicios/', null=False, blank=False)  # Archivo de imagen
    fecha_subida = models.DateTimeField(auto_now_add=True)  # Fecha de subida
    principal = models.BooleanField(default=False)  # Si es la imagen principal

    def __str__(self):
        return f"Imagen de {self.servicio.nombre} ({self.id})"

    def delete(self, *args, **kwargs):
        # Elimina el archivo físico de la imagen al eliminar la instancia
        if self.imagen and self.imagen.path and os.path.isfile(self.imagen.path):
            os.remove(self.imagen.path)
        super().delete(*args, **kwargs)

# Modelo que representa un pedido realizado por un usuario.
class Pedido(models.Model):
    ESTADO_PEDIDO = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Usuario que realiza el pedido
    fecha_pedido = models.DateTimeField(auto_now_add=True)  # Fecha del pedido
    estado = models.CharField(max_length=20, choices=ESTADO_PEDIDO, default='pendiente')  # Estado actual
    total = models.DecimalField(max_digits=10, decimal_places=2)  # Total del pedido
    notas = models.TextField(blank=True)  # Notas adicionales

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username}"

# Modelo que representa el detalle de cada producto o servicio en un pedido.
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)  # Pedido asociado
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True)  # Producto (opcional)
    servicio = models.ForeignKey(Servicio, on_delete=models.SET_NULL, null=True, blank=True)  # Servicio (opcional)
    cantidad = models.IntegerField(default=1)  # Cantidad solicitada
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)  # Precio unitario
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)  # Subtotal

    def __str__(self):
        return f"Detalle de Pedido #{self.pedido.id}"
