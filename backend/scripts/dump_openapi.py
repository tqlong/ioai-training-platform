from __future__ import annotations

import json

from ioai.entrypoints.api.factory import create_app


OPENAPI_PATH = "backend/generated/openapi.json"


def main() -> None:
    app = create_app()
    payload = app.openapi()
    with open(OPENAPI_PATH, "w", encoding="utf-8") as stream:
        json.dump(payload, stream, sort_keys=True, indent=2)
        stream.write("\n")


if __name__ == "__main__":
    main()
