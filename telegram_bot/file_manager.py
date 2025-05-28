import os
import asyncio
import logging

logger = logging.getLogger(__name__)


class FileManager:
    """
    A utility class for managing user file directories and delayed file deletion.
    """

    def __init__(self, base_path: str) -> None:
        """
        Initialize the FileManager.

        Args:
            base_path (str): The root path where user folders will be created.
        """
        self.base_path = base_path

    def create_user_folder(self, user_id: int) -> str:
        """
        Create a dedicated folder for the user if it doesn't exist.

        Args:
            user_id (int): The unique ID of the user.

        Returns:
            str: Path to the user's folder.
        """
        user_folder = os.path.join(self.base_path, str(user_id))
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
            logger.info(f"Created directory for user {user_id}: {user_folder}")
        return user_folder

    async def delete_file_later(self, file_path: str, delay_minutes: int = 10) -> None:
        """
        Delete the specified file after a delay (in minutes).

        Args:
            file_path (str): Full path to the file to be deleted.
            delay_minutes (int): Delay in minutes before deletion. Defaults to 10.
        """
        await asyncio.sleep(delay_minutes * 60)
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"File deleted: {file_path}")
