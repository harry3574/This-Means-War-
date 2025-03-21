import pyttsx3

class TTSHandler:
    def __init__(self, rate=150, volume=1.0):
        """Initialize the TTS engine with customizable parameters."""
        self.engine = pyttsx3.init()

        # Automatically set voice to Microsoft Zira if available, otherwise use default
        self._set_voice_to_zira_if_available()

        # Set speech rate (words per minute)
        self.engine.setProperty('rate', rate)

        # Set volume (0.0 to 1.0)
        self.engine.setProperty('volume', volume)

    def _set_voice_to_zira_if_available(self):
        """
        Internal method to set the voice to Microsoft Zira Desktop if available.
        If not available, it falls back to the default voice.
        """
        voices = self.engine.getProperty('voices')
        zira_voice = None

        # Search for Microsoft Zira Desktop - English (United States)
        for voice in voices:
            if "zira" in voice.name.lower():  # Check if "Zira" is in the voice name
                zira_voice = voice
                break

        if zira_voice:
            print("Using Microsoft Zira Desktop - English (United States).")
            self.engine.setProperty('voice', zira_voice.id)
        else:
            print("Microsoft Zira Desktop not found. Using default voice.")
            self.engine.setProperty('voice', voices[0].id)  # Default voice

    def speak(self, text):
        """Convert text to speech."""
        self.engine.say(text)
        self.engine.runAndWait()

    def stop(self):
        """Stop any ongoing speech."""
        self.engine.stop()

    def set_voice(self, voice_id):
        """Set the voice by ID."""
        voices = self.engine.getProperty('voices')
        if 0 <= voice_id < len(voices):
            self.engine.setProperty('voice', voices[voice_id].id)

    def set_rate(self, rate):
        """Set the speech rate (words per minute)."""
        self.engine.setProperty('rate', rate)

    def set_volume(self, volume):
        """Set the volume (0.0 to 1.0)."""
        self.engine.setProperty('volume', volume)