from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton


async def cm_start() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    kb0 = KeyboardButton(text='Добавить текст')
    kb = KeyboardButton(text='Добавить канал')
    kb1 = KeyboardButton(text='Удалить группу')
    kb2 = KeyboardButton(text='Отправка по таймеру')
    kb3 = KeyboardButton(text='Мои каналы')
    kb4 = KeyboardButton(text='Мой текст')
    markup.add(kb0).add(kb, kb1).add(kb2).add(kb3, kb4)
    return markup

async def inline_st() -> InlineKeyboardMarkup:
    inli = InlineKeyboardMarkup()
    ikb0 = InlineKeyboardButton(text='Отправить в группы/каналы', callback_data='send')
    ikb = InlineKeyboardButton(text='Изменить текст', callback_data='edits')
    ikb1 = InlineKeyboardButton(text='Удалить текст', callback_data='delete')
    ikb2 = InlineKeyboardButton(text='Сохранить текст', callback_data='save')
    inli.row(ikb0).row(ikb, ikb2)
    return inli

async def cancel() -> ReplyKeyboardMarkup:
    can = ReplyKeyboardMarkup(resize_keyboard=True)
    can0 = KeyboardButton(text='Отмена')
    can.add(can0)
    return can
