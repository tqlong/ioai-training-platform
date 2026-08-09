from __future__ import annotations

import argparse
import json
from pathlib import Path

from ioai.entrypoints.api.factory import create_app

OPENAPI_PATH = Path("backend/generated/openapi.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic OpenAPI")
    parser.add_argument("--output", type=Path, default=OPENAPI_PATH)
    arguments = parser.parse_args()
    app = create_app()
    payload = app.openapi()
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    with arguments.output.open("w", encoding="utf-8") as stream:
        json.dump(payload, stream, sort_keys=True, indent=2)
        stream.write("\n")


if __name__ == "__main__":
    main()
