import pyttsx3


class Voice:
    def __init__(self, voice_num):
        self.tts = pyttsx3.init()
        voices = self.tts.getProperty('voices')
        self.tts.setProperty('voice', voices[voice_num].id)

    def say_something(self, message):
        self.tts.say(message)
        self.tts.runAndWait()


def init_voice():
    voice1 = Voice(12)

def say(message):
    voice1.say_something(message)
