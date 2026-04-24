"""
Entrenador con Dataset de Kaggle — Kickstarter Projects
========================================================
Carga y fusiona los dos datasets públicos de Kickstarter disponibles
para entrenar el predictor de éxito con la mayor cantidad de datos.

Datasets soportados
-------------------
  ks-projects-201612.csv  (~323 000 proyectos, diciembre 2016)
  ks-projects-201801.csv  (~378 000 proyectos, enero 2018)
  → Se fusionan automáticamente y se deduplicam por ID

Columnas utilizadas
-------------------
  name          → nombre del proyecto          (texto principal)
  category      → subcategoría específica      (texto enriquecido)
  main_category → categoría principal          (texto enriquecido)
  goal          → meta de financiamiento       (bucket de texto)
  state         → successful / failed / ...
  country       → país                         (texto enriquecido)

Variable objetivo
-----------------
  y = 1  si state == 'successful'
  y = 0  si state == 'failed'
  (se ignoran: canceled, live, suspended)

Preparación de características (enriquecida sin blurb)
------------------------------------------------------
  x_texto = name + category + main_category + country + goal_bucket
  goal_bucket: token discreto según rango de meta USD
    meta_micro  (<  1 000)
    meta_baja   (<  5 000)
    meta_media  (< 20 000)
    meta_alta   (< 100 000)
    meta_grande (≥ 100 000)

Modelo
------
  Regresión Logística con regularización L2
  Evaluado con: Accuracy, Precision, Recall, F1, ROC-AUC
"""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def _goal_bucket(goal_val) -> str:
    """Convierte la meta numérica en un token descriptivo para el TF-IDF."""
    try:
        g = float(goal_val)
    except (ValueError, TypeError):
        return 'meta_desconocida'
    if g < 1_000:
        return 'meta_micro'
    if g < 5_000:
        return 'meta_baja'
    if g < 20_000:
        return 'meta_media'
    if g < 100_000:
        return 'meta_alta'
    return 'meta_grande'


def _load_single_csv(csv_path: str) -> 'pd.DataFrame':
    """Carga un CSV de Kickstarter con detección automática de encoding."""
    import pandas as pd
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {csv_path}")
    for enc in ('utf-8', 'latin-1', 'cp1252'):
        try:
            df = pd.read_csv(csv_path, encoding=enc, low_memory=False)
            df.columns = [c.lower().strip() for c in df.columns]
            return df
        except UnicodeDecodeError:
            continue
    raise ValueError(f"No se pudo decodificar: {csv_path}")


def load_kickstarter_data(
    csv_path: str | list[str],
    max_samples: int | None = 150_000,
    random_state: int = 42,
) -> tuple[list[str], list[int]]:
    """
    Carga y preprocesa uno o varios CSVs de Kickstarter (Kaggle).

    Parámetros
    ----------
    csv_path    : Ruta a un CSV, o lista/string con rutas separadas por coma.
                  Si se pasan dos datasets, se fusionan y deduplicam por ID.
    max_samples : Máximo de muestras a usar tras el balanceo (None = todas).
    random_state: Semilla para reproducibilidad del muestreo.

    Retorna
    -------
    texts  : list[str]  — texto enriquecido por proyecto
    labels : list[int]  — 1 = exitoso, 0 = fallido
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("pandas no está instalado. Ejecuta: pip install pandas")

    # ── Normalizar entrada a lista de rutas ───────────────────────────────────
    if isinstance(csv_path, str):
        paths = [p.strip() for p in csv_path.split(',') if p.strip()]
    else:
        paths = list(csv_path)

    # ── Cargar y fusionar todos los CSV ───────────────────────────────────────
    frames: list[pd.DataFrame] = []
    for p in paths:
        logger.info("Cargando %s ...", p)
        df_part = _load_single_csv(p)
        frames.append(df_part)
        logger.info("  → %d filas cargadas", len(df_part))

    df = pd.concat(frames, ignore_index=True)
    logger.info("Total tras fusión: %d filas", len(df))

    # ── Deduplicar por ID (proyectos presentes en ambos datasets) ─────────────
    id_col = next((c for c in ('id', 'projectid') if c in df.columns), None)
    if id_col:
        before = len(df)
        df = df.drop_duplicates(subset=[id_col])
        logger.info("Deduplicados por '%s': %d eliminados", id_col, before - len(df))

    # ── Filtrar solo proyectos con resultado conocido ─────────────────────────
    state_col = next((c for c in ('state', 'status') if c in df.columns), None)
    if state_col is None:
        raise ValueError("El CSV no tiene columna 'state'. Verifica el dataset.")

    df = df[df[state_col].isin(['successful', 'failed'])].copy()
    logger.info("Proyectos con resultado conocido: %d", len(df))

    if len(df) == 0:
        raise ValueError(
            "No se encontraron filas con state='successful' o 'failed'. "
            "Verifica que es el dataset de Kickstarter."
        )

    # ── Construir texto enriquecido (sin blurb, maximizando señal disponible) ─
    def build_text(row) -> str:
        parts: list[str] = []
        # Nombre del proyecto (campo principal)
        name = str(row.get('name', '') or '').strip()
        if name:
            parts.append(name)
        # Subcategoría y categoría principal → señal temática fuerte
        for col in ('category', 'main_category'):
            val = str(row.get(col, '') or '').strip()
            if val and val.lower() not in ('nan', 'none', ''):
                # Repetir 2x para dar más peso que el nombre
                parts.append(val)
                parts.append(val)
        # País → pequeña señal contextual
        country = str(row.get('country', '') or '').strip()
        if country and country.lower() not in ('nan', 'none', 'n,0"'):
            parts.append(country)
        # Bucket de meta → distingue micro-proyectos de grandes campañas
        goal_val = row.get('usd_goal_real') or row.get('goal', 0)
        parts.append(_goal_bucket(goal_val))
        return ' '.join(parts).strip()

    df['_text'] = df.apply(build_text, axis=1)
    df['_label'] = (df[state_col] == 'successful').astype(int)
    df = df[df['_text'].str.len() > 3].copy()

    # ── Balancear clases si hay desbalance severo (> 3:1) ────────────────────
    n_success = int((df['_label'] == 1).sum())
    n_failed  = int((df['_label'] == 0).sum())
    ratio = max(n_success, n_failed) / max(min(n_success, n_failed), 1)
    logger.info("Distribución bruta: %d exitosos / %d fallidos (ratio %.1f:1)",
                n_success, n_failed, ratio)

    if ratio > 3:
        logger.info("Aplicando undersampling para balancear clases...")
        minority_size = min(n_success, n_failed)
        majority_label = 1 if n_success > n_failed else 0
        df_maj = df[df['_label'] == majority_label].sample(
            minority_size, random_state=random_state
        )
        df_min = df[df['_label'] != majority_label]
        df = pd.concat([df_min, df_maj]).sample(frac=1, random_state=random_state)

    # ── Muestreo por tamaño máximo ────────────────────────────────────────────
    if max_samples and len(df) > max_samples:
        df = df.sample(max_samples, random_state=random_state)
        logger.info("Muestreo limitado a %d proyectos", max_samples)

    texts  = df['_text'].tolist()
    labels = df['_label'].tolist()
    logger.info(
        "Dataset final: %d proyectos (%d exitosos / %d fallidos)",
        len(labels), sum(labels), len(labels) - sum(labels),
    )
    return texts, labels


def describe_dataset(csv_path: str) -> dict:
    """
    Retorna estadísticas descriptivas del dataset Kickstarter.
    Útil para exploración antes del entrenamiento.
    """
    try:
        import pandas as pd
    except ImportError:
        return {'error': 'pandas no instalado'}

    try:
        df = pd.read_csv(csv_path, encoding='latin-1', low_memory=False)
    except Exception as e:
        return {'error': str(e)}

    df.columns = [c.lower().strip() for c in df.columns]
    state_col = 'state' if 'state' in df.columns else None

    stats = {
        'total_rows': len(df),
        'columns': list(df.columns),
    }

    if state_col:
        stats['state_distribution'] = df[state_col].value_counts().to_dict()

    if 'main_category' in df.columns:
        stats['top_categories'] = df['main_category'].value_counts().head(10).to_dict()

    if 'country' in df.columns:
        stats['top_countries'] = df['country'].value_counts().head(10).to_dict()

    return stats
