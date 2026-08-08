from __future__ import annotations

from alembic.config import Config
from alembic.script import ScriptDirectory


ALEMBIC_INI_PATH = "backend/alembic.ini"


def main() -> None:
    config = Config(ALEMBIC_INI_PATH)
    script = ScriptDirectory.from_config(config)
    heads = script.get_current_head()
    if not heads:
        raise RuntimeError("No alembic heads found")


if __name__ == "__main__":
    main()
