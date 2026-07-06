from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

FEDERAL_BLUE = colors.HexColor("#0B3D62")
LIGHT_BLUE = colors.HexColor("#EAF1F8")

_styles = getSampleStyleSheet()
_title_style = ParagraphStyle(
    "DocTitle", parent=_styles["Title"], textColor=FEDERAL_BLUE, spaceAfter=4
)
_subtitle_style = ParagraphStyle(
    "DocSubtitle", parent=_styles["Normal"], textColor=colors.grey, spaceAfter=16
)
_heading_style = ParagraphStyle(
    "SectionHeading", parent=_styles["Heading2"], textColor=FEDERAL_BLUE, spaceBefore=14, spaceAfter=6
)
_body_style = ParagraphStyle("Body", parent=_styles["BodyText"], spaceAfter=8, leading=15)


def build_pdf(
    file_path: str,
    title: str,
    subtitle: str,
    sections: list[tuple[str, str]],
    tables: list[tuple[str, list[list[str]]]] | None = None,
) -> str:
    """Builds a DOT-style report PDF.

    sections: list of (heading, body_text) rendered as paragraphs.
    tables: optional list of (heading, rows) where rows[0] is the header row.
    """
    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title=title,
    )
    story = [
        Paragraph("ROADWAY AI INSPECTOR &amp; DESIGN ASSISTANT", _subtitle_style),
        Paragraph(title, _title_style),
        Paragraph(subtitle, _subtitle_style),
        Spacer(1, 8),
    ]

    for heading, body in sections:
        story.append(Paragraph(heading, _heading_style))
        for line in body.split("\n"):
            if line.strip():
                story.append(Paragraph(line.replace("&", "&amp;"), _body_style))

    for heading, rows in tables or []:
        story.append(Paragraph(heading, _heading_style))
        table = Table(rows, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), FEDERAL_BLUE),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BLUE]),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 10))

    doc.build(story)
    return file_path
