import os
import asyncio
import logging

logger = logging.getLogger(__name__)

class FileManager:
    def __init__(self, base_path: str):
        self.base_path = base_path

    def create_user_folder(self, user_id: int) -> str:
        user_folder = os.path.join(self.base_path, str(user_id))
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
            logger.info(f"Создана директория для пользователя {user_id}: {user_folder}")
        return user_folder

    async def delete_file_later(self, file_path: str, delay_minutes: int = 10):
        await asyncio.sleep(delay_minutes * 60)
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Файл удалён: {file_path}")
