# Archivo: core/initialize_resources.py
# Script para inicializar recursos de ejemplo

import os
import sys
import django

# Configurar el path para que Django pueda encontrar el módulo
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowdmentor.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import ResourceCategory, Resource

def create_sample_data():
    # Crear usuario administrador si no existe
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@crowdmentor.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("Usuario administrador creado: admin / admin123")

    # Crear categorías de ejemplo
    categories_data = [
        {
            'name': 'Plantillas y Documentos',
            'description': 'Plantillas descargables para planes de negocio, pitch decks y documentos legales',
            'icon': 'fas fa-file-alt'
        },
        {
            'name': 'Artículos y Guías',
            'description': 'Artículos educativos y guías paso a paso para emprendedores',
            'icon': 'fas fa-book-open'
        },
        {
            'name': 'Herramientas Recomendadas',
            'description': 'Herramientas digitales útiles para gestionar y hacer crecer tu negocio',
            'icon': 'fas fa-tools'
        },
        {
            'name': 'Videos y Webinars',
            'description': 'Contenido audiovisual educativo sobre emprendimiento',
            'icon': 'fas fa-video'
        }
    ]

    created_categories = []
    for cat_data in categories_data:
        category, created = ResourceCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'description': cat_data['description'],
                'icon': cat_data['icon']
            }
        )
        created_categories.append(category)
        if created:
            print(f"Categoría creada: {category.name}")

    # Crear recursos de ejemplo
    resources_data = [
        # Plantillas y Documentos
        {
            'title': 'Plantilla de Plan de Negocio',
            'description': 'Plantilla completa en formato Word para crear tu plan de negocio. Incluye todas las secciones necesarias con ejemplos y guías.',
            'resource_type': 'template',
            'category': created_categories[0],
            'url': 'https://docs.google.com/document/d/example-business-plan',
            'icon': 'fas fa-file-word',
            'is_featured': True
        },
        {
            'title': 'Plantilla de Pitch Deck',
            'description': 'Presentación PowerPoint profesional para presentar tu proyecto a inversionistas. Diseño moderno y estructura probada.',
            'resource_type': 'template',
            'category': created_categories[0],
            'url': 'https://docs.google.com/presentation/d/example-pitch-deck',
            'icon': 'fas fa-file-powerpoint'
        },
        {
            'title': 'Modelo Financiero Excel',
            'description': 'Hoja de cálculo avanzada para proyecciones financieras, análisis de punto de equilibrio y planificación presupuestaria.',
            'resource_type': 'template',
            'category': created_categories[0],
            'url': 'https://docs.google.com/spreadsheets/d/example-financial-model',
            'icon': 'fas fa-file-excel'
        },
        
        # Artículos y Guías
        {
            'title': 'Cómo validar tu idea de negocio',
            'description': 'Guía completa para validar tu idea antes de invertir tiempo y dinero. Metodología lean startup y técnicas de investigación de mercado.',
            'resource_type': 'guide',
            'category': created_categories[1],
            'url': 'https://medium.com/@crowdmentor/como-validar-tu-idea-de-negocio',
            'icon': 'fas fa-lightbulb',
            'is_featured': True
        },
        {
            'title': 'Marketing Digital para Startups',
            'description': 'Estrategias de marketing digital efectivas y de bajo costo para startups. SEO, redes sociales, content marketing y más.',
            'resource_type': 'guide',
            'category': created_categories[1],
            'url': 'https://blog.crowdmentor.com/marketing-digital-startups',
            'icon': 'fas fa-bullhorn'
        },
        {
            'title': 'Aspectos Legales para Emprendedores',
            'description': 'Todo lo que necesitas saber sobre constitución de empresas, contratos, propiedad intelectual y aspectos legales básicos.',
            'resource_type': 'guide',
            'category': created_categories[1],
            'url': 'https://blog.crowdmentor.com/aspectos-legales-emprendedores',
            'icon': 'fas fa-balance-scale'
        },
        
        # Herramientas Recomendadas
        {
            'title': 'Canva - Diseño Gráfico',
            'description': 'Herramienta online para crear diseños profesionales sin conocimientos de diseño. Ideal para presentaciones, logos y marketing.',
            'resource_type': 'tool',
            'category': created_categories[2],
            'url': 'https://www.canva.com/',
            'icon': 'fas fa-paint-brush'
        },
        {
            'title': 'Trello - Gestión de Proyectos',
            'description': 'Organiza tus proyectos y tareas de manera visual. Colaboración en equipo y seguimiento de progreso simplificado.',
            'resource_type': 'tool',
            'category': created_categories[2],
            'url': 'https://trello.com/',
            'icon': 'fas fa-tasks'
        },
        {
            'title': 'Google Workspace',
            'description': 'Suite completa de herramientas de productividad: Gmail, Drive, Docs, Sheets, Slides. Colaboración en tiempo real.',
            'resource_type': 'tool',
            'category': created_categories[2],
            'url': 'https://workspace.google.com/',
            'icon': 'fas fa-cloud'
        },
        
        # Videos y Webinars
        {
            'title': 'Finanzas para Emprendedores',
            'description': 'Webinar sobre conceptos financieros básicos que todo emprendedor debe conocer. Flujo de caja, ROI, y métricas clave.',
            'resource_type': 'video',
            'category': created_categories[3],
            'url': 'https://youtube.com/watch?v=ejemplo-finanzas',
            'icon': 'fas fa-play-circle',
            'is_featured': True
        },
        {
            'title': 'Cómo hacer un Pitch Efectivo',
            'description': 'Video tutorial sobre cómo presentar tu proyecto de manera convincente. Técnicas de presentación y storytelling.',
            'resource_type': 'video',
            'category': created_categories[3],
            'url': 'https://youtube.com/watch?v=ejemplo-pitch',
            'icon': 'fas fa-chalkboard-teacher'
        }
    ]

    for res_data in resources_data:
        resource, created = Resource.objects.get_or_create(
            title=res_data['title'],
            defaults={
                'description': res_data['description'],
                'resource_type': res_data['resource_type'],
                'category': res_data['category'],
                'url': res_data['url'],
                'icon': res_data['icon'],
                'is_featured': res_data.get('is_featured', False),
                'created_by': admin_user
            }
        )
        if created:
            print(f"Recurso creado: {resource.title}")

    print("\n✅ Datos de ejemplo creados exitosamente!")
    print("📋 Categorías: 4")
    print("📄 Recursos: 11")
    print(f"\n🔗 Accede al panel de administración de recursos:")
    print(f"   http://127.0.0.1:8000/manage-resources/")

if __name__ == "__main__":
    create_sample_data()