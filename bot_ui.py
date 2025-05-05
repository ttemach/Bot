from aiogram import types
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

class BotUI:
    def __init__(self):
        self.menu_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📂 Загрузить файл")],
                [KeyboardButton(text="📄 Конвертировать в PDF")]
            ],
            resize_keyboard=True
        )

    def create_page_keyboard(self, num_pages: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"Страница {i+1}", callback_data=f"page_{i}")]
                for i in range(num_pages)
            ]
        )
