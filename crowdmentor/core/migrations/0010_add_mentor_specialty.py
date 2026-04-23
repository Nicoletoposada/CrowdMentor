from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_investment_contract'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='mentor_specialty',
            field=models.CharField(
                blank=True,
                choices=[
                    ('agronomy', 'Agronomía y Proyectos Agropecuarios'),
                    ('technology', 'Tecnología e Innovación'),
                    ('finance', 'Finanzas y Negocios'),
                    ('health', 'Salud y Bienestar'),
                    ('marketing', 'Marketing y Ventas'),
                    ('legal', 'Legal y Cumplimiento'),
                    ('education', 'Educación'),
                    ('manufacturing', 'Manufactura e Industria'),
                    ('environment', 'Medio Ambiente y Sostenibilidad'),
                    ('arts', 'Arte y Entretenimiento'),
                    ('other', 'Otra especialidad'),
                ],
                max_length=50,
                null=True,
                verbose_name='Especialidad (Mentor)',
            ),
        ),
    ]
