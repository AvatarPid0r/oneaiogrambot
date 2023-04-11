import asyncio
from aiogram import Dispatcher, executor, types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, ParseMode
from aiogram.utils.exceptions import ChatNotFound, ChatIdIsEmpty
import sqlite3 as sq
from config import token
from State import TextState, EditsText, AddsGroups, DeleteGroups, SaveInterval
from sqilite import add_user, edit_user_text, add_groupss, delete_groups
from keyboards import cm_start, inline_st, cancel

storage = MemoryStorage()
bot = Bot(token)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    add_user(user_id)
    await message.answer('''
<b>Привет</b>👋
Этот бот позволяет отправлять заготовленные сообщения в несколько каналов или чатов одновременно. 
Вы можете выбрать нужные вам каналы и чаты, а затем установить интервал времени в минутах, с которым сообщения будут отправляться автоматически.''',
                         reply_markup=await cm_start(), parse_mode='HTML')


@dp.message_handler(text='Добавить текст')
async def add_text(message: types.Message, state: FSMContext):
    await message.answer('Напиши мне любой текст!', reply_markup=await cm_start())
    await TextState.text.set()


@dp.message_handler(state=TextState.text)
async def send_user_text(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_texts = message.html_text
    await state.finish()
    await message.answer(f'<b>Вы отправили такой текст:</b>\n {message.html_text}',
                         reply_markup=await inline_st(), parse_mode='html')
    edit_user_text(user_texts, user_id)


@dp.callback_query_handler(lambda x: x.data == 'edits')
async def inline_edit(callback: CallbackQuery, state: FSMContext):
    await bot.send_message(callback.message.chat.id, 'Отправьте измененный текст')
    await EditsText.text.set()

@dp.callback_query_handler(lambda x: x.data == 'save')
async def fake_save(callback: CallbackQuery):
    await callback.answer('Успешно сохранил ваш текст в базу данных!')

@dp.message_handler(state=EditsText.text)
async def edit_text(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_texts = message.html_text
    await state.finish()
    await message.answer(f'<b>Вот как выглядит ваш обновленный текст</b>\n {message.html_text}',
                         reply_markup=await inline_st(), parse_mode='HTML')
    edit_user_text(user_texts, user_id)


@dp.callback_query_handler(lambda x: x.data == 'send')
async def send_of_groups(callback: CallbackQuery):
    con = sq.connect('DateBase.db')
    cur = con.cursor()
    cur.execute('SELECT user_text, grups FROM users WHERE user_id=?', (callback.from_user.id,))
    result_text = cur.fetchone()
    try:
        if result_text:
            text, groups = result_text
            groups_list = str(groups).replace(' ', '').split(',')
            for group in groups_list:
                try:
                    await bot.send_chat_action(group, "typing")
                    await bot.send_message(chat_id=group, text=text, parse_mode='HTML')
                    await bot.send_message(chat_id=callback.from_user.id, text=f'Успешно отправил в канал\n {group}')
                except (ChatNotFound):
                    await bot.send_message(chat_id=callback.from_user.id, text=f'Не удалось отправить в канал\n {group}')
            con.close()
    except ChatIdIsEmpty:
        await bot.send_message(chat_id=callback.from_user.id, text='Для начала нужно добавить канал')


@dp.message_handler(text='Добавить канал')
async def add_groups(message: types.Message, state: FSMContext):
    await message.answer('''Для корректной обработки, пожалуйста, отправьте мне идентификаторы каналов, которые начинаются с числа "-100" и разделены запятой, <b>без пробелов между ними</b>.

Пример формата: -1001234567891,-1001234567891,-1001234567891. 

Необходимо убедиться, что все идентификаторы каналов начинаются с "-100" и разделены запятой, а также что между идентификаторами нет <b>пробелов</b>.''', parse_mode='HTML')
    await AddsGroups.text.set()


@dp.message_handler(state=AddsGroups.text)
async def add_grop(message: types.Message, state: FSMContext):
    group_id = message.text
    user_id = message.from_user.id
    await state.finish()
    if message.text.startswith('-100'):
        with sq.connect('DateBase.db') as con:
            cur = con.cursor()
            cur.execute('SELECT grups FROM users WHERE user_id=?', (user_id,))
            groups = cur.fetchone()[0]
            if groups:
                groups_list = str(groups).replace(' ', '').split(',')
            else:
                groups_list = []
            if group_id not in groups_list:
                add_groupss(group_id, user_id)
                await message.answer('Успешно добавил канал в базу данных')
            else:
                await message.answer('Данного канала в базе уже есть!')
        con.close()
    else:
        await message.answer('Пришли идентификатор канала начинающийся с "-100"')


@dp.message_handler(text='Удалить группу')
async def delet_groups(message: types.Message, state: FSMContext):
    await message.answer('Пришли мне идентификатор канала который нужно удалить')
    await DeleteGroups.text.set()


@dp.message_handler(state=DeleteGroups.text)
async def delete_grop(message: types.Message, state: FSMContext):
    group_id = message.text
    user_id = message.from_user.id
    await state.finish()
    if message.text.startswith('-100'):
        with sq.connect('DateBase.db') as con:
            cur = con.cursor()
            cur.execute('SELECT grups FROM users WHERE user_id=?', (user_id,))
            groups = cur.fetchone()[0]
            if groups:
                groups_list = str(groups).split(',')
            else:
                groups_list = []
            if group_id not in groups_list:
                await message.answer('Данного канала в базе не нашлось')
            else:
                delete_groups(group_id, user_id)
                await message.answer('Успешно удалил канал из базы данных!')
        con.close()
    else:
        await message.answer('Пришли идентификатор канала начинающийся с "-100"')


sending = True


@dp.message_handler(content_types=['text'])
async def interval(message: types.Message, state: FSMContext):
    global sending
    if message.text == 'Отправка по таймеру':
        await message.answer('Введите время в минутах', reply_markup=await cancel())
        sending = True
        await SaveInterval.text.set()
    if message.text == 'Мои каналы':
        with sq.connect('DateBase.db') as con:
            cur = con.cursor()
            cur.execute('SELECT user_text, grups FROM users WHERE user_id=?', (message.from_user.id,))
            result = cur.fetchone()

            if result:
                text, groups = result
                if groups is not None:
                    groups_list = str(groups).replace(' ', '').split(',')
                    groups_send = str(groups_list)[1:-1].replace("'", "").replace(',', '\n').replace(' ', '')
                    await message.answer(f'Вот ваши каналы:\n{groups_send}')
                else:
                    await message.answer('У вас нету каналов!')
        con.close()
    if message.text == 'Мой текст':
        with sq.connect('DateBase.db') as con:
            cur = con.cursor()
            cur.execute('SELECT user_text, grups FROM users WHERE user_id=?', (message.from_user.id,))
            result = cur.fetchone()

            if result:
                text, groups = result
                if text is not None:
                    await message.answer(f'Вот ваш текст:\n{text}', parse_mode='HTML')
                else:
                    await message.answer('У вас нету текста!')
        con.close()

@dp.message_handler(state=SaveInterval.text)
async def save_interval(message: types.Message, state=FSMContext):
    global sending
    try:
        if message.text.isdigit():
            await handle_valid_interval(message, state)
        elif message.text == 'Отмена':
            await message.answer('Отменил!', reply_markup=await cm_start())
            sending = False
            await state.finish()
        else:
            await message.answer('Неверный формат ввода. Пожалуйста, введите число в минутах.',
                                 reply_markup=await cancel())
    except Exception:
        await message.answer('Для начала добавьте текст и ID канала!')


async def handle_valid_interval(message: types.Message, state=FSMContext):
    try:
        interval = message.text.strip()
        with sq.connect('DateBase.db') as con:
            cur = con.cursor()
            cur.execute('SELECT user_text, grups FROM users WHERE user_id=?', (message.from_user.id,))
            result = cur.fetchone()
            if result:
                text, groups = result
                groups_list = str(groups).replace(' ', '').split(',')
                groups_send = str(groups_list)[1:-1].replace("'", "").replace(',', '\n').replace(' ', '')
                try:
                    while sending:
                        for group in groups_list:
                            try:
                                await bot.send_message(chat_id=group, text=text, parse_mode='HTML')
                            except ChatNotFound:
                                await bot.send_message(chat_id=message.from_user.id,
                                                       text=f'Не удалось доставить сообщение в канал! {group}')

                        await bot.send_message(chat_id=message.from_user.id,
                                               text=f'Успешно! Интервал сообщений будет отправляться каждые {interval} минут ',
                                               reply_markup=await cancel())
                        await bot.send_message(chat_id=message.from_user.id,
                                               text=f'Сообщение успешно доставлено до следующих каналов с интервалом в {interval} минут(у/ы):\n{groups_send}')
                        await asyncio.sleep(int(interval * 60))
                except asyncio.CancelledError:
                    pass
                finally:
                    await state.finish()
            else:
                await bot.send_message(chat_id=message.from_user.id,
                                       text='У вас какая-то ошибка, попробуйте заново')
        con.close()
    except Exception as e:
        await bot.send_message(chat_id=message.from_user.id,
                               text='Для начала добавьте текст или канал!',
                               reply_markup=await cm_start())
async def on_startup(dp):
    print('''
█▄▄ █▄█ ░ ▄▀█ █░█ ▄▀█ ▀█▀ ▄▀█ █▀█ █▀█ █ █▀▄ █▀█ █▀█
█▄█ ░█░ ▄ █▀█ ▀▄▀ █▀█ ░█░ █▀█ █▀▄ █▀▀ █ █▄▀ █▄█ █▀▄''')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

