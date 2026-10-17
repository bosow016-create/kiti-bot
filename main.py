import asyncio
import logging
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile, InlineKeyboardButton, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = os.getenv("8838721828:AAH-KLaYLhzLsn5g5DnEhyc5mIgEnY0rjOc") or "8838721828:AAH-KLaYLhzLsn5g5DnEhyc5mIgEnY0rjOc"

PHOTO_MENU = "menu_banner.png"
PHOTO_SCRIPT = "script.png"
PHOTO_BUY = "buy.png"

GIFT_USER = "Kiti510"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

STARS_PLANS = {
    "stars_7": ("7 дней", 50),
    "stars_30": ("30 дней", 150),
    "stars_forever": ("Навсегда", 250),
}

MENU_CAPTION = "Меню:"

SCRIPT_CAPTION = (
    "📄 <b>Скрипт</b>\n\n"
    "<code>loadstring(game:HttpGet(\"https://pastefy.app/gPuS4n3Q/raw\"))()</code>\n\n"
    "Если скрипт выше не работает:\n"
    "<code>loadstring(game:HttpGet(\"https://raw.githubusercontent.com/Royal-Script-hub/kiti/refs/heads/main/kiti_loader\"))()</code>\n\n"
    "Нажми на скрипт, чтобы скопировать."
)

BUY_CAPTION = (
    "KITI остаётся бесплатным, но если вы не хотите каждый раз "
    "получать новый ключ, смотреть рекламу или просто хотите поддержать проект, вот прайс-лист:\n\n"
    "⭐ <b>7д - 50</b>\n"
    "⭐ <b>30д - 150</b>\n"
    "⭐ <b>Навсегда - 250</b>\n\n"
    "💳 <b>Навсегда - 350₽</b>\n\n"
    "Менеджер: @manager_kiti\n"
    "Покупка за рубли: https://funpay.com/lots/offer?id=75492133\n"
    "Покупка за звёзды: @Kiti510"
)


# ------------------------- КЛАВИАТУРЫ -------------------------

def main_menu_kb():
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="Скрипт 📄", callback_data="show_script"),
        InlineKeyboardButton(text="Купить ключ 💵", callback_data="buy_key"),
    )
    b.row(InlineKeyboardButton(text="Отзывы ⭐ ", url="https://t.me/OTZIVImKITI"))
    b.row(InlineKeyboardButton(text="Поддержка 💬 ", url="https://t.me/manager_kiti"))
    return b.as_markup()


def buy_key_kb():
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="Купить за ₽ 💳 ↗", url="https://funpay.com/lots/offer?id=75492133"))
    b.row(InlineKeyboardButton(text="Купить за Stars ⭐", callback_data="buy_stars"))
    b.row(InlineKeyboardButton(text="Купить за NFT 🎩", callback_data="buy_nft"))
    b.row(InlineKeyboardButton(text="Менеджер ✉️ ↗", url="https://t.me/manager_kiti"))
    b.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_main"))
    return b.as_markup()


def back_kb():
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_main"))
    return b.as_markup()


def stars_kb():
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="7дн - 50⭐", callback_data="stars_7"))
    b.row(InlineKeyboardButton(text="30дн - 150⭐", callback_data="stars_30"))
    b.row(InlineKeyboardButton(text="Навсегда - 250⭐", callback_data="stars_forever"))
    b.row(InlineKeyboardButton(text="◀️ Назад", callback_data="buy_key"))
    return b.as_markup()


def profile_kb(back_to: str):
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="Перейти в профиль", url=f"https://t.me/{GIFT_USER}"))
    b.row(InlineKeyboardButton(text="◀️ Назад", callback_data=back_to))
    return b.as_markup()


# ------------------------- ПОМОЩНИКИ -------------------------

async def send_screen(callback: types.CallbackQuery, photo_path: str, caption: str,
                      kb, parse_mode: str | None = None):
    """Удаляет старое сообщение и отправляет новое (с фото, иначе без)."""
    try:
        await callback.message.delete()
    except Exception:
        pass
    try:
        await callback.message.answer_photo(
            photo=FSInputFile(photo_path), caption=caption,
            reply_markup=kb, parse_mode=parse_mode,
        )
    except Exception as e:
        logging.error(f"Ошибка с фото {photo_path}: {e}")
        await callback.message.answer(caption, reply_markup=kb, parse_mode=parse_mode)


async def show_screen(callback: types.CallbackQuery, photo_path: str, caption: str, kb):
    """Меняет и фото, и подпись в том же сообщении. Если не вышло - отправляет заново."""
    try:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=FSInputFile(photo_path),
                caption=caption,
                parse_mode="HTML",
            ),
            reply_markup=kb,
        )
    except Exception as e:
        logging.error(f"edit_media не сработал, отправляю заново: {e}")
        await send_screen(callback, photo_path, caption, kb, parse_mode="HTML")


async def edit_screen(callback: types.CallbackQuery, text: str, kb):
    """Меняет только текст/подпись, картинка остаётся."""
    try:
        await callback.message.edit_caption(caption=text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        try:
            await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception as e:
            logging.error(f"Ошибка редактирования: {e}")


# ------------------------- ОБРАБОТЧИКИ -------------------------

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    try:
        await message.answer_photo(
            photo=FSInputFile(PHOTO_MENU), caption=MENU_CAPTION, reply_markup=main_menu_kb()
        )
    except Exception as e:
        logging.error(f"Ошибка с фото меню: {e}")
        await message.answer(MENU_CAPTION, reply_markup=main_menu_kb())


@dp.callback_query(F.data == "show_script")
async def show_script(callback: types.CallbackQuery):
    await callback.answer()
    await show_screen(callback, PHOTO_SCRIPT, SCRIPT_CAPTION, back_kb())


@dp.callback_query(F.data == "buy_key")
async def buy_key(callback: types.CallbackQuery):
    await callback.answer()
    await show_screen(callback, PHOTO_BUY, BUY_CAPTION, buy_key_kb())


@dp.callback_query(F.data == "buy_stars")
async def buy_stars(callback: types.CallbackQuery):
    await callback.answer()
    text = (
        "<b>Выберите срок ключа:</b>\n\n"
        "Выбор срока создаст заявку и зафиксирует время, "
        "начиная с которого будут учитываться подарки."
    )
    await edit_screen(callback, text, stars_kb())


@dp.callback_query(F.data.in_(STARS_PLANS.keys()))
async def choose_stars_plan(callback: types.CallbackQuery):
    await callback.answer()
    title, price = STARS_PLANS[callback.data]
    now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    text = (
        f"<b>Заявка создана ✅</b>\n\n"
        f"Срок: <b>{title}</b>\n"
        f"Стоимость: <b>{price}⭐</b>\n"
        f"Время фиксации: <b>{now}</b>\n\n"
        f"Отправьте подарок на <b>{price}⭐</b> на @{GIFT_USER}. "
        f"Ключ выдаётся после получения подарка."
    )
    await edit_screen(callback, text, profile_kb("buy_stars"))


@dp.callback_query(F.data == "buy_nft")
async def buy_nft(callback: types.CallbackQuery):
    await callback.answer()
    text = (
        "🎩 <b>Ключ за NFT</b>\n\n"
        f"Отправьте любой NFT подарок на @{GIFT_USER} - взамен получите ключ <b>навсегда.</b>\n\n"
        "Ключ выдаётся после получения подарка 🍖"
    )
    await edit_screen(callback, text, profile_kb("buy_key"))


@dp.callback_query(F.data == "back_main")
async def back_main(callback: types.CallbackQuery):
    await callback.answer()
    await show_screen(callback, PHOTO_MENU, MENU_CAPTION, main_menu_kb())


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())