"""
Pipeline de Preprocesamiento NLP
=================================
Convierte texto crudo en representaciones limpias y normalizadas.

Pasos del pipeline:
  1. Minúsculas
  2. Eliminar URLs, menciones, caracteres especiales
  3. Tokenización
  4. Eliminación de stopwords (español + inglés)
  5. Stemming con SnowballStemmer
  6. Filtro por longitud mínima
"""
import re
import unicodedata

# Se descargan bajo demanda si no están presentes
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import SnowballStemmer
    from nltk.tokenize import word_tokenize
    _NLTK_AVAILABLE = True
except ImportError:
    _NLTK_AVAILABLE = False


def _ensure_nltk_data() -> None:
    """Descarga los recursos NLTK necesarios si aún no están presentes."""
    if not _NLTK_AVAILABLE:
        return
    for resource in ('stopwords', 'punkt', 'punkt_tab'):
        try:
            nltk.data.find(f'tokenizers/{resource}' if 'punkt' in resource else f'corpora/{resource}')
        except LookupError:
            nltk.download(resource, quiet=True)


class TextPreprocessor:
    """
    Preprocesador de texto para proyectos y perfiles en CrowdMentor.

    Parámetros
    ----------
    language : str
        Idioma principal ('spanish' o 'english').
    stemming : bool
        Si es True aplica SnowballStemmer al idioma indicado.
    min_token_length : int
        Longitud mínima de token para incluir en el resultado.
    """

    # Palabras de dominio empresarial/técnico que NO deben eliminarse
    DOMAIN_KEEP = {
        'startup', 'mvp', 'roi', 'b2b', 'b2c', 'app', 'api',
        'plan', 'meta', 'red', 'red', 'bajo', 'alto',
    }

    def __init__(self, language: str = 'spanish', stemming: bool = True,
                 min_token_length: int = 3):
        self.language = language
        self.stemming = stemming
        self.min_token_length = min_token_length

        _ensure_nltk_data()

        if _NLTK_AVAILABLE:
            # Combinamos stopwords en español e inglés
            self._stopwords = (
                set(stopwords.words('spanish')) |
                set(stopwords.words('english'))
            ) - self.DOMAIN_KEEP
            self._stemmer = SnowballStemmer(language) if stemming else None
        else:
            self._stopwords = set()
            self._stemmer = None

    # ── Paso 1-2: Limpieza estructural ────────────────

    @staticmethod
    def _remove_noise(text: str) -> str:
        """Elimina URLs, correos, números y caracteres no alfabéticos."""
        text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
        text = re.sub(r'\S+@\S+', ' ', text)
        text = re.sub(r'\d+', ' ', text)
        text = re.sub(r'[^a-záéíóúüñA-ZÁÉÍÓÚÜÑ\s]', ' ', text)
        return text

    @staticmethod
    def _normalize_unicode(text: str) -> str:
        """Normaliza caracteres Unicode pero preserva acentos del español."""
        return unicodedata.normalize('NFC', text)

    # ── Paso 3-6: Tokenización y filtrado ─────────────

    def _tokenize(self, text: str) -> list[str]:
        """Tokeniza usando NLTK si disponible, sino split básico."""
        if _NLTK_AVAILABLE:
            return word_tokenize(text, language=self.language)
        return text.split()

    def _filter_tokens(self, tokens: list[str]) -> list[str]:
        filtered = []
        for tok in tokens:
            if len(tok) < self.min_token_length:
                continue
            if tok in self._stopwords:
                continue
            filtered.append(tok)
        return filtered

    def _stem(self, tokens: list[str]) -> list[str]:
        if self._stemmer is None:
            return tokens
        return [self._stemmer.stem(tok) for tok in tokens]

    # ── Pipeline completo ─────────────────────────────

    def transform(self, text: str) -> str:
        """
        Aplica el pipeline NLP completo.

        Parámetros
        ----------
        text : str
            Texto crudo de entrada.

        Retorna
        -------
        str
            Texto preprocesado listo para vectorización TF-IDF.
        """
        if not isinstance(text, str) or not text.strip():
            return ''

        text = self._normalize_unicode(text)
        text = text.lower()
        text = self._remove_noise(text)

        tokens = self._tokenize(text)
        tokens = self._filter_tokens(tokens)
        if self.stemming:
            tokens = self._stem(tokens)

        return ' '.join(tokens)

    def transform_batch(self, texts: list[str]) -> list[str]:
        """Aplica transform() a una lista de textos."""
        return [self.transform(t) for t in texts]


# Instancia global reutilizable (singleton liviano)
_preprocessor: TextPreprocessor | None = None


def get_preprocessor() -> TextPreprocessor:
    """Retorna la instancia global del preprocesador."""
    global _preprocessor
    if _preprocessor is None:
        from ml_models.config import PREPROCESSOR
        _preprocessor = TextPreprocessor(**PREPROCESSOR)
    return _preprocessor
