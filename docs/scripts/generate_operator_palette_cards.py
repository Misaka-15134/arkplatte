from __future__ import annotations

import csv
import io
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = ROOT / "arknights_palette"
DATA_ROOT = PACKAGE_ROOT / "arknights_palette" / "data"
FIGURE_DIR = Path(__file__).resolve().parents[1] / "figures" / "operator_palettes"
sys.path.insert(0, str(PACKAGE_ROOT))

import arknights_palette as akp  # noqa: E402


OPERATORS = [
    "cello",
    "skadi2",
    "mlyss",
    "wisdel",
    "ling",
    "shu",
    "logos",
    "surtr",
    "mlynar",
    "kalts",
    "mizuki",
    "archet",
]

ROLE_LABELS = {
    "theme": "主题",
    "accent_1": "强调1",
    "accent_2": "强调2",
    "dark": "深色",
    "light": "浅色",
    "neutral": "中性",
    "support_7": "辅助7",
    "support_8": "辅助8",
}


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def load_rows() -> tuple[dict[str, dict[str, str]], dict[str, list[dict[str, str]]]]:
    with (DATA_ROOT / "operators.csv").open(encoding="utf-8", newline="") as handle:
        operators = {row["name_key"]: row for row in csv.DictReader(handle)}
    palette_rows: dict[str, list[dict[str, str]]] = {}
    with (DATA_ROOT / "palettes.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["palette_type"] == "core":
                palette_rows.setdefault(row["operator_id"], []).append(row)
    for rows in palette_rows.values():
        rows.sort(key=lambda row: int(row["rank"]))
    return operators, palette_rows


def fetch_portrait(url: str) -> Image.Image:
    with urllib.request.urlopen(url, timeout=30) as response:
        data = response.read()
    image = Image.open(io.BytesIO(data)).convert("RGBA")
    bbox = image.getbbox()
    if bbox:
        image = image.crop(bbox)
    return image


def fit_image(image: Image.Image, box: tuple[int, int]) -> Image.Image:
    width, height = box
    scale = min(width / image.width, height / image.height)
    size = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
    return image.resize(size, Image.Resampling.LANCZOS)


def text_color(hex_color: str) -> str:
    rgb = tuple(int(hex_color[i : i + 2], 16) for i in (1, 3, 5))
    luminance = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
    return "#111111" if luminance > 155 else "#FFFFFF"


def draw_card(op: dict[str, str], colors: list[dict[str, str]], index: int) -> Path:
    output = FIGURE_DIR / f"{index:02d}-{op['name_key']}.png"
    if output.exists():
        portrait = Image.open(output).convert("RGBA").crop((22, 60, 252, 270))
    else:
        portrait = fetch_portrait(op["portrait_source"])
    canvas = Image.new("RGB", (620, 300), "#FFFFFF")
    draw = ImageDraw.Draw(canvas)
    title_font = load_font(24, bold=True)
    sub_font = load_font(13)
    mono_font = load_font(12)

    draw.rounded_rectangle((10, 10, 610, 290), radius=16, fill="#FAFAFA", outline="#E2E5EA", width=1)
    name = op["name_cn"]
    title_box = draw.textbbox((0, 0), name, font=title_font)
    draw.text(((620 - (title_box[2] - title_box[0])) / 2, 24), name, fill="#161A1D", font=title_font)

    image_box = (24, 60, 250, 270)
    swatch_left = 286
    swatch_top = 60
    swatch_w = 294
    swatch_h = 21
    swatch_gap = 6

    draw.rounded_rectangle(image_box, radius=12, fill="#F0F2F5")
    fitted = fit_image(portrait, (image_box[2] - image_box[0] - 12, image_box[3] - image_box[1] - 12))
    x = image_box[0] + (image_box[2] - image_box[0] - fitted.width) // 2
    y = image_box[1] + (image_box[3] - image_box[1] - fitted.height) // 2
    canvas.paste(fitted, (x, y), fitted)

    for idx, row in enumerate(colors):
        y0 = swatch_top + idx * (swatch_h + swatch_gap)
        color = row["hex"]
        role = ROLE_LABELS.get(row["role"], row["role"])
        draw.rounded_rectangle((swatch_left, y0, swatch_left + swatch_w, y0 + swatch_h), radius=5, fill=color)
        draw.text((swatch_left + 10, y0 + 3), role, fill=text_color(color), font=sub_font)
        draw.text((swatch_left + 204, y0 + 4), color, fill=text_color(color), font=mono_font)

    canvas.save(output, dpi=(180, 180))
    return output


def main() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    operators, palette_rows = load_rows()
    written = []
    for index, key in enumerate(OPERATORS, start=1):
        op = operators[key]
        rows = palette_rows[op["operator_id"]]
        written.append(draw_card(op, rows[:8], index))
    for path in written:
        print(path.as_posix())


if __name__ == "__main__":
    main()
