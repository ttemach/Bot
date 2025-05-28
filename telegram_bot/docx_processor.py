import re
from docx import Document
from typing import List, Dict


class DocxProcessor:
    """
    A utility class to process .docx files and split their content into pages
    based on a line limit. Also handles Markdown escaping for Telegram formatting.
    """

    def __init__(self, lines_per_page: int) -> None:
        """
        Initialize the DocxProcessor.

        Args:
            lines_per_page (int): Number of lines per page when splitting the document.
        """
        self.lines_per_page = lines_per_page
        self.user_documents: Dict[int, List[str]] = {}

    def escape_markdown(self, text: str) -> str:
        """
        Escape special characters for Telegram MarkdownV2.

        Args:
            text (str): Raw text to be escaped.

        Returns:
            str: Escaped text.
        """
        escape_chars = r"_*[]()~`>#+-=|{}.!\\"
        return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

    def process_docx(self, file_path: str, user_id: int) -> List[str]:
        """
        Process a .docx file, split its content into pages, and apply Telegram Markdown formatting.

        Args:
            file_path (str): Path to the .docx file.
            user_id (int): Unique identifier for the user uploading the file.

        Returns:
            List[str]: List of page contents, each as a string.
        """
        doc = Document(file_path)
        pages: List[str] = []
        current_page: List[str] = []

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            formatted = self.escape_markdown(text)

            if para.style.name.startswith("List"):
                formatted = f"• {formatted}"

            if para.runs:
                run = para.runs[0]
                if run.bold:
                    formatted = f"*{formatted}*"
                if run.italic:
                    formatted = f"_{formatted}_"
                if run.underline:
                    formatted = f"__{formatted}__"

            current_page.append(formatted)

            if len(current_page) >= self.lines_per_page:
                pages.append("\n".join(current_page))
                current_page = []

        if current_page:
            pages.append("\n".join(current_page))

        self.user_documents[user_id] = pages
        return pages
