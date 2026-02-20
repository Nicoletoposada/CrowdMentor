# Script para eliminar recursos específicos

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowdmentor.settings')
django.setup()

from core.models import Resource

# Recursos a eliminar
recursos_a_eliminar = [
    "Plantillas Canva - Negocios",
    "Business Model Canvas - Strategyzer",
    "Business Model Canvas Explicado en Español"
]

print("="*70)
print("ELIMINANDO RECURSOS ESPECÍFICOS")
print("="*70)

for titulo in recursos_a_eliminar:
    try:
        recurso = Resource.objects.get(title=titulo)
        recurso.delete()
        print(f"✓ Eliminado: {titulo}")
    except Resource.DoesNotExist:
        print(f"⚠️ No encontrado: {titulo}")

print("\n" + "="*70)
print("✅ Eliminación completada")
print(f"📊 Total de recursos: {Resource.objects.count()}")
print("="*70)
