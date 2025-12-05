import os
from pathlib import Path


def get_plugin_path() -> Path:
    return Path(os.path.dirname(os.path.realpath(__file__)))
