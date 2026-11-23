import json

FILE = "stats.json"

def load_stats():
    try:
        with open(
            FILE,
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except:
        return {
            "users": [],
            "messages": 0,
            "voice_messages": 0,
            "orders": 0,
            "requests": {}
        }


def save_stats(data):
    with open(
        FILE,
        "w",
        encoding="utf-8"

    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )



def add_user(user_id):
    data = load_stats()

    if user_id not in data["users"]:
        data["users"].append(user_id)

    save_stats(data)


def add_message(text):
    if not text:
        return

    data = load_stats()
    data["messages"] += 1
    words = text.lower().split()
    for word in words:
        if len(word) > 3:
            if word in data["requests"]:
                data["requests"][word] += 1
            else:
                data["requests"][word] = 1
    save_stats(data)

def add_voice():
    data = load_stats()
    data["voice_messages"] += 1
    save_stats(data)

def add_order():
    data = load_stats()
    data["orders"] += 1
    save_stats(data)


def get_stats():
    data = load_stats()
    top = sorted(
        data["requests"].items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]


    result = f"""

📊 Статистика AutoRepair Bot


👥 Пользователей:

{len(data["users"])}


💬 Сообщений:

{data["messages"]}


🎤 Голосовых сообщений:

{data["voice_messages"]}


📅 Заявок:

{data["orders"]}


🔥 Популярные запросы:

"""

    for word, count in top:
        result += f"\n• {word} — {count}"
    return result