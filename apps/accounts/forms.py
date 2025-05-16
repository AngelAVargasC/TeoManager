# apps/accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from apps.accounts.models import PerfilUsuario
from apps.accounts.models import LandingPage

class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(
        label="Correo electrónico",
        required=True,
        help_text="Requerido, debe ser único."
    )
    tipo_cuenta = forms.ChoiceField(
        label="¿Te registras como…?",
        choices=PerfilUsuario.CUENTA_TIPO_CHOICES,
        widget=forms.RadioSelect,
        initial='usuario',
        help_text="Elige 'Empresa' si vas a vender, o 'Usuario' si vas a comprar."
    )

    # Campos específicos para "Usuario"
    first_name = forms.CharField(
        label="Nombre",
        max_length=30,
        required=False,
        help_text="Obligatorio si te registras como Usuario."
    )
    last_name = forms.CharField(
        label="Apellido",
        max_length=30,
        required=False,
        help_text="Obligatorio si te registras como Usuario."
    )

    # Campos para "Empresa"
    empresa = forms.CharField(
        label="Empresa",
        max_length=100,
        required=False,
        help_text="Obligatorio si te registras como Empresa."
    )
    telefono = forms.CharField(
        label="Teléfono",
        max_length=15,
        required=False,
        help_text="Obligatorio si te registras como Empresa."
    )
    direccion = forms.CharField(
        label="Dirección",
        widget=forms.Textarea,
        required=False,
        help_text="Obligatorio si te registras como Empresa."
    )

    class Meta:
        model = User
        fields = [
            'username','email',
            'password1','password2',
            'tipo_cuenta',
            'first_name','last_name',
            'empresa','telefono','direccion',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inyectar clases y placeholders
        self.fields['username'].widget.attrs.update({
            'class':'form-input','placeholder':'Ingresa tu nombre de usuario'
        })
        self.fields['email'].widget.attrs.update({
            'class':'form-input','placeholder':'ejemplo@correo.com'
        })
        self.fields['password1'].widget.attrs.update({
            'class':'form-input','placeholder':'Mínimo 8 caracteres'
        })
        self.fields['password2'].widget.attrs.update({
            'class':'form-input','placeholder':'Repite tu contraseña'
        })
        self.fields['tipo_cuenta'].widget.attrs.update({
            'class':'radio-group'
        })
        self.fields['first_name'].widget.attrs.update({
            'class':'form-input','placeholder':'Tu nombre'
        })
        self.fields['last_name'].widget.attrs.update({
            'class':'form-input','placeholder':'Tu apellido'
        })
        self.fields['empresa'].widget.attrs.update({
            'class':'form-input','placeholder':'Nombre de tu empresa'
        })
        self.fields['telefono'].widget.attrs.update({
            'class':'form-input','placeholder':'Número de contacto'
        })
        self.fields['direccion'].widget.attrs.update({
            'class':'form-input','placeholder':'Dirección completa','rows':3
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('Ya existe un usuario registrado con este correo electrónico.')
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1') or ''
        if len(password) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
        if not any(c.isdigit() for c in password):
            raise ValidationError('La contraseña debe contener al menos un número.')
        if not any(c.isupper() for c in password):
            raise ValidationError('La contraseña debe contener al menos una letra mayúscula.')
        if not any(c.islower() for c in password):
            raise ValidationError('La contraseña debe contener al menos una letra minúscula.')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?/' for c in password):
            raise ValidationError('La contraseña debe contener al menos un carácter especial.')
        return password

    def clean(self):
        cleaned = super().clean()
        tipo = cleaned.get('tipo_cuenta')
        if tipo == 'empresa':
            # Requerir datos de empresa
            for f in ('empresa','telefono','direccion'):
                if not cleaned.get(f):
                    self.add_error(f, 'Requerido para cuentas de empresa.')
        else:
            # Requerir nombre y apellido
            for f in ('first_name','last_name'):
                if not cleaned.get(f):
                    self.add_error(f, 'Requerido para cuentas de usuario.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name','')
        user.last_name  = self.cleaned_data.get('last_name','')
        if commit:
            user.save()
            PerfilUsuario.objects.create(
                usuario=user,
                tipo_cuenta=self.cleaned_data['tipo_cuenta'],
                empresa=self.cleaned_data.get('empresa','').strip(),
                telefono=self.cleaned_data.get('telefono','').strip(),
                direccion=self.cleaned_data.get('direccion','').strip()
            )
        return user

class LandingPageForm(forms.ModelForm):
    """Formulario para crear o editar la landing page de una empresa."""
    class Meta:
        model = LandingPage
        # Incluyo el campo contenido para editar la sección 'Sobre nosotros'
        fields = ['titulo', 'descripcion', 'hero_image', 'plantilla', 'contenido']
        widgets = {
            'titulo': forms.TextInput(attrs={'class':'form-input','placeholder':'Título de tu página'}),
            'descripcion': forms.Textarea(attrs={'class':'form-input','placeholder':'Breve descripción o slogan','rows':3}),
            'hero_image': forms.URLInput(attrs={'class':'form-input','placeholder':'URL de la imagen de cabecera'}),
            'plantilla': forms.Select(attrs={'class':'form-input'}),
            'contenido': forms.Textarea(attrs={'class':'form-input','placeholder':'Contenido principal (ej. sección "Sobre Nosotros")','rows':6}),
        }
    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo','').strip()
        if not titulo:
            raise forms.ValidationError('El título no puede estar vacío.')
        return titulo
