"""Ingestion data model — stage 1 (collection batch).

Every collected record carries source metadata (URL, service code, collected
time) so downstream stages can trace evidence back to origin. These are
*collection* records, not verified product facts: nothing here is authoritative
until the fact-validation stage says so.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class ProductRecord:
    """One retail product as advertised on the bank's public site."""

    bank_code: str
    product_code: str
    product_name: str
    category_code: str          # bank-internal category, e.g. S02
    category_name: str          # e.g. 예금
    summary: str = ""           # marketing one-liner, not a fact source
    sale_start: str = ""        # YYYYMMDDHHMM as published
    sale_end: str = ""
    source_api: str = ""        # service code the record came from
    source_page: str = ""       # human-visible page URL
    raw: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DocumentRecord:
    """One terms/explanatory document attached to a product."""

    bank_code: str
    product_code: str
    form_id: str
    title: str
    category_code: str          # bank-internal doc category, e.g. F01 약관 / F03 상품설명서
    file_url: str
    local_path: Optional[str] = None
    sha256: Optional[str] = None
    bytes: Optional[int] = None
    source_api: str = ""
    raw: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CollectionManifest:
    """Run-level metadata written next to the collected files."""

    bank_code: str
    collected_at: str           # ISO-8601 with timezone
    base_dir: str
    products: list = field(default_factory=list)
    documents: list = field(default_factory=list)
    notes: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
