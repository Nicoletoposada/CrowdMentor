import sys

# Verificar que el servidor solo se inicie con 'runserver'
if 'runserver' not in sys.argv:
    raise RuntimeError("El servidor solo puede ejecutarse con 'python manage.py runserver'")