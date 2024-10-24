from aiogram.fsm.state import State, StatesGroup


class ZodiacStates(StatesGroup):
    main_menu = State()
    set_zodiac = State()
    chosen_zodiac = State()
