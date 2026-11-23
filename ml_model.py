import json
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC


with open(
    "intents.json",
    encoding="utf-8"
) as file:
    data = json.load(file)


X_text = []
y = []


for intent, value in data["intents"].items():
    for example in value["examples"]:
        X_text.append(example)
        y.append(intent)


vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(2,5)
)


X = vectorizer.fit_transform(
    X_text
)


model = LinearSVC()
model.fit(
    X,
    y
)


def get_intent(text):
    text = text.lower()
    result = model.predict(
        vectorizer.transform(
            [text]
        )
    )
    return result[0]

def get_answer(intent):
    if intent in data["intents"]:
        answers = data["intents"][intent]["responses"]
        return random.choice(
            answers
        )


    return "Я пока не знаю ответа."


def generate_answer(text):
    text = text.lower()
    for intent, value in data["intents"].items():
        for example in value["examples"]:
            if example in text:
                return random.choice(
                    value["responses"]
                )

    return None