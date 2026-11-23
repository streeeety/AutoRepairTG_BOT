import random

ADS = [

"""
Кстати 😊
Если понадобится помощь с автомобилем —
мы всегда готовы помочь 🚗
""",



"""
Если захотите проверить автомобиль,
можно записаться на диагностику 🔧
""",



"""
Напоминаю: у нас можно оформить запись
на обслуживание автомобиля 🚗
"""

]


def get_ad():
    return random.choice(ADS)


def need_ad(text):
    text = text.lower()
    important_words = [

        "машина",
        "авто",
        "автомобиль",
        "ремонт",
        "двигатель",
        "масло",
        "поломка"

    ]


    for word in important_words:
        if word in text:
            return True



    if random.randint(1,5) == 1:
        return True

    return False