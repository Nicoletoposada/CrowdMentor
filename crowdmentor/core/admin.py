from django.contrib import admin # type: ignore
from django.utils.html import format_html # type: ignore
from .models import Profile, Project, Investment, Mentorship, Message, ResourceCategory, Resource, UploadedFile

# Register your models here.

class UploadedFileInline(admin.TabularInline):
    model = UploadedFile
    extra = 0
    readonly_fields = ['file_preview', 'file', 'description', 'uploaded_at']
    fields = ['file_preview', 'file', 'description', 'uploaded_at']
    can_delete = False

    def file_preview(self, obj):
        if obj.file:
            url = obj.file.url
            name = obj.file.name.split('/')[-1]
            ext = name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'jfif']:
                return format_html('<a href="{}" target="_blank"><img src="{}" style="max-height:80px;max-width:120px;"/></a>', url, url)
            return format_html('<a href="{}" target="_blank">{}</a>', url, name)
        return '-'
    file_preview.short_description = 'Vista previa'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'is_approved', 'is_approved_by_admin', 'num_archivos']
    list_filter = ['user_type', 'is_approved', 'is_approved_by_admin']
    search_fields = ['user__username', 'user__email']
    inlines = [UploadedFileInline]

    def num_archivos(self, obj):
        count = obj.uploaded_files.count()
        return count
    num_archivos.short_description = 'Archivos subidos'

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ['profile', 'file_link', 'description', 'uploaded_at']
    list_filter = ['uploaded_at', 'profile__user_type']
    search_fields = ['profile__user__username', 'description']
    readonly_fields = ['uploaded_at']

    def file_link(self, obj):
        if obj.file:
            url = obj.file.url
            name = obj.file.name.split('/')[-1]
            return format_html('<a href="{}" target="_blank">{}</a>', url, name)
        return '-'
    file_link.short_description = 'Archivo'

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
