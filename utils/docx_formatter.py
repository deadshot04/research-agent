from pathlib import Path
import aspose.words as aw
from aspose.words.saving import OoxmlSaveOptions, OoxmlCompliance
import logging
import re
from utils.docx_formatter import populate_template

logger = logging.getLogger(__name__)

def format_report_docx(report_data, output_file):
    """Generate a DOCX report using the EY template."""
    try:
        template_path = Path("EY_report_template.docx")
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        doc = aw.Document(str(template_path))

        # Load and insert content into placeholders
        replacements = {
            "Title": report_data.get("title", "Default Title"),
            "Subtitle": report_data.get("subtitle", "Default Subtitle"),
            "ExecutiveSummary": report_data.get("executive_summary", "Default Executive Summary"),
            "ChapterContent": report_data.get("chapter_content", "Default Chapter Content"),
            "AuthorName": report_data.get("author_name", "Default Author Name"),
        }

        # Find and replace placeholders using regular expressions to handle field values correctly
        for placeholder, value in replacements.items():
            for field in doc.range.fields:
                if field.field_code.text.strip() == f'MERGEFIELD  "{placeholder}"':
                    field.unlink()  # Remove the field
                    builder = aw.DocumentBuilder(doc)
                    builder.move_to(field.start)
                    builder.insert_text(str(value))

        save_options = OoxmlSaveOptions(aw.SaveFormat.DOCX)
        save_options.compliance = OoxmlCompliance.ISO29500_2008_TRANSITIONAL

        doc.save(str(output_file), save_options)

    except Exception as e:
        logger.error(f"DOCX conversion failed: {str(e)}")