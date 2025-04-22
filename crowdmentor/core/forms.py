# core/forms.py
from django import forms # type: ignore
from django.contrib.auth.forms import UserCreationForm # type: ignore
from django.contrib.auth.models import User # type: ignore
from .models import Profile, Project, Investment

class CustomUserCreationForm(UserCreationForm):
    user_type = forms.ChoiceField(
        choices=Profile.USER_TYPES,
        widget=forms.Select(attrs={'class': 'form-control custom-select'})
    )
    bio = forms.CharField(widget=forms.Textarea, required=False)
    experience = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'user_type', 'bio', 'experience']

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'funding_goal', 'image']

class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = ['amount', 'equity_percentage']