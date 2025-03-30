import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, BotCommand, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from docx import Document

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

    # Проверяем, что файл имеет расширение .docx
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

    await message.answer("✅ Файл успешно загружен и сохранен!")

    # Читаем и отправляем первые несколько строк
    doc = Document(save_location)
    text_lines = [para.text for para in doc.paragraphs if para.text.strip()][:5]  # Берем первые 5 непустых строк
    text_preview = "\n".join(text_lines) if text_lines else "Документ пуст."
    logger.info(f"Первые строки документа {file_name}: {text_preview}")
    await message.answer(f"📖 Первые строки из документа:\n{text_preview}")

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
