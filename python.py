import asyncio
import os
import logging
import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, BotCommand, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.filters import Command
from docx import Document
from docx2pdf import convert

# === Токен и путь ===
TOKEN = "7966099738:AAFApqIteo2qjORnHOUO5t-VZP9jDKMkfVM"
SAVE_PATH = r"C:\Users\User\PycharmProjects\pythonProject4"

# === Логирование ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# === Инициализация бота и диспетчера ===
bot = Bot(token=TOKEN)
dp = Dispatcher()

# === Создание папки для сохранения файлов ===
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)
    logger.info(f"Создана директория: {SAVE_PATH}")

# === Клавиатура меню ===
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📂 Загрузить файл")],
        [KeyboardButton(text="📄 Конвертировать в PDF")]
    ],
    resize_keyboard=True
)

# === Словарь для хранения данных пользователя ===
user_documents = {}

# === Команды бота ===
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запуск бота"),
    ]
    await bot.set_my_commands(commands)
    logger.info("Команды установлены")

# === Обработчик /start ===
@dp.message(Command("start"))
async def start_handler(message: Message):
    logger.info(f"Пользователь {message.from_user.id} запустил бота")
    await message.answer("Привет! Выберите действие из меню.", reply_markup=menu_keyboard)

# === Инструкция по загрузке файла ===
@dp.message(lambda message: message.text == "📂 Загрузить файл")
async def upload_file_info(message: Message):
    logger.info(f"Пользователь {message.from_user.id} запросил загрузку файла")
    await message.answer("Отправьте файл формата .docx (не более 50 МБ).")

# === Обработка загруженного файла ===
@dp.message(lambda message: message.document)
async def handle_files(message: Message):
    file = message.document
    file_name = file.file_name
    logger.info(f"Загрузка файла: {file_name} от {message.from_user.id}")

    if not file_name.lower().endswith(".docx"):
        await message.answer("❌ Поддерживаются только файлы DOCX.")
        return

    if file.file_size > 50 * 1024 * 1024:
        await message.answer("❌ Файл превышает 50 МБ.")
        return

    file_path = await bot.get_file(file.file_id)
    downloaded_file = await bot.download_file(file_path.file_path)

    save_location = os.path.join(SAVE_PATH, file_name)
    with open(save_location, "wb") as f:
        f.write(downloaded_file.read())
    logger.info(f"Файл сохранён: {save_location}")

    # Чтение и разбиение документа на страницы
    doc = Document(save_location)
    pages = []
    current_page = []

    def escape_markdown(text):
        escape_chars = r"_*[]()~`>#+-=|{}.!\\"
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

    await message.answer(
        f"✅ Файл загружен! В нём {num_pages} страниц. Выберите номер страницы:",
        reply_markup=page_keyboard
    )

# === Конвертация DOCX в PDF и отправка ===
@dp.message(lambda message: message.text == "📄 Конвертировать в PDF")
async def convert_to_pdf(message: Message):
    user_id = message.from_user.id
    if user_id not in user_documents:
        await message.answer("❌ Сначала загрузите DOCX-файл!")
        return

    # Находим последний загруженный файл пользователя
    docx_files = [f for f in os.listdir(SAVE_PATH) if f.endswith(".docx")]
    if not docx_files:
        await message.answer("❌ Файл не найден.")
        return

    latest_file = max(docx_files, key=lambda f: os.path.getctime(os.path.join(SAVE_PATH, f)))
    docx_path = os.path.join(SAVE_PATH, latest_file)
    pdf_path = docx_path.replace(".docx", ".pdf")

    try:
        convert(docx_path, pdf_path)
        logger.info(f"Успешная конвертация: {pdf_path}")

        pdf_to_send = FSInputFile(pdf_path)
        await bot.send_document(
            chat_id=message.chat.id,
            document=pdf_to_send,
            caption=f"✅ Конвертация завершена! Вот ваш файл: {os.path.basename(pdf_path)}"
        )
    except Exception as e:
        logger.error(f"Ошибка при конвертации: {e}")
        await message.answer("❌ Не удалось конвертировать файл.")

# === Отображение выбранной страницы ===
@dp.message(lambda message: message.text.isdigit())
async def get_page(message: Message):
    user_id = message.from_user.id
    if user_id not in user_documents:
        await message.answer("❌ Сначала загрузите файл.")
        return

    page_num = int(message.text) - 1
    pages = user_documents[user_id]

    if page_num < 0 or page_num >= len(pages):
        await message.answer("❌ Такой страницы не существует.")
    else:
        await message.answer(f"📄 *Страница {page_num + 1}:*\n{pages[page_num]}", parse_mode="MarkdownV2")

# === Удаление лишнего текста ===
@dp.message()
async def block_text_messages(message: Message):
    logger.warning(f"Удалено сообщение от {message.from_user.id}")
    await message.delete()

# === Запуск бота ===
async def main():
    logger.info("Бот запускается...")
    await set_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
