import speech_recognition as sr
import subprocess
import sys
import json
import os
from datetime import date

STATE_FILE = "crisis_state.json"

CRISES = [
    {
        "id": 1,
        "prompt": "Crisis #1 I just bled all over my seat in science class everyone is going to be staring at me I just know it. Should I A wait till class ends and stay sitting or should I B ask for a paper towel from the teacher to clean up my mess and a hoodie from my friend to hide it from everybody else.",
        "path_a_prompt": "all right everyone is all gone the teacher is asking why I’m still sitting. Should I be honest yes or no",
        "path_a_yes_response": "thank you so much the teacher helped me and said it is ok everyone makes a slip up sometimes.",
        "path_a_no_response": "she says the teacher walked up to me and said here’s some paper towels everyone makes mistakes sometimes.",
        "path_b_response": "thank you so much ripping off the bandage works so much better it was so embarrassing but I managed to survive."
    }
    # Add more crises here as dictionaries
]

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"last_played_date": None, "current_crisis_index": 0}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

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

def run_crisis(crisis):
    speak(crisis["prompt"])

    while True:
        response = listen()
        if not response:
            return False

        words = response.split()
        if 'a' in words or 'wait' in response:
            speak(crisis["path_a_prompt"])
            while True:
                sub_response = listen()
                if not sub_response:
                    return False
                sub_words = sub_response.split()
                if 'yes' in sub_words or 'honest' in sub_response:
                    speak(crisis["path_a_yes_response"])
                    return True
                elif 'no' in sub_words:
                    speak(crisis["path_a_no_response"])
                    return True
                else:
                    speak("Please say yes or no.")
        elif 'b' in words or 'ask' in response or 'paper' in response:
            speak(crisis["path_b_response"])
            return True
        else:
            speak("Please say A or B.")

def run_scenario():
    state = load_state()
    today = date.today().isoformat()

    if state["last_played_date"] == today:
        speak("We already handled a crisis today! Let's play again tomorrow.")
        return

    index = state["current_crisis_index"]
    if index >= len(CRISES):
        speak("We have handled all the crises!")
        return

    crisis = CRISES[index]
    completed = run_crisis(crisis)

    if completed:
        state["last_played_date"] = today
        state["current_crisis_index"] = index + 1
        save_state(state)

if __name__ == "__main__":
    run_scenario()
