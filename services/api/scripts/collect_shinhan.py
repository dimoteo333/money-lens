"""CLI: collect Shinhan Bank public product/terms data (stage 1).

Usage (from services/api):
    .venv/bin/python -m scripts.collect_shinhan --out ../../data/ingestion \
        --categories S01 S02 S03 [--no-download] [--limit N]

Output: <out>/shinhan/<YYYYMMDD>/manifest.json (+ docs/*.pdf when downloading).
Downloaded PDFs are local-only reference material — never commit them.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.ingestion.shinhan import CATEGORIES, ShinhanClient, collect_shinhan


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="data/ingestion", help="output root dir")
    ap.add_argument("--categories", nargs="+", default=["S01", "S02", "S03"],
                    choices=sorted(CATEGORIES))
    ap.add_argument("--no-download", action="store_true",
                    help="collect metadata only, skip PDF downloads")
    ap.add_argument("--limit", type=int, default=None,
                    help="max products per category (for smoke tests)")
    ap.add_argument("--delay", type=float, default=1.0,
                    help="seconds between HTTP calls (politeness)")
    args = ap.parse_args()

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)
    client = ShinhanClient(delay_seconds=args.delay)
    manifest = collect_shinhan(
        out_root,
        categories=args.categories,
        download=not args.no_download,
        client=client,
        limit_per_category=args.limit,
    )
    print(json.dumps({
        "bank": manifest["bank_code"],
        "collected_at": manifest["collected_at"],
        "products": len(manifest["products"]),
        "documents": len(manifest["documents"]),
        "manifest": str(Path(manifest["base_dir"]) / "manifest.json"),
        "downloaded": sum(1 for d in manifest["documents"] if d.get("local_path")),
        "failed_downloads": sum(1 for n in manifest["notes"] if n.startswith("download failed")),
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
