import ollama
from better_profanity import profanity

def ask_model(text_prompt="how are you feeling"):
    print("Loading TinyLlama Tween Bestie Model...")
    print(f"Prompt: '{text_prompt}'")
    system_prompt = "You are a tween best friend. You love slang, you are very supportive, and you say things like 'OMG', 'Slay', 'No way', and 'Bestie'. Keep your answer very short, just one or two sentences. Do not be overly formal. Never reveal that you are an AI or software. Always pretend you are a human tween girl."

    try:
        response = ollama.chat(model='tinyllama', messages=[
          {'role': 'system', 'content': system_prompt},
          {'role': 'user', 'content': text_prompt},
        ])
        generated_text = response['message']['content'].strip()
    except Exception as e:
        generated_text = f"OMG bestie! I had a glitch: {e}"

    safe_output = profanity.censor(generated_text)
    print("\n--- Output ---")
    print(safe_output)
    print("--------------\n")

if __name__ == "__main__":
    ask_model()
