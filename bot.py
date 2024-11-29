from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext
from telegram.ext import filters
from html import escape
import asyncio
import logging

# Настройка логгера
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("bot")

BOT_TOKEN = "7815708235:AAHE2vX23m07OrOwDNuybGgznTzQScKWDW0"
YOUR_CHAT_ID = "1030373986"

# Обработка команды /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Это бот для обратной связи со мной. Напиши сюда своё обращение.")

# Обработка сообщений пользователей
async def handle_user_message(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    user_name = escape(user.first_name)
    mention = f"<a href='tg://user?id={user_id}'>{user_name}</a>"

    try:
        await context.bot.send_message(
            chat_id=YOUR_CHAT_ID,
            text=f"Сообщение от {mention} (ID: {user_id}):\n\n{update.message.text}",
            parse_mode="HTML",
        )
        await update.message.reply_text("Обращение было принято.")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения админу: {e}")

# Обработка ответа админа
async def handle_admin_reply(update: Update, context: CallbackContext):
    if update.message.reply_to_message:
        original_message = update.message.reply_to_message.text
        user_id = extract_user_id(original_message)

        if user_id:
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=update.message.text,
                )
                await update.message.reply_text("Ответ отправлен!")
            except Exception as e:
                logger.error(f"Ошибка при отправке ответа пользователю: {e}")
                await update.message.reply_text("Ошибка при отправке ответа пользователю.")
        else:
            await update.message.reply_text("Ошибка: не удалось извлечь ID пользователя.")
    else:
        await update.message.reply_text("Чтобы ответить пользователю, используйте функцию ответа на сообщение бота.")

# Извлечение ID пользователя
def extract_user_id(text: str) -> int:
    try:
        start = text.index("ID: ") + 4
        end = text.find(")", start)
        return int(text[start:end])
    except (ValueError, IndexError):
        return None

# Глобальная обработка ошибок
async def error_handler(update: object, context: CallbackContext) -> None:
    logger.error(msg="Ошибка вызвана апдейтом:", exc_info=context.error)

# Основная функция
async def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.REPLY, handle_user_message))
    application.add_handler(MessageHandler(filters.REPLY & filters.TEXT, handle_admin_reply))
    application.add_error_handler(error_handler)

    # Явный запуск polling
    await application.initialize()  # Инициализация
    try:
        await application.start()
        await application.updater.start_polling()
        await asyncio.Future()  # Блокирует выполнение до прерывания (Ctrl+C)
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    import sys

    # Установка политики цикла для Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Запуск приложения
    asyncio.run(main())