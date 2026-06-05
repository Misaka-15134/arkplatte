from __future__ import annotations

import csv
import json
from functools import lru_cache
from importlib.resources import files
from typing import Any


def _resource_text(filename: str) -> str:
    return files("arknights_palette").joinpath("data", filename).read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def operators() -> list[dict[str, str]]:
    text = _resource_text("operators.csv")
    return list(csv.DictReader(text.splitlines()))


@lru_cache(maxsize=1)
def palettes() -> list[dict[str, str]]:
    text = _resource_text("palettes.csv")
    return list(csv.DictReader(text.splitlines()))


@lru_cache(maxsize=1)
def manifest() -> dict[str, Any]:
    return json.loads(_resource_text("palette_manifest.json"))

