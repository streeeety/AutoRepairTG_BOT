import speech_recognition as sr

def voice_to_text(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)


    try:
        text = recognizer.recognize_google(
            audio,
            language="ru-RU"
        )
        return text

    except:
        return None