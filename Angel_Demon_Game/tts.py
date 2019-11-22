import pyttsx3


class Voice:
    def __init__(self, voice_num):
        self.tts = pyttsx3.init()
        voices = self.tts.getProperty('voices')
        self.tts.setProperty('voice', voices[voice_num].id)

    def say_something(self, message):
        self.tts.say(message)
        self.tts.runAndWait()
