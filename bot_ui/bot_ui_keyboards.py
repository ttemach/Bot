from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Create the main menu reply keyboard markup.

    Returns:
        ReplyKeyboardMarkup: Keyboard with main menu buttons.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📂 Загрузить файл"),
                KeyboardButton(text="ℹ️ Помощь")
            ],
            [
                KeyboardButton(text="📄 Конвертировать в PDF"),
                KeyboardButton(text="⚙️ Настройки")
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )


def create_page_keyboard(num_pages: int) -> InlineKeyboardMarkup:
    """
    Create an inline keyboard with buttons for each page.

    Args:
        num_pages (int): Number of pages to create buttons for.

    Returns:
        InlineKeyboardMarkup: Inline keyboard with page buttons.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"Страница {i + 1}", callback_data=f"page_{i}")]
            for i in range(num_pages)
        ]
    )
