import re
from docx import Document

class DocxProcessor:
    def __init__(self, lines_per_page: int):
        self.lines_per_page = lines_per_page
        self.user_documents = {}

    def escape_markdown(self, text: str) -> str:
        escape_chars = r"_*[]()~`>#+-=|{}.!\\"  # Telegram MarkdownV2
        return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

    def process_docx(self, file_path: str, user_id: int):
        doc = Document(file_path)
        pages = []
        current_page = []

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
