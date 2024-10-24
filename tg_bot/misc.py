SIGNS_EN_RU = {
    'Aries': 'Овен',
    'Taurus': 'Телец',
    'Gemini': 'Близнецы',
    'Cancer': 'Рак',
    'Leo': 'Лев',
    'Virgo': 'Дева',
    'Libra': 'Весы',
    'Scorpio': 'Скорпион',
    'Sagittarius': 'Стрелец',
    'Capricorn': 'Козерог',
    'Aquarius': 'Водолей',
    'Pisces': 'Рыбы'
}

SIGNS_RU_EN = {
    'Овен': 'Aries',
    'Телец': 'Taurus',
    'Близнецы': 'Gemini',
    'Рак': 'Cancer',
    'Лев': 'Leo',
    'Дева': 'Virgo',
    'Весы': 'Libra',
    'Скорпион': 'Scorpio',
    'Стрелец': 'Sagittarius',
    'Козерог': 'Capricorn',
    'Водолей': 'Aquarius',
    'Рыбы': 'Pisces',
}

ZODIAC_SIGNS = [
    "♈️ Овен", "♉️ Телец", "♊️ Близнецы", "♋️ Рак",
    "♌️ Лев", "♍️ Дева", "♎️ Весы", "♏️ Скорпион",
    "♐️ Стрелец", "♑️ Козерог", "♒️ Водолей", "♓️ Рыбы"
]

DATE_FORMAT = "%d.%m.%Y"


def format_date(date):
    return date.strftime(DATE_FORMAT)
