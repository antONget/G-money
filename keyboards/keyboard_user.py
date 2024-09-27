from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.models import User
import logging

list_help = ["👥 Привлечь новых клиентов 👥",
             "💪 Прокачать бренд в соцсетях и мессенджерах 💪",
             "👩‍💻 Нанять сотрудников 🧑‍💻",
             "👩‍🎓 Обучить отдел продаж 👨‍🎓",
             "🔝 Поднять продажи, маржу, средний чек 🔝",
             "🔊 Сделать громкую пиар-акцию 🔊"]


def keyboard_position(position: list) -> InlineKeyboardMarkup:
    logging.info(f"keyboards_attach_resources")
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for i, title in enumerate(list_help):
        if not position[i]:
            text = title
        else:
            text = f"✅ {title}"
        button = f'select_{i}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    kb_builder.row(*buttons, width=1)
    return kb_builder.as_markup()


def keyboard_position_1(position: list) -> InlineKeyboardMarkup:
    logging.info(f"keyboards_attach_resources")
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    for i, title in enumerate(list_help):
        if not position[i]:
            text = title
        else:
            text = f"✅ {title}"
        button = f'select_{i}'
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    kb_builder.row(*buttons, width=1)
    kb_builder.row(InlineKeyboardButton(
            text="Продолжить",
            callback_data="continue"), width=1)
    return kb_builder.as_markup()


def keyboards_get_contact() -> ReplyKeyboardMarkup:
    logging.info("keyboards_get_contact")
    button_1 = KeyboardButton(text='Отправить свой контакт ☎️',
                              request_contact=True)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1]],
        resize_keyboard=True
    )
    return keyboard