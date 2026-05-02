from __future__ import annotations

from time import sleep

from google import genai
from google.genai import errors, types

import ollama

from config import Config
from core import Book

_CHARS_PER_TOKEN = 3
_GEMINI_TOKEN_LIMIT = 250_000
_REQUEST_INTERVAL = 15      # seconds between requests on the free Gemini tier
_MAX_SERVER_ERRORS = 5


EMBEDDING_MODEL = 'hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'
LANGUAGE_MODEL = 'hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF'

def _char_limit(config: Config) -> int:
    return _GEMINI_TOKEN_LIMIT * _CHARS_PER_TOKEN


def query_gemini(query: str) -> str:
    """Sends a query to Gemini 2.5 Flash and returns the response text."""
    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=query,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        ),
    )
    return response.text


def query_local(query: str, config: Config) -> str:
    """Sends a query to the local llama.cpp model and returns the response text."""
    if config.local_model_path is None:
        raise FileNotFoundError("No local model path configured.")
    # Deferred import — llama_cpp is an optional heavy dependency
    from llama_cpp import Llama  # type: ignore[import]

    llm = Llama(
        model_path=str(config.local_model_path),
        n_gpu_layers=config.gpu_layers,
        n_ctx=config.context_window,
    )
    response = llm(query, max_tokens=None, stop=None, echo=False)
    return response["choices"][0]["text"]


def get_summary(text: str, prompt: str, config: Config) -> str:
    """Returns an LLM-generated summary of *text* using *prompt* as the prefix."""
    query = prompt + text
    if config.use_local_model:
        return query_local(query, config)
    return query_gemini(query)


# ── Book chunking ─────────────────────────────────────────────────────────────

def _split_text(text: str, char_limit: int) -> list[str]:
    """Splits *text* into a list of strings each no longer than *char_limit*."""
    return [text[i : i + char_limit] for i in range(0, len(text), char_limit)]


def chunk_book_by_chapter(book: Book, char_limit: int) -> list[str]:
    """Splits a book's chapters into chunks that fit within *char_limit* characters.

    Chapters that are individually larger than *char_limit* are split further.
    """
    chunks: list[str] = [""]
    for i in range(book.length):
        chapter = book.chapter_text(i)
        if len(chapter) > char_limit:
            # Oversized chapter — split it first, then pack the pieces
            for piece in _split_text(chapter, char_limit):
                if len(chunks[-1]) + len(piece) > char_limit:
                    chunks.append("")
                chunks[-1] += piece
        elif len(chunks[-1]) + len(chapter) > char_limit:
            chunks.append(chapter)
        else:
            chunks[-1] += chapter
    return [c for c in chunks if c.strip()]


# ── RAG Model ─────────────────────────────────────────────────────────────────

vector_db = []
def create_chunk_key(text: str):
    embedding = ollama.embed(model=EMBEDDING_MODEL,input=text)




# ── High-level summarisation ──────────────────────────────────────────────────

def summarise_book(
    book: Book,
    chunk_prompt: str,
    combine_prompt: str,
    config: Config,
) -> str:
    """Generates a full-book summary.

    Steps:
      1. Split the book into context-window-sized chunks.
      2. Summarise each chunk individually.
      3. Combine all chunk summaries into one final summary.
    """
    char_limit = _char_limit(config)
    chunks = chunk_book_by_chapter(book, char_limit)
    total = len(chunks)
    print(f"Summarising {total} chunk(s). This may take a while...")

    part_summaries: list[str] = []
    server_error_count = 0

    for i, chunk in enumerate(chunks, start=1):
        print(f"  Processing chunk {i}/{total}...")
        try:
            summary = get_summary(chunk, chunk_prompt, config)
        except errors.ServerError:
            server_error_count += 1
            if server_error_count >= _MAX_SERVER_ERRORS:
                ans = input(
                    f"{_MAX_SERVER_ERRORS} server errors encountered. Continue? (y/n): "
                )
                if ans.strip().lower() != "y":
                    raise
            print("Server error — waiting 60 s before retrying...")
            sleep(60)
            summary = get_summary(chunk, chunk_prompt, config)

        part_summaries.append(summary)
        if i < total:
            sleep(_REQUEST_INTERVAL)

    combined = "\n\n".join(part_summaries)
    print("Generating final combined summary...")
    return get_summary(combined, combine_prompt, config)
