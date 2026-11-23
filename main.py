from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from ml_model import (
    get_intent,
    get_answer,
    generate_answer
)
from voice import voice_to_text
from free_chat import free_answer

from marketing import (
    need_ad,
    get_ad
)
from statistics import (
    add_user,
    add_message,
    add_voice,
    add_order,
    get_stats
)
from datetime import datetime
import subprocess
import os

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))


def main_menu():
    return ReplyKeyboardMarkup(

        [

            ["🔧 Услуги", "💰 Цены"],
            ["📅 Запись", "📍 Контакты"],
            ["🤖 Задать вопрос"]

        ],
        resize_keyboard=True
    )

async def start(update, context):
    add_user(
        update.message.from_user.id
    )
    await update.message.reply_text(

"""
🚗 AutoRepair Bot


Я виртуальный помощник автосервиса.


Могу:

🔧 рассказать об услугах

💰 показать цены

📅 оформить запись

🤖 ответить на вопросы


Выберите действие 👇

""",

reply_markup=main_menu()
)


async def services(update, context):
    keyboard = [

        [
            InlineKeyboardButton(
                "🔧 Диагностика",
                callback_data="diag"
            )
        ],

        [
            InlineKeyboardButton(
                "🛢 Замена масла",
                callback_data="oil"
            )
        ],

        [
            InlineKeyboardButton(
                "⚙️ Ремонт двигателя",
                callback_data="engine"
            )
        ]

    ]


    await update.message.reply_text(
        "Выберите услугу:",
        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )

async def service_button(update, context):
    query = update.callback_query
    await query.answer()


    data = {


        "diag":

        "🔧 Диагностика автомобиля\nЦена: 1000 рублей",


        "oil":

        "🛢 Замена масла\nЦена: 1500 рублей",


        "engine":

        "⚙️ Ремонт двигателя\nЦена: от 5000 рублей"

    }


    await query.message.reply_text(
        data[query.data]
    )


async def booking(update, context):
    context.user_data["booking"] = True
    await update.message.reply_text(

"""
📅 Оформление заявки


Отправьте:


🚘 Марка автомобиля

🔧 Какая услуга нужна

📆 Желаемая дата


Можно текстом или голосом 🎤

"""

)


def save_order(user,text):
    time = datetime.now().strftime(
        "%d.%m.%Y %H:%M"
    )


    order = f"""

====================

Дата:

{time}


Клиент:

{user}


Заявка:

{text}


====================

"""

    with open(
        "orders.txt",
        "a",
        encoding="utf-8"
    ) as file:
        file.write(order)
    return order


def is_booking_request(text):

    if not text:

        return False

    text = text.lower()

    phrases = [

        "запись",
        "записаться",
        "хочу записаться",
        "запишите меня",
        "запиши меня",
        "нужен ремонт",
        "хочу ремонт",
        "починить машину",
        "нужна диагностика",
        "хочу в сервис"

    ]

    return any(
        phrase in text
        for phrase in phrases
    )


async def process_text(update, context, text):
    if not text:

        return

    add_user(
        update.message.from_user.id
    )

    add_message(text)

    if is_booking_request(text):
        context.user_data["booking"] = True
        await update.message.reply_text(

"""
📅 Отлично, оформим запись!


Отправьте:


🚘 Марка автомобиля

🔧 Какая услуга нужна

📆 Желаемая дата

"""
        )
        return


    if context.user_data.get("booking"):
        order = save_order(
            update.message.from_user.first_name,
            text
        )

        add_order()
        context.user_data["booking"] = False

        await context.bot.send_message(
            ADMIN_ID,
            "🚗 Новая заявка:\n\n" + order
        )

        await update.message.reply_text(

"""
✅ Заявка принята!


В скором времени с вами свяжутся
для уточнения деталей 🚗

""",

reply_markup=main_menu()

        )
        return

    free = free_answer(text)

    if free:
        response = free
    else:
        intent = get_intent(text)
        response = get_answer(intent)
        generated = generate_answer(text)
        if generated:
            response = generated


    if need_ad(text):
        response += "\n\n" + get_ad()


    await update.message.reply_text(
        response,
        reply_markup=main_menu()

    )

async def answer(update, context):

    await process_text(
        update,
        context,
        update.message.text

    )

async def voice_message(update, context):
    add_voice()
    file = await context.bot.get_file(
        update.message.voice.file_id
    )

    await file.download_to_drive(
        "voice.ogg"
    )


    subprocess.run(

        [
            "ffmpeg",
            "-i",
            "voice.ogg",
            "voice.wav",
            "-y"
        ],

        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


    text = voice_to_text(
        "voice.wav"
    )


    if not text:
        await update.message.reply_text(
            "🎤 Не удалось распознать голос"
        )
        return

    await process_text(
        update,
        context,
        text
    )



async def orders(update, context):
    if update.message.from_user.id != ADMIN_ID:
        return


    with open(
        "orders.txt",
        encoding="utf-8"
    ) as file:
        data=file.read()



    await update.message.reply_text(
        data[-4000:]
    )




async def stats(update, context):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text(
            "❌ Нет доступа"
        )
        return

    await update.message.reply_text(
        get_stats()
    )


async def clear_orders(update, context):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text(
            "❌ Нет доступа"
        )
        return



    open(
        "orders.txt",
        "w",
        encoding="utf-8"
    ).close()



    await update.message.reply_text(
        "✅ Список заявок очищен."
    )

async def menu(update, context):
    text = update.message.text

    if text == "🔧 Услуги":
        await services(update, context)



    elif text == "📅 Запись":
        await booking(update, context)



    elif text == "💰 Цены":
        await update.message.reply_text(
            "🔧 Диагностика — 1000₽\n🛢 Масло — 1500₽\n⚙️ Двигатель — от 5000₽"
        )



    elif text == "📍 Контакты":
        await update.message.reply_text(
            "📍 Автосервис\n☎️ +7 900 000-00-00"
        )


def main():
    app = Application.builder()\
        .token(TOKEN)\
        .build()


    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CommandHandler(
            "orders",
            orders
        )
    )



    app.add_handler(
        CommandHandler(
            "stats",
            stats
        )
    )


    app.add_handler(
        CommandHandler(
            "clear_orders",
            clear_orders
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            service_button
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Regex(
                "^(🔧 Услуги|💰 Цены|📅 Запись|📍 Контакты)$"
            ),
            menu
        )
    )

    app.add_handler(
        MessageHandler(
            filters.VOICE,
            voice_message
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            answer
        )
    )
    print(

        "Бот запущен"

    )
    app.run_polling()
if __name__ == "__main__":
    main()