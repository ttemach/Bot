from docx2pdf import convert
from aiogram.types import FSInputFile
import os
import logging

logger = logging.getLogger(__name__)

class PDFConverter:
    def convert_to_pdf(self, docx_path: str) -> str:
        pdf_path = docx_path.replace(".docx", ".pdf")
        convert(docx_path, pdf_path)
        return pdf_path

    def get_latest_docx(self, user_folder: str) -> str:
        docx_files = [f for f in os.listdir(user_folder) if f.endswith(".docx")]
        if not docx_files:
            return None
        return max(docx_files, key=lambda f: os.path.getmtime(os.path.join(user_folder, f)))

