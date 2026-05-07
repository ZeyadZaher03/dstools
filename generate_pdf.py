"""Convert Project_Report.md to a styled PDF."""
from markdown_pdf import MarkdownPdf, Section
from pathlib import Path

src = Path("/Users/zeyadzaher/DS_Tools_Final_Project/Project_Report.md")
dst = Path("/Users/zeyadzaher/DS_Tools_Final_Project/Project_Report.pdf")

css = """
@page { size: A4; margin: 1.8cm 1.5cm; }

* { box-sizing: border-box; }

body {
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.55;
    color: #222222;
    word-wrap: break-word;
    overflow-wrap: break-word;
}

h1 {
    font-size: 24pt;
    color: #1a2138;
    border-bottom: 3px solid #f28e2b;
    padding-bottom: 6px;
    margin: 0 0 14px 0;
    page-break-after: avoid;
}
h2 {
    font-size: 16pt;
    color: #2c5282;
    border-bottom: 1px solid #cbd5e0;
    padding-bottom: 4px;
    margin: 22px 0 10px 0;
    page-break-after: avoid;
}
h3 {
    font-size: 13pt;
    color: #1a2138;
    margin: 16px 0 6px 0;
    page-break-after: avoid;
}
h4 {
    font-size: 11.5pt;
    color: #2d3748;
    margin: 12px 0 4px 0;
    page-break-after: avoid;
}

p { margin: 6px 0; }

ul, ol { margin: 6px 0 8px 22px; padding: 0; }
li { margin: 3px 0; }

strong { color: #1a2138; font-weight: 600; }
em { color: #4a5568; }

a { color: #2c5282; text-decoration: none; }

/* ── Tables ── */
table {
    border-collapse: collapse;
    width: 100%;
    margin: 10px 0;
    font-size: 9.5pt;
    table-layout: auto;
    word-break: break-word;
    page-break-inside: avoid;
}
th {
    background-color: #2c5282;
    color: #ffffff;
    padding: 7px 8px;
    text-align: left;
    border: 1px solid #2c5282;
    font-weight: 600;
    word-break: break-word;
}
td {
    padding: 6px 8px;
    border: 1px solid #cbd5e0;
    vertical-align: top;
    word-break: break-word;
    overflow-wrap: anywhere;
    color: #222222;
}
tr:nth-child(even) td { background-color: #f7fafc; }
td strong { color: #1a2138; }

/* ── Code ── */
code {
    background-color: #edf2f7;
    color: #2d3748;
    padding: 1px 4px;
    border-radius: 3px;
    font-family: "Menlo", "Consolas", "Courier New", monospace;
    font-size: 9pt;
    word-break: break-word;
    overflow-wrap: anywhere;
}
pre {
    background-color: #1e293b;
    color: #e2e8f0;
    padding: 10px 12px;
    border-radius: 4px;
    border-left: 3px solid #f28e2b;
    font-family: "Menlo", "Consolas", "Courier New", monospace;
    font-size: 8.5pt;
    line-height: 1.45;
    margin: 10px 0;
    white-space: pre-wrap;
    word-break: break-all;
    overflow-wrap: anywhere;
    page-break-inside: avoid;
}
pre code {
    background: transparent;
    color: #e2e8f0;
    padding: 0;
    font-size: 8.5pt;
    word-break: break-all;
    white-space: pre-wrap;
}

hr {
    border: none;
    border-top: 1px solid #cbd5e0;
    margin: 18px 0;
}

blockquote {
    border-left: 3px solid #f28e2b;
    color: #4a5568;
    padding: 4px 0 4px 12px;
    margin: 10px 0;
    font-style: italic;
    background-color: #fef5e7;
}

/* Avoid orphan headings */
h1, h2, h3, h4 { page-break-inside: avoid; }
"""

pdf = MarkdownPdf(toc_level=2, optimize=True)
pdf.meta["title"] = "E-Commerce Customer Churn Prediction"
pdf.meta["author"] = "DS Tools — Spring 2026 Team"
pdf.meta["subject"] = "Final Project Report"

text = src.read_text(encoding="utf-8")
pdf.add_section(Section(text, toc=False, paper_size="A4"), user_css=css)
pdf.save(dst)
print(f"PDF saved → {dst}  ({dst.stat().st_size/1024:.1f} KB)")
