"""
conftest.py — Configuración de pytest para CrowdMentor
=======================================================
Permite ejecutar los tests con:
  pytest                        (descubre todos los tests)
  pytest core/tests.py -v       (solo tests de core)
  pytest -k "TestProjectModel"  (filtrar por clase)
  pytest -k "test_str"          (filtrar por nombre de test)

Requiere:  pip install pytest pytest-django
"""
import django
from django.conf import settings  # type: ignore


def pytest_configure():
    """Configura Django antes de que pytest comience a recolectar tests."""
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowdmentor.settings')
    django.setup()
