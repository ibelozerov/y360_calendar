import json
from pathlib import Path
from dataclasses import dataclass

CONFIG_DIR = Path.home() / ".y360_calendar"
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class AppConfig:
    client_id: str
    client_secret: str
    org_id: str


def config_exists() -> bool:
    return CONFIG_FILE.exists()


def load_config() -> AppConfig:
    data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    return AppConfig(**data)


def save_config(config: AppConfig) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps(
            {"client_id": config.client_id, "client_secret": config.client_secret, "org_id": config.org_id},
            indent=2,
        ),
        encoding="utf-8",
    )
