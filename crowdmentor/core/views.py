# core/views.py
from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib.auth import login, logout # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.contrib import messages # type: ignore
from django.conf import settings # type: ignore
from django.views import View # type: ignore
from .forms import CustomUserCreationForm, ProjectForm, InvestmentForm
from .models import Project, Investment, Mentorship, Profile

def home(request):
    projects = Project.objects.filter(is_active=True)
    return render(request, 'home.html', {'projects': projects})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            profile = Profile.objects.create(
                user=user,
                user_type=form.cleaned_data['user_type'],
                bio=form.cleaned_data['bio'],
                experience=form.cleaned_data['experience'],
                is_approved=form.cleaned_data['user_type'] in ['entrepreneur', 'investor']
            )

            # Manejar los archivos subidos
            files = request.FILES.getlist('files')
            if len(files) > 10:
                messages.error(request, 'No puedes subir más de 10 archivos.')
                return redirect('register')

            # Guardar los archivos en el sistema de archivos o base de datos según sea necesario
            for file in files:
                # Aquí puedes implementar la lógica para guardar los archivos
                pass

            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, 'No se encontró un perfil asociado a este usuario.')
        return redirect('home')

    if request.user.is_superuser:  # Verificar si el usuario es administrador
        return render(request, 'admin_dashboard.html', {'profile': profile})

    if profile.user_type == 'entrepreneur':
        projects = Project.objects.filter(owner=request.user)
        return render(request, 'dashboard.html', {'projects': projects, 'profile': profile})
    elif profile.user_type in ['mentor', 'investor']:
        mentorships = Mentorship.objects.filter(mentor=request.user)
        investments = Investment.objects.filter(investor=request.user)
        return render(request, 'dashboard.html', {'mentorships': mentorships, 'investments': investments, 'profile': profile})
    else:  # Evaluator
        pending_mentors = Profile.objects.filter(user_type='mentor', is_approved=False)
        return render(request, 'dashboard.html', {'pending_mentors': pending_mentors, 'profile': profile})

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            messages.success(request, 'Project created successfully!')
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'project_create.html', {'form': form})

def project_list(request):
    projects = Project.objects.filter(is_active=True)
    return render(request, 'project_list.html', {'projects': projects})

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST' and request.user.profile.user_type == 'investor':
        form = InvestmentForm(request.POST)
        if form.is_valid():
            investment = form.save(commit=False)
            investment.project = project
            investment.investor = request.user
            investment.save()
            project.amount_raised += investment.amount
            project.save()
            messages.success(request, 'Investment successful!')
            return redirect('project_detail', pk=project.pk)
    else:
        form = InvestmentForm()
    return render(request, 'project_detail.html', {'project': project, 'form': form})

@login_required
def approve_mentor(request, profile_id):
    if request.user.profile.user_type == 'evaluator':
        profile = get_object_or_404(Profile, pk=profile_id)
        profile.is_approved = True
        profile.save()
        messages.success(request, 'Mentor approved!')
    return redirect('dashboard')

class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('/')
