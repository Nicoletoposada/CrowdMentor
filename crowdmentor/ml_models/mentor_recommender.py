"""
Módulo 2 — Recomendador de Mentores
=====================================
Recomienda los mentores más compatibles para un proyecto dado.

Modelo matemático
-----------------
Sea V_p el vector TF-IDF de la descripción del proyecto p,
y V_mᵢ el vector TF-IDF del perfil del mentor i (bio + especialidad).

Similitud Coseno:
  sim(p, mᵢ) = (V_p · V_mᵢ) / (‖V_p‖ × ‖V_mᵢ‖)

Puntuación final con bonus por especialidad:
  score(p, mᵢ) = sim(p, mᵢ) + δ × I(specialty(mᵢ) == cat(p))

  donde δ = specialty_bonus ∈ [0, 1]
        I(·) = función indicadora

El ranking final ordena por score(p, mᵢ) descendente y retorna
los top-k mentores aprobados por la plataforma.

Actualización del índice
------------------------
Cada vez que un mentor se une o actualiza su perfil, se reconstruye
la matriz de vectores de mentores y se persiste en disco.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np

try:
    import joblib
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    _SKLEARN_AVAILABLE = True
except ImportError:
    _SKLEARN_AVAILABLE = False

from ml_models.config import (
    MENTOR_RECOMMENDER,
    MENTOR_VECTORIZER_PATH,
    MENTOR_MATRIX_PATH,
)
from ml_models.preprocessor import get_preprocessor

if TYPE_CHECKING:
    pass  # Evitar importación circular con Django

logger = logging.getLogger(__name__)


class MentorRecommender:
    """
    Recomendador basado en contenido para emparejar proyectos con mentores.

    El sistema indexa el corpus de perfiles de mentores con TF-IDF
    y calcula la similitud coseno entre la descripción del proyecto
    y cada perfil de mentor en tiempo real.

    Uso básico
    ----------
    >>> rec = MentorRecommender()
    >>> rec.build_index()   # construye el índice desde la BD
    >>> results = rec.recommend("App de telemedicina para zonas rurales", top_k=5)
    >>> for r in results:
    ...     print(r['name'], r['score'])
    """

    def __init__(self):
        self._vectorizer: TfidfVectorizer | None = None
        self._mentor_matrix = None     # scipy sparse matrix
        self._mentor_meta: list[dict] = []  # metadata de cada mentor
        self._cfg = MENTOR_RECOMMENDER
        self._load_if_exists()

    # ── Estado ────────────────────────────────────────

    def is_ready(self) -> bool:
        """Retorna True si el índice está construido y listo."""
        return (
            self._vectorizer is not None and
            self._mentor_matrix is not None and
            len(self._mentor_meta) > 0
        )

    # ── Persistencia ──────────────────────────────────

    def _load_if_exists(self) -> None:
        if not _SKLEARN_AVAILABLE:
            return
        if MENTOR_VECTORIZER_PATH.exists() and MENTOR_MATRIX_PATH.exists():
            try:
                data = joblib.load(MENTOR_MATRIX_PATH)
                self._vectorizer = joblib.load(MENTOR_VECTORIZER_PATH)
                self._mentor_matrix = data['matrix']
                self._mentor_meta   = data['meta']
                logger.info("Índice de mentores cargado (%d mentores)", len(self._mentor_meta))
            except Exception as exc:
                logger.warning("No se pudo cargar el índice de mentores: %s", exc)

    def save(self) -> None:
        if not self.is_ready():
            return
        joblib.dump(self._vectorizer, MENTOR_VECTORIZER_PATH)
        joblib.dump(
            {'matrix': self._mentor_matrix, 'meta': self._mentor_meta},
            MENTOR_MATRIX_PATH,
        )
        logger.info("Índice de mentores guardado (%d mentores)", len(self._mentor_meta))

    # ── Construcción del índice ───────────────────────

    def build_index(self) -> int:
        """
        Construye el índice TF-IDF desde la base de datos de CrowdMentor.

        Requiere contexto Django activo (llama a Profile.objects).

        Retorna el número de mentores indexados.
        """
        if not _SKLEARN_AVAILABLE:
            raise ImportError("Instala scikit-learn: pip install scikit-learn")

        from django.contrib.auth.models import User
        from core.models import Profile

        # Solo mentores aprobados
        mentors = Profile.objects.filter(
            user_type='mentor',
            is_approved=True,
        ).select_related('user')

        if not mentors.exists():
            logger.warning("No hay mentores aprobados para indexar")
            return 0

        preprocessor = get_preprocessor()
        corpus = []
        meta   = []

        for m in mentors:
            # Construir texto del perfil: bio + experiencia + especialidad
            specialty_text = m.get_mentor_specialty_display() if m.mentor_specialty else ''
            raw = f"{m.bio} {m.experience} {specialty_text}"
            corpus.append(preprocessor.transform(raw))
            meta.append({
                'user_id':   m.user.id,
                'username':  m.user.username,
                'name':      m.user.get_full_name() or m.user.username,
                'bio':       m.bio[:200],
                'specialty': m.mentor_specialty or '',
                'specialty_display': specialty_text,
            })

        cfg = self._cfg
        self._vectorizer = TfidfVectorizer(
            max_features=cfg['tfidf_max_features'],
            ngram_range=cfg['tfidf_ngram_range'],
        )
        self._mentor_matrix = self._vectorizer.fit_transform(corpus)
        self._mentor_meta   = meta

        self.save()
        logger.info("Índice construido con %d mentores", len(meta))
        return len(meta)

    def build_index_from_data(self, mentors_data: list[dict]) -> int:
        """
        Construye el índice desde datos en memoria (sin BD).
        Útil para pruebas o entrenamiento offline.

        Cada elemento debe tener: user_id, name, bio, specialty (opcional).
        """
        if not _SKLEARN_AVAILABLE:
            raise ImportError("Instala scikit-learn: pip install scikit-learn")

        preprocessor = get_preprocessor()
        corpus = []
        meta   = []

        for m in mentors_data:
            raw = f"{m.get('bio', '')} {m.get('experience', '')} {m.get('specialty', '')}"
            corpus.append(preprocessor.transform(raw))
            meta.append({
                'user_id':          m.get('user_id'),
                'username':         m.get('username', ''),
                'name':             m.get('name', ''),
                'bio':              m.get('bio', '')[:200],
                'specialty':        m.get('specialty', ''),
                'specialty_display': m.get('specialty_display', ''),
            })

        cfg = self._cfg
        self._vectorizer = TfidfVectorizer(
            max_features=cfg['tfidf_max_features'],
            ngram_range=cfg['tfidf_ngram_range'],
        )
        self._mentor_matrix = self._vectorizer.fit_transform(corpus)
        self._mentor_meta   = meta

        self.save()
        return len(meta)

    # ── Recomendación ─────────────────────────────────

    def recommend(self, project_description: str, project_category: str = '',
                  top_k: int | None = None) -> list[dict]:
        """
        Recomienda los mentores más compatibles para un proyecto.

        Parámetros
        ----------
        project_description : Descripción del proyecto
        project_category    : Categoría del proyecto (para bonus de especialidad)
        top_k               : Número de resultados (por defecto usa config)

        Retorna
        -------
        list[dict] ordenada por score descendente, con:
          - user_id, name, bio, specialty_display
          - similarity : float [0, 1]  (similitud coseno pura)
          - score      : float [0, 1+] (similitud + bonus especialidad)
          - match_pct  : int           (score * 100, para display)
        """
        if not self.is_ready():
            return []

        if top_k is None:
            top_k = self._cfg['top_k']

        preprocessor = get_preprocessor()
        query_clean  = preprocessor.transform(project_description)
        query_vec    = self._vectorizer.transform([query_clean])

        # Calcular similitud coseno entre proyecto y todos los mentores
        # shape: (1, n_mentors)
        sims = cosine_similarity(query_vec, self._mentor_matrix).flatten()

        # Aplicar bonus si la especialidad del mentor coincide con la categoría
        specialty_bonus = self._cfg['specialty_bonus']
        cat_lower = project_category.lower()

        results = []
        for idx, sim in enumerate(sims):
            meta   = self._mentor_meta[idx]
            bonus  = specialty_bonus if cat_lower and cat_lower in meta['specialty'].lower() else 0.0
            score  = float(sim) + bonus

            results.append({
                **meta,
                'similarity': round(float(sim), 4),
                'score':      round(score, 4),
                'match_pct':  min(int(score * 100), 100),
            })

        # Ordenar por score y retornar top-k
        results.sort(key=lambda r: r['score'], reverse=True)
        return results[:top_k]


# ── Singleton ────────────────────────────────────────
_recommender: MentorRecommender | None = None


def get_recommender() -> MentorRecommender:
    global _recommender
    if _recommender is None:
        _recommender = MentorRecommender()
    return _recommender


def rebuild_mentor_index() -> int:
    """Reconstruye el índice desde la BD y retorna el número de mentores."""
    global _recommender
    rec = get_recommender()
    count = rec.build_index()
    return count
