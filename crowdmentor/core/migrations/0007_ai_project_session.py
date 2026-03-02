# Generated migration for AIProjectSession model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_increase_investment_amount_max_digits'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AIProjectSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(
                    choices=[('active', 'Activa'), ('completed', 'Completada'), ('abandoned', 'Abandonada')],
                    default='active', max_length=20)),
                ('messages', models.JSONField(default=list)),
                ('generated_title', models.CharField(blank=True, max_length=200)),
                ('generated_description', models.TextField(blank=True)),
                ('generated_tags', models.CharField(blank=True, max_length=500)),
                ('generated_funding_goal', models.CharField(blank=True, max_length=50)),
                ('generated_profitability_time', models.CharField(blank=True, max_length=20)),
                ('generated_profitability_unit', models.CharField(blank=True, default='meses', max_length=10)),
                ('current_phase', models.CharField(default='welcome', max_length=20)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='ai_project_sessions',
                    to=settings.AUTH_USER_MODEL)),
                ('resulting_project', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='ai_session',
                    to='core.project')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
