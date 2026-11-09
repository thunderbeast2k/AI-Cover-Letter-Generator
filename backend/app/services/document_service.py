import io
import re
from datetime import datetime
from typing import Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from app.schemas.request_models import PersonalInfo, JobInfo


class DocumentService:
    """Generates production-grade PDF and DOCX files for cover letters."""

    @classmethod
    def generate_pdf(
        cls,
        cover_letter: str,
        personal_info: PersonalInfo,
        job_info: JobInfo,
        template_id: str = "classic"
    ) -> bytes:
        """Render a polished, publication-ready PDF using ReportLab."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=54,  # 0.75 inch
            rightMargin=54,
            topMargin=48,
            bottomMargin=48
        )

        styles = getSampleStyleSheet()

        # Custom typography styles
        name_style = ParagraphStyle(
            "DocName",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=16 if template_id != "minimal" else 14,
            leading=20,
            textColor=colors.HexColor("#1e293b"),
            alignment=TA_LEFT if template_id != "minimal" else TA_CENTER
        )

        contact_style = ParagraphStyle(
            "DocContact",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#64748b"),
            alignment=TA_LEFT if template_id != "minimal" else TA_CENTER
        )

        meta_style = ParagraphStyle(
            "DocMeta",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#334155")
        )

        body_style = ParagraphStyle(
            "DocBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=15,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=4,
            spaceAfter=8
        )

        story = []

        # 1. Header: Candidate Info
        story.append(Paragraph(personal_info.full_name, name_style))
        story.append(Spacer(1, 4))

        contact_parts = [p for p in [
            personal_info.email,
            personal_info.phone,
            personal_info.location,
            personal_info.linkedin_url,
            personal_info.github_url or personal_info.portfolio_url
        ] if p]
        contact_line = " &bull; ".join(contact_parts)
        story.append(Paragraph(contact_line, contact_style))
        story.append(Spacer(1, 8))

        # Divider line
        divider_color = colors.HexColor("#3b82f6" if template_id == "technical" else "#cbd5e1")
        story.append(HRFlowable(width="100%", thickness=1, color=divider_color, spaceBefore=4, spaceAfter=14))

        # 2. Date
        today_str = datetime.now().strftime("%B %d, %Y")
        story.append(Paragraph(today_str, meta_style))
        story.append(Spacer(1, 10))

        # 3. Recipient block
        recipient_lines = []
        if job_info.hiring_manager_name:
            recipient_lines.append(job_info.hiring_manager_name)
        recipient_lines.append(job_info.company_name)
        if job_info.company_location:
            recipient_lines.append(job_info.company_location)

        for r_line in recipient_lines:
            story.append(Paragraph(r_line, meta_style))
        story.append(Spacer(1, 12))

        # 4. Body content
        # Clean up any potential markdown headers or bold asterisks
        cleaned_text = cover_letter.replace("**", "").replace("__", "")
        paragraphs = [p.strip() for p in cleaned_text.split("\n\n") if p.strip()]

        # Filter out redundant header if the generated letter repeats Date or Recipient block
        for p in paragraphs:
            # Escape HTML characters for ReportLab Paragraph
            safe_text = p.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            # Convert single newlines within a paragraph into <br/>
            safe_text = safe_text.replace("\n", "<br/>")
            story.append(Paragraph(safe_text, body_style))

        # Build document
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    @classmethod
    def generate_docx(
        cls,
        cover_letter: str,
        personal_info: PersonalInfo,
        job_info: JobInfo,
        template_id: str = "classic"
    ) -> bytes:
        """Render an editable, elegantly formatted DOCX using python-docx."""
        doc = docx.Document()

        # Set 1-inch margins
        for section in doc.sections:
            section.top_margin = Inches(0.8)
            section.bottom_margin = Inches(0.8)
            section.left_margin = Inches(0.8)
            section.right_margin = Inches(0.8)

        # Candidate Name
        name_p = doc.add_paragraph()
        if template_id == "minimal":
            name_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        name_run = name_p.add_run(personal_info.full_name)
        name_run.font.name = "Calibri"
        name_run.font.size = Pt(16)
        name_run.font.bold = True
        name_run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
        name_p.paragraph_format.space_after = Pt(2)

        # Contact Info
        contact_p = doc.add_paragraph()
        if template_id == "minimal":
            contact_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        contact_parts = [p for p in [
            personal_info.email,
            personal_info.phone,
            personal_info.location,
            personal_info.linkedin_url,
            personal_info.github_url or personal_info.portfolio_url
        ] if p]
        contact_run = contact_p.add_run(" | ".join(contact_parts))
        contact_run.font.name = "Calibri"
        contact_run.font.size = Pt(9.5)
        contact_run.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
        contact_p.paragraph_format.space_after = Pt(14)

        # Date
        date_p = doc.add_paragraph()
        date_run = date_p.add_run(datetime.now().strftime("%B %d, %Y"))
        date_run.font.name = "Calibri"
        date_run.font.size = Pt(10)
        date_p.paragraph_format.space_after = Pt(8)

        # Recipient
        if job_info.hiring_manager_name:
            rec_mgr = doc.add_paragraph()
            rec_mgr.add_run(job_info.hiring_manager_name).font.name = "Calibri"
            rec_mgr.paragraph_format.space_after = Pt(1)

        rec_comp = doc.add_paragraph()
        rec_comp.add_run(job_info.company_name).font.name = "Calibri"
        rec_comp.paragraph_format.space_after = Pt(1)

        if job_info.company_location:
            rec_loc = doc.add_paragraph()
            rec_loc.add_run(job_info.company_location).font.name = "Calibri"
            rec_loc.paragraph_format.space_after = Pt(12)
        else:
            rec_comp.paragraph_format.space_after = Pt(12)

        # Body paragraphs
        cleaned_text = cover_letter.replace("**", "").replace("__", "")
        paragraphs = [p.strip() for p in cleaned_text.split("\n\n") if p.strip()]

        for p_text in paragraphs:
            p = doc.add_paragraph()
            run = p.add_run(p_text)
            run.font.name = "Calibri"
            run.font.size = Pt(10.5)
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(8)

        buffer = io.BytesIO()
        doc.save(buffer)
        docx_bytes = buffer.getvalue()
        buffer.close()
        return docx_bytes
