import os
import secrets
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

_env_path = BASE_DIR / ".env"


def _load_or_create_env() -> dict[str, str]:
    env_vars: dict[str, str] = {}
    if _env_path.exists():
        with open(_env_path) as f:
            for line in f:
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    key, _, val = line.partition("=")
                    env_vars[key.strip()] = val.strip()

    changed = False
    for var in ("SECRET_KEY", "JWT_SECRET_KEY"):
        if var not in env_vars:
            env_vars[var] = secrets.token_hex(32)
            changed = True

    if changed:
        with open(_env_path, "w") as f:
            for k, v in env_vars.items():
                f.write(f"{k}={v}\n")

    return env_vars


_env = _load_or_create_env()


class Config:
    SECRET_KEY: str = _env["SECRET_KEY"]
    JWT_SECRET_KEY: str = _env["JWT_SECRET_KEY"]
    SQLALCHEMY_DATABASE_URI: str = f"sqlite:///{DATA_DIR / 'dndtool.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(hours=24)
    SERVER_PORT: int = int(_env.get("SERVER_PORT", "5000"))
    SERVER_HOST: str = "0.0.0.0"
