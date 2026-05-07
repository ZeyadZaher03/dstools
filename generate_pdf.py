"""Convert Project_Report.md to a styled PDF following the project style guide."""
import re
from markdown_pdf import MarkdownPdf, Section
from pathlib import Path

src = Path("/Users/zeyadzaher/DS_Tools_Final_Project/Project_Report.md")
dst = Path("/Users/zeyadzaher/DS_Tools_Final_Project/Project_Report.pdf")

# ── Style Guide CSS ──
# Font: Aptos (with safe fallbacks for systems without it)
# Body: justified, 1.15 line height, 12pt after paragraphs
# Headings: H1 16pt centered, H2 14pt, H3 12pt italic dark grey
# Tables: clean grid, gray header row, specific cell margins
# Captions: 10pt italic dark grey centered

css = """
@page { size: A4; margin: 2cm 1.8cm; }

* { box-sizing: border-box; }

body, p, li, td, th, h1, h2, h3, h4, h5, h6, div, span, code, pre, blockquote {
    font-family: "Aptos", "Aptos Display", "Segoe UI", Calibri, "Helvetica Neue", Arial, sans-serif;
}

body {
    font-size: 11pt;
    line-height: 1.15;
    color: #000000;
    text-align: justify;
    word-wrap: break-word;
    overflow-wrap: break-word;
}

/* ── Paragraphs (Justified, 12pt after) ── */
p {
    margin: 0 0 12pt 0;
    text-align: justify;
    line-height: 1.15;
}

/* ── Headings ── */
h1 {
    font-size: 16pt;
    font-weight: bold;
    color: #000000;
    margin: 24pt 0 12pt 0;
    text-align: center;
    page-break-after: avoid;
}

h2 {
    font-size: 14pt;
    font-weight: bold;
    color: #000000;
    margin: 18pt 0 6pt 0;
    text-align: left;
    page-break-after: avoid;
}

h3 {
    font-size: 12pt;
    font-weight: bold;
    font-style: italic;
    color: rgb(64, 64, 64);
    margin: 12pt 0 6pt 0;
    text-align: left;
    page-break-after: avoid;
}

h4, h5, h6 {
    font-size: 11pt;
    font-weight: bold;
    color: rgb(64, 64, 64);
    margin: 10pt 0 4pt 0;
    page-break-after: avoid;
}

/* Centered titles for Abstract and Table of Contents */
h1.centered, h2.centered, h3.centered,
h2.toc-title {
    text-align: center;
}

/* ── Lists ── */
ul, ol {
    margin: 0 0 12pt 24pt;
    padding: 0;
    text-align: justify;
}

li {
    margin: 0 0 6pt 0;
    line-height: 1.15;
    text-align: justify;
}

/* ── Inline emphasis ── */
strong { font-weight: bold; color: #000000; }
em { font-style: italic; }

a {
    color: #0563C1;
    text-decoration: underline;
}

/* ── Tables (clean grid, gray header, autofit) ── */
table {
    border-collapse: collapse;
    width: auto;
    max-width: 100%;
    margin: 8pt auto 12pt auto;
    border: 1px solid #000000;
    table-layout: auto;
    page-break-inside: avoid;
}

/* Header row.  Cell margins: top/bottom 0.04in (~2.88pt), left/right 0.07in (~5pt) */
th {
    background-color: #F2F2F2;
    color: #000000;
    font-size: 11pt;
    font-weight: bold;
    text-align: center;
    border: 1px solid #000000;
    padding: 2.88pt 5.04pt;
    word-break: break-word;
    overflow-wrap: anywhere;
}

/* Body cells.  Bottom = 0.04in margin + 6pt space after text = ~8.88pt */
td {
    font-size: 11pt;
    color: #000000;
    border: 1px solid #000000;
    padding: 2.88pt 5.04pt 8.88pt 5.04pt;
    vertical-align: top;
    text-align: left;
    word-break: break-word;
    overflow-wrap: anywhere;
    line-height: 1.15;
}

td p { margin: 0 0 6pt 0; }
td p:last-child { margin-bottom: 0; }

/* ── Captions (Figure / Table lines) ── */
.caption,
p.caption {
    font-size: 10pt;
    font-style: italic;
    color: rgb(80, 80, 80);
    text-align: center;
    margin: 4pt 0 12pt 0;
}

/* ── Code blocks ── */
code {
    font-family: "Consolas", "Menlo", "Courier New", monospace;
    font-size: 10pt;
    background-color: #F2F2F2;
    color: #000000;
    padding: 1px 4px;
    border-radius: 2px;
    word-break: break-word;
    overflow-wrap: anywhere;
}

pre {
    font-family: "Consolas", "Menlo", "Courier New", monospace;
    font-size: 9.5pt;
    background-color: #F8F8F8;
    color: #000000;
    border: 1px solid #D0D0D0;
    padding: 8pt 10pt;
    margin: 8pt 0 12pt 0;
    line-height: 1.35;
    text-align: left;
    white-space: pre-wrap;
    word-break: break-word;
    overflow-wrap: anywhere;
    page-break-inside: avoid;
}

pre code {
    background: transparent;
    padding: 0;
    font-size: 9.5pt;
    word-break: break-word;
    white-space: pre-wrap;
}

/* ── Misc ── */
hr {
    border: none;
    border-top: 1px solid #999999;
    margin: 12pt 0;
}

blockquote {
    margin: 8pt 0 12pt 16pt;
    padding-left: 12pt;
    border-left: 2pt solid #B0B0B0;
    color: rgb(64, 64, 64);
    font-style: italic;
    text-align: justify;
}
"""


def preprocess(md_text: str) -> str:
    """Apply rules that need DOM-level changes the markdown parser can't infer."""

    # 1. Center "Abstract" and "Table of Contents" headings (any level)
    md_text = re.sub(
        r'^(#{1,6})\s+(Abstract|Table of Contents)\s*$',
        lambda m: f'<h2 class="centered">{m.group(2)}</h2>',
        md_text,
        flags=re.MULTILINE | re.IGNORECASE,
    )

    # 2. Convert standalone "Figure N: ..." or "Table N: ..." paragraph lines to captions.
    #    Strict match: must start with the word, then a number, then : or . or whitespace.
    #    This avoids accidentally converting body sentences that begin with "Figure" or "Table".
    md_text = re.sub(
        r'^(Figure|Table)\s+(\d+)([:.\-]?)\s*([^\n]+)$',
        lambda m: (
            f'<p class="caption"><strong>{m.group(1)} {m.group(2)}'
            f'{m.group(3) or ":"}</strong> {m.group(4).strip()}</p>'
        ),
        md_text,
        flags=re.MULTILINE,
    )

    return md_text


# Build PDF
pdf = MarkdownPdf(toc_level=2, optimize=True)
pdf.meta["title"] = "E-Commerce Customer Churn Prediction"
pdf.meta["author"] = "DS Tools — Spring 2026 Team"
pdf.meta["subject"] = "Final Project Report"

text = src.read_text(encoding="utf-8")
text = preprocess(text)

pdf.add_section(Section(text, toc=False, paper_size="A4"), user_css=css)
pdf.save(dst)

size_kb = dst.stat().st_size / 1024
print(f"PDF saved → {dst}  ({size_kb:.1f} KB)")
