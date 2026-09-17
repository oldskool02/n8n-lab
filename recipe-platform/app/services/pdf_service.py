from io import BytesIO

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
)
from reportlab.lib.styles import getSampleStyleSheet

FALLBACK_IMAGE = Path(__file__).resolve().parent.parent / "assets" / "recipe-fallback.png"


def create_recipe_pdf(recipe, image_bytes=None):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
    )

    styles = getSampleStyleSheet()

    if image_bytes:
        image = Image(
            BytesIO(image_bytes),
            width=400,
            height=267,
        )
    else:
        image = Image(
            str(FALLBACK_IMAGE),
            width=400,
            height=267,
        )

    ingredients = [
        Paragraph(
            f"{item.quantity} {item.unit} {item.ingredient}",
            styles["Normal"],
        )
        for item in recipe.ingredients
    ]

    steps = [
        Paragraph(
            f"Step {item.step_number}. {item.instruction}",
            styles["Normal"],
        )
        for item in recipe.steps
    ]

    story = [
        image,
        Paragraph(recipe.title, styles["Title"]),
        Paragraph(f"Servings: {recipe.servings}", styles["Normal"]),
        Paragraph(f"Diet: {recipe.diet}", styles["Normal"]),
        Paragraph(f"Cuisine: {recipe.cuisine}", styles["Normal"]),
        Paragraph("Ingredients:", styles["Heading2"]),
        *ingredients,
        Paragraph("Steps:", styles["Heading2"]),
        *steps,
    ]

    document.build(story)

    return buffer.getvalue()
