import os
try:
    import tomllib          # Python 3.11+
except ImportError:
    import tomli as tomllib
from pathlib import Path

CONFIG_DIR  = Path.home() / ".clai"
CONFIG_FILE = CONFIG_DIR / "config.toml"

DEFAULT_CONFIG = {
    "backend": "ollama",
    "ollama_model": "mistral",          # ← changed from llama3 to mistral
    "ollama_url": "http://localhost:11434/api/generate",
    "gemini_api_key": "",
    "gemini_model": "gemini-1.5-flash"
}

def load_config() -> dict:
    """Load config from ~/.clai/config.toml, or return defaults."""
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()

    with open(CONFIG_FILE, "rb") as f:
        user_config = tomllib.load(f)

    merged = DEFAULT_CONFIG.copy()
    merged.update(user_config)
    return merged

def save_config(config: dict):
    """Save config to ~/.clai/config.toml"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    with open(CONFIG_FILE, "w") as f:
        f.write(f'backend = "{config["backend"]}"\n')
        f.write(f'ollama_model = "{config["ollama_model"]}"\n')
        f.write(f'ollama_url = "{config["ollama_url"]}"\n')
        f.write(f'gemini_api_key = "{config["gemini_api_key"]}"\n')
        f.write(f'gemini_model = "{config["gemini_model"]}"\n')

def set_backend(backend: str):
    """Switch between ollama and gemini."""
    config = load_config()
    config["backend"] = backend
    save_config(config)

def set_gemini_key(api_key: str):
    """Save the Gemini API key."""
    config = load_config()
    config["gemini_api_key"] = api_key
    save_config(config)
