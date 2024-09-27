from database.models import User, Report
from database.models import async_session
from sqlalchemy import select, update, delete
from dataclasses import dataclass
import logging


"""USER"""


async def add_user(tg_id: int, data: dict) -> None:
    """
    Добавляем нового пользователя если его еще нет в БД
    :param tg_id:
    :param data:
    :return:
    """
    logging.info(f'add_user')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        # если пользователя нет в базе
        if not user:
            session.add(User(**data))
            await session.commit()


async def set_fullname(fullname: str, tg_id: int) -> None:
    """
    Обновляем ФИО пользователя
    :param fullname:
    :param tg_id:
    :return:
    """
    logging.info(f'set_fullname')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.fullname = fullname
            await session.commit()


async def set_business(business: str, tg_id: int) -> None:
    """
    Обновляем должность пользователя
    :param business:
    :param tg_id:
    :return:
    """
    logging.info(f'set_business')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.business = business
            await session.commit()


async def set_position(position: str, tg_id: int) -> None:
    """
    Обновляем должность пользователя
    :param position:
    :param tg_id:
    :return:
    """
    logging.info(f'set_position {position} {tg_id}')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.position = position
            await session.commit()


async def set_phone(phone: str, tg_id: int) -> None:
    """
    Обновляем должность пользователя
    :param phone:
    :param tg_id:
    :return:
    """
    logging.info(f'set_positon')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.phone = phone
            await session.commit()


async def get_user_tg_id(tg_id: int) -> User:
    """
    Получаем информацию по пользователю
    :param tg_id:
    :return:
    """
    logging.info(f'get_user_tg_id')
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        return user


async def get_all_users() -> list[User]:
    """
    Получаем список всех пользователей зарегистрированных в боте
    :return:
    """
    logging.info(f'get_all_users')
    async with async_session() as session:
        users = await session.scalars(select(User))
        return users

