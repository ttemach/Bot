import asyncio
import os
import logging
import re
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import (
    Message, BotCommand, ReplyKeyboardMarkup, KeyboardButton, FSInputFile,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)
from aiogram.filters import Command
from docx import Document
from docx2pdf import convert

# === Загрузка переменных окружения ===
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
BASE_SAVE_PATH = r"C:\Users\User\PycharmProjects\pythonProject4"  # Основная папка для хранения файлов

# === Логирование ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# === Инициализация бота и диспетчера ===
bot = Bot(token=TOKEN)
dp = Dispatcher()

# === Создание папки для сохранения файлов ===
def create_user_folder(user_id: int) -> str:
    # Создаём папку с именем пользователя (по его user_id)
    user_folder = os.path.join(BASE_SAVE_PATH, str(user_id))
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
        logger.info(f"Создана директория для пользователя {user_id}: {user_folder}")
    return user_folder

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

# === Удаление файла через X минут ===
async def schedule_file_deletion(file_path: str, delay_minutes: int = 10):
    await asyncio.sleep(delay_minutes * 60)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.info(f"Файл удалён автоматически: {file_path}")
        except Exception as e:
            logger.error(f"Ошибка при удалении файла: {e}")

# === Очистка данных пользователя ===
async def cleanup_user_data(user_id: int, delay_minutes: int = 10):
    await asyncio.sleep(delay_minutes * 60)
    if user_id in user_documents:
        del user_documents[user_id]
        logger.info(f"Данные пользователя {user_id} очищены.")

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
    user_id = message.from_user.id
    logger.info(f"Загрузка файла: {file_name} от {user_id}")

    if not file_name.lower().endswith(".docx"):
        await message.answer(
            "❌ Этот файл не удалось загрузить. Убедитесь, что он:\n"
            "- В формате .docx\n"
            "- Не превышает 50MB\n"
            "- Не повреждён"
        )
        return

    if file.file_size > 50 * 1024 * 1024:
        await message.answer("❌ Файл превышает 50 МБ.")
        return

    # Создаем папку для пользователя
    user_folder = create_user_folder(user_id)

    await message.answer("🔄 Загружаем и обрабатываем ваш файл...")

    try:
        file_path = await bot.get_file(file.file_id)
        downloaded_file = await bot.download_file(file_path.file_path)

        save_location = os.path.join(user_folder, file_name)
        with open(save_location, "wb") as f:
            f.write(downloaded_file.read())
        logger.info(f"Файл сохранён: {save_location}")

        asyncio.create_task(schedule_file_deletion(save_location, delay_minutes=1))
        asyncio.create_task(cleanup_user_data(user_id, delay_minutes=1))

        doc = Document(save_location)
    except Exception as e:
        logger.error(f"Ошибка обработки: {e}")
        await message.answer(
            "❌ Этот файл не удалось загрузить. Убедитесь, что он:\n"
            "- В формате .docx\n"
            "- Не превышает 50MB\n"
            "- Не повреждён"
        )
        return

    pages = []
    current_page = []

    def escape_markdown_v2(text: str) -> str:
        """
        Экранирует текст для MarkdownV2 согласно документации Telegram.
        """
        escape_chars = r"_*[]()~`>#+-=|{}.!\\"
        return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            formatted_text = escape_markdown_v2(text)

            # Проверяем, является ли параграф частью списка
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

    user_documents[user_id] = pages
    num_pages = len(pages)

    inline_page_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"Страница {i+1}", callback_data=f"page_{i}")]
            for i in range(num_pages)
        ]
    )

    await message.answer(
        f"✅ Файл загружен!\nВ нём *{num_pages}* страниц.\nВыберите страницу для просмотра:",
        reply_markup=inline_page_keyboard,
        parse_mode="Markdown"
    )

# === Callback-кнопка: показать выбранную страницу ===
@dp.callback_query(F.data.startswith("page_"))
async def show_selected_page(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in user_documents:
        await callback.answer("Сначала загрузите файл!", show_alert=True)
        return

    page_num = int(callback.data.split("_")[1])
    pages = user_documents[user_id]

    if page_num < 0 or page_num >= len(pages):
        await callback.answer("Такой страницы не существует!", show_alert=True)
    else:
        await callback.message.answer(
            f"📄 *Страница {page_num + 1}:*\n{pages[page_num]}", parse_mode="MarkdownV2"
        )
        await callback.answer()

# === Конвертация DOCX в PDF и отправка ===
@dp.message(lambda message: message.text == "📄 Конвертировать в PDF")
async def convert_to_pdf(message: Message):
    user_id = message.from_user.id
    if user_id not in user_documents:
        await message.answer("❌ Сначала загрузите DOCX-файл!")
        return

    await message.answer("🔄 Конвертируем файл в PDF...")

    # Создаем папку для пользователя
    user_folder = create_user_folder(user_id)

    docx_files = [f for f in os.listdir(user_folder) if f.endswith(".docx")]
    if not docx_files:
        await message.answer("❌ Файл не найден.")
        return

    latest_file = max(docx_files, key=lambda f: os.path.getctime(os.path.join(user_folder, f)))
    docx_path = os.path.join(user_folder, latest_file)
    pdf_path = docx_path.replace(".docx", ".pdf")

    try:
        convert(docx_path, pdf_path)
        logger.info(f"Успешная конвертация: {pdf_path}")

        pdf_to_send = FSInputFile(pdf_path)
        await bot.send_document(
            chat_id=message.chat.id,
            document=pdf_to_send,
            caption=f"✅ Обработка завершена! Вот ваш PDF: {os.path.basename(pdf_path)}"
        )

        asyncio.create_task(schedule_file_deletion(pdf_path, delay_minutes=1))

    except Exception as e:
        logger.error(f"Ошибка при конвертации: {e}")
        await message.answer(
            "❌ Не удалось конвертировать файл.\n"
            "Проверьте, что он не повреждён и попробуйте снова."
        )

# === Обработка неизвестных текстовых сообщений (не команды и не документы) ===
@dp.message()
async def handle_unknown_text(message: Message):
    if message.text and not message.text.startswith("/") and not message.document:
        logger.info(f"Неизвестное сообщение от {message.from_user.id}: {message.text}")
        await message.answer("❗ Пожалуйста, выберите действие из меню.")

# === Запуск бота ===
async def main():
    logger.info("Бот запускается...")
    await set_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
