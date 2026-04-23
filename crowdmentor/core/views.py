# core/views.py
from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib.auth import login, logout, authenticate # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.contrib import messages # type: ignore
from django.conf import settings # type: ignore
from django.views import View # type: ignore
from django.contrib.auth.models import User, Group # type: ignore
from django.http import JsonResponse, HttpResponse # type: ignore
from .forms import CustomUserCreationForm, ProjectForm, InvestmentForm, LoginForm, ResourceForm, ResourceCategoryForm, ProjectSearchForm, ProjectEvaluationForm, CriterionScoreForm, ProjectRatingForm, ProjectCategoryForm, MentorInvestorConnectionForm, MentorInvestorMessageForm, ConnectionSearchForm, MentorshipMessageForm, UserEditForm, ProfileEditForm, PasswordChangeCustomForm
from .models import Project, Investment, Mentorship, Profile, Message, UploadedFile, Resource, ResourceCategory, ProjectCategory, ProjectEvaluation, EvaluationCriteria, CriterionScore, ProjectRating, Notification, MentorInvestorConnection, MentorInvestorMessage, AIProjectSession, InvestmentContract
from django.db.models import Q, Avg, Count, Sum # type: ignore
from django.views.decorators.http import require_POST # type: ignore
from django.core.files.storage import default_storage # type: ignore
from django.core.files.base import ContentFile # type: ignore
from decimal import Decimal, ROUND_HALF_UP
from urllib import request as urllib_request
from urllib.error import URLError, HTTPError
import json
import socket
import os

from django.utils import timezone # type: ignore

def resources(request):
    """Vista para mostrar la página de recursos para emprendedores."""
    categories = ResourceCategory.objects.all()
    resources_by_category = {}
    
    for category in categories:
        resources_by_category[category] = Resource.objects.filter(
            category=category, 
            is_active=True
        ).order_by('-is_featured', '-created_at')[:10]  # Máximo 10 recursos por categoría
    
    return render(request, 'resources.html', {
        'categories': categories,
        'resources_by_category': resources_by_category
    })

def home(request):
    projects = Project.objects.filter(is_active=True)

    # Ranking de impacto con datos ficticios (siempre con nombres), 100 pts por proyecto.
    entrepreneur_seed = [
        ('Valentina Rojas', 5),
        ('Santiago Mejia', 4),
        ('Camila Torres', 3),
        ('Andres Salazar', 2),
        ('Laura Cardenas', 1),
    ]
    mentor_seed = [
        ('Juan Pablo Diaz', 5),
        ('Manuela Restrepo', 4),
        ('Felipe Arango', 3),
        ('Natalia Giraldo', 2),
        ('David Quintero', 1),
    ]

    entrepreneur_ranking = [
        {
            'name': name,
            'funded_projects': projects_count,
            'points': projects_count * 100,
        }
        for name, projects_count in entrepreneur_seed
    ]

    mentor_ranking = [
        {
            'name': name,
            'funded_projects': projects_count,
            'points': projects_count * 100,
        }
        for name, projects_count in mentor_seed
    ]

    entrepreneur_ranking = sorted(entrepreneur_ranking, key=lambda item: item['points'], reverse=True)
    mentor_ranking = sorted(mentor_ranking, key=lambda item: item['points'], reverse=True)

    return render(request, 'home.html', {
        'projects': projects,
        'entrepreneur_ranking': entrepreneur_ranking,
        'mentor_ranking': mentor_ranking,
    })

def ensure_project_categories():
    if ProjectCategory.objects.exists():
        return

    categories = [
        {
            'name': 'Tecnologia',
            'description': 'Proyectos relacionados con software, hardware, apps, etc.',
            'icon': 'fas fa-laptop-code'
        },
        {
            'name': 'Sostenibilidad',
            'description': 'Proyectos enfocados en el medio ambiente y sostenibilidad',
            'icon': 'fas fa-leaf'
        },
        {
            'name': 'Salud',
            'description': 'Proyectos relacionados con la salud y bienestar',
            'icon': 'fas fa-heartbeat'
        },
        {
            'name': 'Educacion',
            'description': 'Proyectos educativos e innovacion en aprendizaje',
            'icon': 'fas fa-graduation-cap'
        },
        {
            'name': 'Fintech',
            'description': 'Tecnologia financiera y servicios financieros',
            'icon': 'fas fa-credit-card'
        },
        {
            'name': 'E-commerce',
            'description': 'Comercio electronico y marketplaces',
            'icon': 'fas fa-shopping-cart'
        },
        {
            'name': 'Impacto social',
            'description': 'Proyectos con impacto social positivo',
            'icon': 'fas fa-hands-helping'
        }
    ]

    for cat_data in categories:
        ProjectCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'description': cat_data['description'],
                'icon': cat_data['icon']
            }
        )

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            user_type = form.cleaned_data['user_type']
            profile = Profile.objects.create(
                user=user,
                user_type=user_type,
                bio=form.cleaned_data['bio'],
                experience=form.cleaned_data['experience'],
                is_approved=user_type in ['entrepreneur', 'investor'],
                mentor_specialty=form.cleaned_data.get('mentor_specialty') if user_type == 'mentor' else None
            )

            # Handle multiple file uploads
            files = request.FILES.getlist('files')
            if len(files) > 10:
                messages.error(request, 'No puedes subir más de 10 archivos.')
                user.delete()  # Eliminar el usuario si hay error
                return redirect('register')

            for file in files:
                UploadedFile.objects.create(
                    profile=profile,
                    file=file
                )
            
            # Crear notificaciones para aprobaciones pendientes
            if user_type == 'mentor':
                # Notificar a todos los evaluadores
                evaluators = User.objects.filter(profile__user_type='evaluator', profile__is_approved_by_admin=True)
                for evaluator in evaluators:
                    Notification.objects.create(
                        user=evaluator,
                        title='Nueva solicitud de mentor',
                        message=f'{user.username} ha solicitado ser mentor y necesita aprobación.',
                        notification_type='system'
                    )
            elif user_type == 'evaluator':
                # Notificar a todos los administradores
                admins = User.objects.filter(is_superuser=True)
                for admin in admins:
                    Notification.objects.create(
                        user=admin,
                        title='Nueva solicitud de evaluador',
                        message=f'{user.username} ha solicitado ser evaluador y necesita aprobación.',
                        notification_type='system'
                    )

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
        accepted_mentorships = Mentorship.objects.filter(
            project__owner=request.user,
            status='accepted'
        )
        pending_mentorships = Mentorship.objects.filter(
            project__owner=request.user,
            status='pending'
        )
        unread_mentorship_messages = 0
        for mentorship in accepted_mentorships:
            unread_mentorship_messages += mentorship.messages.filter(
                is_read=False
            ).exclude(sender=request.user).count()
        total_active_chats = accepted_mentorships.count()
        return render(request, 'dashboard.html', {
            'projects': projects,
            'investments': investments,
            'profile': profile,
            'mentorships': accepted_mentorships,
            'pending_mentorships': pending_mentorships,
            'unread_mentorship_messages': unread_mentorship_messages,
            'total_active_chats': total_active_chats,
        })
    elif profile.user_type in ['mentor', 'investor']:
        if profile.user_type == 'mentor' and not profile.is_approved:
            messages.error(request, 'Tu cuenta aún no ha sido aprobada por un Evaluador.')
            return redirect('home')
        mentorships = Mentorship.objects.filter(mentor=request.user)
        pending_mentorships = mentorships.filter(status='pending')
        investments = Investment.objects.filter(investor=request.user)
        
        # Datos para conexiones mentor-inversionista
        if profile.user_type == 'mentor':
            connections = MentorInvestorConnection.objects.filter(mentor=request.user, status='accepted')
            pending_connections = MentorInvestorConnection.objects.filter(mentor=request.user, status='pending')
        else:
            connections = MentorInvestorConnection.objects.filter(investor=request.user, status='accepted')
            pending_connections = MentorInvestorConnection.objects.filter(investor=request.user, status='pending')
        
        # Contar mensajes no leídos en conexiones
        unread_connections_messages = 0
        for connection in connections:
            unread_connections_messages += connection.messages.filter(
                is_read=False
            ).exclude(sender=request.user).count()

        active_mentorships = mentorships.filter(status='accepted')

        # Incluir mensajes no leídos de mentorías para mentores
        if profile.user_type == 'mentor':
            for mentorship in active_mentorships:
                unread_connections_messages += mentorship.messages.filter(
                    is_read=False
                ).exclude(sender=request.user).count()

        total_active_chats = connections.count() + active_mentorships.count()
        
        return render(request, 'dashboard.html', {
            'mentorships': mentorships,
            'pending_mentorships': pending_mentorships,
            'investments': investments,
            'profile': profile,
            'connections': connections,
            'pending_connections': pending_connections,
            'unread_connections_messages': unread_connections_messages,
            'total_active_chats': total_active_chats,
        })
    else:  # Evaluator
        pending_mentors = Profile.objects.filter(user_type='mentor', is_approved=False)
        mentor_files = []
        for mentor in pending_mentors:
            files = UploadedFile.objects.filter(profile=mentor)
            mentor_files.append({
                'mentor': mentor,
                'files': files
            })
        return render(request, 'dashboard.html', {
            'pending_mentors': pending_mentors,
            'mentor_files': mentor_files,
            'profile': profile
        })

@login_required
def project_create(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Debes iniciar sesión para crear un proyecto.')
        return redirect('login')

    ensure_project_categories()

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()

            # Vincular sesión IA si viene de ella
            ai_session_id = request.POST.get('ai_session')
            if ai_session_id:
                try:
                    ai_session = AIProjectSession.objects.get(pk=ai_session_id, user=request.user)
                    ai_session.resulting_project = project
                    ai_session.status = 'completed'
                    ai_session.save(update_fields=['resulting_project', 'status'])
                except AIProjectSession.DoesNotExist:
                    pass
            
            # Crear notificación para administradores
            from django.contrib.auth.models import User
            admins = User.objects.filter(is_superuser=True)
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    title='Nuevo proyecto creado',
                    message=f'{request.user.username} ha creado el proyecto "{project.title}".',
                    notification_type='project_update',
                    related_project=project
                )
            
            messages.success(request, '¡Proyecto creado exitosamente!')
            return redirect('project_detail', pk=project.pk)
    else:
        # Pre-llenar con datos del asistente IA (vienen por GET)
        ai_session_id = request.GET.get('ai_session', '')
        initial = {}
        if ai_session_id:
            initial = {
                'title': request.GET.get('title', ''),
                'description': request.GET.get('description', ''),
                'tags': request.GET.get('tags', ''),
                'funding_goal': request.GET.get('funding_goal', '') or None,
                'profitability_time': request.GET.get('profitability_time', '') or None,
                'profitability_unit': request.GET.get('profitability_unit', 'meses'),
            }
        form = ProjectForm(initial=initial)
    
    context = {
        'form': form,
        'categories': ProjectCategory.objects.all(),
        'ai_session_id': request.GET.get('ai_session', '') or request.POST.get('ai_session', ''),
        'from_ai': bool(request.GET.get('ai_session', '')),
    }
    return render(request, 'project_create.html', context)

def project_list(request):
    ensure_project_categories()
    form = ProjectSearchForm(request.GET or None)
    projects = Project.objects.filter(is_active=True)
    
    if form.is_valid():
        # Búsqueda por texto
        search = form.cleaned_data.get('search')
        if search:
            projects = projects.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) | 
                Q(tags__icontains=search)
            )
        
        # Filtro por categoría
        category = form.cleaned_data.get('category')
        if category:
            projects = projects.filter(category=category)
        
        # Filtro por rango de financiamiento
        min_funding = form.cleaned_data.get('min_funding')
        if min_funding:
            projects = projects.filter(funding_goal__gte=min_funding)
        
        max_funding = form.cleaned_data.get('max_funding')
        if max_funding:
            projects = projects.filter(funding_goal__lte=max_funding)
        
        # Filtro por estado
        status = form.cleaned_data.get('status')
        if status:
            projects = projects.filter(status=status)
        
        # Ordenamiento
        sort_by = form.cleaned_data.get('sort_by', '-created_at')
        projects = projects.order_by(sort_by)
    else:
        projects = projects.order_by('-created_at')
    
    # Agregar datos de evaluación y rating
    projects = projects.annotate(
        avg_rating=Avg('ratings__rating'),
        rating_count=Count('ratings')
    )
    
    context = {
        'projects': projects,
        'form': form,
        'categories': ProjectCategory.objects.all()
    }
    
    return render(request, 'project_list.html', context)

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # Incrementar contador de vistas
    project.views_count += 1
    project.save()
    
    # Formularios
    investment_form = InvestmentForm(project=project)
    rating_form = ProjectRatingForm()
    
    # Obtener rating del usuario actual si existe
    user_rating = None
    if request.user.is_authenticated:
        try:
            user_rating = ProjectRating.objects.get(project=project, user=request.user)
        except ProjectRating.DoesNotExist:
            pass
    
    if request.method == 'POST':
        # Verificar que el usuario tenga perfil antes de procesar cualquier acción
        if not hasattr(request.user, 'profile'):
            messages.error(request, 'Tu cuenta no tiene un perfil asociado. Contacta al administrador.')
            return redirect('project_detail', pk=project.pk)
            
        if request.user.profile.user_type == 'investor' and 'invest' in request.POST:
            # Verificar que el proyecto no esté financiado o completado
            if project.status in ('funded', 'completed'):
                messages.error(request, 'Este proyecto ya alcanzó su meta de financiación y no acepta más inversiones.')
                return redirect('project_detail', pk=project.pk)

            investment_form = InvestmentForm(request.POST, project=project)
            if investment_form.is_valid():
                # Verificar que el usuario no sea el dueño del proyecto
                if request.user == project.owner:
                    messages.error(request, 'No puedes invertir en tu propio proyecto.')
                    return redirect('project_detail', pk=project.pk)
                
                # Verificar si ya existe una inversión pendiente o aceptada
                existing_investment = Investment.objects.filter(
                    project=project,
                    investor=request.user,
                    status__in=['pending', 'accepted']
                ).first()
                
                if existing_investment:
                    messages.warning(request, 'Ya tienes una inversión pendiente o activa en este proyecto.')
                    return redirect('project_detail', pk=project.pk)

                # Segunda barrera para evitar sobrepasar la meta por concurrencia.
                current_total = Investment.objects.filter(
                    project=project,
                    status__in=['pending', 'accepted']
                ).aggregate(total=Sum('amount'))['total'] or 0
                remaining = project.funding_goal - current_total
                if investment_form.cleaned_data['amount'] > remaining:
                    messages.error(
                        request,
                        f'La inversión supera el cupo disponible. Máximo permitido actualmente: {remaining:,.0f} COP.'
                    )
                    return redirect('project_detail', pk=project.pk)
                
                investment = investment_form.save(commit=False)
                investment.project = project
                investment.investor = request.user
                investment.status = 'pending'
                investment.save()
                
                # Crear notificación para el emprendedor
                Notification.objects.create(
                    user=project.owner,
                    title='Nueva propuesta de inversión',
                    message=f'{request.user.username} ha propuesto invertir ${investment.amount:,.0f} COP en tu proyecto "{project.title}".',
                    notification_type='investment',
                    related_project=project,
                    related_investment=investment
                )
                
                messages.success(request, 'Tu inversión está pendiente de aprobación por el emprendedor.')
                return redirect('project_detail', pk=project.pk)
            else:
                messages.error(request, 'Por favor, corrige los errores en el formulario de inversión.')
        
        elif 'rate' in request.POST and request.user.is_authenticated:
            rating_form = ProjectRatingForm(request.POST)
            if rating_form.is_valid():
                rating, created = ProjectRating.objects.get_or_create(
                    project=project,
                    user=request.user,
                    defaults={
                        'rating': rating_form.cleaned_data['rating'],
                        'comment': rating_form.cleaned_data['comment']
                    }
                )
                if not created:
                    rating.rating = rating_form.cleaned_data['rating']
                    rating.comment = rating_form.cleaned_data['comment']
                    rating.save()
                
                messages.success(request, 'Tu calificación ha sido registrada.')
                return redirect('project_detail', pk=project.pk)
    
    # Obtener estadísticas del proyecto
    ratings = project.ratings.all()
    avg_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0
    evaluations = project.evaluations.all()
    avg_evaluation = evaluations.aggregate(Avg('overall_score'))['overall_score__avg'] or 0

    # Participantes del proyecto (para proyectos financiados/completados)
    accepted_mentors = Mentorship.objects.filter(project=project, status='accepted').select_related('mentor__profile')
    accepted_investors = Investment.objects.filter(project=project, status='accepted').select_related('investor__profile')

    context = {
        'project': project,
        'investment_form': investment_form,
        'rating_form': rating_form,
        'user_rating': user_rating,
        'ratings': ratings[:5],  # Mostrar solo las primeras 5
        'avg_rating': avg_rating,
        'rating_count': ratings.count(),
        'evaluations': evaluations,
        'avg_evaluation': avg_evaluation,
        'funding_percentage': project.get_funding_percentage(),
        'accepted_mentors': accepted_mentors,
        'accepted_investors': accepted_investors,
    }
    
    return render(request, 'project_detail.html', context)

@login_required
def approve_mentor(request, profile_id):
    if request.user.profile.user_type == 'evaluator':
        profile = get_object_or_404(Profile, pk=profile_id)
        profile.is_approved = True
        profile.save()
        
        # Crear notificación para el mentor aprobado
        Notification.objects.create(
            user=profile.user,
            title='¡Tu cuenta ha sido aprobada!',
            message='Felicidades, tu solicitud de mentor ha sido aprobada. Ya puedes ofrecer mentorías.',
            notification_type='system'
        )
        
        messages.success(request, 'Mentor approved!')
    return redirect('dashboard')

@login_required
def approve_evaluator(request, user_id):
    if not request.user.is_staff:
        return JsonResponse({'success': False})
    
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            profile = user.profile
            
            # Verificar que el usuario sea un evaluador pendiente
            if profile.user_type == 'evaluator' and not profile.is_approved_by_admin:
                # Marcar como aprobado
                profile.is_approved_by_admin = True
                profile.save()
                
                # Asignar permisos de evaluador
                evaluator_group, created = Group.objects.get_or_create(name='Evaluadores')
                user.groups.add(evaluator_group)
                
                # Crear notificación para el evaluador aprobado
                Notification.objects.create(
                    user=user,
                    title='¡Tu cuenta de evaluador ha sido aprobada!',
                    message='Felicidades, tu solicitud de evaluador ha sido aprobada por el administrador. Ya puedes evaluar proyectos.',
                    notification_type='system'
                )
                
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Usuario no es un evaluador pendiente'})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Usuario no encontrado'})
    return JsonResponse({'success': False})

@login_required
def reject_evaluator(request, user_id):
    if not request.user.is_staff:
        return JsonResponse({'success': False})
    
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            profile = user.profile
            
            # Verificar que el usuario sea un evaluador pendiente
            if profile.user_type == 'evaluator' and not profile.is_approved_by_admin:
                # Eliminar el usuario y su perfil
                user.delete()  # Esto también eliminará el perfil debido a CASCADE
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Usuario no es un evaluador pendiente'})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Usuario no encontrado'})
    return JsonResponse({'success': False})

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, 'Acceso denegado. Solo los administradores pueden acceder a esta página.')
        return redirect('home')

    # ── Usuarios ──────────────────────────────────────────────────────────────
    users = User.objects.select_related('profile').all().order_by('-date_joined')
    users_by_type = {
        'entrepreneur': Profile.objects.filter(user_type='entrepreneur').count(),
        'mentor':       Profile.objects.filter(user_type='mentor').count(),
        'investor':     Profile.objects.filter(user_type='investor').count(),
        'evaluator':    Profile.objects.filter(user_type='evaluator').count(),
    }

    # ── Evaluadores pendientes ────────────────────────────────────────────────
    pending_evaluators = Profile.objects.filter(user_type='evaluator', is_approved_by_admin=False)

    # ── Proyectos ─────────────────────────────────────────────────────────────
    projects = Project.objects.select_related('owner', 'category').all().order_by('-created_at')

    # ── Inversiones ───────────────────────────────────────────────────────────
    investments = Investment.objects.select_related('project', 'investor').all().order_by('-invested_at')
    investments_stats = Investment.objects.aggregate(
        total=Sum('amount'),
        count=Count('id'),
        pendiente=Count('id', filter=Q(status='pending')),
        aceptada=Count('id', filter=Q(status='accepted')),
        rechazada=Count('id', filter=Q(status='rejected')),
    )

    # ── Mentorías ─────────────────────────────────────────────────────────────
    mentorships = Mentorship.objects.select_related('project', 'mentor').all().order_by('-assigned_at')
    mentorships_stats = {
        'total':    Mentorship.objects.count(),
        'pending':  Mentorship.objects.filter(status='pending').count(),
        'accepted': Mentorship.objects.filter(status='accepted').count(),
        'rejected': Mentorship.objects.filter(status='rejected').count(),
    }

    # ── Monitoreo general ─────────────────────────────────────────────────────
    monitoring = {
        'total_users':          User.objects.count(),
        'active_users':         User.objects.filter(is_active=True).count(),
        'inactive_users':       User.objects.filter(is_active=False).count(),
        'total_projects':       Project.objects.count(),
        'active_projects':      Project.objects.filter(is_active=True).count(),
        'inactive_projects':    Project.objects.filter(is_active=False).count(),
        'total_investments':    investments_stats['count'] or 0,
        'total_amount':         investments_stats['total'] or 0,
        'pending_investments':  investments_stats['pendiente'] or 0,
        'total_mentorships':    mentorships_stats['total'],
        'active_mentorships':   mentorships_stats['accepted'],
    }

    return render(request, 'admin_dashboard.html', {
        'users': users,
        'users_by_type': users_by_type,
        'projects': projects,
        'pending_evaluators': pending_evaluators,
        'investments': investments,
        'investments_stats': investments_stats,
        'mentorships': mentorships,
        'mentorships_stats': mentorships_stats,
        'monitoring': monitoring,
    })


@login_required
def toggle_project_active(request, project_id):
    """Activa o desactiva un proyecto desde el panel de admin."""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Acceso denegado'}, status=403)
    try:
        project = Project.objects.get(id=project_id)
        project.is_active = not project.is_active
        project.save()
        return JsonResponse({'success': True, 'is_active': project.is_active})
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Proyecto no encontrado'}, status=404)


@login_required
def toggle_user_active(request, user_id):
    """Activa o desactiva la cuenta de un usuario desde el panel de admin."""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Acceso denegado'}, status=403)
    if request.user.id == user_id:
        return JsonResponse({'error': 'No puedes desactivar tu propia cuenta'}, status=400)
    try:
        user = User.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save()
        return JsonResponse({'success': True, 'is_active': user.is_active})
    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)


@login_required
def admin_toggle_investment(request, investment_id):
    """Cambia el estado de una inversión desde el panel de admin."""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Acceso denegado'}, status=403)
    try:
        investment = Investment.objects.get(id=investment_id)
        action = request.POST.get('action')
        if action == 'accept':
            if investment.status != 'accepted':
                project = investment.project
                accepted_total = Investment.objects.filter(
                    project=project,
                    status='accepted'
                ).exclude(id=investment.id).aggregate(total=Sum('amount'))['total'] or 0

                available = project.funding_goal - accepted_total
                if investment.amount > available:
                    return JsonResponse({
                        'error': f'No se puede aceptar: excede la meta del proyecto. Cupo disponible: {available:,.0f} COP.'
                    }, status=400)

                investment.status = 'accepted'
                investment.is_accepted = True
                investment.save()
                project.amount_raised = Investment.objects.filter(
                    project=project, status='accepted'
                ).aggregate(total=Sum('amount'))['total'] or 0

                # Verificar si se alcanzó la meta de financiación
                if project.amount_raised >= project.funding_goal and project.status not in ('funded', 'completed'):
                    project.status = 'funded'
                    Notification.objects.create(
                        user=project.owner,
                        title='¡Meta de financiación alcanzada!',
                        message=f'Tu proyecto "{project.title}" ha alcanzado su meta de financiación de {project.funding_goal:,.0f} COP. El proyecto ahora está completado.',
                        notification_type='project_update',
                        related_project=project,
                    )

                project.save()
        elif action == 'reject':
            if investment.status == 'accepted':
                project = investment.project
                project.amount_raised = max(
                    0,
                    (project.amount_raised or 0) - investment.amount
                )
                project.save()
            investment.status = 'rejected'
            investment.is_accepted = False
            investment.save()
        elif action == 'pending':
            investment.status = 'pending'
            investment.is_accepted = False
            investment.save()
        return JsonResponse({'success': True, 'status': investment.status})
    except Investment.DoesNotExist:
        return JsonResponse({'error': 'Inversión no encontrada'}, status=404)

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
        if investment.status == 'accepted':
            messages.info(request, 'Esta inversión ya fue aceptada anteriormente.')
            return redirect('dashboard')

        project = investment.project
        accepted_total = Investment.objects.filter(
            project=project,
            status='accepted'
        ).exclude(id=investment.id).aggregate(total=Sum('amount'))['total'] or 0
        available = project.funding_goal - accepted_total

        if investment.amount > available:
            messages.error(
                request,
                f'No se puede aceptar esta inversión porque supera la meta del proyecto. Cupo disponible: {available:,.0f} COP.'
            )
            return redirect('dashboard')

        investment.status = 'accepted'
        investment.is_accepted = True
        investment.save()

        # Recalcular el monto financiado solo con inversiones aceptadas.
        project.amount_raised = Investment.objects.filter(
            project=project,
            status='accepted'
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Verificar si se alcanzó la meta de financiación
        if project.amount_raised >= project.funding_goal and project.status not in ('funded', 'completed'):
            project.status = 'funded'
            # Notificar al emprendedor que su proyecto fue financiado
            Notification.objects.create(
                user=project.owner,
                title='¡Meta de financiación alcanzada!',
                message=f'Tu proyecto "{project.title}" ha alcanzado su meta de financiación de {project.funding_goal:,.0f} COP. El proyecto ahora está completado.',
                notification_type='project_update',
                related_project=project,
            )

        project.save()

        # Generar contrato de inversión
        contract = InvestmentContract.objects.create(investment=investment)

        # Crear notificación para el inversionista con enlace al contrato
        from django.urls import reverse
        contract_url = reverse('view_investment_contract', args=[contract.id])
        upload_url = reverse('upload_signed_contract', args=[contract.id])
        Notification.objects.create(
            user=investment.investor,
            title='¡Inversión aceptada! Contrato generado',
            message=(
                f'Tu inversión de ${investment.amount:,.0f} COP en "{project.title}" ha sido aceptada. '
                f'Se ha generado un contrato de inversión. '
                f'Por favor, descárgalo, fírmalo y súbelo firmado a la plataforma.'
            ),
            notification_type='investment',
            related_project=project,
            related_investment=investment,
        )

        messages.success(
            request,
            f'Has aceptado la inversión. Se ha generado un contrato (N.° CM-{contract.id:06d}) '
            f'para el inversionista.'
        )
    elif action == 'reject':
        investment.status = 'rejected'
        investment.save()
        
        # Crear notificación para el inversionista
        Notification.objects.create(
            user=investment.investor,
            title='Inversión rechazada',
            message=f'Tu inversión de ${investment.amount:,.0f} COP en "{investment.project.title}" ha sido rechazada.',
            notification_type='investment',
            related_project=investment.project
        )

        messages.success(request, 'Has rechazado la inversión. El dinero será reembolsado al inversionista.')
    else:
        messages.error(request, 'Acción no válida.')

    return redirect('dashboard')

class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('/')

@login_required
def request_mentorship_by_mentor(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.user.profile.user_type != 'mentor':
        messages.error(request, 'Solo los mentores pueden solicitar mentorías.')
        return redirect('project_list')

    # Check if there's an active mentorship
    active_mentorship = Mentorship.objects.filter(
        project=project,
        mentor=request.user,
        status='accepted'
    ).exists()

    if active_mentorship:
        messages.error(request, 'Ya tienes una mentoría activa para este proyecto.')
        return redirect('project_list')

    # Check if there's a pending request
    pending_mentorship = Mentorship.objects.filter(
        project=project,
        mentor=request.user,
        status='pending'
    ).exists()

    if pending_mentorship:
        messages.info(request, f'Ya tienes una solicitud de mentoría pendiente para el proyecto {project.title}.')
        return redirect('project_list')

    # Create new mentorship request
    mentorship = Mentorship.objects.create(
        project=project,
        mentor=request.user,
        initiated_by='mentor',
        status='pending'
    )
    
    # Crear notificación para el dueño del proyecto
    Notification.objects.create(
        user=project.owner,
        title='Nueva solicitud de mentoría',
        message=f'{request.user.username} quiere ser mentor de tu proyecto "{project.title}".',
        notification_type='mentorship',
        related_mentorship=mentorship,
        related_project=project
    )

    messages.success(request, f'Solicitud de mentoría enviada para el proyecto {project.title}.')
    return redirect('project_list')

@login_required
def request_mentorship_by_entrepreneur(request, mentor_id):
    mentor = get_object_or_404(Profile, user_id=mentor_id, user_type='mentor')
    if request.user.profile.user_type != 'entrepreneur':
        messages.error(request, 'Solo los emprendedores pueden solicitar mentorías.')
        return redirect('mentor_list')

    # Get the entrepreneur's most recent active project
    try:
        project = Project.objects.filter(owner=request.user, is_active=True).latest('created_at')
    except Project.DoesNotExist:
        messages.error(request, 'No tienes ningún proyecto activo para solicitar mentoría.')
        return redirect('project_list')
    
    # Check if there's an active mentorship
    active_mentorship = Mentorship.objects.filter(
        project=project,
        mentor=mentor.user,
        status='accepted'
    ).exists()

    if active_mentorship:
        messages.error(request, 'Ya tienes una mentoría activa con este mentor.')
        return redirect('mentor_list')

    # Check if there's a pending request
    pending_mentorship = Mentorship.objects.filter(
        project=project,
        mentor=mentor.user,
        status='pending'
    ).exists()

    if pending_mentorship:
        messages.info(request, f'Ya tienes una solicitud de mentoría pendiente con {mentor.user.username}.')
        return redirect('mentor_list')

    # Create new mentorship request
    mentorship = Mentorship.objects.create(
        project=project,
        mentor=mentor.user,
        initiated_by='entrepreneur',
        status='pending'
    )
    
    # Crear notificación para el mentor
    Notification.objects.create(
        user=mentor.user,
        title='Nueva solicitud de mentoría',
        message=f'{request.user.username} solicita tu mentoría para el proyecto "{project.title}".',
        notification_type='mentorship',
        related_mentorship=mentorship,
        related_project=project
    )

    messages.success(request, f'Solicitud de mentoría enviada al mentor {mentor.user.username}.')
    return redirect('mentor_list')

@login_required
def respond_to_mentorship_request(request, mentorship_id, action):
    mentorship = get_object_or_404(Mentorship, id=mentorship_id)
    
    # Verificar que el usuario sea el dueño del proyecto o el mentor, dependiendo de quién inició la solicitud
    if mentorship.initiated_by == 'mentor':
        if request.user != mentorship.project.owner:
            messages.error(request, 'No tienes permiso para responder a esta solicitud.')
            return redirect('dashboard')
    else:  # initiated_by == 'entrepreneur'
        if request.user != mentorship.mentor:
            messages.error(request, 'No tienes permiso para responder a esta solicitud.')
            return redirect('dashboard')

    if action == 'accept':
        mentorship.status = 'accepted'
        mentorship.save()
        
        # Crear notificación para quien solicitó la mentoría
        if mentorship.initiated_by == 'mentor':
            recipient = mentorship.mentor
            message_text = f'{request.user.username} ha aceptado tu solicitud de mentoría para el proyecto "{mentorship.project.title}".'
        else:
            recipient = mentorship.project.owner
            message_text = f'{request.user.username} ha aceptado tu solicitud de mentoría.'
        
        Notification.objects.create(
            user=recipient,
            title='Solicitud de mentoría aceptada',
            message=message_text,
            notification_type='mentorship',
            related_mentorship=mentorship,
            related_project=mentorship.project
        )
        
        messages.success(request, 'Has aceptado la solicitud de mentoría.')
    elif action == 'reject':
        # Crear notificación antes de eliminar
        if mentorship.initiated_by == 'mentor':
            recipient = mentorship.mentor
        else:
            recipient = mentorship.project.owner
        
        Notification.objects.create(
            user=recipient,
            title='Solicitud de mentoría rechazada',
            message=f'{request.user.username} ha rechazado tu solicitud de mentoría.',
            notification_type='mentorship'
        )
        
        mentorship.delete()
        messages.info(request, 'Has rechazado la solicitud de mentoría.')
    else:
        messages.error(request, 'Acción no válida.')
        return redirect('dashboard')

    return redirect('dashboard')

@login_required
def mentor_list(request):
    mentors = Profile.objects.filter(user_type='mentor', is_approved=True)
    
    # Si el usuario es emprendedor, obtener sus mentorías activas
    active_mentorships = []
    if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.user_type == 'entrepreneur':
        # Obtener el proyecto más reciente activo del emprendedor
        try:
            project = Project.objects.filter(owner=request.user, is_active=True).latest('created_at')
            # Obtener todas las mentorías activas para ese proyecto
            active_mentorships = Mentorship.objects.filter(
                project=project,
                status='accepted'
            ).values_list('mentor_id', flat=True)
        except Project.DoesNotExist:
            pass
    
    return render(request, 'mentor_list.html', {
        'mentors': mentors,
        'active_mentorships': active_mentorships
    })

@login_required
def project_list_for_mentors(request):
    projects = Project.objects.filter(is_active=True)
    return render(request, 'project_list_for_mentors.html', {'projects': projects})

@login_required
def mentorship_chat(request, mentorship_id):
    mentorship = get_object_or_404(Mentorship, id=mentorship_id)
    
    # Verificar que el usuario sea el mentor o el dueño del proyecto
    if request.user != mentorship.mentor and request.user != mentorship.project.owner:
        messages.error(request, 'No tienes permiso para acceder a este chat.')
        return redirect('dashboard')
    
    # Verificar que la mentoría esté aceptada
    if mentorship.status != 'accepted':
        messages.error(request, 'Esta mentoría no está activa.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = MentorshipMessageForm(request.POST, user=request.user)
        if form.is_valid():
            message = form.save(commit=False)
            message.mentorship = mentorship
            message.sender = request.user
            message.save()
            
            # Crear notificación para el otro usuario
            recipient = mentorship.mentor if request.user == mentorship.project.owner else mentorship.project.owner
            Notification.objects.create(
                user=recipient,
                title='Nuevo mensaje de mentoría',
                message=f'{request.user.username} te ha enviado un mensaje.',
                notification_type='message',
                related_mentorship=mentorship
            )
            
            return redirect('mentorship_chat', mentorship_id=mentorship_id)
    else:
        form = MentorshipMessageForm(user=request.user)

    # Obtener todos los mensajes del chat
    chat_messages = mentorship.messages.all().order_by('timestamp')
    
    # Marcar mensajes como leídos
    mentorship.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    # Obtener el otro usuario
    other_user = mentorship.mentor if request.user == mentorship.project.owner else mentorship.project.owner
    
    # Determinar el tipo de usuario actual
    current_user_type = request.user.profile.user_type if hasattr(request.user, 'profile') else None

    return render(request, 'mentorship_chat.html', {
        'mentorship': mentorship,
        'messages': chat_messages,
        'form': form,
        'other_user': other_user,
        'current_user_type': current_user_type
    })

@login_required
def mark_messages_as_read(request, mentorship_id):
    mentorship = get_object_or_404(Mentorship, id=mentorship_id)
    
    # Verificar que el usuario sea el mentor o el dueño del proyecto
    if request.user != mentorship.mentor and request.user != mentorship.project.owner:
        return JsonResponse({'error': 'No tienes permiso para realizar esta acción.'}, status=403)
    
    # Marcar como leídos los mensajes que no fueron enviados por el usuario actual
    mentorship.messages.filter(sender__id__ne=request.user.id, is_read=False).update(is_read=True)
    
    return JsonResponse({'success': True})

@login_required
def get_unread_messages_count(request):
    # Obtener todas las mentorías activas del usuario
    if request.user.profile.user_type == 'mentor':
        mentorships = Mentorship.objects.filter(mentor=request.user, status='accepted')
    else:
        mentorships = Mentorship.objects.filter(project__owner=request.user, status='accepted')
    
    # Contar mensajes no leídos
    unread_count = 0
    for mentorship in mentorships:
        unread_count += mentorship.messages.filter(sender__id__ne=request.user.id, is_read=False).count()
    
    return JsonResponse({'unread_count': unread_count})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('admin_dashboard')
                return redirect('dashboard')
            else:
                form.add_error(None, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

# ========== VISTAS DE ADMINISTRACIÓN DE RECURSOS ==========

@login_required
def admin_resources(request):
    """Vista principal para gestionar recursos desde el panel de administrador"""
    if not request.user.is_superuser:
        messages.error(request, 'Acceso denegado. Solo los administradores pueden acceder a esta página.')
        return redirect('home')

    categories = ResourceCategory.objects.all()
    resources = Resource.objects.all().order_by('-created_at')
    
    context = {
        'categories': categories,
        'resources': resources,
    }
    return render(request, 'admin_resources.html', context)

@login_required
def create_resource_category(request):
    """Vista para crear una nueva categoría de recursos"""
    if not request.user.is_superuser:
        messages.error(request, 'Acceso denegado.')
        return redirect('home')

    if request.method == 'POST':
        form = ResourceCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada exitosamente.')
            return redirect('admin_resources')
    else:
        form = ResourceCategoryForm()
    
    return render(request, 'create_resource_category.html', {'form': form})

@login_required
def edit_resource_category(request, category_id):
    """Vista para editar una categoría de recursos"""
    if not request.user.is_superuser:
        messages.error(request, 'Acceso denegado.')
        return redirect('home')

    category = get_object_or_404(ResourceCategory, id=category_id)
    
    if request.method == 'POST':
        form = ResourceCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada exitosamente.')
            return redirect('admin_resources')
    else:
        form = ResourceCategoryForm(instance=category)
    
    return render(request, 'edit_resource_category.html', {'form': form, 'category': category})

@login_required
def delete_resource_category(request, category_id):
    """Vista para eliminar una categoría de recursos"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Acceso denegado'}, status=403)

    try:
        category = ResourceCategory.objects.get(id=category_id)
        
        # Verificar si tiene recursos asociados
        if category.resources.exists():
            return JsonResponse({
                'error': 'No se puede eliminar la categoría porque tiene recursos asociados'
            }, status=400)
        
        category.delete()
        return JsonResponse({'success': 'Categoría eliminada correctamente'})
    except ResourceCategory.DoesNotExist:
        return JsonResponse({'error': 'Categoría no encontrada'}, status=404)

@login_required
def create_resource(request):
    """Vista para crear un nuevo recurso"""
    if not request.user.is_superuser:
        messages.error(request, 'Acceso denegado.')
        return redirect('home')

    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.created_by = request.user
            resource.save()
            messages.success(request, 'Recurso creado exitosamente.')
            return redirect('admin_resources')
    else:
        form = ResourceForm()
    
    return render(request, 'create_resource.html', {'form': form})

@login_required
def edit_resource(request, resource_id):
    """Vista para editar un recurso"""
    if not request.user.is_superuser:
        messages.error(request, 'Acceso denegado.')
        return redirect('home')

    resource = get_object_or_404(Resource, id=resource_id)
    
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, 'Recurso actualizado exitosamente.')
            return redirect('admin_resources')
    else:
        form = ResourceForm(instance=resource)
    
    return render(request, 'edit_resource.html', {'form': form, 'resource': resource})

@login_required
def delete_resource(request, resource_id):
    """Vista para eliminar un recurso"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Acceso denegado'}, status=403)

    try:
        resource = Resource.objects.get(id=resource_id)
        resource.delete()
        return JsonResponse({'success': 'Recurso eliminado correctamente'})
    except Resource.DoesNotExist:
        return JsonResponse({'error': 'Recurso no encontrado'}, status=404)

@login_required
def toggle_resource_status(request, resource_id):
    """Vista para activar/desactivar un recurso"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Acceso denegado'}, status=403)

    try:
        resource = Resource.objects.get(id=resource_id)
        resource.is_active = not resource.is_active
        resource.save()
        
        status = 'activado' if resource.is_active else 'desactivado'
        return JsonResponse({
            'success': f'Recurso {status} correctamente',
            'is_active': resource.is_active
        })
    except Resource.DoesNotExist:
        return JsonResponse({'error': 'Recurso no encontrado'}, status=404)

@login_required
def toggle_resource_featured(request, resource_id):
    """Vista para destacar/no destacar un recurso"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Acceso denegado'}, status=403)

    try:
        resource = Resource.objects.get(id=resource_id)
        resource.is_featured = not resource.is_featured
        resource.save()
        
        status = 'destacado' if resource.is_featured else 'no destacado'
        return JsonResponse({
            'success': f'Recurso marcado como {status}',
            'is_featured': resource.is_featured
        })
    except Resource.DoesNotExist:
        return JsonResponse({'error': 'Recurso no encontrado'}, status=404)

# ========== VISTAS DE EVALUACIÓN ==========

@login_required
def evaluate_project(request, project_id):
    """Vista para evaluar un proyecto"""
    if request.user.profile.user_type not in ['evaluator', 'mentor']:
        messages.error(request, 'No tienes permisos para evaluar proyectos.')
        return redirect('project_detail', pk=project_id)

    project = get_object_or_404(Project, id=project_id)
    criteria = EvaluationCriteria.objects.filter(is_active=True)
    
    # Verificar si ya existe una evaluación
    try:
        evaluation = ProjectEvaluation.objects.get(project=project, evaluator=request.user)
        existing_scores = {cs.criteria.id: cs for cs in evaluation.criterion_scores.all()}
    except ProjectEvaluation.DoesNotExist:
        evaluation = None
        existing_scores = {}

    if request.method == 'POST':
        evaluation_form = ProjectEvaluationForm(request.POST, instance=evaluation)
        
        if evaluation_form.is_valid():
            if not evaluation:
                evaluation = evaluation_form.save(commit=False)
                evaluation.project = project
                evaluation.evaluator = request.user
                evaluation.save()
            else:
                evaluation = evaluation_form.save()
            
            # Procesar puntajes de criterios
            total_score = 0
            total_weight = 0
            
            for criterion in criteria:
                score_key = f'score_{criterion.id}'
                comment_key = f'comment_{criterion.id}'
                
                if score_key in request.POST:
                    score = float(request.POST[score_key])
                    comment = request.POST.get(comment_key, '')
                    
                    criterion_score, created = CriterionScore.objects.get_or_create(
                        evaluation=evaluation,
                        criteria=criterion,
                        defaults={'score': score, 'comments': comment}
                    )
                    if not created:
                        criterion_score.score = score
                        criterion_score.comments = comment
                        criterion_score.save()
                    
                    total_score += score * criterion.weight
                    total_weight += criterion.weight
            
            # Calcular puntaje general
            if total_weight > 0:
                evaluation.overall_score = round(total_score / total_weight, 2)
                evaluation.save()
            
            # Crear notificación para el emprendedor
            Notification.objects.create(
                user=project.owner,
                title='Nueva evaluación de proyecto',
                message=f'Tu proyecto "{project.title}" ha sido evaluado con un puntaje de {evaluation.overall_score}/10.',
                notification_type='evaluation',
                related_project=project
            )
            
            messages.success(request, 'Evaluación guardada exitosamente.')
            return redirect('project_detail', pk=project_id)
    else:
        evaluation_form = ProjectEvaluationForm(instance=evaluation)
    
    context = {
        'project': project,
        'evaluation_form': evaluation_form,
        'criteria': criteria,
        'existing_scores': existing_scores,
        'evaluation': evaluation
    }
    
    return render(request, 'evaluate_project.html', context)

@login_required
def notifications(request):
    """Vista para mostrar notificaciones del usuario"""
    all_notifications = request.user.notifications.all()
    unread_count = all_notifications.filter(is_read=False).count()
    notifications = all_notifications[:20]  # Últimas 20 notificaciones
    
    # Marcar como leídas
    if request.method == 'POST':
        notification_ids = request.POST.getlist('mark_read')
        Notification.objects.filter(id__in=notification_ids, user=request.user).update(is_read=True)
        return redirect('notifications')
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count
    }
    
    return render(request, 'notifications.html', context)

@login_required
def mark_notification_read(request, notification_id):
    """Marcar una notificación como leída"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'error': 'Notificación no encontrada'}, status=404)

@login_required
def get_notifications_count(request):
    """API endpoint para obtener el número de notificaciones no leídas"""
    unread_count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'unread_count': unread_count})

@login_required
def analytics_dashboard(request):
    """Dashboard de analíticas para administradores"""
    if not request.user.is_superuser:
        messages.error(request, 'Acceso denegado.')
        return redirect('home')
    
    # Estadísticas generales
    total_projects = Project.objects.count()
    active_projects = Project.objects.filter(is_active=True).count()
    total_investments = Investment.objects.aggregate(
        total=Sum('amount'),
        count=Count('id')
    )
    total_users = User.objects.count()
    
    # Proyectos por categoría
    projects_by_category = ProjectCategory.objects.annotate(
        project_count=Count('project')
    ).order_by('-project_count')
    
    # Proyectos más financiados
    top_funded_projects = Project.objects.order_by('-amount_raised')[:10]
    
    # Proyectos más vistos
    top_viewed_projects = Project.objects.order_by('-views_count')[:10]
    
    # Evaluaciones promedio por proyecto
    best_evaluated_projects = Project.objects.annotate(
        avg_evaluation=Avg('evaluations__overall_score'),
        recommended_count=Count('evaluations', filter=Q(evaluations__is_recommended=True))
    ).filter(avg_evaluation__isnull=False).order_by('-avg_evaluation')[:10]
    
    context = {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'total_investments': total_investments,
        'total_users': total_users,
        'projects_by_category': projects_by_category,
        'top_funded_projects': top_funded_projects,
        'top_viewed_projects': top_viewed_projects,
        'best_evaluated_projects': best_evaluated_projects,
    }
    
    return render(request, 'analytics_dashboard.html', context)

@login_required
def analytics_report(request):
    """Generar un reporte CSV con las principales métricas analíticas."""
    if not request.user.is_superuser:
        messages.error(request, 'Acceso denegado.')
        return redirect('home')

    # Reutilizar la lógica del dashboard
    total_projects = Project.objects.count()
    active_projects = Project.objects.filter(is_active=True).count()
    total_investments = Investment.objects.aggregate(
        total=Sum('amount'),
        count=Count('id')
    )
    total_users = User.objects.count()

    projects_by_category = ProjectCategory.objects.annotate(
        project_count=Count('project')
    ).order_by('-project_count')

    top_funded_projects = Project.objects.order_by('-amount_raised')[:10]
    top_viewed_projects = Project.objects.order_by('-views_count')[:10]
    best_evaluated_projects = Project.objects.annotate(
        avg_evaluation=Avg('evaluations__overall_score'),
        recommended_count=Count('evaluations', filter=Q(evaluations__is_recommended=True))
    ).filter(avg_evaluation__isnull=False).order_by('-avg_evaluation')[:10]

    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    filename = f'reporte_analiticas_{timestamp}.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    import csv

    writer = csv.writer(response)
    writer.writerow(['Reporte de Analiticas'])
    writer.writerow(['Generado', timezone.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])

    writer.writerow(['Resumen'])
    writer.writerow(['Total de proyectos', total_projects])
    writer.writerow(['Proyectos activos', active_projects])
    writer.writerow(['Total de usuarios', total_users])
    writer.writerow(['Total de inversiones', total_investments.get('count') or 0])
    writer.writerow(['Monto total invertido', total_investments.get('total') or 0])
    writer.writerow([])

    writer.writerow(['Proyectos por categoria'])
    writer.writerow(['Categoria', 'Cantidad de proyectos'])
    for category in projects_by_category:
        writer.writerow([category.name, category.project_count])
    writer.writerow([])

    writer.writerow(['Top 10 proyectos mas financiados'])
    writer.writerow(['Proyecto', 'Monto recaudado'])
    for project in top_funded_projects:
        writer.writerow([project.title, project.amount_raised])
    writer.writerow([])

    writer.writerow(['Top 10 proyectos mas vistos'])
    writer.writerow(['Proyecto', 'Vistas'])
    for project in top_viewed_projects:
        writer.writerow([project.title, project.views_count])
    writer.writerow([])

    writer.writerow(['Top 10 proyectos mejor evaluados'])
    writer.writerow(['Proyecto', 'Promedio de evaluacion', 'Recomendaciones'])
    for project in best_evaluated_projects:
        writer.writerow([project.title, project.avg_evaluation, project.recommended_count])

    return response

@login_required
def like_project(request, project_id):
    """Toggle like/unlike en un proyecto"""
    if request.method == 'POST':
        project = get_object_or_404(Project, id=project_id)
        
        # Por simplicidad, incrementamos el contador (después implementaremos likes por usuario)
        project.likes_count += 1
        project.save()
        
        return JsonResponse({
            'liked': True,
            'likes_count': project.likes_count
        })
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


# ========== MÉTRICAS POR ROL ==========

@login_required
def entrepreneur_metrics(request):
    """Dashboard de métricas personales para emprendedores."""
    profile = get_object_or_404(Profile, user=request.user)
    if profile.user_type != 'entrepreneur':
        messages.error(request, 'Acceso denegado.')
        return redirect('dashboard')

    projects = Project.objects.filter(owner=request.user)

    # Agregar anotaciones por proyecto
    projects_data = []
    for p in projects:
        investments_accepted = p.investments.filter(status='accepted')
        investments_pending = p.investments.filter(status='pending')
        total_invested = investments_accepted.aggregate(total=Sum('amount'))['total'] or 0
        investors_count = investments_accepted.count()
        mentors_count = p.mentorships.filter(status='accepted').count()
        avg_score = p.evaluations.aggregate(avg=Avg('overall_score'))['avg']
        projects_data.append({
            'project': p,
            'total_invested': total_invested,
            'investors_count': investors_count,
            'pending_investments': investments_pending.count(),
            'mentors_count': mentors_count,
            'avg_score': round(avg_score, 2) if avg_score else None,
            'funding_pct': p.get_funding_percentage(),
        })

    total_raised = sum(d['total_invested'] for d in projects_data)
    total_investors = Investment.objects.filter(project__owner=request.user, status='accepted').values('investor').distinct().count()
    total_mentors = Mentorship.objects.filter(project__owner=request.user, status='accepted').values('mentor').distinct().count()
    total_projects = projects.count()
    active_projects = projects.filter(is_active=True).count()

    context = {
        'projects_data': projects_data,
        'total_raised': total_raised,
        'total_investors': total_investors,
        'total_mentors': total_mentors,
        'total_projects': total_projects,
        'active_projects': active_projects,
        'profile': profile,
    }
    return render(request, 'entrepreneur_metrics.html', context)


@login_required
def entrepreneur_report(request):
    """Exporta reporte CSV de métricas del emprendedor."""
    profile = get_object_or_404(Profile, user=request.user)
    if profile.user_type != 'entrepreneur':
        messages.error(request, 'Acceso denegado.')
        return redirect('dashboard')

    import csv
    projects = Project.objects.filter(owner=request.user)

    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="reporte_emprendedor_{timestamp}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Reporte de Métricas - Emprendedor'])
    writer.writerow(['Generado el', timezone.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow(['Emprendedor', request.user.get_full_name() or request.user.username])
    writer.writerow([])

    writer.writerow(['Resumen General'])
    writer.writerow(['Total proyectos', projects.count()])
    writer.writerow(['Proyectos activos', projects.filter(is_active=True).count()])
    total_raised = Investment.objects.filter(project__owner=request.user, status='accepted').aggregate(total=Sum('amount'))['total'] or 0
    writer.writerow(['Total recaudado', total_raised])
    writer.writerow([])

    writer.writerow(['Detalle por Proyecto'])
    writer.writerow(['Proyecto', 'Estado', 'Meta', 'Recaudado', '% Financiado', 'Inversiones aceptadas',
                     'Inversiones pendientes', 'Mentores', 'Promedio evaluación', 'Vistas', 'Likes'])
    for p in projects:
        investments_accepted = p.investments.filter(status='accepted')
        investments_pending = p.investments.filter(status='pending')
        total_invested = investments_accepted.aggregate(total=Sum('amount'))['total'] or 0
        avg_score = p.evaluations.aggregate(avg=Avg('overall_score'))['avg']
        writer.writerow([
            p.title,
            p.get_status_display(),
            p.funding_goal,
            total_invested,
            f"{p.get_funding_percentage():.1f}%",
            investments_accepted.count(),
            investments_pending.count(),
            p.mentorships.filter(status='accepted').count(),
            f"{avg_score:.2f}" if avg_score else 'Sin evaluar',
            p.views_count,
            p.likes_count,
        ])

    return response


@login_required
def investor_metrics(request):
    """Dashboard de métricas de portafolio para inversionistas."""
    profile = get_object_or_404(Profile, user=request.user)
    if profile.user_type != 'investor':
        messages.error(request, 'Acceso denegado.')
        return redirect('dashboard')

    investments = Investment.objects.filter(investor=request.user).select_related('project')

    accepted = investments.filter(status='accepted')
    pending = investments.filter(status='pending')
    rejected = investments.filter(status='rejected')

    total_invested = accepted.aggregate(total=Sum('amount'))['total'] or 0
    total_equity = sum(inv.equity_percentage for inv in accepted)
    projects_count = accepted.values('project').distinct().count()

    # Por proyecto
    portfolio = []
    for inv in accepted:
        portfolio.append({
            'investment': inv,
            'project': inv.project,
            'funding_pct': inv.project.get_funding_percentage(),
        })

    # Distribución por estado de proyecto
    status_breakdown = {}
    for inv in accepted:
        s = inv.project.get_status_display()
        status_breakdown[s] = status_breakdown.get(s, 0) + 1

    context = {
        'portfolio': portfolio,
        'pending_investments': pending,
        'rejected_investments': rejected,
        'total_invested': total_invested,
        'total_equity': round(total_equity, 2),
        'projects_count': projects_count,
        'pending_count': pending.count(),
        'rejected_count': rejected.count(),
        'status_breakdown': status_breakdown,
        'profile': profile,
    }
    return render(request, 'investor_metrics.html', context)


@login_required
def investor_report(request):
    """Exporta reporte CSV del portafolio del inversionista."""
    profile = get_object_or_404(Profile, user=request.user)
    if profile.user_type != 'investor':
        messages.error(request, 'Acceso denegado.')
        return redirect('dashboard')

    import csv
    investments = Investment.objects.filter(investor=request.user).select_related('project')
    accepted = investments.filter(status='accepted')
    total_invested = accepted.aggregate(total=Sum('amount'))['total'] or 0
    total_equity = sum(inv.equity_percentage for inv in accepted)

    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="reporte_inversionista_{timestamp}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Reporte de Portafolio - Inversionista'])
    writer.writerow(['Generado el', timezone.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow(['Inversionista', request.user.get_full_name() or request.user.username])
    writer.writerow([])

    writer.writerow(['Resumen'])
    writer.writerow(['Total invertido (aceptadas)', total_invested])
    writer.writerow(['Equity total acumulado (%)', f"{total_equity:.2f}"])
    writer.writerow(['Proyectos en portafolio', accepted.values('project').distinct().count()])
    writer.writerow(['Inversiones pendientes', investments.filter(status='pending').count()])
    writer.writerow([])

    writer.writerow(['Detalle de Inversiones Aceptadas'])
    writer.writerow(['Proyecto', 'Estado proyecto', 'Monto invertido', 'Equity (%)',
                     '% Financiado del proyecto', 'Meta de financiación', 'Total recaudado', 'Fecha de inversión'])
    for inv in accepted:
        writer.writerow([
            inv.project.title,
            inv.project.get_status_display(),
            inv.amount,
            f"{inv.equity_percentage:.2f}",
            f"{inv.project.get_funding_percentage():.1f}%",
            inv.project.funding_goal,
            inv.project.amount_raised,
            inv.invested_at.strftime('%Y-%m-%d'),
        ])

    pending = investments.filter(status='pending')
    if pending.exists():
        writer.writerow([])
        writer.writerow(['Inversiones Pendientes'])
        writer.writerow(['Proyecto', 'Monto', 'Equity (%)', 'Fecha de solicitud'])
        for inv in pending:
            writer.writerow([
                inv.project.title,
                inv.amount,
                f"{inv.equity_percentage:.2f}",
                inv.invested_at.strftime('%Y-%m-%d'),
            ])

    return response


@login_required
def mentor_metrics(request):
    """Dashboard de métricas de actividad para mentores."""
    profile = get_object_or_404(Profile, user=request.user)
    if profile.user_type != 'mentor':
        messages.error(request, 'Acceso denegado.')
        return redirect('dashboard')

    mentorships = Mentorship.objects.filter(mentor=request.user).select_related('project', 'project__owner')

    active = mentorships.filter(status='accepted')
    pending_ms = mentorships.filter(status='pending')
    rejected_ms = mentorships.filter(status='rejected')

    # Mensajes enviados/recibidos
    total_messages_sent = Message.objects.filter(mentorship__mentor=request.user, sender=request.user).count()
    total_messages_received = Message.objects.filter(mentorship__mentor=request.user).exclude(sender=request.user).count()

    # Proyectos activos que mentor está apoyando
    active_projects_data = []
    for ms in active:
        p = ms.project
        avg_score = p.evaluations.aggregate(avg=Avg('overall_score'))['avg']
        messages_count = ms.messages.count()
        active_projects_data.append({
            'mentorship': ms,
            'project': p,
            'funding_pct': p.get_funding_percentage(),
            'avg_score': round(avg_score, 2) if avg_score else None,
            'messages_count': messages_count,
        })

    # Conexiones con inversionistas
    connections = MentorInvestorConnection.objects.filter(mentor=request.user, status='accepted').count()

    context = {
        'active_projects_data': active_projects_data,
        'pending_mentorships': pending_ms,
        'total_active': active.count(),
        'total_pending': pending_ms.count(),
        'total_rejected': rejected_ms.count(),
        'total_messages_sent': total_messages_sent,
        'total_messages_received': total_messages_received,
        'investor_connections': connections,
        'profile': profile,
    }
    return render(request, 'mentor_metrics.html', context)


@login_required
def mentor_report(request):
    """Exporta reporte CSV de actividad del mentor."""
    profile = get_object_or_404(Profile, user=request.user)
    if profile.user_type != 'mentor':
        messages.error(request, 'Acceso denegado.')
        return redirect('dashboard')

    import csv
    mentorships = Mentorship.objects.filter(mentor=request.user).select_related('project', 'project__owner')
    active = mentorships.filter(status='accepted')

    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="reporte_mentor_{timestamp}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Reporte de Actividad - Mentor'])
    writer.writerow(['Generado el', timezone.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow(['Mentor', request.user.get_full_name() or request.user.username])
    writer.writerow([])

    writer.writerow(['Resumen'])
    writer.writerow(['Mentorías activas', active.count()])
    writer.writerow(['Mentorías pendientes', mentorships.filter(status='pending').count()])
    total_sent = Message.objects.filter(mentorship__mentor=request.user, sender=request.user).count()
    total_recv = Message.objects.filter(mentorship__mentor=request.user).exclude(sender=request.user).count()
    writer.writerow(['Mensajes enviados', total_sent])
    writer.writerow(['Mensajes recibidos', total_recv])
    investor_conn = MentorInvestorConnection.objects.filter(mentor=request.user, status='accepted').count()
    writer.writerow(['Conexiones con inversionistas', investor_conn])
    writer.writerow([])

    writer.writerow(['Detalle de Mentorías Activas'])
    writer.writerow(['Proyecto', 'Emprendedor', 'Estado proyecto', '% Financiado',
                     'Meta', 'Recaudado', 'Promedio evaluación', 'Mensajes intercambiados', 'Desde'])
    for ms in active:
        p = ms.project
        avg_score = p.evaluations.aggregate(avg=Avg('overall_score'))['avg']
        writer.writerow([
            p.title,
            p.owner.get_full_name() or p.owner.username,
            p.get_status_display(),
            f"{p.get_funding_percentage():.1f}%",
            p.funding_goal,
            p.amount_raised,
            f"{avg_score:.2f}" if avg_score else 'Sin evaluar',
            ms.messages.count(),
            ms.assigned_at.strftime('%Y-%m-%d'),
        ])

    return response


# ========== VISTAS PARA INTERACCIÓN MENTOR-INVERSIONISTA ==========

@login_required
def investor_list_for_mentors(request):
    """Vista para que mentores vean lista de inversionistas disponibles"""
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'mentor':
        messages.error(request, 'Solo los mentores pueden acceder a esta página.')
        return redirect('home')
    
    # Obtener inversionistas activos
    investors = Profile.objects.filter(user_type='investor', is_approved=True).select_related('user')
    
    # Obtener conexiones existentes para no mostrar inversionistas ya conectados
    existing_connections = MentorInvestorConnection.objects.filter(
        mentor=request.user,
        status__in=['pending', 'accepted']
    ).values_list('investor_id', flat=True)
    
    investors = investors.exclude(user_id__in=existing_connections)
    
    context = {
        'investors': investors,
        'user_type': 'mentor'
    }
    return render(request, 'mentor_investor_list.html', context)

@login_required
def mentor_list_for_investors(request):
    """Vista para que inversionistas vean lista de mentores disponibles"""
    if not hasattr(request.user, 'profile') or request.user.profile.user_type != 'investor':
        messages.error(request, 'Solo los inversionistas pueden acceder a esta página.')
        return redirect('home')
    
    # Obtener mentores activos y aprobados
    mentors = Profile.objects.filter(user_type='mentor', is_approved=True).select_related('user')
    
    # Obtener conexiones existentes para no mostrar mentores ya conectados
    existing_connections = MentorInvestorConnection.objects.filter(
        investor=request.user,
        status__in=['pending', 'accepted']
    ).values_list('mentor_id', flat=True)
    
    mentors = mentors.exclude(user_id__in=existing_connections)
    
    context = {
        'mentors': mentors,
        'user_type': 'investor'
    }
    return render(request, 'mentor_investor_list.html', context)

@login_required
def create_mentor_investor_connection(request, target_user_id):
    """Crear una nueva conexión entre mentor e inversionista"""
    if not hasattr(request.user, 'profile'):
        messages.error(request, 'Tu cuenta no tiene un perfil asociado.')
        return redirect('home')
    
    target_user = get_object_or_404(User, id=target_user_id)
    current_user_type = request.user.profile.user_type
    target_user_type = target_user.profile.user_type
    
    # Validar que la conexión sea válida (mentor-inversionista)
    if not ((current_user_type == 'mentor' and target_user_type == 'investor') or 
            (current_user_type == 'investor' and target_user_type == 'mentor')):
        messages.error(request, 'Solo se pueden crear conexiones entre mentores e inversionistas.')
        return redirect('home')
    
    # Verificar que no exista ya una conexión
    if current_user_type == 'mentor':
        existing_connection = MentorInvestorConnection.objects.filter(
            mentor=request.user, investor=target_user
        ).first()
    else:
        existing_connection = MentorInvestorConnection.objects.filter(
            mentor=target_user, investor=request.user
        ).first()
    
    if existing_connection:
        messages.warning(request, 'Ya existe una conexión con este usuario.')
        return redirect('mentor_investor_connections')
    
    if request.method == 'POST':
        form = MentorInvestorConnectionForm(request.POST)
        if form.is_valid():
            connection = form.save(commit=False)
            
            # Establecer mentor e inversionista según el tipo de usuario
            if current_user_type == 'mentor':
                connection.mentor = request.user
                connection.investor = target_user
                connection.initiated_by = 'mentor'
            else:
                connection.mentor = target_user
                connection.investor = request.user
                connection.initiated_by = 'investor'
            
            connection.save()
            
            # Crear notificación para el usuario objetivo
            Notification.objects.create(
                user=target_user,
                title='Nueva solicitud de conexión',
                message=f'{request.user.username} quiere conectarse contigo para colaborar.',
                notification_type='system'
            )
            
            messages.success(request, 'Solicitud de conexión enviada exitosamente.')
            return redirect('mentor_investor_connections')
    else:
        form = MentorInvestorConnectionForm()
    
    context = {
        'form': form,
        'target_user': target_user,
        'current_user_type': current_user_type,
        'target_user_type': target_user_type
    }
    return render(request, 'create_mentor_investor_connection.html', context)

@login_required
def mentor_investor_connections(request):
    """Vista del dashboard de conexiones"""
    if not hasattr(request.user, 'profile'):
        messages.error(request, 'Tu cuenta no tiene un perfil asociado.')
        return redirect('home')
    
    user_type = request.user.profile.user_type
    
    if user_type not in ['mentor', 'investor', 'entrepreneur']:
        messages.error(request, 'Solo mentores, inversionistas y emprendedores pueden acceder a esta página.')
        return redirect('home')
    
    # Obtener conexiones según el tipo de usuario
    if user_type == 'mentor':
        connections = MentorInvestorConnection.objects.filter(mentor=request.user)
    elif user_type == 'investor':
        connections = MentorInvestorConnection.objects.filter(investor=request.user)
    else:
        connections = MentorInvestorConnection.objects.none()
    
    # Separar por estado
    pending_connections = connections.filter(status='pending')
    active_connections = connections.filter(status='accepted')

    # Mentorias (mentor-emprendedor)
    if user_type == 'mentor':
        mentorships = Mentorship.objects.filter(mentor=request.user)
    elif user_type == 'entrepreneur':
        mentorships = Mentorship.objects.filter(project__owner=request.user)
    else:
        mentorships = Mentorship.objects.none()

    pending_mentorships = mentorships.filter(status='pending')
    active_mentorships = mentorships.filter(status='accepted')
    
    # Estadísticas
    total_connections = active_connections.count() + active_mentorships.count()
    pending_total = pending_connections.count() + pending_mentorships.count()
    unread_messages = 0
    
    for connection in active_connections:
        unread_messages += connection.messages.filter(
            is_read=False
        ).exclude(sender=request.user).count()

    for mentorship in active_mentorships:
        unread_messages += mentorship.messages.filter(
            is_read=False
        ).exclude(sender=request.user).count()
    
    context = {
        'pending_connections': pending_connections,
        'active_connections': active_connections,
        'pending_mentorships': pending_mentorships,
        'active_mentorships': active_mentorships,
        'total_connections': total_connections,
        'pending_total': pending_total,
        'unread_messages': unread_messages,
        'user_type': user_type
    }
    return render(request, 'mentor_investor_connections.html', context)

@login_required
def respond_to_connection_request(request, connection_id, action):
    """Responder a una solicitud de conexión mentor-inversionista"""
    connection = get_object_or_404(MentorInvestorConnection, id=connection_id)
    
    # Verificar que el usuario tenga permiso para responder
    if request.user != connection.mentor and request.user != connection.investor:
        messages.error(request, 'No tienes permiso para responder a esta solicitud.')
        return redirect('mentor_investor_connections')
    
    # El usuario que NO inició la conexión es quien puede responder
    if ((connection.initiated_by == 'mentor' and request.user == connection.mentor) or 
        (connection.initiated_by == 'investor' and request.user == connection.investor)):
        messages.error(request, 'No puedes responder a tu propia solicitud.')
        return redirect('mentor_investor_connections')
    
    if action == 'accept':
        connection.status = 'accepted'
        connection.connected_at = timezone.now()
        connection.save()
        
        # Crear notificación para quien inició la conexión
        initiator = connection.mentor if connection.initiated_by == 'mentor' else connection.investor
        Notification.objects.create(
            user=initiator,
            title='Conexión aceptada',
            message=f'{request.user.username} ha aceptado tu solicitud de conexión.',
            notification_type='system'
        )
        
        messages.success(request, 'Has aceptado la solicitud de conexión.')
        
    elif action == 'reject':
        connection.delete()
        messages.info(request, 'Has rechazado la solicitud de conexión.')
    else:
        messages.error(request, 'Acción no válida.')
    
    return redirect('mentor_investor_connections')

@login_required
def mentor_investor_chat(request, connection_id):
    """Chat entre mentor e inversionista"""
    connection = get_object_or_404(MentorInvestorConnection, id=connection_id)
    
    # Verificar que el usuario tenga acceso al chat
    if request.user != connection.mentor and request.user != connection.investor:
        messages.error(request, 'No tienes permiso para acceder a este chat.')
        return redirect('mentor_investor_connections')
    
    # Verificar que la conexión esté activa
    if connection.status != 'accepted':
        messages.error(request, 'Esta conexión no está activa.')
        return redirect('mentor_investor_connections')
    
    if request.method == 'POST':
        form = MentorInvestorMessageForm(request.POST, user=request.user)
        if form.is_valid():
            message = form.save(commit=False)
            message.connection = connection
            message.sender = request.user
            message.save()
            
            # Actualizar última actividad de la conexión
            connection.last_activity = timezone.now()
            connection.save()
            
            # Crear notificación para el otro usuario
            recipient = connection.get_other_user(request.user)
            Notification.objects.create(
                user=recipient,
                title='Nuevo mensaje',
                message=f'{request.user.username} te ha enviado un mensaje.',
                notification_type='message'
            )
            
            return redirect('mentor_investor_chat', connection_id=connection_id)
    else:
        form = MentorInvestorMessageForm(user=request.user)
    
    # Obtener mensajes del chat
    messages_list = connection.messages.all().order_by('timestamp')
    
    # Marcar mensajes como leídos
    connection.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    # Obtener el otro usuario
    other_user = connection.get_other_user(request.user)
    
    context = {
        'connection': connection,
        'messages': messages_list,
        'form': form,
        'other_user': other_user,
        'current_user_type': request.user.profile.user_type
    }
    return render(request, 'mentor_investor_chat.html', context)

@login_required
def get_mentor_investor_unread_count(request):
    """API para obtener el contador de mensajes no leídos en conexiones mentor-inversionista"""
    if not hasattr(request.user, 'profile'):
        return JsonResponse({'unread_count': 0})
    
    user_type = request.user.profile.user_type
    
    if user_type not in ['mentor', 'investor']:
        return JsonResponse({'unread_count': 0})
    
    # Obtener conexiones activas
    if user_type == 'mentor':
        connections = MentorInvestorConnection.objects.filter(mentor=request.user, status='accepted')
    else:
        connections = MentorInvestorConnection.objects.filter(investor=request.user, status='accepted')
    
    # Contar mensajes no leídos
    unread_count = 0
    for connection in connections:
        unread_count += connection.messages.filter(
            is_read=False
        ).exclude(sender=request.user).count()
    
    return JsonResponse({'unread_count': unread_count})

@login_required
def search_mentor_investor_connections(request):
    """Búsqueda avanzada de conexiones mentor-inversionista"""
    if not hasattr(request.user, 'profile'):
        return redirect('home')
    
    user_type = request.user.profile.user_type
    if user_type not in ['mentor', 'investor']:
        return redirect('home')
    
    form = ConnectionSearchForm(request.GET or None)
    connections = MentorInvestorConnection.objects.none()
    
    if user_type == 'mentor':
        base_connections = MentorInvestorConnection.objects.filter(mentor=request.user, status='accepted')
    else:
        base_connections = MentorInvestorConnection.objects.filter(investor=request.user, status='accepted')
    
    if form.is_valid():
        connections = base_connections
        
        search = form.cleaned_data.get('search')
        if search:
            if user_type == 'mentor':
                connections = connections.filter(
                    Q(investor__username__icontains=search) |
                    Q(investor__first_name__icontains=search) |
                    Q(investor__last_name__icontains=search) |
                    Q(purpose__icontains=search) |
                    Q(investment_interests__icontains=search)
                )
            else:
                connections = connections.filter(
                    Q(mentor__username__icontains=search) |
                    Q(mentor__first_name__icontains=search) |
                    Q(mentor__last_name__icontains=search) |
                    Q(purpose__icontains=search) |
                    Q(expertise_areas__icontains=search)
                )
        
        expertise_area = form.cleaned_data.get('expertise_area')
        if expertise_area:
            connections = connections.filter(expertise_areas__icontains=expertise_area)
        
        sort_by = form.cleaned_data.get('sort_by', '-last_activity')
        connections = connections.order_by(sort_by)
    else:
        connections = base_connections.order_by('-last_activity')
    
    context = {
        'connections': connections,
        'form': form,
        'user_type': user_type
    }
    return render(request, 'search_mentor_investor_connections.html', context)


@login_required
def profile_view(request):
    """Vista para ver y editar el perfil del usuario autenticado."""
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            'user_type': 'entrepreneur',
            'bio': '',
            'experience': '',
        }
    )

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'update_profile':
            user_form = UserEditForm(request.POST, instance=request.user)
            profile_form = ProfileEditForm(request.POST, request.FILES, instance=profile)

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Perfil actualizado exitosamente.')
                return redirect('profile')
            else:
                password_form = PasswordChangeCustomForm(user=request.user)

        elif action == 'change_password':
            password_form = PasswordChangeCustomForm(user=request.user, data=request.POST)
            user_form = UserEditForm(instance=request.user)
            profile_form = ProfileEditForm(instance=profile)

            if password_form.is_valid():
                from django.contrib.auth import update_session_auth_hash
                updated_user = password_form.save()
                update_session_auth_hash(request, updated_user)
                messages.success(request, 'Contraseña cambiada exitosamente.')
                return redirect('profile')
        else:
            user_form = UserEditForm(instance=request.user)
            profile_form = ProfileEditForm(instance=profile)
            password_form = PasswordChangeCustomForm(user=request.user)
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=profile)
        password_form = PasswordChangeCustomForm(user=request.user)

    context = {
        'profile': profile,
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
    }
    return render(request, 'profile.html', context)


# ════════════════════════════════════════════════════════════
# Asistente IA PMI para estructuración de proyectos
# ════════════════════════════════════════════════════════════

PMI_SYSTEM_PROMPT = """
Eres un experto consultor de proyectos que sigue la metodología PMI (Project Management Institute)
adaptada para emprendimientos. Tu misión es guiar al emprendedor paso a paso para estructurar
su idea de negocio de forma sólida, de manera conversacional y amigable.

Eres parte de CrowdMentor, una plataforma que conecta emprendedores con mentores e inversionistas.
Una vez que el emprendedor tenga su proyecto estructurado, podrá publicarlo y recibir mentoría.

GUÍA DE CONVERSACIÓN PMI (sé natural, no robótico):
1. IDEACIÓN: Explora la idea, el nombre tentativo del proyecto.
2. PROBLEMA Y SOLUCIÓN: ¿Qué problema resuelve? ¿Cómo lo resuelve?
3. MERCADO OBJETIVO: ¿A quiénes va dirigido? ¿Cuál es el tamaño del mercado?
4. MODELO DE NEGOCIO: ¿Cómo generará ingresos? ¿Qué te diferencia de la competencia?
5. RECURSOS Y PRESUPUESTO: ¿Cuánto capital inicial se necesita? ¿A qué se destinaría?
6. RIESGOS: ¿Cuáles son los principales riesgos y cómo mitigarlos?
7. CRONOGRAMA: ¿En cuánto tiempo espera ser rentable?
8. RESUMEN FINAL: Cuando tengas información suficiente (después de al menos 6 respuestas del usuario),
   genera un JSON EXACTAMENTE en este formato (sólo cuando el usuario confirme que quiere continuar
   o cuando el tema esté completamente desarrollado):

   <PROJECT_DATA>
   {
     "title": "Título del proyecto",
     "description": "Descripción detallada del proyecto incluyendo problema, solución, mercado y modelo de negocio",
     "tags": "tag1, tag2, tag3",
     "funding_goal": "50000",
     "profitability_time": "18",
     "profitability_unit": "meses"
   }
   </PROJECT_DATA>

IMPORTANTE:
- Haz UNA sola pregunta a la vez.
- Sé alentador y constructivo.
- Si el usuario no tiene clara una fase, ayúdalo con ejemplos o sugerencias.
- Después de cada respuesta del usuario, resume brevemente lo que entendiste y avanza a la siguiente fase.
- El JSON solo debe aparecer cuando hayas recopilado información suficiente de todas las fases.
- Usa Español latinoamericano.
- Mantén respuestas concisas (máximo 150 palabras por respuesta).
"""


def _get_ollama_response(session: AIProjectSession, user_message: str) -> str:
    """Llama a Ollama local y devuelve la respuesta del modelo."""
    base_url = getattr(settings, 'OLLAMA_BASE_URL', 'http://127.0.0.1:11434').rstrip('/')
    model = getattr(settings, 'OLLAMA_MODEL', 'qwen2.5:7b-instruct')
    connect_timeout = int(getattr(settings, 'AI_CONNECT_TIMEOUT_SECONDS', 15))
    read_timeout = int(getattr(settings, 'AI_READ_TIMEOUT_SECONDS', 45))
    total_timeout = max(connect_timeout + read_timeout, 30)

    def _build_payload(last_messages: int, num_predict: int, temperature: float = 0.7) -> dict:
        messages_payload = [{'role': 'system', 'content': PMI_SYSTEM_PROMPT}]
        for msg in session.get_last_n_messages(last_messages):
            role = 'user' if msg['role'] == 'user' else 'assistant'
            messages_payload.append({'role': role, 'content': msg['content']})
        messages_payload.append({'role': 'user', 'content': user_message})
        return {
            'model': model,
            'messages': messages_payload,
            'stream': False,
            'options': {
                'temperature': temperature,
                'num_predict': num_predict,
            },
        }

    try:
        req = urllib_request.Request(
            url=f'{base_url}/api/chat',
            data=json.dumps(_build_payload(last_messages=12, num_predict=260)).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        with urllib_request.urlopen(req, timeout=total_timeout) as response:
            body = response.read().decode('utf-8')
            data = json.loads(body)
            return data.get('message', {}).get('content', '').strip() or (
                '⚠️ El modelo local respondió vacío. Inténtalo de nuevo.'
            )
    except (socket.timeout, TimeoutError):
        # Reintento más liviano para equipos con CPU o memoria limitada.
        try:
            retry_req = urllib_request.Request(
                url=f'{base_url}/api/chat',
                data=json.dumps(_build_payload(last_messages=5, num_predict=110, temperature=0.45)).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST',
            )
            with urllib_request.urlopen(retry_req, timeout=total_timeout) as retry_response:
                retry_body = retry_response.read().decode('utf-8')
                retry_data = json.loads(retry_body)
                return retry_data.get('message', {}).get('content', '').strip() or (
                    '⚠️ El modelo local respondió vacío. Inténtalo de nuevo.'
                )
        except Exception:
            return (
                '⚠️ El modelo local tardó demasiado en responder. '
                'Intenta con una pregunta más corta o vuelve a intentar en unos segundos.'
            )
    except HTTPError as exc:
        return (
            f'⚠️ Error HTTP de Ollama ({exc.code}). '
            'Verifica que el modelo exista y esté cargado. '
            'Mientras tanto, puedes <a href="/project/create/">crear tu proyecto manualmente</a>.'
        )
    except URLError:
        return (
            '⚠️ No se pudo conectar con Ollama local. '
            'Verifica que el servicio esté activo en tu equipo. '
            'Mientras tanto, puedes <a href="/project/create/">crear tu proyecto manualmente</a>.'
        )
    except Exception as exc:
        return f'⚠️ Ocurrió un error al contactar el asistente local: {exc}. Por favor inténtalo de nuevo.'


def _build_gemini_contents(session: AIProjectSession, user_message: str, last_messages: int = 8) -> list[dict]:
    """Convierte el historial a formato de conversación de Gemini."""
    contents = []
    for msg in session.get_last_n_messages(last_messages):
        role = 'user' if msg.get('role') == 'user' else 'model'
        text = (msg.get('content') or '').strip()
        if text:
            contents.append({'role': role, 'parts': [{'text': text}]})

    contents.append({'role': 'user', 'parts': [{'text': user_message}]})
    return contents


def _get_remote_llm_response(session: AIProjectSession, user_message: str) -> str:
    """Backend remoto con Gemini vía API key."""
    api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        return ''

    api_base_url = getattr(settings, 'GEMINI_API_BASE_URL', 'https://generativelanguage.googleapis.com/v1beta/models').rstrip('/')
    model = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash')
    timeout = int(getattr(settings, 'GEMINI_TIMEOUT_SECONDS', 35))

    payload = {
        'system_instruction': {
            'parts': [{'text': PMI_SYSTEM_PROMPT}],
        },
        'contents': _build_gemini_contents(session, user_message, last_messages=8),
        'generationConfig': {
            'temperature': 0.45,
            'maxOutputTokens': 220,
        },
    }

    try:
        req = urllib_request.Request(
            url=f'{api_base_url}/{model}:generateContent?key={api_key}',
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        with urllib_request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode('utf-8')
            data = json.loads(body)
            parts = (
                data.get('candidates', [{}])[0]
                .get('content', {})
                .get('parts', [])
            )
            text = ''.join(part.get('text', '') for part in parts).strip()
            return text
    except Exception:
        return ''


def _build_local_guided_fallback(session: AIProjectSession) -> str:
    """Respuesta local determinística para no bloquear al usuario si no hay motor IA disponible."""
    user_turns = [m for m in session.messages if m.get('role') == 'user']
    n = len(user_turns)

    if n <= 1:
        return (
            '¡Buena base! Para aterrizar tu idea, dime en una frase: '
            '¿qué problema real resuelves y para quién?'
        )
    if n == 2:
        return (
            'Perfecto, ya entendí el problema. Ahora vamos al mercado: '
            '¿quién es tu cliente ideal (edad, perfil o tipo de negocio) y cómo lo contactas hoy?'
        )
    if n == 3:
        return (
            'Vamos bien. Cuéntame tu modelo de ingresos: '
            '¿cómo cobrarás (suscripción, comisión, venta directa) y por qué te elegirán frente a otras opciones?'
        )
    if n == 4:
        return (
            'Siguiente paso: presupuesto inicial. '
            '¿cuánto capital necesitas para arrancar y en qué 3 rubros principales lo invertirías?'
        )
    if n == 5:
        return (
            'Antes del resumen, identifiquemos riesgos: '
            'menciona 2 riesgos clave (comercial, técnico o financiero) y cómo planeas mitigarlos.'
        )
    return (
        'Con lo que tenemos, ya puedes continuar al formulario y pulir detalles finales. '
        'Si quieres, responde con el tiempo estimado para llegar a rentabilidad (ej. 12 meses).'
    )


def _get_ai_response(session: AIProjectSession, user_message: str) -> tuple[str, str]:
    """Responde solo con Gemini. Sin API key o sin respuesta, no genera contenido conversacional."""
    gemini_api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')
    if not gemini_api_key:
        return (
            '⚠️ El asistente IA está deshabilitado porque no hay API key de Gemini configurada. '
            'Configura GEMINI_API_KEY para habilitar respuestas.',
            'gemini-not-configured',
        )

    remote_text = _get_remote_llm_response(session, user_message)
    if remote_text:
        return remote_text, 'gemini'

    return (
        '⚠️ No se pudo obtener respuesta de Gemini en este momento. '
        'Verifica tu API key, modelo o conexión e inténtalo de nuevo.',
        'gemini-error',
    )


def _extract_project_data(ai_text: str) -> dict | None:
    """Extrae el JSON de PROJECT_DATA si está presente en la respuesta."""
    import re, json
    match = re.search(r'<PROJECT_DATA>(.*?)</PROJECT_DATA>', ai_text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(1).strip())
    except (json.JSONDecodeError, ValueError):
        return None


@login_required
def ai_project_assistant(request):
    """Vista principal del asistente IA PMI."""
    try:
        profile = request.user.profile
        if profile.user_type != 'entrepreneur':
            messages.warning(request, 'El asistente de IA está disponible solo para emprendedores.')
            return redirect('dashboard')
    except Profile.DoesNotExist:
        messages.error(request, 'Completa tu perfil primero.')
        return redirect('dashboard')

    if request.method == 'POST' and request.POST.get('action') == 'new_session':
        # Crear nueva sesión
        session = AIProjectSession.objects.create(user=request.user)
        welcome_msg = (
            '¡Hola! Soy tu asistente de proyectos PMI 🚀 \n\n'
            'Estoy aquí para ayudarte a estructurar tu idea de emprendimiento de forma profesional, '
            'siguiendo la metodología PMI (Project Management Institute). \n\n'
            'Al finalizar, tendrás un proyecto bien definido que podrás publicar en CrowdMentor '
            'para conectar con mentores e inversionistas. \n\n'
            '✨ **¿Tienes ya alguna idea de proyecto o negocio en mente?** Cuéntame, aunque sea de '
            'forma muy general — no importa si aún está poco desarrollada.'
        )
        session.add_message('assistant', welcome_msg)
        return redirect('ai_project_assistant_session', session_id=session.pk)

    # Listar sesiones del usuario
    sessions = AIProjectSession.objects.filter(user=request.user)
    return render(request, 'ai_project_assistant.html', {'sessions': sessions})


@login_required
def ai_project_assistant_session(request, session_id):
    """Vista de una sesión del asistente IA."""
    session = get_object_or_404(AIProjectSession, pk=session_id, user=request.user)

    if request.method == 'POST':
        import json as json_module
        data = json_module.loads(request.body.decode('utf-8'))
        user_message = data.get('message', '').strip()

        if not user_message:
            return JsonResponse({'error': 'Mensaje vacío'}, status=400)

        if session.status != 'active':
            return JsonResponse({'error': 'La sesión ya fue cerrada.'}, status=400)

        # Guardar mensaje del usuario
        session.add_message('user', user_message)

        # Obtener respuesta IA con estrategia de fallback.
        ai_response, response_backend = _get_ai_response(session, user_message)

        # Verificar si hay datos de proyecto generados
        project_data = _extract_project_data(ai_response)

        # Limpiar el texto de la respuesta (quitar bloque JSON)
        import re
        clean_response = re.sub(r'<PROJECT_DATA>.*?</PROJECT_DATA>', '', ai_response, flags=re.DOTALL).strip()
        if not clean_response:
            clean_response = '✅ ¡Excelente! He estructurado tu proyecto. Pulsa **“Crear Proyecto”** para continuar.'

        session.add_message('assistant', clean_response)

        response_payload = {'message': clean_response, 'project_data': None, 'backend': response_backend}

        if project_data:
            session.generated_title = project_data.get('title', '')
            session.generated_description = project_data.get('description', '')
            session.generated_tags = project_data.get('tags', '')
            session.generated_funding_goal = project_data.get('funding_goal', '')
            session.generated_profitability_time = project_data.get('profitability_time', '')
            session.generated_profitability_unit = project_data.get('profitability_unit', 'meses')
            session.current_phase = 'summary'
            session.save(update_fields=[
                'generated_title', 'generated_description', 'generated_tags',
                'generated_funding_goal', 'generated_profitability_time',
                'generated_profitability_unit', 'current_phase'
            ])
            response_payload['project_data'] = project_data

        return JsonResponse(response_payload)

    return render(request, 'ai_project_assistant_session.html', {'session': session})


@login_required
def ai_project_use_data(request, session_id):
    """Redirige al formulario de creación de proyecto pre-llenado con los datos de la IA."""
    session = get_object_or_404(AIProjectSession, pk=session_id, user=request.user)
    if not session.generated_title:
        messages.warning(request, 'La sesión no tiene datos generados todavía.')
        return redirect('ai_project_assistant_session', session_id=session_id)

    # Pasar datos como parámetros GET al formulario de creación
    from urllib.parse import urlencode
    params = urlencode({
        'ai_session': session_id,
        'title': session.generated_title,
        'description': session.generated_description,
        'tags': session.generated_tags,
        'funding_goal': session.generated_funding_goal,
        'profitability_time': session.generated_profitability_time,
        'profitability_unit': session.generated_profitability_unit,
    })
    return redirect(f'/project/create/?{params}')


@login_required  
def ai_project_session_delete(request, session_id):
    """Elimina una sesión de IA."""
    session = get_object_or_404(AIProjectSession, pk=session_id, user=request.user)
    if request.method == 'POST':
        session.delete()
        messages.success(request, 'Sesión eliminada.')
        return redirect('ai_project_assistant')
    return redirect('ai_project_assistant')


# ─────────────────────────────────────────────────────────────
# Contratos de inversión
# ─────────────────────────────────────────────────────────────

@login_required
def view_investment_contract(request, contract_id):
    """Muestra el contrato de inversión para impresión."""
    from .models import InvestmentContract
    contract = get_object_or_404(InvestmentContract, id=contract_id)
    investment = contract.investment

    # Solo el emprendedor o el inversionista pueden ver el contrato
    if request.user != investment.project.owner and request.user != investment.investor:
        messages.error(request, 'No tienes permiso para ver este contrato.')
        return redirect('dashboard')

    investor_amount = investment.amount or Decimal('0')
    investor_percentage = Decimal(str(investment.equity_percentage or 0))
    funding_goal = investment.project.funding_goal or Decimal('0')

    # El porcentaje del inversionista aplica sobre lo que invirtio.
    investor_profit = (investor_amount * investor_percentage / Decimal('100')).quantize(
        Decimal('0.01'),
        rounding=ROUND_HALF_UP,
    )
    investor_total_return = (investor_amount + investor_profit).quantize(
        Decimal('0.01'),
        rounding=ROUND_HALF_UP,
    )

    # Comision de la plataforma sobre la meta de financiacion del proyecto.
    platform_percentage = Decimal('10.00')
    platform_amount = (funding_goal * platform_percentage / Decimal('100')).quantize(
        Decimal('0.01'),
        rounding=ROUND_HALF_UP,
    )

    return render(request, 'investment_contract.html', {
        'contract': contract,
        'investment': investment,
        'investor_profit': investor_profit,
        'investor_total_return': investor_total_return,
        'platform_percentage': platform_percentage,
        'platform_amount': platform_amount,
    })


@login_required
def upload_signed_contract(request, contract_id):
    """Permite al inversionista subir el contrato firmado."""
    from .models import InvestmentContract
    contract = get_object_or_404(InvestmentContract, id=contract_id)
    investment = contract.investment

    # Solo el inversionista puede subir el contrato firmado
    if request.user != investment.investor:
        messages.error(request, 'Solo el inversionista puede subir el contrato firmado.')
        return redirect('dashboard')

    if request.method == 'POST':
        signed_file = request.FILES.get('signed_document')
        if not signed_file:
            messages.error(request, 'Por favor selecciona un archivo.')
            return render(request, 'upload_signed_contract.html', {'contract': contract})

        # Validar tamaño (máx. 10 MB)
        if signed_file.size > 10 * 1024 * 1024:
            messages.error(request, 'El archivo no puede superar 10 MB.')
            return render(request, 'upload_signed_contract.html', {'contract': contract})

        # Validar extensión
        allowed_ext = {'.pdf', '.jpg', '.jpeg', '.png'}
        import os
        ext = os.path.splitext(signed_file.name)[1].lower()
        if ext not in allowed_ext:
            messages.error(request, 'Formato no permitido. Usa PDF, JPG o PNG.')
            return render(request, 'upload_signed_contract.html', {'contract': contract})

        contract.signed_document = signed_file
        contract.status = 'signed_uploaded'
        contract.signed_at = timezone.now()
        contract.save()

        # Notificar al emprendedor
        Notification.objects.create(
            user=investment.project.owner,
            title='Contrato firmado recibido',
            message=(
                f'{investment.investor.username} ha subido el contrato firmado '
                f'para la inversión en "{investment.project.title}".'
            ),
            notification_type='investment',
            related_project=investment.project,
            related_investment=investment,
        )

        messages.success(request, '¡Contrato firmado subido correctamente! El emprendedor ha sido notificado.')
        return redirect('dashboard')

    return render(request, 'upload_signed_contract.html', {'contract': contract})