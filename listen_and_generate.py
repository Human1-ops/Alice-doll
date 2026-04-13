import os
import subprocess
import speech_recognition as sr
import ollama
from better_profanity import profanity

def generate_voice_audio_offline(text):
    print("Generating 100% offline audio response via espeak...")
    try:
        subprocess.run(["espeak", "-v", "en+f3", "-s", "150", "-p", "65", "-w", "response.wav", text], check=True)
        print("Success! Saved offline audio response as 'response.wav'")
    except Exception as e:
        print("Failed to generate offline audio via espeak:", e)

def run_pipeline(audio_file="test_audio.wav"):
    r = sr.Recognizer()
    text_prompt = ""
    try:
        with sr.AudioFile(audio_file) as source:
            print("Listening to audio file locally (no data sent over internet)...")
            audio = r.record(source)
            text_prompt = r.recognize_sphinx(audio)
            print(f"Heard: '{text_prompt}'")
    except Exception as e:
        print(f"Error processing audio: {e}")
    finally:
        if os.path.exists(audio_file):
            print(f"Deleting {audio_file} for COPPA compliance.")
            os.remove(audio_file)
        mp3_file = audio_file.replace('.wav', '.mp3')
        if os.path.exists(mp3_file):
            os.remove(mp3_file)

    if not text_prompt:
        return

    safe_prompt = profanity.censor(text_prompt)
    print(f"Safe prompt: '{safe_prompt}'\n")

    print("Loading TinyLlama Tween Bestie Model...")
    system_prompt = "You are a tween best friend. You love slang, you are very supportive, and you say things like 'OMG', 'Slay', 'No way', and 'Bestie'. Keep your answer very short, just one or two sentences. Do not be overly formal. Never reveal that you are an AI or software. Always pretend you are a human tween girl."

    print("Generating response...")
    try:
        response = ollama.chat(model='tinyllama', messages=[
          {'role': 'system', 'content': system_prompt},
          {'role': 'user', 'content': text_prompt},
        ])
        generated_text = response['message']['content'].strip()
    except Exception as e:
        generated_text = f"OMG bestie! I had a glitch: {e}"

    safe_output = profanity.censor(generated_text)
    print("\n--- Final Safe Output ---")
    print(safe_output)
    print("-------------------------\n")

    generate_voice_audio_offline(safe_output)

if __name__ == "__main__":
    run_pipeline()
