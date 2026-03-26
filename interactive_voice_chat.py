import speech_recognition as sr
import ollama
import subprocess
from better_profanity import profanity

def generate_voice_audio_offline(text):
    print("Bestie is speaking...")
    try:
        # Playing the audio directly using espeak
        subprocess.run(["espeak", "-v", "en+f3", "-s", "150", "-p", "65", text], check=True)
    except Exception as e:
        print("Failed to speak via espeak:", e)

def voice_chat():
    r = sr.Recognizer()

    print("Loading TinyLlama Tween Bestie Model...")
    system_prompt = "You are a tween best friend. You love slang, you are very supportive, and you say things like 'OMG', 'Slay', 'No way', and 'Bestie'. Keep your answer very short, just one or two sentences. Do not be overly formal. Never reveal that you are an AI or software. Always pretend you are a human tween girl."
    messages = [{'role': 'system', 'content': system_prompt}]

    try:
        with sr.Microphone() as source:
            print("\nAdjusting for ambient noise... Please wait.")
            r.adjust_for_ambient_noise(source, duration=1)
            print("\nVoice Chat Started! (Press Ctrl+C to stop)")

            while True:
                print("\nListening... (Speak now!)")
                audio = r.listen(source)

                try:
                    print("Recognizing your voice...")
                    # offline recognition using pocketsphinx
                    user_text = r.recognize_sphinx(audio)
                    print(f"You said: '{user_text}'")

                    if not user_text.strip():
                        continue

                    messages.append({'role': 'user', 'content': user_text})

                    response = ollama.chat(model='tinyllama', messages=messages)
                    generated_text = response['message']['content'].strip()

                    messages.append({'role': 'assistant', 'content': generated_text})

                    safe_output = profanity.censor(generated_text)
                    print(f"Bestie: {safe_output}")

                    generate_voice_audio_offline(safe_output)

                except sr.UnknownValueError:
                    print("Oops, I couldn't understand that. Could you repeat?")
                except sr.RequestError as e:
                    print(f"Sphinx error; {e}")

    except KeyboardInterrupt:
        print("\nBestie: TTYL! 💖")
    except AttributeError:
        print("\nError: Could not find PyAudio. Please install it using 'pip install PyAudio' to use the microphone.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    voice_chat()
