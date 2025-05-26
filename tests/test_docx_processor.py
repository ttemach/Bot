import os
from telegram_bot.docx_processor import DocxProcessor


def test_process_docx_creates_pages(tmp_path):
    docx_path = tmp_path / "test.docx"

    from docx import Document
    doc = Document()
    for i in range(35):
        doc.add_paragraph(f"Тест параграф {i + 1}")
    doc.save(docx_path)

    processor = DocxProcessor()
    pages = processor.process_docx(str(docx_path), user_id=123)

    assert isinstance(pages, list)
    assert len(pages) >= 2
