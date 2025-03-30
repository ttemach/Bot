import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, BotCommand, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from docx import Document

TOKEN = "7966099738:AAFApqIteo2qjORnHOUO5t-VZP9jDKMkfVM"

bot = Bot(token=TOKEN)
dp = Dispatcher()

SAVE_PATH = r"C:\Users\User\PycharmProjects\pythonProject4"
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

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

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Привет! Выберите команду из меню.", reply_markup=menu_keyboard)

@dp.message(lambda message: message.text == "📂 Загрузить файл")
async def upload_file_info(message: Message):
    await message.answer("Максимальный размер файла для загрузки: 50 МБ. Пожалуйста, отправьте ваш файл.")

@dp.message(lambda message: message.document)
async def handle_files(message: Message):
    file = message.document
    file_name = file.file_name

    # Проверяем разрешенные форматы
    allowed_extensions = {"jpg", "png", "mp4", "mp3", "docx"}
    if file_name.split(".")[-1].lower() not in allowed_extensions:
        await message.answer("❌ Формат файла не поддерживается! Разрешены: JPG, PNG, MP4, MP3, DOCX.")
        return

    if file.file_size > 50 * 1024 * 1024:
        await message.answer("Файл слишком большой! Лимит 50 МБ.")
        return

    file_path = await bot.get_file(file.file_id)
    downloaded_file = await bot.download_file(file_path.file_path)

    save_location = os.path.join(SAVE_PATH, file_name)
    with open(save_location, "wb") as f:
        f.write(downloaded_file.read())

    await message.answer("✅ Файл успешно загружен и сохранен!")

    # Если файл .docx, читаем и отправляем первые несколько строк
    if file_name.lower().endswith(".docx"):
        doc = Document(save_location)
        text_lines = [para.text for para in doc.paragraphs if para.text.strip()][:5]  # Берем первые 5 непустых строк
        text_preview = "\n".join(text_lines) if text_lines else "Документ пуст."
        await message.answer(f"📖 Первые строки из документа:\n{text_preview}")

@dp.message()
async def block_text_messages(message: Message):
    await message.delete()

async def main():
    await set_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
