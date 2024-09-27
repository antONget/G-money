import asyncio

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config_data.config import Config, load_config
import database.requests as rq
import keyboards.keyboard_user as kb
from filter.filter import validate_russian_phone_number
from services.googlesheets import append_row


import logging


router = Router()
config: Config = load_config()


class User(StatesGroup):
    name = State()
    business = State()
    phone = State()
    time = State()


@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext) -> None:
    """
    Запуск бота - нажата кнопка "Начать" или введена команда "/start"
    :param message:
    :param state:
    :return:
    """
    logging.info(f"process_start_command {message.chat.id}")
    file_id = "AgACAgIAAxkBAAMFZvZTaqifzDH9m6mJ-emba4B0s7kAAozrMRudcrFLtXk4GrNrxEcBAAMCAAN4AAM2BA"
    await state.set_state(state=None)
    user = await rq.get_user_tg_id(tg_id=message.chat.id)
    if not user:
        if message.from_user.username == None:
            username = 'None'
        else:
            username = message.from_user.username
        await rq.add_user(tg_id=message.chat.id,
                          data={"tg_id": message.chat.id, "username": username})
    await message.answer_photo(photo=file_id,
                               caption=f'Приветствую, я - робот Илон! 👋\n'
                                       f'Мы вместе с командой G-money поможем привлечь новых клиентов в ваш'
                                       f' бизнес 💰💰💰.')
    await asyncio.sleep(1)
    await message.answer(text="Как вас зовут?")
    await state.set_state(User.name)


@router.message(F.text, StateFilter(User.name))
async def get_fullname(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем от пользователя ФИО
    :param message:
    :param state:
    :return:
    """
    logging.info(f'get_fullname {message.chat.id}')
    # await bot.delete_message(chat_id=message.chat.id,
    #                          message_id=message.message_id-1)
    # await bot.delete_message(chat_id=message.chat.id,
    #                          message_id=message.message_id)
    await bot.set_message_reaction(chat_id=message.chat.id,
                                   message_id=message.message_id,
                                   reaction=[{"type": "emoji", "emoji": "🤝"}])
    await rq.set_fullname(fullname=message.text, tg_id=message.chat.id)
    await state.update_data(name=message.text)
    await state.set_state(state=None)
    await message.answer(text=f"Очень приятно, {message.text} 👋.\n"
                              f"Какой у вас бизнес?")

    await state.set_state(User.business)


@router.message(F.text, StateFilter(User.business))
async def get_business(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем какой бизнес у пользователя
    :param message:
    :param state:
    :return:
    """
    logging.info(f'get_business {message.chat.id}')
    # await bot.delete_message(chat_id=message.chat.id,
    #                          message_id=message.message_id-1)
    # await bot.delete_message(chat_id=message.chat.id,
    #                          message_id=message.message_id)
    await bot.set_message_reaction(chat_id=message.chat.id,
                                   message_id=message.message_id,
                                   reaction=[{"type": "emoji", "emoji": "🔥"}])
    await asyncio.sleep(1)
    await rq.set_business(business=message.text, tg_id=message.chat.id)
    await state.set_state(state=None)
    position = [0, 0, 0, 0, 0, 0]
    await state.update_data(position=position)
    await message.answer(text=f"Чем мы можем быть вам полезны?\n\n"
                              f"Отметьте из предложенного списка (можно несколько вариантов):",
                         reply_markup=kb.keyboard_position(position=position))


@router.callback_query(F.data.startswith('select_'))
async def select_position(callback: CallbackQuery, state: FSMContext):
    """
    Выбор полей в которых бот может полезен
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'select_position {callback.message.chat.id}')
    data = await state.get_data()

    position = data['position']
    index = int(callback.data.split('_')[-1])
    if position[index]:
        position[index] = 0
    else:
        position[index] = 1
    await state.update_data(position=position)
    await callback.message.edit_text(text="Чем мы можем быть полезны Вам?\n\n"
                                          "Отметьте из предложенного (можно несколько вариантов):",
                                     reply_markup=kb.keyboard_position_1(position=position))
    await callback.answer()


@router.callback_query(F.data == 'continue')
async def process_continue(callback: CallbackQuery, state: FSMContext):
    """
    Продолжить
    :param callback:
    :param state:
    :return:
    """
    logging.info(f'process_continue {callback.message.chat.id}')
    await callback.message.edit_text(text="Записал! 👌",
                                     reply_markup=None)

    await callback.message.answer(text="Оставьте свой номер телефона:",
                                  reply_markup=kb.keyboards_get_contact())
    data = await state.get_data()
    position = ','.join(map(str, data["position"]))
    await rq.set_position(position=position, tg_id=callback.message.chat.id)
    await state.set_state(User.phone)
    await callback.answer()


@router.message(StateFilter(User.phone))
async def get_phone_user(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем номер телефона проверяем его на валидность и заносим его в БД
    :param message:
    :param state:
    :return:
    """
    logging.info(f'get_phone_user: {message.chat.id}')
    # await bot.delete_message(chat_id=message.chat.id,
    #                          message_id=message.message_id-2)
    # await bot.delete_message(chat_id=message.chat.id,
    #                          message_id=message.message_id-1)
    # await bot.delete_message(chat_id=message.chat.id,
    #                          message_id=message.message_id)
    # если номер телефона отправлен через кнопку "Поделится"
    if message.contact:
        phone = str(message.contact.phone_number)
    # если введен в поле ввода
    else:
        phone = message.text
        # проверка валидности отправленного номера телефона, если не валиден просим ввести его повторно
        if not validate_russian_phone_number(phone):
            await message.answer(text="Неверный формат номера, повторите ввод.")
            return
    # обновляем поле номера телефона
    await state.update_data(phone=phone)
    await rq.set_phone(phone=phone, tg_id=message.chat.id)
    await message.answer(text="В какое время удобнее, чтобы наш менеджер связался с вами?",
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(User.time)


@router.message(StateFilter(User.time))
async def get_time(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Получаем время звонка
    :param message:
    :param state:
    :param bot:
    :return:
    """
    logging.info(f'get_phone_user: {message.chat.id}')
    # await bot.delete_message(chat_id=message.chat.id,
    #                          message_id=message.message_id-1)
    # await bot.delete_message(chat_id=message.chat.id,
    #                          message_id=message.message_id)
    await state.set_state(state=None)
    await state.update_data(time=message.text)
    await message.answer(text="Отлично! 🔥🔥🔥\n У меня уже есть пара идей для вашего бизнеса.\n"
                              "Сейчас обсужу их с командой, и свяжемся с вами в удобное время. ")
    data = await state.get_data()
    user_info = await rq.get_user_tg_id(tg_id=message.chat.id)
    position = data["position"]
    text = ''
    i = 0
    for p in position:
        if p:
            i += 1
            text += f"{i}. {kb.list_help[i]}\n"
    for admin in config.tg_bot.admin_ids.split(','):
        try:
            await bot.send_message(chat_id=admin,
                                   text=f"<b>Пользователь @{user_info.username} заполнил анкету:\n\n</b>"
                                        f"<b>Имя:</b> {user_info.fullname}\n"
                                        f"<b>Телефон:</b> {user_info.phone}\n"
                                        f"<b>Время звонка:</b> {message.text}\n"
                                        f"<b>Ниша бизнеса:</b> {user_info.business}\n"
                                        f"<b>Чем мы можем быть полезны:</b>\n{text}")
        except:
            pass
    await append_row(data=[user_info.fullname, user_info.phone, message.text,user_info.business, text])

