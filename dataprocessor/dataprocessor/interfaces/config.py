import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    data_dir: Path


def obter_settings() -> Settings:
    return Settings(data_dir=Path(os.environ.get("DATAPROCESSOR_DATA_DIR", "data")))
