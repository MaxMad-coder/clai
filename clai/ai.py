import requests
from google import genai
from google.genai import types
from clai.config import load_config
from clai.memory import load_memory, format_memory_for_prompt

SYSTEM_PROMPT = """You are CLAI, a terminal assistant for developers.
Always give short, precise, terminal-friendly answers.
No long explanations. No markdown formatting.
If suggesting commands, put each command on its own line.
If given project memory, use it to give answers specific
to that project — not generic answers.
Be direct and helpful."""


def build_prompt(user_prompt: str, project_path: str = ".") -> str:
    """
    Build the full prompt by injecting project memory if available.
    """
    memory = load_memory(project_path)
    memory_context = format_memory_for_prompt(memory)

    if memory:
        return (
            f"{SYSTEM_PROMPT}\n\n"
            f"Project Memory:\n{memory_context}\n\n"
            f"User: {user_prompt}\n"
            f"CLAI:"
        )
    else:
        return (
            f"{SYSTEM_PROMPT}\n\n"
            f"No project memory found. Answering from general knowledge.\n\n"
            f"User: {user_prompt}\n"
            f"CLAI:"
        )


def send_to_llm(prompt: str, project_path: str = ".") -> str:
    """
    Main function called by all commands.
    Automatically picks Ollama or Gemini based on config.
    """
    config  = load_config()
    backend = config["backend"]

    if backend == "ollama":
        return ask_ollama(prompt, config, project_path)
    elif backend == "gemini":
        return ask_gemini(prompt, config, project_path)
    else:
        return f"Error: Unknown backend '{backend}'. Use 'ollama' or 'gemini'."


def ask_ollama(prompt: str, config: dict, project_path: str = ".") -> str:
    """Send prompt to local Ollama instance."""
    try:
        full_prompt = build_prompt(prompt, project_path)
        response = requests.post(
            config["ollama_url"],
            json={
                "model":  config["ollama_model"],
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


def ask_gemini(prompt: str, config: dict, project_path: str = ".") -> str:
    """Send prompt to Google Gemini API."""
    try:
        if not config["gemini_api_key"]:
            return "Error: Gemini API key not set. Run: python -m clai.main config --set-key YOUR_KEY"

        client      = genai.Client(api_key=config["gemini_api_key"])
        full_prompt = build_prompt(prompt, project_path)

        response = client.models.generate_content(
            model=config["gemini_model"],
            contents=full_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            )
        )
        return response.text

    except Exception as e:
        return f"Gemini error: {str(e)}"