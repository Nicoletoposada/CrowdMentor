# core/forms.py
from django import forms # type: ignore
from django.contrib.auth.forms import UserCreationForm # type: ignore
from django.contrib.auth.models import User # type: ignore
from .models import Profile, Project, Investment

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
            if len(result) > 10:
                raise forms.ValidationError('No puedes subir más de 10 archivos.')
            return result
        return single_file_clean(data, initial)

class CustomUserCreationForm(UserCreationForm):
    user_type = forms.ChoiceField(
        choices=Profile.USER_TYPES,
        widget=forms.Select(attrs={'class': 'form-control custom-select'}),
        required=True
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=True,
        help_text='Por favor, describe tu experiencia y habilidades'
    )
    experience = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=True,
        help_text='Por favor, describe tu experiencia profesional'
    )
    files = MultipleFileField(
        required=True,
        widget=MultipleFileInput(attrs={'class': 'form-control'}),
        help_text='Sube tus documentos de soporte (máximo 10 archivos)'
    )
    password1 = forms.CharField(
        label='Contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'id': 'id_password1',
            'autocomplete': 'new-password',
        })
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña',
            'id': 'id_password2',
            'autocomplete': 'new-password',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'user_type', 'bio', 'experience', 'files']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields required
        for field in self.fields:
            self.fields[field].required = True

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'funding_goal', 'image']

class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = ['amount', 'equity_percentage']

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
        })
    )