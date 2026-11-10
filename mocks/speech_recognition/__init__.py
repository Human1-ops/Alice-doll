class Recognizer:
    def listen(self, source, timeout=None, phrase_time_limit=None):
        return None

    def recognize_sphinx(self, audio):
        return ""


class Microphone:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
