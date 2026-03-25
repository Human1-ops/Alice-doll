import os
import speech_recognition as sr
import ollama
import requests
from better_profanity import profanity

API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")

def get_or_create_alice_voice():
    headers = {"xi-api-key": API_KEY}

    # 1. Check if voice already exists
    print("Checking for existing Alice voice clone...")
    response = requests.get("https://api.elevenlabs.io/v1/voices", headers=headers)
    voices = response.json().get("voices", [])

    for v in voices:
        if v.get("name") == "Alice":
            print(f"Found Alice! Voice ID: {v.get('voice_id')}")
            return v.get("voice_id")

    # 2. If not, create it
    print("Alice voice not found. Uploading alice_voice.wav to create clone...")
    url = "https://api.elevenlabs.io/v1/voices/add"
    data = {
      "name": "Alice",
      "description": "Tween bestie doll voice clone"
    }

    if not os.path.exists("alice_voice.wav"):
        print("Error: alice_voice.wav not found! Cannot clone voice.")
        return None

    with open("alice_voice.wav", "rb") as f:
        files = [
          ("files", ("alice_voice.wav", f, "audio/wav"))
        ]
        response = requests.post(url, headers=headers, data=data, files=files)

    if response.status_code == 200:
        voice_id = response.json().get("voice_id")
        print(f"Successfully created Alice clone! Voice ID: {voice_id}")
        return voice_id
    else:
        print(f"Failed to clone voice: {response.text}")
        return None

def generate_voice_audio(text, voice_id):
    if not voice_id:
        print("No valid voice_id provided, skipping audio generation.")
        return

    print("Generating audio response via ElevenLabs...")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        with open("response.mp3", "wb") as f:
            f.write(response.content)
        print("Success! Saved audio response as 'response.mp3' using Alice's cloned voice!")
    else:
        print(f"Failed to generate audio: {response.text}")

def run_pipeline(audio_file="test_audio.wav"):
    # 1. Setup speech recognition
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
        # COPPA Compliance: Delete collected audio data immediately
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

    # 2. Setup Offline Smart LLM (TinyLlama via Ollama)
    print("Loading TinyLlama Tween Bestie Model...")
    system_prompt = "You are a tween best friend. You love slang, you are very supportive, and you say things like 'OMG', 'Slay', 'No way', and 'Bestie'. Keep your answer very short, just one or two sentences. Do not be overly formal."

    # 3. Generate text
    print("Generating response...")
    try:
        response = ollama.chat(model='tinyllama', messages=[
          {'role': 'system', 'content': system_prompt},
          {'role': 'user', 'content': text_prompt},
        ])
        generated_text = response['message']['content'].strip()
    except Exception as e:
        generated_text = f"OMG bestie! I had a glitch: {e}"

    # 4. Explicit content filter for tweens
    safe_output = profanity.censor(generated_text)

    print("\n--- Final Safe Output ---")
    print(safe_output)
    print("-------------------------\n")

    # 5. Generate Tween Bestie Voice Output
    voice_id = get_or_create_alice_voice()
    generate_voice_audio(safe_output, voice_id)

if __name__ == "__main__":
    run_pipeline()