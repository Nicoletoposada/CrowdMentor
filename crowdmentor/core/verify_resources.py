#!/usr/bin/env python
"""
Script de verificación del sistema de recursos
"""
import os
import sys
import django

# Configurar el path para que Django pueda encontrar el módulo
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowdmentor.settings')
django.setup()

from core.models import ResourceCategory, Resource
from django.contrib.auth.models import User

def verify_system():
    print("🔍 Verificando el sistema de gestión de recursos...")
    print("=" * 50)
    
    # Verificar modelos
    print(f"📂 Categorías en la base de datos: {ResourceCategory.objects.count()}")
    print(f"📄 Recursos en la base de datos: {Resource.objects.count()}")
    
    # Mostrar categorías
    print("\n📋 Categorías disponibles:")
    for category in ResourceCategory.objects.all():
        resource_count = category.resources.count()
        print(f"  • {category.name} ({resource_count} recursos) - {category.icon}")
    
    # Mostrar recursos destacados
    featured_resources = Resource.objects.filter(is_featured=True)
    print(f"\n⭐ Recursos destacados: {featured_resources.count()}")
    for resource in featured_resources:
        print(f"  • {resource.title} ({resource.category.name})")
    
    # Verificar usuario admin
    try:
        admin_user = User.objects.get(username='admin')
        print(f"\n👤 Usuario administrador encontrado: {admin_user.username}")
        print(f"   📧 Email: {admin_user.email}")
        print(f"   🔑 Es superusuario: {admin_user.is_superuser}")
    except User.DoesNotExist:
        print("\n❌ No se encontró el usuario administrador 'admin'")
        print("   Ejecuta: python manage.py createsuperuser")
    
    # URLs importantes
    print("\n🔗 URLs importantes:")
    print("   🏠 Home: http://127.0.0.1:8000/")
    print("   📚 Recursos públicos: http://127.0.0.1:8000/resources/")
    print("   ⚙️  Panel admin: http://127.0.0.1:8000/admin_dashboard/")
    print("   🗂️  Gestión recursos: http://127.0.0.1:8000/manage-resources/")
    print("   🔧 Django Admin: http://127.0.0.1:8000/admin/")
    
    print("\n✅ Verificación completada!")
    print("\n💡 Para probar el sistema:")
    print("   1. Accede al panel de administración")
    print("   2. Inicia sesión como administrador")
    print("   3. Ve a 'Gestionar Recursos'")
    print("   4. Crea categorías y recursos")
    print("   5. Verifica en la página pública de recursos")

if __name__ == '__main__':
    verify_system()