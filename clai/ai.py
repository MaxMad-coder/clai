import requests
from google import genai
from google.genai import types
from clai.config import load_config

SYSTEM_PROMPT = """You are CLAI, a terminal assistant for developers.
Always give short, precise, terminal-friendly answers.
No long explanations. No markdown formatting.
If suggesting commands, put each command on its own line.
Be direct and helpful."""

# ── Ollama Backend ─────────────────────────────────────────────────────────

def ask_ollama(prompt: str, config: dict) -> str:
    """Send prompt to local Ollama instance."""
    try:
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {prompt}\nCLAI:"

        response = requests.post(
            config["ollama_url"],
            json={
                "model": config["ollama_model"],
                "prompt": full_prompt,
                "stream": False
            },
            timeout=120
        )
        return response.json()["response"]

    except requests.exceptions.ConnectionError:
        return "Error: Ollama is not running. Start it with: ollama serve"
    except requests.exceptions.Timeout:
        return "Error: Ollama took too long to respond. Try a smaller model."
    except Exception as e:
        return f"Ollama error: {str(e)}"

# ── Gemini Backend ─────────────────────────────────────────────────────────

def ask_gemini(prompt: str, config: dict) -> str:
    """Send prompt to Google Gemini API."""
    try:
        if not config["gemini_api_key"]:
            return "Error: Gemini API key not set. Run: python -m clai.main config --set-key YOUR_KEY"

        client = genai.Client(api_key=config["gemini_api_key"])
        response = client.models.generate_content(
		model_name=config["gemini_model"],
            	contents = prompt,
            	config = types.GenerateContentConfig(
                	system_instruction=SYSTEM_PROMPT
            ) 
	)
        return response.text

    except Exception as e:
        return f"Gemini error: {str(e)}"

# ── Main Entry Point ───────────────────────────────────────────────────────

def send_to_llm(prompt: str) -> str:
    """
    Main function called by all commands.
    Automatically picks Ollama or Gemini based on config.
    """
    config = load_config()
    backend = config["backend"]

    if backend == "ollama":
        return ask_ollama(prompt, config)
    elif backend == "gemini":
        return ask_gemini(prompt, config)
    else:
        return f"Error: Unknown backend '{backend}'. Use 'ollama' or 'gemini'."
