from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).parent
EBOOKS_DIR = _ROOT / "ebooks"
LLM_DIR = _ROOT / "llm_models"
PROMPTS_DIR = _ROOT / "Prompts"
ENV_FILE = _ROOT / ".env"


@dataclass(frozen=True)
class Config:
    api_key: str
    context_window: int
    use_local_model: bool
    gpu_layers: int
    local_model_path: Path | None
    prompts: dict[str, str] = field(default_factory=dict)


def _ensure_dirs() -> None:
    for directory in (EBOOKS_DIR, LLM_DIR, PROMPTS_DIR):
        directory.mkdir(exist_ok=True)


def _load_prompts() -> dict[str, str]:
    if not PROMPTS_DIR.exists():
        return {}
    return {
        p.stem: p.read_text(encoding="utf-8")
        for p in PROMPTS_DIR.glob("*.txt")
    }


def _find_local_model() -> Path | None:
    """Returns the path to a .gguf model in llm_models/, prompting if there are multiple."""
    models = list(LLM_DIR.glob("*.gguf"))
    if not models:
        return None
    if len(models) == 1:
        return models[0]
    print("Multiple local models found. Select one:")
    for i, m in enumerate(models, start=1):
        print(f"  {i}. {m.name}")
    # Lazy import to avoid a circular dependency at module load time
    from ui import get_int
    idx = get_int("> ", min_val=0, max_val=len(models) + 1) - 1
    return models[idx]


def _prompt_for_env() -> None:
    """Interactively creates a .env file."""
    api_key = input("Enter your Gemini API key: ").strip()
    use_local = input("Use a local model instead of Gemini? (y/n): ").strip().lower() == "y"
    use_gpu = input("Enable GPU acceleration for local model? (y/n): ").strip().lower() == "y"
    ENV_FILE.write_text(
        f'GEMINI_API_KEY = "{api_key}"\n'
        f"CONTEXT_WINDOW = 130000\n"
        f"USE_LOCAL_MODEL = {str(use_local).lower()}\n"
        f"USE_GPU = {str(use_gpu).lower()}\n",
        encoding="utf-8",
    )
    print(".env file created.")


def load_config() -> Config:
    """Loads configuration from disk, creating .env if it does not exist."""
    _ensure_dirs()

    if not ENV_FILE.exists():
        print("No .env file found.")
        _prompt_for_env()

    load_dotenv(ENV_FILE)

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. Please add it to your .env file."
        )

    context_window = int(os.getenv("CONTEXT_WINDOW", "130000"))
    use_local_model = os.getenv("USE_LOCAL_MODEL", "false").lower() == "true"
    use_gpu = os.getenv("USE_GPU", "false").lower() == "true"
    gpu_layers = -1 if use_gpu else 0

    local_model_path: Path | None = None
    if use_local_model:
        local_model_path = _find_local_model()
        if local_model_path is None:
            print(
                "No .gguf model found in llm_models/. Falling back to Gemini API.\n"
                "See README.md for recommended models."
            )
            use_local_model = False

    return Config(
        api_key=api_key,
        context_window=context_window,
        use_local_model=use_local_model,
        gpu_layers=gpu_layers,
        local_model_path=local_model_path,
        prompts=_load_prompts(),
    )
