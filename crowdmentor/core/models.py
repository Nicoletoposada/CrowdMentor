# core/models.py
from django.db import models # type: ignore
from django.contrib.auth.models import User # type: ignore
from django.utils import timezone # type: ignore

class Profile(models.Model):
    USER_TYPES = (
        ('entrepreneur', 'Emprendedor'),
        ('mentor', 'Mentor'),
        ('investor', 'Inversionista'),
        ('evaluator', 'Evaluador'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    bio = models.TextField()
    experience = models.TextField()
    is_approved = models.BooleanField(default=False)  # For mentors/evaluators
    is_approved_by_admin = models.BooleanField(default=False)  # Para evaluadores aprobados por el administrador

    def __str__(self):
        return f"{self.user.username} - {self.user_type}"

class UploadedFile(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='uploaded_files')
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.file.name} - {self.profile.user.username}"

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    funding_goal = models.DecimalField(max_digits=10, decimal_places=2)
    amount_raised = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Investment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='investments')
    investor = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    equity_percentage = models.FloatField()  # Percentage of project ownership
    invested_at = models.DateTimeField(default=timezone.now)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.investor.username} invested {self.amount} in {self.project.title}"

class Mentorship(models.Model):
    INITIATED_BY_CHOICES = [
        ('mentor', 'Mentor'),
        ('entrepreneur', 'Entrepreneur'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='mentorships')
    mentor = models.ForeignKey(User, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='pending'
    )
    initiated_by = models.CharField(
        max_length=20,
        choices=INITIATED_BY_CHOICES,
        default='mentor'
    )

    def __str__(self):
        return f"{self.mentor.username} mentoring {self.project.title} ({self.status})"

class Message(models.Model):
    mentorship = models.ForeignKey(Mentorship, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return self.sender.username

class ResourceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-folder')  # FontAwesome icon class
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Resource Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class Resource(models.Model):
    RESOURCE_TYPES = (
        ('document', 'Documento'),
        ('link', 'Enlace'),
        ('video', 'Video'),
        ('tool', 'Herramienta'),
        ('template', 'Plantilla'),
        ('guide', 'Guía'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    category = models.ForeignKey(ResourceCategory, on_delete=models.CASCADE, related_name='resources')
    
    # Para documentos/archivos
    file = models.FileField(upload_to='resources/files/', blank=True, null=True)
    
    # Para enlaces externos
    url = models.URLField(blank=True, null=True)
    
    # Metadatos
    icon = models.CharField(max_length=50, default='fas fa-file')  # FontAwesome icon class
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)  # Para destacar recursos importantes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.title

    def get_resource_url(self):
        """Retorna la URL del recurso (archivo o enlace externo)"""
        if self.file:
            return self.file.url
        return self.url or '#'