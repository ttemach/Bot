import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, BotCommand, ReplyKeyboardMarkup, KeyboardButton, ParseMode
from aiogram.filters import Command
from docx import Document
import re

TOKEN = "7966099738:AAFApqIteo2qjORnHOUO5t-VZP9jDKMkfVM"

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher()

SAVE_PATH = r"C:\Users\User\PycharmProjects\pythonProject4"
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)
    logger.info(f"Создана директория для сохранения файлов: {SAVE_PATH}")

menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📂 Загрузить файл")]
    ],
    resize_keyboard=True
)

# Словарь для хранения содержимого документов
user_documents = {}

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запуск бота"),
    ]
    await bot.set_my_commands(commands)
    logger.info("Команды бота установлены")

@dp.message(Command("start"))
async def start_handler(message: Message):
    logger.info(f"Пользователь {message.from_user.id} запустил бота")
    await message.answer("Привет! Выберите команду из меню.", reply_markup=menu_keyboard)

@dp.message(lambda message: message.text == "📂 Загрузить файл")
async def upload_file_info(message: Message):
    logger.info(f"Пользователь {message.from_user.id} запросил загрузку файла")
    await message.answer("Максимальный размер файла для загрузки: 50 МБ. Пожалуйста, отправьте ваш файл.")

@dp.message(lambda message: message.document)
async def handle_files(message: Message):
    file = message.document
    file_name = file.file_name
    logger.info(f"Пользователь {message.from_user.id} загружает файл: {file_name}")

    if not file_name.lower().endswith(".docx"):
        logger.warning(f"Формат файла {file_name} не поддерживается")
        await message.answer("❌ Формат файла не поддерживается! Разрешены только: DOCX.")
        return

    if file.file_size > 50 * 1024 * 1024:
        logger.warning(f"Файл {file_name} превышает лимит 50 МБ")
        await message.answer("Файл слишком большой! Лимит 50 МБ.")
        return

    file_path = await bot.get_file(file.file_id)
    downloaded_file = await bot.download_file(file_path.file_path)

    save_location = os.path.join(SAVE_PATH, file_name)
    with open(save_location, "wb") as f:
        f.write(downloaded_file.read())
    logger.info(f"Файл {file_name} успешно сохранен в {save_location}")

    doc = Document(save_location)
    pages = []
    current_page = []

    def escape_markdown(text):
        """Экранирует специальные символы MarkdownV2"""
        escape_chars = r"_*[]()~`>#+-=|{}.!"
        return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            formatted_text = escape_markdown(text)

            if para.style.name.startswith("List"):
                formatted_text = f"• {formatted_text}"

            if para.runs:
                run = para.runs[0]
                if run.bold:
                    formatted_text = f"*{formatted_text}*"
                if run.italic:
                    formatted_text = f"_{formatted_text}_"
                if run.underline:
                    formatted_text = f"__{formatted_text}__"

            current_page.append(formatted_text)

        if len(current_page) >= 30:
            pages.append("\n".join(current_page))
            current_page = []

    if current_page:
        pages.append("\n".join(current_page))

    user_documents[message.from_user.id] = pages
    num_pages = len(pages)

    page_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=str(i + 1))] for i in range(num_pages)],
        resize_keyboard=True
    )

    await message.answer(f"✅ Файл успешно загружен! В документе {num_pages} страниц. Выберите номер страницы:", reply_markup=page_keyboard)

@dp.message(lambda message: message.text.isdigit())
async def get_page(message: Message):
    user_id = message.from_user.id
    if user_id not in user_documents:
        await message.answer("❌ Вы еще не загружали файл!")
        return

    page_num = int(message.text) - 1
    pages = user_documents[user_id]

    if page_num < 0 or page_num >= len(pages):
        await message.answer("❌ Такой страницы нет в документе!")
    else:
        await message.answer(f"📄 *Страница {page_num + 1}:*\n{pages[page_num]}")

@dp.message()
async def block_text_messages(message: Message):
    logger.warning(f"Пользователь {message.from_user.id} отправил запрещенное текстовое сообщение")
    await message.delete()

async def main():
    logger.info("Бот запускается...")
    await set_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
