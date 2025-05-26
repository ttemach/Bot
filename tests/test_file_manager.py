from telegram_bot.file_manager import FileManager
import os


def test_create_user_folder(tmp_path):
    fm = FileManager(str(tmp_path))
    folder = fm.create_user_folder(42)
    assert os.path.exists(folder)
    assert os.path.isdir(folder)
