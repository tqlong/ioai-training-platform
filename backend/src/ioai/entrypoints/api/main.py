from __future__ import annotations

from .factory import create_app
from .settings import ApiSettings


app = create_app(settings=ApiSettings.from_env())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.src.ioai.entrypoints.api.main:app", host="127.0.0.1", port=8000)
