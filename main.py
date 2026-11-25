"""Write this entry's one word for The Agent's Uh-Oh."""

import os
from pathlib import Path

WORD = "blanking"


def output_file() -> Path:
    root = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    return Path(root) / "entry.txt"


def entry_bytes(word: str = WORD) -> bytes:
    """Return the exact UTF-8 payload: one word, no newline, 1 to 99 characters."""
    if not word or word != word.strip() or any(character.isspace() for character in word):
        raise SystemExit("entry must be a single word with no surrounding space")
    if not 1 <= len(word) <= 99:
        raise SystemExit("entry must be 1 to 99 characters")
    return word.encode("utf-8")


def main() -> None:
    path = output_file()
    payload = entry_bytes()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


if __name__ == "__main__":
    main()
