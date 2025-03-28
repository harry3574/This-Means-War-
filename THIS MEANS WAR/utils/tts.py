import pyttsx3
from typing import Optional

class TTSHandler:
    def __init__(self, rate=150, volume=1.0, voice_id=None):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)
        if voice_id:
            self.set_voice(voice_id)
    
    def set_voice(self, voice_id: str) -> bool:
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if voice.id == voice_id:
                self.engine.setProperty('voice', voice.id)
                return True
        return False
    
    def speak(self, text: str) -> None:
        self.engine.say(text)
        self.engine.runAndWait()
    
    def stop(self) -> None:
        self.engine.stop()
    
    @staticmethod
    def list_voices() -> list:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        return [{'id': v.id, 'name': v.name} for v in voices]