"""
GUÍA RÁPIDA: Cómo Agregar Recursos Adicionales
==============================================

Este script de ejemplo muestra cómo agregar nuevos recursos fácilmente.
Copia y modifica según tus necesidades.
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


def agregar_recurso_simple(
    titulo,
    descripcion,
    url,
    categoria_nombre,
    tipo_recurso='link',
    es_destacado=False,
    icono='fas fa-link'
):
    """
    Función helper para agregar un recurso rápidamente.
    
    Parámetros:
    -----------
    titulo : str
        Título del recurso
    descripcion : str
        Descripción detallada
    url : str
        URL del recurso externo
    categoria_nombre : str
        Nombre de la categoría (debe existir)
    tipo_recurso : str
        Opciones: 'document', 'link', 'video', 'tool', 'template', 'guide'
    es_destacado : bool
        Si el recurso debe aparecer destacado
    icono : str
        Clase de Font Awesome para el icono
    """
    
    # Obtener usuario admin
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ Error: No hay usuario administrador")
        return None
    
    # Obtener la categoría
    try:
        categoria = ResourceCategory.objects.get(name=categoria_nombre)
    except ResourceCategory.DoesNotExist:
        print(f"❌ Error: La categoría '{categoria_nombre}' no existe")
        print(f"Categorías disponibles: {list(ResourceCategory.objects.values_list('name', flat=True))}")
        return None
    
    # Crear el recurso
    recurso, created = Resource.objects.get_or_create(
        title=titulo,
        defaults={
            'description': descripcion,
            'resource_type': tipo_recurso,
            'category': categoria,
            'url': url,
            'icon': icono,
            'is_featured': es_destacado,
            'created_by': admin_user
        }
    )
    
    if created:
        print(f"✅ Recurso creado: {titulo}")
    else:
        print(f"ℹ️ El recurso '{titulo}' ya existe")
    
    return recurso


def crear_categoria(nombre, descripcion, icono='fas fa-folder'):
    """
    Crear una nueva categoría de recursos.
    
    Parámetros:
    -----------
    nombre : str
        Nombre de la categoría
    descripcion : str
        Descripción de la categoría
    icono : str
        Clase de Font Awesome para el icono
    """
    categoria, created = ResourceCategory.objects.get_or_create(
        name=nombre,
        defaults={
            'description': descripcion,
            'icon': icono
        }
    )
    
    if created:
        print(f"✅ Categoría creada: {nombre}")
    else:
        print(f"ℹ️ La categoría '{nombre}' ya existe")
    
    return categoria


# ==============================================================================
# EJEMPLOS DE USO
# ==============================================================================

def ejemplos():
    """
    Ejemplos de cómo agregar diferentes tipos de recursos.
    Descomenta los que necesites usar.
    """
    
    # -------------------------------------------------------------------------
    # EJEMPLO 1: Agregar una plantilla
    # -------------------------------------------------------------------------
    # agregar_recurso_simple(
    #     titulo="Plantilla de Contrato de Cofundadores",
    #     descripcion="Plantilla legal para formalizar acuerdos entre cofundadores de startups.",
    #     url="https://ejemplo.com/plantilla-cofundadores",
    #     categoria_nombre="Plantillas y Documentos",
    #     tipo_recurso='template',
    #     es_destacado=True,
    #     icono='fas fa-file-contract'
    # )
    
    # -------------------------------------------------------------------------
    # EJEMPLO 2: Agregar un artículo/guía
    # -------------------------------------------------------------------------
    # agregar_recurso_simple(
    #     titulo="Guía de User Research",
    #     descripcion="Cómo realizar investigación de usuarios efectiva para tu producto.",
    #     url="https://ejemplo.com/user-research-guide",
    #     categoria_nombre="Artículos y Guías",
    #     tipo_recurso='guide',
    #     es_destacado=False,
    #     icono='fas fa-users'
    # )
    
    # -------------------------------------------------------------------------
    # EJEMPLO 3: Agregar un video
    # -------------------------------------------------------------------------
    # agregar_recurso_simple(
    #     titulo="Product-Market Fit Explicado",
    #     descripcion="Video tutorial sobre cómo encontrar y validar product-market fit.",
    #     url="https://youtube.com/watch?v=ejemplo123",
    #     categoria_nombre="Videos y Webinars",
    #     tipo_recurso='video',
    #     es_destacado=True,
    #     icono='fas fa-play-circle'
    # )
    
    # -------------------------------------------------------------------------
    # EJEMPLO 4: Agregar una herramienta
    # -------------------------------------------------------------------------
    # agregar_recurso_simple(
    #     titulo="Figma - Diseño UI/UX",
    #     descripcion="Herramienta colaborativa de diseño de interfaces. Plan gratuito disponible.",
    #     url="https://www.figma.com/",
    #     categoria_nombre="Herramientas Recomendadas",
    #     tipo_recurso='tool',
    #     es_destacado=False,
    #     icono='fas fa-pen-nib'
    # )
    
    # -------------------------------------------------------------------------
    # EJEMPLO 5: Crear una nueva categoría y agregar recursos
    # -------------------------------------------------------------------------
    # # Primero crear la categoría
    # crear_categoria(
    #     nombre="Podcasts y Entrevistas",
    #     descripcion="Podcasts y entrevistas con emprendedores exitosos",
    #     icono='fas fa-podcast'
    # )
    # 
    # # Luego agregar recursos a esa categoría
    # agregar_recurso_simple(
    #     titulo="Podcast: Cómo Escalar tu Startup",
    #     descripcion="Entrevista con fundadores que escalaron sus startups exitosamente.",
    #     url="https://ejemplo.com/podcast-scaling",
    #     categoria_nombre="Podcasts y Entrevistas",
    #     tipo_recurso='link',
    #     icono='fas fa-microphone'
    # )
    
    pass


# ==============================================================================
# ICONOS DE FONT AWESOME ÚTILES
# ==============================================================================
"""
Documentos:
- fas fa-file-pdf
- fas fa-file-word
- fas fa-file-excel
- fas fa-file-powerpoint
- fas fa-file-contract
- fas fa-file-invoice

Educación:
- fas fa-book
- fas fa-book-open
- fas fa-graduation-cap
- fas fa-chalkboard-teacher
- fas fa-university

Multimedia:
- fas fa-video
- fas fa-play-circle
- fas fa-film
- fas fa-podcast
- fas fa-microphone

Herramientas:
- fas fa-tools
- fas fa-cog
- fas fa-wrench
- fas fa-hammer

Negocio:
- fas fa-chart-line
- fas fa-briefcase
- fas fa-handshake
- fas fa-lightbulb
- fas fa-rocket

Comunicación:
- fas fa-comments
- fas fa-envelope
- fas fa-paper-plane

Diseño:
- fas fa-paint-brush
- fas fa-palette
- fas fa-pen-nib

Tecnología:
- fas fa-laptop-code
- fas fa-code
- fas fa-server
- fas fa-database

Ver más en: https://fontawesome.com/icons
"""


# ==============================================================================
# CHECKLIST LEGAL ANTES DE AGREGAR UN RECURSO
# ==============================================================================
"""
Antes de agregar un recurso, verifica:

✅ ¿Es un ENLACE y no una copia del contenido?
✅ ¿El contenido es público y accesible sin login?
✅ ¿Tiene una licencia apropiada? (Creative Commons, dominio público, etc.)
✅ ¿Es de una fuente confiable? (universidad, organización sin fines de lucro, etc.)
✅ ¿Incluyes atribución si es requerida?
✅ ¿El enlace funciona correctamente?

❌ NO agregues:
❌ Copias de PDFs con copyright
❌ Contenido privado o pagado
❌ Materiales sin permiso explícito
❌ Enlaces a sitios de piratería
"""


# ==============================================================================
# EJECUTAR SCRIPT
# ==============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("AGREGAR RECURSOS PERSONALIZADOS")
    print("=" * 70)
    print()
    
    # Descomentar para ejecutar ejemplos
    # ejemplos()
    
    # O agregar tus propios recursos aquí:
    
    # AGREGA TUS RECURSOS AQUÍ
    # ------------------------
    
    # agregar_recurso_simple(
    #     titulo="Tu Título Aquí",
    #     descripcion="Tu descripción aquí...",
    #     url="https://...",
    #     categoria_nombre="Plantillas y Documentos",  # o la categoría que prefieras
    #     tipo_recurso='link',  # document, link, video, tool, template, guide
    #     es_destacado=False,
    #     icono='fas fa-link'
    # )
    
    print()
    print("✅ Script ejecutado. Descomenta los ejemplos o agrega tus propios recursos.")
    print()
    print("📊 Estadísticas actuales:")
    print(f"   Categorías: {ResourceCategory.objects.count()}")
    print(f"   Recursos: {Resource.objects.count()}")
    print()
    print("🔗 Ver recursos: http://127.0.0.1:8000/resources/")
    print("🔧 Administrar: http://127.0.0.1:8000/manage-resources/")
    print("=" * 70)
