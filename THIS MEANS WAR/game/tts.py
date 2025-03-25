# game/tts.py
import pyttsx3

class TTSHandler:
    def __init__(self, rate=150, volume=1.0):
        self.engine = pyttsx3.init()
        self.set_voice_to_zira_if_available()
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()
    
    # ... (keep rest of your existing TTS methods)