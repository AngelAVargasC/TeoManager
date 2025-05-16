from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Modelo que almacena el perfil extendido de cada usuario, incluyendo empresa, teléfono, dirección y permisos.
class PerfilUsuario(models.Model):
    # 1) Defino las opciones de tipo de cuenta
    CUENTA_TIPO_CHOICES = [
        ('empresa', 'Empresa'),
        ('usuario', 'Usuario'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    # 2) Nuevo campo para distinguir registro Empresa vs Usuario
    tipo_cuenta = models.CharField(
        max_length=10,
        choices=CUENTA_TIPO_CHOICES,
        default='usuario',
        help_text="¿Te registras como empresa o como consumidor?"
    )

    # --- tus campos existentes ---
    empresa = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    direccion = models.TextField()
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ESTADO_SUSCRIPCION = [
        ('activa',   'Activa'),
        ('inactiva', 'Inactiva'),
        ('vencida',  'Vencida'),
    ]
    estado_suscripcion = models.CharField(max_length=10, choices=ESTADO_SUSCRIPCION, default='inactiva')
    fecha_vencimiento = models.DateTimeField(null=True, blank=True)
    PERMISOS = [
        ('Usuario',      'Usuario'),
        ('Administrador','Administrador'),
    ]
    permisos = models.CharField(max_length=20, choices=PERMISOS, default='Usuario')

    def __str__(self):
        return f"{self.usuario.username} ({self.get_tipo_cuenta_display()})"

    @property
    def is_admin(self):
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

class LandingPage(models.Model):
    """Modelo para almacenar contenido de la landing page de una empresa."""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='landing_pages')
    titulo = models.CharField(max_length=200, help_text='Título principal de la página')
    descripcion = models.TextField(blank=True, help_text='Breve descripción o slogan de la empresa')
    hero_image = models.URLField(blank=True, null=True, help_text='URL de la imagen de cabecera (hero)')
    contenido = models.TextField(blank=True, help_text='texto enriquecido para la sección principal')
    # Plantillas disponibles
    PLANTILLA_CHOICES = [
        ('plantilla1', 'Plantilla Clásica'),
        ('plantilla2', 'Plantilla Moderna'),
    ]
    plantilla = models.CharField(max_length=50, choices=PLANTILLA_CHOICES, default='plantilla1', help_text='Selecciona el diseño de tu landing page')
    color_scheme = models.CharField(max_length=50, default='default', help_text='Esquema de color o tema para la página')
    fecha_creacion = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"LandingPage de {self.usuario.username} - {self.get_plantilla_display()}"
