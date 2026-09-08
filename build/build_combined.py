#!/usr/bin/env python3
"""STRUCTRA — Revit for Structures (Combined flagship) — full-dark premium outline.
Renders an 8-page A4 PDF with ReportLab. No network needed.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as canvas_mod
from reportlab.lib.utils import ImageReader

ROOT = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(ROOT, "fonts")
ASSETS = os.path.join(ROOT, "assets")
OUT = os.path.join(os.path.dirname(ROOT), "output", "STRUCTRA_Revit-for-Structures_Course-Outline.pdf")

W, H = A4  # 595.27 x 841.89
M = 40.0
CW = W - 2 * M  # content width

# ---------- palette ----------
BG      = HexColor("#070B14")
BG_TOP  = HexColor("#0B1222")
PANEL   = HexColor("#0D1526")
PANEL2  = HexColor("#111B31")
LINE    = HexColor("#1E2A45")
LINE2   = HexColor("#2B3A5C")
INK     = HexColor("#EDF1F7")
BODY    = HexColor("#A7B2C6")
MUTED   = HexColor("#67738D")
FAINT   = HexColor("#3B4663")
BLUE    = HexColor("#2E7CF6")
BLUE_B  = HexColor("#63A4FF")
BLUE_D  = HexColor("#12305F")
AMBER   = HexColor("#E8A33D")
AMBER_B = HexColor("#F5C169")
GHOST   = HexColor("#111A2E")
SERIF   = HexColor("#CBD5E6")

# ---------- fonts ----------
pdfmetrics.registerFont(TTFont("BC-R",  os.path.join(FONTS, "BarlowCondensed-Regular.ttf")))
pdfmetrics.registerFont(TTFont("BC-M",  os.path.join(FONTS, "BarlowCondensed-Medium.ttf")))
pdfmetrics.registerFont(TTFont("BC-SB", os.path.join(FONTS, "BarlowCondensed-SemiBold.ttf")))
pdfmetrics.registerFont(TTFont("BC-B",  os.path.join(FONTS, "BarlowCondensed-Bold.ttf")))
pdfmetrics.registerFont(TTFont("BC-XB", os.path.join(FONTS, "BarlowCondensed-ExtraBold.ttf")))
pdfmetrics.registerFont(TTFont("BC-I",  os.path.join(FONTS, "BarlowCondensed-Italic.ttf")))
pdfmetrics.registerFont(TTFont("B-R",   os.path.join(FONTS, "Barlow-Regular.ttf")))
pdfmetrics.registerFont(TTFont("B-M",   os.path.join(FONTS, "Barlow-Medium.ttf")))
pdfmetrics.registerFont(TTFont("B-SB",  os.path.join(FONTS, "Barlow-SemiBold.ttf")))
pdfmetrics.registerFont(TTFont("B-B",   os.path.join(FONTS, "Barlow-Bold.ttf")))
pdfmetrics.registerFont(TTFont("B-I",   os.path.join(FONTS, "Barlow-Italic.ttf")))
pdfmetrics.registerFont(TTFont("M-R",   os.path.join(FONTS, "IBMPlexMono-Regular.ttf")))
pdfmetrics.registerFont(TTFont("M-M",   os.path.join(FONTS, "IBMPlexMono-Medium.ttf")))
pdfmetrics.registerFont(TTFont("M-SB",  os.path.join(FONTS, "IBMPlexMono-SemiBold.ttf")))
pdfmetrics.registerFont(TTFont("N-I",   os.path.join(FONTS, "Newsreader-Italic.ttf")))
pdfmetrics.registerFont(TTFont("N-MI",  os.path.join(FONTS, "Newsreader-MediumItalic.ttf")))

# ---------- helpers ----------
def tracked_width(s, font, size, track=0):
    return pdfmetrics.stringWidth(s, font, size) + track * len(s)

def tracked(c, x, y, s, font="M-R", size=7, color=MUTED, track=0.9, anchor="start", max_w=None):
    """Draw letterspaced (tracked) text. track = extra pt per char."""
    c.saveState()
    c.setFont(font, size)
    c.setFillColor(color)
    w = tracked_width(s, font, size, track)
    if max_w and w > max_w:  # shrink tracking to fit
        track = max(0, (max_w - pdfmetrics.stringWidth(s, font, size)) / max(1, len(s)))
        w = tracked_width(s, font, size, track)
    if anchor == "end":
        x = x - w
    elif anchor == "middle":
        x = x - w / 2
    t = c.beginText(x, y)
    t.setFont(font, size)
    t.setCharSpace(track)
    t.textLine(s)
    c.drawText(t)
    c.restoreState()
    return w

def txt(c, x, y, s, font="B-R", size=9, color=BODY, anchor="start"):
    c.saveState()
    c.setFont(font, size)
    c.setFillColor(color)
    w = pdfmetrics.stringWidth(s, font, size)
    if anchor == "end":
        x -= w
    elif anchor == "middle":
        x -= w / 2
    c.drawString(x, y, s)
    c.restoreState()
    return w

def wrap_lines(text, font, size, max_w):
    words = text.split()
    lines, cur = [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if pdfmetrics.stringWidth(trial, font, size) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines

def para(c, x, y_top, text, font="B-R", size=9, leading=13.5, color=BODY, max_w=CW):
    lines = wrap_lines(text, font, size, max_w)
    c.saveState()
    c.setFont(font, size)
    c.setFillColor(color)
    y = y_top
    for ln in lines:
        c.drawString(x, y, ln)
        y -= leading
    c.restoreState()
    return y_top - y  # height used

def hairline(c, x1, y, x2, color=LINE, width=0.6):
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, y, x2, y)
    c.restoreState()

def panel(c, x, y, w, h, fill=PANEL, stroke=LINE, r=6, sw=0.7):
    c.saveState()
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(sw)
    c.roundRect(x, y, w, h, r, stroke=1, fill=1)
    c.restoreState()

def page_bg(c, glow=True):
    # subtle vertical gradient via bands
    c.saveState()
    bands = 28
    top = BG_TOP; bot = BG
    for i in range(bands):
        t = i / (bands - 1)
        r = top.red * (1 - t) + bot.red * t
        g = top.green * (1 - t) + bot.green * t
        b = top.blue * (1 - t) + bot.blue * t
        from reportlab.lib.colors import Color
        c.setFillColor(Color(r, g, b))
        c.setStrokeColor(Color(r, g, b))
        c.rect(0, H - (i + 1) * (H / bands), W, H / bands + 0.5, stroke=0, fill=1)
    # blueprint grid
    c.setStrokeColor(HexColor("#16203A"))
    c.setLineWidth(0.35)
    p = c.beginPath()
    x = 0
    while x <= W:
        p.moveTo(x, 0); p.lineTo(x, H); x += 28
    y = 0
    while y <= H:
        p.moveTo(0, y); p.lineTo(W, y); y += 28
    c.saveState()
    try: c.setStrokeAlpha(0.35)
    except Exception: pass
    c.drawPath(p, stroke=1, fill=0)
    c.restoreState()
    # NOTE: no alpha glow — transparency renders inconsistently, so the
    # gradient + grid carry the depth; crisp hairline arcs accent the corner.
    if glow:
        c.saveState()
        c.setStrokeColor(HexColor("#1B2A4D"))
        c.setLineWidth(0.7)
        c.circle(W - 40, H - 60, 120, stroke=1, fill=0)
        c.setStrokeColor(HexColor("#152238"))
        c.circle(W - 40, H - 60, 150, stroke=1, fill=0)
        c.restoreState()
    c.restoreState()

def ghost(c, s, x, y, size=150, color=None):
    c.saveState()
    c.setFont("BC-XB", size)
    c.setFillColor(color or GHOST)
    c.drawString(x, y, s)
    c.restoreState()

def top_bar(c, left="STRUCTRA TRAINING", right="AUTODESK REVIT — COURSE OUTLINE"):
    y = H - 34
    c.saveState()
    c.setFillColor(BLUE)
    c.rect(M, y - 2, 8, 8, stroke=0, fill=1)
    c.restoreState()
    tracked(c, M + 13, y, left, font="M-SB", size=7.5, color=INK, track=1.1)
    tracked(c, W - M, y, right, font="M-R", size=6.5, color=MUTED, track=0.9, anchor="end")
    hairline(c, M, y - 10, W - M, color=LINE)

def footer(c, pg, total=8, left="STRUCTRA TRAINING  ·  REVIT FOR STRUCTURES"):
    y = 30
    hairline(c, M, y + 12, W - M, color=LINE)
    tracked(c, M, y, left, font="M-R", size=6, color=MUTED, track=0.8)
    tracked(c, W - M, y, f"STRUCTRATRAINING.CO.KE   —   {pg:02d} / {total:02d}",
            font="M-R", size=6, color=MUTED, track=0.8, anchor="end")

def page_head(c, pg, kicker, kicker_color=BLUE_B):
    top_bar(c)
    y = H - 66
    tracked(c, M, y, kicker, font="M-M", size=7, color=kicker_color, track=1.2)
    return y - 10

def image_box(c, x, y_bottom, w, h, path, caption=None, sub=None, fig=None, accent=BLUE, r=5):
    """Framed image with 1px line + caption strip below inside the frame."""
    cap_h = 22 if caption else 0
    total_h = h + cap_h
    y0 = y_bottom
    # frame
    c.saveState()
    c.setStrokeColor(LINE2); c.setLineWidth(0.8)
    c.setFillColor(HexColor("#0A0F1D"))
    c.roundRect(x, y0, w, total_h, r, stroke=1, fill=1)
    # paper backdrop so portrait/odd-aspect sheets read as pinned paper
    p = c.beginPath(); p.roundRect(x + 0.8, y0 + cap_h, w - 1.6, h - 0.8, max(1, r - 1))
    c.saveState()
    c.clipPath(p, stroke=0, fill=0)
    c.setFillColor(HexColor("#F4F1EA"))
    c.rect(x, y0 + cap_h, w, h, stroke=0, fill=1)
    try:
        c.drawImage(ImageReader(path), x, y0 + cap_h, w, h - 0.6,
                    preserveAspectRatio=True, anchor="c", mask="auto")
    except Exception:
        pass
    c.restoreState()
    if caption:
        hairline(c, x + 8, y0 + cap_h - 0.5, x + w - 8, color=LINE)
        tracked(c, x + 8, y0 + 8, caption, font="M-M", size=6, color=INK, track=0.7, max_w=w - 90)
        if fig:
            tracked(c, x + w - 8, y0 + 8, fig, font="M-R", size=6, color=MUTED, track=0.7, anchor="end")
    c.restoreState()
    return total_h

def pill(c, x, y, s, font="M-SB", size=6.5, fg=white, bg=BLUE, track=0.8, pad_x=9, h=17):
    w = tracked_width(s, font, size, track) + pad_x * 2
    c.saveState()
    c.setFillColor(bg); c.setStrokeColor(bg)
    c.roundRect(x, y, w, h, h / 2, stroke=0, fill=1)
    c.restoreState()
    tracked(c, x + pad_x, y + 5.5, s, font=font, size=size, color=fg, track=track)
    return w

# ---------- curriculum data ----------
# (number, title, [subs])
CONCRETE_A = [
    ("01", "Brief overview of Revit", ["How Revit thinks", "Revit vs AutoCAD", "Why BIM wins"]),
    ("02", "Setting up the software", ["Essential libraries", "Autodesk extensions"]),
    ("03", "Beginning with Revit", ["New projects", "Templates", "Palettes · tabs · panels"]),
    ("04", "Datum elements", ["Levels", "Grids", "Propagating extents", "Grid-bubble styling", "Linking CAD for grids"]),
    ("05", "3D elements, first pass", ["Foundations", "Columns", "Beams", "Slabs"]),
]
CONCRETE_B = [
    ("06", "Columns", ["Placement", "Loading families"]),
    ("07", "Foundations", ["Hosting on columns", "Strip footings", "Eccentricity", "Basement slabs", "Family libraries"]),
    ("08", "Beams & slabs", ["Copy level-to-level", "Slab creation", "Hollow-pot & waffle"]),
    ("09", "Curved beams", ["Modelling procedure, end to end"]),
    ("10", "Beam systems & justification", ["Beam-system modelling", "Layout rules", "Justification rules", "Deselecting cleanly"]),
]
CONCRETE_C = [
    ("11", "Staircases & ramps", ["Stair types", "Architectural vs structural ramps", "Stairs modelled as ramps", "Shaft openings"]),
    ("12", "Visibility, graphics & filters", ["Graphic overrides — methods 1–4"]),
    ("13", "Roofs & trusses", ["Sloped & gable-ended roofs", "System trusses", "Custom trusses"]),
    ("14", "Reinforcement", ["Sections first", "Foundations", "Columns", "Beams", "Slabs", "Stairs", "Ramps"]),
    ("15", "Annotations", ["Dimensions", "Spot elevations", "Spot coordinates", "Spot slopes"]),
    ("16", "Section detailing", ["Breaklines", "Hatch regions", "Rebar tags", "Comments", "Element tags"]),
]
CONCRETE_D = [
    ("17", "Schedules & takeoffs", ["Bar bending schedules", "Shape images in BBS", "Material takeoffs", "Sorting & filtering"]),
    ("18", "Drawings on sheets", ["Titleblock sizes", "System blocks", "Custom blocks", "Text & fields", "Saving family templates", "Duplicates", "Placing views"]),
    ("19", "Printing to PDF", ["Sheet setup", "Single sheets", "Batch printing"]),
    ("20", "Export & handover", ["Export options", "To AutoCAD", "To analysis"]),
]

STEEL_A = [
    ("01", "Brief overview of Revit", ["How Revit thinks", "Revit vs CAD", "Why BIM wins"]),
    ("02", "Setting up the software", ["Essential libraries", "Autodesk extensions"]),
    ("03", "Beginning with Revit", ["New projects", "Templates", "Palettes · tabs · panels"]),
    ("04", "Datum elements", ["Levels", "Grids", "Elevation markers", "Propagating extents", "Grid-bubble styling", "Linking CAD"]),
]
STEEL_B = [
    ("05", "Steel columns", ["Placement", "Loading families"]),
    ("06", "Concrete columns", ["Placement", "Loading families"]),
    ("07", "Foundations", ["Hosting on columns", "Extended family libraries"]),
    ("08", "Rafters", ["Placement", "Steel beam sections", "Attaching columns", "Copying grid-to-grid"]),
    ("09", "Steel beams", ["Sections", "Floor beams", "Justification rules", "Copying", "Eaves-level beams"]),
    ("10", "Beam systems & justification", ["Beam-system modelling", "Layout rules", "Justification rules", "Deselecting"]),
]
STEEL_C = [
    ("11", "Composite beam & slab", ["Composite beams", "Composite slabs", "Cantilevered edges"]),
    ("12", "Floor openings", ["The shaft-opening tool"]),
    ("13", "Curved beams", ["Modelling procedure, end to end"]),
    ("14", "Sloped / slanted beams", ["The offset method", "Framing elevations"]),
    ("15", "Purlins & side rails", ["Reference-plane method", "Beam-system method", "Side rails"]),
    ("16", "Bracings", ["Vertical bracing", "Horizontal bracing"]),
    ("17", "Visibility, graphics & filters", ["Graphic overrides — methods 1–4", "Hiding elements"]),
    ("18", "Sections", ["Section types", "Cutting live sections"]),
    ("19", "Reinforcement", ["Cover setup", "Foundations", "Columns", "Slabs"]),
    ("20", "Splitting elements", ["Clean splits, buildable parts"]),
    ("21", "Connections — first principles", ["Uploading connections", "Applying them", "Propagating across the frame"]),
]
STEEL_D22 = ("22", "Connection types — the library", [
    "Haunch", "Apex", "Base plate", "Gusset — bracing", "Gusset — column-base",
    "Purlin / side-rail", "End plate, single-sided (simple)", "End plate, single-sided (moment)",
    "End plate, double-sided (simple)", "Fin plate", "Clip angle", "Column splice", "Custom connections",
])
STEEL_E = [
    ("23", "Fabrication & parametric cuts", ["Elements & modifiers", "Where cuts live", "Use & location"]),
    ("24", "Annotations", ["Dimensions", "Spot elevations", "Coordinates", "Slopes", "Custom bolt & plate tags"]),
    ("25", "Section detailing", ["Breaklines", "Hatch regions", "Rebar tags", "Comments", "Element tags"]),
    ("26", "Schedules & takeoffs", ["Bar bending schedules", "Shape images in BBS", "Material takeoffs", "Sorting & filtering"]),
    ("27", "Drawings on sheets", ["Titleblock sizes", "System blocks", "Custom blocks", "Text & fields", "Saving family templates", "Duplicates", "Placing views"]),
    ("28", "Printing to PDF", ["Sheet setup", "Single sheets", "Batch printing"]),
    ("29", "Export & handover", ["Export options", "To AutoCAD", "To analysis"]),
]

def module_block(c, x, y_top, w, num, title, subs, accent, sub_color=BODY):
    """One curriculum row. Returns y_bottom (below hairline)."""
    num_x = x
    tx = x + 30
    tw = w - 30
    # number
    tracked(c, num_x, y_top - 12, num, font="M-SB", size=8.5, color=accent, track=0.4)
    # title
    txt(c, tx, y_top - 12, title.upper(), font="BC-SB", size=12.5, color=INK)
    # subs
    sub_txt = "   ·   ".join(subs)
    lines = wrap_lines(sub_txt, "B-R", 8.2, tw)
    c.saveState(); c.setFont("B-R", 8.2); c.setFillColor(sub_color)
    yy = y_top - 24.5
    for ln in lines[:2]:
        c.drawString(tx, yy, ln); yy -= 10.5
    c.restoreState()
    bottom = yy - 2
    hairline(c, x, bottom, x + w, color=LINE)
    return bottom - 6

def phase_label(c, x, y_top, w, label, accent):
    tracked(c, x, y_top, label, font="M-SB", size=6.5, color=accent, track=1.0)
    lw = tracked_width(label, "M-SB", 6.5, 1.0)
    hairline(c, x + lw + 10, y_top + 2.5, x + w, color=LINE)
    return y_top - 10

def module_list(c, x, y_top, w, groups, accent):
    """groups = [(phase_label, [modules])]. Returns y_bottom."""
    y = y_top
    for label, mods in groups:
        y = phase_label(c, x, y, w, label, accent)
        for num, title, subs in mods:
            y = module_block(c, x, y + 2, w, num, title, subs, accent)
    return y

# ============================================================ PAGES
def fit_size(s, font, target_w, start=120):
    w1 = pdfmetrics.stringWidth(s, font, 1.0)
    return min(start, target_w / w1)

def p1_cover(c):
    page_bg(c, glow=True)
    top_bar(c)
    y = H - 74
    tracked(c, M, y, "STEEL & CONCRETE  ·  STRUCTURAL MODELING IN AUTODESK REVIT",
            font="M-M", size=7, color=BLUE_B, track=1.1)
    y -= 10
    # Title block — each line justified to full content width
    s1 = fit_size("REVIT FOR", "BC-XB", CW - 2, 120)
    c.saveState(); c.setFillColor(INK); c.setFont("BC-XB", s1)
    c.drawString(M - 1, y - s1 * 0.82, "REVIT FOR")
    c.restoreState()
    y = y - s1 * 0.82 - 6
    s2 = fit_size("STRUCTURES", "BC-XB", CW - 2, 120)
    c.saveState(); c.setFillColor(BLUE); c.setFont("BC-XB", s2)
    c.drawString(M - 1, y - s2 * 0.82, "STRUCTURES")
    c.restoreState()
    y = y - s2 * 0.82 - 14
    txt(c, M, y, "Build real, buildable structural models — not just pretty renders.",
        font="N-MI", size=14.5, color=SERIF)
    y -= 22
    # hero image
    ih = 288
    image_box(c, M, y - ih - 24, CW, ih, os.path.join(ASSETS, "steel-portal.jpg"),
              caption="STEEL PORTAL FRAME STRUCTURE — 3D PROJECT OVERVIEW & FRAMING ELEVATIONS",
              fig="FIG. 01", accent=BLUE)
    # floating pills over image top-left
    pill(c, M + 12, y - 22, "2 TRACKS  ·  49 MODULES", bg=BLUE)
    pill(c, M + 12, y - 43, "100% LIVE ON ZOOM", bg=HexColor("#131E36"), fg=INK)
    # 2026 stamp overlapping hero top-right
    c.saveState()
    bw, bh = 120, 44
    bx = W - M - bw + 6
    by = y - 10
    c.setFillColor(BLUE)
    p = c.beginPath()
    p.moveTo(bx + 14, by + bh); p.lineTo(bx + bw, by + bh)
    p.lineTo(bx + bw - 14, by); p.lineTo(bx, by)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.restoreState()
    txt(c, bx + 58, by + 15, "2026", font="BC-XB", size=26, color=white, anchor="middle")
    tracked(c, bx + 58, by + 6.5, "SEPT COHORT", font="M-SB", size=5.5, color=white, track=1.0, anchor="middle")
    y = y - ih - 24 - 16
    # meta strip
    hairline(c, M, y, W - M, color=LINE2)
    y -= 14
    cols = [("START", "14 SEPT 2026"), ("FORMAT", "LIVE · ONLINE"), ("RHYTHM", "WEEKDAY EVENINGS"), ("FEE", "KSH 2,500 / TRACK")]
    colw = CW / 4
    for i, (k, v) in enumerate(cols):
        x = M + i * colw
        if i:
            c.saveState(); c.setStrokeColor(LINE); c.setLineWidth(0.6)
            c.line(x, y - 14, x, y + 12); c.restoreState()
        tracked(c, x + (10 if i else 0), y, k, font="M-R", size=6.5, color=MUTED, track=1.1)
        txt(c, x + (10 if i else 0), y - 15, v, font="BC-SB", size=13.5,
            color=AMBER_B if k == "FEE" else INK)
    y -= 32
    # inside index strip
    idx = [("01", "PROGRAM", "p. 2"), ("02", "CONCRETE", "p. 3"), ("03", "STEEL", "p. 5"), ("04", "JOIN", "p. 8")]
    iw = CW / 4
    for i, (n, t, pg) in enumerate(idx):
        x = M + i * iw
        panel(c, x + (4 if i else 0), y - 26, iw - (4 if i else 4), 26, fill=PANEL, stroke=LINE, r=5)
        tracked(c, x + (14 if i else 10), y - 10, n, font="M-SB", size=7, color=BLUE_B, track=0.5)
        tracked(c, x + (14 if i else 10) + 20, y - 10, t, font="M-M", size=7, color=INK, track=0.8)
        tracked(c, x + iw - 12, y - 10, pg, font="M-R", size=7, color=MUTED, track=0.5, anchor="end")
    footer(c, 1)

def p2_overview(c):
    page_bg(c, glow=False)
    y = page_head(c, 2, "01  —  THE PROGRAM")
    ghost(c, "01", W - M - 92, y - 148, size=100)
    txt(c, M, y - 34, "One program.", font="BC-XB", size=46, color=INK)
    # mixed line: "Two " condensed + "buildable" serif italic + " tracks."
    y2 = y - 78
    c.saveState()
    c.setFont("BC-XB", 46); c.setFillColor(INK)
    c.drawString(M, y2, "Two ")
    w1 = pdfmetrics.stringWidth("Two ", "BC-XB", 46)
    c.setFont("N-MI", 40); c.setFillColor(BLUE_B)
    c.drawString(M + w1, y2 + 3, "buildable")
    w2 = pdfmetrics.stringWidth("buildable", "N-MI", 40)
    c.setFont("BC-XB", 46); c.setFillColor(INK)
    c.drawString(M + w1 + w2 + 8, y2, "tracks.")
    c.restoreState()
    y = y2 - 24
    used = para(c, M, y, "Revit for Structures is a hands-on Autodesk Revit program for engineering students and early-career professionals who want to build real, buildable structural models. Two focused tracks — Reinforced Concrete and Steel — each run from first launch to finished documentation: modelling, reinforcement and connections, schedules, and sheets that print clean.",
                font="B-R", size=9.3, leading=14.2, color=BODY, max_w=CW)
    y = y - used - 12
    # outcomes 4-up
    outcomes = [
        ("01", "Model the whole frame", "Columns to slabs, rafters to bracing."),
        ("02", "Detail like a pro", "Rebar, tags, bolts, plates & cuts."),
        ("03", "Quantify & schedule", "Bar bending schedules & takeoffs."),
        ("04", "Document & deliver", "Sheets, PDFs, CAD & analysis handoff."),
    ]
    colw = (CW - 3 * 10) / 4
    oy = y
    for i, (n, t, d) in enumerate(outcomes):
        x = M + i * (colw + 10)
        panel(c, x, oy - 64, colw, 64, fill=PANEL, stroke=LINE, r=6)
        tracked(c, x + 10, oy - 16, n, font="M-SB", size=7, color=BLUE_B, track=0.6)
        txt(c, x + 10, oy - 31, t, font="B-SB", size=8.2, color=INK)
        txt(c, x + 10, oy - 44, d.split(",")[0] + ("," if "," in d else ""), font="B-R", size=7.4, color=BODY)
        if "," in d:
            txt(c, x + 10, oy - 54, d.split(",", 1)[1].strip(), font="B-R", size=7.4, color=BODY)
    y = oy - 64 - 16
    tracked(c, M, y, "WHAT YOU WILL MODEL  —  REAL, STUDENT-GRADE OUTPUT", font="M-M", size=7, color=MUTED, track=1.1)
    y -= 10
    # 2x2 gallery
    gw, gap = (CW - 10) / 2, 10
    gh = 128
    gal = [
        (os.path.join(ASSETS, "tower-21.jpg"), "21 FLOORS + 2 BASEMENTS", "Concrete tower frame", "FIG. 02"),
        (os.path.join(ASSETS, "tower-32.jpg"), "32 FLOORS + 4 BASEMENTS", "Curved tower + levels", "FIG. 03"),
        (os.path.join(ASSETS, "steel-portal.jpg"), "STEEL PORTAL FRAME STRUCTURE", "Portal frame + elevations", "FIG. 04"),
        (os.path.join(ASSETS, "steel-connections.jpg"), "STEEL CONNECTIONS", "Beam end connections", "FIG. 05"),
    ]
    # row 1
    for i in range(2):
        x = M + i * (gw + gap)
        image_box(c, x, y - gh - 22, gw, gh, gal[i][0], caption=gal[i][1], fig=gal[i][3])
    y = y - gh - 22 - 10
    for i in range(2, 4):
        x = M + (i - 2) * (gw + gap)
        image_box(c, x, y - gh - 22, gw, gh, gal[i][0], caption=gal[i][1], fig=gal[i][3])
    y = y - gh - 22 - 14
    # track chooser
    tracked(c, M, y + 4, "CHOOSE YOUR TRACK  —  OR TAKE BOTH", font="M-M", size=7, color=MUTED, track=1.1)
    y -= 8
    tw = (CW - 10) / 2
    for i, (tag, title, sub, pgref, acc) in enumerate([
        ("TRACK 01", "REINFORCED CONCRETE", "20 modules · Grids → BBS  ·  p. 3", "03", AMBER),
        ("TRACK 02", "STEEL STRUCTURES", "29 modules · Columns → Connections  ·  p. 5", "05", BLUE),
    ]):
        x = M + i * (tw + 10)
        panel(c, x, y - 56, tw, 56, fill=PANEL, stroke=LINE, r=6)
        c.saveState(); c.setFillColor(acc)
        c.roundRect(x, y - 56, 4, 56, 2, stroke=0, fill=1); c.restoreState()
        tracked(c, x + 14, y - 17, tag, font="M-SB", size=6.5, color=acc, track=1.0)
        txt(c, x + 14, y - 35, title, font="BC-SB", size=17, color=INK)
        txt(c, x + 14, y - 48, sub, font="B-R", size=7.6, color=BODY)
    footer(c, 2)

def p3_concrete_a(c):
    page_bg(c, glow=False)
    y = page_head(c, 3, "02  —  TRACK 01  ·  REINFORCED CONCRETE  ·  20 MODULES", kicker_color=AMBER_B)
    ghost(c, "RC", W - M - 148, y - 130, size=102)
    tracked(c, M, y - 6, "FROM DATUMS TO DOCUMENTATION", font="M-R", size=7, color=MUTED, track=1.2)
    txt(c, M, y - 40, "Reinforced concrete,", font="BC-XB", size=42, color=INK)
    c.saveState(); c.setFont("BC-XB", 42); c.setFillColor(INK)
    c.drawString(M, y - 78, "modelled to the ")
    w1 = pdfmetrics.stringWidth("modelled to the ", "BC-XB", 42)
    c.setFillColor(AMBER); c.drawString(M + w1, y - 78, "rebar.")
    c.restoreState()
    y = y - 96
    # image band
    ih = 110
    image_box(c, M, y - ih - 22, CW, ih, os.path.join(ASSETS, "tower-21.jpg"),
              caption="21 FLOORS + 2 BASEMENTS — REINFORCED-CONCRETE TOWER FRAME, MODELLED IN REVIT",
              fig="FIG. 02", accent=AMBER)
    y = y - ih - 22 - 14
    y = module_list(c, M, y, CW, [
        ("A  ·  GROUNDWORK  —  01–05", CONCRETE_A),
        ("B  ·  MODELLING THE FRAME  —  06–10", CONCRETE_B),
    ], AMBER)
    footer(c, 3)

def p4_concrete_b(c):
    page_bg(c, glow=False)
    y = page_head(c, 4, "02  —  TRACK 01  ·  REINFORCED CONCRETE, CONTINUED", kicker_color=AMBER_B)
    ghost(c, "C2", W - M - 148, y - 130, size=102)
    txt(c, M, y - 38, "Detail, reinforce,", font="BC-XB", size=40, color=INK)
    c.saveState(); c.setFont("BC-XB", 40); c.setFillColor(INK)
    c.drawString(M, y - 74, "then ")
    w1 = pdfmetrics.stringWidth("then ", "BC-XB", 40)
    c.setFillColor(AMBER); c.drawString(M + w1, y - 74, "deliver.")
    c.setFillColor(INK)
    w2 = pdfmetrics.stringWidth("deliver.", "BC-XB", 40)
    c.setFont("N-MI", 17); c.setFillColor(SERIF)
    c.drawString(M + w1 + w2 + 14, y - 70, "Stairs, rebar, tags, sheets.")
    c.restoreState()
    y = y - 92
    ih = 110
    image_box(c, M, y - ih - 22, CW, ih, os.path.join(ASSETS, "tower-32.jpg"),
              caption="32 FLOORS + 4 BASEMENTS — CURVED TOWER WITH LEVELS & GRIDS, MODELLED IN REVIT",
              fig="FIG. 03", accent=AMBER)
    y = y - ih - 22 - 14
    y = module_list(c, M, y, CW, [
        ("C  ·  DETAIL & REINFORCE  —  11–16", CONCRETE_C),
        ("D  ·  DOCUMENT & DELIVER  —  17–20", CONCRETE_D),
    ], AMBER)
    footer(c, 4)

def p5_steel_a(c):
    page_bg(c, glow=False)
    y = page_head(c, 5, "03  —  TRACK 02  ·  STEEL STRUCTURES  ·  29 MODULES", kicker_color=BLUE_B)
    ghost(c, "ST", W - M - 138, y - 130, size=102)
    tracked(c, M, y - 6, "COLUMNS · RAFTERS · BEAMS · BRACING", font="M-R", size=7, color=MUTED, track=1.2)
    txt(c, M, y - 40, "Steel, from first", font="BC-XB", size=42, color=INK)
    c.saveState(); c.setFont("BC-XB", 42); c.setFillColor(INK)
    c.drawString(M, y - 78, "column to custom ")
    w1 = pdfmetrics.stringWidth("column to custom ", "BC-XB", 42)
    c.setFillColor(BLUE); c.drawString(M + w1, y - 78, "connection.")
    c.restoreState()
    y = y - 96
    ih = 102
    image_box(c, M, y - ih - 22, CW, ih, os.path.join(ASSETS, "steel-portal.jpg"),
              caption="STEEL PORTAL FRAME STRUCTURE — EAVES, APEX & FRAMING ELEVATIONS, MODELLED IN REVIT",
              fig="FIG. 04", accent=BLUE)
    y = y - ih - 22 - 14
    y = module_list(c, M, y, CW, [
        ("A  ·  GROUNDWORK  —  01–04", STEEL_A),
        ("B  ·  THE STEEL FRAME  —  05–10", STEEL_B),
    ], BLUE_B)
    footer(c, 5)

def p6_steel_b(c):
    page_bg(c, glow=False)
    y = page_head(c, 6, "03  —  TRACK 02  ·  STEEL, CONTINUED", kicker_color=BLUE_B)
    ghost(c, "S2", W - M - 138, y - 134, size=102)
    txt(c, M, y - 38, "Roofs, openings,", font="BC-XB", size=40, color=INK)
    c.saveState(); c.setFont("BC-XB", 40); c.setFillColor(INK)
    c.drawString(M, y - 74, "bracing & ")
    w1 = pdfmetrics.stringWidth("bracing & ", "BC-XB", 40)
    c.setFillColor(BLUE); c.drawString(M + w1, y - 74, "views.")
    c.setFont("N-MI", 17); c.setFillColor(SERIF)
    c.drawString(M + w1 + pdfmetrics.stringWidth("views.", "BC-XB", 40) + 14, y - 70, "Composite decks to live sections.")
    c.restoreState()
    y = y - 92
    y = module_list(c, M, y, CW, [
        ("C  ·  ROOF, BRACING & VIEWS  —  11–21", STEEL_C),
    ], BLUE_B)
    # tip strip
    y -= 2
    panel(c, M, y - 46, CW, 46, fill=HexColor("#0B1428"), stroke=LINE2, r=6)
    c.saveState(); c.setFillColor(BLUE)
    c.roundRect(M, y - 46, 4, 46, 2, stroke=0, fill=1); c.restoreState()
    tracked(c, M + 16, y - 18, "NEXT  —  THE CONNECTION LIBRARY", font="M-SB", size=6.5, color=BLUE_B, track=1.0)
    txt(c, M + 16, y - 34, "Thirteen connection families plus your own customs — overleaf.", font="N-MI", size=11.5, color=SERIF)
    txt(c, W - M - 14, y - 29, "→  P. 07", font="BC-SB", size=15, color=INK, anchor="end")
    footer(c, 6)

def chips(c, x, y_top, w, items, accent=BLUE_B):
    """Flow connection-type pills. Returns y_bottom."""
    y = y_top
    cx = x
    h, gap = 16, 6
    c.saveState()
    for it in items:
        tw = pdfmetrics.stringWidth(it, "M-M", 6.3)
        pw = tw + 16
        if cx + pw > x + w:
            cx = x; y -= h + gap
        c.setStrokeColor(LINE2); c.setLineWidth(0.7); c.setFillColor(PANEL2)
        c.roundRect(cx, y - h, pw, h, h / 2, stroke=1, fill=1)
        c.setFont("M-M", 6.3); c.setFillColor(INK)
        c.drawString(cx + 8, y - h + 5.2, it)
        cx += pw + gap
    c.restoreState()
    return y - h - 4

def p7_steel_c(c):
    page_bg(c, glow=False)
    y = page_head(c, 7, "03  —  TRACK 02  ·  CONNECTIONS & DELIVERY", kicker_color=BLUE_B)
    ghost(c, "S3", W - M - 138, y - 130, size=102)
    txt(c, M, y - 38, "The connection", font="BC-XB", size=40, color=INK)
    c.saveState(); c.setFont("BC-XB", 40); c.setFillColor(BLUE)
    c.drawString(M, y - 74, "library.")
    c.setFont("N-MI", 17); c.setFillColor(SERIF)
    c.drawString(M + pdfmetrics.stringWidth("library.", "BC-XB", 40) + 14, y - 70, "Applied, propagated, detailed.")
    c.restoreState()
    y = y - 92
    # module 22 feature — panel sized to fit the chips exactly
    num, title, subs = STEEL_D22
    items = ["Main types"] + subs
    _rows, _cx, _hh, _gap = 1, 0, 16, 6
    for it in items:
        _pw = pdfmetrics.stringWidth(it, "M-M", 6.3) + 16
        if _cx + _pw > CW - 32:
            _rows += 1; _cx = 0
        _cx += _pw + _gap
    panel_h = 56 + _rows * (_hh + _gap) + 8
    panel(c, M, y - panel_h, CW, panel_h, fill=HexColor("#0B1428"), stroke=LINE2, r=8)
    tracked(c, M + 16, y - 20, "22  ·  CONNECTION TYPES — THE LIBRARY",
            font="M-SB", size=7.5, color=BLUE_B, track=1.0)
    txt(c, M + 16, y - 36, "Main types first, then every family you will meet on a real frame —",
        font="B-R", size=8.4, color=BODY)
    chips(c, M + 16, y - 50, CW - 32, items)
    # anchor note fills the panel foot
    hairline(c, M + 16, y - panel_h + 24, W - M - 16, color=LINE)
    tracked(c, M + 16, y - panel_h + 13, "APPLIED LIVE  —  MODULE 21  ·  UPLOAD  →  APPLY  →  PROPAGATE",
            font="M-R", size=6, color=MUTED, track=0.8)
    y = y - panel_h - 12
    ih = 90
    image_box(c, M, y - ih - 22, CW, ih, os.path.join(ASSETS, "steel-connections-top.jpg"),
              caption="STEEL CONNECTIONS — END PLATES, CLIP ANGLES & MOMENT DETAILS AT 1:10",
              fig="FIG. 05", accent=BLUE)
    y = y - ih - 22 - 14
    y = module_list(c, M, y, CW, [
        ("D  ·  FABRICATION  —  23", [STEEL_E[0]]),
        ("E  ·  DOCUMENT & DELIVER  —  24–29", STEEL_E[1:]),
    ], BLUE_B)
    footer(c, 7)

def p8_join(c):
    page_bg(c, glow=True)
    y = page_head(c, 8, "04  —  JOIN THE COHORT")
    ghost(c, "04", W - M - 138, y - 130, size=102)
    txt(c, M, y - 38, "Join the", font="BC-XB", size=44, color=INK)
    c.saveState(); c.setFont("BC-XB", 44); c.setFillColor(BLUE)
    c.drawString(M, y - 80, "September cohort.")
    c.restoreState()
    txt(c, M, y - 102, "Live, online and hands-on — from the third week of September.",
        font="N-MI", size=13.5, color=SERIF)
    y = y - 124
    # schedule + investment cards
    tw = (CW - 10) / 2
    # left: schedule
    panel(c, M, y - 168, tw, 168, fill=PANEL, stroke=LINE, r=8)
    tracked(c, M + 16, y - 20, "SCHEDULE", font="M-SB", size=7, color=BLUE_B, track=1.2)
    sched = [("START", "Mon 14 Sept 2026"), ("RHYTHM", "Weekday evenings"), ("FORMAT", "Live on Zoom"), ("TRACK", "4 weeks each")]
    yy = y - 42
    for k, v in sched:
        tracked(c, M + 16, yy, k, font="M-R", size=6.5, color=MUTED, track=1.0)
        txt(c, M + 96, yy - 1, v, font="B-SB", size=9, color=INK)
        yy -= 20
    hairline(c, M + 16, yy + 6, M + tw - 16, color=LINE)
    txt(c, M + 16, yy - 8, "Take either track — or both,", font="B-R", size=8, color=BODY)
    txt(c, M + 16, yy - 20, "back to back.", font="B-R", size=8, color=BODY)
    # right: investment
    x2 = M + tw + 10
    panel(c, x2, y - 168, tw, 168, fill=HexColor("#101B33"), stroke=BLUE_D, r=8)
    tracked(c, x2 + 16, y - 20, "INVESTMENT", font="M-SB", size=7, color=BLUE_B, track=1.2)
    txt(c, x2 + 16, y - 56, "KSH", font="BC-SB", size=20, color=BODY)
    txt(c, x2 + 52, y - 66, "2,500", font="BC-XB", size=54, color=INK)
    txt(c, x2 + 16, y - 84, "per track  ·  live instruction + materials", font="B-R", size=8, color=BODY)
    hairline(c, x2 + 16, y - 96, x2 + tw - 16, color=LINE)
    txt(c, x2 + 16, y - 112, "Students & early-career engineers", font="B-SB", size=8.4, color=INK)
    txt(c, x2 + 16, y - 124, "No prior Revit experience needed.", font="B-R", size=8, color=BODY)
    txt(c, x2 + 16, y - 136, "Just a laptop that runs Revit.", font="B-R", size=8, color=BODY)
    y = y - 168 - 14
    # steps
    tracked(c, M, y, "HOW IT WORKS", font="M-M", size=7, color=MUTED, track=1.1)
    y -= 10
    steps = [
        ("1", "Reserve your seat", "Write to us via the website and pick a track."),
        ("2", "Set up Revit", "We guide libraries & extensions before day one."),
        ("3", "Build live", "Evenings on Zoom — model, detail, document."),
    ]
    sw = (CW - 20) / 3
    for i, (n, t, d) in enumerate(steps):
        x = M + i * (sw + 10)
        panel(c, x, y - 76, sw, 76, fill=PANEL, stroke=LINE, r=6)
        c.saveState(); c.setFillColor(BLUE); c.setFont("BC-XB", 22)
        c.drawString(x + 12, y - 30, n); c.restoreState()
        txt(c, x + 30, y - 26, t, font="B-SB", size=8.4, color=INK)
        para(c, x + 12, y - 44, d, font="B-R", size=7.8, leading=11, color=BODY, max_w=sw - 24)
    y = y - 76 - 14
    # graduate proof band — the full connections sheet
    tracked(c, M, y, "GRADUATE WITH SHEETS LIKE THIS", font="M-M", size=7, color=MUTED, track=1.1)
    y -= 8
    pih = 148
    image_box(c, M, y - pih - 22, CW, pih, os.path.join(ASSETS, "steel-connections.jpg"),
              caption="STEEL CONNECTIONS — BEAM END CONNECTIONS (S.3) AT 1:10, MODELLED & DETAILED IN REVIT",
              fig="S.3", accent=BLUE)
    y = y - pih - 22 - 14
    # CTA band
    panel(c, M, y - 92, CW, 92, fill=BLUE, stroke=BLUE, r=8)
    tracked(c, M + 20, y - 24, "SEATS ARE LIMITED  —  SEPTEMBER COHORT", font="M-SB", size=7, color=white, track=1.1)
    txt(c, M + 18, y - 56, "structratraining.co.ke", font="BC-XB", size=34, color=white)
    txt(c, M + 20, y - 74, "Reserve your track — Concrete, Steel, or both.", font="B-M", size=9.5, color=white)
    # arrow chip
    pill(c, W - M - 108, y - 58, "ENROL  →", bg=white, fg=BLUE, font="M-SB", size=8)
    y = y - 92 - 12
    txt(c, M, y, "Autodesk Revit is a trademark of Autodesk, Inc. Structra Training is an independent program.",
        font="B-I", size=7, color=MUTED)
    footer(c, 8)

def build():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    c = canvas_mod.Canvas(OUT, pagesize=A4)
    c.setTitle("Revit for Structures — Course Outline — Structra Training")
    c.setAuthor("Structra Training")
    c.setSubject("Steel & Concrete Structural Modeling in Autodesk Revit — Course Outline")
    for fn in [p1_cover, p2_overview, p3_concrete_a, p4_concrete_b, p5_steel_a, p6_steel_b, p7_steel_c, p8_join]:
        fn(c)
        c.showPage()
    c.save()
    print("wrote", OUT, os.path.getsize(OUT), "bytes")

if __name__ == "__main__":
    build()
