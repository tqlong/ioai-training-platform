from __future__ import annotations

import argparse
from pathlib import Path

from ioai.adapters.vocabulary.artifact_contract import ARTIFACT_PATH
from ioai.adapters.vocabulary.generation import (
    build_vocabulary_artifact,
    check_vocabulary_drift,
    render_vocabulary_artifact,
)

SOURCE_PATH = Path("vocab.md")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate canonical vocabulary data")
    parser.add_argument(
        "--check", action="store_true", help="fail when artifact drifts"
    )
    arguments = parser.parse_args()
    source = SOURCE_PATH.read_text(encoding="utf-8")

    if arguments.check:
        check_vocabulary_drift(source, ARTIFACT_PATH.read_text(encoding="utf-8"))
        print("Canonical vocabulary artifact is current")
        return

    artifact = render_vocabulary_artifact(build_vocabulary_artifact(source))
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(artifact, encoding="utf-8")
    print(f"Generated {ARTIFACT_PATH}")


if __name__ == "__main__":
    main()
