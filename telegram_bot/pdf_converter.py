import os
import logging
from docx2pdf import convert

logger = logging.getLogger(__name__)


class PDFConverter:
    """
    A utility class to handle conversion of DOCX files to PDF format.
    """

    def convert_to_pdf(self, docx_path: str) -> str:
        """
        Convert a DOCX file to PDF using the same filename.

        Args:
            docx_path (str): Full path to the .docx file.

        Returns:
            str: Path to the generated PDF file.
        """
        pdf_path = docx_path.replace(".docx", ".pdf")
        convert(docx_path, pdf_path)
        return pdf_path

    def get_latest_docx(self, user_folder: str) -> str | None:
        """
        Get the most recently modified DOCX file from a user's folder.

        Args:
            user_folder (str): Path to the user's directory.

        Returns:
            str | None: Filename of the latest .docx file or None if no files found.
        """
        docx_files = [f for f in os.listdir(user_folder) if f.endswith(".docx")]
        if not docx_files:
            return None
        return max(
            docx_files,
            key=lambda f: os.path.getmtime(os.path.join(user_folder, f))
        )
