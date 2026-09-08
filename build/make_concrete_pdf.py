#!/usr/bin/env python3
"""
Revit Concrete Modeling Course Outline — enhanced layout.
Design system adapted from 'light them.jpeg' (light case-study style):
- white page with fine light-blue grid
- Poppins ExtraBold display type, navy + vivid-blue accent words
- pill badges, colored section callouts (orange / blue / green / navy)
- numbered module cards (01..20), Inter body text
"""
import os
from PIL import Image, ImageOps
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase.pdfmetrics import stringWidth

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FONTDIR = os.path.join(ROOT, "build", "fonts")
IMGDIR = os.path.join(ROOT, "build", "img")
os.makedirs(IMGDIR, exist_ok=True)

# ---------------------------------------------------------------- palette ---
INK      = HexColor("#1C2A4E")   # dark navy  (display type)
BLUE     = HexColor("#3A5CF5")   # vivid royal blue accent
BLUE_TINT= HexColor("#E8EEFE")   # light blue fill
GRID     = HexColor("#E9EFF9")   # background grid line
LINE     = HexColor("#DEE7F6")   # card border
GREEN    = HexColor("#12B87C")
GREEN_TINT=HexColor("#DFF7EE")
ORANGE   = HexColor("#F5A52C")
ORANGE_TINT=HexColor("#FDF0DA")
GRAY     = HexColor("#5C6779")   # body text
GRAY_LT  = HexColor("#97A1B4")
WHITE    = HexColor("#FFFFFF")
NAVY_BG  = HexColor("#141F3C")   # closing band
SHADOW   = HexColor("#D9E4F4")

# ------------------------------------------------------------------ fonts ---
def reg(name, fn):
    pdfmetrics.registerFont(TTFont(name, os.path.join(FONTDIR, fn)))

for fn in ["Poppins-Regular.ttf","Poppins-Medium.ttf","Poppins-SemiBold.ttf",
           "Poppins-Bold.ttf","Poppins-ExtraBold.ttf",
           "Inter-Regular.ttf","Inter-Medium.ttf","Inter-SemiBold.ttf",
           "Inter-Bold.ttf","Inter-ExtraBold.ttf"]:
    reg(fn[:-4], fn)

POP = {400:"Poppins-Regular",500:"Poppins-Medium",600:"Poppins-SemiBold",
       700:"Poppins-Bold",800:"Poppins-ExtraBold"}
ITR = {400:"Inter-Regular",500:"Inter-Medium",600:"Inter-SemiBold",
       700:"Inter-Bold",800:"Inter-ExtraBold"}

# ------------------------------------------------------------------- page ---
PAGE_W, PAGE_H = 612, 792
M = 48                       # page margin
CW = PAGE_W - 2*M            # content width

TOTAL_PAGES = 5
OUT = os.path.join(ROOT, "enhanced", "Revit Concrete Modeling Course Outline.pdf")

# ---------------------------------------------------------------- helpers ---
def rrect(c, x, y, w, h, r, fill=None, stroke=None, sw=1):
    c.saveState()
    if fill is not None:
        c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke); c.setLineWidth(sw)
    c.roundRect(x, y, w, h, r,
                fill=1 if fill is not None else 0,
                stroke=1 if stroke is not None else 0)
    c.restoreState()

def rrect_path(c, x, y, w, h, r):
    p = c.beginPath()
    p.roundRect(x, y, w, h, r)
    return p

def shadow_card(c, x, y, w, h, r=12, dy=2.2, border=LINE):
    rrect(c, x, y-dy, w, h, r, fill=SHADOW)
    rrect(c, x, y, w, h, r, fill=WHITE, stroke=border, sw=1)

def text_w(s, font, size):
    return stringWidth(s, font, size)

def spaced(c, x, y, s, font, size, color, tracking, anchor="left"):
    c.saveState()
    c.setFont(font, size)
    c.setFillColor(color)
    widths = [text_w(ch, font, size) for ch in s]
    total = sum(widths) + tracking * (len(s) - 1)
    if anchor == "center":
        x = x - total / 2
    elif anchor == "right":
        x = x - total
    for ch, wch in zip(s, widths):
        c.drawString(x, y, ch)
        x += wch + tracking
    c.restoreState()
    return total

def wrap_text(s, font, size, maxw):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(t, font, size) <= maxw:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def draw_wrapped(c, x, y, s, font, size, color, maxw, lh):
    c.saveState()
    c.setFont(font, size)
    c.setFillColor(color)
    for ln in wrap_text(s, font, size, maxw):
        c.drawString(x, y, ln)
        y -= lh
    c.restoreState()
    return y + lh   # baseline of last line

def pill(c, x, y, label, font, size, color, fill, padx=11, pady=5, border=None, tracking=0.8):
    """pill with baseline y at label baseline center; left edge x. returns width"""
    tw = text_w(label, font, size) + tracking * max(0, len(label) - 1)
    w = tw + 2 * padx
    h = size + 2 * pady
    rrect(c, x, y - h + pady - 1, w, h, h / 2, fill=fill, stroke=border, sw=0.8)
    if tracking:
        spaced(c, x + padx, y, label, font, size, color, tracking)
    else:
        c.saveState(); c.setFont(font, size); c.setFillColor(color)
        c.drawString(x + padx, y, label); c.restoreState()
    return w

def diamond(c, x, y, r, color):
    c.saveState()
    c.setFillColor(color)
    p = c.beginPath()
    p.moveTo(x, y + r)
    p.lineTo(x + r, y)
    p.lineTo(x, y - r)
    p.lineTo(x - r, y)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()

def triangle(c, x, y, h, color):
    """small play-triangle pointing right, left edge at x, vertical center y"""
    c.saveState()
    c.setFillColor(color)
    p = c.beginPath()
    p.moveTo(x, y + h / 2)
    p.lineTo(x, y - h / 2)
    p.lineTo(x + h * 0.86, y)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()

def bg_grid(c):
    c.saveState()
    c.setFillColor(WHITE)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setStrokeColor(GRID)
    c.setLineWidth(0.55)
    step = 26
    p = c.beginPath()
    x = step
    while x < PAGE_W:
        p.moveTo(x, 0); p.lineTo(x, PAGE_H)
        x += step
    y = step
    while y < PAGE_H:
        p.moveTo(0, y); p.lineTo(PAGE_W, y)
        y += step
    c.drawPath(p, fill=0, stroke=1)
    c.restoreState()

def logo(c, x, ytop):
    """small brand mark: navy rounded square with R + two-line wordmark. ytop = top edge"""
    s = 22
    rrect(c, x, ytop - s, s, s, 5.5, fill=INK)
    c.saveState()
    c.setFont(POP[800], 12.5)
    c.setFillColor(WHITE)
    c.drawString(x + s / 2 - text_w("R", POP[800], 12.5) / 2, ytop - s + 5.4, "R")
    c.restoreState()
    spaced(c, x + s + 8, ytop - 10, "REVIT CONCRETE", POP[700], 8.5, INK, 1.1)
    spaced(c, x + s + 8, ytop - 20, "MODELING COURSE", POP[500], 6, GRAY_LT, 2.0)

def header(c, phase_label, phase_fill=BLUE_TINT, phase_color=BLUE):
    logo(c, M, PAGE_H - M + 2)
    w = text_w(phase_label, POP[700], 7.5) + 0.8 * max(0, len(phase_label) - 1) + 22
    pill(c, PAGE_W - M - w, PAGE_H - M - 6, phase_label, POP[700], 7.5,
         phase_color, phase_fill, tracking=0.8)

def footer(c, page):
    c.saveState()
    c.setStrokeColor(LINE)
    c.setLineWidth(0.8)
    c.line(M, 52, PAGE_W - M, 52)
    spaced(c, M, 40, "REVIT CONCRETE MODELING  ·  COURSE OUTLINE", ITR[600], 6,
           GRAY_LT, 1.4)
    num = f"{page:02d} / {TOTAL_PAGES:02d}"
    c.setFont(ITR[700], 8.5)
    c.setFillColor(BLUE)
    c.drawRightString(PAGE_W - M, 39, num)
    c.restoreState()

def phase_progress(c, x, y, current):
    """four numbered phase dots, current highlighted (like the 01..05 steps)."""
    labels = ["FOUNDATIONS", "3D MODEL", "REINFORCE", "DELIVERY"]
    gap = 88
    for i in range(4):
        cx = x + i * gap + 7
        d = 14
        if i + 1 < current:
            rrect(c, cx - 7, y - 7, 14, 14, 7, fill=BLUE_TINT)
            col = BLUE
        elif i + 1 == current:
            rrect(c, cx - 7, y - 7, 14, 14, 7, fill=BLUE)
            col = WHITE
        else:
            rrect(c, cx - 7, y - 7, 14, 14, 7, fill=WHITE, stroke=LINE, sw=1)
            col = GRAY_LT
        c.saveState()
        c.setFont(POP[700], 7.5)
        c.setFillColor(col)
        c.drawString(cx - text_w(f"{i+1:02d}", POP[700], 7.5) / 2, y - 2.6, f"{i+1:02d}")
        c.restoreState()
        if i < 3:
            c.saveState()
            c.setStrokeColor(LINE)
            c.setLineWidth(1)
            c.line(cx + 11, y, cx + gap - 11, y)
            c.restoreState()
        spaced(c, cx + 19, y - 2.2, labels[i], ITR[600], 6.2,
               BLUE if i + 1 == current else GRAY_LT, 1.2)

def eyebrow(c, x, y, label, color=BLUE):
    triangle(c, x, y + 3, 7.5, color)
    spaced(c, x + 13, y, label, POP[700], 8, color, 2.0)

def h2(c, x, y, ink_part, blue_part=None, size=25):
    f = POP[800]
    c.saveState()
    c.setFont(f, size)
    cx = x
    c.setFillColor(INK)
    c.drawString(cx, y, ink_part)
    cx += text_w(ink_part, f, size)
    if blue_part:
        c.setFillColor(BLUE)
        c.drawString(cx, y, blue_part)
    c.restoreState()
    return cx

CARD_TL, CARD_TP = 12, 10   # title line-height, topic line-height

def card_height(num, title, topics, w, pad=11):
    inner_w = w - 2 * pad
    return (53.5 + len(wrap_text(title, POP[600], 11, inner_w)) * CARD_TL +
            len(topics) * CARD_TP)

def card_module(c, x, y, w, num, title, topics, accent=BLUE):
    """draw one module card, top-left at (x, y). returns card height."""
    pad = 11
    inner_w = w - 2 * pad
    title_lines = wrap_text(title, POP[600], 11, inner_w)
    h = (53.5 + len(title_lines) * CARD_TL + len(topics) * CARD_TP)
    shadow_card(c, x, y - h, w, h, r=10)
    c.saveState()
    c.setFont(POP[800], 15)
    c.setFillColor(accent)
    c.drawString(x + pad, y - 13.5, f"{num:02d}")
    c.setStrokeColor(accent)
    c.setLineWidth(2.2)
    c.line(x + pad, y - 17.5, x + pad + 16, y - 17.5)
    c.restoreState()
    ty = y - 13.5 - 17 - 4
    c.saveState()
    c.setFont(POP[600], 11)
    c.setFillColor(INK)
    for tl in title_lines:
        c.drawString(x + pad, ty, tl)
        ty -= CARD_TL
    c.restoreState()
    ty -= 8
    for t in topics:
        diamond(c, x + pad + 2.6, ty + 3, 2.3, accent)
        c.saveState()
        c.setFont(ITR[400], 8.3)
        c.setFillColor(GRAY)
        c.drawString(x + pad + 9.5, ty, t)
        c.restoreState()
        ty -= CARD_TP
    return h

# ----------------------------------------------------------------- images ---
def prep_images():
    hero = os.path.join(ROOT, "32 floors + 4 Basements.jpeg")
    Image.open(hero).convert("RGB").save(os.path.join(IMGDIR, "hero_src.jpg"), quality=88)
    src = Image.open(hero).convert("RGB")
    w, h = src.size
    # card inner image is 206x226 -> ratio 0.911 (keep full width, crop height)
    ch = int(w / 0.911)
    y0 = (h - ch) // 2
    crop = src.crop((0, y0, w, y0 + ch))
    crop.save(os.path.join(IMGDIR, "hero_32.jpg"), quality=88)

    src2 = Image.open(os.path.join(ROOT, "21 floors + 2 Basements.jpeg")).convert("RGB")
    w2, h2 = src2.size
    cw2 = int(w2 * 0.78)
    crop2 = src2.crop((0, 0, cw2, h2))
    crop2.save(os.path.join(IMGDIR, "tower_21.jpg"), quality=88)
    return {
        "hero": (os.path.join(IMGDIR, "hero_32.jpg"),),
        "tower21": (os.path.join(IMGDIR, "tower_21.jpg"),),
    }

def photo_card(c, path, x, ytop, w, h, radius=12, pad=9, border=LINE):
    """white photo card, top-left (x,ytop); returns bottom y."""
    shadow_card(c, x, ytop - h, w, h, r=radius)
    img_x, img_y = x + pad, ytop - h + pad
    img_w, img_h = w - 2 * pad, h - 2 * pad
    p = rrect_path(c, img_x, img_y, img_w, img_h, radius - 6)
    c.saveState()
    c.clipPath(p, stroke=0)
    c.drawImage(ImageReader(path), img_x, img_y, img_w, img_h)
    c.restoreState()
    return ytop - h

# ------------------------------------------------------------------ data ---
MODULES = [
    (1, "Brief overview of Revit",
     ["What Revit entails", "Differences & benefits vs AutoCAD"]),
    (2, "Setting up the software",
     ["Libraries you'll need — a brief intro", "Downloading extensions from Autodesk"]),
    (3, "Beginning with Revit",
     ["Creating a new project", "An overview of templates", "Palettes, tabs and panels"]),
    (4, "Creating datum elements",
     ["Creating levels", "Creating grids — like levels", "Propagate extents on the grid",
      "Customizing grid bubbles", "Linking CAD files to create grids"]),
    (5, "Creating 3D elements — overview",
     ["Foundations, columns, beams, slabs"]),
    (6, "Creating columns",
     ["Placement of columns", "Loading column families"]),
    (7, "Creating foundations",
     ["Hosting foundations on columns", "Strip footing", "Using the eccentricity option",
      "Basement floor slab", "Loading foundation families"]),
    (8, "Creating beams & slabs",
     ["Copying beams and slabs level to level", "Creating a slab",
      "Hollow-core & waffle slabs"]),
    (9, "Curved beams",
     ["Procedure for modeling curved beams"]),
    (10, "Beam system layout & justification",
     ["Modeling structural beams with the beam system", "Beam system layout rules",
      "Beam system justification rules", "Deselecting the beam system"]),
    (11, "Creating staircases & ramps",
     ["Types of staircase", "Architectural & structural ramps",
      "Modeling a staircase as a ramp", "Shaft openings"]),
    (12, "Visibility/Graphics & filters",
     ["V/G overrides — method 1", "V/G overrides — method 2",
      "V/G overrides — method 3", "V/G overrides — method 4"]),
    (13, "Creating roofs & truss placement",
     ["Sloped and gable-ended roofing", "Adding system trusses on your roof",
      "Editing & creating custom trusses"]),
    (14, "Placing of reinforcement",
     ["Creating sections in your drawing", "Foundation reinforcement",
      "Column reinforcement", "Beam reinforcement", "Slab reinforcement",
      "Staircase reinforcement", "Ramp reinforcement"]),
    (15, "Annotations",
     ["Adding dimensions", "Adding spot elevations",
      "Adding spot coordinates", "Adding spot slopes"]),
    (16, "Detailing of sections",
     ["Placing breaklines in sections", "Using hatch files to create regions",
      "Placement of rebar tags", "Adding comments on reinforcement",
      "Tagging of structural elements"]),
    (17, "Schedules & material takeoffs",
     ["Creating bar bending schedules", "Loading shape images into BBS",
      "Creating material takeoffs", "Sorting & filtering fields"]),
    (18, "Placing drawings on sheets",
     ["Paper sizes for title blocks", "System-loaded title blocks",
      "Editing & customizing title blocks", "Texts and fields in the title block",
      "Saving title blocks as a family template", "Duplicate options for drawings",
      "Placing drawings on the sheets"]),
    (19, "Printing sheets to PDF",
     ["Setting up sheets before printing", "Printing one sheet at a time",
      "Printing several sheets at a time"]),
    (20, "Conversion to CAD & other formats",
     ["Export options for other formats", "Transporting your drawing to AutoCAD",
      "Sending your model for analysis"]),
]

# ----------------------------------------------------------------- cover ---
def page_cover(c, imgs):
    bg_grid(c)
    logo(c, M, PAGE_H - M + 2)
    w = text_w("COURSE OUTLINE", POP[700], 7.5) + 0.8 * 13 + 22
    pill(c, PAGE_W - M - w, PAGE_H - M - 6, "COURSE OUTLINE", POP[700], 7.5,
         BLUE, BLUE_TINT, tracking=0.8)

    # eyebrow
    y = PAGE_H - 138
    spaced(c, M, y, "REVIT  CONCRETE  STRUCTURE  TRAINING", POP[700], 9, BLUE, 2.2)

    # full-width display block
    def disp_line(yy, parts, size=48):
        f = POP[800]
        cx = M
        c.saveState()
        c.setFont(f, size)
        for txt, col in parts:
            c.setFillColor(col)
            c.drawString(cx, yy, txt)
            cx += text_w(txt, f, size)
        c.restoreState()

    y -= 54
    disp_line(y, [("BUILD ", INK), ("CONCRETE", BLUE)])
    y -= 54
    disp_line(y, [("STRUCTURES", INK)])
    y -= 54
    disp_line(y, [("IN REVIT", BLUE)])
    y -= 54
    disp_line(y, [("COURSE ", INK), ("OUTLINE", BLUE)])

    # sub + pills (left column)
    sy = y - 34
    draw_wrapped(c, M, sy,
                 "A complete, project-based outline for structural engineers — "
                 "20 modules that take you from an empty template to a finished, "
                 "printable sheet set.",
                 ITR[400], 10.5, GRAY, 268, 15.5)
    py = sy - 42
    px = M
    for label, fill, col in [("20 MODULES", BLUE_TINT, BLUE),
                             ("72 TOPICS", GREEN_TINT, GREEN),
                             ("4 PHASES", ORANGE_TINT, ORANGE)]:
        pw = pill(c, px, py, label, POP[700], 7, col, fill, tracking=1.0)
        px += pw + 8

    # "inside the course" card (left column, under pills)
    cx_, cw_ = M, 272
    ct, cb = 322, 160
    shadow_card(c, cx_, cb, cw_, ct - cb, r=12)
    triangle(c, cx_ + 16, ct - 27, 7, BLUE)
    spaced(c, cx_ + 29, ct - 32, "INSIDE THE COURSE", POP[700], 7.5, BLUE, 1.6)
    rows = ["One structure, built floor by floor",
            "From datum elements to sheet sets",
            "Reinforcement & detailing in real Revit",
            "Ends with PDF sheets & CAD handoff"]
    ry = ct - 58
    for r_ in rows:
        diamond(c, cx_ + 20, ry + 3, 2.4, BLUE)
        c.saveState()
        c.setFont(ITR[500], 8.5)
        c.setFillColor(GRAY)
        c.drawString(cx_ + 28, ry, r_)
        c.restoreState()
        ry -= 19

    # hero photo card (right)
    hx, hw, hh = PAGE_W - M - 224, 224, 244
    photo_card(c, imgs["hero"][0], hx, 424, hw, hh, radius=14)
    # orange ring badge over the card, top-right corner
    rx, ry, r = hx + hw - 44, 436, 40
    c.saveState()
    c.setStrokeColor(WHITE); c.setLineWidth(6)
    c.circle(rx, ry, r, stroke=1, fill=1)
    c.setStrokeColor(ORANGE); c.setLineWidth(4)
    c.circle(rx, ry, r, stroke=1, fill=0)
    c.setFont(POP[800], 21)
    c.setFillColor(ORANGE)
    c.drawCentredString(rx, ry - 5, "20")
    spaced(c, rx, ry - 16, "MODULES", POP[700], 5.8, INK, 1.5, anchor="center")
    c.restoreState()
    # caption chip inside the photo, bottom center
    cap = "32 FLOORS + 4 BASEMENTS"
    capw = text_w(cap, POP[600], 6) + 1.0 * (len(cap) - 1) + 22
    cy_ = 424 - hh + 12
    rrect(c, hx + (hw - capw) / 2, cy_, capw, 18, 9, fill=WHITE)
    spaced(c, hx + hw / 2, cy_ + 6.5, cap, POP[600], 6, INK, 1.0, anchor="center")

    # full-width stat strip
    stat_div = 150
    c.saveState()
    c.setStrokeColor(LINE); c.setLineWidth(0.8)
    c.line(M, stat_div, PAGE_W - M, stat_div)
    c.restoreState()
    stats = [("20", "MODULES", BLUE), ("72", "TOPICS COVERED", GREEN),
             ("1", "COMPLETE STRUCTURE", ORANGE)]
    sx = M
    colw = CW / 3
    for num, lab, col in stats:
        c.saveState()
        c.setFont(POP[800], 26)
        c.setFillColor(col)
        c.drawString(sx, stat_div - 34, num)
        c.restoreState()
        spaced(c, sx, stat_div - 50, lab, ITR[600], 6.2, GRAY_LT, 1.4)
        sx += colw

    # phase strip (bottom band)
    by, bh = 60, 50
    shadow_card(c, M, by, CW, bh, r=12)
    for i, (num, lab) in enumerate([("01", "FOUNDATIONS"), ("02", "3D MODEL"),
                                    ("03", "REINFORCE"), ("04", "DELIVERY")]):
        cx2 = M + 26 + i * (CW / 4)
        c.saveState()
        c.setFont(POP[800], 12)
        c.setFillColor(BLUE)
        c.drawString(cx2, by + bh / 2 - 4, num)
        c.restoreState()
        spaced(c, cx2 + 20, by + bh / 2 - 1, lab, POP[600], 6.5, INK, 1.2)
        if i < 3:
            c.saveState()
            c.setStrokeColor(LINE); c.setLineWidth(1)
            c.line(M + 26 + (i + 1) * (CW / 4) - 12, by + 11,
                   M + 26 + (i + 1) * (CW / 4) - 12, by + bh - 11)
            c.restoreState()

    footer(c, 1)

# ------------------------------------------------------- roadmap helpers ---
PHASE_NAMES = {1: "FOUNDATIONS", 2: "3D MODEL", 3: "REINFORCE", 4: "DELIVERY"}

def roadmap_header(c, page, phase, eyebrow_label, h2_ink, h2_blue, deck, deck_w=516):
    bg_grid(c)
    header(c, f"PHASE {phase:02d} — {PHASE_NAMES[phase]}")
    y = PAGE_H - 118
    eyebrow(c, M, y, eyebrow_label)
    h2(c, M, y - 38, h2_ink, h2_blue, size=26)
    draw_wrapped(c, M, y - 66, deck, ITR[400], 9.5, GRAY, deck_w, 14)
    phase_progress(c, M, y - 100, phase)
    return y - 100

def cards_grid(c, top_y, col_a, col_b, col_w=251, gap=14, bottom=150):
    """two explicit columns of module cards; returns final bottom y."""
    xs = [M, M + col_w + gap]
    for col, mods in enumerate((col_a, col_b)):
        y = top_y
        for m in mods:
            num, title, topics = m
            h = card_height(num, title, topics, col_w)
            if y - h < bottom:
                raise RuntimeError(f"module {num} overflows page (y-h={y - h:.0f} < {bottom})")
            card_module(c, xs[col], y, col_w, num, title, topics)
            y -= h + 11
    return top_y - max([sum(card_height(*m, col_w) + 11 for m in col) for col in (col_a, col_b)])

# ---------------------------------------------------------------- page 2 ---
def page_p2(c, imgs):
    top = roadmap_header(
        c, 2, 1, "PHASE 01  ·  THE BASELINES",
        "GET STARTED", " THE RIGHT WAY",
        "Understand what Revit is really doing, set the software up properly, and lay "
        "the datum elements every concrete model is built on.",
        deck_w=340)
    cards_grid(c, top - 26,
               [MODULES[0], MODULES[2]], [MODULES[1], MODULES[3]], bottom=196)
    # orange callout — “The Challenge (Before Revit)”
    ch = 96
    cy = 158
    shadow_card(c, M, cy - ch, CW, ch, r=12)
    rrect(c, M + 1, cy - ch + 1, 5, ch - 2, 2.4, fill=ORANGE)
    # ring icon
    rx, ry = M + 44, cy - ch / 2
    c.saveState()
    c.setStrokeColor(ORANGE); c.setLineWidth(4)
    c.circle(rx, ry, 16, stroke=1, fill=0)
    c.setStrokeColor(ORANGE_TINT); c.setLineWidth(4)
    c.circle(rx, ry, 10, stroke=1, fill=0)
    c.restoreState()
    eyebrow(c, M + 82, cy - 24, "THE CHALLENGE — BEFORE REVIT", ORANGE)
    draw_wrapped(c, M + 82, cy - 42,
                 "Without a structured approach, concrete design stays in 2D — CAD "
                 "lines, manual schedules and rework at every revision. This course "
                 "changes that: one coordinated model, from day one.",
                 ITR[400], 9, GRAY, CW - 82 - 28, 13)
    footer(c, 2)

# ---------------------------------------------------------------- page 3 ---
def page_p3(c, imgs):
    top = roadmap_header(
        c, 3, 2, "PHASE 02  ·  THE 3D MODEL",
        "MODEL THE ", "STRUCTURE",
        "From the first column to the last slab — build a complete concrete frame, "
        "floor by floor.", deck_w=420)
    # slim blue callout strip under the header
    sy = top - 20
    shadow_card(c, M, sy - 44, CW, 44, r=10)
    c.saveState()
    c.setFont(POP[800], 13)
    c.setFillColor(BLUE)
    c.drawString(M + 16, sy - 27, "02")
    c.restoreState()
    c.saveState()
    c.setFont(POP[700], 8)
    c.setFillColor(BLUE)
    c.drawString(M + 40, sy - 20, "THE CORE PROJECT")
    c.setFont(ITR[400], 8.5)
    c.setFillColor(GRAY)
    c.drawString(M + 40, sy - 33,
                 "Levels, grids, columns, foundations, beams and slabs are linked "
                 "data — not drawing objects.")
    c.restoreState()
    cards_grid(c, sy - 66,
               [MODULES[4], MODULES[6], MODULES[7]],
               [MODULES[5], MODULES[8], MODULES[9]], bottom=76)
    footer(c, 3)

# ---------------------------------------------------------------- page 4 ---
def page_p4(c, imgs):
    top = roadmap_header(
        c, 4, 3, "PHASE 03  ·  ENGINEERING DETAIL",
        "REINFORCE & ", "ANNOTATE",
        "Control how the model looks, then put real engineering into it — rebar, "
        "dimensions and section detailing.", deck_w=516)
    cards_grid(c, top - 26,
               [MODULES[10], MODULES[12], MODULES[14]],
               [MODULES[11], MODULES[13], MODULES[15]], bottom=168)
    # green callout
    ch = 94
    cy = 154
    shadow_card(c, M, cy - ch, CW, ch, r=12)
    rrect(c, M + 1, cy - ch + 1, 5, ch - 2, 2.4, fill=GREEN)
    c.saveState()
    c.setStrokeColor(GREEN); c.setLineWidth(3.5)
    c.circle(M + 44, cy - ch / 2, 15, stroke=1, fill=0)
    # check mark
    c.setLineWidth(3)
    c.line(M + 37, cy - ch / 2, M + 42, cy - ch / 2 - 5)
    c.line(M + 42, cy - ch / 2 - 5, M + 51, cy - ch / 2 + 6)
    c.restoreState()
    eyebrow(c, M + 82, cy - 24, "WHERE THE ENGINEERING LIVES", GREEN)
    draw_wrapped(c, M + 82, cy - 42,
                 "Visibility settings, reinforcement, annotations and section detailing "
                 "turn a geometry model into construction documentation the team can "
                 "actually build from.",
                 ITR[400], 9, GRAY, CW - 82 - 28, 13)
    footer(c, 4)

# ---------------------------------------------------------------- page 5 ---
def page_p5(c, imgs):
    top = roadmap_header(
        c, 5, 4, "PHASE 04  ·  DELIVERY",
        "FROM MODEL TO ", "SHEET SET",
        "Quantify it, place it on sheets, and hand clean files to the people who "
        "need them.", deck_w=380)
    cards_grid(c, top - 26,
               [MODULES[16], MODULES[18]], [MODULES[17], MODULES[19]], bottom=230)
    # navy closing band with photo
    bh = 160
    by = 64
    rrect(c, M, by, CW, bh, 14, fill=NAVY_BG)
    # photo right side
    pw_, ph_ = 150, 124
    px, py_ = PAGE_W - M - pw_ - 18, by + (bh - ph_) / 2
    p = rrect_path(c, px, py_, pw_, ph_, 8)
    c.saveState()
    c.clipPath(p, stroke=0)
    c.drawImage(ImageReader(imgs["tower21"][0]), px, py_, pw_, ph_)
    c.restoreState()
    c.saveState()
    c.setStrokeColor(HexColor("#2C3C6B")); c.setLineWidth(1)
    p2 = rrect_path(c, px, py_, pw_, ph_, 8)
    c.drawPath(p2, fill=0, stroke=1)
    c.restoreState()
    # text
    triangle(c, M + 22, by + bh - 40, 7.5, GREEN)
    spaced(c, M + 35, by + bh - 46, "THE RESULT", POP[700], 8.5, GREEN, 2.0)
    c.saveState()
    c.setFont(POP[700], 14.5)
    c.setFillColor(WHITE)
    c.drawString(M + 22, by + bh - 74, "From an empty template")
    c.drawString(M + 22, by + bh - 94, "to a finished sheet set.")
    c.setFont(ITR[400], 8.5)
    c.setFillColor(HexColor("#A9B6D6"))
    c.drawString(M + 22, by + bh - 114,
                 "Schedules, takeoffs and clean CAD / analysis handoffs — ready for review.")
    c.restoreState()
    # CTA pill
    cta = "START WITH MODULE 01"
    cw_ = text_w(cta, POP[700], 7.5) + 1.0 * (len(cta) - 1) + 26
    rrect(c, M + 22, by + 14, cw_, 22, 11, fill=WHITE)
    spaced(c, M + 22 + 13, by + 25, cta, POP[700], 7.5, BLUE, 1.0)
    footer(c, 5)

# ------------------------------------------------------------------- main ---
def main():
    imgs = prep_images()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    c = canvas.Canvas(OUT, pagesize=(PAGE_W, PAGE_H))
    c.setTitle("Revit Concrete Modeling — Course Outline (Enhanced Layout)")
    c.setAuthor("Revit Concrete Structure Training")
    c.setSubject("Course outline — light case-study layout")

    page_cover(c, imgs)
    c.showPage()
    page_p2(c, imgs)
    c.showPage()
    page_p3(c, imgs)
    c.showPage()
    page_p4(c, imgs)
    c.showPage()
    page_p5(c, imgs)
    c.save()
    print("wrote", OUT)

if __name__ == "__main__":
    main()
