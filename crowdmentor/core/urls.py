# core/urls.py
from django.urls import path # type: ignore
from . import views
from django.contrib.auth import views as auth_views # type: ignore
from .views import LogoutView, manage_investment, login_view, resources
from .views import request_mentorship_by_mentor, request_mentorship_by_entrepreneur, respond_to_mentorship_request

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('projects/', views.project_list, name='project_list'),
    path('project/<int:pk>/', views.project_detail, name='project_detail'),
    path('project/create/', views.project_create, name='project_create'),
    path('approve_mentor/<int:profile_id>/', views.approve_mentor, name='approve_mentor'),
    path('approve_evaluator/<int:user_id>/', views.approve_evaluator, name='approve_evaluator'),
    path('reject_evaluator/<int:user_id>/', views.reject_evaluator, name='reject_evaluator'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('delete_project/<int:project_id>/', views.delete_project, name='delete_project'),
    path('toggle_project_active/<int:project_id>/', views.toggle_project_active, name='toggle_project_active'),
    path('toggle_user_active/<int:user_id>/', views.toggle_user_active, name='toggle_user_active'),
    path('admin_toggle_investment/<int:investment_id>/', views.admin_toggle_investment, name='admin_toggle_investment'),
    path('manage_investment/<int:investment_id>/', manage_investment, name='manage_investment'),
    path('mentorship/request-by-mentor/<int:project_id>/', views.request_mentorship_by_mentor, name='request_mentorship_by_mentor'),
    path('mentorship/request-by-entrepreneur/<int:mentor_id>/', views.request_mentorship_by_entrepreneur, name='request_mentorship_by_entrepreneur'),
    path('mentorship/respond/<int:mentorship_id>/<str:action>/', views.respond_to_mentorship_request, name='respond_to_mentorship_request'),
    path('mentors/', views.mentor_list, name='mentor_list'),
    path('projects-for-mentors/', views.project_list_for_mentors, name='project_list_for_mentors'),
    path('mentorship/chat/<int:mentorship_id>/', views.mentorship_chat, name='mentorship_chat'),
    path('mentorship/mark-read/<int:mentorship_id>/', views.mark_messages_as_read, name='mark_messages_as_read'),
    path('mentorship/unread-count/', views.get_unread_messages_count, name='get_unread_messages_count'),
    path('resources/', resources, name='resources'),
    
    # URLs para administración de recursos
    path('manage-resources/', views.admin_resources, name='admin_resources'),
    path('manage-resources/category/create/', views.create_resource_category, name='create_resource_category'),
    path('manage-resources/category/<int:category_id>/edit/', views.edit_resource_category, name='edit_resource_category'),
    path('manage-resources/category/<int:category_id>/delete/', views.delete_resource_category, name='delete_resource_category'),
    path('manage-resources/create/', views.create_resource, name='create_resource'),
    path('manage-resources/<int:resource_id>/edit/', views.edit_resource, name='edit_resource'),
    path('manage-resources/<int:resource_id>/delete/', views.delete_resource, name='delete_resource'),
    path('manage-resources/<int:resource_id>/toggle-status/', views.toggle_resource_status, name='toggle_resource_status'),
    path('manage-resources/<int:resource_id>/toggle-featured/', views.toggle_resource_featured, name='toggle_resource_featured'),
    
    # URLs para evaluaciones y analíticas
    path('project/<int:project_id>/evaluate/', views.evaluate_project, name='evaluate_project'),
    path('project/<int:project_id>/like/', views.like_project, name='like_project'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/count/', views.get_notifications_count, name='get_notifications_count'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('analytics/report/', views.analytics_report, name='analytics_report'),
    path('mis-metricas/emprendedor/', views.entrepreneur_metrics, name='entrepreneur_metrics'),
    path('mis-metricas/emprendedor/reporte/', views.entrepreneur_report, name='entrepreneur_report'),
    path('mis-metricas/inversionista/', views.investor_metrics, name='investor_metrics'),
    path('mis-metricas/inversionista/reporte/', views.investor_report, name='investor_report'),
    path('mis-metricas/mentor/', views.mentor_metrics, name='mentor_metrics'),
    path('mis-metricas/mentor/reporte/', views.mentor_report, name='mentor_report'),
    
    # URLs para sistema mentor-inversionista
    path('investors/', views.investor_list_for_mentors, name='investor_list_for_mentors'),
    path('mentors-for-investors/', views.mentor_list_for_investors, name='mentor_list_for_investors'),
    path('connect/<int:target_user_id>/', views.create_mentor_investor_connection, name='create_mentor_investor_connection'),
    path('connections/', views.mentor_investor_connections, name='mentor_investor_connections'),
    path('connections/<int:connection_id>/<str:action>/', views.respond_to_connection_request, name='respond_to_connection_request'),
    path('connections/chat/<int:connection_id>/', views.mentor_investor_chat, name='mentor_investor_chat'),
    path('connections/unread-count/', views.get_mentor_investor_unread_count, name='get_mentor_investor_unread_count'),
    path('connections/search/', views.search_mentor_investor_connections, name='search_mentor_investor_connections'),

    # ── Asistente IA PMI para estructuración de proyectos ──
    path('ai-assistant/', views.ai_project_assistant, name='ai_project_assistant'),
    path('ai-assistant/<int:session_id>/', views.ai_project_assistant_session, name='ai_project_assistant_session'),
    path('ai-assistant/<int:session_id>/chat/', views.ai_project_assistant_session, name='ai_project_chat'),
    path('ai-assistant/<int:session_id>/use/', views.ai_project_use_data, name='ai_project_use_data'),
    path('ai-assistant/<int:session_id>/delete/', views.ai_project_session_delete, name='ai_project_session_delete'),
]