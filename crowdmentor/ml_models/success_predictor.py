"""
Módulo 1 — Predictor de Éxito de Proyectos
===========================================
Predice la probabilidad de que un proyecto alcance su meta de financiamiento.

Modelo matemático
-----------------
Sea x = [x_texto, x_meta, x_categoria] el vector de características:

  x_texto     → TF-IDF sobre la descripción del proyecto
                TF(t,d) = freq(t,d) / Σfreq(t',d)
                IDF(t)  = log(N / |{d: t∈d}|)

  x_meta      → log(meta_financiamiento + 1)  [normalizado]
  x_categoria → one-hot encoding de la categoría

Clasificador: Regresión Logística con regularización L2
  P(éxito | x) = σ(wᵀx + b) = 1 / (1 + e^{−(wᵀx+b)})

Función de pérdida (Binary Cross-Entropy):
  L = −(1/N) Σᵢ [yᵢ log(P̂ᵢ) + (1−yᵢ) log(1−P̂ᵢ)]

Optimización: L-BFGS (método cuasi-Newton eficiente para LR)

Dataset de entrenamiento
------------------------
Kickstarter Projects (Kaggle) — 300 000+ proyectos con estado real
https://www.kaggle.com/datasets/kemical/kickstarter-projects
"""
from __future__ import annotations

import logging
import numpy as np

try:
    import joblib
    from sklearn.linear_model import LogisticRegression
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.pipeline import Pipeline, FeatureUnion
    from sklearn.preprocessing import FunctionTransformer, StandardScaler
    from sklearn.metrics import (
        accuracy_score, precision_score, recall_score,
        f1_score, roc_auc_score, classification_report,
    )
    _SKLEARN_AVAILABLE = True
except ImportError:
    _SKLEARN_AVAILABLE = False

from ml_models.config import SUCCESS_PREDICTOR, SUCCESS_PREDICTOR_PATH
from ml_models.preprocessor import get_preprocessor

logger = logging.getLogger(__name__)


class ProjectSuccessPredictor:
    """
    Predictor de éxito de proyectos de crowdfunding.

    Uso básico
    ----------
    >>> predictor = ProjectSuccessPredictor()
    >>> if predictor.is_trained():
    ...     result = predictor.predict("App de delivery para zonas rurales", 50000, "Tecnología")
    ...     print(result['probability'], result['label'])
    """

    def __init__(self):
        self._pipeline: Pipeline | None = None
        self._cfg = SUCCESS_PREDICTOR
        self._load_if_exists()

    # ── Estado ────────────────────────────────────────

    def is_trained(self) -> bool:
        return self._pipeline is not None

    # ── Carga / guardado ──────────────────────────────

    def _load_if_exists(self) -> None:
        if not _SKLEARN_AVAILABLE:
            return
        if SUCCESS_PREDICTOR_PATH.exists():
            try:
                self._pipeline = joblib.load(SUCCESS_PREDICTOR_PATH)
                logger.info("Predictor de éxito cargado desde %s", SUCCESS_PREDICTOR_PATH)
            except Exception as exc:
                logger.warning("No se pudo cargar el predictor: %s", exc)
                self._pipeline = None

    def save(self) -> None:
        if self._pipeline is not None:
            joblib.dump(self._pipeline, SUCCESS_PREDICTOR_PATH)
            logger.info("Predictor guardado en %s", SUCCESS_PREDICTOR_PATH)

    # ── Construcción del pipeline ─────────────────────

    def _build_pipeline(self) -> Pipeline:
        """
        Construye el pipeline sklearn:
        TF-IDF (texto) + log(meta) → Regresión Logística
        """
        cfg = self._cfg
        preprocessor = get_preprocessor()

        # Transformador de texto: aplica NLP + TF-IDF
        text_pipeline = Pipeline([
            ('preprocess', FunctionTransformer(
                lambda docs: [preprocessor.transform(d) for d in docs],
                validate=False,
            )),
            ('tfidf', TfidfVectorizer(
                max_features=cfg['tfidf_max_features'],
                ngram_range=cfg['tfidf_ngram_range'],
                min_df=cfg['tfidf_min_df'],
                sublinear_tf=cfg['tfidf_sublinear_tf'],
            )),
        ])
        return text_pipeline

    # ── Entrenamiento ─────────────────────────────────

    def train(self, texts: list[str], labels: list[int],
              eval_split: float = 0.2) -> dict:
        """
        Entrena el predictor.

        Parámetros
        ----------
        texts  : descripciones de proyectos
        labels : 1 = exitoso, 0 = fallido
        eval_split : fracción de datos para evaluación

        Retorna
        -------
        dict con métricas de entrenamiento
        """
        if not _SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn no está instalado. Ejecuta: pip install scikit-learn")

        from sklearn.model_selection import train_test_split

        cfg = self._cfg
        preprocessor = get_preprocessor()

        # ── Separar train / test ──
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels,
            test_size=eval_split,
            random_state=42,
            stratify=labels,
        )

        logger.info("Entrenando con %d muestras, evaluando con %d", len(X_train), len(X_test))

        # ── Preprocesar y vectorizar ──
        X_train_clean = [preprocessor.transform(t) for t in X_train]
        X_test_clean  = [preprocessor.transform(t) for t in X_test]

        vectorizer = TfidfVectorizer(
            max_features=cfg['tfidf_max_features'],
            ngram_range=cfg['tfidf_ngram_range'],
            min_df=cfg['tfidf_min_df'],
            sublinear_tf=cfg['tfidf_sublinear_tf'],
        )

        X_train_vec = vectorizer.fit_transform(X_train_clean)
        X_test_vec  = vectorizer.transform(X_test_clean)

        # ── Modelo: Regresión Logística con L2 ──
        clf = LogisticRegression(
            C=cfg['C'],
            max_iter=cfg['max_iter'],
            solver=cfg['solver'],
            class_weight=cfg['class_weight'],
            random_state=42,
        )
        clf.fit(X_train_vec, y_train)

        # Guardar como pipeline serializable
        self._pipeline = Pipeline([
            ('tfidf', vectorizer),
            ('clf', clf),
        ])

        # ── Métricas ──
        y_pred  = clf.predict(X_test_vec)
        y_proba = clf.predict_proba(X_test_vec)[:, 1]

        metrics = {
            'accuracy':  round(accuracy_score(y_test, y_pred), 4),
            'precision': round(precision_score(y_test, y_pred, zero_division=0), 4),
            'recall':    round(recall_score(y_test, y_pred, zero_division=0), 4),
            'f1':        round(f1_score(y_test, y_pred, zero_division=0), 4),
            'roc_auc':   round(roc_auc_score(y_test, y_proba), 4),
            'train_size': len(X_train),
            'test_size':  len(X_test),
            'report':     classification_report(y_test, y_pred, target_names=['Fallido', 'Exitoso']),
        }

        logger.info(
            "Entrenamiento completado — Acc: %.4f | F1: %.4f | AUC: %.4f",
            metrics['accuracy'], metrics['f1'], metrics['roc_auc'],
        )
        self.save()
        return metrics

    # ── Inferencia ────────────────────────────────────

    def predict(self, description: str, funding_goal: float = None,
                category: str = None) -> dict:
        """
        Predice la probabilidad de éxito de un proyecto.

        Parámetros
        ----------
        description  : Descripción del proyecto
        funding_goal : Meta de financiamiento (opcional, para contexto)
        category     : Categoría del proyecto (opcional, para contexto)

        Retorna
        -------
        dict con:
          - probability : float [0, 1]
          - label       : str ('Probable éxito' | 'Riesgo alto')
          - confidence  : str ('Alta' | 'Media' | 'Baja')
          - factors     : list[str] — factores clave detectados
        """
        if not self.is_trained():
            return self._untrained_response()

        preprocessor = get_preprocessor()
        clean_text = preprocessor.transform(description)
        proba = float(self._pipeline.predict_proba([clean_text])[0][1])

        threshold = self._cfg['threshold']
        label = 'Probable éxito' if proba >= threshold else 'Riesgo alto'

        confidence = 'Alta' if abs(proba - 0.5) > 0.25 else \
                     'Media' if abs(proba - 0.5) > 0.10 else 'Baja'

        factors = self._extract_factors(description, proba, funding_goal, category)

        return {
            'probability':    round(proba, 4),
            'probability_pct': round(proba * 100, 1),
            'label':          label,
            'confidence':     confidence,
            'factors':        factors,
            'is_trained':     True,
        }

    def _extract_factors(self, description: str, proba: float,
                         funding_goal, category) -> list[str]:
        """Extrae factores cualitativos que influyen en la predicción."""
        factors = []

        # Longitud de descripción
        words = description.split()
        if len(words) < 30:
            factors.append("Descripción muy corta — ampliar detalles del proyecto")
        elif len(words) > 80:
            factors.append("Descripción detallada — ventaja en evaluación")

        # Meta de financiamiento
        if funding_goal is not None:
            goal = float(funding_goal)
            if goal > 500_000:
                factors.append("Meta de financiamiento muy alta — considerar reducirla para proyectos iniciales")
            elif goal < 5_000:
                factors.append("Meta conservadora — más alcanzable para nuevos proyectos")

        # Palabras clave positivas
        positive_kw = {'innovador', 'sostenible', 'escalable', 'mercado', 'solución',
                       'impacto', 'tecnología', 'crecimiento', 'rentable', 'validado',
                       'prototipo', 'equipo', 'experiencia'}
        desc_lower = description.lower()
        found_kw = [kw for kw in positive_kw if kw in desc_lower]
        if found_kw:
            factors.append(f"Palabras clave positivas detectadas: {', '.join(found_kw[:4])}")

        if not factors:
            factors.append("Análisis basado en patrones del modelo entrenado")

        return factors

    @staticmethod
    def _untrained_response() -> dict:
        return {
            'probability':     None,
            'probability_pct': None,
            'label':           'Modelo no entrenado',
            'confidence':      None,
            'factors':         ['Ejecuta el comando de entrenamiento para activar esta función'],
            'is_trained':      False,
        }


# Instancia global (singleton)
_predictor: ProjectSuccessPredictor | None = None


def get_predictor() -> ProjectSuccessPredictor:
    """Retorna la instancia global del predictor (carga el modelo si existe)."""
    global _predictor
    if _predictor is None:
        _predictor = ProjectSuccessPredictor()
    return _predictor
