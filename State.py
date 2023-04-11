from aiogram.dispatcher.filters.state import State, StatesGroup


class TextState(StatesGroup):
    text = State()

class EditsText(StatesGroup):
    text = State()

class AddsGroups(StatesGroup):
    text = State()

class DeleteGroups(StatesGroup):
    text = State()

class SaveInterval(StatesGroup):
    text = State()