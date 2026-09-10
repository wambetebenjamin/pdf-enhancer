#!/usr/bin/env python3
"""Generate the polished Structra Revit for Structures course outline PDF.

Run from the repository root:
    python scripts/generate_enhanced_outline.py

Dependencies:
    reportlab>=4.0
    Pillow>=10.0
"""

from __future__ import annotations

import html
import io
import os
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image, ImageChops, ImageOps
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    FrameBreak,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
)
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "Revit_for_Structures_Course_Outline_Enhanced.pdf"

PAGE_W, PAGE_H = A4

# Brand palette
NAVY = HexColor("#101C30")
NAVY_2 = HexColor("#182A45")
INK = HexColor("#182231")
MUTED = HexColor("#5E6A7A")
WHITE = HexColor("#FFFFFF")
LINE = HexColor("#DCE3EC")
BLUE = HexColor("#4F67F6")
BLUE_LIGHT = HexColor("#EEF1FF")
CONCRETE_BG = HexColor("#F4F6FC")
AMBER = HexColor("#ED9A34")
AMBER_LIGHT = HexColor("#FFF3E3")
STEEL_BG = HexColor("#FBF8F2")
COVER_BG = HexColor("#F6F8FB")

REGULAR_FONT = "Helvetica"
BOLD_FONT = "Helvetica-Bold"


def register_fonts() -> None:
    """Register a clean sans serif and retain a safe built-in fallback."""
    global REGULAR_FONT, BOLD_FONT
    candidates = [
        (
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ),
        (
            ROOT / "fonts" / "DejaVuSans.ttf",
            ROOT / "fonts" / "DejaVuSans-Bold.ttf",
        ),
    ]
    for regular, bold in candidates:
        if regular.exists() and bold.exists():
            REGULAR_FONT = "StructraSans"
            BOLD_FONT = "StructraSans-Bold"
            pdfmetrics.registerFont(TTFont(REGULAR_FONT, str(regular)))
            pdfmetrics.registerFont(TTFont(BOLD_FONT, str(bold)))
            pdfmetrics.registerFontFamily(
                "StructraSans",
                normal=REGULAR_FONT,
                bold=BOLD_FONT,
                italic=REGULAR_FONT,
                boldItalic=BOLD_FONT,
            )
            return

    # Helvetica and Helvetica Bold are built into every ReportLab installation.


register_fonts()


CONCRETE_MODULES: list[tuple[str, list[str]]] = [
    (
        "Brief overview of Revit",
        ["Difference with AutoCAD software", "Benefits over AutoCAD software"],
    ),
    (
        "Setting up the software",
        [
            "Brief introduction of libraries required",
            "Downloading other extensions from the Autodesk site",
        ],
    ),
    (
        "Beginning with Revit",
        [
            "Creating a new project",
            "An overview of the templates",
            "An overview of palettes, tabs and panels",
        ],
    ),
    (
        "Creating datum elements",
        [
            "Creating levels",
            "Creating grids",
            "Propagating grid extents",
            "Customizing grid bubble shape and appearance",
            "Linking CAD files to create grids",
        ],
    ),
    ("Overview of creating 3D elements", ["Foundations, columns, beams and slabs"]),
    ("Creating columns", ["Placement of columns", "Loading column families"]),
    (
        "Creating foundations",
        [
            "Hosting foundations on the columns created",
            "Creating strip footing",
            "Using the eccentricity option",
            "Basement floor slab",
            "Loading foundation families into your drawings",
        ],
    ),
    (
        "Creating beams and slabs",
        [
            "Copying beams and slabs from level to level",
            "Creating a slab",
            "Hollow pot and waffle slabs",
        ],
    ),
    ("Curved beams", ["Procedure for modeling curved beams"]),
    (
        "Beam system layout and justification rules",
        [
            "Using the beam system to model structural beams",
            "Modeling beams using beam system layout rules",
            "Modeling beams using beam system justification rules",
            "Deselecting the beam system",
        ],
    ),
    (
        "Creating staircases and ramps",
        [
            "Types of staircases",
            "Creating an architectural ramp and a structural ramp",
            "Modeling a staircase as a ramp",
            "Shaft openings",
        ],
    ),
    (
        "Visibility/graphics and filters",
        [
            "Applying visibility/graphic overrides — method 1",
            "Applying visibility/graphic overrides — method 2",
            "Applying visibility/graphic overrides — method 3",
            "Applying visibility/graphic overrides — method 4",
        ],
    ),
    (
        "Creating roofs and truss placement",
        [
            "Sloped and gable-ended roofing",
            "Adding system trusses to your roof",
            "Editing and creating customized trusses",
        ],
    ),
    (
        "Placing reinforcement",
        [
            "Creating sections in your drawing",
            "Foundation reinforcement",
            "Column reinforcement",
            "Beam reinforcement",
            "Slab reinforcement",
            "Staircase reinforcement",
            "Ramp reinforcement",
        ],
    ),
    (
        "Annotations",
        [
            "Adding dimensions",
            "Adding spot elevations",
            "Adding spot coordinates",
            "Adding spot slope",
        ],
    ),
    (
        "Detailing of sections",
        [
            "Placing breaklines in sections",
            "Using hatch files to create regions",
            "Placement of rebar tags on reinforcement",
            "Adding comments on reinforcement",
            "Tagging structural elements",
        ],
    ),
    (
        "Schedules and material takeoffs",
        [
            "Creating bar bending schedules",
            "Loading shape images into bar bending schedules",
            "Creating material takeoffs for structural elements",
            "Sorting and filtering fields in schedules",
        ],
    ),
    (
        "Placing drawings on sheets",
        [
            "Loading different paper sizes for title blocks",
            "Using system-loaded title blocks",
            "Editing and customizing title blocks",
            "Adjusting text and fields in a title block",
            "Saving title blocks as a Revit family template",
            "Duplicate options for drawings",
            "Placing drawings on sheets",
        ],
    ),
    (
        "Printing sheets to PDF format",
        [
            "Setting up sheets before printing",
            "Printing one sheet at a time",
            "Printing several sheets at a time",
        ],
    ),
    (
        "Converting files into CAD and other formats",
        [
            "Export options for your drawing",
            "Transporting your drawing to AutoCAD",
            "Sending your model for analysis",
        ],
    ),
]

STEEL_MODULES: list[tuple[str, list[str]]] = [
    (
        "Brief overview of Revit",
        ["Difference with CAD software", "Benefits over CAD software"],
    ),
    (
        "Setting up the software",
        [
            "Brief introduction of libraries required",
            "Downloading other extensions from the Autodesk site",
        ],
    ),
    (
        "Beginning with Revit",
        [
            "Creating a new project",
            "An overview of the templates",
            "An overview of palettes, tabs and panels",
        ],
    ),
    (
        "Creating datum elements",
        [
            "Creating levels",
            "Creating grids",
            "Elevation markers",
            "Propagating grid extents",
            "Customizing grid bubble shape and appearance (optional)",
            "Linking CAD files to create grids",
        ],
    ),
    ("Modeling steel columns", ["Placement of columns", "Loading column families"]),
    (
        "Modeling concrete columns",
        ["Placement of concrete columns", "Loading column families"],
    ),
    (
        "Modeling the foundations",
        [
            "Hosting foundations on the columns created",
            "Loading other foundation families into your drawings",
        ],
    ),
    (
        "Modeling the rafters",
        [
            "Placement of rafters",
            "Loading steel beam sections",
            "Attaching columns to the rafters",
            "Copying rafters from grid to grid",
        ],
    ),
    (
        "Modeling the steel beams",
        [
            "Loading steel beam sections",
            "Modeling the floor beams",
            "Justification rule of the beams",
            "Copying the floor beams",
            "Modeling beams at the eaves level",
        ],
    ),
    (
        "Beam system layout and justification rules",
        [
            "Using the beam system to model structural beams",
            "Modeling beams using beam system layout rules",
            "Modeling beams using beam system justification rules",
            "Deselecting the beam system",
        ],
    ),
    (
        "Composite slab and composite beam",
        [
            "Modeling the composite beam",
            "Modeling the composite slab",
            "Cantilevering the composite slab",
        ],
    ),
    ("Floor openings", ["Using the shaft opening tool"]),
    ("Curved beams", ["Procedure for modeling curved beams"]),
    (
        "Sloped / slanted beams",
        [
            "Modeling sloped beams using the offset tool",
            "Modeling sloped beams using the framing elevation",
        ],
    ),
    (
        "Purlins and side rails",
        [
            "Modeling purlins using reference planes",
            "Modeling purlins using the beam system",
            "Modeling the side rails",
        ],
    ),
    ("Bracings", ["Vertical bracings", "Horizontal bracing"]),
    (
        "Visibility/graphics and filters",
        [
            "Applying visibility/graphic overrides — method 1",
            "Applying visibility/graphic overrides — method 2",
            "Applying visibility/graphic overrides — method 3",
            "Applying visibility/graphic overrides — method 4",
            "Hiding elements",
        ],
    ),
    ("Creating sections", ["Types of sections", "Creating sections in your drawing"]),
    (
        "Placing reinforcement",
        [
            "Setting up the reinforcement cover",
            "Placing reinforcement at the foundation",
            "Column reinforcement",
            "Slab reinforcement",
        ],
    ),
    ("Splitting elements", ["Splitting elements"]),
    (
        "Introduction to connections",
        [
            "Uploading the connections",
            "Applying connections to structural elements",
            "Propagating the connections",
        ],
    ),
    (
        "Connection types",
        [
            "Main types of connection",
            "Haunch connection",
            "Apex connection",
            "Base plate connection",
            "Gusset plate bracing connection",
            "Gusset plate column-base plate connection",
            "Purlin / side rail connection",
            "Single-sided end plate (simple connection)",
            "Single-sided end plate (moment connection)",
            "Double-sided end plate (simple connection)",
            "Fin plate (simple connection)",
            "Clip angle (simple connection)",
            "Column splice connection",
            "Creating custom connections",
        ],
    ),
    ("Fabrication elements, modifiers and parametric cuts", ["Use and location"]),
    (
        "Annotations",
        [
            "Adding dimensions",
            "Adding spot elevations",
            "Adding spot coordinates",
            "Adding spot slope",
            "Creating custom bolt and plate tags",
        ],
    ),
    (
        "Detailing of sections",
        [
            "Placing breaklines in sections",
            "Using hatch files to create regions",
            "Placement of rebar tags on reinforcement",
            "Adding comments on reinforcement",
            "Tagging structural elements",
        ],
    ),
    (
        "Schedules and material takeoffs",
        [
            "Creating bar bending schedules",
            "Loading shape images into bar bending schedules",
            "Creating material takeoffs for structural elements",
            "Sorting and filtering fields in schedules",
        ],
    ),
    (
        "Placing drawings on sheets",
        [
            "Loading different paper sizes for title blocks",
            "Using system-loaded title blocks",
            "Editing and customizing title blocks",
            "Adjusting text and fields in a title block",
            "Saving title blocks as a Revit family template",
            "Duplicate options for drawings",
            "Placing drawings on sheets",
        ],
    ),
    (
        "Printing sheets to PDF format",
        [
            "Setting up sheets before printing",
            "Printing one sheet at a time",
            "Printing several sheets at a time",
        ],
    ),
    (
        "Converting files into CAD and other formats",
        [
            "Export options for your drawing",
            "Transporting your drawing to AutoCAD",
            "Sending your model for analysis",
        ],
    ),
]


TITLE_STYLE = ParagraphStyle(
    "module-title",
    fontName=BOLD_FONT,
    fontSize=9.15,
    leading=11.6,
    textColor=INK,
    alignment=TA_LEFT,
    allowWidows=0,
    allowOrphans=0,
)
BODY_STYLE = ParagraphStyle(
    "module-body",
    fontName=REGULAR_FONT,
    fontSize=7.9,
    leading=10.5,
    textColor=MUTED,
    alignment=TA_LEFT,
    allowWidows=0,
    allowOrphans=0,
)
OVERVIEW_STYLE = ParagraphStyle(
    "overview",
    fontName=REGULAR_FONT,
    fontSize=8.4,
    leading=12.0,
    textColor=INK,
)
DETAIL_STYLE = ParagraphStyle(
    "detail",
    fontName=REGULAR_FONT,
    fontSize=7.45,
    leading=9.7,
    textColor=INK,
)


class ModuleCard(Flowable):
    """An indivisible, consistently spaced curriculum module card."""

    def __init__(
        self,
        number: int,
        title: str,
        items: Sequence[str],
        accent,
        tint,
    ) -> None:
        super().__init__()
        self.number = number
        self.title = title
        self.items = list(items)
        self.accent = accent
        self.tint = tint
        self._title_para: Paragraph | None = None
        self._item_paras: list[Paragraph] = []
        self._title_h = 0.0
        self._item_heights: list[float] = []
        self.width = 0.0
        self.height = 0.0
        self.spaceAfter = 9.0

    def wrap(self, availWidth: float, availHeight: float) -> tuple[float, float]:
        self.width = availWidth
        pad_x = 9.0
        badge_w = 24.0
        title_width = availWidth - (2 * pad_x) - badge_w - 3
        item_width = availWidth - (2 * pad_x) - 22

        self._title_para = Paragraph(html.escape(self.title), TITLE_STYLE)
        _, self._title_h = self._title_para.wrap(title_width, 200)

        self._item_paras = []
        self._item_heights = []
        for item in self.items:
            para = Paragraph(html.escape(item), BODY_STYLE)
            _, item_h = para.wrap(item_width, 200)
            self._item_paras.append(para)
            self._item_heights.append(item_h)

        header_h = max(22.0, self._title_h)
        items_h = sum(self._item_heights) + max(0, len(self.items) - 1) * 1.8
        self.height = 10.0 + header_h + 5.5 + items_h + 9.5
        return self.width, self.height

    def draw(self) -> None:
        c = self.canv
        w, h = self.width, self.height
        pad_x = 9.0
        badge_w = 24.0

        # A soft shadow and crisp card edge create separation without visual noise.
        c.setFillColor(HexColor("#E4E9F0"))
        c.roundRect(1.1, -1.2, w - 1.1, h, 7, stroke=0, fill=1)
        c.setFillColor(WHITE)
        c.setStrokeColor(LINE)
        c.setLineWidth(0.55)
        c.roundRect(0, 0, w - 1.1, h, 7, stroke=1, fill=1)

        c.setFillColor(self.accent)
        c.roundRect(0, 0, 3.5, h, 1.75, stroke=0, fill=1)

        top = h - 10.0
        badge_size = 20.0
        badge_x = pad_x
        badge_y = top - badge_size
        c.setFillColor(self.tint)
        c.circle(badge_x + badge_size / 2, badge_y + badge_size / 2, badge_size / 2, stroke=0, fill=1)
        c.setFillColor(self.accent)
        c.setFont(BOLD_FONT, 7.3 if self.number < 10 else 6.8)
        c.drawCentredString(
            badge_x + badge_size / 2,
            badge_y + 6.1,
            f"{self.number:02d}",
        )

        title_x = pad_x + badge_w
        title_y = top - self._title_h
        assert self._title_para is not None
        self._title_para.drawOn(c, title_x, title_y)

        header_h = max(22.0, self._title_h)
        cursor_y = top - header_h - 5.5
        text_x = pad_x + 20
        for para, para_h in zip(self._item_paras, self._item_heights):
            c.setFillColor(self.accent)
            c.circle(pad_x + 9.5, cursor_y - 3.8, 1.25, stroke=0, fill=1)
            para.drawOn(c, text_x, cursor_y - para_h)
            cursor_y -= para_h + 1.8


class StructraDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str | os.PathLike[str]) -> None:
        super().__init__(
            str(filename),
            pagesize=A4,
            leftMargin=0,
            rightMargin=0,
            topMargin=0,
            bottomMargin=0,
            title="Revit for Structures — Course Outline",
            author="Structra Training",
            subject="Steel and concrete structural modeling in Autodesk Revit",
            creator="Structra Training course outline generator",
        )

        cover_frame = Frame(
            0,
            0,
            PAGE_W,
            PAGE_H,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
            id="cover-frame",
        )

        side = 13.5 * mm
        gutter = 5.5 * mm
        content_bottom = 16.5 * mm
        content_top = PAGE_H - 43.5 * mm
        frame_width = (PAGE_W - (2 * side) - gutter) / 2
        frame_height = content_top - content_bottom

        def track_frames(prefix: str) -> list[Frame]:
            return [
                Frame(
                    side,
                    content_bottom,
                    frame_width,
                    frame_height,
                    leftPadding=0,
                    rightPadding=0,
                    topPadding=0,
                    bottomPadding=0,
                    id=f"{prefix}-left",
                ),
                Frame(
                    side + frame_width + gutter,
                    content_bottom,
                    frame_width,
                    frame_height,
                    leftPadding=0,
                    rightPadding=0,
                    topPadding=0,
                    bottomPadding=0,
                    id=f"{prefix}-right",
                ),
            ]

        self.addPageTemplates(
            [
                PageTemplate(id="cover", frames=[cover_frame], onPage=draw_cover),
                PageTemplate(
                    id="concrete",
                    frames=track_frames("concrete"),
                    onPage=lambda c, d: draw_track_page(
                        c,
                        d,
                        track="REINFORCED CONCRETE STRUCTURES",
                        eyebrow="TRACK 01  /  STRUCTURAL MODELING + REINFORCEMENT",
                        accent=BLUE,
                        tint=BLUE_LIGHT,
                        background=CONCRETE_BG,
                    ),
                ),
                PageTemplate(
                    id="steel",
                    frames=track_frames("steel"),
                    onPage=lambda c, d: draw_track_page(
                        c,
                        d,
                        track="STEEL STRUCTURES",
                        eyebrow="TRACK 02  /  MODELING + CONNECTION DETAILING",
                        accent=AMBER,
                        tint=AMBER_LIGHT,
                        background=STEEL_BG,
                    ),
                ),
            ]
        )


def draw_brand(c: Canvas, x: float, y: float, light: bool = False) -> None:
    """Draw the compact Structra wordmark; y is the top edge."""
    text_color = WHITE if light else NAVY
    secondary = HexColor("#B8C4D6") if light else MUTED

    # Abstract pair of structural roof / frame planes.
    c.setFillColor(WHITE if light else NAVY)
    p = c.beginPath()
    p.moveTo(x, y - 17)
    p.lineTo(x + 8.2, y)
    p.lineTo(x + 16.4, y - 17)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.setFillColor(BLUE)
    p2 = c.beginPath()
    p2.moveTo(x + 11.5, y - 17)
    p2.lineTo(x + 17.4, y - 5.5)
    p2.lineTo(x + 23.2, y - 17)
    p2.close()
    c.drawPath(p2, stroke=0, fill=1)

    c.setFillColor(text_color)
    c.setFont(BOLD_FONT, 8.5)
    c.drawString(x + 30, y - 7.5, "STRUCTRA")
    c.setFillColor(secondary)
    c.setFont(BOLD_FONT, 4.7)
    c.drawString(x + 30.2, y - 15.6, "TRAINING")


def draw_grid(
    c: Canvas,
    color,
    spacing: float = 22.0,
    *,
    bottom: float = 0,
    top: float = PAGE_H,
) -> None:
    """Draw a subtle page grid within the requested vertical region."""
    c.setStrokeColor(color)
    c.setLineWidth(0.25)
    x = 0.0
    while x <= PAGE_W:
        c.line(x, bottom, x, top)
        x += spacing
    y = bottom
    while y <= top:
        c.line(0, y, PAGE_W, y)
        y += spacing


def prepared_image(
    path: Path,
    target_width: int,
    target_height: int,
    *,
    trim_white: bool = False,
    fit: str = "contain",
) -> ImageReader:
    image = Image.open(path).convert("RGB")
    if trim_white:
        background = Image.new("RGB", image.size, "white")
        difference = ImageChops.difference(image, background).convert("L")
        # Ignore near-white JPEG noise before finding the useful illustration.
        difference = difference.point(lambda p: 255 if p > 20 else 0)
        box = difference.getbbox()
        if box:
            left, top, right, bottom = box
            pad_x = max(8, int((right - left) * 0.04))
            pad_y = max(8, int((bottom - top) * 0.04))
            image = image.crop(
                (
                    max(0, left - pad_x),
                    max(0, top - pad_y),
                    min(image.width, right + pad_x),
                    min(image.height, bottom + pad_y),
                )
            )

    if fit == "cover":
        image = ImageOps.fit(
            image,
            (target_width, target_height),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )
    else:
        image.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (target_width, target_height), "white")
        canvas.paste(
            image,
            ((target_width - image.width) // 2, (target_height - image.height) // 2),
        )
        image = canvas

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=88, optimize=True)
    buffer.seek(0)
    return ImageReader(buffer)


def draw_image_card(
    c: Canvas,
    image: ImageReader,
    x: float,
    y: float,
    width: float,
    height: float,
    caption: str,
    accent,
) -> None:
    c.setFillColor(HexColor("#0A1424"))
    c.roundRect(x + 1.5, y - 2, width, height + 2, 8, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.roundRect(x, y, width, height, 8, stroke=0, fill=1)

    image_pad = 5.5
    caption_h = 23
    c.drawImage(
        image,
        x + image_pad,
        y + caption_h,
        width - 2 * image_pad,
        height - caption_h - image_pad,
        preserveAspectRatio=False,
        mask="auto",
    )
    c.setFillColor(accent)
    c.roundRect(x + 7, y + 6, 5, 5, 2.5, stroke=0, fill=1)
    c.setFillColor(NAVY)
    c.setFont(BOLD_FONT, 6.5)
    c.drawString(x + 17, y + 6.1, caption.upper())


def draw_detail_card(
    c: Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    label: str,
    value: str,
    accent,
) -> None:
    c.setFillColor(WHITE)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.55)
    c.roundRect(x, y, width, height, 7, stroke=1, fill=1)
    c.setFillColor(accent)
    c.roundRect(x, y + height - 3.2, width, 3.2, 1.6, stroke=0, fill=1)
    c.setFillColor(MUTED)
    c.setFont(BOLD_FONT, 5.6)
    c.drawString(x + 9, y + height - 17, label.upper())

    # Values are controlled document copy and may contain simple <br/> breaks.
    para = Paragraph(value, DETAIL_STYLE)
    _, ph = para.wrap(width - 18, height - 25)
    para.drawOn(c, x + 9, y + height - 23 - ph)


def draw_cover(c: Canvas, doc: BaseDocTemplate) -> None:
    c.saveState()
    c.setTitle("Revit for Structures — Course Outline")
    c.setAuthor("Structra Training")
    c.setSubject("Steel and concrete structural modeling in Autodesk Revit")

    c.setFillColor(COVER_BG)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    draw_grid(c, HexColor("#E3E8F0"), spacing=24)

    hero_bottom = PAGE_H - 470
    c.setFillColor(NAVY)
    c.rect(0, hero_bottom, PAGE_W, 470, stroke=0, fill=1)
    draw_grid(c, NAVY_2, spacing=24, bottom=hero_bottom, top=PAGE_H)

    # Architectural planes provide depth while preserving a calm title area.
    c.setFillColor(NAVY_2)
    p = c.beginPath()
    p.moveTo(PAGE_W - 180, PAGE_H)
    p.lineTo(PAGE_W, PAGE_H)
    p.lineTo(PAGE_W, PAGE_H - 255)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.setFillColor(HexColor("#1F3658"))
    p = c.beginPath()
    p.moveTo(PAGE_W - 80, PAGE_H)
    p.lineTo(PAGE_W, PAGE_H)
    p.lineTo(PAGE_W, PAGE_H - 145)
    p.close()
    c.drawPath(p, stroke=0, fill=1)

    draw_brand(c, 36, PAGE_H - 31, light=True)

    c.setFillColor(BLUE)
    c.roundRect(PAGE_W - 128, PAGE_H - 51, 92, 22, 11, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.setFont(BOLD_FONT, 6.4)
    c.drawCentredString(PAGE_W - 82, PAGE_H - 43.5, "SEPTEMBER 2026 INTAKE")

    c.setFillColor(HexColor("#AFC0DB"))
    c.setFont(BOLD_FONT, 6.8)
    c.drawString(36, PAGE_H - 83, "AUTODESK REVIT  /  STRUCTURAL BIM TRAINING")

    c.setFillColor(WHITE)
    c.setFont(BOLD_FONT, 31)
    c.drawString(36, PAGE_H - 126, "REVIT FOR")
    c.setFont(BOLD_FONT, 42)
    c.drawString(36, PAGE_H - 169, "STRUCTURES")

    c.setFillColor(HexColor("#C9D4E6"))
    c.setFont(REGULAR_FONT, 8.4)
    c.drawString(38, PAGE_H - 192, "Build coordinated, buildable structural models — from datum to documentation.")

    pill_y = PAGE_H - 224
    c.setFillColor(BLUE)
    c.roundRect(36, pill_y, 154, 21, 10.5, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.setFont(BOLD_FONT, 6.1)
    c.drawCentredString(113, pill_y + 7.2, "REINFORCED CONCRETE TRACK")
    c.setFillColor(AMBER)
    c.roundRect(199, pill_y, 90, 21, 10.5, stroke=0, fill=1)
    c.setFillColor(NAVY)
    c.drawCentredString(244, pill_y + 7.2, "STEEL TRACK")

    concrete_img = prepared_image(
        ROOT / "21 floors + 2 Basements.jpeg",
        560,
        258,
        trim_white=True,
        fit="contain",
    )
    steel_img = prepared_image(
        ROOT / "Steel portal frame structure.jpeg",
        560,
        258,
        trim_white=True,
        fit="contain",
    )
    cards_y = PAGE_H - 449
    card_gap = 10
    card_w = (PAGE_W - 72 - card_gap) / 2
    draw_image_card(c, concrete_img, 36, cards_y, card_w, 169, "Concrete structures", BLUE)
    draw_image_card(
        c,
        steel_img,
        36 + card_w + card_gap,
        cards_y,
        card_w,
        169,
        "Steel structures",
        AMBER,
    )

    # Overview begins at a fixed top line so the lower section feels anchored.
    c.setFillColor(BLUE)
    c.roundRect(36, PAGE_H - 503, 28, 4, 2, stroke=0, fill=1)
    c.setFillColor(NAVY)
    c.setFont(BOLD_FONT, 11.2)
    c.drawString(36, PAGE_H - 521, "PROGRAM OVERVIEW")

    overview = (
        "Revit for Structures is a hands-on program for engineering students and early-career "
        "professionals who want to build real structural models — not just attractive renders. "
        "Choose either focused track or take both, progressing from Revit fundamentals through "
        "modeling, detailing, schedules and construction documentation."
    )
    overview_para = Paragraph(overview, OVERVIEW_STYLE)
    _, overview_h = overview_para.wrap(PAGE_W - 72, 70)
    overview_para.drawOn(c, 36, PAGE_H - 535 - overview_h)

    detail_top = PAGE_H - 600
    detail_gap = 9
    detail_w = (PAGE_W - 72 - 2 * detail_gap) / 3
    detail_h = 75
    details = [
        ("Start date", "Monday, 14 September 2026<br/>Third week of September", BLUE),
        ("Format", "100% online<br/>Live instructor-led sessions via Zoom", BLUE),
        ("Duration", "4 weeks per track<br/>Weekday evenings", BLUE),
        ("Fee", "KSH 2,500 per track", AMBER),
        (
            "Who it’s for",
            "University engineering students and early-career structural / BIM professionals",
            AMBER,
        ),
        (
            "Prerequisites",
            "A laptop capable of running Revit; no prior Revit experience required",
            AMBER,
        ),
    ]
    for index, (label, value, accent) in enumerate(details):
        row, col = divmod(index, 3)
        x = 36 + col * (detail_w + detail_gap)
        y = detail_top - detail_h - row * (detail_h + detail_gap)
        draw_detail_card(c, x, y, detail_w, detail_h, label, value, accent)

    c.setStrokeColor(LINE)
    c.setLineWidth(0.55)
    c.line(36, 32, PAGE_W - 36, 32)
    c.setFillColor(MUTED)
    c.setFont(REGULAR_FONT, 6.2)
    c.drawString(36, 20, "structratraining.co.ke")
    c.drawCentredString(PAGE_W / 2, 20, "+254 7XX XXX XXX")
    c.setFont(BOLD_FONT, 6.2)
    c.drawRightString(PAGE_W - 36, 20, "COURSE OUTLINE  /  2026")
    c.restoreState()


def draw_track_page(
    c: Canvas,
    doc: BaseDocTemplate,
    *,
    track: str,
    eyebrow: str,
    accent,
    tint,
    background,
) -> None:
    c.saveState()
    c.setFillColor(background)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

    # Consistent top alignment across every curriculum page.
    header_h = 111
    c.setFillColor(NAVY)
    c.rect(0, PAGE_H - header_h, PAGE_W, header_h, stroke=0, fill=1)
    c.setFillColor(NAVY_2)
    p = c.beginPath()
    p.moveTo(PAGE_W - 145, PAGE_H)
    p.lineTo(PAGE_W, PAGE_H)
    p.lineTo(PAGE_W, PAGE_H - header_h)
    p.lineTo(PAGE_W - 80, PAGE_H - header_h)
    p.close()
    c.drawPath(p, stroke=0, fill=1)

    # A restrained blueprint grid remains only in the header.
    c.setStrokeColor(HexColor("#243B5E"))
    c.setLineWidth(0.25)
    for x in range(0, int(PAGE_W) + 1, 24):
        c.line(x, PAGE_H - header_h, x, PAGE_H)
    for y in range(int(PAGE_H - header_h), int(PAGE_H) + 1, 24):
        c.line(0, y, PAGE_W, y)

    draw_brand(c, 38, PAGE_H - 24, light=True)
    c.setFillColor(HexColor("#AFC0DB"))
    c.setFont(BOLD_FONT, 5.8)
    c.drawRightString(PAGE_W - 38, PAGE_H - 37, "REVIT FOR STRUCTURES  /  COURSE OUTLINE")

    c.setFillColor(accent)
    c.roundRect(38, PAGE_H - 66, 32, 3.5, 1.75, stroke=0, fill=1)
    c.setFillColor(HexColor("#B9C6D9"))
    c.setFont(BOLD_FONT, 5.9)
    c.drawString(38, PAGE_H - 78, eyebrow)
    c.setFillColor(WHITE)
    c.setFont(BOLD_FONT, 17.5)
    c.drawString(38, PAGE_H - 101, track)

    c.setFillColor(tint)
    c.circle(PAGE_W - 48, PAGE_H - 85, 21, stroke=0, fill=1)
    c.setFillColor(accent)
    c.setFont(BOLD_FONT, 7.5)
    c.drawCentredString(PAGE_W - 48, PAGE_H - 87.5, "BIM")

    c.setFillColor(accent)
    c.rect(0, PAGE_H - header_h - 4, PAGE_W, 4, stroke=0, fill=1)

    # Vertical guide and footer lock all pages to the same underlying grid.
    c.setStrokeColor(LINE)
    c.setLineWidth(0.45)
    c.line(PAGE_W / 2, 47, PAGE_W / 2, PAGE_H - 126)
    c.line(38, 35, PAGE_W - 38, 35)
    c.setFillColor(MUTED)
    c.setFont(REGULAR_FONT, 6.0)
    c.drawString(38, 22, "structratraining.co.ke   •   +254 7XX XXX XXX")
    c.setFont(BOLD_FONT, 6.0)
    c.drawRightString(PAGE_W - 38, 22, f"{doc.page:02d}  /  STRUCTRA TRAINING")
    c.restoreState()


def module_story(
    modules: Iterable[tuple[str, Sequence[str]]],
    *,
    accent,
    tint,
    start_number: int = 1,
) -> list[Flowable]:
    return [
        ModuleCard(number, title, items, accent, tint)
        for number, (title, items) in enumerate(modules, start=start_number)
    ]


def module_slice(
    modules: Sequence[tuple[str, Sequence[str]]],
    start: int,
    stop: int,
    *,
    accent,
    tint,
) -> list[Flowable]:
    """Create cards for a one-based, inclusive module range."""
    return module_story(
        modules[start - 1 : stop],
        accent=accent,
        tint=tint,
        start_number=start,
    )


def build_pdf(output: Path = OUTPUT) -> None:
    document = StructraDocTemplate(output)
    story: list[Flowable] = [
        # Cover -> concrete page 1, balanced deliberately across both columns.
        NextPageTemplate("concrete"),
        PageBreak(),
        *module_slice(CONCRETE_MODULES, 1, 6, accent=BLUE, tint=BLUE_LIGHT),
        FrameBreak(),
        *module_slice(CONCRETE_MODULES, 7, 11, accent=BLUE, tint=BLUE_LIGHT),
        PageBreak(),
        # Concrete page 2. Explicit frame breaks prevent a sparse final column.
        *module_slice(CONCRETE_MODULES, 12, 15, accent=BLUE, tint=BLUE_LIGHT),
        FrameBreak(),
        *module_slice(CONCRETE_MODULES, 16, 20, accent=BLUE, tint=BLUE_LIGHT),
        # Steel pages use the same top-aligned, deliberately balanced columns.
        NextPageTemplate("steel"),
        PageBreak(),
        *module_slice(STEEL_MODULES, 1, 5, accent=AMBER, tint=AMBER_LIGHT),
        FrameBreak(),
        *module_slice(STEEL_MODULES, 6, 10, accent=AMBER, tint=AMBER_LIGHT),
        PageBreak(),
        *module_slice(STEEL_MODULES, 11, 16, accent=AMBER, tint=AMBER_LIGHT),
        FrameBreak(),
        *module_slice(STEEL_MODULES, 17, 21, accent=AMBER, tint=AMBER_LIGHT),
        PageBreak(),
        *module_slice(STEEL_MODULES, 22, 24, accent=AMBER, tint=AMBER_LIGHT),
        FrameBreak(),
        *module_slice(STEEL_MODULES, 25, 29, accent=AMBER, tint=AMBER_LIGHT),
    ]
    document.build(story)


if __name__ == "__main__":
    build_pdf()
    print(f"Created {OUTPUT.relative_to(ROOT)}")
