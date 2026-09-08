#!/usr/bin/env python3
"""
Revit Concrete Modeling — Table of Contents.
Light-theme layout replicated from 'light them.jpeg' (case-study design):
- white page + fine light-blue grid
- top three letter-spaced labels (blue / navy / blue)
- huge Poppins ExtraBold title, navy + vivid blue accent word
- pill badges, play-triangle section labels ("Table of Contents")
- numbered content blocks (01..20), green check bullets
- green stat blocks, orange ring (white center), photo cards
- ALL LIGHT: no dark fills anywhere
Content = original outline, word for word, same 4-page structure.
"""
import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.pdfmetrics import stringWidth

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FONTDIR = os.path.join(ROOT, "build", "fonts")
IMGDIR = os.path.join(ROOT, "build", "img")
os.makedirs(IMGDIR, exist_ok=True)

# ---------------------------------------------------------------- palette ---
INK        = HexColor("#1C2A4E")   # navy text only (light theme)
BLUE       = HexColor("#3A5CF5")
BLUE_TINT  = HexColor("#E8EEFE")
GRID       = HexColor("#E9EFF9")
LINE       = HexColor("#DEE7F6")
GREEN      = HexColor("#12B87C")
GREEN_TINT = HexColor("#DFF7EE")
ORANGE     = HexColor("#F5A52C")
GRAY       = HexColor("#5C6779")
GRAY_LT    = HexColor("#97A1B4")
WHITE      = HexColor("#FFFFFF")
SHADOW     = HexColor("#D9E4F4")

for fn in ["Poppins-Regular.ttf","Poppins-Medium.ttf","Poppins-SemiBold.ttf",
           "Poppins-Bold.ttf","Poppins-ExtraBold.ttf",
           "Inter-Regular.ttf","Inter-Medium.ttf","Inter-SemiBold.ttf",
           "Inter-Bold.ttf","Inter-ExtraBold.ttf"]:
    pdfmetrics.registerFont(TTFont(fn[:-4], os.path.join(FONTDIR, fn)))

POP = {400:"Poppins-Regular",500:"Poppins-Medium",600:"Poppins-SemiBold",
       700:"Poppins-Bold",800:"Poppins-ExtraBold"}
ITR = {400:"Inter-Regular",500:"Inter-Medium",600:"Inter-SemiBold",
       700:"Inter-Bold",800:"Inter-ExtraBold"}

PAGE_W, PAGE_H = 612, 792
M = 48
CW = PAGE_W - 2*M
TOTAL_PAGES = 4
OUT = os.path.join(ROOT, "enhanced", "Revit Concrete Modeling Course Outline.pdf")

# ---------------------------------------------------------------- helpers ---
def rrect(c, x, y, w, h, r, fill=None, stroke=None, sw=1):
    c.saveState()
    if fill is not None: c.setFillColor(fill)
    if stroke is not None: c.setStrokeColor(stroke); c.setLineWidth(sw)
    c.roundRect(x, y, w, h, r,
                fill=1 if fill is not None else 0,
                stroke=1 if stroke is not None else 0)
    c.restoreState()

def rrect_path(c, x, y, w, h, r):
    p = c.beginPath(); p.roundRect(x, y, w, h, r); return p

def shadow_card(c, x, y, w, h, r=12, dy=2.2, border=LINE):
    rrect(c, x, y-dy, w, h, r, fill=SHADOW)
    rrect(c, x, y, w, h, r, fill=WHITE, stroke=border, sw=1)

def text_w(s, font, size):
    return stringWidth(s, font, size)

def spaced(c, x, y, s, font, size, color, tracking, anchor="left"):
    c.saveState()
    c.setFont(font, size); c.setFillColor(color)
    widths = [text_w(ch, font, size) for ch in s]
    total = sum(widths) + tracking * (len(s) - 1)
    if anchor == "center": x = x - total / 2
    elif anchor == "right": x = x - total
    for ch, wch in zip(s, widths):
        c.drawString(x, y, ch); x += wch + tracking
    c.restoreState()
    return total

def wrap_text(s, font, size, maxw):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(t, font, size) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def draw_wrapped(c, x, y, s, font, size, color, maxw, lh):
    c.saveState(); c.setFont(font, size); c.setFillColor(color)
    for ln in wrap_text(s, font, size, maxw):
        c.drawString(x, y, ln); y -= lh
    c.restoreState()
    return y + lh

def pill(c, x, y, label, font, size, color, fill, padx=11, pady=5,
         border=None, tracking=0.8):
    tw = text_w(label, font, size) + tracking * max(0, len(label) - 1)
    w = tw + 2*padx; h = size + 2*pady
    rrect(c, x, y - h + pady - 1, w, h, h/2, fill=fill, stroke=border, sw=0.8)
    spaced(c, x + padx, y, label, font, size, color, tracking)
    return w

def check(c, x, y, color=GREEN, s=1.0):
    c.saveState()
    c.setStrokeColor(color); c.setLineWidth(1.3 * s)
    c.line(x - 3*s, y + 0.5, x - 0.9*s, y - 1.6*s)
    c.line(x - 0.9*s, y - 1.6*s, x + 3.2*s, y + 1.9*s)
    c.restoreState()

def triangle(c, x, y, h, color):
    c.saveState(); c.setFillColor(color)
    p = c.beginPath()
    p.moveTo(x, y + h/2); p.lineTo(x, y - h/2); p.lineTo(x + h*0.86, y)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()

def section_label(c, x, y, label, color=INK, mark=BLUE, size=9.5):
    triangle(c, x, y + 3.2, 8, mark)
    spaced(c, x + 14, y, label, POP[600], size, color, 1.4)

def bg_grid(c):
    c.saveState()
    c.setFillColor(WHITE); c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setStrokeColor(GRID); c.setLineWidth(0.55)
    p = c.beginPath()
    x = 26
    while x < PAGE_W: p.moveTo(x, 0); p.lineTo(x, PAGE_H); x += 26
    y = 26
    while y < PAGE_H: p.moveTo(0, y); p.lineTo(PAGE_W, y); y += 26
    c.drawPath(p, fill=0, stroke=1)
    c.restoreState()

def logo(c, x, ytop, title=None, sub=None):
    """light brand mark: white square, blue border, blue R."""
    s = 22
    rrect(c, x, ytop - s, s, s, 5.5, fill=WHITE, stroke=BLUE, sw=1.4)
    c.saveState()
    c.setFont(POP[800], 12.5); c.setFillColor(BLUE)
    c.drawString(x + s/2 - text_w("R", POP[800], 12.5)/2, ytop - s + 5.4, "R")
    c.restoreState()
    if title:
        spaced(c, x + s + 8, ytop - 10, title, POP[600], 9, INK, 0.4)
        if sub:
            spaced(c, x + s + 8, ytop - 20, sub, POP[500], 5.8, GRAY_LT, 1.8)

def header(c, page):
    logo(c, M, PAGE_H - M + 2, "Revit Concrete Modeling",
         "REVIT CONCRETE STRUCTURE TRAINING")
    label = f"0{page} / 0{TOTAL_PAGES}"
    w = text_w(label, POP[700], 7.5) + 0.8 * (len(label) - 1) + 22
    pill(c, PAGE_W - M - w, PAGE_H - M - 6, label, POP[700], 7.5,
         BLUE, BLUE_TINT, tracking=0.8)

def footer(c, page):
    c.saveState()
    c.setStrokeColor(LINE); c.setLineWidth(0.8)
    c.line(M, 52, PAGE_W - M, 52)
    spaced(c, M, 40, "REVIT CONCRETE MODELING  ·  TABLE OF CONTENTS",
           ITR[600], 6, GRAY_LT, 1.4)
    c.setFont(ITR[700], 8.5); c.setFillColor(BLUE)
    c.drawRightString(PAGE_W - M, 39, f"0{page} / 0{TOTAL_PAGES}")
    c.restoreState()

# ------------------------------------------------------------------ cards ---
CARD_TL, CARD_TP = 12, 10
def _topic_lines(title, topics, w):
    usable = w - 2*11 - 9.5
    return (len(wrap_text(title, POP[600], 11, w - 22)),
            sum(len(wrap_text(t, ITR[400], 8.3, usable)) for t in topics))

def card_height(title, topics, w):
    tl, tlines = _topic_lines(title, topics, w)
    return 53.5 + tl * CARD_TL + tlines * CARD_TP

def card_module(c, x, y, w, num, title, topics, accent=BLUE):
    pad = 11
    tl, tlines = _topic_lines(title, topics, w)
    h = 53.5 + tl * CARD_TL + tlines * CARD_TP
    shadow_card(c, x, y - h, w, h, r=10)
    c.saveState()
    c.setFont(POP[800], 15); c.setFillColor(accent)
    c.drawString(x + pad, y - 13.5, f"{num:02d}")
    c.setStrokeColor(accent); c.setLineWidth(2.2)
    c.line(x + pad, y - 17.5, x + pad + 16, y - 17.5)
    c.restoreState()
    ty = y - 13.5 - 17 - 4
    c.saveState(); c.setFont(POP[600], 11); c.setFillColor(INK)
    for line in wrap_text(title, POP[600], 11, w - 22):
        c.drawString(x + pad, ty, line); ty -= CARD_TL
    c.restoreState()
    ty -= 8
    usable = w - 2*pad - 9.5
    for t in topics:
        check(c, x + pad + 1.8, ty + 3)
        for line in wrap_text(t, ITR[400], 8.3, usable):
            c.saveState(); c.setFont(ITR[400], 8.3); c.setFillColor(GRAY)
            c.drawString(x + pad + 9.5, ty, line)
            c.restoreState()
            ty -= CARD_TP
    return h

def cards_grid(c, top_y, col_a, col_b, col_w=251, gap=14, bottom=80):
    xs = [M, M + col_w + gap]
    for col, mods in enumerate((col_a, col_b)):
        y = top_y
        for m in mods:
            h = card_height(m[1], m[2], col_w)
            if y - h < bottom:
                raise RuntimeError(f"module {m[0]} overflows (y-h={y-h:.0f})")
            card_module(c, xs[col], y, col_w, *m)
            y -= h + 11
    return top_y - max(sum(card_height(t, tp, col_w) + 11 for _, t, tp in col)
                       for col in (col_a, col_b))

# ----------------------------------------------------------------- images ---
def crop_ratio(src_path, out_path, ratio):
    """crop image to target w/h ratio (centered), save."""
    im = Image.open(src_path).convert("RGB")
    w, h = im.size
    if w / h > ratio:
        nw = int(h * ratio); x0 = (w - nw) // 2
        im = im.crop((x0, 0, x0 + nw, h))
    else:
        nh = int(w / ratio); y0 = (h - nh) // 2
        im = im.crop((0, y0, w, y0 + nh))
    im.save(out_path, quality=88)
    return out_path

def prep_images():
    return {
        "hero": crop_ratio(os.path.join(ROOT, "32 floors + 4 Basements.jpeg"),
                           os.path.join(IMGDIR, "hero_32.jpg"), 1.0),
        "tower21": crop_ratio(os.path.join(ROOT, "21 floors + 2 Basements.jpeg"),
                              os.path.join(IMGDIR, "tower_21.jpg"), 233/212),
    }

def photo_card(c, path, x, ytop, w, h, radius=12, pad=9, border=LINE,
               caption=None, cap_color=INK):
    shadow_card(c, x, ytop - h, w, h, r=radius)
    ix, iy = x + pad, ytop - h + pad
    iw, ih = w - 2*pad, h - 2*pad
    p = rrect_path(c, ix, iy, iw, ih, radius - 6)
    c.saveState()
    c.clipPath(p, stroke=0)
    c.drawImage(ImageReader(path), ix, iy, iw, ih)
    c.restoreState()
    if caption:
        capw = text_w(caption, POP[600], 6) + 1.0 * (len(caption) - 1) + 22
        cy = ytop - h + 12
        rrect(c, x + (w - capw)/2, cy, capw, 18, 9, fill=WHITE)
        spaced(c, x + w/2, cy + 6.5, caption, POP[600], 6, cap_color, 1.0,
               anchor="center")
    return ytop - h

def ring_badge(c, cx, cy, r, big, small):
    """orange ring, WHITE center (light theme)."""
    c.saveState()
    c.setFillColor(WHITE)
    c.setStrokeColor(WHITE); c.setLineWidth(6)
    c.circle(cx, cy, r, stroke=1, fill=1)
    c.setStrokeColor(ORANGE); c.setLineWidth(4)
    c.circle(cx, cy, r, stroke=1, fill=0)
    c.setFont(POP[800], int(r * 0.52)); c.setFillColor(ORANGE)
    c.drawCentredString(cx, cy - r * 0.12, big)
    spaced(c, cx, cy - r * 0.36, small, POP[700], r * 0.145, INK, 1.4,
           anchor="center")
    c.restoreState()

def green_stat(c, x, y, big, small, align="left"):
    c.saveState()
    c.setFont(POP[800], 24); c.setFillColor(GREEN)
    if align == "center":
        c.drawCentredString(x, y, big)
    else:
        c.drawString(x, y, big)
    c.restoreState()
    spaced(c, x, y - 14, small, ITR[600], 6.2, GRAY_LT, 1.4,
           anchor="center" if align == "center" else "left")

# ------------------------------------------------------------------- data ---
TOC = [
    (1, "Brief overview of Revit (what it entails)",
     ["Difference with AutoCAD software", "Benefits over AutoCAD software"]),
    (2, "Setting up the software",
     ["Brief introduction of Libraries required",
      "Downloading other extensions from Autodesk site"]),
    (3, "Beginning with Revit",
     ["Creating a new project", "An overview of the templates",
      "An overview of palettes, tabs and panels"]),
    (4, "Creating Datum Elements",
     ["Creating Levels", "Creating grids – (same as with the levels creation)",
      "Propagate options extents on the grid",
      "Customizing and changing the shape and appearance of grid bubbles",
      "Linking CAD files to create grids"]),
    (5, "Brief Overview of Creating 3D elements",
     ["Foundations, Columns, Beams, Slabs"]),
    (6, "Creating Columns",
     ["Placement of columns", "Loading column families"]),
    (7, "Creating Foundations",
     ["Hosting foundations on the columns created", "Creating Strip footing",
      "Using eccentricity option", "Basement floor slab",
      "Loading foundation families into your drawings"]),
    (8, "Creating Beams and slabs",
     ["Copying beams and slabs from level to level", "Creating a slab",
      "Hollow pot and waffle slab"]),
    (9, "Curved Beams",
     ["Procedure of modeling the curved beams"]),
    (10, "Beam System Layout and Justification Rules",
     ["Using the beam system to model the structural beams",
      "Modelling the beams using the beam system layout rules",
      "Modelling the beams using the beam system Justification Rules",
      "Deselecting the beam system"]),
    (11, "Creating Staircase and Ramps",
     ["Types of staircase", "Creating an architectural ramp and structural ramp",
      "Modeling Staircase as a ramp", "Shaft openings"]),
    (12, "Visibility/Graphics and Filters",
     ["Applying Visibility/Graphic Overrides — Method 1",
      "Applying Visibility/Graphic Overrides — Method 2",
      "Applying Visibility/Graphic Overrides — Method 3",
      "Applying Visibility/Graphic Overrides — Method 4"]),
    (13, "Creating Roofs and Truss placement",
     ["Sloped and gable ended roofing", "Adding system trusses on your roof",
      "Editing and creating your own customized trusses"]),
    (14, "Placing of Reinforcement",
     ["Creating sections in your drawing", "Foundation Reinforcement",
      "Column Reinforcement", "Beam Reinforcement", "Slab reinforcement",
      "Staircase reinforcement", "Ramp reinforcement"]),
    (15, "Annotations",
     ["Adding dimensions", "Adding spot elevations",
      "Adding spot coordinates", "Adding spot slope"]),
    (16, "Detailing of Sections",
     ["Placing breaklines in the sections",
      "Using hatch files to create regions",
      "Placement of rebar tags on your reinforcements",
      "Adding comments on your reinforcement",
      "Tagging of the structural elements"]),
    (17, "Schedules and Material Takeoffs",
     ["Creating Bar Bending Schedules",
      "Loading shape images into bar bending schedules",
      "Creating Material Takeoffs for the structural elements",
      "Sorting and filtering fields in material takeoffs and bar bending schedules"]),
    (18, "Placing Drawings on Sheets",
     ["Loading different paper sizes for your title blocks",
      "Using system loaded title blocks",
      "Editing and customizing the title blocks",
      "Adjusting texts and fields in your title block",
      "Saving title blocks as a Revit family template",
      "Introduction to duplicate options for drawings",
      "Placing drawings on the sheets"]),
    (19, "Printing Sheets to PDF format",
     ["Setting up your sheets before printing",
      "Printing one sheet at a time",
      "Printing several sheets at a time"]),
    (20, "Conversion of your files into CAD and other formats",
     ["Export options for your drawing into other formats",
      "Transporting your drawing to AutoCAD",
      "Sending your model for analysis"]),
]

# ----------------------------------------------------------------- cover ---
def page_cover(c, imgs):
    bg_grid(c)
    logo(c, M, PAGE_H - M + 2)
    w = text_w("TABLE OF CONTENTS", POP[700], 7.5) + 0.8 * 16 + 22
    pill(c, PAGE_W - M - w, PAGE_H - M - 6, "TABLE OF CONTENTS", POP[700],
         7.5, BLUE, BLUE_TINT, tracking=0.8)

    # three top labels (like EFFECTIVE / IN BUILDING / TRUST)
    y = PAGE_H - 116
    spaced(c, M, y, "REVIT", POP[700], 9, BLUE, 2.4)
    spaced(c, PAGE_W / 2, y, "CONCRETE STRUCTURE", POP[700], 9, INK, 2.4,
           anchor="center")
    spaced(c, PAGE_W - M, y, "TRAINING", POP[700], 9, BLUE, 2.4, anchor="right")

    # huge display title — the document title, word for word
    def disp_line(yy, parts, size=52):
        f = POP[800]; cx = M
        c.saveState(); c.setFont(f, size)
        for txt, col in parts:
            c.setFillColor(col); c.drawString(cx, yy, txt)
            cx += text_w(txt, f, size)
        c.restoreState()

    disp_line(y - 56, [("REVIT CONCRETE", INK)])
    disp_line(y - 110, [("MODELING", BLUE)])

    # green stat block (JELD-WEN "Production 44%" style)
    c.saveState()
    c.setFont(POP[700], 18); c.setFillColor(GREEN)
    c.drawString(M, y - 152, "20 Sections")
    c.restoreState()
    c.saveState()
    c.setFont(ITR[400], 10); c.setFillColor(GRAY)
    c.drawString(M + text_w("20 Sections", POP[700], 18) + 10, y - 150,
                 "in this course outline")
    c.restoreState()
    ring_badge(c, 330, y - 158, 26, "20", "SECTIONS")

    # section label
    section_label(c, M, y - 196, "TABLE OF CONTENTS")

    # sections 01–06 as numbered cards (original page 1 content)
    cards_grid(c, y - 224,
               [TOC[0], TOC[2], TOC[4]],
               [TOC[1], TOC[3], TOC[5]], bottom=96)
    footer(c, 1)

# ------------------------------------------------------------ content pages -
def content_header(c, page):
    bg_grid(c)
    header(c, page)
    section_label(c, M, PAGE_H - 116, "TABLE OF CONTENTS")
    return PAGE_H - 140   # cards top y

def page_2(c, imgs):
    top = content_header(c, 2)
    cards_grid(c, top,
               [TOC[6], TOC[8], TOC[7], TOC[10]],
               [TOC[9], TOC[11]], bottom=80)
    # 32-floor photo card in right column, under the cards
    rw = 251
    rx = M + rw + 14
    right_h = sum(card_height(t, tp, rw) + 11 for _, t, tp in (TOC[9], TOC[11]))
    py_ = top - right_h - 14
    photo_card(c, imgs["hero"], rx, py_, rw, 251, radius=12,
               caption="32 FLOORS + 4 BASEMENTS")
    footer(c, 2)

def page_3(c, imgs):
    top = content_header(c, 3)
    cards_grid(c, top,
               [TOC[12], TOC[14], TOC[16]],
               [TOC[13], TOC[15]], bottom=80)
    # photo card in right column, under the cards
    rw = 251
    rx = M + rw + 14
    right_h = sum(card_height(t, tp, rw) + 11 for _, t, tp in (TOC[13], TOC[15]))
    py_ = top - right_h - 14
    photo_card(c, imgs["tower21"], rx, py_, rw, 230, radius=12,
               caption="21 FLOORS + 2 BASEMENTS")
    footer(c, 3)

def page_4(c, imgs):
    top = content_header(c, 4)
    cards_grid(c, top,
               [TOC[17], TOC[18], TOC[19]],
               [], bottom=80)
    # light summary card (right column)
    rw = 251
    rx = M + rw + 14
    ch = 300
    shadow_card(c, rx, top - ch, rw, ch, r=14)
    cx = rx + rw / 2
    c.saveState()
    c.setStrokeColor(LINE); c.setLineWidth(1)
    c.line(rx + 24, top - ch/2, rx + rw - 24, top - ch/2)
    c.restoreState()
    green_stat(c, cx, top - ch/2 + 52, "20", "SECTIONS", align="center")
    green_stat(c, cx, top - ch/2 - 34, "72", "TOPICS", align="center")
    ring_badge(c, rx + 34, top - 34, 22, "20", "")

    # light closing band (no dark fills)
    bh = 120
    by = 76
    shadow_card(c, M, by, CW, bh, r=14)
    rrect(c, M + 1, by + 1, 5, bh - 2, 2.4, fill=BLUE)
    c.saveState()
    c.setFont(POP[700], 15); c.setFillColor(INK)
    c.drawString(M + 26, by + bh - 42, "End of Table of Contents")
    c.setFont(ITR[400], 9); c.setFillColor(GRAY)
    c.drawString(M + 26, by + bh - 62, "Revit Concrete Structure Training")
    c.restoreState()
    cta = "20 SECTIONS  ·  72 TOPICS"
    cw_ = text_w(cta, POP[700], 7.5) + 1.0 * (len(cta) - 1) + 26
    rrect(c, M + 26, by + 18, cw_, 24, 12, fill=WHITE, stroke=BLUE, sw=1.2)
    spaced(c, M + 26 + 13, by + 30, cta, POP[700], 7.5, BLUE, 1.0)
    footer(c, 4)

# ------------------------------------------------------------------- main ---
def main():
    imgs = prep_images()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    c = canvas.Canvas(OUT, pagesize=(PAGE_W, PAGE_H))
    c.setTitle("Revit Concrete Modeling — Table of Contents")
    c.setAuthor("Revit Concrete Structure Training")
    c.setSubject("Course outline — light case-study layout")

    page_cover(c, imgs); c.showPage()
    page_2(c, imgs); c.showPage()
    page_3(c, imgs); c.showPage()
    page_4(c, imgs); c.showPage()
    c.save()
    print("wrote", OUT)

if __name__ == "__main__":
    main()
