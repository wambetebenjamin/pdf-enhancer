#!/usr/bin/env python3
"""Generate the premium Structra Revit for Structures course outline.

Run from the repository root:
    python scripts/generate_enhanced_outline.py

Dependencies:
    reportlab>=4.0
    Pillow>=10.0
"""

from __future__ import annotations

import html
import io
from pathlib import Path
from typing import Iterable, Sequence

from PIL import Image, ImageChops
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
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

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "Revit_for_Structures_Course_Outline_Enhanced.pdf"
PAGE_W, PAGE_H = A4

# A warm editorial palette: restrained enough to feel premium, soft enough to
# remain friendly and approachable.
INK = HexColor("#18312F")
INK_2 = HexColor("#294542")
CREAM = HexColor("#F7F3EC")
PAPER = HexColor("#FFFDF9")
WHITE = HexColor("#FFFFFF")
MUTED = HexColor("#667571")
HAIRLINE = HexColor("#DFE4DE")
LAVENDER = HexColor("#7269E8")
LAVENDER_DARK = HexColor("#5148BC")
LILAC = HexColor("#ECE9FF")
LILAC_SOFT = HexColor("#F5F3FF")
TERRACOTTA = HexColor("#C8754F")
TERRACOTTA_DARK = HexColor("#975137")
PEACH = HexColor("#F7E4D8")
PEACH_SOFT = HexColor("#FCF4EE")
MINT = HexColor("#DDEDE7")
TEAL = HexColor("#2D776C")

BODY_FONT = "Helvetica"
MEDIUM_FONT = "Helvetica"
SEMIBOLD_FONT = "Helvetica-Bold"
BOLD_FONT = "Helvetica-Bold"
DISPLAY_FONT = "Times-Bold"


def register_fonts() -> None:
    """Register bundled OFL fonts so the document renders consistently."""
    global BODY_FONT, MEDIUM_FONT, SEMIBOLD_FONT, BOLD_FONT, DISPLAY_FONT
    sans_dir = ROOT / "assets" / "fonts" / "plus-jakarta-sans"
    display_path = ROOT / "assets" / "fonts" / "fraunces" / "Fraunces-SemiBold.ttf"
    files = {
        "Structra-Regular": sans_dir / "PlusJakartaSans-Regular.ttf",
        "Structra-Medium": sans_dir / "PlusJakartaSans-Medium.ttf",
        "Structra-SemiBold": sans_dir / "PlusJakartaSans-SemiBold.ttf",
        "Structra-Bold": sans_dir / "PlusJakartaSans-Bold.ttf",
        "Structra-Display": display_path,
    }
    if not all(path.exists() for path in files.values()):
        return
    for name, path in files.items():
        pdfmetrics.registerFont(TTFont(name, str(path)))
    BODY_FONT = "Structra-Regular"
    MEDIUM_FONT = "Structra-Medium"
    SEMIBOLD_FONT = "Structra-SemiBold"
    BOLD_FONT = "Structra-Bold"
    DISPLAY_FONT = "Structra-Display"
    pdfmetrics.registerFontFamily(
        "Structra",
        normal=BODY_FONT,
        bold=BOLD_FONT,
        italic=BODY_FONT,
        boldItalic=BOLD_FONT,
    )


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


MODULE_TITLE_STYLE = ParagraphStyle(
    "module-title",
    fontName=SEMIBOLD_FONT,
    fontSize=9.2,
    leading=11.9,
    textColor=INK,
    alignment=TA_LEFT,
    allowWidows=0,
    allowOrphans=0,
)
MODULE_BODY_STYLE = ParagraphStyle(
    "module-body",
    fontName=BODY_FONT,
    fontSize=7.8,
    leading=10.65,
    textColor=MUTED,
    alignment=TA_LEFT,
    allowWidows=0,
    allowOrphans=0,
)
COVER_COPY_STYLE = ParagraphStyle(
    "cover-copy",
    fontName=BODY_FONT,
    fontSize=10.0,
    leading=15.2,
    textColor=INK_2,
)
OVERVIEW_COPY_STYLE = ParagraphStyle(
    "overview-copy",
    fontName=BODY_FONT,
    fontSize=9.5,
    leading=14.7,
    textColor=INK_2,
)
SMALL_COPY_STYLE = ParagraphStyle(
    "small-copy",
    fontName=BODY_FONT,
    fontSize=7.25,
    leading=10.0,
    textColor=INK_2,
)


class ModuleCard(Flowable):
    """A spacious, unsplittable curriculum module with a soft editorial card."""

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
        self.width = 0.0
        self.height = 0.0
        self.spaceAfter = 8.5
        self._title_para: Paragraph | None = None
        self._title_h = 0.0
        self._item_paras: list[Paragraph] = []
        self._item_heights: list[float] = []

    def wrap(self, avail_width: float, avail_height: float) -> tuple[float, float]:
        self.width = avail_width
        pad = 10.5
        number_area = 31.0
        title_width = avail_width - 2 * pad - number_area
        item_width = avail_width - 2 * pad - 14.0

        self._title_para = Paragraph(html.escape(self.title), MODULE_TITLE_STYLE)
        _, self._title_h = self._title_para.wrap(title_width, 180)

        self._item_paras = []
        self._item_heights = []
        for item in self.items:
            para = Paragraph(html.escape(item), MODULE_BODY_STYLE)
            _, item_h = para.wrap(item_width, 180)
            self._item_paras.append(para)
            self._item_heights.append(item_h)

        header_h = max(22.0, self._title_h)
        item_gaps = max(0, len(self.items) - 1) * 1.55
        self.height = 10.0 + header_h + 5.0 + sum(self._item_heights) + item_gaps + 10.0
        return self.width, self.height

    def draw(self) -> None:
        c = self.canv
        w, h = self.width, self.height
        pad = 10.5
        fill = PAPER if self.number % 2 else self.tint

        # Gentle lift rather than a heavy drop shadow.
        c.setFillColor(HexColor("#E8E5DE"))
        c.roundRect(1.2, -1.4, w - 1.2, h, 10.5, stroke=0, fill=1)
        c.setFillColor(fill)
        c.setStrokeColor(HexColor("#E1E2DC"))
        c.setLineWidth(0.55)
        c.roundRect(0, 0, w - 1.2, h, 10.5, stroke=1, fill=1)

        top = h - 10.0
        badge_w, badge_h = 25.0, 20.0
        c.setFillColor(self.tint)
        c.roundRect(pad, top - badge_h, badge_w, badge_h, 10, stroke=0, fill=1)
        c.setFillColor(self.accent)
        c.setFont(BOLD_FONT, 6.7)
        c.drawCentredString(pad + badge_w / 2, top - 13.3, f"{self.number:02d}")

        assert self._title_para is not None
        title_x = pad + 31.0
        self._title_para.drawOn(c, title_x, top - self._title_h)

        header_h = max(22.0, self._title_h)
        cursor = top - header_h - 5.0
        text_x = pad + 13.0
        for para, para_h in zip(self._item_paras, self._item_heights):
            c.setFillColor(self.accent)
            c.circle(pad + 4.3, cursor - 4.2, 1.1, stroke=0, fill=1)
            para.drawOn(c, text_x, cursor - para_h)
            cursor -= para_h + 1.55


class PremiumDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str | Path) -> None:
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
            creator="Structra Training premium course outline generator",
            pageCompression=1,
        )

        blank_frame = Frame(
            0,
            0,
            PAGE_W,
            PAGE_H,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
            id="full-page",
        )

        side = 13.5 * mm
        gutter = 6.0 * mm
        bottom = 17.0 * mm
        top = PAGE_H - 55.0 * mm
        column_w = (PAGE_W - 2 * side - gutter) / 2
        column_h = top - bottom

        def frames(prefix: str) -> list[Frame]:
            return [
                Frame(
                    side,
                    bottom,
                    column_w,
                    column_h,
                    leftPadding=0,
                    rightPadding=0,
                    topPadding=0,
                    bottomPadding=0,
                    id=f"{prefix}-left",
                ),
                Frame(
                    side + column_w + gutter,
                    bottom,
                    column_w,
                    column_h,
                    leftPadding=0,
                    rightPadding=0,
                    topPadding=0,
                    bottomPadding=0,
                    id=f"{prefix}-right",
                ),
            ]

        specs = [
            (
                "concrete-a",
                "TRACK ONE",
                "Reinforced concrete",
                "Foundations, datum + core structural elements",
                "MODULES 01–11",
                LAVENDER,
                LILAC,
                LILAC_SOFT,
            ),
            (
                "concrete-b",
                "TRACK ONE",
                "Reinforced concrete",
                "Reinforcement, documentation + export",
                "MODULES 12–20",
                LAVENDER,
                LILAC,
                LILAC_SOFT,
            ),
            (
                "steel-a",
                "TRACK TWO",
                "Steel structures",
                "Datum, columns, rafters + framing systems",
                "MODULES 01–10",
                TERRACOTTA,
                PEACH,
                PEACH_SOFT,
            ),
            (
                "steel-b",
                "TRACK TWO",
                "Steel structures",
                "Composite systems, bracing + connections",
                "MODULES 11–21",
                TERRACOTTA,
                PEACH,
                PEACH_SOFT,
            ),
            (
                "steel-c",
                "TRACK TWO",
                "Steel structures",
                "Connection detailing, schedules + deliverables",
                "MODULES 22–29",
                TERRACOTTA,
                PEACH,
                PEACH_SOFT,
            ),
        ]

        templates: list[PageTemplate] = [
            PageTemplate(id="cover", frames=[blank_frame], onPage=draw_cover),
            PageTemplate(id="overview", frames=[blank_frame], onPage=draw_overview),
        ]
        for template_id, eyebrow, title, subtitle, module_range, accent, tint, background in specs:
            templates.append(
                PageTemplate(
                    id=template_id,
                    frames=frames(template_id),
                    onPage=lambda c, d, e=eyebrow, t=title, s=subtitle, r=module_range, a=accent, ti=tint, bg=background: draw_curriculum_page(
                        c,
                        d,
                        eyebrow=e,
                        title=t,
                        subtitle=s,
                        module_range=r,
                        accent=a,
                        tint=ti,
                        background=bg,
                    ),
                )
            )
        self.addPageTemplates(templates)


def top_y(distance: float) -> float:
    return PAGE_H - distance


def draw_wordmark(c: Canvas, x: float, y_top: float, *, reversed: bool = False) -> None:
    """Draw a compact, warm wordmark; y_top is measured from the page bottom."""
    primary = WHITE if reversed else INK
    secondary = HexColor("#CBD7D3") if reversed else MUTED
    icon_bg = WHITE if reversed else INK
    icon_fg = INK if reversed else CREAM

    c.setFillColor(icon_bg)
    c.roundRect(x, y_top - 25, 25, 25, 7.5, stroke=0, fill=1)
    c.setStrokeColor(icon_fg)
    c.setLineWidth(2.0)
    c.setLineCap(1)
    c.line(x + 7, y_top - 18, x + 7, y_top - 10)
    c.line(x + 12.5, y_top - 18, x + 12.5, y_top - 6.5)
    c.line(x + 18, y_top - 18, x + 18, y_top - 12)
    c.line(x + 6, y_top - 18, x + 19, y_top - 18)

    c.setFillColor(primary)
    c.setFont(BOLD_FONT, 8.7)
    c.drawString(x + 34, y_top - 10.2, "STRUCTRA")
    c.setFillColor(secondary)
    c.setFont(SEMIBOLD_FONT, 4.8)
    c.drawString(x + 34.2, y_top - 19.0, "TRAINING")


def trim_image(image: Image.Image, threshold: int = 20) -> Image.Image:
    rgb = image.convert("RGB")
    difference = ImageChops.difference(rgb, Image.new("RGB", rgb.size, "white")).convert("L")
    difference = difference.point(lambda p: 255 if p > threshold else 0)
    box = difference.getbbox()
    if not box:
        return rgb
    left, top, right, bottom = box
    pad_x = max(8, int((right - left) * 0.03))
    pad_y = max(8, int((bottom - top) * 0.03))
    return rgb.crop(
        (
            max(0, left - pad_x),
            max(0, top - pad_y),
            min(rgb.width, right + pad_x),
            min(rgb.height, bottom + pad_y),
        )
    )


def transparent_model(
    path: Path,
    target_w: int,
    target_h: int,
    *,
    crop: tuple[int, int, int, int] | None = None,
) -> ImageReader:
    """Remove a near-white drawing background and return a fitted PNG."""
    image = Image.open(path).convert("RGB")
    if crop:
        image = image.crop(crop)
    image = trim_image(image)
    image.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)

    rgba = image.convert("RGBA")
    pixels = rgba.load()
    for py in range(rgba.height):
        for px in range(rgba.width):
            red, green, blue, _ = pixels[px, py]
            darkness = 255 - min(red, green, blue)
            alpha = max(0, min(255, (darkness - 5) * 6))
            pixels[px, py] = (red, green, blue, alpha)

    canvas = Image.new("RGBA", (target_w, target_h), (255, 255, 255, 0))
    canvas.alpha_composite(
        rgba,
        ((target_w - rgba.width) // 2, (target_h - rgba.height) // 2),
    )
    buffer = io.BytesIO()
    canvas.save(buffer, format="PNG", optimize=True)
    buffer.seek(0)
    return ImageReader(buffer)


def draw_soft_shadow_card(
    c: Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    radius: float = 15,
    fill=PAPER,
    border=HAIRLINE,
) -> None:
    c.setFillColor(HexColor("#E7E1D8"))
    c.roundRect(x + 2, y - 3, width, height, radius, stroke=0, fill=1)
    c.setFillColor(fill)
    c.setStrokeColor(border)
    c.setLineWidth(0.55)
    c.roundRect(x, y, width, height, radius, stroke=1, fill=1)


def draw_pill(
    c: Canvas,
    x: float,
    y: float,
    width: float,
    label: str,
    *,
    fill,
    text_color,
    height: float = 23,
) -> None:
    c.setFillColor(fill)
    c.roundRect(x, y, width, height, height / 2, stroke=0, fill=1)
    c.setFillColor(text_color)
    c.setFont(BOLD_FONT, 6.2)
    c.drawCentredString(x + width / 2, y + height / 2 - 2.25, label)


def draw_spark(c: Canvas, x: float, y: float, color, size: float = 8) -> None:
    c.setStrokeColor(color)
    c.setLineWidth(1.2)
    c.setLineCap(1)
    c.line(x - size, y, x + size, y)
    c.line(x, y - size, x, y + size)
    c.line(x - size * 0.55, y - size * 0.55, x + size * 0.55, y + size * 0.55)
    c.line(x - size * 0.55, y + size * 0.55, x + size * 0.55, y - size * 0.55)


def draw_footer(c: Canvas, page_number: int, *, accent=MUTED) -> None:
    c.setStrokeColor(HAIRLINE)
    c.setLineWidth(0.5)
    c.line(39, 35, PAGE_W - 39, 35)
    c.setFillColor(MUTED)
    c.setFont(MEDIUM_FONT, 5.8)
    c.drawString(39, 21, "structratraining.co.ke")
    c.drawCentredString(PAGE_W / 2, 21, "+254 7XX XXX XXX")
    c.setFillColor(accent)
    c.setFont(BOLD_FONT, 5.8)
    c.drawRightString(PAGE_W - 39, 21, f"{page_number:02d}  /  07")
    c.linkURL("https://structratraining.co.ke", (39, 16, 129, 29), relative=0)


def draw_cover(c: Canvas, doc: BaseDocTemplate) -> None:
    c.saveState()
    c.setTitle("Revit for Structures — Course Outline")
    c.setAuthor("Structra Training")
    c.setSubject("Steel and concrete structural modeling in Autodesk Revit")

    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

    # Soft oversized forms make the cover inviting without sacrificing polish.
    c.setFillColor(LILAC)
    c.circle(PAGE_W + 45, PAGE_H - 95, 155, stroke=0, fill=1)
    c.setFillColor(PEACH)
    c.circle(-35, 58, 118, stroke=0, fill=1)
    c.setStrokeColor(HexColor("#D9D2C8"))
    c.setLineWidth(0.65)
    c.circle(PAGE_W - 72, 86, 72, stroke=1, fill=0)
    c.circle(PAGE_W - 72, 86, 56, stroke=1, fill=0)

    draw_wordmark(c, 43, top_y(34))
    draw_pill(
        c,
        43,
        top_y(112),
        172,
        "LIVE ONLINE  •  SEPTEMBER 2026",
        fill=MINT,
        text_color=TEAL,
        height=25,
    )

    c.setFillColor(INK)
    c.setFont(MEDIUM_FONT, 22)
    c.drawString(43, top_y(166), "Revit for")
    c.setFont(DISPLAY_FONT, 47)
    c.drawString(41, top_y(218), "Structures")

    copy = (
        "Learn to model with confidence. Create coordinated concrete and steel "
        "structures in Autodesk Revit — then turn them into clear, buildable documentation."
    )
    para = Paragraph(copy, COVER_COPY_STYLE)
    _, ph = para.wrap(262, 100)
    para.drawOn(c, 43, top_y(247) - ph)

    draw_pill(c, 43, top_y(357), 130, "CONCRETE TRACK", fill=LILAC, text_color=LAVENDER_DARK)
    draw_pill(c, 181, top_y(357), 96, "STEEL TRACK", fill=PEACH, text_color=TERRACOTTA_DARK)

    draw_soft_shadow_card(c, 43, top_y(516), 248, 112, radius=17, fill=PAPER)
    c.setFillColor(LAVENDER)
    c.setFont(BOLD_FONT, 6.3)
    c.drawString(61, top_y(431), "NEXT INTAKE")
    c.setFillColor(INK)
    c.setFont(DISPLAY_FONT, 15.8)
    c.drawString(60, top_y(458), "Monday, 14 September 2026")
    c.setFillColor(MUTED)
    c.setFont(MEDIUM_FONT, 7.6)
    c.drawString(61, top_y(477), "Weekday evenings  •  Live instructor-led Zoom sessions")
    c.setFillColor(TEAL)
    c.roundRect(61, top_y(503), 116, 20, 10, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.setFont(BOLD_FONT, 6.2)
    c.drawCentredString(119, top_y(496.5), "NO PRIOR REVIT NEEDED")

    # Spacious hero panel and isolated model: cleaner than a screenshot collage.
    panel_x, panel_y, panel_w, panel_h = 319, 129, 232, 596
    c.setFillColor(HexColor("#DED9F7"))
    c.roundRect(panel_x + 3, panel_y - 4, panel_w, panel_h, 28, stroke=0, fill=1)
    c.setFillColor(LILAC)
    c.roundRect(panel_x, panel_y, panel_w, panel_h, 28, stroke=0, fill=1)
    c.setFillColor(PEACH)
    c.circle(panel_x + panel_w - 35, panel_y + panel_h - 64, 54, stroke=0, fill=1)
    c.setFillColor(MINT)
    c.circle(panel_x + 28, panel_y + 80, 48, stroke=0, fill=1)
    c.setStrokeColor(WHITE)
    c.setLineWidth(0.8)
    c.circle(panel_x + panel_w - 36, panel_y + 84, 30, stroke=1, fill=0)
    c.circle(panel_x + panel_w - 36, panel_y + 84, 41, stroke=1, fill=0)
    draw_spark(c, panel_x + 36, panel_y + panel_h - 50, LAVENDER_DARK, 7)

    model = transparent_model(ROOT / "21 floors + 2 Basements.jpeg", 900, 1050)
    c.drawImage(model, panel_x + 8, panel_y + 93, panel_w - 16, 430, mask="auto")

    c.setFillColor(INK)
    c.setFont(BOLD_FONT, 6.2)
    c.drawString(panel_x + 22, panel_y + 49, "COURSE OUTLINE  /  2026")
    c.setFillColor(MUTED)
    c.setFont(BODY_FONT, 7.0)
    c.drawString(panel_x + 22, panel_y + 30, "Model  •  Detail  •  Document")

    # Friendly, scanable essentials.
    stats_y = 188
    stats = [
        ("4 weeks", "per track"),
        ("KSH 2,500", "per track"),
        ("100% online", "live on Zoom"),
    ]
    for index, (value, label) in enumerate(stats):
        x = 43 + index * 88
        c.setFillColor(INK)
        c.setFont(SEMIBOLD_FONT, 8.2)
        c.drawString(x, stats_y, value)
        c.setFillColor(MUTED)
        c.setFont(BODY_FONT, 6.3)
        c.drawString(x, stats_y - 13, label)

    c.setFillColor(INK)
    c.setFont(DISPLAY_FONT, 15.5)
    c.drawString(43, 112, "Build something real.")
    c.setFillColor(MUTED)
    c.setFont(BODY_FONT, 7.4)
    c.drawString(43, 93, "Two focused tracks. One practical, portfolio-ready learning experience.")

    c.setStrokeColor(HexColor("#D7D1C8"))
    c.setLineWidth(0.55)
    c.line(43, 54, PAGE_W - 43, 54)
    c.setFillColor(MUTED)
    c.setFont(MEDIUM_FONT, 6.1)
    c.drawString(43, 36, "structratraining.co.ke")
    c.drawCentredString(PAGE_W / 2, 36, "+254 7XX XXX XXX")
    c.setFillColor(INK)
    c.setFont(BOLD_FONT, 6.1)
    c.drawRightString(PAGE_W - 43, 36, "STRUCTRA TRAINING")
    c.restoreState()


def draw_icon(c: Canvas, kind: str, cx: float, cy: float, color) -> None:
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.25)
    c.setLineCap(1)
    c.setLineJoin(1)
    if kind == "calendar":
        c.roundRect(cx - 7, cy - 6, 14, 12, 2, stroke=1, fill=0)
        c.line(cx - 7, cy + 2, cx + 7, cy + 2)
        c.line(cx - 3.5, cy + 8, cx - 3.5, cy + 4.5)
        c.line(cx + 3.5, cy + 8, cx + 3.5, cy + 4.5)
    elif kind == "video":
        c.roundRect(cx - 7, cy - 5, 10, 10, 2, stroke=1, fill=0)
        p = c.beginPath()
        p.moveTo(cx + 4, cy + 3.5)
        p.lineTo(cx + 8, cy + 6)
        p.lineTo(cx + 8, cy - 6)
        p.lineTo(cx + 4, cy - 3.5)
        p.close()
        c.drawPath(p, stroke=1, fill=0)
    elif kind == "clock":
        c.circle(cx, cy, 7, stroke=1, fill=0)
        c.line(cx, cy, cx, cy + 4)
        c.line(cx, cy, cx + 3.5, cy - 2)
    elif kind == "fee":
        c.circle(cx, cy, 7, stroke=1, fill=0)
        c.setFont(BOLD_FONT, 6.2)
        c.drawCentredString(cx, cy - 2.2, "K")
    elif kind == "people":
        c.circle(cx - 3, cy + 3, 3, stroke=1, fill=0)
        c.circle(cx + 4, cy + 2, 2.3, stroke=1, fill=0)
        c.arc(cx - 9, cy - 8, cx + 3, cy + 1, 5, 170)
        c.arc(cx - 1, cy - 7, cx + 9, cy, 10, 160)
    else:
        c.roundRect(cx - 7, cy - 5, 14, 10, 1.5, stroke=1, fill=0)
        c.line(cx - 9, cy - 8, cx + 9, cy - 8)
        c.line(cx - 5, cy - 5, cx - 6, cy - 8)
        c.line(cx + 5, cy - 5, cx + 6, cy - 8)


def draw_info_card(
    c: Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    icon: str,
    label: str,
    value: str,
    accent,
    tint,
) -> None:
    draw_soft_shadow_card(c, x, y, width, height, radius=12, fill=PAPER)
    c.setFillColor(tint)
    c.circle(x + 24, y + height - 24, 13, stroke=0, fill=1)
    draw_icon(c, icon, x + 24, y + height - 24, accent)
    c.setFillColor(MUTED)
    c.setFont(BOLD_FONT, 5.4)
    c.drawString(x + 45, y + height - 18, label.upper())
    value_para = Paragraph(value, SMALL_COPY_STYLE)
    _, ph = value_para.wrap(width - 55, height - 28)
    value_para.drawOn(c, x + 45, y + height - 26 - ph)


def draw_track_choice_card(
    c: Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    track_label: str,
    title: str,
    detail: str,
    modules: str,
    accent,
    tint,
    image: ImageReader,
) -> None:
    draw_soft_shadow_card(c, x, y, width, height, radius=18, fill=tint, border=tint)
    c.setFillColor(accent)
    c.setFont(BOLD_FONT, 5.7)
    c.drawString(x + 17, y + height - 24, track_label.upper())
    c.setFillColor(INK)
    c.setFont(DISPLAY_FONT, 17)
    c.drawString(x + 16, y + height - 49, title)
    c.setFillColor(MUTED)
    c.setFont(MEDIUM_FONT, 6.7)
    c.drawString(x + 17, y + height - 66, detail)
    draw_pill(c, x + 17, y + height - 98, 83, modules, fill=PAPER, text_color=accent, height=21)
    c.drawImage(image, x + width - 126, y + 12, 114, 112, mask="auto")
    c.setFillColor(accent)
    c.circle(x + 25, y + 28, 3, stroke=0, fill=1)
    c.setFillColor(INK_2)
    c.setFont(MEDIUM_FONT, 6.2)
    c.drawString(x + 34, y + 25.5, "Flexible — choose one or both")


def draw_overview(c: Canvas, doc: BaseDocTemplate) -> None:
    c.saveState()
    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    c.setFillColor(MINT)
    c.circle(PAGE_W + 16, PAGE_H - 68, 82, stroke=0, fill=1)
    c.setFillColor(LILAC)
    c.circle(-28, 318, 75, stroke=0, fill=1)

    draw_wordmark(c, 42, top_y(31))
    c.setFillColor(MUTED)
    c.setFont(BOLD_FONT, 5.8)
    c.drawRightString(PAGE_W - 42, top_y(46), "PROGRAM OVERVIEW  /  2026")

    c.setFillColor(TEAL)
    c.setFont(BOLD_FONT, 6.4)
    c.drawString(42, top_y(91), "A PRACTICAL PATH INTO STRUCTURAL BIM")
    c.setFillColor(INK)
    c.setFont(DISPLAY_FONT, 27)
    c.drawString(40, top_y(126), "Everything you need")
    c.drawString(40, top_y(158), "to build with confidence.")

    overview = (
        "Revit for Structures is a hands-on program for engineering students and early-career "
        "professionals who want to build real, coordinated structural models — not just attractive "
        "renders. Start with the fundamentals, then progress through modeling, detailing, schedules "
        "and construction documentation."
    )
    para = Paragraph(overview, OVERVIEW_COPY_STYLE)
    _, ph = para.wrap(PAGE_W - 84, 80)
    para.drawOn(c, 42, top_y(183) - ph)

    c.setFillColor(INK)
    c.setFont(BOLD_FONT, 6.2)
    c.drawString(42, top_y(249), "AT A GLANCE")

    card_gap = 9
    card_w = (PAGE_W - 84 - 2 * card_gap) / 3
    card_h = 77
    details = [
        ("calendar", "Start date", "Monday, 14 September 2026", LAVENDER, LILAC),
        ("video", "Format", "100% online<br/>Live sessions via Zoom", TEAL, MINT),
        ("clock", "Duration", "4 weeks per track<br/>Weekday evenings", TERRACOTTA, PEACH),
        ("fee", "Fee", "KSH 2,500 per track", TERRACOTTA, PEACH),
        ("people", "Designed for", "Students + early-career structural / BIM professionals", LAVENDER, LILAC),
        ("laptop", "What you need", "A Revit-ready laptop<br/>No prior experience required", TEAL, MINT),
    ]
    top = top_y(270)
    for index, (icon, label, value, accent, tint) in enumerate(details):
        row, col = divmod(index, 3)
        x = 42 + col * (card_w + card_gap)
        y = top - card_h - row * (card_h + 9)
        draw_info_card(
            c,
            x,
            y,
            card_w,
            card_h,
            icon=icon,
            label=label,
            value=value,
            accent=accent,
            tint=tint,
        )

    c.setFillColor(INK)
    c.setFont(BOLD_FONT, 6.2)
    c.drawString(42, top_y(458), "CHOOSE YOUR TRACK")
    c.setFillColor(MUTED)
    c.setFont(BODY_FONT, 7.0)
    c.drawString(133, top_y(458), "Follow one focused route — or complete both.")

    track_gap = 12
    track_w = (PAGE_W - 84 - track_gap) / 2
    track_y = 69
    track_h = 276
    concrete_image = transparent_model(ROOT / "21 floors + 2 Basements.jpeg", 520, 480)
    steel_image = transparent_model(
        ROOT / "Steel portal frame structure.jpeg",
        520,
        440,
        crop=(175, 48, 1120, 590),
    )
    draw_track_choice_card(
        c,
        42,
        track_y,
        track_w,
        track_h,
        track_label="Track one",
        title="Concrete",
        detail="Modeling  •  reinforcement  •  sheets",
        modules="20 MODULES",
        accent=LAVENDER,
        tint=LILAC,
        image=concrete_image,
    )
    draw_track_choice_card(
        c,
        42 + track_w + track_gap,
        track_y,
        track_w,
        track_h,
        track_label="Track two",
        title="Steel",
        detail="Framing  •  connections  •  schedules",
        modules="29 MODULES",
        accent=TERRACOTTA,
        tint=PEACH,
        image=steel_image,
    )

    draw_footer(c, doc.page, accent=TEAL)
    c.restoreState()


def draw_curriculum_page(
    c: Canvas,
    doc: BaseDocTemplate,
    *,
    eyebrow: str,
    title: str,
    subtitle: str,
    module_range: str,
    accent,
    tint,
    background,
) -> None:
    c.saveState()
    c.setFillColor(background)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)

    # Quiet ornamental forms create a themed page without competing with text.
    c.setFillColor(tint)
    c.circle(PAGE_W + 14, PAGE_H - 66, 80, stroke=0, fill=1)
    c.setStrokeColor(tint)
    c.setLineWidth(9)
    c.circle(-23, 72, 64, stroke=1, fill=0)
    c.setStrokeColor(HexColor("#E7E5DF"))
    c.setLineWidth(0.45)
    c.bezier(PAGE_W - 178, PAGE_H, PAGE_W - 118, PAGE_H - 58, PAGE_W - 85, PAGE_H - 116, PAGE_W, PAGE_H - 126)
    c.bezier(PAGE_W - 153, PAGE_H, PAGE_W - 105, PAGE_H - 56, PAGE_W - 65, PAGE_H - 100, PAGE_W, PAGE_H - 108)

    draw_wordmark(c, 39, top_y(28))
    c.setFillColor(MUTED)
    c.setFont(BOLD_FONT, 5.7)
    c.drawRightString(PAGE_W - 39, top_y(43), "REVIT FOR STRUCTURES  /  COURSE OUTLINE")

    c.setFillColor(accent)
    c.setFont(BOLD_FONT, 6.2)
    c.drawString(39, top_y(80), eyebrow)
    c.setFillColor(INK)
    c.setFont(DISPLAY_FONT, 24.5)
    c.drawString(37, top_y(114), title)
    c.setFillColor(MUTED)
    c.setFont(MEDIUM_FONT, 7.2)
    c.drawString(39, top_y(137), subtitle)

    range_w = 89
    draw_pill(
        c,
        PAGE_W - 39 - range_w,
        top_y(128),
        range_w,
        module_range,
        fill=tint,
        text_color=accent,
        height=24,
    )
    c.setFillColor(accent)
    c.roundRect(39, top_y(151), 32, 3, 1.5, stroke=0, fill=1)

    # A fixed frame top makes every continuation page begin on the same baseline.
    c.setStrokeColor(HexColor("#E5E3DD"))
    c.setLineWidth(0.45)
    c.line(PAGE_W / 2, 49, PAGE_W / 2, top_y(158))
    draw_footer(c, doc.page, accent=accent)
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
    return module_story(
        modules[start - 1 : stop],
        accent=accent,
        tint=tint,
        start_number=start,
    )


def build_pdf(output: Path = OUTPUT) -> None:
    document = PremiumDocTemplate(output)
    story: list[Flowable] = [
        # A calm cover and a dedicated overview keep the curriculum pages airy.
        NextPageTemplate("overview"),
        PageBreak(),
        NextPageTemplate("concrete-a"),
        PageBreak(),
        # Concrete — page 1, balanced from the same top baseline.
        *module_slice(CONCRETE_MODULES, 1, 6, accent=LAVENDER, tint=LILAC),
        FrameBreak(),
        *module_slice(CONCRETE_MODULES, 7, 11, accent=LAVENDER, tint=LILAC),
        NextPageTemplate("concrete-b"),
        PageBreak(),
        # Concrete — page 2.
        *module_slice(CONCRETE_MODULES, 12, 15, accent=LAVENDER, tint=LILAC),
        FrameBreak(),
        *module_slice(CONCRETE_MODULES, 16, 20, accent=LAVENDER, tint=LILAC),
        NextPageTemplate("steel-a"),
        PageBreak(),
        # Steel — page 1.
        *module_slice(STEEL_MODULES, 1, 5, accent=TERRACOTTA, tint=PEACH),
        FrameBreak(),
        *module_slice(STEEL_MODULES, 6, 10, accent=TERRACOTTA, tint=PEACH),
        NextPageTemplate("steel-b"),
        PageBreak(),
        # Steel — page 2.
        *module_slice(STEEL_MODULES, 11, 16, accent=TERRACOTTA, tint=PEACH),
        FrameBreak(),
        *module_slice(STEEL_MODULES, 17, 21, accent=TERRACOTTA, tint=PEACH),
        NextPageTemplate("steel-c"),
        PageBreak(),
        # Steel — page 3.
        *module_slice(STEEL_MODULES, 22, 24, accent=TERRACOTTA, tint=PEACH),
        FrameBreak(),
        *module_slice(STEEL_MODULES, 25, 29, accent=TERRACOTTA, tint=PEACH),
    ]
    document.build(story)


if __name__ == "__main__":
    build_pdf()
    print(f"Created {OUTPUT.relative_to(ROOT)}")
