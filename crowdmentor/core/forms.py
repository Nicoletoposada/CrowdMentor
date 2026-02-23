# core/forms.py
from django import forms # type: ignore
from django.contrib.auth.forms import UserCreationForm # type: ignore
from django.contrib.auth.models import User # type: ignore
from .models import Profile, Project, Investment, Resource, ResourceCategory, ProjectCategory, ProjectEvaluation, EvaluationCriteria, CriterionScore, ProjectRating, MentorInvestorConnection, MentorInvestorMessage, Message

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
        fields = ['title', 'description', 'category', 'funding_goal', 'deadline', 'tags', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del proyecto'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe tu proyecto en detalle'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'funding_goal': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Meta de financiamiento en COP',
                'min': '100000'
            }),
            'deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'tecnología, startup, innovación (separar con comas)'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }

class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = ['amount', 'equity_percentage']
        labels = {
            'amount': 'Monto de Inversión',
            'equity_percentage': 'Porcentaje de Participación',
        }
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Monto en COP',
                'min': '100000',
                'step': '1000'
            }),
            'equity_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Porcentaje (0-100)',
                'min': '0.1',
                'max': '100',
                'step': '0.1'
            })
        }
        help_texts = {
            'amount': 'Ingresa el monto que deseas invertir en pesos colombianos (mínimo $100,000 COP)',
            'equity_percentage': 'Porcentaje de participación que solicitas en el proyecto'
        }

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

class ResourceCategoryForm(forms.ModelForm):
    class Meta:
        model = ResourceCategory
        fields = ['name', 'description', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la categoría'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la categoría'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Clase de icono (ej: fas fa-book)',
                'value': 'fas fa-folder'
            })
        }

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'description', 'resource_type', 'category', 'file', 'url', 'icon', 'is_featured']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del recurso'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción detallada del recurso'
            }),
            'resource_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://ejemplo.com'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Clase de icono (ej: fas fa-file-pdf)',
                'value': 'fas fa-file'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar ayuda para los campos
        self.fields['file'].help_text = 'Sube un archivo si es un documento o plantilla'
        self.fields['url'].help_text = 'Ingresa una URL si es un enlace externo'
        self.fields['icon'].help_text = 'Clase de FontAwesome para el icono'
        self.fields['is_featured'].help_text = 'Marcar para destacar este recurso'

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        url = cleaned_data.get('url')
        resource_type = cleaned_data.get('resource_type')

        # Validar que al menos uno de file o url esté presente
        if not file and not url:
            raise forms.ValidationError('Debes proporcionar un archivo o una URL.')

        # Si es un enlace o herramienta, debe tener URL
        if resource_type in ['link', 'tool'] and not url:
            raise forms.ValidationError(f'Para el tipo "{resource_type}" es obligatorio proporcionar una URL.')

        return cleaned_data

class ProjectSearchForm(forms.Form):
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar proyectos...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=ProjectCategory.objects.all(),
        required=False,
        empty_label='Todas las categorías',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    min_funding = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Financiamiento mínimo'
        })
    )
    max_funding = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Financiamiento máximo'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + list(Project.PROJECT_STATUS),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('created_at', 'Más recientes'),
            ('-created_at', 'Más antiguos'),
            ('funding_goal', 'Menor financiamiento'),
            ('-funding_goal', 'Mayor financiamiento'),
            ('-views_count', 'Más vistos'),
            ('-likes_count', 'Más populares'),
        ],
        required=False,
        initial='-created_at',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

class ProjectEvaluationForm(forms.ModelForm):
    class Meta:
        model = ProjectEvaluation
        fields = ['comments', 'is_recommended']
        widgets = {
            'comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Comentarios generales sobre el proyecto'
            }),
            'is_recommended': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class CriterionScoreForm(forms.ModelForm):
    class Meta:
        model = CriterionScore
        fields = ['score', 'comments']
        widgets = {
            'score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '10',
                'step': '0.1'
            }),
            'comments': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Comentarios sobre este criterio'
            })
        }

class ProjectRatingForm(forms.ModelForm):
    class Meta:
        model = ProjectRating
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f"{i} estrella{'s' if i > 1 else ''}") for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Comparte tu opinión sobre este proyecto'
            })
        }

class ProjectCategoryForm(forms.ModelForm):
    class Meta:
        model = ProjectCategory
        fields = ['name', 'description', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la categoría'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la categoría'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Clase de icono (ej: fas fa-lightbulb)',
                'value': 'fas fa-folder'
            })
        }

class MentorInvestorConnectionForm(forms.ModelForm):
    class Meta:
        model = MentorInvestorConnection
        fields = ['purpose', 'expertise_areas', 'investment_interests']
        widgets = {
            'purpose': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe el propósito de esta conexión y cómo podríais colaborar...'
            }),
            'expertise_areas': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: tecnología, marketing digital, finanzas corporativas'
            }),
            'investment_interests': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: startups tecnológicas, proyectos sostenibles, innovación'
            })
        }
        labels = {
            'purpose': 'Propósito de la conexión',
            'expertise_areas': 'Áreas de expertise',
            'investment_interests': 'Intereses de inversión'
        }
        help_texts = {
            'purpose': 'Explica por qué quieres conectarte y cómo pueden colaborar',
            'expertise_areas': 'Menciona las áreas de expertise relevantes para la colaboración',
            'investment_interests': 'Especifica los tipos de proyectos o sectores de interés'
        }

class MentorInvestorMessageForm(forms.ModelForm):
    class Meta:
        model = MentorInvestorMessage
        fields = ['content', 'message_type', 'is_important', 'related_project']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Escribe tu mensaje...'
            }),
            'message_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_important': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'related_project': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'content': 'Mensaje',
            'message_type': 'Tipo de mensaje',
            'is_important': 'Marcar como importante',
            'related_project': 'Proyecto relacionado (opcional)'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar proyectos según el tipo de usuario
        if user:
            if hasattr(user, 'profile'):
                if user.profile.user_type == 'entrepreneur':
                    # Si es emprendedor, mostrar sus proyectos
                    self.fields['related_project'].queryset = Project.objects.filter(owner=user, is_active=True)
                elif user.profile.user_type == 'investor':
                    # Si es inversionista, mostrar proyectos en los que ha invertido
                    invested_projects = Investment.objects.filter(investor=user, status='accepted').values_list('project', flat=True)
                    self.fields['related_project'].queryset = Project.objects.filter(id__in=invested_projects)
                else:
                    # Para otros tipos de usuario, mostrar todos los proyectos activos
                    self.fields['related_project'].queryset = Project.objects.filter(is_active=True)
            else:
                self.fields['related_project'].queryset = Project.objects.filter(is_active=True)
        
        # Hacer el campo opcional
        self.fields['related_project'].required = False
        self.fields['related_project'].empty_label = 'Ningún proyecto específico'

class ConnectionSearchForm(forms.Form):
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre, expertise, intereses...'
        })
    )
    expertise_area = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Área de expertise'
        })
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('-last_activity', 'Actividad reciente'),
            ('mentor__username', 'Nombre del mentor'),
            ('investor__username', 'Nombre del inversionista'),
            ('-created_at', 'Conexiones más recientes'),
            ('created_at', 'Conexiones más antiguas'),
        ],
        required=False,
        initial='-last_activity',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

class MentorshipMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'message_type', 'is_important', 'related_resource']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Escribe tu mensaje...'
            }),
            'message_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_important': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'related_resource': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'content': 'Mensaje',
            'message_type': 'Tipo de mensaje',
            'is_important': 'Marcar como importante',
            'related_resource': 'Recurso relacionado (opcional)'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Mostrar recursos disponibles (activos y destacados primero)
        self.fields['related_resource'].queryset = Resource.objects.filter(is_active=True).order_by('-is_featured', 'title')
        
        # Hacer el campo opcional
        self.fields['related_resource'].required = False
        self.fields['related_resource'].empty_label = 'Ningún recurso específico'