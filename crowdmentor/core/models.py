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
    bio = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)  # For mentors/evaluators

    def __str__(self):
        return f"{self.user.username} - {self.user_type}"

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
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='mentorships')
    mentor = models.ForeignKey(User, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=(('active', 'Active'), ('completed', 'Completed')), default='active')

    def __str__(self):
        return f"{self.mentor.username} mentoring {self.project.title}"