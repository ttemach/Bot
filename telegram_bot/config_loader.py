import os
import yaml
from dotenv import load_dotenv

class Config:
    def __init__(self, path: str = "config.yaml"):
        # Загрузка .env-файла
        load_dotenv()

        # Загрузка YAML конфигурации
        with open(path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        # Блок BOT
        self.bot_token = os.getenv("BOT_TOKEN") or config_data["bot"]["token"]
        self.base_save_path = config_data["bot"]["base_save_path"]

        # Блок LIMITS
        self.max_file_size_mb = config_data["limits"]["max_file_size_mb"]
        self.max_file_size_bytes = self.max_file_size_mb * 1024 * 1024
        self.docx_lines_per_page = config_data["limits"]["docx_lines_per_page"]

        # Блок LOGGING
        self.logging_level = config_data["logging"]["level"].upper()
