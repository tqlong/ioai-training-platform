from __future__ import annotations

from pathlib import Path

from ioai.adapters.vocabulary.markdown_source import parse_vocabulary_markdown

VOCABULARY_SOURCE = Path("vocab.md")


def main() -> None:
    records = parse_vocabulary_markdown(VOCABULARY_SOURCE.read_text(encoding="utf-8"))
    print(f"Validated {len(records)} canonical vocabulary records")


if __name__ == "__main__":
    main()
