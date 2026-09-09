#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STRUCTRA course case study - v6 (deterministic full pages, no empty bottoms).

Design rules that guarantee "no empty space at the bottom of a page":
  * Mid-document sections (Background, Challenge, Solution module flow) are one
    continuous flowing stream with *splittable* module paragraphs, so every
    page they span is filled to the bottom by text.
  * The cover page and each "Result" page use a measured, single-pass layout:
    every fixed element is wrapped to find its exact height, and the photo band
    height is then computed so the page ends ~4 mm above the bottom margin.
  * Page breaks are explicit only where a page must start fresh (after the
    cover, before each result page, before the closing navy page).
"""
import os, json, re
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, PageBreak, Flowable,
                                Image as RLImage)
from PIL import Image as PILImage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "work", "fonts")
IMG = os.path.join(ROOT, "work", "img")
JSON = os.path.join(ROOT, "work", "json")
OUT = ROOT

for _n, _f in [("Anton", "Anton.ttf"),
               ("Mon", "Montserrat-Regular.ttf"),
               ("MonMed", "Montserrat-Medium.ttf"),
               ("MonSem", "Montserrat-SemiBold.ttf"),
               ("MonBold", "Montserrat-Bold.ttf"),
               ("MonXb", "Montserrat-ExtraBold.ttf"),
               ("MonBlack", "Montserrat-Black.ttf")]:
    pdfmetrics.registerFont(TTFont(_n, os.path.join(FONTS, _f)))

NAVY   = HexColor("#0D1B4B")
NAVY2  = HexColor("#1C2951")
BLUE   = HexColor("#4A6CF7")
BLUE_D = HexColor("#2563EB")
GREEN  = HexColor("#22C55E")
ORANGE = HexColor("#F59E0B")
INK    = HexColor("#17202B")
GRAY   = HexColor("#3E4A59")
MUTE   = HexColor("#5F6C7C")
LINE   = HexColor("#DCE2EA")
PAGE   = HexColor("#F5F6FA")
PAPER  = white
C_TINT = HexColor("#E9EDFE")
O_TINT = HexColor("#FDF1E0")

EXTRA = {"result": 0.0}   # mm added to final photo band; set by audit loop
BAND_MM = {}            # per pdf file: mm of navy CTA band above the bottom margin
CUR_FILE = ""           # pdf filename being built

PAGE_W, PAGE_H = A4
ML = MR = 16*mm
TOP_M, BOT_M = 14*mm, 14*mm
CW = PAGE_W - ML - MR
FRAME_H = PAGE_H - TOP_M - BOT_M   # 762.5 pt
TAIL = 4.5*mm                        # page-bottom breathing space after last photo

def hx(c): return "#%02X%02X%02X" % (int(c.red*255), int(c.green*255), int(c.blue*255))
def esc(s): return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
def rc(r): return [r]*4
def clean(s):
    s = s.replace("\u2014", ", ").replace("\u2013", ", ").replace("\u2192", ",")
    s = s.replace("\uf0ae", "").replace("\uf076", "")
    return re.sub(r"\s+", " ", s).strip(" .,;:,")
def clean_tail(s):
    s = re.sub(r"\s*\.{3,}\s*\d*\s*$", "", s)
    s = re.sub(r"\s{3,}\s?\d+\s*$", "", s)
    s = re.sub(r"\s+", " ", s).strip(" .")
    return re.sub(r"-", " ", s)
def topics_sentence(bullets):
    parts = [clean(b) for b in bullets if clean(b)]
    return "; ".join(parts)
def ps(name, **kw):
    b = dict(fontName="Mon", fontSize=10, leading=15.5, textColor=INK,
             alignment=TA_LEFT, spaceBefore=0, spaceAfter=0)
    b.update(kw)
    return ParagraphStyle(name, **b)

# ---------- measured helpers ----------
def ph(fl, width=CW):
    """exact rendered height of a flowable at content width"""
    w, h = fl.wrap(width, FRAME_H)
    return h

def img_cap(paths):
    """max photo-band height (mm->pt auto via ratio) that fits the column width"""
    if len(paths) == 1:
        im = PILImage.open(paths[0]); iw, ih = im.size
        return (CW*0.985)*ih/iw
    ia = PILImage.open(paths[0]); ib = PILImage.open(paths[1])
    gap = 8*mm
    rsum = ia.size[0]/ia.size[1] + ib.size[0]/ib.size[1]
    return (CW-gap)/rsum

def dist(leftover, slots):
    """split leftover points across spacer slots (list of max heights), return list heights"""
    caps = [max(0, c) for c in slots]
    out = [0.0]*len(caps)
    while leftover > 0.5 and any(out[i] < caps[i] for i in range(len(caps))):
        for i in range(len(caps)):
            if leftover <= 0.5:
                break
            add = min(caps[i]-out[i], leftover, 9*mm)
            if add > 0:
                out[i] += add; leftover -= add
    out[-1] += max(leftover, 0)          # anything left goes in the last slot
    return out

# ---------------- primitives ----------------
def pill(text, bg, fg=white, size=8.2, padx=11, pady=4.8, font="MonBold"):
    w = pdfmetrics.stringWidth(text, font, size) + 2*padx
    p = Paragraph(f'<font face="{font}" color="{hx(fg)}" size="{size}">{esc(text)}</font>',
                  ps("_p", alignment=TA_CENTER, leading=size+1.8))
    t = Table([[p]], colWidths=[w])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),bg),("ROUNDEDCORNERS",(0,0),(-1,-1),rc(13)),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING",(0,0),(-1,-1),pady),("BOTTOMPADDING",(0,0),(-1,-1),pady)]))
    return t

def kpi_block(num, label, bg, numsize=34):
    np_ = Paragraph(f'<font face="Anton" color="white" size="{numsize}">{esc(num)}</font>',
                    ps("_kn", alignment=TA_CENTER, leading=numsize+6))
    lp = Paragraph(f'<font face="MonBold" color="white" size="8">{esc(label.upper())}</font>',
                   ps("_kl", alignment=TA_CENTER, leading=11))
    t = Table([[np_],[lp]], colWidths=[None])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),bg),("ROUNDEDCORNERS",(0,0),(-1,-1),rc(13)),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING",(0,0),(0,0),13),("BOTTOMPADDING",(0,0),(0,0),0),
        ("TOPPADDING",(0,1),(0,1),2),("BOTTOMPADDING",(0,1),(0,1),12),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    return t

def kpi_row(items, gap=6*mm, numsize=34):
    n=len(items); w=(CW-gap*(n-1))/n
    cells = [kpi_block(num, label, bg, numsize) for num, label, bg in items]
    t=Table([cells], colWidths=[w]*n)
    t.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
        ("VALIGN",(0,0),(-1,-1),"TOP")]))
    return t

def hair(color=LINE, w=0.9):
    t=Table([[""]], colWidths=[CW], rowHeights=[0.3])
    t.setStyle(TableStyle([("LINEABOVE",(0,0),(-1,-1),w,color),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0)]))
    return t

def spacer(h): return Spacer(1, h)

def img_band(paths, h):
    def ic(p, w, ht): return RLImage(p, width=w, height=ht, kind="direct")
    if len(paths) == 1:
        im = PILImage.open(paths[0]); iw, ih = im.size
        w = h*iw/ih
        if w > CW*0.985:
            w = CW*0.985; h = w*ih/iw
        pad = (CW-w)/2
        t = Table([["", ic(paths[0], w, h), ""]], colWidths=[pad, w, pad], rowHeights=[h])
    else:
        ia = PILImage.open(paths[0]); ib = PILImage.open(paths[1])
        gap = 8*mm
        wa = h*ia.size[0]/ia.size[1]; wb = h*ib.size[0]/ib.size[1]
        if wa+wb+gap > CW:
            k = (CW-gap)/(wa+wb); wa, wb = wa*k, wb*k
        pad = (CW-wa-wb-gap)/2
        t = Table([["", ic(paths[0], wa, h), "", ic(paths[1], wb, h), ""]],
                  colWidths=[pad, wa, gap, wb, pad], rowHeights=[h])
    t.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    return t

class SectHead(Flowable):
    def __init__(self, pilltxt, pillbg, kicker, title, accent, tsize=22):
        Flowable.__init__(self)
        self.pilltxt, self.pillbg = pilltxt, pillbg
        self.kicker, self.title, self.accent = kicker, title, accent
        self.tsize = tsize
    def wrap(self, aw, ah):
        self.width = aw
        self.height = 43
        return aw, 43
    def draw(self):
        c = self.canv
        c.setFillColor(self.accent)
        c.roundRect(0, 2, 5, 37, 2.5, stroke=0, fill=1)
        c.setFillColor(MUTE); c.setFont("MonBold", 7.6)
        c.drawString(15, 32, self.kicker.upper())
        pw = pdfmetrics.stringWidth(self.pilltxt, "MonBold", 8.4) + 20
        avail = self.width - pw - 40
        fs = self.tsize
        tw = pdfmetrics.stringWidth(self.title, "MonBlack", fs)
        if tw > avail:
            fs = max(13.5, fs*avail/tw)
        c.setFillColor(NAVY); c.setFont("MonBlack", fs)
        c.drawString(15, 6, self.title)
        c.setFillColor(self.pillbg)
        c.roundRect(self.width-pw, 23, pw, 16, 8, stroke=0, fill=1)
        c.setFillColor(white); c.setFont("MonBold", 8.4)
        c.drawCentredString(self.width-pw/2, 28.4, self.pilltxt)

# ---------------- measured page builders ----------------
def cover_flow(badge, title_pairs, subtitle, accent, stats, imgs):
    """cover page: everything measured, photo last, sized to end at TAIL above
    the bottom margin. Title pairs: list of (text, color, size)."""
    top = Table([
        [Paragraph(f'<font face="MonBlack" color="{hx(NAVY)}" size="12">STRUCTRA TRAINING</font>'
                   f'<br/><font face="MonBold" color="{hx(MUTE)}" size="8.4">COURSE CASE STUDY</font>',
                   ps("_lg", leading=17)),
         pill(badge, accent, size=8.8)]],
        colWidths=[CW*0.55, CW*0.45])
    top.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("ALIGN",(1,0),(1,0),"RIGHT"),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0)]))
    subp = Paragraph(subtitle, ps("_sub", fontName="MonMed", fontSize=12.4,
                                  leading=20, textColor=GRAY))
    tparas = []
    for txt, col, sz in title_pairs:
        tparas.append(Paragraph(f'<font face="Anton" color="{hx(col)}" size="{sz}">{esc(txt)}</font>',
                                ps("_t", leading=int(sz*1.1))))
    kpi = kpi_row(stats, numsize=36)
    hr = hair()
    # base spacers (will be stretched to fill leftover)
    base = [12, 6, 9, 8, 8]   # mm: after top row, between title lines, title->sub, sub->kpi, kpi->hr
    gaps_mm = [12, 5, 9, 8, 8]
    # fixed block (no spacers, no photo)
    blk = [top] + tparas + [subp, kpi, hr]
    used = sum(ph(f) for f in blk) + sum(g*mm for g in gaps_mm)
    cap = img_cap(imgs)
    avail = FRAME_H - used - TAIL
    photo_h = min(avail, cap)
    leftover = avail - photo_h
    extra = dist(leftover, [14*mm]*4 + [20*mm])
    order = []
    order.append(top); order.append(spacer(gaps_mm[0]*mm + extra[0]))
    for i, tp in enumerate(tparas):
        order.append(tp)
        order.append(spacer((gaps_mm[i+1]*mm if i+1 < len(gaps_mm)-2 else (gaps_mm[len(gaps_mm)-2]*mm)) ))
    # simpler: rebuild with explicit slots
    order = []
    slots = [g*mm + e for g, e in zip(gaps_mm, extra[:5])]
    order += [top, spacer(slots[0])]
    order += [tparas[0], spacer(slots[1])] if False else []
    return None  # replaced below

def cover_flow2(badge, title_pairs, subtitle, accent, stats, imgs):
    """clean deterministic cover"""
    top = Table([
        [Paragraph(f'<font face="MonBlack" color="{hx(NAVY)}" size="12">STRUCTRA TRAINING</font>'
                   f'<br/><font face="MonBold" color="{hx(MUTE)}" size="8.4">COURSE CASE STUDY</font>',
                   ps("_lg", leading=17)),
         pill(badge, accent, size=8.8)]],
        colWidths=[CW*0.55, CW*0.45])
    top.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("ALIGN",(1,0),(1,0),"RIGHT"),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0)]))
    tparas = [Paragraph(f'<font face="Anton" color="{hx(col)}" size="{sz}">{esc(txt)}</font>',
                        ps("_t", leading=int(sz*1.1))) for txt, col, sz in title_pairs]
    subp = Paragraph(subtitle, ps("_sub", fontName="MonMed", fontSize=12.4,
                                  leading=20, textColor=GRAY))
    kpi = kpi_row(stats, numsize=36)
    hr = hair()
    # slot gaps (mm) then stretch leftover
    gaps_mm = [10, 5, 9, 8, 8, 6]
    blk = [top] + tparas + [subp, kpi, hr]
    used = sum(ph(f) for f in blk)
    gap_total = sum(g*mm for g in gaps_mm)
    cap = img_cap(imgs)
    avail = FRAME_H - used - gap_total - TAIL
    photo_h = max(50*mm, min(avail, cap))
    leftover = avail - photo_h
    extra = dist(leftover, [16*mm, 8*mm, 14*mm, 12*mm, 14*mm, 30*mm])
    gm = [g*mm + e for g, e in zip(gaps_mm, extra)]
    parts = [top]
    parts.append(spacer(gm[0]))
    parts += [tparas[0], spacer(gm[1]), tparas[1]]
    parts.append(spacer(gm[2]))
    parts.append(subp)
    parts.append(spacer(gm[3]))
    parts.append(kpi)
    parts.append(spacer(gm[4]))
    parts.append(hr)
    parts.append(spacer(gm[5]))
    parts.append(img_band(imgs, photo_h))
    return parts

def result_flow(accent, title, paras, imgs, stats, numsize=30, photo_base=50*mm,
                photos_last=True):
    """Result section in continuous flow: heading, KPI cards, photos and prose.
    photos_last keeps photos after the outcome text (used mid-document so the
    following section text back-fills any tail); otherwise photos sit right
    after the KPI cards so they never strand at a page bottom."""
    head = SectHead("THE RESULT", GREEN, "04  |  OUTCOME", title, accent)
    kpi = kpi_row(stats, numsize=numsize)
    plist = [Paragraph(p, ps("_rp", fontSize=11.4, leading=18.8, textColor=INK,
                             spaceAfter=8, alignment=TA_JUSTIFY)) for p in paras]
    parts = [head, spacer(4.5*mm), kpi, spacer(4.5*mm)]
    if photos_last:
        parts += plist
        parts.append(spacer(3*mm))
        parts.append(img_band(imgs, photo_base + EXTRA.get("result", 0.0)))
    else:
        parts.append(img_band(imgs, photo_base + EXTRA.get("result", 0.0)))
        parts.append(spacer(3*mm))
        parts += plist
    return parts

# ---------------- flowing section builders ----------------
def section01(accent, paras, facts):
    fl = [SectHead("BACKGROUND", GREEN, "01  |  CONTEXT", "Background", accent),
          spacer(3.4*mm)]
    gap = 9*mm
    half = (CW-gap)/2
    left = [Paragraph(p, ps("_bp", fontSize=11.2, leading=18.4, textColor=INK,
                            spaceAfter=10, alignment=TA_JUSTIFY)) for p in paras]
    right = facts_table(facts, half)
    cols = Table([[left, "", right]], colWidths=[half, gap, half])
    cols.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0)]))
    fl.append(cols)
    fl.append(spacer(4.5*mm))
    return fl

def facts_table(facts, width):
    per = (width-8)/2
    cells = [[Paragraph(f'<font face="MonBold" color="{hx(MUTE)}" size="7.4">{esc(l.upper())}</font>',
                        ps("_fl", leading=10, spaceAfter=1.8)),
              Paragraph(f'<font face="MonMed" color="{hx(INK)}" size="9.6">{esc(v)}</font>',
                        ps("_fv", leading=14.6))] for l, v in facts]
    rows = [[cells[i] if i < len(cells) else "", cells[i+1] if i+1 < len(cells) else ""]
            for i in range(0, len(cells), 2)]
    t = Table(rows, colWidths=[per, per])
    t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),7),
        ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),6.5*mm)]))
    return t

def section02(accent, items, outcome_text=None):
    fl = [SectHead("THE CHALLENGE", ORANGE, "02  |  BEFORE TRAINING", "The challenge", accent),
          spacer(3.4*mm)]
    for i, (h, d) in enumerate(items, 1):
        row = Table([[num_badge(f"{i:02d}", O_TINT, accent, d=10.5*mm, size=15), "",
                      [Paragraph(f'<font face="MonBold" color="{hx(NAVY)}" size="11.6">{esc(h)}</font>',
                                 ps("_ch", leading=15.5)),
                       Paragraph(f'<font face="Mon" color="{hx(GRAY)}" size="10.4">{esc(d)}</font>',
                                 ps("_cd", leading=16.8, spaceBefore=2.5))]]],
                     colWidths=[10.5*mm, 6.5*mm, CW-17*mm])
        row.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
            ("LINEBELOW",(0,0),(-1,-1),0.8,LINE),
            ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
            ("TOPPADDING",(0,0),(-1,-1),7.5),("BOTTOMPADDING",(0,0),(-1,-1),7.5)]))
        fl.append(row)
    if outcome_text:
        fl.append(spacer(3*mm))
        fl.append(Paragraph(outcome_text, ps("_ot", fontName="MonMed", fontSize=11,
                                             leading=17.5, textColor=NAVY)))
    fl.append(spacer(4.5*mm))
    return fl

def num_badge(num, bg, fg, d=10*mm, size=14):
    p = Paragraph(f'<font face="Anton" color="{hx(fg)}" size="{size}">{esc(num)}</font>',
                  ps("_nb", alignment=TA_CENTER, leading=size+3))
    t = Table([[p]], colWidths=[d], rowHeights=[d])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),bg),
        ("ROUNDEDCORNERS",(0,0),(-1,-1),rc(int(d/2))),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0)]))
    return t

def section03(kicker, title, accent, lead, mods):
    fl = [SectHead("THE SOLUTION", BLUE, kicker, title, accent), spacer(3*mm),
          Paragraph(lead, ps("_sl", fontName="MonMed", fontSize=11.6, leading=18.6,
                             textColor=GRAY)), spacer(3*mm)]
    for i, m in enumerate(mods, 1):
        fl.extend(module_block(m, i, accent))
    fl.append(spacer(3*mm))
    return fl

def module_block(mod, num, accent):
    t = clean(mod["title"])
    return [
        Paragraph(f'<font face="Anton" color="{hx(accent)}" size="14"> {num:02d} </font>'
                  f'<font face="MonBold" color="{hx(NAVY)}" size="12.8">{esc(t)}</font>',
                  ps("_mh", leading=17.5, spaceBefore=13, spaceAfter=3.5, keepWithNext=1)),
        Paragraph(esc(topics_sentence(mod.get("bullets", []))) + ".",
                  ps("_mt", fontSize=10.4, leading=16.6, textColor=MUTE,
                     leftIndent=30, spaceAfter=4.5))
    ] if topics_sentence(mod.get("bullets", [])) else [
        Paragraph(f'<font face="Anton" color="{hx(accent)}" size="14"> {num:02d} </font>'
                  f'<font face="MonBold" color="{hx(NAVY)}" size="12.8">{esc(t)}</font>',
                  ps("_mh", leading=17.5, spaceBefore=13, spaceAfter=4.5, keepWithNext=1))]

# ---------------- document shell ----------------
class CaseDoc(BaseDocTemplate):
    def __init__(self, filename, label):
        self.label = label
        super().__init__(filename, pagesize=A4, leftMargin=ML, rightMargin=MR,
                         topMargin=TOP_M, bottomMargin=BOT_M,
                         title=label, author="STRUCTRA TRAINING")
        fr = Frame(ML, BOT_M, CW, FRAME_H, leftPadding=0, rightPadding=0,
                   topPadding=0, bottomPadding=0, id="m")
        self.addPageTemplates([PageTemplate(id="p", frames=[fr], onPage=self.furn)])
    def furn(self, c, doc):
        c.saveState()
        c.setFillColor(PAGE); c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
        c.setStrokeColor(HexColor("#D9DEE8")); c.setLineWidth(0.8)
        c.line(ML, PAGE_H-8.5*mm, PAGE_W-MR, PAGE_H-8.5*mm)
        c.setFillColor(NAVY); c.setFont("MonBold", 7.4)
        c.drawString(ML, PAGE_H-12.6*mm, "STRUCTRA TRAINING")
        c.setFont("Mon", 7); c.setFillColor(MUTE)
        c.drawRightString(PAGE_W-MR, PAGE_H-12.6*mm, self.label)
        c.setStrokeColor(HexColor("#E1E5EE")); c.setLineWidth(0.8)
        c.line(ML, 9.6*mm, PAGE_W-MR, 9.6*mm)
        c.setFont("MonBold", 8); c.setFillColor(MUTE)
        c.drawRightString(PAGE_W-MR, 6.6*mm, f"{c.getPageNumber():02d}")
        c.setFont("Mon", 6.8)
        c.drawString(ML, 6.6*mm, "structratraining.co.ke")
        c.restoreState()

class CtaBand(Flowable):
    """Footer CTA band whose paint extends from the page bottom up to the last
    content line (measured per file by the first build pass), so the last page
    is always filled to the bottom. BAND_MM tells how far (in mm) the navy area
    must reach above the bottom margin line."""
    def __init__(self, line1, msg, btn):
        Flowable.__init__(self)
        self.line1, self.msg, self.btn = line1, msg, btn
        self.h = 3   # tiny layout box: never pushed to a new page
    def wrap(self, aw, ah):
        self.width = aw
        self.height = self.h
        return aw, self.h
    def draw(self):
        hmm = BAND_MM.get(CUR_FILE, 0.0)
        if hmm < 1:
            return
        total = BOT_M + hmm*mm + 2   # from page bottom up to the content
        c = self.canv
        c.saveState()
        c.translate(-ML, -total)
        c.setFillColor(NAVY)
        c.rect(0, 0, PAGE_W, total, stroke=0, fill=1)
        # content: centred block inside the band
        cx = PAGE_W/2
        block_h = 116
        cy = (total - block_h)/2 + 34
        c.setFillColor(white); c.setFont("Anton", 19)
        c.drawCentredString(cx, cy, "STRUCTRA")
        c.setFillColor(HexColor("#A9B7E8")); c.setFont("MonBold", 7.6)
        c.drawCentredString(cx, cy+26, self.line1)
        bw = pdfmetrics.stringWidth(self.btn, "MonBold", 9.5) + 40
        c.setFillColor(GREEN)
        c.roundRect(cx-bw/2, cy-30, bw, 22, 11, stroke=0, fill=1)
        c.setFillColor(white); c.setFont("MonBold", 9.5)
        c.drawCentredString(cx, cy-22.5, self.btn)
        c.setFont("Mon", 8); c.setFillColor(HexColor("#C7CFE8"))
        c.drawCentredString(cx, cy-50, "structratraining.co.ke  ·  +254 7XX XXX XXX  ·  Start 14 September 2026  ·  KSH 2,500 per track")
        c.restoreState()

class FullNavy(Flowable):
    def __init__(self, line1, msg, btn):
        Flowable.__init__(self)
        self.line1, self.msg, self.btn = line1, msg, btn
    def wrap(self, aw, ah):
        self.width = aw
        self.height = FRAME_H
        return aw, FRAME_H
    def draw(self):
        c = self.canv
        c.saveState()
        c.translate(-ML, -BOT_M)
        c.setFillColor(NAVY)
        c.rect(0, 0, PAGE_W, PAGE_H + 30, stroke=0, fill=1)
        c.setFillColor(NAVY2); c.circle(PAGE_W-40, 60, 130, stroke=0, fill=1)
        c.setFillColor(HexColor("#0A1440")); c.circle(PAGE_W-6, -10, 52, stroke=0, fill=1)
        my = PAGE_H/2 + 30
        c.setFillColor(white); c.setFont("Anton", 26)
        c.drawCentredString(PAGE_W/2, my+40, "STRUCTRA")
        c.setFillColor(HexColor("#A9B7E8")); c.setFont("MonBold", 8.6)
        c.drawCentredString(PAGE_W/2, my+22, self.line1)
        c.setFillColor(white); c.setFont("MonXb", 27)
        c.drawCentredString(PAGE_W/2, my-26, self.msg)
        bw = pdfmetrics.stringWidth(self.btn, "MonBold", 10.5) + 48
        bx = (PAGE_W-bw)/2
        c.setFillColor(GREEN)
        c.roundRect(bx, my-92, bw, 26, 13, stroke=0, fill=1)
        c.setFillColor(white); c.setFont("MonBold", 10.5)
        c.drawCentredString(PAGE_W/2, my-83.5, self.btn)
        c.setFont("Mon", 9); c.setFillColor(HexColor("#C7CFE8"))
        c.drawCentredString(PAGE_W/2, my-130, "structratraining.co.ke   ·   +254 7XX XXX XXX")
        c.setFillColor(HexColor("#8A9BC6")); c.setFont("Mon", 8)
        c.drawCentredString(PAGE_W/2, my-145, "Start date 14 September 2026 · 100% online · 4 weeks per track · KSH 2,500 per track")
        c.restoreState()

# ---------------- data ----------------
FACTS = [("Start date","Monday, 14 September 2026, third week of September"),
         ("Format","100% online, live sessions led by an instructor on Zoom"),
         ("Duration","4 weeks per track, weekday evenings"),
         ("Fee","KSH 2,500 per track"),
         ("Who it's for","University engineering students and early career structural and BIM professionals"),
         ("Prerequisite","A laptop capable of running Revit, no prior Revit experience required")]

def load_mods(jf):
    data = json.load(open(f"{JSON}/{jf}"))
    return [{"num": int(m["num"]), "title": clean_tail(m["title"]),
             "bullets": [clean_tail(b) for b in m["bullets"]]} for m in data]

def parse_combined():
    pages = json.load(open(f"{JSON}/combined.json"))
    tracks = []; cur = None
    for p in pages:
        for ln in p:
            t = ln.strip()
            if t == "STRUCTRA TRAINING" or re.fullmatch(r"\d{1,2}", t) or t.startswith("structratraining"): continue
            if t in ("Reinforced Concrete Structures Track", "Steel Structures Track"):
                cur = {"mods": []}; tracks.append(cur); continue
            if cur is None: continue
            m = re.match(r"^(\d{1,2})\.\s*(.*)$", t)
            if m: cur["mods"].append({"num": int(m.group(1)), "title": m.group(2).strip(), "bullets": []}); continue
            b = re.sub(r"^[–-]\s*", "", t).strip()
            if b and cur["mods"]: cur["mods"][-1]["bullets"].append(b)
    return tracks

def common_challenge(outcome):
    return [("Who it is for", "University engineering students and early career structural and BIM "
            "professionals who want to build real, buildable models, not just pretty renders."),
            ("Starting level", "No prior Revit experience is required. The only prerequisite is a "
            "laptop capable of running Autodesk Revit."),
            ("Format and pace", "100% online, live sessions led by an instructor on Zoom, weekday "
            "evenings, four weeks per track."),
            ("The gap it closes", outcome)]

# ---------------- builders ----------------
def build_combined():
    tracks = parse_combined()
    conc = [{"num": int(m["num"]), "title": clean_tail(m["title"]),
             "bullets": [clean_tail(b) for b in m["bullets"]]} for m in tracks[0]["mods"]]
    stl  = [{"num": int(m["num"]), "title": clean_tail(m["title"]),
             "bullets": [clean_tail(b) for b in m["bullets"]]} for m in tracks[1]["mods"]]
    out = os.path.join(OUT, "Revit for Structures Course Outline (Case Study).pdf")
    global CUR_FILE
    CUR_FILE = os.path.basename(out)
    doc = CaseDoc(out, "Revit for Structures, steel and concrete modeling")
    s = []
    s.extend(cover_flow2("CASE STUDY",
        [("REVIT FOR", NAVY, 52), ("STRUCTURES", BLUE, 52)],
        "Steel and concrete structural modeling in Autodesk Revit. The full program case study, "
        "module by module, across two live online tracks.",
        BLUE,
        [("2","Training tracks",NAVY),("49","Modules in full",BLUE),
         ("173","Subtopics",HexColor("#0E6B56")),("4 wks","Per track online",ORANGE)],
        [f"{IMG}/model.jpg"]))
    s.append(PageBreak())
    s.extend(section01(BLUE, [
        "Revit for Structures is a hands on Autodesk Revit training program for engineering "
        "students and early career professionals who want to build real, buildable structural "
        "models, not just pretty renders. The program runs as two focused tracks that can be "
        "taken separately or together: Reinforced Concrete Structures and Steel Structures.",
        "Both tracks move from the fundamentals of the Revit interface through full structural "
        "modeling, reinforcement and connection detailing, schedules and construction "
        "documentation."], FACTS))
    s.extend(section02(BLUE, common_challenge(
        "Moving from knowing Revit exists to modeling complete structures end to end, with "
        "reinforcement, connections, schedules and sheets.")))
    s.extend(section03("03  |  TRACK 01", "The solution, track one, reinforced concrete", BLUE,
        "Twenty modules, 72 practical subtopics. The full curriculum delivered in the live "
        "sessions, module by module.", conc))
    s.extend(result_flow(BLUE, "Result, concrete track",
        ["Learners complete the track able to model reinforced concrete frames from datum to "
         "documentation, with reinforcement, bar bending schedules and printed sheets. The "
         "structures below are modeled during the program."],
        [f"{IMG}/concrete_21.jpg", f"{IMG}/concrete_32.jpg"],
        [("20","Modules",NAVY),("72","Subtopics",BLUE),("4 wks","Duration",HexColor("#0E6B56"))]))
    s.extend(section03("03  |  TRACK 02", "The solution, track two, steel structures",
        HexColor("#0E6B56"),
        "Twenty nine modules, 101 practical subtopics. The full curriculum delivered in the live "
        "sessions, module by module.", stl))
    s.extend(result_flow(HexColor("#0E6B56"), "Result, steel track",
        ["Learners complete the track able to model complete steel structures: rafters, floor "
         "beams, purlins and bracing, detailed down to haunch, apex, base plate and gusset plate "
         "connections, ready for fabrication data. The structures shown above are modeled during the program."],
        [f"{IMG}/steel_portal.jpg", f"{IMG}/steel_conn.jpg"],
        [("29","Modules",NAVY),("101","Subtopics",BLUE),("4 wks","Duration",HexColor("#0E6B56"))]))
    _end = (FullNavy if NAVY_PAGE.get(CUR_FILE) else CtaBand)
    s.append(_end("STEEL AND CONCRETE STRUCTURAL MODELING, AUTODESK REVIT",
                  "Ready to start building real structures?",
                  "ENROL, NEXT COHORT 14 SEPT 2026"))
    doc.build(s)

SPECS = [
    dict(jsonf="concrete.json", out="Revit Concrete Modeling Course Outline (Case Study).pdf",
         label="Revit Concrete Structure Training", badge="CASE STUDY: REINFORCED CONCRETE",
         accent=BLUE,
         title=[("REVIT", NAVY, 54), ("CONCRETE", BLUE, 54)],
         subtitle="Concrete structural modeling in Autodesk Revit. The track case study: "
                  "twenty modules from datum setup to printed sheets.",
         overview=["Revit Concrete Structure Training is a live instructor led track within the "
                   "Structra Revit for Structures program. Over four weekday evening weeks you "
                   "move from the Revit interface, levels and grids through columns, "
                   "foundations, beams, slabs, staircases and roofs, then into reinforcement "
                   "placement, detailing, bar bending schedules and construction sheets.",
                   "The track is 100% practical and built for engineering students and "
                   "early career structural professionals who want to produce real, buildable "
                   "reinforced concrete models."],
         outcome="Learners complete the track able to model reinforced concrete frames from "
                 "datum to documentation, with reinforcement, bar bending schedules and "
                 "printed sheets.",
         photos=[f"{IMG}/concrete_21.jpg", f"{IMG}/concrete_32.jpg"],
         res_paras=1),
    dict(jsonf="steel.json", out="Revit Steel Modeling Course Outline (Case Study).pdf",
         label="Revit Steel Structure Training", badge="CASE STUDY: STEEL STRUCTURES",
         accent=HexColor("#0E6B56"),
         title=[("REVIT", NAVY, 54), ("STEEL", HexColor("#0E6B56"), 54)],
         subtitle="Steel structural modeling in Autodesk Revit. The track case study: "
                  "twenty nine modules from datum setup to fabrication detail.",
         overview=["Revit Steel Structure Training is a live instructor led track within the "
                   "Structra Revit for Structures program. Over four weekday evening weeks you "
                   "move from the Revit interface, levels and grids through steel and concrete "
                   "columns, foundations, rafters, steel beams, purlins and bracing, then into "
                   "connections, fabrication elements, schedules and sheets.",
                   "The track is 100% practical and built for engineering students and "
                   "early career structural professionals who want to produce real, buildable "
                   "steel models."],
         outcome="Learners complete the track able to model complete steel structures: "
                 "rafters, floor beams, purlins and bracing, detailed down to haunch, apex, "
                 "base plate and gusset plate connections, ready for fabrication data.",
         photos=[f"{IMG}/steel_portal.jpg", f"{IMG}/steel_conn.jpg"],
         res_paras=1),
]

def build_track(d):
    mods = load_mods(d["jsonf"])
    nm, nb = len(mods), sum(len(m["bullets"]) for m in mods)
    out = os.path.join(OUT, d["out"])
    global CUR_FILE
    CUR_FILE = d["out"]
    doc = CaseDoc(out, d["label"])
    s = []
    s.extend(cover_flow2(d["badge"], d["title"], d["subtitle"], d["accent"],
        [(f"{nm}","Modules in full",NAVY),(f"{nb}","Subtopics",BLUE),
         ("4 wks","Per track",HexColor("#0E6B56")),("100%","Live online",ORANGE)],
        d["photos"]))
    s.append(PageBreak())
    s.extend(section01(d["accent"], d["overview"], FACTS))
    kw = "reinforced concrete" if "concrete" in d["jsonf"] else "steel"
    s.extend(section02(d["accent"], common_challenge(
        "Moving from knowing Revit exists to modeling " + kw +
        " structures end to end, with details, schedules and sheets.")))
    s.extend(section03("03  |  CURRICULUM", "The solution, module by module", d["accent"],
        f"All {nm} modules in full, {nb} practical subtopics, covered in the live sessions.",
        mods))
    s.extend(result_flow(d["accent"], "The result, what you will be able to build",
        [d["outcome"] + " The structures shown above are modeled during the program."],
        d["photos"],
        [(f"{nm}","Modules",NAVY),(f"{nb}","Subtopics",BLUE),("4 wks","Duration",HexColor("#0E6B56"))],
        photos_last=False))
    _end = (FullNavy if NAVY_PAGE.get(CUR_FILE) else CtaBand)
    s.append(_end(d["label"].upper() + ", AUTODESK REVIT",
                  "Ready to start building real structures?",
                  "ENROL, NEXT COHORT 14 SEPT 2026"))
    doc.build(s)

# ---------------- audit ----------------
def page_gaps(fn):
    import pymupdf
    PAGE_T = (0xF5, 0xF6, 0xFA)
    doc = pymupdf.open(fn)
    res = []
    for page in doc:
        txt = page.get_text()
        navy = ("Ready to start building" in txt and "ENROL" in txt)
        dpi = 40
        pix = page.get_pixmap(dpi=dpi)
        W, H, n = pix.width, pix.height, pix.n
        left = int(16/25.4*dpi); right = W-int(16/25.4*dpi)
        top = int(14/25.4*dpi); bot = int(14/25.4*dpi)
        data = pix.samples
        low = -1
        for y in range(H-bot-1, top-1, -1):
            r0 = y*W*n + left*n
            ok = False
            for k in range(0, (right-left)*n, 2*n):
                r, g, b = data[r0+k], data[r0+k+1], data[r0+k+2]
                d = max(abs(r-PAGE_T[0]), abs(g-PAGE_T[1]), abs(b-PAGE_T[2]))
                if d > 18 or (0.3*r+0.6*g+0.1*b) < 235:
                    ok = True; break
            if ok:
                low = y; break
        if low < 0 or navy:
            res.append(None)
        else:
            res.append((H-bot-1-low)/dpi*25.4)
    doc.close()
    return res

ORDER = ["Revit for Structures Course Outline (Case Study).pdf",
         "Revit Concrete Modeling Course Outline (Case Study).pdf",
         "Revit Steel Modeling Course Outline (Case Study).pdf"]
NAVY_PAGE = {}
BAND_MM = {}

def rebuild_all():
    build_combined()
    for d in SPECS:
        build_track(d)

def report(tag):
    print("== page-bottom gaps", tag)
    worst = 0
    for nm in ORDER:
        gaps = page_gaps(nm)
        ws = max([g for g in gaps if g is not None] or [0])
        worst = max(worst, ws)
        print(" ", nm, " | worst white-page gap:", f"{ws:.1f} mm")
        print("   " + " ".join("p%02d=%s" % (i, ("--" if g is None else f"{g:.0f}")) for i, g in enumerate(gaps, 1)))
    print("   >>> worst gap:", f"{worst:.1f} mm")

if __name__ == "__main__":
    rebuild_all()
    for nm in ORDER:
        tails = [g for g in page_gaps(nm) if g is not None]
        last = tails[-1] if tails else 0.0
        if last >= 45:
            BAND_MM[nm] = max(0.0, last - 1.0)
            NAVY_PAGE[nm] = False
        else:
            BAND_MM[nm] = 0.0
            NAVY_PAGE[nm] = True
        print(f"decision {nm}: last content tail {last:.1f} mm -> "
              + (f"CTA band (absorbs {BAND_MM[nm]:.0f} mm)" if not NAVY_PAGE[nm] else "full navy CTA page"))
    rebuild_all()
    report("final")
