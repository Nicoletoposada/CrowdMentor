#!/usr/bin/env python
"""
Script para inicializar datos de ejemplo en el sistema de evaluación y categorías
"""
import os
import sys
import django

# Configurar Django
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Subir un nivel desde core/ al root
sys.path.insert(0, project_root)  # Insertar al inicio para mayor prioridad
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowdmentor.settings')

# Verificar que podemos importar Django
try:
    import django
    django.setup()
except ImportError as e:
    print(f"Error: No se puede importar Django. {e}")
    print(f"Directorio actual: {current_dir}")
    print(f"Directorio del proyecto: {project_root}")
    print("Asegúrate de que Django esté instalado: pip install django")
    sys.exit(1)

from core.models import ProjectCategory, EvaluationCriteria, Project

def create_project_categories():
    """Crear categorías de proyecto"""
    categories = [
        {
            'name': 'Tecnología',
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
            'name': 'Educación',
            'description': 'Proyectos educativos e innovación en aprendizaje',
            'icon': 'fas fa-graduation-cap'
        },
        {
            'name': 'Fintech',
            'description': 'Tecnología financiera y servicios financieros',
            'icon': 'fas fa-credit-card'
        },
        {
            'name': 'E-commerce',
            'description': 'Comercio electrónico y marketplaces',
            'icon': 'fas fa-shopping-cart'
        },
        {
            'name': 'Social Impact',
            'description': 'Proyectos con impacto social positivo',
            'icon': 'fas fa-hands-helping'
        }
    ]
    
    created_count = 0
    for cat_data in categories:
        category, created = ProjectCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'description': cat_data['description'],
                'icon': cat_data['icon']
            }
        )
        if created:
            created_count += 1
            print(f"✓ Categoría creada: {category.name}")
        else:
            print(f"- Categoría ya existe: {category.name}")
    
    print(f"\n{created_count} categorías nuevas creadas de {len(categories)} totales.\n")

def create_evaluation_criteria():
    """Crear criterios de evaluación"""
    criteria = [
        {
            'name': 'Innovación',
            'description': 'Grado de novedad e innovación de la propuesta',
            'weight': 2.0,
            'max_score': 10
        },
        {
            'name': 'Viabilidad Técnica',
            'description': 'Factibilidad técnica de implementar la solución',
            'weight': 1.5,
            'max_score': 10
        },
        {
            'name': 'Potencial de Mercado',
            'description': 'Tamaño del mercado objetivo y potencial de crecimiento',
            'weight': 2.0,
            'max_score': 10
        },
        {
            'name': 'Equipo',
            'description': 'Competencias y experiencia del equipo emprendedor',
            'weight': 1.5,
            'max_score': 10
        },
        {
            'name': 'Modelo de Negocio',
            'description': 'Claridad y sostenibilidad del modelo de negocio',
            'weight': 1.8,
            'max_score': 10
        },
        {
            'name': 'Impacto Social',
            'description': 'Impacto positivo en la sociedad o medio ambiente',
            'weight': 1.2,
            'max_score': 10
        },
        {
            'name': 'Escalabilidad',
            'description': 'Capacidad de crecer y expandirse a otros mercados',
            'weight': 1.3,
            'max_score': 10
        },
        {
            'name': 'Diferenciación',
            'description': 'Ventaja competitiva frente a soluciones existentes',
            'weight': 1.4,
            'max_score': 10
        }
    ]
    
    created_count = 0
    for crit_data in criteria:
        criterion, created = EvaluationCriteria.objects.get_or_create(
            name=crit_data['name'],
            defaults={
                'description': crit_data['description'],
                'weight': crit_data['weight'],
                'max_score': crit_data['max_score']
            }
        )
        if created:
            created_count += 1
            print(f"✓ Criterio creado: {criterion.name} (peso: {criterion.weight})")
        else:
            print(f"- Criterio ya existe: {criterion.name}")
    
    print(f"\n{created_count} criterios nuevos creados de {len(criteria)} totales.\n")

def update_existing_projects():
    """Actualizar proyectos existentes con datos de ejemplo"""
    projects = Project.objects.all()
    categories = list(ProjectCategory.objects.all())
    
    if not categories:
        print("No hay categorías disponibles. Ejecuta create_project_categories() primero.")
        return
    
    updated_count = 0
    for i, project in enumerate(projects):
        # Asignar categoría
        if not project.category:
            project.category = categories[i % len(categories)]
        
        # Asignar tags de ejemplo
        if not project.tags:
            if 'tech' in project.title.lower() or 'app' in project.title.lower():
                project.tags = 'tecnología, innovación, startup'
            elif 'eco' in project.title.lower() or 'green' in project.title.lower():
                project.tags = 'sostenibilidad, medio ambiente, verde'
            elif 'health' in project.title.lower() or 'salud' in project.title.lower():
                project.tags = 'salud, bienestar, medicina'
            else:
                project.tags = 'emprendimiento, innovación, negocios'
        
        # Asignar vistas y likes aleatorios para demo
        import random
        if project.views_count == 0:
            project.views_count = random.randint(10, 500)
        if project.likes_count == 0:
            project.likes_count = random.randint(1, 50)
        
        project.save()
        updated_count += 1
        print(f"✓ Proyecto actualizado: {project.title}")
    
    print(f"\n{updated_count} proyectos actualizados.\n")

def main():
    print("🚀 Inicializando datos del sistema mejorado de CrowdMentor...\n")
    
    # Crear categorías
    print("📁 Creando categorías de proyecto...")
    create_project_categories()
    
    # Crear criterios de evaluación
    print("⭐ Creando criterios de evaluación...")
    create_evaluation_criteria()
    
    # Actualizar proyectos existentes
    print("🔄 Actualizando proyectos existentes...")
    update_existing_projects()
    
    print("✅ Inicialización completada exitosamente!")
    print("\nAhora puedes:")
    print("- Ver proyectos con categorías y filtros en /projects/")
    print("- Evaluar proyectos en /project/<id>/evaluate/")
    print("- Ver notificaciones en /notifications/")
    print("- Acceder al dashboard de analíticas en /analytics/ (solo admin)")

if __name__ == '__main__':
    main()