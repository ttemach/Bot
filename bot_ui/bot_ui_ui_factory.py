from .bot_ui_keyboards import get_main_menu_keyboard, create_page_keyboard
from . import bot_ui_messages as messages


class BotUI:
    """
    A class that encapsulates bot UI components such as keyboards and messages.
    """

    def __init__(self):
        """
        Initialize the BotUI instance with the main menu keyboard
        and access to message templates.
        """
        self.menu_keyboard = get_main_menu_keyboard()
        self.messages = messages

    def create_page_keyboard(self, num_pages: int):
        """
        Create an inline keyboard for navigating pages.

        Args:
            num_pages (int): Number of pages to create buttons for.

        Returns:
            InlineKeyboardMarkup: Inline keyboard markup with page buttons.
        """
        return create_page_keyboard(num_pages)
