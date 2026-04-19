import speech_recognition as sr
import subprocess
import sys

def speak(text):
    print(f"Doll: {text}")
    sys.stdout.flush()
    try:
        subprocess.run(['espeak', '--', text], stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        pass

def listen():
    if not sys.stdin.isatty():
        line = sys.stdin.readline()
        if not line:
            return ""
        return line.strip().lower()

    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            text = r.recognize_sphinx(audio)
            return text.lower()
    except Exception as e:
        print("(Microphone input failed. Please type your response:)")
        sys.stdout.flush()
        line = sys.stdin.readline()
        if not line:
            return ""
        return line.strip().lower()

def run_scenario():
    speak("Crisis #1 I just bled all over my seat in science class everyone is going to be staring at me I just know it. Should I A wait till class ends and stay sitting or should I B ask for a paper towel from the teacher to clean up my mess and a hoodie from my friend to hide it from everybody else.")

    while True:
        response = listen()
        if not response:
            return

        words = response.split()
        if 'a' in words or 'wait' in response:
            speak("all right everyone is all gone the teacher is asking why I’m still sitting. Should I be honest yes or no")
            while True:
                sub_response = listen()
                if not sub_response:
                    return
                sub_words = sub_response.split()
                if 'yes' in sub_words or 'honest' in sub_response:
                    speak("thank you so much the teacher helped me and said it is ok everyone makes a slip up sometimes.")
                    return
                elif 'no' in sub_words:
                    speak("she says the teacher walked up to me and said here’s some paper towels everyone makes mistakes sometimes.")
                    return
                else:
                    speak("Please say yes or no.")
        elif 'b' in words or 'ask' in response or 'paper' in response:
            speak("thank you so much ripping off the bandage works so much better it was so embarrassing but I managed to survive.")
            return
        else:
            speak("Please say A or B.")

if __name__ == "__main__":
    run_scenario()
