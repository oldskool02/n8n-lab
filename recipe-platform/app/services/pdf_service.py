from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

FALLBACK_IMAGE = (
    Path(__file__).parent.parent / "assets" / "recipe-fallback.png"
)


def create_recipe_pdf(recipe, image_bytes=None):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=recipe.title,
        author=recipe.user.email,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "RecipeTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        alignment=TA_CENTER,
        spaceAfter=10,
    )

    metadata_style = ParagraphStyle(
        "Metadata",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=12,
        alignment=TA_CENTER,
        spaceAfter=10,
    )

    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        spaceBefore=14,
        spaceAfter=7,
        keepWithNext=1,
    )

    ingredient_style = ParagraphStyle(
        "Ingredient",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
    )

    step_number_style = ParagraphStyle(
        "StepNumber",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=15,
    )

    step_text_style = ParagraphStyle(
        "StepText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
    )

    # Use the supplied image, or fallback image
    if image_bytes:
        image_source = BytesIO(image_bytes)
    else:
        image_source = FALLBACK_IMAGE

    image_reader = ImageReader(image_source)
    image_width, image_height = image_reader.getSize()

    # Fit the image inside a sensible area while preserving aspect ratio
    max_image_width = 165 * mm
    max_image_height = 92 * mm

    scale = min(
        max_image_width / image_width,
        max_image_height / image_height,
        1,
    )

    display_width = image_width * scale
    display_height = image_height * scale

    image = Image(
        image_source,
        width=display_width,
        height=display_height,
    )

    image.hAlign = "CENTER"

    title = Paragraph(
        escape(recipe.title),
        title_style
    )

    metadata = Table(
        [
            [
                Paragraph(
                    f"<b>Servings:</b><br/>{escape(str(recipe.servings))}",
                    metadata_style,
                ),
                Paragraph(
                    f"<b>Diet:</b><br/>{escape(str(recipe.diet or 'None'))}",
                    metadata_style,
                ),
                Paragraph(
                    f"<b>Cuisine:</b><br/>{escape(str(recipe.cuisine or 'None'))}",
                    metadata_style,
                ),
            ]
        ],
        colWidths=[55 * mm, 55 * mm, 55 * mm],
    )

    metadata.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("LINEABOVE", (0, 0), (-1, -1), 0.5, colors.HexColor("#BBBBBB")),
                ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#BBBBBB")),
            ]
        )
    )

    ingredients = []

    for item in recipe.ingredients:
        quantity = escape(str(item.quantity))
        unit = escape(str(item.unit))
        ingredient = escape(str(item.ingredient))

        ingredients.append(
            Paragraph(
                f"{quantity} {unit} {ingredient}",
                ingredient_style,
            )
        )

    steps = []

    for item in recipe.steps:
        number = escape(str(item.step_number))
        instruction = escape(str(item.instruction))

        step = Table(
            [
                [
                    Paragraph(f"{number}.", step_number_style),
                    Paragraph(instruction, step_text_style),
                ]
            ],
            colWidths=[10 * mm, 145 * mm],
            hAlign="LEFT",
        )

        step.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )

        steps.append(step)

    story = [
        Spacer(1, 4 * mm),
        image,
        Spacer(1, 6 * mm),
        title,
        Spacer(1, 2 * mm),
        metadata,
        Spacer(1, 4 * mm),
        HRFlowable(
            width="100%",
            thickness=0.8,
            color=colors.HexColor("#BBBBBB"),
            spaceBefore=2,
            spaceAfter=4,
        ),
        Paragraph("Ingredients", section_style),
        *ingredients,
        Paragraph("Method", section_style),
        *steps,
    ]

    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.HexColor("#777777"))
        canvas.drawCentredString(
            A4[0] / 2,
            9 * mm,
            f"Recipe Generator  •   Page {doc.page}",
        )
        canvas.restoreState()

    document.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )

    return buffer.getvalue()
