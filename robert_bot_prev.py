import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

# Загрузка .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")  # Пример: @bobscience
OWNER_IDS = [int(uid.strip()) for uid in os.getenv("OWNER_IDS", "").split(",") if uid.strip().isdigit()]

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Команда /post — только для владельцев
@dp.message(Command("post"))
async def post_to_channel(message: types.Message):
    if message.from_user.id not in OWNER_IDS:
        await message.answer("⛔️ У вас нет доступа к этой команде.")
        return

    try:
        await bot.send_photo(
            chat_id=CHANNEL_USERNAME,
            photo=types.FSInputFile("robert_yutube.jpg"),
            caption=(
                "Привет! 👋 Я Роберт, и если ты смотрел(а) мой ролик про «Лимонную батарейку», вот твой бонус 🎁\n\n"
                "<b>❗️❗️❗️Лимоны зажгли лампочку?! Как я это сделал? 👨‍💻</b>\n\n"
                "В файле подробно расписано как это повторить и удивить родителей или друзей!\n\n"
                "— какие материалы нужны 🍋🔩\n"
                "— как всё правильно соединить 🔌\n"
                "— что делать, если лампочка не горит 💡\n"
                "— почему лимоны вообще дают электричество ⚡️\n\n"
                "Жмите на кнопку ниже (подождите загрузку 5-10 сек), чтобы получить файл 👇👇👇"
            ),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[
                    InlineKeyboardButton(
                        text="💡 Инструкция 💡",
                        url="https://t.me/bobscience_bot?start=TGkanal"
                    )
                ]]
            )
        )
        await message.answer("✅ Пост с картинкой и кнопкой успешно отправлен.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при отправке поста: {e}")

# /start — проверка подписки, отправка презентации и таймер
@dp.message(CommandStart())
async def start_handler(message: types.Message, command: CommandStart):
    user_id = message.from_user.id

    # Отправка фонового изображения
    await bot.send_photo(user_id, types.FSInputFile("oblozhka_fon_bota.jpg"))

    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
            await message.answer("✅ Подписка подтверждена! Вот ваш файл:")
            await bot.send_document(
                chat_id=user_id,
                document=types.FSInputFile("Лимонная_батарейка_презентация.pdf"),
                caption="📄\n"
                        "Не спешите закрывать бота, в ближайшие 5 дней я пришлю вам реферат по этому эксперименту.\n\n"
                        "Руководства по новым экспериментам буду выдавать тут 👋"
            )
            asyncio.create_task(send_delayed_referral(user_id))
        else:
            raise Exception("Пользователь не подписан")
    except Exception:
        await message.answer(
            "🔒 <b>Доступ к знаниям только для подписчиков канала</b>\n\n"
            "1. Подпишитесь на канал @bobscience 👈\n"
            "2. Нажмите кнопку «✅ Я подписался» 👇",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="📲 Перейти в канал", url="https://t.me/bobscience")],
                    [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_TGkanal")]
                ]
            )
        )

# Обработка кнопки «Я подписался»
@dp.callback_query(F.data == "check_TGkanal")
async def check_subscription(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
            await callback.answer(
                "✅ Подписка подтверждена!\n"
                "Спасибо за подписку, жмите кнопку «СТАРТ», если ещё не нажали 👇",
                show_alert=True
            )
        else:
            await callback.answer("❌ Вы ещё не подписаны!", show_alert=True)
    except Exception as e:
        logging.error(f"Ошибка при проверке подписки: {e}")
        await callback.answer("⚠️ Ошибка. Попробуйте позже.", show_alert=True)

# Отложенная отправка реферата
async def send_delayed_referral(user_id: int):
    await asyncio.sleep(900)  # 15 минут
    try:
        await bot.send_message(user_id, "Подробный реферат 🔗")
        await bot.send_document(
            chat_id=user_id,
            document=types.FSInputFile("Реферат_Лимонная_батарейка.pdf"),
            caption="📝 Ваш реферат готов!"
        )
    except Exception as e:
        logging.error(f"Ошибка при отправке реферата через 15 минут: {e}")

# Запуск
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
