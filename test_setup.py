import os
import ollama
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def check_ollama():
    print("Checking Ollama (your local AI helper)...")
    try:
        response = ollama.chat(
            model = "llama3.2:1b",
            messages = [{"role": "user", "content": "Reply with exactly: OK"}],
        )
        answer = response["message"]["content"]
        print(f"✅ Ollama is working! It replied: {answer.strip()!r}")
        return True

    except Exception as e:
        print("❌ Ollama check failed.")
        print(f"   Error details: {e}")
        print("   Common fixes:")
        print("   - Is the Ollama app actually running? (it should be after install)")
        print("   - Did you run: ollama pull llama3.2:1b")
        print("   - Try running 'ollama list' in your terminal to see installed model")
        return False

def check_groq():
    print("\nChecking Groq (your cloud AI helper)...")
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key or api_key == "GROQ_API_KEY":
        print("❌ Groq check failed.")
        print("    No API key found. Did you:")
        print("    1. Copy .env.example to .env ?")
        print("    2. Paste your real key from https://console.groq.com/keys into it?")
        return False

    try:
        client = Groq(api_key = api_key)
        response = client.chat.completions.create(
            model = "openai/gpt-oss-120b",
            messages = [{"role": "user", "content": "Reply with exactly: OK"}],
        )
        answer = response.choices[0].message.content
        print(f"✅ Groq is working! It replied: {answer.strip()!r}")
        return True

    except Exception as e:
        print("❌ Groq check failed.")
        print(f"   Error details: {e}")
        print("   Common fixes:")
        print("   - Double-check the key was copied correctly (no extra spaces)")
        print("   - Make sure you're connected to the internet")
        return False


if __name__ == "__main__":
    print("-" * 50)
    print("SmartRoute-MCP - Phase 0 Setup Check")
    print("-" * 50 + "\n")

    ollama_ok = check_ollama()
    groq_ok = check_groq()

    print("\n" + "=" * 50)
    if ollama_ok and groq_ok:
        print("🎉 Your kitchen is ready. On to Phase 1: building the Router!")
    else:
        print("⚠️  Fix the ❌ items above, then run this script again.")
    print("=" * 50)


         
