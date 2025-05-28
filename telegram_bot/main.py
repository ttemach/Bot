import os
import logging
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, CallbackQuery, BotCommand, MenuButtonCommands, FSInputFile
from aiogram.filters import Command

from file_manager import FileManager
from docx_processor import DocxProcessor
from pdf_converter import PDFConverter
from bot_ui.bot_ui_ui_factory import BotUI
from config_loader import Config

# === Загрузка конфигурации и переменных окружения ===
load_dotenv()
config = Config()

# === Логирование ===
logging.basicConfig(level=config.logging_level, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# === Инициализация бота и диспетчера ===
bot = Bot(token=config.bot_token)
dp = Dispatcher()

# === Создание объектов классов с конфигурацией ===
file_manager = FileManager(config.base_save_path)
docx_processor = DocxProcessor(config.docx_lines_per_page)
pdf_converter = PDFConverter()
bot_ui = BotUI()

# === Установка команд бота ===
async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="upload", description="Загрузить файл"),
        BotCommand(command="convert", description="Конвертировать в PDF"),
    ]
    await bot.set_my_commands(commands)

# === Обработчик команды /start ===
@dp.message(Command("start"))
async def start_handler(message: Message):
    logger.info(f"Пользователь {message.from_user.id} запустил бота")
    await message.answer("Привет! Выберите действие из меню.", reply_markup=bot_ui.menu_keyboard)

# === Обработка кнопки "📂 Загрузить файл" ===
@dp.message(lambda message: message.text == "📂 Загрузить файл")
async def upload_file_info(message: Message):
    logger.info(f"Пользователь {message.from_user.id} запросил загрузку файла")
    await message.answer("Отправьте файл формата .docx (не более 50 МБ).")

# === Обработка загруженного файла ===
@dp.message(lambda message: message.document)
async def handle_files(message: Message):
    file = message.document
    user_id = message.from_user.id
    file_name = file.file_name

    logger.info(f"Загрузка файла: {file_name} от {user_id}")

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
        await message.answer(f"✅ Файл загружен! {num_pages} страниц. Выберите страницу для просмотра.", reply_markup=keyboard)

    except Exception as e:
        logger.error(f"Ошибка при обработке файла: {e}")
        await message.answer("❌ Ошибка при загрузке файла.")

# === Обработка кнопок страниц ===
@dp.callback_query(lambda c: c.data.startswith("page_"))
async def show_page(callback: CallbackQuery):
    user_id = callback.from_user.id
    page_num = int(callback.data.split("_")[1])

    if user_id not in docx_processor.user_documents:
        await callback.answer("Сначала загрузите файл.", show_alert=True)
        return

    pages = docx_processor.user_documents[user_id]

    if 0 <= page_num < len(pages):
        await callback.message.answer(f"📄 Страница {page_num + 1}:\n{pages[page_num]}")
        await callback.answer()

# === Конвертация в PDF ===
@dp.message(lambda message: message.text == "📄 Конвертировать в PDF")
async def convert_to_pdf(message: Message):
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
        logger.error(f"Ошибка при конвертации: {e}")
        await message.answer("❌ Не удалось конвертировать файл в PDF.")

# === Обработка "ℹ️ Помощь" ===
@dp.message(lambda message: message.text == "ℹ️ Помощь")
async def help_handler(message: Message):
    await message.answer(bot_ui.messages.get_help_text(), parse_mode="Markdown")

# === Обработка "⚙️ Настройки" ===
@dp.message(lambda message: message.text == "⚙️ Настройки")
async def settings_handler(message: Message):
    await message.answer(bot_ui.messages.get_settings_text(), parse_mode="Markdown")

# === Обработка неизвестных сообщений ===
@dp.message()
async def handle_unknown_text(message: Message, menu_keyboard=None):
    if message.text and not message.text.startswith("/") and not message.document:
        logger.info(f"Неизвестное сообщение от {message.from_user.id}: {message.text}")
        await message.answer(bot_ui.messages.get_unknown_text(), reply_markup=bot_ui.menu_keyboard)

# === Точка входа ===
async def main():
    await set_bot_commands(bot)
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands(type="commands"))
    logger.info("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
