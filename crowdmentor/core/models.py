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

    # Campos adicionales de perfil
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    linkedin_url = models.URLField(max_length=200, blank=True)
    website_url = models.URLField(max_length=200, blank=True)

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
    PROJECT_STATUS = (
        ('draft', 'Borrador'),
        ('active', 'Activo'),
        ('funded', 'Financiado'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    category = models.ForeignKey('ProjectCategory', on_delete=models.SET_NULL, null=True, blank=True)
    funding_goal = models.DecimalField(max_digits=20, decimal_places=2)
    amount_raised = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=PROJECT_STATUS, default='active')
    
    # Nuevos campos para métricas
    views_count = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    deadline = models.DateField(blank=True, null=True)
    
    # Tags para búsqueda
    tags = models.CharField(max_length=500, blank=True, help_text="Separar con comas")

    # Tiempo estimado para inicio de rentabilidad
    PROFITABILITY_UNIT_CHOICES = (
        ('meses', 'Meses'),
        ('años', 'Años'),
    )
    profitability_time = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="Tiempo estimado para que el proyecto empiece a generar rentabilidad"
    )
    profitability_unit = models.CharField(
        max_length=10,
        choices=PROFITABILITY_UNIT_CHOICES,
        default='meses',
        blank=True
    )

    def __str__(self):
        return self.title

    def get_funding_percentage(self):
        """Calcula el porcentaje de financiamiento alcanzado"""
        if self.funding_goal > 0:
            return min((self.amount_raised / self.funding_goal) * 100, 100)
        return 0

    def get_average_rating(self):
        """Calcula el promedio de calificaciones"""
        ratings = self.ratings.all()
        if ratings:
            return sum(r.rating for r in ratings) / len(ratings)
        return 0

    def get_evaluation_score(self):
        """Calcula el puntaje promedio de evaluaciones"""
        evaluations = self.evaluations.all()
        if evaluations:
            return sum(e.overall_score for e in evaluations) / len(evaluations)
        return 0

    def is_deadline_approaching(self):
        """Verifica si la fecha límite está cerca (próximos 7 días)"""
        if self.deadline:
            from datetime import date, timedelta
            return self.deadline <= date.today() + timedelta(days=7)
        return False

class Investment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='investments')
    investor = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
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
        ('entrepreneur', 'Emprendedor'),
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
    
    # Tipos de mensaje
    MESSAGE_TYPES = (
        ('text', 'Mensaje de texto'),
        ('advice', 'Consejo/Asesoría'),
        ('feedback', 'Retroalimentación'),
        ('milestone', 'Hito del proyecto'),
        ('resource', 'Recurso compartido'),
        ('system', 'Mensaje del sistema'),
    )
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    
    # Metadatos
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)  # Para marcar mensajes importantes
    
    # Enlace opcional al proyecto de la mentoría
    related_resource = models.ForeignKey('Resource', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"

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

class ProjectCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-folder')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Project Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class EvaluationCriteria(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    weight = models.FloatField(default=1.0)  # Peso del criterio en la evaluación
    max_score = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Evaluation Criteria"
        ordering = ['name']

    def __str__(self):
        return self.name

class ProjectEvaluation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='evaluations')
    evaluator = models.ForeignKey(User, on_delete=models.CASCADE)
    overall_score = models.FloatField(default=0.0)
    comments = models.TextField(blank=True)
    is_recommended = models.BooleanField(default=False)
    evaluated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['project', 'evaluator']

    def __str__(self):
        return f"Evaluación de {self.project.title} por {self.evaluator.username}"

    def calculate_overall_score(self):
        """Calcula el puntaje general basado en los criterios evaluados"""
        criterion_scores = self.criterion_scores.all()
        if not criterion_scores:
            return 0.0
        
        total_weighted_score = 0
        total_weight = 0
        
        for cs in criterion_scores:
            weighted_score = cs.score * cs.criteria.weight
            total_weighted_score += weighted_score
            total_weight += cs.criteria.weight
        
        if total_weight == 0:
            return 0.0
        
        # Normalizar a escala de 0-10
        normalized_score = (total_weighted_score / total_weight)
        self.overall_score = round(normalized_score, 2)
        return self.overall_score

class CriterionScore(models.Model):
    evaluation = models.ForeignKey(ProjectEvaluation, on_delete=models.CASCADE, related_name='criterion_scores')
    criteria = models.ForeignKey(EvaluationCriteria, on_delete=models.CASCADE)
    score = models.FloatField()
    comments = models.TextField(blank=True)

    class Meta:
        unique_together = ['evaluation', 'criteria']

    def __str__(self):
        return f"{self.criteria.name}: {self.score}"

class ProjectRating(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['project', 'user']

    def __str__(self):
        return f"{self.project.title} - {self.rating} estrellas"

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('investment', 'Nueva Inversión'),
        ('mentorship', 'Solicitud de Mentoría'),
        ('evaluation', 'Nueva Evaluación'),
        ('message', 'Nuevo Mensaje'),
        ('project_update', 'Actualización de Proyecto'),
        ('system', 'Notificación del Sistema'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Enlaces opcionales
    related_project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True)
    related_investment = models.ForeignKey(Investment, on_delete=models.CASCADE, blank=True, null=True)
    related_mentorship = models.ForeignKey(Mentorship, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"

class MentorInvestorConnection(models.Model):
    CONNECTION_STATUS = (
        ('pending', 'Pendiente'),
        ('accepted', 'Aceptada'),
        ('rejected', 'Rechazada'),
        ('blocked', 'Bloqueada'),
    )
    
    INITIATED_BY_CHOICES = [
        ('mentor', 'Mentor'),
        ('investor', 'Inversionista'),
    ]

    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentor_connections')
    investor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investor_connections')
    initiated_by = models.CharField(max_length=20, choices=INITIATED_BY_CHOICES)
    status = models.CharField(max_length=20, choices=CONNECTION_STATUS, default='pending')
    
    # Información adicional de la conexión
    purpose = models.TextField(help_text="Propósito o motivo de la conexión")
    expertise_areas = models.CharField(max_length=500, blank=True, help_text="Áreas de expertise relevantes")
    investment_interests = models.CharField(max_length=500, blank=True, help_text="Intereses de inversión")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    connected_at = models.DateTimeField(null=True, blank=True)  # Cuando se acepta la conexión
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['mentor', 'investor']
        ordering = ['-created_at']

    def __str__(self):
        return f"Conexión: {self.mentor.username} - {self.investor.username} ({self.status})"

    def get_other_user(self, current_user):
        """Retorna el otro usuario en la conexión"""
        if current_user == self.mentor:
            return self.investor
        return self.mentor

    def is_active(self):
        """Verifica si la conexión está activa"""
        return self.status == 'accepted'

class MentorInvestorMessage(models.Model):
    connection = models.ForeignKey(MentorInvestorConnection, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    
    # Tipos de mensaje
    MESSAGE_TYPES = (
        ('text', 'Mensaje de texto'),
        ('opportunity', 'Oportunidad de inversión'),
        ('collaboration', 'Propuesta de colaboración'),
        ('knowledge_share', 'Intercambio de conocimientos'),
        ('system', 'Mensaje del sistema'),
    )
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    
    # Metadatos
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)  # Para marcar mensajes importantes
    
    # Enlaces opcionales a proyectos o inversiones
    related_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    related_investment = models.ForeignKey(Investment, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username} -> {self.connection.get_other_user(self.sender).username}: {self.content[:50]}..."


# ─────────────────────────────────────────────────────────────
# Asistente IA para estructuración de proyectos (PMI)
# ─────────────────────────────────────────────────────────────
class AIProjectSession(models.Model):
    """Almacena la sesión de conversación con el asistente de IA PMI."""
    STATUS_CHOICES = [
        ('active', 'Activa'),
        ('completed', 'Completada'),
        ('abandoned', 'Abandonada'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_project_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Historial completo de mensajes en JSON: [{role, content, timestamp}]
    messages = models.JSONField(default=list)

    # Datos estructurados extraídos por la IA al finalizar
    generated_title = models.CharField(max_length=200, blank=True)
    generated_description = models.TextField(blank=True)
    generated_tags = models.CharField(max_length=500, blank=True)
    generated_funding_goal = models.CharField(max_length=50, blank=True)
    generated_profitability_time = models.CharField(max_length=20, blank=True)
    generated_profitability_unit = models.CharField(max_length=10, blank=True, default='meses')

    # Proyecto creado a partir de esta sesión (puede ser None)
    resulting_project = models.ForeignKey(
        'Project', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='ai_session'
    )

    # Fase actual del proceso PMI guiado
    PMI_PHASES = [
        ('welcome', 'Bienvenida'),
        ('ideation', 'Ideación'),
        ('problem', 'Problema y Solución'),
        ('market', 'Mercado Objetivo'),
        ('business_model', 'Modelo de Negocio'),
        ('resources', 'Recursos y Presupuesto'),
        ('risks', 'Riesgos'),
        ('timeline', 'Cronograma'),
        ('summary', 'Resumen Generado'),
    ]
    current_phase = models.CharField(max_length=20, default='welcome')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Sesión IA de {self.user.username} – {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    def add_message(self, role: str, content: str):
        """Agrega un mensaje al historial."""
        from django.utils import timezone as tz
        msgs = list(self.messages)
        msgs.append({'role': role, 'content': content, 'timestamp': tz.now().isoformat()})
        self.messages = msgs
        self.save(update_fields=['messages', 'updated_at'])

    def get_last_n_messages(self, n: int = 20):
        """Devuelve los últimos N mensajes para contexto."""
        return self.messages[-n:] if len(self.messages) > n else self.messages


class InvestmentContract(models.Model):
    """Contrato de inversión generado cuando el emprendedor acepta una inversión."""
    CONTRACT_STATUS = [
        ('generated', 'Generado'),
        ('signed_uploaded', 'Firmado y Subido'),
    ]

    investment = models.OneToOneField(
        Investment, on_delete=models.CASCADE, related_name='contract'
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=CONTRACT_STATUS, default='generated')

    # Archivo del contrato firmado (subido por el inversionista)
    signed_document = models.FileField(
        upload_to='contracts/signed/%Y/%m/',
        blank=True, null=True,
        help_text='Documento firmado subido por el inversionista'
    )
    signed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Contrato – {self.investment.investor.username} / {self.investment.project.title}"