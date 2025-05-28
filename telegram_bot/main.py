import os
import logging
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import (
    Message, CallbackQuery, BotCommand, MenuButtonCommands, FSInputFile
)
from aiogram.filters import Command

from file_manager import FileManager
from docx_processor import DocxProcessor
from pdf_converter import PDFConverter
from bot_ui.bot_ui_ui_factory import BotUI
from config_loader import Config


# === Load configuration and environment ===
load_dotenv()
config = Config()

# === Logging configuration ===
logging.basicConfig(
    level=config.logging_level,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# === Initialize bot and dispatcher ===
bot = Bot(token=config.bot_token)
dp = Dispatcher()

# === Create instances of service classes ===
file_manager = FileManager(config.base_save_path)
docx_processor = DocxProcessor(config.docx_lines_per_page)
pdf_converter = PDFConverter()
bot_ui = BotUI()


async def set_bot_commands(bot: Bot) -> None:
    """
    Set default bot commands for the command menu.
    """
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="upload", description="Загрузить файл"),
        BotCommand(command="convert", description="Конвертировать в PDF"),
    ]
    await bot.set_my_commands(commands)


@dp.message(Command("start"))
async def start_handler(message: Message) -> None:
    """
    Handle /start command. Send greeting and show main menu.
    """
    logger.info(f"User {message.from_user.id} started the bot.")
    await message.answer("Привет! Выберите действие из меню.", reply_markup=bot_ui.menu_keyboard)


@dp.message(lambda message: message.text == "📂 Загрузить файл")
async def upload_file_info(message: Message) -> None:
    """
    Inform user to upload a .docx file when pressing upload button.
    """
    logger.info(f"User {message.from_user.id} requested to upload a file.")
    await message.answer("Отправьте файл формата .docx (не более 50 МБ).")


@dp.message(lambda message: message.document)
async def handle_files(message: Message) -> None:
    """
    Handle uploaded .docx files, process and split into pages.
    """
    file = message.document
    user_id = message.from_user.id
    file_name = file.file_name

    logger.info(f"Received file: {file_name} from user {user_id}")

    if not file_name.lower().endswith(".docx"):
        await message.answer("❌ Это не .docx файл.")
        return

    if file.file_size > config.max_file_size_bytes:
        await message.answer("❌ Файл слишком большой. Максимум 50 МБ.")
        return

    user_folder = file_manager.create_user_folder(user_id)
    file_path = os.path.join(user_folder, file_name)

    await message.answer("🔄 Загружаем файл...")

    try:
        file_info = await bot.get_file(file.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)

        with open(file_path, "wb") as f:
            f.write(downloaded_file.getvalue())

        pages = docx_processor.process_docx(file_path, user_id)
        num_pages = len(pages)

        keyboard = bot_ui.create_page_keyboard(num_pages)
        await message.answer(
            f"✅ Файл загружен! {num_pages} страниц. Выберите страницу для просмотра.",
            reply_markup=keyboard
        )

    except Exception as e:
        logger.error(f"Error processing file: {e}")
        await message.answer("❌ Ошибка при загрузке файла.")


@dp.callback_query(lambda c: c.data.startswith("page_"))
async def show_page(callback: CallbackQuery) -> None:
    """
    Display the selected page from the uploaded .docx file.
    """
    user_id = callback.from_user.id
    page_num = int(callback.data.split("_")[1])

    if user_id not in docx_processor.user_documents:
        await callback.answer("Сначала загрузите файл.", show_alert=True)
        return

    pages = docx_processor.user_documents[user_id]

    if 0 <= page_num < len(pages):
        await callback.message.answer(f"📄 Страница {page_num + 1}:\n{pages[page_num]}")
        await callback.answer()


@dp.message(lambda message: message.text == "📄 Конвертировать в PDF")
async def convert_to_pdf(message: Message) -> None:
    """
    Convert the latest uploaded .docx file to PDF and send it.
    """
    user_id = message.from_user.id

    if user_id not in docx_processor.user_documents:
        await message.answer("❌ Сначала загрузите DOCX файл!")
        return

    user_folder = file_manager.create_user_folder(user_id)
    docx_file = pdf_converter.get_latest_docx(user_folder)

    if not docx_file:
        await message.answer("❌ DOCX файл не найден.")
        return

    docx_path = os.path.join(user_folder, docx_file)
    pdf_path = pdf_converter.convert_to_pdf(docx_path)

    try:
        pdf_file = FSInputFile(pdf_path)
        await bot.send_document(message.chat.id, pdf_file, caption="Вот ваш PDF!")
    except Exception as e:
        logger.error(f"PDF conversion error: {e}")
        await message.answer("❌ Не удалось конвертировать файл в PDF.")


@dp.message(lambda message: message.text == "ℹ️ Помощь")
async def help_handler(message: Message) -> None:
    """
    Show help information to the user.
    """
    await message.answer(bot_ui.messages.get_help_text(), parse_mode="Markdown")


@dp.message(lambda message: message.text == "⚙️ Настройки")
async def settings_handler(message: Message) -> None:
    """
    Show settings placeholder message.
    """
    await message.answer(bot_ui.messages.get_settings_text(), parse_mode="Markdown")


@dp.message()
async def handle_unknown_text(message: Message, menu_keyboard=None) -> None:
    """
    Handle unknown text messages that do not match any command or button.
    """
    if message.text and not message.text.startswith("/") and not message.document:
        logger.info(f"Unknown message from user {message.from_user.id}: {message.text}")
        await message.answer(bot_ui.messages.get_unknown_text(), reply_markup=bot_ui.menu_keyboard)


async def main() -> None:
    """
    Main entry point: configure and start the bot.
    """
    await set_bot_commands(bot)
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands(type="commands"))
    logger.info("Bot is starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
