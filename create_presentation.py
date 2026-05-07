"""
Generate PowerPoint presentation for E-Commerce Customer Churn Prediction project.
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import os

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# ── Color Palette ──
DARK_BG = RGBColor(0x0F, 0x14, 0x2E)
DARK_BG_2 = RGBColor(0x1B, 0x22, 0x3F)
ACCENT_BLUE = RGBColor(0x4C, 0x78, 0xA8)
ACCENT_ORANGE = RGBColor(0xF2, 0x8E, 0x2B)
ACCENT_GREEN = RGBColor(0x59, 0xA1, 0x4F)
ACCENT_RED = RGBColor(0xE1, 0x57, 0x59)
ACCENT_TEAL = RGBColor(0x76, 0xB7, 0xB2)
ACCENT_PURPLE = RGBColor(0xAF, 0x7A, 0xA1)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xCC, 0xCC, 0xCC)
DARK_TEXT = RGBColor(0x2D, 0x2D, 0x2D)
MEDIUM_GRAY = RGBColor(0x66, 0x66, 0x66)
LIGHT_BG = RGBColor(0xF7, 0xF8, 0xFA)
SOFT_BG = RGBColor(0xEC, 0xEF, 0xF4)

# ── Team info ──
TEAM = [
    ("يوسف محمود مصطفى",        "23011657"),
    ("صالح كامل عوض كامل",      "22010122"),
    ("احمد مجدي احمد النجار",   "2401241821"),
    ("زياد مصطفي عيد داود",     "22010105"),
    ("زياد محمد عبدالمنعم محمد", "20221445711"),
]

def add_dark_bg(slide):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = DARK_BG

def add_light_bg(slide):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = LIGHT_BG

def add_textbox(slide, left, top, width, height, text, font_size=18,
                color=DARK_TEXT, bold=False, alignment=PP_ALIGN.LEFT, font_name='Calibri'):
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = alignment
    return txBox

def add_bullet_list(slide, left, top, width, height, items, font_size=16,
                    color=DARK_TEXT, spacing=Pt(6), font_name='Calibri'):
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = item
        p.font.size = Pt(font_size)
        p.font.color.rgb = color
        p.font.name = font_name
        p.space_after = spacing
        p.level = 0
    return txBox

def add_shape_box(slide, left, top, width, height, fill_color, text="",
                  font_size=14, font_color=WHITE, bold=False,
                  alignment=PP_ALIGN.CENTER, font_name='Calibri'):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    if text:
        tf = shape.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.paragraphs[0].alignment = alignment
        p = tf.paragraphs[0]
        p.text = text
        p.font.size = Pt(font_size)
        p.font.color.rgb = font_color
        p.font.bold = bold
        p.font.name = font_name
    return shape

def add_rect(slide, left, top, width, height, color):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape

def add_accent_bar(slide, top=1.1, left=0.8, width=1.5, color=None):
    add_rect(slide, left, top, width, 0.06, color or ACCENT_ORANGE)

def add_slide_header(slide, number, title):
    """Standard light-bg slide header with number, title, and accent bar."""
    add_textbox(slide, 0.8, 0.4, 1.2, 0.8, number,
                font_size=36, color=ACCENT_ORANGE, bold=True)
    add_textbox(slide, 1.9, 0.4, 11, 0.8, title,
                font_size=32, color=DARK_TEXT, bold=True)
    add_accent_bar(slide, top=1.1)

def add_footer(slide, slide_num, total, dark=False):
    """Footer with project name + page numbers."""
    color = LIGHT_GRAY if dark else MEDIUM_GRAY
    add_textbox(slide, 0.8, 7.15, 6, 0.3,
                "E-Commerce Customer Churn Prediction · DS Tools 2026",
                font_size=10, color=color)
    add_textbox(slide, 7.5, 7.15, 5.0, 0.3,
                f"{slide_num} / {total}",
                font_size=10, color=color, alignment=PP_ALIGN.RIGHT)

# We'll fill slide count after building
TOTAL_SLIDES = 14

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 1: TITLE SLIDE
# ════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_dark_bg(slide)

# Top accent strip
add_rect(slide, 0, 0, 13.333, 0.08, ACCENT_ORANGE)

# Subtle decorative shape (right side)
shape = slide.shapes.add_shape(MSO_SHAPE.OVAL,
    Inches(10.5), Inches(-1.2), Inches(5.0), Inches(5.0))
shape.fill.solid()
shape.fill.fore_color.rgb = DARK_BG_2
shape.line.fill.background()

shape = slide.shapes.add_shape(MSO_SHAPE.OVAL,
    Inches(-1.5), Inches(4.5), Inches(4.0), Inches(4.0))
shape.fill.solid()
shape.fill.fore_color.rgb = DARK_BG_2
shape.line.fill.background()

add_textbox(slide, 0.9, 1.4, 7.5, 0.5,
    "DS TOOLS · FINAL PROJECT · SPRING 2026",
    font_size=14, color=ACCENT_ORANGE, bold=True)

add_textbox(slide, 0.9, 2.0, 12.0, 1.4,
    "E-Commerce Customer",
    font_size=54, color=WHITE, bold=True)
add_textbox(slide, 0.9, 2.95, 12.0, 1.4,
    "Churn Prediction",
    font_size=54, color=ACCENT_ORANGE, bold=True)

add_textbox(slide, 0.9, 4.1, 11.5, 0.6,
    "Uncovering patterns, building models, driving retention decisions with SAS",
    font_size=20, color=LIGHT_GRAY)

# Accent bar
add_rect(slide, 0.9, 4.85, 1.5, 0.06, ACCENT_ORANGE)

add_textbox(slide, 0.9, 5.05, 11, 0.5,
    "Faculty of Computers and Data Science",
    font_size=15, color=LIGHT_GRAY)

# Key stats boxes at bottom
for i, (label, value) in enumerate([
    ("ROWS", "6,200"),
    ("FEATURES", "21 + 8 engineered"),
    ("MODELS", "Logistic + Tree"),
    ("VISUALS", "16+ charts"),
]):
    x = 0.9 + i * 3.0
    add_shape_box(slide, x, 5.85, 2.75, 1.05, DARK_BG_2,
                  f"{value}\n{label}", font_size=13, font_color=LIGHT_GRAY, bold=True)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 2: TEAM MEMBERS
# ════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_dark_bg(slide)

add_rect(slide, 0, 0, 13.333, 0.08, ACCENT_ORANGE)

add_textbox(slide, 0.9, 0.5, 8, 0.5,
    "MEET THE TEAM",
    font_size=14, color=ACCENT_ORANGE, bold=True)
add_textbox(slide, 0.9, 1.0, 11.5, 1.0,
    "Team Members",
    font_size=44, color=WHITE, bold=True)

add_rect(slide, 0.9, 2.0, 1.5, 0.06, ACCENT_ORANGE)

add_textbox(slide, 0.9, 2.2, 11.5, 0.5,
    "Five contributors · Faculty of Computers and Data Science",
    font_size=16, color=LIGHT_GRAY)

# Team cards — 5 cards in a balanced layout (3 + 2)
card_colors = [ACCENT_BLUE, ACCENT_GREEN, ACCENT_ORANGE, ACCENT_RED, ACCENT_TEAL]

# Top row — 3 cards
for i in range(3):
    x = 0.6 + i * 4.15
    name, sid = TEAM[i]
    add_shape_box(slide, x, 3.1, 3.95, 1.6, DARK_BG_2, "")
    # Side accent
    add_rect(slide, x, 3.1, 0.18, 1.6, card_colors[i])
    # Name (Arabic) - using Arial which has better Arabic support
    add_textbox(slide, x + 0.35, 3.25, 3.5, 0.7, name,
                font_size=20, color=WHITE, bold=True,
                alignment=PP_ALIGN.RIGHT, font_name='Arial')
    # ID label
    add_textbox(slide, x + 0.35, 3.95, 3.5, 0.3, "ID",
                font_size=10, color=ACCENT_ORANGE, bold=True)
    add_textbox(slide, x + 0.35, 4.2, 3.5, 0.4, sid,
                font_size=18, color=LIGHT_GRAY, font_name='Consolas')

# Bottom row — 2 cards centered
for i in range(2):
    x = 2.7 + i * 4.15
    idx = i + 3
    name, sid = TEAM[idx]
    add_shape_box(slide, x, 4.95, 3.95, 1.6, DARK_BG_2, "")
    add_rect(slide, x, 4.95, 0.18, 1.6, card_colors[idx])
    add_textbox(slide, x + 0.35, 5.10, 3.5, 0.7, name,
                font_size=20, color=WHITE, bold=True,
                alignment=PP_ALIGN.RIGHT, font_name='Arial')
    add_textbox(slide, x + 0.35, 5.80, 3.5, 0.3, "ID",
                font_size=10, color=ACCENT_ORANGE, bold=True)
    add_textbox(slide, x + 0.35, 6.05, 3.5, 0.4, sid,
                font_size=18, color=LIGHT_GRAY, font_name='Consolas')

add_footer(slide, 2, TOTAL_SLIDES, dark=True)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 3: AGENDA
# ════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_light_bg(slide)

add_textbox(slide, 0.8, 0.4, 1.2, 0.8, "00",
    font_size=36, color=ACCENT_ORANGE, bold=True)
add_textbox(slide, 1.9, 0.4, 11, 0.8, "Agenda",
    font_size=36, color=DARK_TEXT, bold=True)
add_accent_bar(slide, top=1.1)

steps = [
    ("01", "Problem Definition", "Why churn prediction matters for e-commerce", ACCENT_BLUE),
    ("02", "Data Understanding", "6,200 customers, 21 features, real-world complexity", ACCENT_BLUE),
    ("03", "Data Investigation", "Statistical exploration, distributions, correlations", ACCENT_GREEN),
    ("04", "Data Cleaning", "Missing values, outliers, inconsistencies", ACCENT_GREEN),
    ("05", "Feature Engineering", "8 new features capturing behavioral patterns", ACCENT_ORANGE),
    ("06", "Model Building", "Logistic Regression + Decision Tree comparison", ACCENT_ORANGE),
    ("07", "Model Explanation", "Odds ratios, feature importance, calibration", ACCENT_RED),
    ("08", "Business Application", "Risk tiers, revenue impact, retention ROI", ACCENT_RED),
]

for i, (num, title, desc, color) in enumerate(steps):
    row = i // 2
    col = i % 2
    x = 0.8 + col * 6.2
    y = 1.6 + row * 1.30
    add_shape_box(slide, x, y, 0.7, 0.7, color, num, font_size=20, font_color=WHITE, bold=True)
    add_textbox(slide, x + 0.85, y, 4.8, 0.4, title, font_size=18, color=DARK_TEXT, bold=True)
    add_textbox(slide, x + 0.85, y + 0.4, 4.8, 0.35, desc, font_size=13, color=MEDIUM_GRAY)

add_footer(slide, 3, TOTAL_SLIDES)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 4: PROBLEM DEFINITION
# ════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_light_bg(slide)
add_slide_header(slide, "01", "Problem Definition")

add_textbox(slide, 0.8, 1.5, 7, 0.5,
    "Why does customer churn matter?",
    font_size=22, color=ACCENT_BLUE, bold=True)

add_bullet_list(slide, 0.8, 2.1, 7.5, 3.0, [
    "Acquiring a new customer costs 5-7x more than retaining one",
    "30.5% of our customers churned — significant revenue at risk",
    "Without prediction, retention efforts are reactive and wasteful",
    "Goal: Predict churn probability for every customer, enabling",
    "   proactive, targeted retention campaigns",
], font_size=17, color=DARK_TEXT)

add_shape_box(slide, 8.5, 1.5, 4.2, 2.5, ACCENT_BLUE,
    "CLASSIFICATION PROBLEM\n\nInput: 21 customer features\nOutput: P(Churn)\nTarget: Binary (Yes/No)",
    font_size=15, font_color=WHITE)

add_shape_box(slide, 8.5, 4.3, 4.2, 2.5, DARK_BG,
    "BUSINESS OBJECTIVE\n\nIdentify at-risk customers\nBEFORE they leave\n\nPrioritize retention spend\nby predicted risk tier",
    font_size=14, font_color=LIGHT_GRAY)

add_footer(slide, 4, TOTAL_SLIDES)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 5: DATA UNDERSTANDING
# ════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_light_bg(slide)
add_slide_header(slide, "02", "Data Understanding")

add_textbox(slide, 0.8, 1.4, 5, 0.5,
    "Dataset: 6,200 e-commerce customers",
    font_size=20, color=DARK_TEXT, bold=True)

categories = [
    ("Demographic (4)", "Age, Gender, Marital Status,\nPreferred Device", ACCENT_BLUE),
    ("Behavioral (5)", "Num Complaints, Satisfaction,\nDays Since Order, Coupons, Products", ACCENT_GREEN),
    ("Financial (4)", "Monthly Charges, Total Charges,\nCashback Amount, Contract", ACCENT_ORANGE),
    ("Service (4)", "Internet Service, Online Security,\nTech Support, Payment Method", ACCENT_RED),
    ("Spatial (1)", "Warehouse to Home (km)", ACCENT_TEAL),
    ("Target (1)", "Churn: Yes (30.5%)\n           No (69.5%)", ACCENT_PURPLE),
]

for i, (cat, desc, color) in enumerate(categories):
    row = i // 3
    col = i % 3
    x = 0.8 + col * 4.0
    y = 2.1 + row * 2.05
    add_shape_box(slide, x, y, 3.6, 0.55, color, cat, font_size=15, font_color=WHITE, bold=True)
    add_textbox(slide, x + 0.15, y + 0.65, 3.4, 1.0, desc, font_size=13, color=MEDIUM_GRAY)

add_shape_box(slide, 0.8, 6.3, 11.7, 0.7, RGBColor(0xFD, 0xF0, 0xD5),
    "9 columns have missing values (≈1,100 cells, ~1.4% of data) — cleaned via median + mode imputation",
    font_size=13, font_color=RGBColor(0x85, 0x5C, 0x0C))

add_footer(slide, 5, TOTAL_SLIDES)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 6: DATA INVESTIGATION
# ════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_light_bg(slide)
add_slide_header(slide, "03", "Data Investigation — Key Findings")

findings = [
    ("Contract Type", "Strongest predictor.\nMonth-to-Month: ~45% churn\nTwo Year: ~15% churn",
     ACCENT_RED, "3x difference"),
    ("Tenure Effect", "Strong protective factor.\n<6 months: ~42% churn\n>48 months: ~18% churn",
     ACCENT_BLUE, "2.3x difference"),
    ("Payment Method", "Electronic Check users\nchurn at ~40% vs Credit\nCard users at ~25%",
     ACCENT_ORANGE, "1.6x difference"),
    ("Complaints", "3+ complaints doubles\nchurn rate. Strong dose-\nresponse relationship.",
     ACCENT_GREEN, "2x increase"),
]

for i, (title, body, color, stat) in enumerate(findings):
    x = 0.6 + i * 3.15
    add_shape_box(slide, x, 1.5, 2.9, 0.55, color, title, font_size=16, font_color=WHITE, bold=True)
    add_textbox(slide, x + 0.1, 2.15, 2.7, 1.5, body, font_size=13, color=DARK_TEXT)
    add_shape_box(slide, x + 0.3, 3.7, 2.3, 0.5, SOFT_BG,
                  stat, font_size=14, font_color=color, bold=True)

add_textbox(slide, 0.8, 4.5, 11.5, 0.5,
    "Statistical Methods Used",
    font_size=18, color=DARK_TEXT, bold=True)

add_bullet_list(slide, 0.8, 5.0, 11.5, 2.0, [
    "PROC MEANS — Descriptive statistics with skewness/kurtosis analysis",
    "PROC UNIVARIATE — Distribution fitting (Normal, Lognormal, Exponential)",
    "PROC FREQ + Chi-Square — Categorical associations with Cramer's V effect sizes",
    "PROC TTEST — Two-sample comparison of churned vs retained groups",
    "PROC CORR — Pearson correlation matrix with significance testing",
    "PROC TABULATE — Multi-dimensional cross-tabulations",
], font_size=13, color=MEDIUM_GRAY)

add_footer(slide, 6, TOTAL_SLIDES)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 7: DATA CLEANING
# ════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_light_bg(slide)
add_slide_header(slide, "04", "Data Cleaning")

add_shape_box(slide, 0.8, 1.5, 7.5, 0.5, ACCENT_BLUE,
    "Missing Values Handled (9 columns, ≈1,100 cells)",
    font_size=15, font_color=WHITE, bold=True)

missing_items = [
    "Age (180 missing, 2.9%) → Median imputation (robust to right-skew)",
    "Total_Charges (200, 3.2%) → Median imputation (contains outliers)",
    "Satisfaction_Score (150, 2.4%) → Median (ordinal, median preserves rank)",
    "Online_Security / Tech_Support → Mode imputation ('No' = most frequent)",
    "Monthly_Charges, Warehouse_KM, Days_Since_Order, Cashback → Median",
]
add_bullet_list(slide, 0.9, 2.1, 7.3, 2.5, missing_items, font_size=13, color=DARK_TEXT, spacing=Pt(4))

add_shape_box(slide, 0.8, 4.3, 7.5, 0.5, ACCENT_ORANGE,
    "Outlier Treatment (IQR Method)",
    font_size=15, font_color=WHITE, bold=True)

outlier_items = [
    "IQR fences computed: Q3 + 1.5*IQR for each variable",
    "Num_Complaints: Capped at IQR upper fence (extreme values)",
    "Warehouse_To_Home_KM: Capped at IQR upper fence",
    "Days_Since_Last_Order: Business rule cap at 365 days",
    "Total_Charges < 0: Recalculated (data entry error fix)",
]
add_bullet_list(slide, 0.9, 4.9, 7.3, 2.0, outlier_items, font_size=13, color=DARK_TEXT, spacing=Pt(4))

add_shape_box(slide, 8.8, 1.5, 3.8, 2.5, RGBColor(0xFD, 0xE0, 0xE0),
    "BEFORE\n\n1,100 missing cells\nOutliers in 3 columns\nNegative Total_Charges\nInconsistent casing",
    font_size=14, font_color=ACCENT_RED, bold=True)

add_shape_box(slide, 8.8, 4.3, 3.8, 2.5, RGBColor(0xE0, 0xF5, 0xE0),
    "AFTER\n\n0 missing cells\nOutliers capped (IQR)\nAll values valid\nConsistent formatting",
    font_size=14, font_color=ACCENT_GREEN, bold=True)

add_footer(slide, 7, TOTAL_SLIDES)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 8: FEATURE ENGINEERING
# ════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_light_bg(slide)
add_slide_header(slide, "05", "Feature Engineering — 8 New Features")

features = [
    ("Avg Charge/Month", "Total / Tenure", "Detects plan changes over time", ACCENT_BLUE),
    ("Charge Deviation", "Current - Historical Avg", "Price shock / downgrade signal", ACCENT_BLUE),
    ("Tenure Group", "5-level lifecycle bin", "New/Growing/Mature/Est./Loyal", ACCENT_GREEN),
    ("Complaint Rate", "Complaints / Tenure", "Normalized frustration metric", ACCENT_GREEN),
    ("Engagement Score", "Composite (5 inputs)", "Satisfaction + usage + recency", ACCENT_ORANGE),
    ("High Value Flag", "Charges>68 & Tenure>24", "Priority retention targets", ACCENT_ORANGE),
    ("Digital Engaged", "Digital pay + Security", "Platform investment = stickier", ACCENT_RED),
    ("Contract x Complaints", "Interaction term", "M2M complaint = urgent; 2Yr = less so", ACCENT_RED),
]

for i, (name, formula, rationale, color) in enumerate(features):
    row = i // 2
    col = i % 2
    x = 0.6 + col * 6.3
    y = 1.5 + row * 1.30

    add_shape_box(slide, x, y, 0.25, 1.05, color, "", font_size=10, font_color=WHITE)
    add_textbox(slide, x + 0.4, y, 5.5, 0.35, name, font_size=16, color=DARK_TEXT, bold=True)
    add_textbox(slide, x + 0.4, y + 0.35, 5.5, 0.3, f"Formula: {formula}", font_size=12, color=ACCENT_BLUE)
    add_textbox(slide, x + 0.4, y + 0.65, 5.5, 0.3, rationale, font_size=12, color=MEDIUM_GRAY)

add_textbox(slide, 0.8, 6.6, 11.5, 0.4,
    "All features validated with PROC TTEST — significant difference between churned/retained groups (p < 0.05)",
    font_size=12, color=MEDIUM_GRAY)

add_footer(slide, 8, TOTAL_SLIDES)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 9: MODEL BUILDING
# ════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_light_bg(slide)
add_slide_header(slide, "06", "Model Building — Two Models Compared")

add_shape_box(slide, 0.8, 1.5, 5.8, 0.6, ACCENT_BLUE,
    "MODEL 1: Logistic Regression (Primary)", font_size=17, font_color=WHITE, bold=True)
add_bullet_list(slide, 0.9, 2.2, 5.6, 3.0, [
    "PROC LOGISTIC with DESCENDING",
    "Stepwise feature selection (SLE=0.05, SLS=0.05)",
    "Reference coding for categorical variables",
    "Hosmer-Lemeshow goodness-of-fit test",
    "ROC curve + Odds Ratio plots auto-generated",
    "Two thresholds tested: 0.5 (standard) + 0.4 (recall-optimized)",
    "Model stored with STORE statement for reuse",
], font_size=13, color=DARK_TEXT, spacing=Pt(3))

add_shape_box(slide, 6.9, 1.5, 5.8, 0.6, ACCENT_GREEN,
    "MODEL 2: Decision Tree (Secondary)", font_size=17, font_color=WHITE, bold=True)
add_bullet_list(slide, 7.0, 2.2, 5.6, 3.0, [
    "PROC HPSPLIT",
    "Entropy-based splitting criterion",
    "Cost-complexity pruning (avoids overfitting)",
    "Automatic variable importance ranking",
    "Visual tree diagram generated",
    "Both models scored on same test set for fair comparison",
], font_size=13, color=DARK_TEXT, spacing=Pt(3))

add_shape_box(slide, 0.8, 5.0, 11.7, 0.6, SOFT_BG,
    "Train/Test Split: 70/30 stratified by Churn (PROC SURVEYSELECT with STRATA) — preserves class balance",
    font_size=14, font_color=DARK_TEXT)

add_textbox(slide, 0.8, 5.85, 11.5, 0.5,
    "Evaluation Metrics (computed via custom SAS macro)", font_size=16, color=DARK_TEXT, bold=True)

metrics = [
    ("Accuracy", "Overall correctness", ACCENT_BLUE),
    ("Precision", "Of predicted churners,\nhow many actually churned?", ACCENT_GREEN),
    ("Recall", "Of actual churners,\nhow many did we catch?", ACCENT_ORANGE),
    ("F1 Score", "Harmonic mean of\nPrecision and Recall", ACCENT_RED),
    ("Specificity", "True negative rate", ACCENT_TEAL),
]

for i, (name, desc, color) in enumerate(metrics):
    x = 0.6 + i * 2.5
    add_shape_box(slide, x, 6.35, 2.2, 0.7, color, f"{name}\n{desc}",
                  font_size=10, font_color=WHITE, bold=True)

add_footer(slide, 9, TOTAL_SLIDES)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 10: MODEL EXPLANATION
# ════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_light_bg(slide)
add_slide_header(slide, "07", "Model Explanation — What Drives Churn?")

add_textbox(slide, 0.8, 1.4, 6, 0.5,
    "Top Predictors (from Logistic Regression)",
    font_size=20, color=DARK_TEXT, bold=True)

predictors = [
    ("1", "Contract Type", "Month-to-Month → 3-4x higher odds vs Two Year", ACCENT_RED),
    ("2", "Tenure Months", "Each month reduces churn odds by ~2-3%", ACCENT_BLUE),
    ("3", "Num Complaints", "Each complaint increases odds by ~15-20%", ACCENT_ORANGE),
    ("4", "Payment Method", "Electronic Check → ~1.5x higher odds", ACCENT_GREEN),
    ("5", "Engagement Score", "Higher composite score = significantly lower churn", ACCENT_BLUE),
    ("6", "Online Security", "No security → higher churn probability", ACCENT_RED),
]

for i, (rank, name, impact, color) in enumerate(predictors):
    y = 2.0 + i * 0.7
    add_shape_box(slide, 0.8, y, 0.5, 0.5, color, rank,
                  font_size=18, font_color=WHITE, bold=True)
    add_textbox(slide, 1.5, y, 2.5, 0.5, name,
                font_size=16, color=DARK_TEXT, bold=True)
    add_textbox(slide, 4.0, y, 4.5, 0.5, impact,
                font_size=14, color=MEDIUM_GRAY)

add_shape_box(slide, 8.8, 1.4, 3.8, 3.0, DARK_BG,
    "MODEL CALIBRATION\n\nPredictions grouped into\ndeciles and compared\nagainst actual churn rate.\n\nPoints near the diagonal\n= well-calibrated model\n\nOur model tracks closely\nacross all probability ranges",
    font_size=13, font_color=LIGHT_GRAY)

add_shape_box(slide, 8.8, 4.7, 3.8, 1.8, SOFT_BG,
    "INTERACTION INSIGHT\n\nA complaint from a M2M\ncustomer is 2x more urgent\nthan from a 2-Year customer.\n\nThe Contract x Complaint\ninteraction feature captures this.",
    font_size=12, font_color=DARK_TEXT)

add_footer(slide, 10, TOTAL_SLIDES)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 11: BUSINESS APPLICATION
# ════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_light_bg(slide)
add_slide_header(slide, "08", "Business Application — Making It Useful")

tiers = [
    ("CRITICAL", ">70% prob", "Personal outreach +\nspecial offer", ACCENT_RED),
    ("HIGH", "50-70% prob", "Email campaign +\nloyalty discount", ACCENT_ORANGE),
    ("MEDIUM", "30-50% prob", "Engagement program +\nrecommendations", RGBColor(0xED, 0xC9, 0x49)),
    ("LOW", "<30% prob", "Standard\nnurture flow", ACCENT_GREEN),
]

for i, (tier, prob, action, color) in enumerate(tiers):
    x = 0.6 + i * 3.15
    add_shape_box(slide, x, 1.5, 2.9, 0.5, color, tier, font_size=18, font_color=WHITE, bold=True)
    add_textbox(slide, x + 0.1, 2.1, 2.7, 0.35, prob,
                font_size=14, color=DARK_TEXT, bold=True, alignment=PP_ALIGN.CENTER)
    add_textbox(slide, x + 0.1, 2.5, 2.7, 0.7, action,
                font_size=13, color=MEDIUM_GRAY, alignment=PP_ALIGN.CENTER)

add_textbox(slide, 0.8, 3.5, 11.5, 0.5,
    "Actionable Recommendations",
    font_size=20, color=DARK_TEXT, bold=True)

recs = [
    ("Contract Incentives", "Offer 15% discount for M2M → Annual upgrade. Reduces churn odds by 3-4x."),
    ("Complaint Fast-Track", "Priority resolution for high-risk customers. Each resolved complaint = ~18% lower churn."),
    ("Payment Nudging", "Incentivize Electronic Check → Credit Card switch with cashback bonus."),
    ("Engagement Programs", "Target low-Engagement_Score customers with product recs + coupons."),
    ("Revenue Protection", "Monthly revenue-at-risk dashboard by tier. Focus retention budget on Critical tier."),
]

for i, (title, desc) in enumerate(recs):
    y = 4.1 + i * 0.55
    add_shape_box(slide, 0.8, y, 0.12, 0.4, ACCENT_ORANGE, "", font_size=10, font_color=WHITE)
    add_textbox(slide, 1.1, y, 3.0, 0.4, title, font_size=14, color=DARK_TEXT, bold=True)
    add_textbox(slide, 4.2, y, 8.3, 0.4, desc, font_size=13, color=MEDIUM_GRAY)

add_shape_box(slide, 0.8, 6.95, 11.7, 0.32, RGBColor(0xE0, 0xF5, 0xE0),
    "If we retain just 10% of Critical-tier customers through targeted intervention, the model pays for itself many times over",
    font_size=12, font_color=ACCENT_GREEN, bold=True)

add_footer(slide, 11, TOTAL_SLIDES)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 12: VISUALIZATIONS OVERVIEW
# ════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_light_bg(slide)
add_slide_header(slide, "09", "Visualizations — 16+ Charts Generated")

viz_list = [
    ("Exploration (6)", [
        "1. Churn distribution bar chart",
        "2. Age distribution by churn (histogram + KDE)",
        "3. Monthly charges by contract (grouped box plot)",
        "4. Multivariate scatter matrix with prediction ellipses",
        "5. Tenure density overlay by churn",
        "6. Complaints vs satisfaction scatter (jittered)",
    ], ACCENT_BLUE),
    ("Cleaning (3)", [
        "7a. Age distribution BEFORE cleaning",
        "7b. Age distribution AFTER cleaning",
        "8. Complaint outlier box plot with IQR fence",
    ], ACCENT_GREEN),
    ("Features (3)", [
        "9. Engagement score by churn (box plot)",
        "10. Churn rate by tenure lifecycle (clustered bar)",
        "11. Contract-complaint risk density overlay",
    ], ACCENT_ORANGE),
    ("Modeling (5+)", [
        "12. Predicted probability distribution (panel)",
        "13. Model calibration plot (pred vs actual)",
        "14. Churn rate ladder by risk factors (horizontal bar)",
        "15. Risk tier distribution",
        "16. Revenue at risk by tier",
        "+ ROC curve, odds ratio, decision tree (auto-generated)",
    ], ACCENT_RED),
]

for i, (section, items, color) in enumerate(viz_list):
    x = 0.5 + i * 3.15
    add_shape_box(slide, x, 1.5, 2.9, 0.5, color, section, font_size=15, font_color=WHITE, bold=True)
    add_bullet_list(slide, x + 0.1, 2.1, 2.8, 4.5, items, font_size=10, color=DARK_TEXT, spacing=Pt(3))

add_footer(slide, 12, TOTAL_SLIDES)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 13: SAS PROCEDURES USED
# ════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_light_bg(slide)
add_slide_header(slide, "10", "SAS Procedures & Techniques")

proc_groups = [
    ("Data Management", [
        "PROC IMPORT — CSV loading",
        "PROC CONTENTS — Metadata",
        "PROC PRINT — Data preview",
        "PROC SORT — Ordering",
        "PROC EXPORT — Output CSV",
        "PROC FORMAT — Custom formats",
    ], ACCENT_BLUE),
    ("Statistical Analysis", [
        "PROC MEANS — Descriptive stats",
        "PROC UNIVARIATE — Distribution analysis",
        "PROC FREQ — Frequencies + Chi-Square",
        "PROC CORR — Correlation matrix",
        "PROC TTEST — Group comparisons",
        "PROC TABULATE — Cross-tabulations",
    ], ACCENT_GREEN),
    ("Modeling", [
        "PROC LOGISTIC — Logistic regression",
        "PROC HPSPLIT — Decision tree",
        "PROC REG — Linear regression",
        "PROC SURVEYSELECT — Stratified split",
        "PROC STDIZE — Median imputation",
        "PROC RANK — Decile ranking",
    ], ACCENT_ORANGE),
    ("Advanced Techniques", [
        "SAS Macros — Reusable code",
        "%LET — Global parameters",
        "PROC SQL — Complex queries",
        "ODS GRAPHICS — 16+ plots",
        "Interaction terms",
        "Model calibration analysis",
    ], ACCENT_RED),
]

for i, (group, items, color) in enumerate(proc_groups):
    x = 0.5 + i * 3.15
    add_shape_box(slide, x, 1.5, 2.9, 0.55, color, group, font_size=15, font_color=WHITE, bold=True)
    add_bullet_list(slide, x + 0.15, 2.2, 2.7, 4.5, items, font_size=12, color=DARK_TEXT, spacing=Pt(4))

add_textbox(slide, 0.8, 6.5, 11.5, 0.5,
    "Total: 20+ SAS procedures and techniques · 3 custom macros · 1,000+ lines of SAS code",
    font_size=14, color=MEDIUM_GRAY, bold=True, alignment=PP_ALIGN.CENTER)

add_footer(slide, 13, TOTAL_SLIDES)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 14: CONCLUSION + THANK YOU
# ════════════════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_dark_bg(slide)
add_rect(slide, 0, 0, 13.333, 0.08, ACCENT_ORANGE)

# Decorative shapes
shape = slide.shapes.add_shape(MSO_SHAPE.OVAL,
    Inches(11.0), Inches(-1.5), Inches(4.5), Inches(4.5))
shape.fill.solid()
shape.fill.fore_color.rgb = DARK_BG_2
shape.line.fill.background()

add_textbox(slide, 0.8, 0.5, 11.5, 0.5,
    "WRAP UP",
    font_size=14, color=ACCENT_ORANGE, bold=True)
add_textbox(slide, 0.8, 1.0, 11.5, 0.9,
    "Conclusion & Key Takeaways",
    font_size=40, color=WHITE, bold=True)
add_rect(slide, 0.8, 2.0, 1.5, 0.06, ACCENT_ORANGE)

takeaways = [
    "Transformed a raw, messy dataset into an actionable churn prediction system",
    "Contract type and tenure are the two most powerful churn predictors",
    "Our engineered engagement score significantly improves prediction power",
    "Logistic regression provides interpretable probability scores per customer",
    "Risk-tiered action plans enable targeted, cost-effective retention",
    "Estimated ROI: retaining 10% of critical customers justifies the program",
]

for i, text in enumerate(takeaways):
    y = 2.3 + i * 0.65
    add_shape_box(slide, 0.8, y, 0.45, 0.45, ACCENT_ORANGE,
                  str(i+1), font_size=16, font_color=WHITE, bold=True)
    add_textbox(slide, 1.5, y, 11.0, 0.5, text, font_size=16, color=LIGHT_GRAY)

add_textbox(slide, 0.8, 6.4, 11.5, 0.6,
    "Thank You",
    font_size=32, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)
add_textbox(slide, 0.8, 6.9, 11.5, 0.4,
    "Questions & Discussion",
    font_size=14, color=ACCENT_ORANGE, alignment=PP_ALIGN.CENTER)

add_footer(slide, 14, TOTAL_SLIDES, dark=True)

# ── Save ──
output_path = "/Users/zeyadzaher/DS_Tools_Final_Project/Churn_Prediction_Presentation.pptx"
prs.save(output_path)
print(f"Presentation saved to: {output_path}")
print(f"Total slides: {len(prs.slides)}")
