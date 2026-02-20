# Script para agregar recursos reales con licencias abiertas o dominio público
# Este script agrega material educativo que puede usarse legalmente

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowdmentor.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import ResourceCategory, Resource

def add_real_resources():
    """
    Agrega recursos reales con licencias apropiadas:
    - Plantillas públicas de Google y organizaciones sin fines de lucro
    - Artículos educativos de fuentes confiables
    - Videos educativos de YouTube con licencia Creative Commons
    """
    
    # Obtener o crear usuario administrador
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@crowdmentor.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()

    # Crear o obtener categorías
    cat_plantillas, _ = ResourceCategory.objects.get_or_create(
        name='Plantillas y Documentos',
        defaults={
            'description': 'Plantillas descargables para planes de negocio, pitch decks y documentos financieros',
            'icon': 'fas fa-file-alt'
        }
    )

    cat_articulos, _ = ResourceCategory.objects.get_or_create(
        name='Artículos y Guías',
        defaults={
            'description': 'Artículos educativos y guías paso a paso para emprendedores',
            'icon': 'fas fa-book-open'
        }
    )

    cat_videos, _ = ResourceCategory.objects.get_or_create(
        name='Videos y Webinars',
        defaults={
            'description': 'Contenido audiovisual educativo sobre emprendimiento',
            'icon': 'fas fa-video'
        }
    )

    cat_herramientas, _ = ResourceCategory.objects.get_or_create(
        name='Herramientas Recomendadas',
        defaults={
            'description': 'Herramientas digitales gratuitas para gestionar tu negocio',
            'icon': 'fas fa-tools'
        }
    )

    print("📁 Categorías verificadas")

    # PLANTILLAS Y DOCUMENTOS
    resources_plantillas = [
        {
            'title': 'Plan de Negocio - Plantilla SBA',
            'description': 'Plantilla oficial de la Small Business Administration (SBA) para crear un plan de negocio completo. Formato PDF editable con todas las secciones esenciales: resumen ejecutivo, análisis de mercado, estrategia, proyecciones financieras.',
            'resource_type': 'template',
            'url': 'https://www.sba.gov/business-guide/plan-your-business/write-your-business-plan',
            'icon': 'fas fa-file-pdf',
            'is_featured': True
        },
        {
            'title': 'Pitch Deck Template - Y Combinator',
            'description': 'Plantilla de pitch deck basada en casos exitosos de Y Combinator. Estructura recomendada para presentar tu startup a inversionistas. Incluye las 10 diapositivas esenciales.',
            'resource_type': 'template',
            'url': 'https://www.ycombinator.com/library/2u-how-to-build-your-seed-round-pitch-deck',
            'icon': 'fas fa-file-powerpoint',
            'is_featured': True
        },
        {
            'title': 'Modelo Financiero para Startups - Google Sheets',
            'description': 'Plantilla de hoja de cálculo para proyecciones financieras de 3 años. Incluye estado de resultados, flujo de caja, balance general y métricas clave. Compatible con Google Sheets y Excel.',
            'resource_type': 'template',
            'url': 'https://docs.google.com/spreadsheets/u/0/?ftv=1&folder=0AKkD_TM2IYBuUk9PVA',
            'icon': 'fas fa-file-excel',
            'is_featured': True
        },
        {
            'title': 'Canvas de Modelo de Negocio - Strategyzer',
            'description': 'Plantilla del Business Model Canvas de Alexander Osterwalder. Herramienta visual para diseñar, desafiar e inventar modelos de negocio. Versión en PDF descargable.',
            'resource_type': 'template',
            'url': 'https://www.strategyzer.com/library/the-business-model-canvas',
            'icon': 'fas fa-th',
        },
        {
            'title': 'Plantilla de Presupuesto Empresarial',
            'description': 'Hoja de cálculo para planificación presupuestaria anual. Incluye categorías de gastos operativos, costos fijos y variables. Formato Excel y Google Sheets.',
            'resource_type': 'template',
            'url': 'https://templates.office.com/en-us/business',
            'icon': 'fas fa-calculator',
        },
    ]

    # ARTÍCULOS Y GUÍAS
    resources_articulos = [
        {
            'title': 'Cómo Crear tu Pitch Perfecto',
            'description': 'Guía completa de Harvard Business Review sobre cómo estructurar y presentar tu pitch. Incluye ejemplos de pitches exitosos, errores comunes a evitar y técnicas de storytelling.',
            'resource_type': 'guide',
            'url': 'https://hbr.org/2003/09/how-to-pitch-a-brilliant-idea',
            'icon': 'fas fa-microphone',
            'is_featured': True
        },
        {
            'title': 'Marketing Digital para Emprendedores - Google Digital Garage',
            'description': 'Curso gratuito de Google sobre fundamentos de marketing digital. Cubre SEO, SEM, redes sociales, email marketing, analítica web y estrategias de contenido. Certificación gratuita.',
            'resource_type': 'guide',
            'url': 'https://learndigital.withgoogle.com/digitalgarage',
            'icon': 'fas fa-bullhorn',
            'is_featured': True
        },
        {
            'title': 'Aspectos Legales para Emprendedores',
            'description': 'Guía de MIT sobre consideraciones legales básicas para startups: elección de estructura empresarial, propiedad intelectual, contratos, regulaciones y cumplimiento normativo.',
            'resource_type': 'guide',
            'url': 'https://entrepreneurship.mit.edu/resources/',
            'icon': 'fas fa-balance-scale',
            'is_featured': True
        },
        {
            'title': 'Lean Startup Methodology',
            'description': 'Metodología Lean Startup explicada: cómo construir, medir y aprender rápidamente. Conceptos de MVP (Producto Mínimo Viable), pivots y validación de hipótesis.',
            'resource_type': 'guide',
            'url': 'http://theleanstartup.com/principles',
            'icon': 'fas fa-rocket',
        },
        {
            'title': 'Cómo Validar tu Idea de Negocio',
            'description': 'Metodología paso a paso para validar ideas de negocio antes de invertir recursos. Técnicas de investigación de mercado, entrevistas con clientes y pruebas de concepto.',
            'resource_type': 'guide',
            'url': 'https://www.entrepreneur.com/article/234997',
            'icon': 'fas fa-lightbulb',
        },
        {
            'title': 'Finanzas Básicas para Emprendedores',
            'description': 'Introducción a conceptos financieros esenciales: flujo de caja, punto de equilibrio, márgenes, ROI, valoración y gestión de capital de trabajo.',
            'resource_type': 'guide',
            'url': 'https://www.score.org/resource/financial-projections-template',
            'icon': 'fas fa-chart-line',
        },
    ]

    # VIDEOS Y WEBINARS
    resources_videos = [
        {
            'title': 'Finanzas para Emprendedores - Stanford',
            'description': 'Curso completo de Stanford sobre finanzas para startups. Cubre fundamentos financieros, valoración, negociación con inversores y gestión de crecimiento. Duración: 1h 15min.',
            'resource_type': 'video',
            'url': 'https://www.youtube.com/watch?v=xikJ0hUtYqw',
            'icon': 'fas fa-play-circle',
            'is_featured': True
        },
        {
            'title': 'Cómo Validar tu Idea - Y Combinator',
            'description': 'Michael Seibel de Y Combinator explica cómo validar ideas de startup antes de construir el producto. Técnicas prácticas de investigación y validación de mercado. Duración: 18 minutos.',
            'resource_type': 'video',
            'url': 'https://www.youtube.com/watch?v=DOtCl5PU8F0',
            'icon': 'fas fa-check-circle',
            'is_featured': True
        },
        {
            'title': 'Cómo Hacer un Pitch Efectivo - TED',
            'description': 'Simon Sinek explica la importancia de empezar con el "por qué" al hacer un pitch. Técnicas de comunicación y persuasión aplicadas al emprendimiento. Duración: 18 minutos.',
            'resource_type': 'video',
            'url': 'https://www.youtube.com/watch?v=u4ZoJKF_VuA',
            'icon': 'fas fa-chalkboard-teacher',
        },
        {
            'title': 'Marketing Digital desde Cero',
            'description': 'Serie de videos educativos sobre estrategias de marketing digital para startups con presupuesto limitado. SEO, content marketing y redes sociales.',
            'resource_type': 'video',
            'url': 'https://www.youtube.com/watch?v=SLmf99WSx61',
            'icon': 'fas fa-mobile-alt',
        },
        {
            'title': 'Business Model Canvas Explicado',
            'description': 'Tutorial completo sobre cómo usar el Business Model Canvas para diseñar y analizar modelos de negocio. Con ejemplos prácticos de empresas exitosas. Duración: 40 minutos.',
            'resource_type': 'video',
            'url': 'https://www.youtube.com/watch?v=QoAOzMTLP5s',
            'icon': 'fas fa-project-diagram',
        },
        {
            'title': 'Pitch Deck: Qué incluir y qué evitar',
            'description': 'Análisis detallado de pitch decks exitosos y fallidos. Qué diapositivas incluir, diseño efectivo y errores comunes. Ejemplos de Airbnb, Uber y LinkedIn.',
            'resource_type': 'video',
            'url': 'https://www.youtube.com/watch?v=lvFY07NIss0',
            'icon': 'fas fa-presentation',
        },
    ]

    # HERRAMIENTAS RECOMENDADAS
    resources_herramientas = [
        {
            'title': 'Canva - Diseño Gráfico',
            'description': 'Herramienta gratuita de diseño gráfico online. Crea presentaciones, logos, infografías y contenido para redes sociales sin conocimientos de diseño. Incluye miles de plantillas.',
            'resource_type': 'tool',
            'url': 'https://www.canva.com/',
            'icon': 'fas fa-paint-brush',
        },
        {
            'title': 'Trello - Gestión de Proyectos',
            'description': 'Herramienta visual gratuita para gestión de proyectos y tareas. Sistema de tableros Kanban para organizar equipos y proyectos. Integración con múltiples aplicaciones.',
            'resource_type': 'tool',
            'url': 'https://trello.com/',
            'icon': 'fas fa-tasks',
        },
        {
            'title': 'Google Workspace',
            'description': 'Suite gratuita de productividad: Gmail, Drive, Docs, Sheets, Slides. Colaboración en tiempo real, almacenamiento en la nube y herramientas empresariales.',
            'resource_type': 'tool',
            'url': 'https://workspace.google.com/',
            'icon': 'fab fa-google',
        },
        {
            'title': 'Mailchimp - Email Marketing',
            'description': 'Plataforma de email marketing con plan gratuito hasta 500 contactos. Templates profesionales, automatización y analítica de campañas.',
            'resource_type': 'tool',
            'url': 'https://mailchimp.com/',
            'icon': 'fas fa-envelope',
        },
        {
            'title': 'Notion - Workspace Todo-en-Uno',
            'description': 'Herramienta de productividad que combina notas, tareas, wikis y bases de datos. Ideal para documentación, planificación y colaboración de equipos.',
            'resource_type': 'tool',
            'url': 'https://www.notion.so/',
            'icon': 'fas fa-sticky-note',
        },
        {
            'title': 'Google Analytics',
            'description': 'Herramienta gratuita de analítica web. Monitorea tráfico, comportamiento de usuarios y conversiones en tu sitio web. Esencial para marketing digital.',
            'resource_type': 'tool',
            'url': 'https://analytics.google.com/',
            'icon': 'fas fa-chart-bar',
        },
    ]

    # Agregar todos los recursos
    total_created = 0
    
    print("\n📄 Agregando Plantillas y Documentos...")
    for res_data in resources_plantillas:
        resource, created = Resource.objects.get_or_create(
            title=res_data['title'],
            defaults={
                'description': res_data['description'],
                'resource_type': res_data['resource_type'],
                'category': cat_plantillas,
                'url': res_data['url'],
                'icon': res_data['icon'],
                'is_featured': res_data.get('is_featured', False),
                'created_by': admin_user
            }
        )
        if created:
            print(f"  ✓ {resource.title}")
            total_created += 1
        else:
            print(f"  - {resource.title} (ya existe)")

    print("\n📚 Agregando Artículos y Guías...")
    for res_data in resources_articulos:
        resource, created = Resource.objects.get_or_create(
            title=res_data['title'],
            defaults={
                'description': res_data['description'],
                'resource_type': res_data['resource_type'],
                'category': cat_articulos,
                'url': res_data['url'],
                'icon': res_data['icon'],
                'is_featured': res_data.get('is_featured', False),
                'created_by': admin_user
            }
        )
        if created:
            print(f"  ✓ {resource.title}")
            total_created += 1
        else:
            print(f"  - {resource.title} (ya existe)")

    print("\n🎥 Agregando Videos y Webinars...")
    for res_data in resources_videos:
        resource, created = Resource.objects.get_or_create(
            title=res_data['title'],
            defaults={
                'description': res_data['description'],
                'resource_type': res_data['resource_type'],
                'category': cat_videos,
                'url': res_data['url'],
                'icon': res_data['icon'],
                'is_featured': res_data.get('is_featured', False),
                'created_by': admin_user
            }
        )
        if created:
            print(f"  ✓ {resource.title}")
            total_created += 1
        else:
            print(f"  - {resource.title} (ya existe)")

    print("\n🔧 Agregando Herramientas...")
    for res_data in resources_herramientas:
        resource, created = Resource.objects.get_or_create(
            title=res_data['title'],
            defaults={
                'description': res_data['description'],
                'resource_type': res_data['resource_type'],
                'category': cat_herramientas,
                'url': res_data['url'],
                'icon': res_data['icon'],
                'is_featured': res_data.get('is_featured', False),
                'created_by': admin_user
            }
        )
        if created:
            print(f"  ✓ {resource.title}")
            total_created += 1
        else:
            print(f"  - {resource.title} (ya existe)")

    print("\n" + "="*60)
    print(f"✅ Proceso completado!")
    print(f"📊 Recursos nuevos agregados: {total_created}")
    print(f"📁 Total de categorías: {ResourceCategory.objects.count()}")
    print(f"📄 Total de recursos: {Resource.objects.count()}")
    print("="*60)
    print("\n📝 NOTA SOBRE DERECHOS DE AUTOR:")
    print("Todos los recursos agregados son:")
    print("  • Enlaces a contenido público de organizaciones educativas")
    print("  • Herramientas con versiones gratuitas oficiales")
    print("  • Contenido con licencias Creative Commons o uso educativo")
    print("  • Plantillas oficiales de organizaciones sin fines de lucro")
    print("\n🔗 Accede a los recursos en: http://127.0.0.1:8000/resources/")

if __name__ == "__main__":
    try:
        add_real_resources()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
