"""
Script para agregar recursos exactamente como se especifican en DERECHOS_DE_AUTOR.md
Todos los recursos respetan leyes de derechos de autor y son enlaces a contenido público
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowdmentor.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import ResourceCategory, Resource

def add_recursos_derechos_autor():
    """
    Agrega recursos según documento DERECHOS_DE_AUTOR.md
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

    print("✓ Usuario administrador verificado")

    # Limpiar recursos existentes
    Resource.objects.all().delete()
    print("✓ Recursos anteriores eliminados")

    # =========================================================================
    # CREAR O OBTENER CATEGORÍAS
    # =========================================================================
    
    cat_plantillas, _ = ResourceCategory.objects.get_or_create(
        name='Plantillas y Documentos',
        defaults={
            'description': 'Plantillas gratuitas para planes de negocio, presentaciones y hojas de cálculo',
            'icon': 'fas fa-file-alt'
        }
    )

    cat_articulos, _ = ResourceCategory.objects.get_or_create(
        name='Artículos y Guías',
        defaults={
            'description': 'Artículos educativos y guías de organizaciones reconocidas',
            'icon': 'fas fa-book-open'
        }
    )

    cat_videos, _ = ResourceCategory.objects.get_or_create(
        name='Videos y Webinars',
        defaults={
            'description': 'Contenido audiovisual educativo de universidades y organizaciones',
            'icon': 'fas fa-video'
        }
    )

    cat_herramientas, _ = ResourceCategory.objects.get_or_create(
        name='Herramientas Recomendadas',
        defaults={
            'description': 'Herramientas digitales con versiones gratuitas oficiales',
            'icon': 'fas fa-tools'
        }
    )

    print("📁 Categorías creadas")

    # =========================================================================
    # 1. PLANTILLAS Y DOCUMENTOS
    # =========================================================================
    
    plantillas = [
        {
            'title': 'Plan de Negocio - Plantilla SBA',
            'description': 'Plantilla oficial de la Small Business Administration (SBA) del gobierno de EE.UU. Dominio público según 17 U.S.C. § 105. Libre uso, distribución y modificación para planificación empresarial.',
            'resource_type': 'template',
            'url': 'https://www.sba.gov/business-guide/plan-your-business/write-your-business-plan',
            'icon': 'fas fa-file-contract',
            'is_featured': True
        },
        {
            'title': 'Plantilla de Presentaciones - Google Slides',
            'description': 'Plantillas gratuitas oficiales de Google Slides. Ideales para pitch decks, presentaciones de negocios e informes. Editables en línea sin necesidad de descargas.',
            'resource_type': 'template',
            'url': 'https://slides.google.com/template/pitch',
            'icon': 'fas fa-file-powerpoint',
            'is_featured': True
        },
        {
            'title': 'Plantilla de Hojas de Cálculo - Google Sheets',
            'description': 'Plantillas gratuitas de Google Sheets para modelos financieros, presupuestos, flujo de caja y proyecciones. Perfectas para análisis financiero de startups.',
            'resource_type': 'template',
            'url': 'https://sheets.google.com/',
            'icon': 'fas fa-file-excel',
            'is_featured': True
        },
    ]

    for recurso in plantillas:
        Resource.objects.create(
            title=recurso['title'],
            description=recurso['description'],
            resource_type=recurso['resource_type'],
            category=cat_plantillas,
            url=recurso['url'],
            icon=recurso['icon'],
            is_featured=recurso['is_featured'],
            created_by=admin_user
        )
    
    print(f"✓ {len(plantillas)} plantillas agregadas")

    # =========================================================================
    # 2. ARTÍCULOS Y GUÍAS
    # =========================================================================
    
    articulos = [
        {
            'title': 'Harvard Business Review - Entrepreneurship',
            'description': 'Artículos de Harvard Business Review sobre emprendimiento, estrategia de negocios, innovación y liderazgo. Contenido editorial de una de las publicaciones más respetadas en gestión empresarial.',
            'resource_type': 'guide',
            'url': 'https://hbr.org/topic/entrepreneurship',
            'icon': 'fas fa-graduation-cap',
            'is_featured': True
        },
        {
            'title': 'Google Digital Garage',
            'description': 'Plataforma educativa gratuita de Google con cursos sobre marketing digital, desarrollo web, analítica y emprendimiento digital. Certificaciones gratuitas disponibles.',
            'resource_type': 'guide',
            'url': 'https://learndigital.withgoogle.com/digitalgarage',
            'icon': 'fab fa-google',
            'is_featured': True
        },
        {
            'title': 'MIT Entrepreneurship Center',
            'description': 'Recursos educativos del MIT sobre emprendimiento, innovación tecnológica y creación de startups. Materiales de una de las instituciones líderes en emprendimiento.',
            'resource_type': 'guide',
            'url': 'http://entrepreneurship.mit.edu/',
            'icon': 'fas fa-university',
            'is_featured': True
        },
        {
            'title': 'The Lean Startup Methodology',
            'description': 'Metodología Lean Startup - Principios y recursos sobre desarrollo ágil de productos, validación de hipótesis y construcción iterativa. Conceptos de dominio público para uso educativo.',
            'resource_type': 'guide',
            'url': 'http://theleanstartup.com/',
            'icon': 'fas fa-rocket',
            'is_featured': False
        },
        {
            'title': 'Entrepreneur.com - Guías de Inicio',
            'description': 'Portal Entrepreneur.com con guías prácticas sobre cómo iniciar un negocio, marketing, finanzas y gestión. Artículos editoriales de expertos en emprendimiento.',
            'resource_type': 'guide',
            'url': 'https://www.entrepreneur.com/starting-a-business',
            'icon': 'fas fa-lightbulb',
            'is_featured': False
        },
        {
            'title': 'SCORE - Mentoring and Education',
            'description': 'SCORE es una organización sin fines de lucro que ofrece mentoría gratuita, talleres y recursos para emprendedores. Más de 10,000 voluntarios expertos disponibles.',
            'resource_type': 'guide',
            'url': 'https://www.score.org/',
            'icon': 'fas fa-hands-helping',
            'is_featured': False
        },
    ]

    for recurso in articulos:
        Resource.objects.create(
            title=recurso['title'],
            description=recurso['description'],
            resource_type=recurso['resource_type'],
            category=cat_articulos,
            url=recurso['url'],
            icon=recurso['icon'],
            is_featured=recurso['is_featured'],
            created_by=admin_user
        )
    
    print(f"✓ {len(articulos)} artículos y guías agregados")

    # =========================================================================
    # 3. VIDEOS Y WEBINARS
    # =========================================================================
    
    videos = [
        {
            'title': 'Stanford eCorner - Entrepreneurship Videos',
            'description': 'Colección de videos educativos de Stanford sobre emprendimiento con charlas de fundadores exitosos, profesores y expertos en innovación. Contenido público compartible.',
            'resource_type': 'video',
            'url': 'https://ecorner.stanford.edu/',
            'icon': 'fab fa-youtube',
            'is_featured': True
        },
        {
            'title': 'Y Combinator Startup Library',
            'description': 'Biblioteca de videos de Y Combinator con consejos prácticos de la aceleradora más exitosa del mundo. Incluye charlas de fundadores de Airbnb, Dropbox, Stripe y más.',
            'resource_type': 'video',
            'url': 'https://www.ycombinator.com/library',
            'icon': 'fab fa-youtube',
            'is_featured': True
        },
        {
            'title': 'TED Talks - Business & Entrepreneurship',
            'description': 'TED Talks sobre emprendimiento, innovación y negocios. Licencia Creative Commons BY-NC-ND 4.0. Videos inspiradores de líderes empresariales y emprendedores.',
            'resource_type': 'video',
            'url': 'https://www.ted.com/topics/business',
            'icon': 'fab fa-youtube',
            'is_featured': True
        },
        {
            'title': 'Google for Startups - YouTube Channel',
            'description': 'Canal oficial de YouTube de Google for Startups con webinars, charlas y talleres sobre tecnología, escalamiento y construcción de productos.',
            'resource_type': 'video',
            'url': 'https://www.youtube.com/@GoogleStartups',
            'icon': 'fab fa-youtube',
            'is_featured': False
        },
    ]

    for recurso in videos:
        Resource.objects.create(
            title=recurso['title'],
            description=recurso['description'],
            resource_type=recurso['resource_type'],
            category=cat_videos,
            url=recurso['url'],
            icon=recurso['icon'],
            is_featured=recurso['is_featured'],
            created_by=admin_user
        )
    
    print(f"✓ {len(videos)} videos agregados")

    # =========================================================================
    # 4. HERRAMIENTAS RECOMENDADAS
    # =========================================================================
    
    herramientas = [
        {
            'title': 'Canva - Diseño Gráfico',
            'description': 'Canva ofrece herramientas de diseño gráfico con versión gratuita robusta. Ideal para crear presentaciones, logos, material de marketing y contenido visual profesional.',
            'resource_type': 'tool',
            'url': 'https://www.canva.com/',
            'icon': 'fas fa-palette',
            'is_featured': True
        },
        {
            'title': 'Trello - Gestión de Proyectos',
            'description': 'Trello es una herramienta de gestión visual de proyectos con versión gratuita. Perfecta para organizar tareas, colaborar con equipos y hacer seguimiento de proyectos con tableros Kanban.',
            'resource_type': 'tool',
            'url': 'https://trello.com/',
            'icon': 'fas fa-tasks',
            'is_featured': True
        },
        {
            'title': 'Google Workspace',
            'description': 'Suite de herramientas de productividad de Google: Gmail, Drive, Docs, Sheets, Slides. Versión gratuita con amplia funcionalidad para equipos pequeños y startups.',
            'resource_type': 'tool',
            'url': 'https://workspace.google.com/',
            'icon': 'fab fa-google',
            'is_featured': True
        },
        {
            'title': 'Mailchimp - Email Marketing',
            'description': 'Mailchimp ofrece plataforma de email marketing con plan gratuito para hasta 500 contactos. Ideal para newsletters, campañas de marketing y automatización de emails.',
            'resource_type': 'tool',
            'url': 'https://mailchimp.com/',
            'icon': 'fas fa-envelope',
            'is_featured': False
        },
        {
            'title': 'Notion - Workspace Todo-en-Uno',
            'description': 'Notion es un espacio de trabajo versátil con versión gratuita. Combina notas, bases de datos, wikis y gestión de proyectos en una sola plataforma.',
            'resource_type': 'tool',
            'url': 'https://www.notion.so/',
            'icon': 'fas fa-clipboard',
            'is_featured': True
        },
        {
            'title': 'Google Analytics',
            'description': 'Google Analytics es la herramienta líder en analítica web, completamente gratuita. Esencial para entender el comportamiento de usuarios, tráfico web y optimizar conversiones.',
            'resource_type': 'tool',
            'url': 'https://analytics.google.com/',
            'icon': 'fas fa-chart-line',
            'is_featured': True
        },
    ]

    for recurso in herramientas:
        Resource.objects.create(
            title=recurso['title'],
            description=recurso['description'],
            resource_type=recurso['resource_type'],
            category=cat_herramientas,
            url=recurso['url'],
            icon=recurso['icon'],
            is_featured=recurso['is_featured'],
            created_by=admin_user
        )
    
    print(f"✓ {len(herramientas)} herramientas agregadas")

    # =========================================================================
    # RESUMEN
    # =========================================================================
    
    total = len(plantillas) + len(articulos) + len(videos) + len(herramientas)
    
    print("\n" + "="*60)
    print("✅ RECURSOS AGREGADOS EXITOSAMENTE")
    print("="*60)
    print(f"📝 Plantillas y Documentos: {len(plantillas)}")
    print(f"📚 Artículos y Guías: {len(articulos)}")
    print(f"🎥 Videos y Webinars: {len(videos)}")
    print(f"🛠️  Herramientas: {len(herramientas)}")
    print(f"\n📊 TOTAL DE RECURSOS: {total}")
    print("="*60)
    print("\n💡 Todos los recursos respetan derechos de autor según")
    print("   documento DERECHOS_DE_AUTOR.md")
    print("\n✓ Script ejecutado correctamente")

if __name__ == '__main__':
    print("\n🚀 Iniciando carga de recursos según DERECHOS_DE_AUTOR.md...\n")
    add_recursos_derechos_autor()
