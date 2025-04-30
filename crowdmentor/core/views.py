# core/views.py
from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib.auth import login, logout # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.contrib import messages # type: ignore
from django.conf import settings # type: ignore
from django.views import View # type: ignore
from django.contrib.auth.models import User # type: ignore
from django.http import JsonResponse # type: ignore
from .forms import CustomUserCreationForm, ProjectForm, InvestmentForm
from .models import Project, Investment, Mentorship, Profile
from django.views.decorators.http import require_POST # type: ignore
from django.core.files.storage import default_storage # type: ignore
from django.core.files.base import ContentFile # type: ignore

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

    if profile.user_type == 'evaluator' and not profile.is_approved_by_admin:
        messages.error(request, 'Tu cuenta aún no ha sido aprobada por el Administrador.')
        return redirect('home')

    if profile.user_type == 'mentor' and not profile.is_approved:
        messages.error(request, 'Tu cuenta aún no ha sido aprobada por un Evaluador.')
        return redirect('home')

    if request.user.is_superuser:  # Verificar si el usuario es administrador
        return render(request, 'admin_dashboard.html', {'profile': profile})

    if profile.user_type == 'entrepreneur':
        projects = Project.objects.filter(owner=request.user)
        investments = Investment.objects.filter(project__owner=request.user, status='pending')
        return render(request, 'dashboard.html', {'projects': projects, 'investments': investments, 'profile': profile})
    elif profile.user_type in ['mentor', 'investor']:
        if profile.user_type == 'mentor' and not profile.is_approved:
            messages.error(request, 'Tu cuenta aún no ha sido aprobada por un Evaluador.')
            return redirect('home')
        mentorships = Mentorship.objects.filter(mentor=request.user)
        investments = Investment.objects.filter(investor=request.user)
        return render(request, 'dashboard.html', {'mentorships': mentorships, 'investments': investments, 'profile': profile})
    else:  # Evaluator
        pending_mentors = Profile.objects.filter(user_type='mentor', is_approved=False)
        return render(request, 'dashboard.html', {'pending_mentors': pending_mentors, 'profile': profile})

@login_required
def project_create(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para crear un proyecto.')
        return redirect('login')

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            messages.success(request, '¡Proyecto creado exitosamente!')
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
            investment.status = 'pending'  # Estado inicial de la inversión
            investment.save()
            messages.success(request, 'Tu inversión está pendiente de aprobación por el emprendedor.')
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

@login_required
def approve_evaluator(request, profile_id):
    if not request.user.is_superuser:
        messages.error(request, 'Acceso denegado. Solo los administradores pueden realizar esta acción.')
        return redirect('home')

    profile = get_object_or_404(Profile, pk=profile_id, user_type='evaluator')
    profile.is_approved_by_admin = True
    profile.save()
    messages.success(request, 'Evaluador aprobado exitosamente.')
    return redirect('admin_dashboard')

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, 'Acceso denegado. Solo los administradores pueden acceder a esta página.')
        return redirect('home')

    users = User.objects.all()
    projects = Project.objects.all()
    investments = Investment.objects.all()
    profiles_pending_approval = Profile.objects.filter(user_type='evaluator', is_approved_by_admin=False)

    evaluators_with_files = []
    for evaluator in profiles_pending_approval:
        uploaded_files = []
        if hasattr(evaluator, 'uploaded_files'):
            uploaded_files = [default_storage.url(file.file.name) for file in evaluator.uploaded_files.all()]
        evaluators_with_files.append({
            'evaluator': evaluator,
            'files': uploaded_files
        })

    return render(request, 'admin_dashboard.html', {
        'users': users,
        'projects': projects,
        'investments': investments,
        'profiles_pending_approval': evaluators_with_files
    })

@login_required
def delete_user(request, user_id):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Acceso denegado'}, status=403)

    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return JsonResponse({'success': 'Usuario eliminado correctamente'})
    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

@login_required
def delete_project(request, project_id):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Acceso denegado'}, status=403)

    try:
        project = Project.objects.get(id=project_id)
        project.delete()
        return JsonResponse({'success': 'Proyecto eliminado correctamente'})
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Proyecto no encontrado'}, status=404)

@login_required
@require_POST
def manage_investment(request, investment_id):
    investment = get_object_or_404(Investment, id=investment_id, project__owner=request.user)
    action = request.POST.get('action')

    if action == 'accept':
        investment.status = 'accepted'
        investment.is_accepted = True
        investment.save()

        # Sumar el monto de la inversión al proyecto
        project = investment.project
        project.amount_raised += investment.amount
        project.save()

        messages.success(request, 'Has aceptado la inversión. El monto ha sido sumado al proyecto.')
    elif action == 'reject':
        investment.status = 'rejected'
        investment.save()

        messages.success(request, 'Has rechazado la inversión. El dinero será reembolsado al inversionista.')
    else:
        messages.error(request, 'Acción no válida.')

    return redirect('dashboard')

class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('/')