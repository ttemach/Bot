from telegram_bot.pdf_converter import PDFConverter
import os


def test_get_latest_docx(tmp_path):
    file1 = tmp_path / "file1.docx"
    file2 = tmp_path / "file2.docx"
    file1.write_text("1")
    file2.write_text("2")
    os.utime(file2, (9999999999, 9999999999))  # обновим время

    converter = PDFConverter()
    latest = converter.get_latest_docx(str(tmp_path))
    assert latest == "file2.docx"
