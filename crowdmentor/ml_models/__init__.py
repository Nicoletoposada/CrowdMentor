"""
CrowdMentor AI System
=====================
Sistema de Inteligencia Artificial diseñado para CrowdMentor.

Módulos:
  - config           : Configuración central (rutas, hiperparámetros)
  - preprocessor     : Pipeline NLP (tokenización, stopwords, stemming)
  - success_predictor: Predicción de éxito de proyectos (TF-IDF + LR)
  - mentor_recommender: Recomendación de mentores (similitud coseno)
  - advisor          : Asesor de mejoras (recuperación basada en contenido)
  - trainer          : Pipeline de entrenamiento unificado

Modelo matemático base
----------------------
TF-IDF:
    TF(t,d)  = frecuencia(t en d) / total_términos(d)
    IDF(t)   = log( N / |{d : t ∈ d}| )
    TF-IDF(t,d) = TF(t,d) × IDF(t)

Similitud Coseno:
    sim(A,B) = (A · B) / (‖A‖ × ‖B‖)

Regresión Logística:
    P(y=1|x) = σ(wᵀx + b) = 1 / (1 + e^{−(wᵀx+b)})
    L = −(1/N) Σ [yᵢ log(ŷᵢ) + (1−yᵢ)log(1−ŷᵢ)]
"""
