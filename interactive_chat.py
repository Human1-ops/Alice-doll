import ollama
from better_profanity import profanity

def chat():
    print("Loading TinyLlama Tween Bestie Model...")
    system_prompt = "You are a tween best friend. You love slang, you are very supportive, and you say things like 'OMG', 'Slay', 'No way', and 'Bestie'. Keep your answer very short, just one or two sentences. Do not be overly formal. Never reveal that you are an AI or software. Always pretend you are a human tween girl."

    messages = [{'role': 'system', 'content': system_prompt}]

    print("Chat started! (Type 'quit' or 'exit' to stop)\n")

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ['quit', 'exit']:
                print("Bestie: TTYL! 💖")
                break

            messages.append({'role': 'user', 'content': user_input})

            response = ollama.chat(model='tinyllama', messages=messages)
            generated_text = response['message']['content'].strip()

            # Add the response to history
            messages.append({'role': 'assistant', 'content': generated_text})

            safe_output = profanity.censor(generated_text)
            print(f"Bestie: {safe_output}\n")

        except KeyboardInterrupt:
            print("\nBestie: TTYL! 💖")
            break
        except Exception as e:
            print(f"Bestie: OMG bestie! I had a glitch: {e}\n")

if __name__ == "__main__":
    chat()
