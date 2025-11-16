# numtriad/encoders/base_text_encoder.py

from typing import List
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None


class BaseTextEncoder:
    """
    Wrapper autour SentenceTransformer (ou fallback) pour produire
    un embedding v_text.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        if SentenceTransformer is None:
            raise ImportError(
                "sentence-transformers n'est pas installé. "
                "pip install sentence-transformers"
            )
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Retourne un tableau (batch, dim).
        """
        return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

    @property
    def dim(self) -> int:
        return self.model.get_sentence_embedding_dimension()
