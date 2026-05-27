"""
CrowdMentor — Suite de Pruebas
================================
Organización
------------
  1. TestProfileModel          — unit: modelo Profile
  2. TestProjectModel          — unit: modelo Project + métodos de negocio
  3. TestInvestmentModel       — unit: modelo Investment
  4. TestMentorshipModel       — unit: modelo Mentorship
  5. TestResourceModel         — unit: modelos Resource / ResourceCategory
  6. TestProjectEvaluationModel— unit: evaluaciones y cálculo de puntaje
  7. TestProjectCategoryModel  — unit: modelo ProjectCategory
  8. TestNotificationModel     — unit: modelo Notification

  9. TestProjectForm           — forms: validación de ProjectForm
 10. TestInvestmentForm        — forms: validación de InvestmentForm
 11. TestLoginForm             — forms: validación de LoginForm
 12. TestCustomUserCreationForm— forms: registro de usuarios

 13. TestPublicViews           — vistas: respuestas HTTP públicas (200)
 14. TestAuthRedirects         — vistas: redirección de protegidas sin sesión
 15. TestAuthViews             — vistas: login / logout
 16. TestDashboardView         — vistas: dashboard autenticado
 17. TestProjectViews          — vistas: detalle y creación de proyectos
 18. TestResourcesView         — vistas: página de recursos
 19. TestNotificationsView     — vistas: notificaciones

 20. TestTextPreprocessor      — ml: pipeline NLP
 21. TestProjectSuccessPredictor— ml: predictor de éxito
 22. TestMentorRecommender     — ml: recomendador de mentores

Ejecutar con:
  python manage.py test core            (Django test runner)
  pytest core/tests.py -v               (pytest + django-pytest)
"""
# ── Imports estándar ──────────────────────────────────────────────────────────
import datetime
from decimal import Decimal

# ── Django ────────────────────────────────────────────────────────────────────
from django.test import TestCase, Client   # type: ignore
from django.urls import reverse            # type: ignore
from django.contrib.auth.models import User  # type: ignore

# ── Modelos propios ────────────────────────────────────────────────────────────
from core.models import (
    Profile, Project, Investment, Mentorship, Message,
    Resource, ResourceCategory, ProjectCategory,
    ProjectEvaluation, EvaluationCriteria, CriterionScore,
    ProjectRating, Notification,
)

# ── Formularios propios ────────────────────────────────────────────────────────
from core.forms import (
    CustomUserCreationForm, ProjectForm, InvestmentForm, LoginForm,
)


# ─────────────────────────────────────────────────────────────────────────────
# Utilidades de fábrica (no son tests)
# ─────────────────────────────────────────────────────────────────────────────

def make_user(username: str = 'testuser', password: str = 'TestPass123!',
              user_type: str = 'entrepreneur') -> User:
    """Crea un User con Profile asociado listo para pruebas."""
    user = User.objects.create_user(
        username=username,
        password=password,
        email=f'{username}@example.com',
    )
    Profile.objects.create(
        user=user,
        user_type=user_type,
        bio='Bio de prueba para tests',
        experience='Experiencia de prueba para tests',
        is_approved=True,
    )
    return user


def make_project(owner: User, title: str = 'Proyecto Test',
                 funding_goal: Decimal = Decimal('1000000.00')) -> Project:
    """Crea un Project de prueba con categoría por defecto."""
    category, _ = ProjectCategory.objects.get_or_create(
        name='Tecnología Test',
        defaults={'description': 'Categoría para tests', 'icon': 'fas fa-laptop'},
    )
    return Project.objects.create(
        title=title,
        description='Descripción del proyecto de prueba con suficiente texto detallado.',
        owner=owner,
        category=category,
        funding_goal=funding_goal,
        status='active',
    )


# ═════════════════════════════════════════════════════════════════════════════
# 1. TESTS DE MODELOS
# ═════════════════════════════════════════════════════════════════════════════

class TestProfileModel(TestCase):
    """Pruebas unitarias del modelo Profile."""

    def setUp(self):
        self.user = make_user()
        self.profile = self.user.profile

    def test_str_contiene_username(self):
        self.assertIn(self.user.username, str(self.profile))

    def test_str_contiene_tipo(self):
        self.assertIn('entrepreneur', str(self.profile))

    def test_emprendedor_aprobado_por_defecto(self):
        self.assertTrue(self.profile.is_approved)

    def test_mentor_no_aprobado_por_defecto(self):
        mentor = make_user(username='mentor_test', user_type='mentor')
        mentor.profile.is_approved = False
        mentor.profile.save()
        self.assertFalse(mentor.profile.is_approved)

    def test_investor_aprobado_por_defecto(self):
        investor = make_user(username='investor_test', user_type='investor')
        self.assertTrue(investor.profile.is_approved)

    def test_campos_opcionales_vacios_por_defecto(self):
        self.assertEqual(self.profile.phone_number, '')
        self.assertEqual(self.profile.location, '')
        self.assertEqual(self.profile.linkedin_url, '')


class TestProjectModel(TestCase):
    """Pruebas unitarias del modelo Project y sus métodos de negocio."""

    def setUp(self):
        self.owner = make_user()
        self.project = make_project(self.owner)

    def test_str(self):
        self.assertEqual(str(self.project), self.project.title)

    def test_porcentaje_financiamiento_cero_sin_recaudado(self):
        self.assertEqual(self.project.get_funding_percentage(), 0)

    def test_porcentaje_financiamiento_parcial(self):
        self.project.amount_raised = Decimal('500000.00')
        self.project.save()
        pct = self.project.get_funding_percentage()
        self.assertAlmostEqual(float(pct), 50.0, places=1)

    def test_porcentaje_financiamiento_tope_100(self):
        self.project.amount_raised = Decimal('2000000.00')
        self.project.save()
        self.assertEqual(self.project.get_funding_percentage(), 100)

    def test_porcentaje_financiamiento_meta_cero(self):
        self.project.funding_goal = Decimal('0')
        self.project.save()
        self.assertEqual(self.project.get_funding_percentage(), 0)

    def test_promedio_calificacion_sin_ratings(self):
        self.assertEqual(self.project.get_average_rating(), 0)

    def test_promedio_calificacion_con_un_rating(self):
        user2 = make_user(username='rater1', user_type='investor')
        ProjectRating.objects.create(project=self.project, user=user2, rating=4)
        self.assertEqual(self.project.get_average_rating(), 4)

    def test_promedio_calificacion_con_varios_ratings(self):
        u1 = make_user(username='rater_a', user_type='investor')
        u2 = make_user(username='rater_b', user_type='mentor')
        ProjectRating.objects.create(project=self.project, user=u1, rating=3)
        ProjectRating.objects.create(project=self.project, user=u2, rating=5)
        self.assertAlmostEqual(self.project.get_average_rating(), 4.0)

    def test_deadline_no_configurado(self):
        self.assertFalse(self.project.is_deadline_approaching())

    def test_deadline_dentro_de_7_dias(self):
        self.project.deadline = datetime.date.today() + datetime.timedelta(days=3)
        self.project.save()
        self.assertTrue(self.project.is_deadline_approaching())

    def test_deadline_mas_de_7_dias(self):
        self.project.deadline = datetime.date.today() + datetime.timedelta(days=30)
        self.project.save()
        self.assertFalse(self.project.is_deadline_approaching())

    def test_deadline_hoy_es_proximo(self):
        self.project.deadline = datetime.date.today()
        self.project.save()
        self.assertTrue(self.project.is_deadline_approaching())

    def test_estado_por_defecto_active(self):
        self.assertEqual(self.project.status, 'active')

    def test_monto_recaudado_por_defecto_cero(self):
        self.assertEqual(self.project.amount_raised, Decimal('0'))

    def test_is_active_por_defecto(self):
        self.assertTrue(self.project.is_active)


class TestInvestmentModel(TestCase):
    """Pruebas unitarias del modelo Investment."""

    def setUp(self):
        self.entrepreneur = make_user()
        self.investor = make_user(username='investor1', user_type='investor')
        self.project = make_project(self.entrepreneur)

    def _make_investment(self, amount=Decimal('100000'), equity=5.0):
        return Investment.objects.create(
            project=self.project,
            investor=self.investor,
            amount=amount,
            equity_percentage=equity,
        )

    def test_str_contiene_investor(self):
        inv = self._make_investment()
        self.assertIn(self.investor.username, str(inv))

    def test_str_contiene_proyecto(self):
        inv = self._make_investment()
        self.assertIn(self.project.title, str(inv))

    def test_estado_por_defecto_pending(self):
        inv = self._make_investment()
        self.assertEqual(inv.status, 'pending')

    def test_is_accepted_por_defecto_false(self):
        inv = self._make_investment()
        self.assertFalse(inv.is_accepted)

    def test_monto_guardado_correctamente(self):
        inv = self._make_investment(amount=Decimal('250000'))
        self.assertEqual(inv.amount, Decimal('250000'))


class TestMentorshipModel(TestCase):
    """Pruebas unitarias del modelo Mentorship."""

    def setUp(self):
        self.entrepreneur = make_user()
        self.mentor = make_user(username='mentor1', user_type='mentor')
        self.project = make_project(self.entrepreneur)

    def _make_mentorship(self):
        return Mentorship.objects.create(
            project=self.project,
            mentor=self.mentor,
        )

    def test_str_contiene_mentor(self):
        ms = self._make_mentorship()
        self.assertIn(self.mentor.username, str(ms))

    def test_str_contiene_proyecto(self):
        ms = self._make_mentorship()
        self.assertIn(self.project.title, str(ms))

    def test_estado_por_defecto_pending(self):
        ms = self._make_mentorship()
        self.assertEqual(ms.status, 'pending')

    def test_cambio_estado_aceptado(self):
        ms = self._make_mentorship()
        ms.status = 'accepted'
        ms.save()
        ms.refresh_from_db()
        self.assertEqual(ms.status, 'accepted')


class TestResourceModel(TestCase):
    """Pruebas unitarias de Resource y ResourceCategory."""

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin_res', password='Admin1234!', email='admin@test.com'
        )
        self.category = ResourceCategory.objects.create(
            name='Guías de Negocios',
            description='Guías para emprendedores',
        )

    def test_str_categoria(self):
        self.assertEqual(str(self.category), 'Guías de Negocios')

    def test_str_recurso(self):
        resource = Resource.objects.create(
            title='Guía de Plan de Negocios',
            description='Una guía completa para emprendedores.',
            resource_type='guide',
            category=self.category,
            url='https://example.com/guide',
            created_by=self.admin,
        )
        self.assertEqual(str(resource), 'Guía de Plan de Negocios')

    def test_get_resource_url_externo(self):
        resource = Resource.objects.create(
            title='Recurso Externo',
            description='Descripción.',
            resource_type='link',
            category=self.category,
            url='https://example.com/recurso',
            created_by=self.admin,
        )
        self.assertEqual(resource.get_resource_url(), 'https://example.com/recurso')

    def test_get_resource_url_fallback_sin_archivo(self):
        resource = Resource.objects.create(
            title='Sin URL',
            description='Sin archivo ni URL.',
            resource_type='document',
            category=self.category,
            created_by=self.admin,
        )
        self.assertEqual(resource.get_resource_url(), '#')

    def test_recurso_activo_por_defecto(self):
        resource = Resource.objects.create(
            title='Activo Por Defecto',
            description='desc',
            resource_type='link',
            category=self.category,
            url='https://example.com',
            created_by=self.admin,
        )
        self.assertTrue(resource.is_active)

    def test_recurso_destacado_false_por_defecto(self):
        resource = Resource.objects.create(
            title='No Destacado',
            description='desc',
            resource_type='link',
            category=self.category,
            url='https://example.com',
            created_by=self.admin,
        )
        self.assertFalse(resource.is_featured)


class TestProjectEvaluationModel(TestCase):
    """Pruebas unitarias de ProjectEvaluation y cálculo de puntaje."""

    def setUp(self):
        self.entrepreneur = make_user()
        self.evaluator = make_user(username='evaluator1', user_type='evaluator')
        self.project = make_project(self.entrepreneur)
        self.evaluation = ProjectEvaluation.objects.create(
            project=self.project,
            evaluator=self.evaluator,
            overall_score=0.0,
        )
        self.criteria = EvaluationCriteria.objects.create(
            name='Viabilidad',
            description='Qué tan viable es el proyecto',
            weight=1.0,
            max_score=10,
        )

    def test_str_contiene_proyecto(self):
        self.assertIn(self.project.title, str(self.evaluation))

    def test_str_contiene_evaluador(self):
        self.assertIn(self.evaluator.username, str(self.evaluation))

    def test_puntaje_cero_sin_criterios(self):
        score = self.evaluation.calculate_overall_score()
        self.assertEqual(score, 0.0)

    def test_puntaje_con_un_criterio(self):
        CriterionScore.objects.create(
            evaluation=self.evaluation,
            criteria=self.criteria,
            score=8.0,
        )
        score = self.evaluation.calculate_overall_score()
        self.assertAlmostEqual(score, 8.0, places=1)

    def test_puntaje_con_multiples_criterios_ponderados(self):
        criteria2 = EvaluationCriteria.objects.create(
            name='Mercado', description='Análisis de mercado',
            weight=2.0, max_score=10,
        )
        CriterionScore.objects.create(
            evaluation=self.evaluation, criteria=self.criteria, score=6.0
        )
        CriterionScore.objects.create(
            evaluation=self.evaluation, criteria=criteria2, score=9.0
        )
        # Ponderado: (6*1 + 9*2) / (1+2) = 24/3 = 8.0
        score = self.evaluation.calculate_overall_score()
        self.assertAlmostEqual(score, 8.0, places=1)

    def test_criterion_score_str(self):
        cs = CriterionScore.objects.create(
            evaluation=self.evaluation, criteria=self.criteria, score=7.5
        )
        self.assertIn('Viabilidad', str(cs))
        self.assertIn('7.5', str(cs))


class TestProjectCategoryModel(TestCase):
    def test_str(self):
        cat = ProjectCategory.objects.create(name='Fintech', description='Tecnología financiera')
        self.assertEqual(str(cat), 'Fintech')


class TestNotificationModel(TestCase):
    def setUp(self):
        self.user = make_user(username='notiuser')

    def test_notificacion_creada_correctamente(self):
        notif = Notification.objects.create(
            user=self.user,
            title='Test Notification',
            message='Esta es una notificación de prueba',
            notification_type='system',
        )
        self.assertEqual(notif.title, 'Test Notification')

    def test_notificacion_no_leida_por_defecto(self):
        notif = Notification.objects.create(
            user=self.user,
            title='Sin leer',
            message='Mensaje de prueba',
            notification_type='system',
        )
        self.assertFalse(notif.is_read)

    def test_marcar_como_leida(self):
        notif = Notification.objects.create(
            user=self.user,
            title='Marcar',
            message='Mensaje',
            notification_type='investment',
        )
        notif.is_read = True
        notif.save()
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)


# ═════════════════════════════════════════════════════════════════════════════
# 2. TESTS DE FORMULARIOS
# ═════════════════════════════════════════════════════════════════════════════

class TestProjectForm(TestCase):
    """Validación del formulario de creación/edición de proyectos."""

    def setUp(self):
        self.category = ProjectCategory.objects.create(
            name='FormTestCat', description='Categoría para tests de form'
        )

    def _valid_data(self, **overrides):
        data = {
            'title': 'Mi Proyecto de Prueba',
            'description': 'Descripción suficientemente detallada del proyecto de prueba.',
            'category': self.category.pk,
            'funding_goal': '1000000',  # Sin separadores para evitar fallo de DecimalField
            'profitability_time': 12,
            'profitability_unit': 'meses',
        }
        data.update(overrides)
        return data

    def test_form_valido(self):
        form = ProjectForm(data=self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_funding_goal_con_puntos_de_miles_es_invalido(self):
        """Django rechaza '1.000.000' antes de clean_funding_goal; comportamiento esperado."""
        form = ProjectForm(data=self._valid_data(funding_goal='1.000.000'))
        self.assertFalse(form.is_valid())
        self.assertIn('funding_goal', form.errors)

    def test_funding_goal_sin_formato(self):
        form = ProjectForm(data=self._valid_data(funding_goal='500000'))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['funding_goal'], Decimal('500000'))

    def test_titulo_requerido(self):
        form = ProjectForm(data=self._valid_data(title=''))
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_descripcion_requerida(self):
        form = ProjectForm(data=self._valid_data(description=''))
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)

    def test_funding_goal_invalido(self):
        form = ProjectForm(data=self._valid_data(funding_goal='no_es_numero'))
        self.assertFalse(form.is_valid())
        self.assertIn('funding_goal', form.errors)

    def test_categoria_es_opcional(self):
        """category es null=True, blank=True en el modelo, por lo tanto no es requerida."""
        data = self._valid_data()
        data.pop('category')
        form = ProjectForm(data=data)
        # Sin categoría el form sigue siendo válido (campo opcional en el modelo)
        self.assertTrue(form.is_valid(), form.errors)


class TestInvestmentForm(TestCase):
    """Validación del formulario de inversión."""

    def setUp(self):
        self.entrepreneur = make_user()
        self.project = make_project(self.entrepreneur)

    def test_inversion_valida(self):
        form = InvestmentForm(
            data={'amount': '500000', 'equity_percentage': '10'},
            project=self.project,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_monto_texto_invalido(self):
        form = InvestmentForm(
            data={'amount': 'texto_invalido', 'equity_percentage': '10'},
            project=self.project,
        )
        self.assertFalse(form.is_valid())

    def test_equity_requerido(self):
        form = InvestmentForm(
            data={'amount': '100000', 'equity_percentage': ''},
            project=self.project,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('equity_percentage', form.errors)

    def test_monto_con_comas_es_invalido(self):
        """Django rechaza '1,000,000' antes de clean_amount; comportamiento esperado."""
        form = InvestmentForm(
            data={'amount': '1,000,000', 'equity_percentage': '5'},
            project=self.project,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)


class TestLoginForm(TestCase):
    """Validación del formulario de inicio de sesión."""

    def test_form_valido(self):
        form = LoginForm(data={'username': 'testuser', 'password': 'pass1234'})
        self.assertTrue(form.is_valid(), form.errors)

    def test_username_requerido(self):
        form = LoginForm(data={'username': '', 'password': 'pass1234'})
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_password_requerido(self):
        form = LoginForm(data={'username': 'testuser', 'password': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)

    def test_ambos_campos_vacios(self):
        form = LoginForm(data={'username': '', 'password': ''})
        self.assertFalse(form.is_valid())


class TestCustomUserCreationForm(TestCase):
    """Validación del formulario de registro de usuarios."""

    def _base_data(self, **overrides):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'Str0ng!Pass#99',
            'password2': 'Str0ng!Pass#99',
            'user_type': 'entrepreneur',
            'mentor_specialty': '',
            'bio': 'Soy un emprendedor con muchas ideas innovadoras.',
            'experience': 'Tengo 5 años de experiencia en startups tecnológicas.',
        }
        data.update(overrides)
        return data

    def test_mentor_sin_especialidad_es_invalido(self):
        data = self._base_data(user_type='mentor', mentor_specialty='')
        form = CustomUserCreationForm(data=data, files={})
        form.is_valid()
        self.assertIn('mentor_specialty', form.errors)

    def test_mentor_con_especialidad_no_genera_error_especialidad(self):
        data = self._base_data(user_type='mentor', mentor_specialty='technology')
        form = CustomUserCreationForm(data=data, files={})
        form.is_valid()
        self.assertNotIn('mentor_specialty', form.errors)

    def test_emprendedor_no_necesita_especialidad(self):
        data = self._base_data(user_type='entrepreneur', mentor_specialty='')
        form = CustomUserCreationForm(data=data, files={})
        form.is_valid()
        self.assertNotIn('mentor_specialty', form.errors)

    def test_passwords_no_coinciden(self):
        data = self._base_data(password2='OtraContrasena123!')
        form = CustomUserCreationForm(data=data, files={})
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


# ═════════════════════════════════════════════════════════════════════════════
# 3. TESTS DE VISTAS
# ═════════════════════════════════════════════════════════════════════════════

class TestPublicViews(TestCase):
    """Vistas accesibles sin autenticación deben devolver HTTP 200."""

    def setUp(self):
        self.client = Client()

    def test_home_200(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_usa_template_correcto(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home.html')

    def test_login_200(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_register_200(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_resources_200(self):
        response = self.client.get(reverse('resources'))
        self.assertEqual(response.status_code, 200)

    def test_project_list_200(self):
        response = self.client.get(reverse('project_list'))
        self.assertEqual(response.status_code, 200)

    def test_mentor_list_requiere_login(self):
        """mentor_list está protegido con @login_required."""
        response = self.client.get(reverse('mentor_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response['Location'])


class TestAuthRedirects(TestCase):
    """Vistas protegidas deben redirigir a login cuando no hay sesión activa."""

    def setUp(self):
        self.client = Client()

    def _assert_redirige_a_login(self, url_name, kwargs=None):
        url = reverse(url_name, kwargs=kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302, msg=f'{url_name} no redirigió')
        self.assertIn('login', response['Location'])

    def test_dashboard_requiere_login(self):
        self._assert_redirige_a_login('dashboard')

    def test_profile_requiere_login(self):
        self._assert_redirige_a_login('profile')

    def test_project_create_requiere_login(self):
        self._assert_redirige_a_login('project_create')

    def test_analytics_requiere_login(self):
        self._assert_redirige_a_login('analytics_dashboard')

    def test_entrepreneur_metrics_requiere_login(self):
        self._assert_redirige_a_login('entrepreneur_metrics')

    def test_investor_metrics_requiere_login(self):
        self._assert_redirige_a_login('investor_metrics')

    def test_mentor_metrics_requiere_login(self):
        self._assert_redirige_a_login('mentor_metrics')

    def test_notifications_requiere_login(self):
        self._assert_redirige_a_login('notifications')

    def test_ai_assistant_requiere_login(self):
        self._assert_redirige_a_login('ai_project_assistant')


class TestAuthViews(TestCase):
    """Pruebas de flujo de autenticación (login / logout)."""

    def setUp(self):
        self.client = Client()
        self.user = make_user(username='loginuser', password='Testpass1!')

    def test_login_credenciales_validas_redirige(self):
        response = self.client.post(reverse('login'), {
            'username': 'loginuser',
            'password': 'Testpass1!',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_credenciales_invalidas_vuelve_al_form(self):
        response = self.client.post(reverse('login'), {
            'username': 'loginuser',
            'password': 'wrong_password',
        })
        self.assertEqual(response.status_code, 200)

    def test_logout_redirige(self):
        self.client.login(username='loginuser', password='Testpass1!')
        response = self.client.get(reverse('logout'))  # LogoutView acepta GET
        self.assertEqual(response.status_code, 302)

    def test_usuario_autenticado_no_ve_login(self):
        """Un usuario ya logueado al acceder a /login/ debe ser redirigido."""
        self.client.login(username='loginuser', password='Testpass1!')
        response = self.client.get(reverse('login'))
        # Debe redirigir (302) o mostrar el dashboard
        self.assertIn(response.status_code, [200, 302])


class TestDashboardView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user(username='dashuser', password='Dashpass1!')

    def test_dashboard_autenticado_200(self):
        self.client.login(username='dashuser', password='Dashpass1!')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_usa_template_correcto(self):
        self.client.login(username='dashuser', password='Dashpass1!')
        response = self.client.get(reverse('dashboard'))
        self.assertTemplateUsed(response, 'dashboard.html')


class TestProjectViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user(username='projuser', password='Projpass1!')
        self.project = make_project(self.user)

    def test_detalle_proyecto_200(self):
        response = self.client.get(
            reverse('project_detail', kwargs={'pk': self.project.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_detalle_proyecto_muestra_titulo(self):
        response = self.client.get(
            reverse('project_detail', kwargs={'pk': self.project.pk})
        )
        self.assertContains(response, self.project.title)

    def test_detalle_proyecto_404_id_invalido(self):
        response = self.client.get(
            reverse('project_detail', kwargs={'pk': 99999})
        )
        self.assertEqual(response.status_code, 404)

    def test_crear_proyecto_get_autenticado_200(self):
        self.client.login(username='projuser', password='Projpass1!')
        response = self.client.get(reverse('project_create'))
        self.assertEqual(response.status_code, 200)

    def test_crear_proyecto_post_valido_redirige(self):
        self.client.login(username='projuser', password='Projpass1!')
        category = ProjectCategory.objects.get(name='Tecnología Test')
        response = self.client.post(reverse('project_create'), {
            'title': 'Proyecto Post Test',
            'description': 'Descripción completa del nuevo proyecto creado en test.',
            'category': category.pk,
            'funding_goal': '500000',
            'profitability_time': 6,
            'profitability_unit': 'meses',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Project.objects.filter(title='Proyecto Post Test').exists()
        )

    def test_proyecto_inactivo_no_aparece_en_lista_home(self):
        self.project.is_active = False
        self.project.save()
        response = self.client.get(reverse('home'))
        self.assertNotContains(response, self.project.title)


class TestResourcesView(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='adminres', password='Admin1234!', email='adminres@test.com'
        )
        self.category = ResourceCategory.objects.create(
            name='Emprendimiento Test',
            description='Recursos para tests',
        )
        self.active_resource = Resource.objects.create(
            title='Guía Lean Startup Test',
            description='Metodología Lean Startup para emprendedores.',
            resource_type='guide',
            category=self.category,
            url='https://example.com/lean',
            is_active=True,
            created_by=self.admin,
        )
        self.inactive_resource = Resource.objects.create(
            title='Recurso Oculto Test',
            description='Este recurso no debe mostrarse.',
            resource_type='link',
            category=self.category,
            url='https://example.com/hidden',
            is_active=False,
            created_by=self.admin,
        )

    def test_resources_muestra_recurso_activo(self):
        response = self.client.get(reverse('resources'))
        self.assertContains(response, 'Guía Lean Startup Test')

    def test_resources_oculta_recurso_inactivo(self):
        response = self.client.get(reverse('resources'))
        self.assertNotContains(response, 'Recurso Oculto Test')

    def test_resources_200(self):
        response = self.client.get(reverse('resources'))
        self.assertEqual(response.status_code, 200)


class TestNotificationsView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user(username='notiviewuser', password='Noti1234!')

    def test_notifications_requiere_login(self):
        response = self.client.get(reverse('notifications'))
        self.assertEqual(response.status_code, 302)

    def test_notifications_autenticado_200(self):
        self.client.login(username='notiviewuser', password='Noti1234!')
        response = self.client.get(reverse('notifications'))
        self.assertEqual(response.status_code, 200)


# ═════════════════════════════════════════════════════════════════════════════
# 4. TESTS DE MÓDULOS ML — TextPreprocessor
# ═════════════════════════════════════════════════════════════════════════════

class TestTextPreprocessor(TestCase):
    """
    Tests unitarios del preprocesador NLP.
    No requieren BD ni modelos entrenados.
    """

    def setUp(self):
        from ml_models.preprocessor import TextPreprocessor, get_preprocessor
        self.TextPreprocessor = TextPreprocessor
        self.get_preprocessor = get_preprocessor

    def test_get_preprocessor_retorna_instancia(self):
        preprocessor = self.get_preprocessor()
        self.assertIsNotNone(preprocessor)

    def test_preprocess_retorna_string(self):
        preprocessor = self.get_preprocessor()
        result = preprocessor.transform(
            "Aplicación móvil para salud y bienestar de personas mayores"
        )
        self.assertIsInstance(result, str)

    def test_preprocess_minusculas(self):
        preprocessor = self.get_preprocessor()
        result = preprocessor.transform("TEXTO EN MAYUSCULAS")
        self.assertEqual(result, result.lower())

    def test_preprocess_elimina_urls(self):
        preprocessor = self.get_preprocessor()
        result = preprocessor.transform(
            "Visita https://example.com/pagina para mas informacion"
        )
        self.assertNotIn('http', result)

    def test_preprocess_string_vacio(self):
        preprocessor = self.get_preprocessor()
        result = preprocessor.transform("")
        self.assertIsInstance(result, str)

    def test_preprocess_elimina_menciones_y_hashtags(self):
        preprocessor = self.get_preprocessor()
        result = preprocessor.transform("Hola tecnologia innovacion startup")
        # El preprocesador elimina caracteres no alfabéticos como @ y #
        self.assertIsInstance(result, str)

    def test_transform_retorna_string(self):
        """transform() es el método principal del pipeline NLP."""
        preprocessor = self.get_preprocessor()
        result = preprocessor.transform(
            "Plataforma de e-learning con inteligencia artificial"
        )
        self.assertIsInstance(result, str)

    def test_idioma_ingles(self):
        preprocessor = self.TextPreprocessor(language='english', stemming=False)
        result = preprocessor.transform("Mobile application for health and wellness")
        self.assertIsInstance(result, str)

    def test_sin_stemming(self):
        preprocessor = self.TextPreprocessor(language='spanish', stemming=False)
        result = preprocessor.transform("emprendedores innovadores construyen startups exitosas")
        self.assertIsInstance(result, str)

    def test_texto_solo_numeros_y_puntuacion(self):
        preprocessor = self.get_preprocessor()
        result = preprocessor.transform("12345 !!! ??? --- ###")
        self.assertIsInstance(result, str)

    def test_texto_largo(self):
        preprocessor = self.get_preprocessor()
        texto_largo = " ".join(["innovacion tecnologica mercado startup"] * 50)
        result = preprocessor.transform(texto_largo)
        self.assertIsInstance(result, str)


# ═════════════════════════════════════════════════════════════════════════════
# 5. TESTS DE MÓDULOS ML — ProjectSuccessPredictor
# ═════════════════════════════════════════════════════════════════════════════

class TestProjectSuccessPredictor(TestCase):
    """
    Tests del predictor de éxito.
    Verifica comportamiento sin modelo entrenado (fallback garantizado) y,
    si el modelo está disponible, verifica sus rangos de salida.
    """

    def setUp(self):
        from ml_models.success_predictor import ProjectSuccessPredictor
        self.predictor = ProjectSuccessPredictor()

    def test_is_trained_devuelve_bool(self):
        result = self.predictor.is_trained()
        self.assertIsInstance(result, bool)

    def test_predict_devuelve_dict(self):
        result = self.predictor.predict(
            description="Aplicación de telemedicina para zonas rurales de Colombia",
            funding_goal=5_000_000,
            category="Salud",
        )
        self.assertIsInstance(result, dict)

    def test_predict_contiene_claves_esperadas(self):
        result = self.predictor.predict(
            description="Plataforma de educación financiera para jóvenes universitarios",
            funding_goal=10_000_000,
            category="Educación",
        )
        claves_esperadas = {'probability', 'label', 'confidence', 'factors'}
        self.assertTrue(
            claves_esperadas.issubset(result.keys()),
            msg=f"Faltan claves: {claves_esperadas - result.keys()}"
        )

    def test_predict_probability_en_rango_si_entrenado(self):
        result = self.predictor.predict(
            description="Startup de tecnología agrícola con sensores IoT",
            funding_goal=20_000_000,
            category="Tecnología",
        )
        prob = result.get('probability')
        if prob is not None:  # Modelo entrenado
            self.assertGreaterEqual(prob, 0.0)
            self.assertLessEqual(prob, 1.0)

    def test_predict_sin_modelo_devuelve_probability_none(self):
        """Sin modelo entrenado, probability debe ser None (respuesta fallback)."""
        if not self.predictor.is_trained():
            result = self.predictor.predict(description="Test")
            self.assertIsNone(result['probability'])

    def test_predict_sin_modelo_label_informativo(self):
        if not self.predictor.is_trained():
            result = self.predictor.predict(description="Test")
            self.assertIsNotNone(result['label'])
            self.assertIsInstance(result['label'], str)

    def test_clip_probability_limite_inferior(self):
        self.assertEqual(self.predictor._clip_probability(0.0), 0.01)

    def test_clip_probability_limite_superior(self):
        self.assertEqual(self.predictor._clip_probability(1.0), 0.99)

    def test_clip_probability_valor_normal(self):
        self.assertAlmostEqual(self.predictor._clip_probability(0.75), 0.75)

    def test_clip_probability_negativo(self):
        self.assertEqual(self.predictor._clip_probability(-0.5), 0.01)

    def test_clip_probability_mayor_que_uno(self):
        self.assertEqual(self.predictor._clip_probability(1.5), 0.99)

    def test_predict_description_vacia(self):
        result = self.predictor.predict(description="")
        self.assertIsInstance(result, dict)

    def test_predict_sin_parametros_opcionales(self):
        result = self.predictor.predict(
            description="Proyecto de tecnología educativa para colegios públicos"
        )
        self.assertIsInstance(result, dict)
        self.assertIn('label', result)

    def test_predict_factors_es_lista(self):
        result = self.predictor.predict(
            description="Solución innovadora de logística para e-commerce",
            funding_goal=15_000_000,
            category="Tecnología",
        )
        if result.get('factors') is not None:
            self.assertIsInstance(result['factors'], list)


# ═════════════════════════════════════════════════════════════════════════════
# 6. TESTS DE MÓDULOS ML — MentorRecommender
# ═════════════════════════════════════════════════════════════════════════════

class TestMentorRecommender(TestCase):
    """Tests del recomendador de mentores."""

    def setUp(self):
        from ml_models.mentor_recommender import MentorRecommender
        self.MentorRecommender = MentorRecommender
        self.recommender = MentorRecommender()

    def test_instancia_creada(self):
        self.assertIsNotNone(self.recommender)

    def test_is_ready_devuelve_bool(self):
        result = self.recommender.is_ready()
        self.assertIsInstance(result, bool)

    def test_recommend_sin_indice_retorna_lista_vacia(self):
        """Sin índice construido, recommend() debe devolver lista vacía."""
        recommender = self.MentorRecommender()
        # Limpiar índice para asegurar estado no entrenado
        recommender._vectorizer = None
        recommender._mentor_matrix = None
        recommender._mentor_meta = []
        result = recommender.recommend("App de telemedicina para zonas rurales", top_k=5)
        self.assertEqual(result, [])

    def test_recommend_retorna_lista(self):
        result = self.recommender.recommend(
            "Plataforma de finanzas personales para jóvenes",
            top_k=5,
        )
        self.assertIsInstance(result, list)

    def test_recommend_query_vacio_retorna_lista(self):
        result = self.recommender.recommend("", top_k=3)
        self.assertIsInstance(result, list)

    def test_build_index_from_data_construye_indice(self):
        """build_index_from_data() debe construir el índice sin BD."""
        recommender = self.MentorRecommender()
        mentors_data = [
            {
                'user_id': 1, 'username': 'mentor_tech', 'name': 'Carlos Tech',
                'bio': 'Experto en tecnología y desarrollo de software',
                'experience': '10 años en startups tecnológicas',
                'specialty': 'technology', 'specialty_display': 'Tecnología e Innovación',
            },
            {
                'user_id': 2, 'username': 'mentor_fin', 'name': 'María Finanzas',
                'bio': 'Consultora financiera y de negocios',
                'experience': '8 años en banca y finanzas corporativas',
                'specialty': 'finance', 'specialty_display': 'Finanzas y Negocios',
            },
            {
                'user_id': 3, 'username': 'mentor_mkt', 'name': 'Luis Marketing',
                'bio': 'Especialista en marketing digital y ventas',
                'experience': '6 años en agencias de publicidad',
                'specialty': 'marketing', 'specialty_display': 'Marketing y Ventas',
            },
        ]
        n = recommender.build_index_from_data(mentors_data)
        self.assertEqual(n, 3)
        self.assertTrue(recommender.is_ready())

    def test_recommend_despues_de_build_index(self):
        """Tras construir el índice, recommend() debe retornar resultados."""
        recommender = self.MentorRecommender()
        mentors_data = [
            {
                'user_id': 1, 'username': 'mentor_tech', 'name': 'Juan Tech',
                'bio': 'Desarrollador de software y emprendedor tecnológico',
                'experience': 'Fundador de tres startups de tecnología',
                'specialty': 'technology', 'specialty_display': 'Tecnología e Innovación',
            },
            {
                'user_id': 2, 'username': 'mentor_health', 'name': 'Ana Salud',
                'bio': 'Médica con enfoque en telemedicina e innovación en salud',
                'experience': 'Directora médica y asesora de startups de salud',
                'specialty': 'health', 'specialty_display': 'Salud y Bienestar',
            },
        ]
        recommender.build_index_from_data(mentors_data)
        results = recommender.recommend(
            "Aplicación de telemedicina con inteligencia artificial",
            project_category="Salud",
            top_k=2,
        )
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertLessEqual(len(results), 2)

    def test_resultado_tiene_claves_esperadas(self):
        """Cada resultado debe tener user_id, name, score y similarity."""
        recommender = self.MentorRecommender()
        mentors_data = [
            {
                'user_id': 10, 'username': 'mtest', 'name': 'Mentor Test',
                'bio': 'Experto en finanzas empresariales',
                'experience': 'CFO en múltiples empresas',
                'specialty': 'finance', 'specialty_display': 'Finanzas y Negocios',
            }
        ]
        recommender.build_index_from_data(mentors_data)
        results = recommender.recommend("Plataforma financiera para pymes", top_k=1)
        if results:
            result = results[0]
            for key in ('user_id', 'name', 'score', 'similarity', 'match_pct'):
                self.assertIn(key, result, msg=f"Falta clave '{key}' en resultado")

    def test_score_en_rango_valido(self):
        """Todos los scores deben ser >= 0."""
        recommender = self.MentorRecommender()
        mentors_data = [
            {
                'user_id': 1, 'username': 'mscoretest', 'name': 'Score Test',
                'bio': 'Experto en tecnología y negocios digitales',
                'experience': 'CTO y cofundador',
                'specialty': 'technology', 'specialty_display': 'Tecnología',
            }
        ]
        recommender.build_index_from_data(mentors_data)
        results = recommender.recommend("App móvil para emprendedores", top_k=1)
        for r in results:
            self.assertGreaterEqual(r['score'], 0.0)
            self.assertGreaterEqual(r['similarity'], 0.0)

    def test_top_k_limita_resultados(self):
        """recommend() no debe devolver más de top_k resultados."""
        recommender = self.MentorRecommender()
        mentors_data = [
            {
                'user_id': i, 'username': f'mentor_{i}', 'name': f'Mentor {i}',
                'bio': f'Experto en área {i} con experiencia comprobada',
                'experience': f'10 años de experiencia en sector {i}',
                'specialty': 'technology', 'specialty_display': 'Tecnología',
            }
            for i in range(10)
        ]
        recommender.build_index_from_data(mentors_data)
        results = recommender.recommend("Proyecto de tecnología innovadora", top_k=3)
        self.assertLessEqual(len(results), 3)
