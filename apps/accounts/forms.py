from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from apps.accounts.models import PerfilUsuario
from django.core.exceptions import ValidationError

# Formulario de registro de usuario extendido, incluye campos adicionales y validaciones personalizadas.
class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Correo electrónico obligatorio
    empresa = forms.CharField(max_length=100, required=True)  # Nombre de la empresa
    telefono = forms.CharField(max_length=15, required=True)  # Teléfono de contacto
    direccion = forms.CharField(widget=forms.Textarea, required=True)  # Dirección física

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'empresa', 'telefono', 'direccion')

    # Validación personalizada para el email (único)
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Ya existe un usuario registrado con este correo electrónico.')
        return email

    # Validación personalizada para la contraseña (fuerza mínima)
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
        if not any(char.isdigit() for char in password):
            raise ValidationError('La contraseña debe contener al menos un número.')
        if not any(char.isupper() for char in password):
            raise ValidationError('La contraseña debe contener al menos una letra mayúscula.')
        if not any(char.islower() for char in password):
            raise ValidationError('La contraseña debe contener al menos una letra minúscula.')
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/' for char in password):
            raise ValidationError('La contraseña debe contener al menos un carácter especial.')
        return password

    # Guarda el usuario y crea el perfil extendido asociado.
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Crear el perfil de usuario
            PerfilUsuario.objects.create(
                usuario=user,
                empresa=self.cleaned_data['empresa'],
                telefono=self.cleaned_data['telefono'],
                direccion=self.cleaned_data['direccion']
            )
        return user 
