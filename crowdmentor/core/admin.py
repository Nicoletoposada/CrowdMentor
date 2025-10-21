from django.contrib import admin # type: ignore
from .models import Profile, Project, Investment, Mentorship, Message, ResourceCategory, Resource

# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'is_approved', 'is_approved_by_admin']
    list_filter = ['user_type', 'is_approved', 'is_approved_by_admin']
    search_fields = ['user__username', 'user__email']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'funding_goal', 'amount_raised', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'owner__username']

@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ['project', 'investor', 'amount', 'status', 'invested_at']
    list_filter = ['status', 'invested_at']
    search_fields = ['project__title', 'investor__username']

@admin.register(Mentorship)
class MentorshipAdmin(admin.ModelAdmin):
    list_display = ['project', 'mentor', 'status', 'initiated_by', 'assigned_at']
    list_filter = ['status', 'initiated_by', 'assigned_at']
    search_fields = ['project__title', 'mentor__username']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['mentorship', 'sender', 'timestamp', 'is_read']
    list_filter = ['is_read', 'timestamp']
    search_fields = ['sender__username', 'content']

@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'icon', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'name': ('name',)}

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'resource_type', 'category', 'is_active', 'is_featured', 'created_by', 'created_at']
    list_filter = ['resource_type', 'category', 'is_active', 'is_featured', 'created_at']
    search_fields = ['title', 'description', 'category__name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'description', 'resource_type', 'category')
        }),
        ('Contenido', {
            'fields': ('file', 'url')
        }),
        ('Configuración', {
            'fields': ('icon', 'is_active', 'is_featured')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
