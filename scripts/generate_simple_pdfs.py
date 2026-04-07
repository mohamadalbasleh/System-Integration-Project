from __future__ import annotations

import html
import re
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def extract_text(html_path: Path) -> list[str]:
    text = html_path.read_text(encoding="utf-8")
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", "", text)
    text = re.sub(r"(?i)</(h1|h2|h3|p|div|section|tr|table|ul|ol|li|pre)>", "\n", text)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)<li>", "- ", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = " ".join(raw_line.split())
        if not line:
            lines.append("")
            continue
        wrapped = textwrap.wrap(line, width=95) or [""]
        lines.extend(wrapped)
    while lines and not lines[-1]:
        lines.pop()
    return lines


def pdf_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_pdf(lines: list[str]) -> bytes:
    page_width = 595
    page_height = 842
    left_margin = 40
    top_start = 800
    line_height = 14
    lines_per_page = 52

    pages = [lines[i:i + lines_per_page] for i in range(0, len(lines), lines_per_page)]
    if not pages:
        pages = [[]]

    objects: list[bytes] = []

    def add_object(content: str | bytes) -> int:
        data = content.encode("latin-1", errors="replace") if isinstance(content, str) else content
        objects.append(data)
        return len(objects)

    font_obj = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    page_ids: list[int] = []
    content_ids: list[int] = []

    for page_lines in pages:
        text_lines = ["BT", f"/F1 11 Tf", f"{left_margin} {top_start} Td", f"{line_height} TL"]
        for index, line in enumerate(page_lines):
            escaped = pdf_escape(line)
            if index == 0:
                text_lines.append(f"({escaped}) Tj")
            else:
                text_lines.append("T*")
                text_lines.append(f"({escaped}) Tj")
        text_lines.append("ET")
        stream = "\n".join(text_lines).encode("latin-1", errors="replace")
        content_obj = add_object(
            f"<< /Length {len(stream)} >>\nstream\n".encode("latin-1") + stream + b"\nendstream"
        )
        content_ids.append(content_obj)
        page_ids.append(add_object(""))

    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    pages_obj = add_object(f"<< /Type /Pages /Count {len(page_ids)} /Kids [{kids}] >>")
    catalog_obj = add_object(f"<< /Type /Catalog /Pages {pages_obj} 0 R >>")

    for idx, page_id in enumerate(page_ids):
        objects[page_id - 1] = (
            f"<< /Type /Page /Parent {pages_obj} 0 R /MediaBox [0 0 {page_width} {page_height}] "
            f"/Resources << /Font << /F1 {font_obj} 0 R >> >> /Contents {content_ids[idx]} 0 R >>"
        ).encode("latin-1")

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("latin-1"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))
    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_obj} 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF"
        ).encode("latin-1")
    )
    return bytes(pdf)


def render(source_name: str, target_name: str) -> None:
    lines = extract_text(DOCS / source_name)
    pdf_bytes = build_pdf(lines)
    (DOCS / target_name).write_bytes(pdf_bytes)


def main() -> None:
    render("api-documentation-report.html", "api-documentation-report.pdf")
    render("postman-testing-evidence.html", "postman-testing-evidence.pdf")


if __name__ == "__main__":
    main()
