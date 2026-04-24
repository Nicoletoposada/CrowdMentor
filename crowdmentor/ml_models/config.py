"""
Configuración central del sistema de IA de CrowdMentor.
Todos los hiperparámetros y rutas se definen aquí para
facilitar la experimentación y reproducibilidad.
"""
from pathlib import Path

# ── Rutas ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / 'saved_models'
DATASETS_DIR = BASE_DIR / 'datasets'

MODELS_DIR.mkdir(exist_ok=True)
DATASETS_DIR.mkdir(exist_ok=True)

# ── Archivos de modelos serializados ───────────────────
SUCCESS_PREDICTOR_PATH   = MODELS_DIR / 'success_predictor.joblib'
MENTOR_VECTORIZER_PATH   = MODELS_DIR / 'mentor_vectorizer.joblib'
MENTOR_MATRIX_PATH       = MODELS_DIR / 'mentor_matrix.joblib'
ADVISOR_VECTORIZER_PATH  = MODELS_DIR / 'advisor_vectorizer.joblib'
ADVISOR_CORPUS_PATH      = MODELS_DIR / 'advisor_corpus.joblib'

# ── Hiperparámetros: Predictor de Éxito ───────────────
# Módulo 1 — Regresión Logística con TF-IDF
SUCCESS_PREDICTOR = {
    # TF-IDF
    'tfidf_max_features': 8000,       # Vocabulario máximo
    'tfidf_ngram_range': (1, 2),      # Unigramas y bigramas
    'tfidf_min_df': 2,                # Ignorar términos que aparecen menos de 2 veces
    'tfidf_sublinear_tf': True,       # Usar log(1+TF) en vez de TF bruto

    # Regresión Logística
    'C': 1.0,                         # Inverso de la regularización L2
    'max_iter': 1000,
    'solver': 'lbfgs',
    'class_weight': 'balanced',       # Compensar desbalance de clases

    # Umbral de decisión
    'threshold': 0.50,
}

# ── Hiperparámetros: Recomendador de Mentores ─────────
# Módulo 2 — Filtrado basado en contenido (coseno)
MENTOR_RECOMMENDER = {
    'tfidf_max_features': 5000,
    'tfidf_ngram_range': (1, 2),
    'top_k': 5,                       # Número de mentores recomendados
    'specialty_bonus': 0.25,          # Bonus si la especialidad coincide
}

# ── Hiperparámetros: Asesor de Mejoras ────────────────
# Módulo 3 — Recuperación basada en contenido (coseno)
ADVISOR = {
    'tfidf_max_features': 5000,
    'tfidf_ngram_range': (1, 2),
    'top_k_similar': 10,              # Proyectos similares exitosos a recuperar
    'min_similarity': 0.10,           # Similitud mínima para incluir un proyecto
}

# ── Preprocesador NLP ─────────────────────────────────
PREPROCESSOR = {
    'language': 'spanish',
    'stemming': True,                 # Activar SnowballStemmer
    'min_token_length': 3,            # Ignorar tokens muy cortos
}
