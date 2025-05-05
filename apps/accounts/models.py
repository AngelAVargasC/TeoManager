from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Modelo que almacena el perfil extendido de cada usuario, incluyendo empresa, teléfono, dirección y permisos.
class PerfilUsuario(models.Model):
    # Opciones de estado de suscripción del usuario
    ESTADO_SUSCRIPCION = [
        ('activa', 'Activa'),
        ('inactiva', 'Inactiva'),
        ('vencida', 'Vencida'),
    ]
    # Tipos de permisos para el usuario
    PERMISOS = [
        ('Usuario', 'Usuario'),
        ('Administrador', 'Administrador'),
    ]
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')  # Relación uno a uno con el modelo User
    empresa = models.CharField(max_length=100)  # Nombre de la empresa del usuario
    telefono = models.CharField(max_length=15)  # Teléfono de contacto
    direccion = models.TextField()  # Dirección física
    fecha_registro = models.DateTimeField(auto_now_add=True)  # Fecha de registro del perfil
    estado_suscripcion = models.CharField(max_length=10, choices=ESTADO_SUSCRIPCION, default='inactiva')  # Estado de la suscripción
    fecha_vencimiento = models.DateTimeField(null=True, blank=True)  # Fecha de vencimiento de la suscripción
    permisos = models.CharField(max_length=20, choices=PERMISOS, default='Usuario')  # Permiso del usuario

    def __str__(self):
        return f"{self.usuario.username} - {self.empresa}"

    @property
    def is_admin(self):
        """Propiedad para saber si el usuario es administrador."""
        return self.permisos == 'Administrador'

# Modelo que almacena la suscripción de un usuario a un plan específico.
class Suscripcion(models.Model):
    PLANES = [
        ('basico', 'Básico'),
        ('premium', 'Premium'),
        ('empresarial', 'Empresarial'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)  # Usuario que tiene la suscripción
    plan = models.CharField(max_length=20, choices=PLANES)  # Tipo de plan
    fecha_inicio = models.DateTimeField(auto_now_add=True)  # Fecha de inicio de la suscripción
    fecha_vencimiento = models.DateTimeField()  # Fecha de vencimiento
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # Precio del plan
    activa = models.BooleanField(default=True)  # Si la suscripción está activa

    def __str__(self):
        return f"{self.usuario.username} - {self.plan}"
