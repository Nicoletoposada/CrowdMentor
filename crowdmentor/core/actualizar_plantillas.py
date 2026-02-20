# Script para actualizar recursos de plantillas
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowdmentor.settings')
django.setup()

from core.models import Resource

# Eliminar los 3 recursos viejos
recursos_a_eliminar = [
    "Plantillas Excel - Microsoft Office",
    "Plantillas PowerPoint - Microsoft Office",
]

print("="*70)
print("ACTUALIZANDO RECURSOS DE PLANTILLAS")
print("="*70)

print("\n🗑️  ELIMINANDO RECURSOS VIEJOS:")
for titulo in recursos_a_eliminar:
    try:
        recurso = Resource.objects.get(title=titulo)
        recurso.delete()
        print(f"✓ Eliminado: {titulo}")
    except Resource.DoesNotExist:
        print(f"⚠️ No encontrado: {titulo}")

print("\n📁 AGREGANDO NUEVOS RECURSOS CON URLs VERIFICADAS:")

# Ahora ejecutar el script de recursos verificados
os.system('python core/add_recursos_verificados.py')

print("\n✅ ACTUALIZACIÓN COMPLETADA")
