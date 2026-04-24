"""
Módulo 3 — Asesor de Mejoras de Proyectos
==========================================
Genera sugerencias concretas para mejorar un proyecto basándose en
los patrones extraídos de proyectos exitosos similares.

Técnica: Recuperación Basada en Contenido (Content-Based Retrieval)
--------------------------------------------------------------------
1. Vectorizar el corpus de proyectos exitosos con TF-IDF
2. Para un proyecto nuevo, calcular su similitud coseno con cada
   proyecto exitoso del corpus
3. Recuperar los top-k proyectos similares
4. Extraer patrones comunes (palabras clave, rangos de meta, categorías)
5. Generar sugerencias basadas en las brechas detectadas

Modelo matemático
-----------------
Sean X = {x₁, x₂, …, xₙ} los proyectos exitosos vectorizados.
Para un nuevo proyecto q:

  sim(q, xᵢ) = (q · xᵢ) / (‖q‖ × ‖xᵢ‖)

  Proyectos similares: S_k = top-k{xᵢ : sim(q, xᵢ) ≥ θ}

  Términos relevantes en S_k:
    freq(t) = Σ_{xᵢ ∈ S_k} TF-IDF(t, xᵢ)

  Sugerencia si t ∉ q y freq(t) está en el top-m de S_k.
"""
from __future__ import annotations

import logging
from collections import Counter
from typing import TYPE_CHECKING

try:
    import joblib
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    _SKLEARN_AVAILABLE = True
except ImportError:
    _SKLEARN_AVAILABLE = False

from ml_models.config import ADVISOR, ADVISOR_VECTORIZER_PATH, ADVISOR_CORPUS_PATH
from ml_models.preprocessor import get_preprocessor

logger = logging.getLogger(__name__)

# ── Banco de sugerencias por área temática ────────────────────────────────────
# Banco expandido con sugerencias accionables y educativas por área de mejora.
SUGGESTION_BANK = {
    'mercado': [
        "Define el TAM (mercado total), SAM (mercado alcanzable) y SOM (objetivo inicial) con cifras reales de tu país o región.",
        "Realiza al menos 5-10 entrevistas con clientes potenciales para validar que el problema es real y están dispuestos a pagar.",
        "Analiza a tus 3 competidores directos: fortalezas, debilidades, precio y por qué los clientes te elegirían a ti.",
        "Construye un buyer persona: nombre ficticio, edad, profesión, ingresos, frustraciones y cómo busca soluciones hoy.",
        "Estima el CAC (costo de adquirir un cliente) y el LTV (valor de vida del cliente). LTV debe ser al menos 3x el CAC.",
        "Valida que el dolor que resuelves es suficientemente fuerte — los mejores negocios atacan problemas por los que ya se gasta dinero.",
        "Identifica los canales donde tu cliente busca soluciones hoy (Google, redes, referidos, ferias) para llegar a ellos.",
    ],
    'modelo_negocio': [
        "Define tu fuente de ingresos principal: ¿suscripción recurrente, comisión por transacción, licencia, freemium o venta directa?",
        "Proyecta ingresos y gastos mes a mes para los primeros 24 meses. Muestra cuándo llegas al break-even.",
        "Calcula tu margen bruto: lo que queda después de descontar los costos variables por cliente/transacción.",
        "Evalúa si tu modelo escala eficientemente — los mejores negocios tienen costos que crecen más lento que los ingresos.",
        "Define el MRR objetivo a 12 meses (ingresos recurrentes mensuales). Los inversores valoran la previsibilidad.",
        "Considera un modelo freemium o prueba de 30 días para reducir la barrera de entrada y acelerar adopción.",
        "Identifica posibles fuentes de ingresos adicionales: upsells, cross-sells, marketplace, datos anonimizados.",
    ],
    'equipo': [
        "Presenta cada fundador con su rol, experiencia clave y por qué está idealmente posicionado para este proyecto.",
        "Identifica las habilidades críticas faltantes en el equipo y cómo planeas cubrirlas (socio, contratación, asesor).",
        "Incluye al menos un asesor con experiencia en la industria o en startups similares. Aumenta la credibilidad.",
        "Define el plan de equity y compensación del equipo fundador para evitar conflictos futuros (usa un vesting schedule).",
        "Muestra el historial relevante del equipo: proyectos previos, clientes conseguidos, tecnología construida, premios.",
        "Establece los 2-3 roles clave que necesitarás contratar en los primeros 12 meses con el financiamiento.",
        "El equipo es lo que más pesa para los inversores — 'apuestan al jockey, no al caballo'. Cuida cómo lo presentas.",
    ],
    'producto': [
        "Define el MVP: la versión más simple posible del producto que valida tu hipótesis principal con el menor costo.",
        "Mapea el journey completo del usuario: desde que descubre el producto hasta que paga y se convierte en recurrente.",
        "Documenta las validaciones que ya hiciste: encuestas, entrevistas, prototipos clickeables, beta testers, pilotos.",
        "Define las 3 funcionalidades innegociables para el lanzamiento y deja el resto para versiones posteriores.",
        "Explica tu diferenciador en una sola frase memorable. Si no puedes, el producto no está bien definido aún.",
        "Crea un roadmap de producto a 6-12 meses: qué construyes primero, segundo y tercero, y por qué en ese orden.",
        "Considera accesibilidad y usabilidad para tu público objetivo — el mejor producto es el que la gente usa, no el más complejo.",
    ],
    'tracción': [
        "Incluye cualquier métrica de tracción disponible: usuarios registrados, activos mensuales, ingresos, órdenes, descargas.",
        "Presenta pilotos o clientes actuales aunque sean pequeños — un cliente real vale más que mil proyecciones.",
        "Comparte testimonios, cartas de intención o contratos firmados de clientes potenciales.",
        "Muestra la tasa de crecimiento semana a semana o mes a mes de tus métricas principales.",
        "Si aún no tienes clientes, describe los experimentos de validación que has hecho (landing page, encuestas, entrevistas).",
        "Menciona reconocimientos: premios de emprendimiento, apariciones en medios, aceleradoras o incubadoras.",
        "El NPS (Net Promoter Score) de tus primeros usuarios es un excelente indicador de product-market fit.",
    ],
    'impacto': [
        "Cuantifica el impacto esperado con indicadores medibles: personas beneficiadas, empleos creados, emisiones reducidas.",
        "Relaciona tu proyecto con los ODS de Naciones Unidas que apliquen (ODS 1-17). Esto abre puertas a fondos de impacto.",
        "Define cómo medirás el impacto real a 1, 3 y 5 años. Los inversores de impacto requieren métricas claras.",
        "Considera certificaciones como B Corp, sello de empresa social o economía circular que aumentan credibilidad.",
        "Explica cómo el crecimiento comercial y el impacto social se refuerzan mutuamente — que crecer más = más impacto.",
        "Si tu proyecto genera impacto ambiental, calcula la huella de carbono evitada o los residuos reducidos.",
    ],
    'tecnologia': [
        "Detalla el stack tecnológico (lenguajes, frameworks, bases de datos, cloud) y justifica por qué lo elegiste.",
        "Describe la arquitectura del sistema: ¿cómo escala cuando pases de 100 a 100,000 usuarios?",
        "Menciona si tienes propiedad intelectual: patentes, algoritmos propietarios, datos únicos o secretos industriales.",
        "Explica las medidas de seguridad y privacidad de datos (cumplimiento GDPR, Habeas Data, encriptación).",
        "Evalúa el uso de IA/ML si aplica: puede diferenciar el producto y generar barreras de entrada.",
        "Define el plan de contingencia ante fallos críticos: backup, redundancia, SLA de uptime.",
        "Si aún no tienes tecnología construida, define claramente qué necesitas construir y en qué tiempo.",
    ],
    'financiamiento': [
        "Especifica el destino exacto de los fondos por rubro (% o valor absoluto) y justifica cada uno.",
        "Define el porcentaje de equity que ofreces y explica la valoración implícita del proyecto con ese cálculo.",
        "Calcula el runway: ¿cuántos meses puede operar el proyecto con el capital que solicitas?",
        "Presenta el hito concreto que alcanzarás con este financiamiento (ej: 'llegar a 500 clientes pagos').",
        "Muestra el retorno esperado para el inversor en escenario conservador, realista y optimista a 5 años.",
        "Menciona fuentes anteriores de capital: bootstrapping, premios, FFF (friends, family, fools), grants.",
        "Define claramente qué decisiones de uso de fondos requieren aprobación del inversor y cuáles son autónomas.",
    ],
    'propuesta_valor': [
        "Resume tu propuesta de valor en una sola frase: 'Ayudamos a [quién] a [resultado] sin [fricción o costo]'.",
        "Compara tu solución con la alternativa de 'no hacer nada' — ¿cuánto le cuesta al cliente no resolver el problema?",
        "Define los 3 beneficios tangibles principales que obtiene el cliente al usar tu solución.",
        "Identifica el 'momento aha' — cuando el usuario entiende instantáneamente el valor. Diseña hacia ese momento.",
        "Valida que tu propuesta de valor resuena con el cliente real, no con lo que tú crees que necesita.",
        "Diferencia entre features (características) y beneficios. Los clientes compran beneficios, no features.",
    ],
    'validacion': [
        "Haz entrevistas de problema (no de solución) con 10+ usuarios potenciales. Escucha más de lo que hablas.",
        "Crea un landing page con descripción del producto y un CTA. Si el 10%+ deja su email, hay demanda.",
        "Construye un prototipo de baja fidelidad (Figma, wireframe, maqueta manual) para probar la experiencia.",
        "Define la hipótesis central que tu MVP debe validar o refutar en las primeras 4-8 semanas.",
        "Establece criterios claros de éxito para la validación ANTES de empezar, para evitar confirmation bias.",
        "Si alguien te paga aunque sea $1 por una solución manual del problema, tienes la validación más poderosa.",
    ],
    'estrategia_go_to_market': [
        "Define los primeros 100 clientes con nombre y apellido (o empresa específica). ¿Cómo los conseguirás uno a uno?",
        "Elige un solo canal de adquisición principal para el lanzamiento y mastering antes de diversificar.",
        "Crea un plan de pre-lanzamiento: lista de espera, comunidad, contenido educativo, alianzas estratégicas.",
        "Identifica 3 aliados que ya tienen acceso a tu cliente ideal y pueden acelerar tu distribución.",
        "Define el mensaje de marketing en 10 palabras que resuene con el problema de tu cliente.",
        "Para B2B: el proceso de venta suele ser largo. Define el ciclo de ventas y los roles en la toma de decisión.",
    ],
}

# Palabras clave que activan cada área (expandido significativamente)
AREA_KEYWORDS = {
    'mercado': {
        'mercado', 'clientes', 'competencia', 'segmento', 'demanda', 'market',
        'tam', 'sam', 'buyer', 'persona', 'audiencia', 'target', 'consumidores',
        'usuarios', 'nicho', 'industria', 'sector', 'demografico', 'publico',
        'potenciales', 'analisis', 'investigacion', 'encuesta',
    },
    'modelo_negocio': {
        'ingresos', 'revenue', 'freemium', 'suscripcion', 'b2b', 'b2c', 'ventas',
        'precio', 'cobrar', 'facturar', 'monetizar', 'mrr', 'arr', 'comision',
        'margen', 'ganancia', 'rentable', 'breakeven', 'cac', 'ltv', 'ticket',
        'pago', 'cobro', 'tarifa', 'modelo', 'negocio',
    },
    'equipo': {
        'equipo', 'fundadores', 'cofundador', 'experiencia', 'team', 'ceo',
        'cto', 'socio', 'asesor', 'mentor', 'staff', 'personal', 'contratar',
        'rol', 'responsable', 'habilidades', 'liderazgo', 'founder', 'cargo',
    },
    'producto': {
        'mvp', 'prototipo', 'producto', 'app', 'plataforma', 'servicio',
        'solucion', 'feature', 'funcionalidad', 'desarrollo', 'version',
        'lanzar', 'beta', 'piloto', 'prueba', 'usuario', 'interfaz', 'ux',
        'diseno', 'herramienta', 'software',
    },
    'tracción': {
        'traccion', 'traction', 'usuarios', 'alianzas', 'crecimiento',
        'metricas', 'kpi', 'conversion', 'activos', 'registros', 'descargas',
        'testimonios', 'referidos', 'nps', 'retencion', 'churn', 'engagement',
    },
    'impacto': {
        'impacto', 'social', 'ambiental', 'sostenible', 'ods', 'comunidad',
        'cambio', 'beneficio', 'responsabilidad', 'verde', 'ecologico',
        'inclusivo', 'equidad', 'pobreza', 'medicion', 'indicadores',
    },
    'tecnologia': {
        'tecnologia', 'software', 'ia', 'blockchain', 'cloud', 'api', 'datos',
        'algoritmo', 'machine', 'learning', 'infraestructura', 'seguridad',
        'privacidad', 'arquitectura', 'stack', 'escalable', 'backend',
        'frontend', 'database', 'servidor', 'codigo',
    },
    'financiamiento': {
        'financiamiento', 'inversion', 'fondos', 'capital', 'equity', 'roi',
        'retorno', 'valorizacion', 'ronda', 'inversor', 'runway', 'presupuesto',
        'costo', 'gasto', 'bootstrap', 'deuda', 'credito', 'valuation',
    },
    'propuesta_valor': {
        'diferencia', 'unico', 'ventaja', 'valor', 'propuesta', 'mejor',
        'innovador', 'disruptivo', 'beneficio', 'ahorra', 'facilita',
        'automatiza', 'reduce', 'diferenciador', 'competitivo', 'exclusivo',
    },
    'validacion': {
        'validar', 'validacion', 'hipotesis', 'experimento', 'encuesta',
        'entrevista', 'feedback', 'prototipo', 'test', 'piloto', 'prueba',
        'usuario', 'landing', 'mvp',
    },
    'estrategia_go_to_market': {
        'lanzamiento', 'marketing', 'publicidad', 'canal', 'distribucion',
        'alianza', 'partner', 'referido', 'viral', 'contenido', 'seo',
        'ads', 'redes', 'social', 'go-to-market', 'gtm', 'ventas',
    },
}


class ProjectAdvisor:
    """
    Asesor de mejoras basado en proyectos exitosos similares.

    Uso básico
    ----------
    >>> advisor = ProjectAdvisor()
    >>> advisor.build_corpus()    # indexa proyectos exitosos de la BD
    >>> tips = advisor.advise("App para conectar agricultores con compradores")
    >>> for tip in tips:
    ...     print(tip['area'], tip['suggestion'])
    """

    def __init__(self):
        self._vectorizer: TfidfVectorizer | None = None
        self._corpus_matrix = None
        self._corpus_meta: list[dict] = []
        self._cfg = ADVISOR
        self._load_if_exists()

    def is_ready(self) -> bool:
        return (
            self._vectorizer is not None and
            self._corpus_matrix is not None and
            len(self._corpus_meta) > 0
        )

    # ── Persistencia ──────────────────────────────────

    def _load_if_exists(self) -> None:
        if not _SKLEARN_AVAILABLE:
            return
        if ADVISOR_VECTORIZER_PATH.exists() and ADVISOR_CORPUS_PATH.exists():
            try:
                data = joblib.load(ADVISOR_CORPUS_PATH)
                self._vectorizer   = joblib.load(ADVISOR_VECTORIZER_PATH)
                self._corpus_matrix = data['matrix']
                self._corpus_meta   = data['meta']
                logger.info("Corpus del asesor cargado (%d proyectos)", len(self._corpus_meta))
            except Exception as exc:
                logger.warning("No se pudo cargar el corpus del asesor: %s", exc)

    def save(self) -> None:
        if not self.is_ready():
            return
        joblib.dump(self._vectorizer, ADVISOR_VECTORIZER_PATH)
        joblib.dump(
            {'matrix': self._corpus_matrix, 'meta': self._corpus_meta},
            ADVISOR_CORPUS_PATH,
        )
        logger.info("Corpus del asesor guardado (%d proyectos)", len(self._corpus_meta))

    # ── Construcción del corpus ───────────────────────

    def build_corpus(self, min_funding_pct: float = 0.80) -> int:
        """
        Construye el corpus de proyectos exitosos desde la BD.

        Parámetros
        ----------
        min_funding_pct : fracción mínima de meta alcanzada para
                          considerar un proyecto como "exitoso"
        """
        if not _SKLEARN_AVAILABLE:
            raise ImportError("Instala scikit-learn: pip install scikit-learn")

        from core.models import Project

        # Proyectos con ≥ min_funding_pct de su meta financiada
        all_projects = Project.objects.filter(is_active=True).select_related('category')

        preprocessor = get_preprocessor()
        corpus = []
        meta   = []

        for p in all_projects:
            try:
                pct = float(p.amount_raised) / float(p.funding_goal) if float(p.funding_goal) > 0 else 0
            except Exception:
                pct = 0

            if pct < min_funding_pct and p.status not in ('funded', 'completed'):
                continue

            raw = f"{p.title} {p.description}"
            corpus.append(preprocessor.transform(raw))
            meta.append({
                'id':       p.id,
                'title':    p.title,
                'category': p.category.name if p.category else '',
                'funded_pct': round(pct * 100, 1),
            })

        if not corpus:
            logger.warning("No hay proyectos exitosos para construir el corpus del asesor")
            return 0

        cfg = self._cfg
        self._vectorizer = TfidfVectorizer(
            max_features=cfg['tfidf_max_features'],
            ngram_range=cfg['tfidf_ngram_range'],
        )
        self._corpus_matrix = self._vectorizer.fit_transform(corpus)
        self._corpus_meta   = meta

        self.save()
        logger.info("Corpus construido con %d proyectos exitosos", len(meta))
        return len(meta)

    def build_corpus_from_data(self, projects_data: list[dict]) -> int:
        """
        Construye el corpus desde datos en memoria (sin BD).
        Útil para entrenamiento con dataset de Kaggle.
        Cada elemento debe tener: id, title, description, category.
        """
        if not _SKLEARN_AVAILABLE:
            raise ImportError("Instala scikit-learn: pip install scikit-learn")

        preprocessor = get_preprocessor()
        corpus = []
        meta   = []

        for p in projects_data:
            raw = f"{p.get('title', '')} {p.get('description', '')}"
            corpus.append(preprocessor.transform(raw))
            meta.append({
                'id':        p.get('id'),
                'title':     p.get('title', ''),
                'category':  p.get('category', ''),
                'funded_pct': p.get('funded_pct', 100),
            })

        cfg = self._cfg
        self._vectorizer = TfidfVectorizer(
            max_features=cfg['tfidf_max_features'],
            ngram_range=cfg['tfidf_ngram_range'],
        )
        self._corpus_matrix = self._vectorizer.fit_transform(corpus)
        self._corpus_meta   = meta

        self.save()
        return len(meta)

    # ── Asesoría ──────────────────────────────────────

    def advise(self, project_description: str,
               project_category: str = '') -> list[dict]:
        """
        Genera sugerencias de mejora para un proyecto.

        Retorna
        -------
        list[dict] con:
          - area       : str  (área de mejora)
          - suggestion : str  (sugerencia concreta)
          - priority   : str  ('Alta' | 'Media' | 'Baja')
          - source     : str  ('rule' | 'content')
        """
        suggestions = []

        # ── Sugerencias por análisis de palabras clave ──
        kw_suggestions = self._keyword_based_suggestions(project_description)
        suggestions.extend(kw_suggestions)

        # ── Sugerencias por recuperación de similares ──
        if self.is_ready():
            content_suggestions = self._content_based_suggestions(
                project_description, project_category
            )
            # Agregar las que no estén ya cubiertas
            existing_areas = {s['area'] for s in suggestions}
            for s in content_suggestions:
                if s['area'] not in existing_areas:
                    suggestions.append(s)
                    existing_areas.add(s['area'])

        # Si no hay sugerencias, dar retroalimentación genérica
        if not suggestions:
            suggestions = self._generic_suggestions()

        # Ordenar por prioridad
        priority_order = {'Alta': 0, 'Media': 1, 'Baja': 2}
        suggestions.sort(key=lambda s: priority_order.get(s['priority'], 2))

        return suggestions[:8]  # máximo 8 sugerencias

    def _keyword_based_suggestions(self, description: str) -> list[dict]:
        """Detecta áreas de mejora por ausencia de palabras clave."""
        desc_lower = description.lower()
        desc_tokens = set(desc_lower.split())
        suggestions = []

        area_priority = {
            'mercado':                    'Alta',
            'modelo_negocio':             'Alta',
            'equipo':                     'Media',
            'producto':                   'Alta',
            'tracción':                   'Media',
            'impacto':                    'Baja',
            'tecnologia':                 'Baja',
            'financiamiento':             'Media',
            'propuesta_valor':            'Alta',
            'validacion':                 'Alta',
            'estrategia_go_to_market':    'Media',
        }

        for area, keywords in AREA_KEYWORDS.items():
            # Si NINGUNA palabra clave del área aparece en la descripción
            found = keywords & desc_tokens
            if not found:
                bank = SUGGESTION_BANK.get(area, [])
                if bank:
                    suggestions.append({
                        'area':       area.replace('_', ' ').title(),
                        'suggestion': bank[0],
                        'priority':   area_priority.get(area, 'Baja'),
                        'source':     'rule',
                    })

        return suggestions

    def _content_based_suggestions(self, description: str,
                                   category: str) -> list[dict]:
        """Extrae patrones de proyectos exitosos similares."""
        preprocessor = get_preprocessor()
        query_clean  = preprocessor.transform(description)
        query_vec    = self._vectorizer.transform([query_clean])

        sims = cosine_similarity(query_vec, self._corpus_matrix).flatten()

        min_sim = self._cfg['min_similarity']
        top_k   = self._cfg['top_k_similar']

        # Índices de proyectos similares exitosos
        similar_idx = [
            i for i in sims.argsort()[::-1][:top_k]
            if sims[i] >= min_sim
        ]

        if not similar_idx:
            return []

        # Extraer categorías más comunes entre los proyectos similares
        cats = [self._corpus_meta[i]['category'] for i in similar_idx if self._corpus_meta[i]['category']]
        if cats:
            most_common_cat = Counter(cats).most_common(1)[0][0]
            if most_common_cat and most_common_cat.lower() not in category.lower():
                return [{
                    'area':       'Categoría',
                    'suggestion': f"Proyectos similares exitosos suelen categorizarse como '{most_common_cat}'. Verifica si aplica a tu proyecto.",
                    'priority':   'Baja',
                    'source':     'content',
                }]

        return []

    @staticmethod
    def _generic_suggestions() -> list[dict]:
        return [
            {
                'area':       'Descripción',
                'suggestion': 'Amplía la descripción del proyecto con al menos 100 palabras que expliquen el problema, la solución y el mercado objetivo.',
                'priority':   'Alta',
                'source':     'rule',
            },
            {
                'area':       'Propuesta de Valor',
                'suggestion': 'Define claramente qué hace único a tu proyecto frente a las alternativas existentes.',
                'priority':   'Alta',
                'source':     'rule',
            },
        ]


# ── Singleton ────────────────────────────────────────
_advisor: ProjectAdvisor | None = None


def get_advisor() -> ProjectAdvisor:
    global _advisor
    if _advisor is None:
        _advisor = ProjectAdvisor()
    return _advisor


def rebuild_advisor_corpus() -> int:
    global _advisor
    adv = get_advisor()
    return adv.build_corpus()
