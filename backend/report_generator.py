from io import BytesIO
from datetime import datetime

from html import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
)


def generate_medical_report(patient, diabetes_result=None):

    """
    Generate a downloadable PDF medical report.

    patient: Dictionary containing patient information.
    diabetes_result: Optional diabetes prediction dictionary.
    """

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=20,
        textColor=colors.HexColor("#087E8B"),
        alignment=TA_CENTER,
        spaceAfter=10
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#087E8B"),
        spaceBefore=15,
        spaceAfter=8
    )

    normal_style = styles["BodyText"]

    story = []

    # Report title
    story.append(
        Paragraph(
            "AI HEALTH PREDICTION APPLICATION",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Patient Medical Health Report",
            ParagraphStyle(
                "Subtitle",
                parent=normal_style,
                alignment=TA_CENTER,
                fontSize=11
            )
        )
    )

    story.append(Spacer(1, 15))

    # Report date
    report_date = datetime.now().strftime(
        "%d-%m-%Y %I:%M %p"
    )

    story.append(
        Paragraph(
            f"<b>Report Generated:</b> {report_date}",
            normal_style
        )
    )

    story.append(HRFlowable(
        width="100%",
        thickness=1,
        color=colors.HexColor("#087E8B")
    ))

    # Patient information
    story.append(
        Paragraph("1. Patient Information", heading_style)
    )

    patient_details = [
        ["Full Name", str(patient.get("full_name") or "N/A")],
        ["Date of Birth", str(patient.get("date_of_birth") or "N/A")],
        ["Email Address", str(patient.get("email") or "N/A")]
    ]

    patient_table = Table(
        [
            [Paragraph(f"<b>{escape(k)}</b>", normal_style),
             Paragraph(escape(v), normal_style)]
            for k, v in patient_details
        ],
        colWidths=[150, 330]
    )

    patient_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1),
         colors.HexColor("#E8F4F5")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))

    story.append(patient_table)

    # Laboratory results
    story.append(
        Paragraph("2. Laboratory Results", heading_style)
    )

    lab_results = [
        ["Parameter", "Recorded Value"],
        ["Glucose", f'{patient.get("glucose", "N/A")} mg/dL'],
        ["Haemoglobin", f'{patient.get("haemoglobin", "N/A")}'],
        ["Cholesterol", f'{patient.get("cholesterol", "N/A")}']
    ]

    lab_table = Table(
        lab_results,
        colWidths=[240, 240]
    )

    lab_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0),
         colors.HexColor("#087E8B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))

    story.append(lab_table)

    # AI remarks
    story.append(
        Paragraph("3. AI-Generated Health Remarks", heading_style)
    )

    remarks = patient.get("remarks") or "No AI remarks available."

    story.append(
        Paragraph(
            escape(str(remarks)).replace("\n", "<br/>"),
            normal_style
        )
    )

    # Optional diabetes prediction
    if diabetes_result:

        story.append(
            Paragraph("4. Diabetes Prediction Results", heading_style)
        )

        prediction_details = [
            ["Prediction Category",
             str(diabetes_result.get("risk_category", "N/A"))],

            ["Model Probability",
             f'{diabetes_result.get("risk_probability", "N/A")}%']
        ]

        prediction_table = Table(
            prediction_details,
            colWidths=[200, 280]
        )

        prediction_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1),
             colors.HexColor("#E8F4F5")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 9)
        ]))

        story.append(prediction_table)

        story.append(Spacer(1, 8))

        story.append(
            Paragraph(
                "This is an educational machine-learning estimate, "
                "not a calibrated personal risk assessment or "
                "medical diagnosis.",
                normal_style
            )
        )

    # Medical disclaimer
    story.append(
        Paragraph("Medical Disclaimer", heading_style)
    )

    disclaimer = (
        "This report is intended for informational and educational "
        "purposes only. AI-generated remarks and machine-learning "
        "predictions are not substitutes for professional medical "
        "advice, diagnosis, or treatment. Please consult a qualified "
        "healthcare professional for medical interpretation."
    )

    story.append(
        Paragraph(disclaimer, normal_style)
    )

    # Generate PDF
    document.build(story)

    buffer.seek(0)

    return buffer