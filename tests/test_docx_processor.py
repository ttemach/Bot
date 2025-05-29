import os
from telegram_bot.docx_processor import DocxProcessor  # Правильный импорт из вашего пакета


def test_process_docx_creates_pages(tmp_path):
    # Создаем тестовый DOCX-файл
    docx_path = tmp_path / "test.docx"

    from docx import Document
    doc = Document()
    for i in range(35):  # Создаем 35 параграфов
        doc.add_paragraph(f"Тестовый параграф {i + 1}")
    doc.save(docx_path)

    # Инициализируем процессор с указанием lines_per_page
    processor = DocxProcessor(lines_per_page=30)  # Значение из constants.py

    # Обрабатываем файл
    pages = processor.process_docx(str(docx_path), user_id=123)

    # Проверяем результаты
    assert isinstance(pages, list)
    assert len(pages) == 2  # 35 строк / 30 на страницу = 2 страницы
    assert all(isinstance(page, str) for page in pages)