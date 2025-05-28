def get_help_text() -> str:
    """
    Return the help message text explaining bot functionality.

    Returns:
        str: Help message with instructions and commands.
    """
    return (
        "🆘 *Помощь*\n\n"
        "Бот принимает `.docx` файлы, разбивает их на страницы и может конвертировать в PDF.\n\n"
        "📂 *Загрузить файл* — отправьте `.docx` до 50 МБ.\n"
        "📄 *Конвертировать в PDF* — получите PDF-документ.\n"
        "⚙️ *Настройки* — в будущем появятся параметры конфигурации.\n\n"
        "Если что-то не работает — отправьте /start."
    )


def get_settings_text() -> str:
    """
    Return the settings message text describing future configuration options.

    Returns:
        str: Settings message with planned features.
    """
    return (
        "⚙️ *Настройки*\n\n"
        "Пока что настроек нет. В будущих версиях вы сможете:\n"
        "• выбирать язык вывода\n"
        "• управлять удалением файлов\n"
        "• форматировать текст при просмотре страниц\n"
        "• и многое другое..."
    )


def get_unknown_text() -> str:
    """
    Return the message text for unknown or unrecognized commands.

    Returns:
        str: Message prompting user to select an action from the menu.
    """
    return "❗ Пожалуйста, выберите действие из меню."
