#!/usr/bin/env python3
"""STRUCTRA - Revit for Structures (Combined flagship) - LIGHT case study edition.
Light blueprint grid, navy + royal headlines, white cards, pill badges.
Copy is dash free: no em dashes, en dashes or hyphens in any content string.
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

W, H = A4
M = 40.0
CW = W - 2 * M

# ---------- palette : light case study ----------
BG      = HexColor("#EDF1F7")
BG_TOP  = HexColor("#FFFFFF")
GRID    = HexColor("#E2E8F1")
PANEL   = HexColor("#FFFFFF")
SHADOW  = HexColor("#D9E1EE")
TINT    = HexColor("#EAF0FF")
LINE    = HexColor("#E2E8F1")
LINE2   = HexColor("#C4D0E4")
INK     = HexColor("#0C1830")
BODY    = HexColor("#46536A")
MUTED   = HexColor("#8593A8")
FAINT   = HexColor("#C4CDDB")
BLUE    = HexColor("#2447F5")
BLUE_B  = HexColor("#2447F5")
BLUE_D  = HexColor("#C9D6FF")
AMBER   = HexColor("#D97706")
AMBER_B = HexColor("#B45309")
GHOST   = HexColor("#E4E9F2")
NAVY    = HexColor("#0C1830")
NAVY_TX = HexColor("#EDF1F7")
NAVY_MU = HexColor("#9AA6BD")
PAPER   = HexColor("#FFFFFF")

# ---------- fonts ----------
pdfmetrics.registerFont(TTFont("B-R",  os.path.join(FONTS, "Barlow-Regular.ttf")))
pdfmetrics.registerFont(TTFont("B-M",  os.path.join(FONTS, "Barlow-Medium.ttf")))
pdfmetrics.registerFont(TTFont("B-SB", os.path.join(FONTS, "Barlow-SemiBold.ttf")))
pdfmetrics.registerFont(TTFont("B-B",  os.path.join(FONTS, "Barlow-Bold.ttf")))
pdfmetrics.registerFont(TTFont("B-XB", os.path.join(FONTS, "Barlow-ExtraBold.ttf")))
pdfmetrics.registerFont(TTFont("B-BLK", os.path.join(FONTS, "Barlow-Black.ttf")))
pdfmetrics.registerFont(TTFont("B-I",  os.path.join(FONTS, "Barlow-Italic.ttf")))
pdfmetrics.registerFont(TTFont("BC-SB", os.path.join(FONTS, "BarlowCondensed-SemiBold.ttf")))
pdfmetrics.registerFont(TTFont("BC-B", os.path.join(FONTS, "BarlowCondensed-Bold.ttf")))
pdfmetrics.registerFont(TTFont("BC-XB", os.path.join(FONTS, "BarlowCondensed-ExtraBold.ttf")))
pdfmetrics.registerFont(TTFont("M-R",  os.path.join(FONTS, "IBMPlexMono-Regular.ttf")))
pdfmetrics.registerFont(TTFont("M-M",  os.path.join(FONTS, "IBMPlexMono-Medium.ttf")))
pdfmetrics.registerFont(TTFont("M-SB", os.path.join(FONTS, "IBMPlexMono-SemiBold.ttf")))

# ---------- helpers ----------
def tracked_width(s, font, size, track=0):
    return pdfmetrics.stringWidth(s, font, size) + track * len(s)

def tracked(c, x, y, s, font="M-R", size=7, color=MUTED, track=0.9, anchor="start", max_w=None):
    c.saveState()
    c.setFont(font, size)
    c.setFillColor(color)
    w = tracked_width(s, font, size, track)
    if max_w and w > max_w:
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

def para(c, x, y_top, text, font="B-R", size=9, leading=13.5, color=BODY, max_w=CW, max_lines=None):
    lines = wrap_lines(text, font, size, max_w)
    if max_lines:
        lines = lines[:max_lines]
    c.saveState()
    c.setFont(font, size)
    c.setFillColor(color)
    y = y_top
    for ln in lines:
        c.drawString(x, y, ln)
        y -= leading
    c.restoreState()
    return y_top - y

def hairline(c, x1, y, x2, color=LINE, width=0.7):
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, y, x2, y)
    c.restoreState()

def panel(c, x, y, w, h, fill=PANEL, stroke=LINE, r=8, sw=0.8, shadow=True):
    c.saveState()
    if shadow:
        c.setFillColor(SHADOW)
        c.setStrokeColor(SHADOW)
        c.roundRect(x + 1, y - 2, w, h, r, stroke=0, fill=1)
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(sw)
    c.roundRect(x, y, w, h, r, stroke=1, fill=1)
    c.restoreState()

def page_bg(c):
    c.saveState()
    bands = 26
    for i in range(bands):
        t = i / (bands - 1)
        r = BG_TOP.red * (1 - t) + BG.red * t
        g = BG_TOP.green * (1 - t) + BG.green * t
        b = BG_TOP.blue * (1 - t) + BG.blue * t
        from reportlab.lib.colors import Color
        c.setFillColor(Color(r, g, b))
        c.setStrokeColor(Color(r, g, b))
        c.rect(0, H - (i + 1) * (H / bands), W, H / bands + 0.5, stroke=0, fill=1)
    c.setStrokeColor(GRID)
    c.setLineWidth(0.5)
    p = c.beginPath()
    x = 0
    while x <= W:
        p.moveTo(x, 0); p.lineTo(x, H); x += 28
    y = 0
    while y <= H:
        p.moveTo(0, y); p.lineTo(W, y); y += 28
    c.drawPath(p, stroke=1, fill=0)
    c.setStrokeColor(HexColor("#D5DDF0"))
    c.setLineWidth(0.7)
    c.circle(W - 40, H - 60, 120, stroke=1, fill=0)
    c.setStrokeColor(HexColor("#E2E8F5"))
    c.circle(W - 40, H - 60, 150, stroke=1, fill=0)
    c.restoreState()

def ghost(c, s, x, y, size=102, color=None):
    c.saveState()
    c.setFont("BC-XB", size)
    c.setFillColor(color or GHOST)
    c.drawString(x, y, s)
    c.restoreState()

def top_bar(c, left="STRUCTRA TRAINING", right="AUTODESK REVIT · COURSE OUTLINE"):
    y = H - 34
    c.saveState()
    c.setFillColor(BLUE)
    c.rect(M, y - 2, 8, 8, stroke=0, fill=1)
    c.restoreState()
    tracked(c, M + 13, y, left, font="M-SB", size=7.5, color=INK, track=1.1)
    tracked(c, W - M, y, right, font="M-R", size=6.5, color=MUTED, track=0.9, anchor="end")
    hairline(c, M, y - 10, W - M, color=LINE)

def footer(c, pg, total=8, left="STRUCTRA TRAINING · REVIT FOR STRUCTURES"):
    y = 30
    hairline(c, M, y + 12, W - M, color=LINE)
    tracked(c, M, y, left, font="M-R", size=6, color=MUTED, track=0.8)
    tracked(c, W - M, y, f"STRUCTRATRAINING.CO.KE · {pg:02d} / {total:02d}",
            font="M-R", size=6, color=MUTED, track=0.8, anchor="end")

def page_head(c, pg, kicker, kicker_color=BLUE_B):
    top_bar(c)
    y = H - 66
    c.saveState()
    c.setFillColor(kicker_color)
    c.rect(M, y - 1, 7, 7, stroke=0, fill=1)
    c.restoreState()
    tracked(c, M + 12, y, kicker, font="M-M", size=7, color=kicker_color, track=1.2)
    return y - 10

def image_box(c, x, y_bottom, w, h, path, caption=None, fig=None, r=8):
    cap_h = 22 if caption else 0
    total_h = h + cap_h
    y0 = y_bottom
    c.saveState()
    c.setFillColor(SHADOW); c.setStrokeColor(SHADOW)
    c.roundRect(x + 1, y0 - 2, w, total_h, r, stroke=0, fill=1)
    c.setStrokeColor(LINE2); c.setLineWidth(0.9)
    c.setFillColor(PANEL)
    c.roundRect(x, y0, w, total_h, r, stroke=1, fill=1)
    p = c.beginPath(); p.roundRect(x + 0.9, y0 + cap_h, w - 1.8, h - 0.9, max(1, r - 1))
    c.saveState()
    c.clipPath(p, stroke=0, fill=0)
    c.setFillColor(PAPER)
    c.rect(x, y0 + cap_h, w, h, stroke=0, fill=1)
    try:
        c.drawImage(ImageReader(path), x, y0 + cap_h, w, h - 0.6,
                    preserveAspectRatio=True, anchor="c", mask="auto")
    except Exception:
        pass
    c.restoreState()
    if caption:
        hairline(c, x + 10, y0 + cap_h - 0.5, x + w - 10, color=LINE)
        tracked(c, x + 10, y0 + 8, caption, font="M-M", size=6, color=INK, track=0.7, max_w=w - 96)
        if fig:
            tracked(c, x + w - 10, y0 + 8, fig, font="M-R", size=6, color=MUTED, track=0.7, anchor="end")
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

def headline(c, x, y_top, lines, caps=44, gap=4, lh=0.86):
    """lines: list of lines; each line is a list of (text, font, color). Autofit to CW."""
    if isinstance(caps, (int, float)):
        caps = [caps] * len(lines)
    y = y_top
    for segs, cap in zip(lines, caps):
        w1 = sum(pdfmetrics.stringWidth(t, f, 1.0) for t, f, _ in segs) or 1
        size = min(cap, CW / w1)
        c.saveState()
        cx = x
        for t, f, col in segs:
            c.setFont(f, size); c.setFillColor(col)
            c.drawString(cx, y - size * lh, t)
            cx += pdfmetrics.stringWidth(t, f, size)
        c.restoreState()
        y -= size * lh + gap
    return y

# ---------- curriculum data : dash free ----------
CONCRETE_A = [
    ("01", "BRIEF OVERVIEW OF REVIT", ["How Revit thinks", "Revit vs AutoCAD", "Why BIM wins"]),
    ("02", "SETTING UP THE SOFTWARE", ["Essential libraries", "Autodesk extensions"]),
    ("03", "BEGINNING WITH REVIT", ["New projects", "Templates", "Palettes · tabs · panels"]),
    ("04", "DATUM ELEMENTS", ["Levels", "Grids", "Propagating extents", "Grid bubble styling", "Linking CAD for grids"]),
    ("05", "3D ELEMENTS, FIRST PASS", ["Foundations", "Columns", "Beams", "Slabs"]),
]
CONCRETE_B = [
    ("06", "COLUMNS", ["Placement", "Loading families"]),
    ("07", "FOUNDATIONS", ["Hosting on columns", "Strip footings", "Eccentricity", "Basement slabs", "Family libraries"]),
    ("08", "BEAMS & SLABS", ["Copy level to level", "Slab creation", "Hollow pot & waffle"]),
    ("09", "CURVED BEAMS", ["Modelling procedure, end to end"]),
    ("10", "BEAM SYSTEMS & JUSTIFICATION", ["Beam system modelling", "Layout rules", "Justification rules", "Deselecting cleanly"]),
]
CONCRETE_C = [
    ("11", "STAIRCASES & RAMPS", ["Stair types", "Architectural vs structural ramps", "Stairs modelled as ramps", "Shaft openings"]),
    ("12", "VISIBILITY, GRAPHICS & FILTERS", ["Graphic overrides, methods 1 to 4"]),
    ("13", "ROOFS & TRUSSES", ["Sloped & gable ended roofs", "System trusses", "Custom trusses"]),
    ("14", "REINFORCEMENT", ["Sections first", "Foundations", "Columns", "Beams", "Slabs", "Stairs", "Ramps"]),
    ("15", "ANNOTATIONS", ["Dimensions", "Spot elevations", "Spot coordinates", "Spot slopes"]),
    ("16", "SECTION DETAILING", ["Breaklines", "Hatch regions", "Rebar tags", "Comments", "Element tags"]),
]
CONCRETE_D = [
    ("17", "SCHEDULES & TAKEOFFS", ["Bar bending schedules", "Shape images in BBS", "Material takeoffs", "Sorting & filtering"]),
    ("18", "DRAWINGS ON SHEETS", ["Titleblock sizes", "System blocks", "Custom blocks", "Text & fields", "Saving family templates", "Duplicates", "Placing views"]),
    ("19", "PRINTING TO PDF", ["Sheet setup", "Single sheets", "Batch printing"]),
    ("20", "EXPORT & HANDOVER", ["Export options", "To AutoCAD", "To analysis"]),
]
STEEL_A = [
    ("01", "BRIEF OVERVIEW OF REVIT", ["How Revit thinks", "Revit vs CAD", "Why BIM wins"]),
    ("02", "SETTING UP THE SOFTWARE", ["Essential libraries", "Autodesk extensions"]),
    ("03", "BEGINNING WITH REVIT", ["New projects", "Templates", "Palettes · tabs · panels"]),
    ("04", "DATUM ELEMENTS", ["Levels", "Grids", "Elevation markers", "Propagating extents", "Grid bubble styling", "Linking CAD"]),
]
STEEL_B = [
    ("05", "STEEL COLUMNS", ["Placement", "Loading families"]),
    ("06", "CONCRETE COLUMNS", ["Placement", "Loading families"]),
    ("07", "FOUNDATIONS", ["Hosting on columns", "Extended family libraries"]),
    ("08", "RAFTERS", ["Placement", "Steel beam sections", "Attaching columns", "Copying grid to grid"]),
    ("09", "STEEL BEAMS", ["Sections", "Floor beams", "Justification rules", "Copying", "Eaves level beams"]),
    ("10", "BEAM SYSTEMS & JUSTIFICATION", ["Beam system modelling", "Layout rules", "Justification rules", "Deselecting"]),
]
STEEL_C = [
    ("11", "COMPOSITE BEAM & SLAB", ["Composite beams", "Composite slabs", "Cantilevered edges"]),
    ("12", "FLOOR OPENINGS", ["The shaft opening tool"]),
    ("13", "CURVED BEAMS", ["Modelling procedure, end to end"]),
    ("14", "SLOPED / SLANTED BEAMS", ["The offset method", "Framing elevations"]),
    ("15", "PURLINS & SIDE RAILS", ["Reference plane method", "Beam system method", "Side rails"]),
    ("16", "BRACINGS", ["Vertical bracing", "Horizontal bracing"]),
    ("17", "VISIBILITY, GRAPHICS & FILTERS", ["Graphic overrides, methods 1 to 4", "Hiding elements"]),
    ("18", "SECTIONS", ["Section types", "Cutting live sections"]),
    ("19", "REINFORCEMENT", ["Cover setup", "Foundations", "Columns", "Slabs"]),
    ("20", "SPLITTING ELEMENTS", ["Clean splits, buildable parts"]),
    ("21", "CONNECTIONS, FIRST PRINCIPLES", ["Uploading connections", "Applying them", "Propagating across the frame"]),
]
STEEL_D22 = ("22", "CONNECTION TYPES, THE LIBRARY", [
    "Haunch", "Apex", "Base plate", "Gusset bracing", "Gusset column base",
    "Purlin / side rail", "End plate, single sided (simple)", "End plate, single sided (moment)",
    "End plate, double sided (simple)", "Fin plate", "Clip angle", "Column splice", "Custom connections",
])
STEEL_E = [
    ("23", "FABRICATION & PARAMETRIC CUTS", ["Elements & modifiers", "Where cuts live", "Use & location"]),
    ("24", "ANNOTATIONS", ["Dimensions", "Spot elevations", "Coordinates", "Slopes", "Custom bolt & plate tags"]),
    ("25", "SECTION DETAILING", ["Breaklines", "Hatch regions", "Rebar tags", "Comments", "Element tags"]),
    ("26", "SCHEDULES & TAKEOFFS", ["Bar bending schedules", "Shape images in BBS", "Material takeoffs", "Sorting & filtering"]),
    ("27", "DRAWINGS ON SHEETS", ["Titleblock sizes", "System blocks", "Custom blocks", "Text & fields", "Saving family templates", "Duplicates", "Placing views"]),
    ("28", "PRINTING TO PDF", ["Sheet setup", "Single sheets", "Batch printing"]),
    ("29", "EXPORT & HANDOVER", ["Export options", "To AutoCAD", "To analysis"]),
]

def module_block(c, x, y_top, w, num, title, subs, accent):
    tx = x + 30
    tw = w - 30
    tracked(c, x, y_top - 12, num, font="M-SB", size=8.5, color=accent, track=0.4)
    txt(c, tx, y_top - 12, title, font="B-B", size=11, color=INK)
    sub_txt = "   ·   ".join(subs)
    lines = wrap_lines(sub_txt, "B-R", 8.2, tw)
    c.saveState(); c.setFont("B-R", 8.2); c.setFillColor(BODY)
    yy = y_top - 24.5
    for ln in lines[:2]:
        c.drawString(tx, yy, ln); yy -= 10.5
    c.restoreState()
    bottom = yy - 1
    hairline(c, x, bottom, x + w, color=LINE)
    return bottom - 6

def phase_label(c, x, y_top, w, label, accent):
    tracked(c, x, y_top, label, font="M-SB", size=6.5, color=accent, track=1.0)
    lw = tracked_width(label, "M-SB", 6.5, 1.0)
    hairline(c, x + lw + 10, y_top + 2.5, x + w, color=LINE)
    return y_top - 10

def module_list(c, x, y_top, w, groups, accent):
    y = y_top
    for label, mods in groups:
        y = phase_label(c, x, y, w, label, accent)
        for num, title, subs in mods:
            y = module_block(c, x, y + 2, w, num, title, subs, accent)
    return y

def chips(c, x, y_top, w, items):
    y = y_top
    cx = x
    h, gap = 16, 6
    c.saveState()
    for it in items:
        tw = pdfmetrics.stringWidth(it, "M-M", 6.3)
        pw = tw + 16
        if cx + pw > x + w:
            cx = x; y -= h + gap
        c.setStrokeColor(LINE2); c.setLineWidth(0.7); c.setFillColor(white)
        c.roundRect(cx, y - h, pw, h, h / 2, stroke=1, fill=1)
        c.setFont("M-M", 6.3); c.setFillColor(INK)
        c.drawString(cx + 8, y - h + 5.2, it)
        cx += pw + gap
    c.restoreState()
    return y - h - 4

# ============================================================ PAGES
def p1_cover(c):
    page_bg(c)
    # trio eyebrows, case study style
    y = H - 34
    tracked(c, M, y, "LIVE ON ZOOM", font="M-SB", size=7, color=BLUE, track=1.2)
    tracked(c, W / 2, y, "STRUCTRA TRAINING", font="M-SB", size=7, color=INK, track=1.2, anchor="middle")
    tracked(c, W - M, y, "SEPT 2026", font="M-SB", size=7, color=BLUE, track=1.2, anchor="end")
    hairline(c, M, y - 10, W - M, color=LINE)
    y = H - 74
    tracked(c, M, y, "STEEL AND CONCRETE · STRUCTURAL MODELING IN AUTODESK REVIT",
            font="M-M", size=7, color=BLUE_B, track=1.1)
    y = headline(c, M, y - 12, [
        [("REVIT FOR", "B-BLK", INK)],
        [("STRUCTURES", "B-BLK", BLUE)],
    ], caps=[120, 120], gap=6)
    txt(c, M, y - 2, "Build real, buildable structural models. Not just pretty renders.",
        font="B-I", size=14, color=BODY)
    y -= 24
    ih = 296
    image_box(c, M, y - ih - 24, CW, ih, os.path.join(ASSETS, "steel-portal.jpg"),
              caption="STEEL PORTAL FRAME STRUCTURE · 3D PROJECT OVERVIEW AND FRAMING ELEVATIONS",
              fig="FIG. 01")
    pill(c, M + 12, y - 22, "2 TRACKS · 49 MODULES", bg=BLUE)
    pill(c, M + 12, y - 43, "100% LIVE ON ZOOM", bg=NAVY, fg=white)
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
    txt(c, bx + 58, by + 15, "2026", font="B-BLK", size=25, color=white, anchor="middle")
    tracked(c, bx + 58, by + 6.5, "SEPT COHORT", font="M-SB", size=5.5, color=white, track=1.0, anchor="middle")
    y = y - ih - 24 - 14
    # meta cards
    cols = [("START", "14 SEPT 2026"), ("FORMAT", "LIVE, ONLINE"), ("RHYTHM", "WEEKDAY EVENINGS"), ("FEE", "KSH 2,500 / TRACK")]
    colw = (CW - 3 * 8) / 4
    for i, (k, v) in enumerate(cols):
        x = M + i * (colw + 8)
        panel(c, x, y - 52, colw, 52, fill=PANEL, stroke=LINE, r=8)
        tracked(c, x + 10, y - 16, k, font="M-R", size=6.5, color=MUTED, track=1.1)
        txt(c, x + 10, y - 34, v, font="B-XB", size=12, color=AMBER_B if k == "FEE" else INK)
    y -= 52 + 10
    idx = [("01", "PROGRAM", "p. 2"), ("02", "CONCRETE", "p. 3"), ("03", "STEEL", "p. 5"), ("04", "JOIN", "p. 8")]
    iw = CW / 4
    for i, (n, t, pg) in enumerate(idx):
        x = M + i * iw
        panel(c, x + (4 if i else 0), y - 26, iw - 4, 26, fill=PANEL, stroke=LINE, r=6)
        tracked(c, x + (14 if i else 10), y - 10, n, font="M-SB", size=7, color=BLUE_B, track=0.5)
        tracked(c, x + (14 if i else 10) + 20, y - 10, t, font="M-M", size=7, color=INK, track=0.8)
        tracked(c, x + iw - 12, y - 10, pg, font="M-R", size=7, color=MUTED, track=0.5, anchor="end")
    footer(c, 1)

def p2_overview(c):
    page_bg(c)
    y = page_head(c, 2, "01 · THE PROGRAM")
    ghost(c, "01", W - M - 92, y - 148, size=100)
    y = headline(c, M, y - 8, [
        [("One program.", "B-BLK", INK)],
        [("Two ", "B-BLK", INK), ("buildable", "B-BLK", BLUE), (" tracks.", "B-BLK", INK)],
    ], caps=[46, 40], gap=5)
    used = para(c, M, y - 10, "Revit for Structures is a hands on Autodesk Revit program for engineering students and early career professionals who want to build real, buildable structural models. Two focused tracks, Reinforced Concrete and Steel, each run from first launch to finished documentation: modelling, reinforcement and connections, schedules, and sheets that print clean.",
                font="B-R", size=9.3, leading=14.2, color=BODY, max_w=CW)
    y = y - 10 - used - 12
    outcomes = [
        ("01", "Model the whole frame", "Columns to slabs, rafters to bracing."),
        ("02", "Detail like a pro", "Rebar, tags, bolts, plates and cuts."),
        ("03", "Quantify & schedule", "Bar bending schedules and takeoffs."),
        ("04", "Document & deliver", "Sheets, PDFs, CAD and analysis handoff."),
    ]
    colw = (CW - 3 * 10) / 4
    oy = y
    for i, (n, t, d) in enumerate(outcomes):
        x = M + i * (colw + 10)
        panel(c, x, oy - 68, colw, 68, fill=PANEL, stroke=LINE, r=8)
        tracked(c, x + 10, oy - 17, n, font="M-SB", size=7, color=BLUE_B, track=0.6)
        txt(c, x + 10, oy - 32, t, font="B-SB", size=8.2, color=INK)
        para(c, x + 10, oy - 46, d, font="B-R", size=7.4, leading=10, color=BODY, max_w=colw - 20, max_lines=2)
    y = oy - 68 - 14
    tracked(c, M, y, "WHAT YOU WILL MODEL · REAL, STUDENT GRADE OUTPUT", font="M-M", size=7, color=MUTED, track=1.1)
    y -= 10
    gw, gap = (CW - 10) / 2, 10
    gh = 132
    gal = [
        (os.path.join(ASSETS, "tower-21.jpg"), "21 FLOORS + 2 BASEMENTS", "FIG. 02"),
        (os.path.join(ASSETS, "tower-32.jpg"), "32 FLOORS + 4 BASEMENTS", "FIG. 03"),
        (os.path.join(ASSETS, "steel-portal.jpg"), "STEEL PORTAL FRAME STRUCTURE", "FIG. 04"),
        (os.path.join(ASSETS, "steel-connections.jpg"), "STEEL CONNECTIONS", "FIG. 05"),
    ]
    for i in range(2):
        x = M + i * (gw + gap)
        image_box(c, x, y - gh - 22, gw, gh, gal[i][0], caption=gal[i][1], fig=gal[i][2])
    y = y - gh - 22 - 10
    for i in range(2, 4):
        x = M + (i - 2) * (gw + gap)
        image_box(c, x, y - gh - 22, gw, gh, gal[i][0], caption=gal[i][1], fig=gal[i][2])
    y = y - gh - 22 - 12
    tracked(c, M, y + 4, "CHOOSE YOUR TRACK · OR TAKE BOTH", font="M-M", size=7, color=MUTED, track=1.1)
    y -= 8
    tw = (CW - 10) / 2
    for i, (tag, title, sub, acc) in enumerate([
        ("TRACK 01", "REINFORCED CONCRETE", "20 modules · Grids to BBS · p. 3", AMBER),
        ("TRACK 02", "STEEL STRUCTURES", "29 modules · Columns to connections · p. 5", BLUE),
    ]):
        x = M + i * (tw + 10)
        panel(c, x, y - 58, tw, 58, fill=PANEL, stroke=LINE, r=8)
        c.saveState(); c.setFillColor(acc)
        c.roundRect(x, y - 58, 4, 58, 2, stroke=0, fill=1); c.restoreState()
        tracked(c, x + 14, y - 17, tag, font="M-SB", size=6.5, color=acc, track=1.0)
        txt(c, x + 14, y - 37, title, font="B-BLK", size=16, color=INK)
        txt(c, x + 14, y - 50, sub, font="B-R", size=7.6, color=BODY)
    footer(c, 2)

def p3_concrete_a(c):
    page_bg(c)
    y = page_head(c, 3, "02 · TRACK 01 · REINFORCED CONCRETE · 20 MODULES", kicker_color=AMBER_B)
    ghost(c, "RC", W - M - 148, y - 130, size=102)
    tracked(c, M, y - 4, "FROM DATUMS TO DOCUMENTATION", font="M-R", size=7, color=MUTED, track=1.2)
    y = headline(c, M, y - 12, [
        [("Reinforced concrete,", "B-BLK", INK)],
        [("modelled to the ", "B-BLK", INK), ("rebar.", "B-BLK", AMBER)],
    ], caps=[40, 40], gap=5)
    y -= 4
    ih = 110
    image_box(c, M, y - ih - 22, CW, ih, os.path.join(ASSETS, "tower-21.jpg"),
              caption="21 FLOORS + 2 BASEMENTS · REINFORCED CONCRETE TOWER FRAME, MODELLED IN REVIT",
              fig="FIG. 02")
    y = y - ih - 22 - 12
    y = module_list(c, M, y, CW, [
        ("A · GROUNDWORK · 01 TO 05", CONCRETE_A),
        ("B · MODELLING THE FRAME · 06 TO 10", CONCRETE_B),
    ], AMBER)
    footer(c, 3)

def p4_concrete_b(c):
    page_bg(c)
    y = page_head(c, 4, "02 · TRACK 01 · REINFORCED CONCRETE, CONTINUED", kicker_color=AMBER_B)
    ghost(c, "C2", W - M - 148, y - 130, size=102)
    y = headline(c, M, y - 8, [
        [("Detail, reinforce,", "B-BLK", INK)],
        [("then ", "B-BLK", INK), ("deliver.", "B-BLK", AMBER)],
    ], caps=[40, 40], gap=5)
    txt(c, M, y - 12, "Stairs, rebar, tags, sheets.", font="B-I", size=12.5, color=BODY)
    y -= 30
    ih = 110
    image_box(c, M, y - ih - 22, CW, ih, os.path.join(ASSETS, "tower-32.jpg"),
              caption="32 FLOORS + 4 BASEMENTS · CURVED TOWER WITH LEVELS AND GRIDS, MODELLED IN REVIT",
              fig="FIG. 03")
    y = y - ih - 22 - 12
    y = module_list(c, M, y, CW, [
        ("C · DETAIL & REINFORCE · 11 TO 16", CONCRETE_C),
        ("D · DOCUMENT & DELIVER · 17 TO 20", CONCRETE_D),
    ], AMBER)
    footer(c, 4)

def p5_steel_a(c):
    page_bg(c)
    y = page_head(c, 5, "03 · TRACK 02 · STEEL STRUCTURES · 29 MODULES", kicker_color=BLUE_B)
    ghost(c, "ST", W - M - 138, y - 130, size=102)
    tracked(c, M, y - 4, "COLUMNS · RAFTERS · BEAMS · BRACING", font="M-R", size=7, color=MUTED, track=1.2)
    y = headline(c, M, y - 12, [
        [("Steel, from", "B-BLK", INK)],
        [("columns to ", "B-BLK", INK), ("connections.", "B-BLK", BLUE)],
    ], caps=[42, 40], gap=5)
    y -= 4
    ih = 102
    image_box(c, M, y - ih - 22, CW, ih, os.path.join(ASSETS, "steel-portal.jpg"),
              caption="STEEL PORTAL FRAME STRUCTURE · EAVES, APEX AND FRAMING ELEVATIONS, MODELLED IN REVIT",
              fig="FIG. 04")
    y = y - ih - 22 - 12
    y = module_list(c, M, y, CW, [
        ("A · GROUNDWORK · 01 TO 04", STEEL_A),
        ("B · THE STEEL FRAME · 05 TO 10", STEEL_B),
    ], BLUE_B)
    footer(c, 5)

def p6_steel_b(c):
    page_bg(c)
    y = page_head(c, 6, "03 · TRACK 02 · STEEL, CONTINUED", kicker_color=BLUE_B)
    ghost(c, "S2", W - M - 138, y - 134, size=102)
    y = headline(c, M, y - 8, [
        [("Roofs, openings,", "B-BLK", INK)],
        [("bracing and ", "B-BLK", INK), ("views.", "B-BLK", BLUE)],
    ], caps=[40, 40], gap=5)
    txt(c, M, y - 12, "Composite decks to live sections.", font="B-I", size=12.5, color=BODY)
    y -= 30
    y = module_list(c, M, y, CW, [
        ("C · ROOF, BRACING & VIEWS · 11 TO 21", STEEL_C),
    ], BLUE_B)
    y -= 2
    panel(c, M, y - 48, CW, 48, fill=TINT, stroke=BLUE_D, r=8)
    c.saveState(); c.setFillColor(BLUE)
    c.roundRect(M, y - 48, 4, 48, 2, stroke=0, fill=1); c.restoreState()
    tracked(c, M + 16, y - 19, "NEXT · THE CONNECTION LIBRARY", font="M-SB", size=6.5, color=BLUE_B, track=1.0)
    txt(c, M + 16, y - 35, "Thirteen connection families plus your own customs. Details on page 07.",
        font="B-I", size=11, color=INK)
    txt(c, W - M - 14, y - 30, "SEE P. 07", font="B-XB", size=14, color=BLUE, anchor="end")
    footer(c, 6)

def p7_steel_c(c):
    page_bg(c)
    y = page_head(c, 7, "03 · TRACK 02 · CONNECTIONS AND DELIVERY", kicker_color=BLUE_B)
    ghost(c, "S3", W - M - 138, y - 130, size=102)
    y = headline(c, M, y - 8, [
        [("The connection", "B-BLK", INK)],
        [("library.", "B-BLK", BLUE)],
    ], caps=[42, 42], gap=5)
    txt(c, M, y - 12, "Applied, propagated, detailed.", font="B-I", size=12.5, color=BODY)
    y -= 30
    num, title, subs = STEEL_D22
    items = ["Main types"] + subs
    _rows, _cx, _hh, _gap = 1, 0, 16, 6
    for it in items:
        _pw = pdfmetrics.stringWidth(it, "M-M", 6.3) + 16
        if _cx + _pw > CW - 32:
            _rows += 1; _cx = 0
        _cx += _pw + _gap
    panel_h = 56 + _rows * (_hh + _gap) + 8
    panel(c, M, y - panel_h, CW, panel_h, fill=TINT, stroke=BLUE_D, r=10)
    tracked(c, M + 16, y - 20, "22 · CONNECTION TYPES · THE LIBRARY",
            font="M-SB", size=7.5, color=BLUE_B, track=1.0)
    txt(c, M + 16, y - 36, "Main types first, then every family you will meet on a real frame:",
        font="B-R", size=8.4, color=BODY)
    chips(c, M + 16, y - 50, CW - 32, items)
    hairline(c, M + 16, y - panel_h + 24, W - M - 16, color=BLUE_D)
    tracked(c, M + 16, y - panel_h + 13, "APPLIED LIVE · MODULE 21 · UPLOAD · APPLY · PROPAGATE",
            font="M-R", size=6, color=MUTED, track=0.8)
    y = y - panel_h - 12
    ih = 90
    image_box(c, M, y - ih - 22, CW, ih, os.path.join(ASSETS, "steel-connections-top.jpg"),
              caption="STEEL CONNECTIONS · END PLATES, CLIP ANGLES AND MOMENT DETAILS AT 1:10",
              fig="FIG. 05")
    y = y - ih - 22 - 12
    y = module_list(c, M, y, CW, [
        ("D · FABRICATION · 23", [STEEL_E[0]]),
        ("E · DOCUMENT & DELIVER · 24 TO 29", STEEL_E[1:]),
    ], BLUE_B)
    footer(c, 7)

def p8_join(c):
    page_bg(c)
    y = page_head(c, 8, "04 · JOIN THE COHORT")
    ghost(c, "04", W - M - 138, y - 130, size=102)
    y = headline(c, M, y - 8, [
        [("Join the", "B-BLK", INK)],
        [("September cohort.", "B-BLK", BLUE)],
    ], caps=[46, 46], gap=5)
    txt(c, M, y - 12, "Live, online and hands on, from the third week of September.",
        font="B-I", size=13, color=BODY)
    y -= 32
    tw = (CW - 10) / 2
    panel(c, M, y - 168, tw, 168, fill=PANEL, stroke=LINE, r=10)
    tracked(c, M + 16, y - 20, "SCHEDULE", font="M-SB", size=7, color=BLUE_B, track=1.2)
    sched = [("START", "Mon 14 Sept 2026"), ("RHYTHM", "Weekday evenings"), ("FORMAT", "Live on Zoom"), ("TRACK", "4 weeks each")]
    yy = y - 42
    for k, v in sched:
        tracked(c, M + 16, yy, k, font="M-R", size=6.5, color=MUTED, track=1.0)
        txt(c, M + 96, yy - 1, v, font="B-SB", size=9, color=INK)
        yy -= 20
    hairline(c, M + 16, yy + 6, M + tw - 16, color=LINE)
    txt(c, M + 16, yy - 8, "Take either track, or both,", font="B-R", size=8, color=BODY)
    txt(c, M + 16, yy - 20, "back to back.", font="B-R", size=8, color=BODY)
    x2 = M + tw + 10
    panel(c, x2, y - 168, tw, 168, fill=NAVY, stroke=NAVY, r=10)
    tracked(c, x2 + 16, y - 20, "INVESTMENT", font="M-SB", size=7, color=BLUE_D, track=1.2)
    txt(c, x2 + 16, y - 54, "KSH", font="B-XB", size=18, color=NAVY_MU)
    txt(c, x2 + 52, y - 64, "2,500", font="B-BLK", size=50, color=NAVY_TX)
    txt(c, x2 + 16, y - 82, "per track · live instruction + materials", font="B-R", size=8, color=NAVY_MU)
    hairline(c, x2 + 16, y - 94, x2 + tw - 16, color=HexColor("#24304D"))
    txt(c, x2 + 16, y - 110, "Students and early career engineers", font="B-SB", size=8.4, color=NAVY_TX)
    txt(c, x2 + 16, y - 122, "No prior Revit experience needed.", font="B-R", size=8, color=NAVY_MU)
    txt(c, x2 + 16, y - 134, "Just a laptop that runs Revit.", font="B-R", size=8, color=NAVY_MU)
    y = y - 168 - 14
    tracked(c, M, y, "HOW IT WORKS", font="M-M", size=7, color=MUTED, track=1.1)
    y -= 10
    steps = [
        ("1", "Reserve your seat", "Write to us via the website and pick a track."),
        ("2", "Set up Revit", "We guide libraries and extensions before day one."),
        ("3", "Build live", "Evenings on Zoom. Model, detail, document."),
    ]
    sw = (CW - 20) / 3
    for i, (n, t, d) in enumerate(steps):
        x = M + i * (sw + 10)
        panel(c, x, y - 76, sw, 76, fill=PANEL, stroke=LINE, r=8)
        txt(c, x + 12, y - 32, n, font="B-BLK", size=22, color=BLUE)
        txt(c, x + 30, y - 27, t, font="B-SB", size=8.4, color=INK)
        para(c, x + 12, y - 45, d, font="B-R", size=7.8, leading=11, color=BODY, max_w=sw - 24, max_lines=2)
    y = y - 76 - 14
    tracked(c, M, y, "GRADUATE WITH SHEETS LIKE THIS", font="M-M", size=7, color=MUTED, track=1.1)
    y -= 8
    pih = 148
    image_box(c, M, y - pih - 22, CW, pih, os.path.join(ASSETS, "steel-connections.jpg"),
              caption="STEEL CONNECTIONS · BEAM END CONNECTIONS (S.3) AT 1:10, MODELLED AND DETAILED IN REVIT",
              fig="S.3")
    y = y - pih - 22 - 14
    panel(c, M, y - 92, CW, 92, fill=BLUE, stroke=BLUE, r=10, shadow=False)
    tracked(c, M + 20, y - 24, "SEATS ARE LIMITED · SEPTEMBER COHORT", font="M-SB", size=7, color=white, track=1.1)
    txt(c, M + 18, y - 56, "structratraining.co.ke", font="B-BLK", size=28, color=white)
    txt(c, M + 20, y - 74, "Reserve your track. Concrete, Steel, or both.", font="B-M", size=9.5, color=white)
    pill(c, W - M - 104, y - 58, "ENROL →", bg=white, fg=BLUE, font="M-SB", size=8)
    y = y - 92 - 12
    txt(c, M, y, "Autodesk Revit is a trademark of Autodesk, Inc. Structra Training is an independent program.",
        font="B-I", size=7, color=MUTED)
    footer(c, 8)

def lint():
    """Fail the build if any dash character sneaks into content."""
    import pymupdf
    doc = pymupdf.open(OUT)
    bad = []
    for i, page in enumerate(doc):
        for ch in ("—", "–", "-"):
            if ch in page.get_text():
                bad.append((i + 1, ch))
    if bad:
        raise SystemExit(f"DASH LINT FAILED: {bad}")
    print("lint ok: no dashes in content")

def build():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    c = canvas_mod.Canvas(OUT, pagesize=A4)
    c.setTitle("Revit for Structures · Course Outline · Structra Training")
    c.setAuthor("Structra Training")
    c.setSubject("Steel and Concrete Structural Modeling in Autodesk Revit · Course Outline")
    for fn in [p1_cover, p2_overview, p3_concrete_a, p4_concrete_b, p5_steel_a, p6_steel_b, p7_steel_c, p8_join]:
        fn(c)
        c.showPage()
    c.save()
    print("wrote", OUT, os.path.getsize(OUT), "bytes")
    lint()

if __name__ == "__main__":
    build()
