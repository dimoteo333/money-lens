"""Embedder + retrieval SQL tests (no model, no database)."""

import math

from app.ingestion.embedder import (
    HashingEmbedder,
    vector_literal,
    get_embedder,
)
from scripts.retrieve import similarity_expr


def test_hashing_embedder_deterministic_and_normalized():
    e = HashingEmbedder(dim=64)
    a = e.embed(["중도해지하면 이자는 어떻게 계산되나요"])
    b = e.embed(["중도해지하면 이자는 어떻게 계산되나요"])
    assert a == b
    norm = math.sqrt(sum(x * x for x in a[0]))
    assert abs(norm - 1.0) < 1e-9


def test_hashing_embedder_similarity_semantics():
    e = HashingEmbedder(dim=256)
    base = e.embed(["중도해지 이자"])[0]
    near = e.embed(["중도해지 이자 계산"])[0]
    far = e.embed(["마이홈플랜 주택청약 종합저축"])[0]
    dot = lambda u, v: sum(x * y for x, y in zip(u, v))
    assert dot(base, near) > dot(base, far)


def test_vector_literal_valid_for_both_backends():
    v = vector_literal([0.5, -0.25, 1.0])
    assert v == "[0.5,-0.25,1]"          # pgvector
    a = vector_literal([0.5, -0.25, 1.0], style="array")
    assert a == "{0.5,-0.25,1}"          # real[]


def test_embedder_factory_rejects_unknown():
    try:
        get_embedder("openai")
    except ValueError as e:
        assert "openai" in str(e)
    else:
        raise AssertionError("expected ValueError")


def test_similarity_expr_branches_on_column_type():
    v = similarity_expr("vector(384)")
    assert "<=>" in v and "%s::vector" in v
    r = similarity_expr("real[]")
    assert "ml_cosine_sim" in r and "%s::real[]" in r
