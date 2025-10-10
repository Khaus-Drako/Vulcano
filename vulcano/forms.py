"""
Formularios para la plataforma Vulcano.
Incluye validaciones personalizadas y widgets mejorados.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile, Project, ProjectImage, Message


class CustomUserCreationForm(UserCreationForm):
    """
    Formulario personalizado de registro con campos adicionales.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellidos'
        })
    )
    role = forms.ChoiceField(
        choices=[('cliente', 'Cliente'), ('arquitecto', 'Arquitecto')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Teléfono (opcional)'
        })
    )
    company = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Empresa (opcional)'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Usuario'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
    
    def clean_email(self):
        """Valida que el email no esté registrado."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este correo electrónico ya está registrado.')
        return email
    
    def save(self, commit=True):
        """Guarda el usuario y crea su perfil."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Crear o actualizar perfil de usuario
            profile, created = UserProfile.objects.get_or_create(user=user)
            # Actualizar perfil con los datos del formulario
            profile.role = self.cleaned_data['role']
            profile.phone = self.cleaned_data.get('phone', '')
            profile.company = self.cleaned_data.get('company', '')
            profile.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """
    Formulario de autenticación con estilos personalizados.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )


class ProjectForm(forms.ModelForm):
    """
    Formulario para crear y editar proyectos arquitectónicos.
    """
    class Meta:
        model = Project
        fields = [
            'title', 'description', 'short_description', 'category',
            'status', 'location', 'area', 'budget', 'start_date',
            'end_date', 'clients', 'is_featured', 'is_published'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del proyecto'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Descripción detallada del proyecto'
            }),
            'short_description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Resumen breve (máx. 300 caracteres)'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad, Estado, País'
            }),
            'area': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Área en metros cuadrados',
                'step': '0.01'
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Presupuesto estimado',
                'step': '0.01'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'clients': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo usuarios con rol cliente
        self.fields['clients'].queryset = User.objects.filter(
            profile__role='cliente'
        ).order_by('first_name', 'last_name')
        self.fields['clients'].label_from_instance = lambda obj: f"{obj.get_full_name()} ({obj.username})"
    
    def clean(self):
        """Validaciones personalizadas."""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        area = cleaned_data.get('area')
        budget = cleaned_data.get('budget')
        
        if start_date and end_date and end_date < start_date:
            raise ValidationError('La fecha de finalización debe ser posterior a la fecha de inicio.')
        
        if area is not None and area < 0:
            self.add_error('area', 'El área no puede ser negativa.')
        
        if budget is not None and budget < 0:
            self.add_error('budget', 'El presupuesto no puede ser negativo.')
        
        return cleaned_data


class ProjectImageForm(forms.ModelForm):
    """
    Formulario para subir imágenes a proyectos.
    """
    class Meta:
        model = ProjectImage
        fields = ['image', 'caption', 'is_main', 'order']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/jpg,image/png,image/webp'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción de la imagen (opcional)'
            }),
            'is_main': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
        }


class MultipleImageUploadForm(forms.Form):
    """
    Formulario para subir múltiples imágenes simultáneamente.
    """
    images = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            # 'multiple': True,
            'class': 'form-control',
            'accept': 'image/jpeg,image/jpg,image/png,image/webp'
        }),
        label='Imágenes',
        help_text='Selecciona una o más imágenes (JPG, PNG, WEBP)',
        required=True
    )


class MessageForm(forms.ModelForm):
    """
    Formulario para enviar mensajes internos.
    """
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'body', 'project']
        widgets = {
            'recipient': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Asunto del mensaje'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Escribe tu mensaje aquí...'
            }),
            'project': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        
        # Filtrar destinatarios según el rol del usuario
        if user.profile.is_cliente():
            # Los clientes solo pueden enviar mensajes a arquitectos de sus proyectos
            arquitectos_ids = user.assigned_projects.values_list('arquitecto_id', flat=True).distinct()
            self.fields['recipient'].queryset = User.objects.filter(id__in=arquitectos_ids)
            self.fields['project'].queryset = user.assigned_projects.all()
        elif user.profile.is_arquitecto():
            # Los arquitectos pueden enviar mensajes a clientes de sus proyectos
            clientes_ids = Project.objects.filter(arquitecto=user).values_list('clients__id', flat=True).distinct()
            self.fields['recipient'].queryset = User.objects.filter(id__in=clientes_ids)
            self.fields['project'].queryset = Project.objects.filter(arquitecto=user)
        else:
            # Los administradores pueden enviar mensajes a todos
            self.fields['recipient'].queryset = User.objects.exclude(id=user.id)
            self.fields['project'].queryset = Project.objects.all()
        
        self.fields['recipient'].label_from_instance = lambda obj: f"{obj.get_full_name()} ({obj.username})"
        self.fields['project'].required = False


class UserProfileForm(forms.ModelForm):
    """
    Formulario para editar el perfil de usuario.
    """
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = UserProfile
        fields = ['phone', 'company', 'bio', 'avatar']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/jpg,image/png,image/webp'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        """Guarda tanto el perfil como los datos del usuario."""
        profile = super().save(commit=False)
        if commit:
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()
            profile.save()
        return profile