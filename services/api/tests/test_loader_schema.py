"""Loader/schema sanity checks (no database needed)."""

from pathlib import Path
import importlib.util

DB = Path(__file__).resolve().parent.parent / "db" / "schema.sql"


def test_schema_defines_all_tables():
    sql = DB.read_text(encoding="utf-8")
    for table in ("bank", "collection_run", "product", "document",
                  "document_version"):
        assert f"CREATE TABLE IF NOT EXISTS {table} (" in sql, table


def test_schema_versioning_constraint():
    sql = DB.read_text(encoding="utf-8")
    # one immutable version per content hash — the 약관 개정 diff source
    assert "UNIQUE (document_id, sha256)" in sql
    assert "UNIQUE (bank_code, product_code)" in sql
    assert "UNIQUE (product_id, form_id)" in sql


def test_loader_module_parses():
    spec = importlib.util.spec_from_file_location(
        "load_postgres",
        Path(__file__).resolve().parent.parent / "scripts" / "load_postgres.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert callable(mod.load_manifest)
