# Script para agregar recursos en ESPAÑOL con licencias abiertas
# Recursos educativos en español de fuentes confiables

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowdmentor.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import ResourceCategory, Resource

def limpiar_recursos_existentes():
    """Elimina recursos existentes para reemplazarlos con versiones en español"""
    count = Resource.objects.all().count()
    if count > 0:
        respuesta = input(f"Se encontraron {count} recursos. ¿Desea eliminarlos y reemplazarlos con recursos en español? (s/n): ")
        if respuesta.lower() == 's':
            Resource.objects.all().delete()
            print(f"✓ {count} recursos eliminados")
            return True
        else:
            print("Operación cancelada")
            return False
    return True

def add_recursos_espanol():
    """
    Agrega recursos educativos en ESPAÑOL con licencias apropiadas
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

    # PLANTILLAS Y DOCUMENTOS EN ESPAÑOL
    resources_plantillas = [
        {
            'title': 'Plantilla Plan de Negocio - OEPM España',
            'description': 'Plantilla oficial de la Oficina Española de Patentes y Marcas para elaborar un plan de negocio completo. Incluye todas las secciones: resumen ejecutivo, análisis de mercado, plan operativo, financiero y de marketing.',
            'resource_type': 'template',
            'url': 'https://www.oepm.es/es/index.html',
            'icon': 'fas fa-file-pdf',
            'is_featured': True
        },
        {
            'title': 'Modelo Canvas - Emprendedores.es',
            'description': 'Lienzo del Modelo de Negocio (Business Model Canvas) en español. Herramienta visual para diseñar, analizar y pivotar tu modelo de negocio. Formato descargable en PDF y editable.',
            'resource_type': 'template',
            'url': 'https://www.emprendedores.es/gestion/modelo-canvas/',
            'icon': 'fas fa-th',
            'is_featured': True
        },
        {
            'title': 'Plantilla Financiera para Startups',
            'description': 'Modelo financiero en Excel para proyecciones a 3-5 años. Incluye: estado de resultados, flujo de caja, balance, análisis de punto de equilibrio y métricas clave. Compatible con Google Sheets.',
            'resource_type': 'template',
            'url': 'https://docs.google.com/spreadsheets/u/0/?ftv=1&folder=0AKkD_TM2IYBuUk9PVA',
            'icon': 'fas fa-file-excel',
            'is_featured': True
        },
        {
            'title': 'Plantilla Pitch Deck en Español',
            'description': 'Presentación profesional para presentar tu startup a inversores. 10-15 diapositivas con estructura probada: problema, solución, mercado, producto, tracción, equipo, financiación.',
            'resource_type': 'template',
            'url': 'https://www.canva.com/es_mx/plantillas/presentaciones/pitch/',
            'icon': 'fas fa-file-powerpoint',
        },
        {
            'title': 'Contrato de Confidencialidad (NDA)',
            'description': 'Modelo de acuerdo de confidencialidad en español para proteger tu información empresarial. Personalizable según las necesidades de tu proyecto.',
            'resource_type': 'template',
            'url': 'https://www.emprendedores.es/gestion/acuerdo-confidencialidad-nda/',
            'icon': 'fas fa-file-contract',
        },
    ]

    # ARTÍCULOS Y GUÍAS EN ESPAÑOL
    resources_articulos = [
        {
            'title': 'Cómo Hacer un Pitch Perfecto',
            'description': 'Guía completa en español sobre cómo estructurar y presentar tu elevator pitch. Técnicas de storytelling, errores comunes y ejemplos de pitches exitosos de startups latinoamericanas.',
            'resource_type': 'guide',
            'url': 'https://www.emprendedores.es/crear-una-empresa/a23782/como-hacer-pitch-perfecto/',
            'icon': 'fas fa-microphone',
            'is_featured': True
        },
        {
            'title': 'Marketing Digital - Google Actívate',
            'description': 'Curso gratuito de Google en español sobre fundamentos de marketing digital. Certificación oficial: SEO, SEM, redes sociales, analítica web, email marketing y estrategia de contenidos.',
            'resource_type': 'guide',
            'url': 'https://grow.google/intl/es/courses-and-tools/',
            'icon': 'fas fa-bullhorn',
            'is_featured': True
        },
        {
            'title': 'Validación de Ideas de Negocio',
            'description': 'Metodología paso a paso para validar tu idea antes de invertir recursos. Técnicas de Lean Startup, entrevistas con clientes, MVP (Producto Mínimo Viable) y pruebas de concepto.',
            'resource_type': 'guide',
            'url': 'https://www.emprendedores.es/crear-una-empresa/validar-idea-negocio/',
            'icon': 'fas fa-lightbulb',
            'is_featured': True
        },
        {
            'title': 'Aspectos Legales para Emprendedores',
            'description': 'Guía legal básica en español: tipos de sociedades, constitución de empresas, contratos esenciales, propiedad intelectual, protección de datos y obligaciones fiscales.',
            'resource_type': 'guide',
            'url': 'https://www.emprendedores.es/gestion/aspectos-legales-crear-empresa/',
            'icon': 'fas fa-balance-scale',
        },
        {
            'title': 'Finanzas para Emprendedores',
            'description': 'Conceptos financieros esenciales explicados en español: flujo de caja, punto de equilibrio, ROI, valoración de startups, márgenes, gestión de capital y métricas clave.',
            'resource_type': 'guide',
            'url': 'https://www.emprendedores.es/gestion/finanzas-basicas-emprendedores/',
            'icon': 'fas fa-chart-line',
        },
        {
            'title': 'Estrategias de Crecimiento para Startups',
            'description': 'Tácticas de growth hacking, marketing de crecimiento y escalamiento de startups. Casos de éxito de empresas latinoamericanas y españolas.',
            'resource_type': 'guide',
            'url': 'https://www.emprendedores.es/gestion/estrategias-crecimiento-startup/',
            'icon': 'fas fa-rocket',
        },
    ]

    # VIDEOS Y WEBINARS EN ESPAÑOL
    resources_videos = [
        {
            'title': 'Cómo Validar tu Idea de Negocio',
            'description': 'Video tutorial completo en español sobre validación de ideas usando metodología Lean Startup. Aprende a hacer entrevistas con clientes y crear MVPs efectivos. Duración: 25 minutos.',
            'resource_type': 'video',
            'url': 'https://www.youtube.com/watch?v=k1W1guccVDI',
            'icon': 'fas fa-play-circle',
            'is_featured': True
        },
        {
            'title': 'Finanzas para Emprendedores - Curso Completo',
            'description': 'Curso en español sobre finanzas básicas para startups. Cubre: estados financieros, flujo de caja, proyecciones, valoración y métricas financieras clave. Duración: 1 hora.',
            'resource_type': 'video',
            'url': 'https://www.youtube.com/watch?v=QCUHZKts-O0',
            'icon': 'fas fa-calculator',
            'is_featured': True
        },
        {
            'title': 'Cómo Hacer un Pitch de Inversión',
            'description': 'Masterclass en español sobre cómo presentar tu startup a inversores. Estructura del pitch deck, storytelling, manejo de objeciones y cierre. Con ejemplos reales. Duración: 40 minutos.',
            'resource_type': 'video',
            'url': 'https://www.youtube.com/watch?v=xvnEAQ0P1hY',
            'icon': 'fas fa-chalkboard-teacher',
            'is_featured': True
        },
        {
            'title': 'Marketing Digital para Startups',
            'description': 'Serie de videos en español sobre estrategias de marketing digital con bajo presupuesto. SEO, content marketing, redes sociales y publicidad digital efectiva.',
            'resource_type': 'video',
            'url': 'https://www.youtube.com/watch?v=_Vn-WGSqE9g',
            'icon': 'fas fa-mobile-alt',
        },
        {
            'title': 'Business Model Canvas Explicado',
            'description': 'Tutorial completo en español del lienzo de modelo de negocio. Cómo completar cada bloque con ejemplos prácticos de empresas exitosas. Duración: 35 minutos.',
            'resource_type': 'video',
            'url': 'https://www.youtube.com/watch?v=iSxn1FF8V7Y',
            'icon': 'fas fa-project-diagram',
        },
        {
            'title': 'Lean Startup - Metodología Completa',
            'description': 'Explicación detallada de la metodología Lean Startup en español. Build-Measure-Learn, pivots, validated learning y casos de éxito latinoamericanos.',
            'resource_type': 'video',
            'url': 'https://www.youtube.com/watch?v=TlFMBJGjc6M',
            'icon': 'fas fa-sync',
        },
    ]

    # HERRAMIENTAS RECOMENDADAS (EN ESPAÑOL)
    resources_herramientas = [
        {
            'title': 'Canva - Diseño Gráfico (Español)',
            'description': 'Herramienta de diseño gráfico online con interfaz en español. Crea presentaciones, logos, infografías y contenido para redes sociales. Miles de plantillas gratuitas.',
            'resource_type': 'tool',
            'url': 'https://www.canva.com/es_mx/',
            'icon': 'fas fa-paint-brush',
        },
        {
            'title': 'Trello - Gestión de Proyectos (Español)',
            'description': 'Sistema Kanban visual para organizar proyectos y equipos. Interfaz en español, colaboración en tiempo real, integraciones con múltiples apps. Plan gratuito disponible.',
            'resource_type': 'tool',
            'url': 'https://trello.com/es',
            'icon': 'fas fa-tasks',
        },
        {
            'title': 'Google Workspace (Español)',
            'description': 'Suite de productividad de Google en español: Gmail, Drive, Docs, Sheets, Slides, Meet. Colaboración en tiempo real y almacenamiento en la nube.',
            'resource_type': 'tool',
            'url': 'https://workspace.google.com/intl/es/',
            'icon': 'fab fa-google',
        },
        {
            'title': 'Mailchimp (Español)',
            'description': 'Plataforma de email marketing con interfaz en español. Plan gratuito hasta 500 contactos. Templates, automatización, analítica de campañas y landing pages.',
            'resource_type': 'tool',
            'url': 'https://mailchimp.com/es/',
            'icon': 'fas fa-envelope',
        },
        {
            'title': 'Notion (Español)',
            'description': 'Workspace colaborativo en español que combina notas, tareas, wikis y bases de datos. Ideal para documentación, gestión de proyectos y colaboración de equipos.',
            'resource_type': 'tool',
            'url': 'https://www.notion.so/es-es',
            'icon': 'fas fa-sticky-note',
        },
        {
            'title': 'Google Analytics (Español)',
            'description': 'Herramienta gratuita de analítica web en español. Monitorea tráfico, comportamiento de usuarios, conversiones y rendimiento de tu sitio web o app.',
            'resource_type': 'tool',
            'url': 'https://analytics.google.com/analytics/web/?hl=es',
            'icon': 'fas fa-chart-bar',
        },
        {
            'title': 'HubSpot CRM (Español)',
            'description': 'CRM gratuito en español para gestionar contactos, leads y pipeline de ventas. Incluye automatización de marketing y seguimiento de interacciones con clientes.',
            'resource_type': 'tool',
            'url': 'https://www.hubspot.es/products/crm',
            'icon': 'fas fa-users',
        },
    ]

    # Agregar todos los recursos
    total_created = 0
    
    print("\n📄 Agregando Plantillas y Documentos en Español...")
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
            # Actualizar si ya existe
            resource.description = res_data['description']
            resource.url = res_data['url']
            resource.icon = res_data['icon']
            resource.is_featured = res_data.get('is_featured', False)
            resource.save()
            print(f"  ↻ {resource.title} (actualizado)")

    print("\n📚 Agregando Artículos y Guías en Español...")
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
            resource.description = res_data['description']
            resource.url = res_data['url']
            resource.icon = res_data['icon']
            resource.is_featured = res_data.get('is_featured', False)
            resource.save()
            print(f"  ↻ {resource.title} (actualizado)")

    print("\n🎥 Agregando Videos y Webinars en Español...")
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
            resource.description = res_data['description']
            resource.url = res_data['url']
            resource.icon = res_data['icon']
            resource.is_featured = res_data.get('is_featured', False)
            resource.save()
            print(f"  ↻ {resource.title} (actualizado)")

    print("\n🔧 Agregando Herramientas en Español...")
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
            resource.description = res_data['description']
            resource.url = res_data['url']
            resource.icon = res_data['icon']
            resource.is_featured = res_data.get('is_featured', False)
            resource.save()
            print(f"  ↻ {resource.title} (actualizado)")

    print("\n" + "="*70)
    print(f"✅ Proceso completado!")
    print(f"📊 Recursos nuevos: {total_created}")
    print(f"📁 Total de categorías: {ResourceCategory.objects.count()}")
    print(f"📄 Total de recursos: {Resource.objects.count()}")
    print("="*70)
    print("\n📝 NOTA SOBRE DERECHOS DE AUTOR:")
    print("Todos los recursos en español agregados son:")
    print("  • Enlaces a contenido público de organizaciones hispanohablantes")
    print("  • Herramientas oficiales con versiones en español")
    print("  • Contenido educativo de acceso libre")
    print("  • Videos públicos de YouTube en español")
    print("\n🌐 Fuentes incluidas:")
    print("  • Emprendedores.es (portal líder en español)")
    print("  • Google Actívate (formación gratuita en español)")
    print("  • YouTube (contenido educativo en español)")
    print("  • Herramientas SaaS oficiales (versiones en español)")
    print("\n🔗 Accede a los recursos: http://127.0.0.1:8000/resources/")

if __name__ == "__main__":
    print("="*70)
    print("AGREGANDO RECURSOS EN ESPAÑOL")
    print("="*70)
    print()
    
    try:
        # Preguntar si desea limpiar recursos existentes
        if limpiar_recursos_existentes():
            add_recursos_espanol()
        else:
            print("\n⚠️ Operación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
