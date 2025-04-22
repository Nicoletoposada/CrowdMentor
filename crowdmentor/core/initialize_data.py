from django.contrib.auth.models import User # type: ignore
from core.models import Profile, Project

# Crear usuarios de ejemplo
user1 = User.objects.create_user(username='entrepreneur1', password='password123')
user2 = User.objects.create_user(username='mentor1', password='password123')
user3 = User.objects.create_user(username='investor1', password='password123')

# Crear perfiles para los usuarios
Profile.objects.create(user=user1, user_type='entrepreneur', bio='Emprendedor apasionado por la tecnología.')
Profile.objects.create(user=user2, user_type='mentor', bio='Mentor con experiencia en startups.')
Profile.objects.create(user=user3, user_type='investor', bio='Inversionista interesado en proyectos sociales.')

# Crear proyectos de ejemplo
Project.objects.create(
    title='Proyecto de Energía Solar',
    description='Un proyecto para llevar energía solar a comunidades rurales.',
    owner=user1,
    funding_goal=50000.00,
    amount_raised=10000.00
)

Project.objects.create(
    title='Aplicación de Salud Mental',
    description='Una app para brindar apoyo psicológico a jóvenes.',
    owner=user1,
    funding_goal=30000.00,
    amount_raised=5000.00
)

print("Datos de ejemplo creados exitosamente.")

exec(open('core/initialize_data.py').read())