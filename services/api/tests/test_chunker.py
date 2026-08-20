"""Chunker unit tests — no network, no database.

The PDF-mechanics test builds a tiny two-page PDF by hand (ASCII text,
Helvetica) so pdfminer reads it exactly like a real terms file: line order,
page numbers, char spans.
"""

from __future__ import annotations

from pathlib import Path

from app.ingestion.chunker import (
    Line,
    assemble_document,
    chunk_lines,
    chunk_pdf,
    extract_lines,
)


def _lines(*texts_pages):
    """texts_pages: interleaved (page, text) tuples -> Line list with spans."""
    out, offset = [], 0
    for page, text in texts_pages:
        start = offset
        out.append(Line(page, text, start, start + len(text)))
        offset += len(text) + 1
    return out


def test_article_split_and_merge():
    lines = _lines(
        (1, "제1조(목적) 이 약관은 거치식 예금 거래에 관한 사항을 정합니다."),
        (1, "제2조(적용범위) 이 예금은 예치기간을 정하고 거래를 시작할 때 만기에 찾는 예금입니다."),
        (2, "제3조(지급시기) 만기일 이후 청구할 때 지급합니다."),
        (2, "제4조(이자) 이자는 약정한 이자율로 계산합니다."),
    )
    chunks = chunk_lines(lines, target_chars=10**6)  # force single chunk
    assert len(chunks) == 1
    assert chunks[0].n_articles == 4
    assert chunks[0].page_start == 1 and chunks[0].page_end == 2
    assert chunks[0].heading.startswith("제1조")

    small = chunk_lines(lines, target_chars=70, max_chars=120)
    assert len(small) >= 2
    # headings track their first article
    headings = [c.heading for c in small]
    assert headings[0].startswith("제1조")
    # char spans are contiguous and cover the document
    doc = assemble_document(lines)
    joined = "".join(doc[c.char_start:c.char_end] for c in small)
    assert len(joined) == sum(c.char_end - c.char_start for c in small)
    for a, b in zip(small, small[1:]):
        assert a.char_end < b.char_start


def test_oversized_article_splits_at_paragraphs():
    paras = [f"{'x' * 40}" for _ in range(60)]
    # one giant article with ①②③ paragraph marks inside
    lines = _lines((1, "제1조(해지) 아래의 사항에 따릅니다."))
    offset = lines[0].char_end + 1
    marks = "①②③④⑤⑥⑦⑧⑨⑩"
    for i, p in enumerate(paras):
        text = marks[i % 10] + " " + p
        lines.append(Line(1 + i // 30, text, offset, offset + len(text)))
        offset += len(text) + 1
    chunks = chunk_lines(lines, target_chars=200, max_chars=400)
    assert all(len(c.text) <= 420 for c in chunks)  # +newlines slack
    assert all(c.n_articles == 1 for c in chunks)


def test_chunk_pdf_fixture(tmp_path: Path):
    pdf = _build_pdf(tmp_path / "terms.pdf")
    lines = extract_lines(pdf)
    # 4 text lines across 2 pages, pages numbered correctly
    assert [l.page for l in lines] == [1, 1, 2, 2]
    # offsets are contiguous into the assembled text
    doc = assemble_document(lines)
    for a, b in zip(lines, lines[1:]):
        assert a.char_end + 1 == b.char_start
    assert doc[lines[0].char_start:lines[0].char_end] == lines[0].text

    _, chunks = chunk_pdf(pdf)
    assert len(chunks) == 1  # ASCII fixture: no 제N조 marks -> single unit
    c = chunks[0]
    assert c.page_start == 1 and c.page_end == 2
    assert c.char_start == lines[0].char_start
    assert c.char_end == lines[-1].char_end


# ----------------------------------------------------------------- fixture

def _build_pdf(path: Path) -> Path:
    """Minimal valid 2-page PDF, ASCII text only."""
    lines_per_page = [
        [b"Article 1 (Purpose) these terms govern deposits.",
         b"Article 2 (Scope) maturity and payment rules follow."],
        [b"Article 3 (Interest) computed at the agreed rate.",
         b"Article 4 (Termination) early withdrawal conditions."],
    ]

    def content_for(page_lines):
        out = b""
        y = 700
        for line in page_lines:
            out += b"BT /F1 12 Tf 40 %d Td (" % y + line + b") Tj ET\n"
            y -= 24
        return out

    c1, c2 = content_for(lines_per_page[0]), content_for(lines_per_page[1])
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",                          # 1
        b"<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >>",            # 2
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 6 0 R >>",  # 3
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 7 0 R >>",  # 4
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",     # 5
        b"<< /Length %d >>\nstream\n" % len(c1) + c1 + b"endstream", # 6
        b"<< /Length %d >>\nstream\n" % len(c2) + c2 + b"endstream", # 7
    ]

    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, obj in enumerate(objs, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref_pos = len(out)
    out += f"xref\n0 {len(objs)+1}\n".encode()
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += (f"trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\n"
            f"startxref\n{xref_pos}\n%%EOF\n").encode()
    path.write_bytes(bytes(out))
    return path
