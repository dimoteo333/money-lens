"""Chunking stage: PDF terms documents -> provenance-preserving chunks.

Design notes
------------
- Extraction: pdfminer.six, layout order preserved, every line carries
  its page number. We rebuild the full document text and record each
  line's character span, so a chunk can always cite (page, char span).
- Boundaries: legal structure first. Korean banking terms are organised
  as 제N장 > 제N조 > ①②③ paragraphs. We cut on 조 (article) and merge
  small articles up to ``target_chars``; oversized articles are split at
  paragraph marks (①②③, 1. 2.) and finally at sentence ends. This keeps
  each chunk one legal unit — better for retrieval + citation than a
  blind sliding window, and no overlap is needed because boundaries are
  semantic.
- Provenance: chunk stores page_start/page_end and char_start/char_end
  into the assembled document text, plus the article heading.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer

# 제1조, 제1장, 부칙, 특약 제2조 등
ARTICLE_RE = re.compile(r"^\s*(제\s*\d+\s*(?:조|장|절)\s*\([^)]*\)|부칙[^\s]*|전문|부칙)")
PARA_RE = re.compile(r"^\s*[①②③④⑤⑥⑦⑧⑨⑩]")

DEFAULT_TARGET_CHARS = 900
DEFAULT_MAX_CHARS = 1600
MIN_CHARS = 60  # merge tail fragments below this into neighbours when possible


@dataclass
class Line:
    page: int          # 1-based
    text: str
    char_start: int    # offset into assembled document text
    char_end: int


@dataclass
class Chunk:
    seq: int
    heading: str
    text: str
    page_start: int
    page_end: int
    char_start: int
    char_end: int
    n_articles: int = 1
    meta: dict = field(default_factory=dict)


class ChunkingError(RuntimeError):
    pass


# ---------------------------------------------------------------- extraction

def extract_lines(pdf_path: str | Path) -> list[Line]:
    """Extract text lines in reading order with page provenance."""
    lines: list[Line] = []
    offset = 0
    try:
        for page_no, page in enumerate(extract_pages(str(pdf_path)), start=1):
            blocks = [el for el in page if isinstance(el, LTTextContainer)]
            for block in blocks:
                for raw in block.get_text().splitlines():
                    text = raw.strip()
                    if not text:
                        continue
                    start = offset
                    lines.append(Line(page_no, text, start, start + len(text)))
                    offset += len(text) + 1  # +1 for the join newline
    except Exception as e:  # corrupt PDF, encrypted, ...
        raise ChunkingError(f"{pdf_path}: {e!r}") from e
    if not lines:
        raise ChunkingError(f"{pdf_path}: no extractable text (scanned?)")
    return lines


def assemble_document(lines: list[Line]) -> str:
    return "\n".join(l.text for l in lines)


# ------------------------------------------------------------------ chunking

def _article_starts(lines: list[Line]) -> list[int]:
    """Indices of lines that begin a new legal unit."""
    starts = [0]
    for i, line in enumerate(lines[1:], start=1):
        if ARTICLE_RE.match(line.text):
            starts.append(i)
    return starts or [0]


def _make_chunk(lines: list[Line], lo: int, hi: int, seq: int, heading: str,
                n_articles: int) -> Chunk:
    part = lines[lo:hi]
    return Chunk(
        seq=seq,
        heading=heading,
        text="\n".join(l.text for l in part),
        page_start=part[0].page,
        page_end=part[-1].page,
        char_start=part[0].char_start,
        char_end=part[-1].char_end,
        n_articles=n_articles,
    )


def _split_oversized(lines: list[Line], lo: int, hi: int, max_chars: int):
    """Split one article at paragraph marks, then sentences."""
    groups: list[list[int]] = []
    cur: list[int] = []
    for i in range(lo, hi):
        if cur and PARA_RE.match(lines[i].text):
            groups.append(cur)
            cur = []
        cur.append(i)
    if cur:
        groups.append(cur)
    # merge groups until max_chars; never emit a tiny (heading-only)
    # buffer — headings ride with the body that follows them
    out: list[list[int]] = []
    buf: list[int] = []
    size = 0
    for g in groups:
        gsize = sum(len(lines[i].text) + 1 for i in g)
        if gsize > max_chars:
            parts = _split_sentences(lines, g)
            if buf and size < 40:
                parts[0] = buf + parts[0]      # heading joins first part
            elif buf:
                out.append(buf)
            buf, size = [], 0
            out.extend(parts)
            continue
        if buf and size >= 40 and size + gsize > max_chars:
            out.append(buf)
            buf, size = [], 0
        buf.extend(g)
        size += gsize
    if buf:
        if size < 40 and out:
            out[-1].extend(buf)                # trailing scrap merges back
        else:
            out.append(buf)
    return out


_SENT_END = re.compile(r"(?<=[.!?다])\s*$")


def _split_sentences(lines: list[Line], idxs: list[int]) -> list[list[int]]:
    """Sentence-level fallback for giant paragraphs (F03 설명서 prose)."""
    # keep it line-based: emit groups of whole lines up to max_chars
    out: list[list[int]] = []
    buf: list[int] = []
    size = 0
    for i in idxs:
        lsize = len(lines[i].text) + 1
        if buf and size + lsize > 800:
            out.append(buf)
            buf, size = [], 0
        buf.append(i)
        size += lsize
    if buf:
        out.append(buf)
    return out


def chunk_lines(lines: list[Line],
                target_chars: int = DEFAULT_TARGET_CHARS,
                max_chars: int = DEFAULT_MAX_CHARS) -> list[Chunk]:
    """Group article units into chunks near ``target_chars``."""
    if not lines:
        return []
    starts = _article_starts(lines)
    # extend article ranges to end-of-doc
    ranges = []
    for idx, s in enumerate(starts):
        e = starts[idx + 1] if idx + 1 < len(starts) else len(lines)
        ranges.append((s, e))

    chunks: list[Chunk] = []
    buf: list[tuple[int, int]] = []
    buf_chars = 0
    buf_heading = ""
    buf_articles = 0

    def flush():
        nonlocal buf, buf_chars, buf_heading, buf_articles
        if not buf:
            return
        lo, hi = buf[0][0], buf[-1][1]
        chunks.append(_make_chunk(lines, lo, hi, len(chunks), buf_heading,
                                  buf_articles))
        buf, buf_chars, buf_heading, buf_articles = [], 0, "", 0

    for s, e in ranges:
        heading = ARTICLE_RE.match(lines[s].text).group(1) if \
            ARTICLE_RE.match(lines[s].text) else lines[s].text[:40]
        size = sum(len(lines[i].text) + 1 for i in range(s, e))
        if size > max_chars:
            flush()
            for g in _split_oversized(lines, s, e, max_chars):
                head = heading if not chunks or chunks and True else heading
                sub = _make_chunk(lines, g[0], g[-1] + 1, 0, heading, 1)
                sub.seq = -1  # renumber below
                chunks.append(sub)
            continue
        if buf and buf_chars + size > target_chars:
            flush()
        if not buf:
            buf_heading = heading
        buf.append((s, e))
        buf_chars += size
        buf_articles += 1
    flush()

    # merge a trailing near-empty chunk (부칙 scrap, table dregs) into the
    # previous chunk so retrieval never sees noise-sized vectors
    if len(chunks) >= 2 and len(chunks[-1].text) < 40:
        last = chunks.pop()
        prev = chunks[-1]
        prev.text += "\n" + last.text
        prev.page_end = last.page_end
        prev.char_end = last.char_end
        prev.n_articles += last.n_articles

    for i, c in enumerate(chunks):
        c.seq = i
    return chunks


def chunk_pdf(pdf_path: str | Path,
              target_chars: int = DEFAULT_TARGET_CHARS,
              max_chars: int = DEFAULT_MAX_CHARS) -> tuple[str, list[Chunk]]:
    """Extract, assemble and chunk one PDF. Returns (full_text, chunks)."""
    lines = extract_lines(pdf_path)
    return assemble_document(lines), chunk_lines(lines, target_chars,
                                                 max_chars)
