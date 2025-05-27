import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")  # Пример: @bobscience

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# /post — публикует пост с картинкой и кнопкой-ссылкой в канал
@dp.message(Command("post"))
async def post_to_channel(message: types.Message):
    try:
        await bot.send_photo(
            chat_id=CHANNEL_USERNAME,
            photo=types.FSInputFile("Post_button.jpg"),  # Картинка в папке проекта
            caption="🧠 <b>Хочешь всё знать!?</b>\n\n"
                    "Нажмите кнопку ниже 👇",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text="💡 ХОЧУ ВСЁ ЗНАТЬ 💡",
                        url="https://t.me/bobscience_bot?start=TGkanal"
                    )]
                ]
            )
        )
        await message.answer("✅ Пост с картинкой и кнопкой успешно отправлен.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при отправке поста: {e}")

# /start?start=TGkanal — обработка перехода из поста
@dp.message(CommandStart(deep_link=True))
async def handle_start_with_param(message: types.Message, command: CommandStart):
    user_id = message.from_user.id

    if command.args == "TGkanal":
        try:
            member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
            if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
                return  # уже подписан — ничего не делаем
            else:
                await message.answer(
                    "🔒 <b>Доступ к знаниям только для подписчиков канала</b>\n\n"
                    "1. Подпишитесь на канал @bobscience👈\n"
                    "2. Нажмите кнопку «✅ Я подписался»👇",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=[
                            [InlineKeyboardButton(text="📲 Перейти в канал", url="https://t.me/bobscience")],
                            [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_TGkanal")]
                        ]
                    )
                )
        except Exception as e:
            logging.error(f"Ошибка при проверке подписки TGkanal: {e}")
            await message.answer("⚠️ Не удалось проверить подписку. Попробуйте позже.")

# Обработка кнопки «Я подписался»
@dp.callback_query(F.data == "check_TGkanal")
async def check_subscription_TGkanal(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
            await callback.answer("✅ Подписка подтверждена!", show_alert=True)
            await callback.message.edit_text("✅ Подписка подтверждена! Получите ваши знания:")

            # 📎 Отправка файла
            await bot.send_document(
                chat_id=user_id,
                document=types.FSInputFile("Реферат_Лимонная_батарейка_docx_1.pdf"),
                caption="📄 Ваш файл: «Реферат Лимонная батарейка»"
            )
        else:
            await callback.answer("❌ Вы ещё не подписаны!", show_alert=True)
    except Exception as e:
        logging.error(f"Ошибка при повторной проверке подписки: {e}")
        await callback.answer("⚠️ Ошибка. Попробуйте позже.", show_alert=True)

# Запуск бота
async def main():
    await bot.delete_webhook(drop_pending_updates=True)  # убираем webhook, если был
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
