"""Embedding providers for RAG stage 3.

The embedder is pluggable behind one protocol so the model can be swapped
without touching the pipeline (see ADR-0004):

- ``SentenceTransformerEmbedder`` — real semantic embeddings, local model
  (Korean-capable multilingual MiniLM by default). Optional dependency:
  ``pip install sentence-transformers``.
- ``HashingEmbedder`` — deterministic feature-hashing embeddings used in
  tests and wiring checks. No network, no model download, same interface.

Vectors are L2-normalized so cosine similarity is a dot product and the
same literal (``[0.1, 0.2, ...]``) feeds either a pgvector ``vector``
column or the real[] fallback.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol, Sequence, runtime_checkable

_TOKEN = re.compile(r"[0-9A-Za-z\uAC00-\uD7A3]+")


@runtime_checkable
class Embedder(Protocol):
    """Anything that can turn texts into fixed-dim normalized vectors."""

    name: str
    dim: int

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        ...


def vector_literal(vec: Sequence[float], style: str = "vector") -> str:
    """Format a vector as a Postgres literal.

    style="vector" -> pgvector  '[0.1,0.2]'
    style="array"  -> real[]    '{0.1,0.2}'
    """
    body = ",".join(f"{x:.6g}" for x in vec)
    return "{" + body + "}" if style == "array" else "[" + body + "]"


class HashingEmbedder:
    """Deterministic feature-hashing embedder (tests / wiring checks).

    Hashes unigram+bigram tokens into ``dim`` buckets with signs and
    L2-normalizes. Same text always yields the same vector; texts sharing
    tokens point in similar directions — enough to exercise retrieval SQL
    end-to-end without semantic quality.
    """

    def __init__(self, dim: int = 384) -> None:
        if dim <= 0:
            raise ValueError("dim must be positive")
        self.dim = dim
        self.name = "hashing-%d" % dim

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._one(t) for t in texts]

    def _one(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        tokens = _TOKEN.findall(text)
        grams = tokens + [f"{a}|{b}" for a, b in zip(tokens, tokens[1:])]
        for gram in grams:
            for salt in (b"", b"#"):
                h = hashlib.blake2b(salt + gram.encode("utf-8"), digest_size=8)
                n = int.from_bytes(h.digest(), "big")
                idx = n % self.dim
                sign = 1.0 if (n >> 63) & 1 else -1.0
                vec[idx] += sign
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]


class SentenceTransformerEmbedder:
    """Local sentence-transformers embedder (the default for real runs)."""

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
                 batch_size: int = 64) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as e:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "sentence-transformers is not installed; "
                "pip install sentence-transformers or use --provider hash"
            ) from e
        self._model = SentenceTransformer(model_name)
        self._batch = batch_size
        self.dim = self._model.get_sentence_embedding_dimension()
        self.name = model_name

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        out = self._model.encode(
            list(texts),
            batch_size=self._batch,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return [[float(x) for x in row] for row in out]


def get_embedder(provider: str = "local", model: str | None = None,
                 dim: int = 384) -> Embedder:
    if provider == "hash":
        return HashingEmbedder(dim=dim)
    if provider == "local":
        return SentenceTransformerEmbedder(
            model or "paraphrase-multilingual-MiniLM-L12-v2")
    raise ValueError(f"unknown embedder provider: {provider!r}")
