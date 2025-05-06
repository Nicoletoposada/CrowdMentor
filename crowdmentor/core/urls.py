# core/urls.py
from django.urls import path # type: ignore
from . import views
from django.contrib.auth import views as auth_views # type: ignore
from .views import LogoutView, manage_investment
from .views import request_mentorship_by_mentor, request_mentorship_by_entrepreneur, respond_to_mentorship_request

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('projects/', views.project_list, name='project_list'),
    path('project/<int:pk>/', views.project_detail, name='project_detail'),
    path('project/create/', views.project_create, name='project_create'),
    path('approve_mentor/<int:profile_id>/', views.approve_mentor, name='approve_mentor'),
    path('approve_evaluator/<int:user_id>/', views.approve_evaluator, name='approve_evaluator'),
    path('reject_evaluator/<int:user_id>/', views.reject_evaluator, name='reject_evaluator'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('delete_project/<int:project_id>/', views.delete_project, name='delete_project'),
    path('manage_investment/<int:investment_id>/', manage_investment, name='manage_investment'),
    path('mentorship/request-by-mentor/<int:project_id>/', views.request_mentorship_by_mentor, name='request_mentorship_by_mentor'),
    path('mentorship/request-by-entrepreneur/<int:mentor_id>/', views.request_mentorship_by_entrepreneur, name='request_mentorship_by_entrepreneur'),
    path('mentorship/respond/<int:mentorship_id>/<str:action>/', views.respond_to_mentorship_request, name='respond_to_mentorship_request'),
    path('mentors/', views.mentor_list, name='mentor_list'),
    path('projects-for-mentors/', views.project_list_for_mentors, name='project_list_for_mentors'),
    path('mentorship/chat/<int:mentorship_id>/', views.mentorship_chat, name='mentorship_chat'),
    path('mentorship/mark-read/<int:mentorship_id>/', views.mark_messages_as_read, name='mark_messages_as_read'),
    path('mentorship/unread-count/', views.get_unread_messages_count, name='get_unread_messages_count'),
]