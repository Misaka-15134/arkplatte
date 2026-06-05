from __future__ import annotations

import warnings
from typing import Iterable, Literal, Sequence

from .data import operators, palettes


HexList = list[str]


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb: Iterable[float]) -> str:
    vals = [max(0, min(255, round(v))) for v in rgb]
    return "#{:02X}{:02X}{:02X}".format(*vals)


def _rgb_to_lab(color: str) -> tuple[float, float, float]:
    rgb = [x / 255 for x in _hex_to_rgb(color)]
    linear = [((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in rgb]
    x = 0.4124564 * linear[0] + 0.3575761 * linear[1] + 0.1804375 * linear[2]
    y = 0.2126729 * linear[0] + 0.7151522 * linear[1] + 0.0721750 * linear[2]
    z = 0.0193339 * linear[0] + 0.1191920 * linear[1] + 0.9503041 * linear[2]
    xyz = [x / 0.95047, y, z / 1.08883]
    f = [v ** (1 / 3) if v > 216 / 24389 else ((24389 / 27) * v + 16) / 116 for v in xyz]
    return (116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2]))


def _lab_to_hex(lab: Sequence[float]) -> str:
    l_val, a_val, b_val = lab
    y = (l_val + 16) / 116
    x = a_val / 500 + y
    z = y - b_val / 200

    def inv_f(v: float) -> float:
        cube = v**3
        return cube if cube > 216 / 24389 else (116 * v - 16) * 27 / 24389

    x, y, z = inv_f(x) * 0.95047, inv_f(y), inv_f(z) * 1.08883
    r_lin = 3.2404542 * x - 1.5371385 * y - 0.4985314 * z
    g_lin = -0.9692660 * x + 1.8760108 * y + 0.0415560 * z
    b_lin = 0.0556434 * x - 0.2040259 * y + 1.0572252 * z

    def gamma(v: float) -> float:
        v = max(0, min(1, v))
        return 1.055 * (v ** (1 / 2.4)) - 0.055 if v > 0.0031308 else 12.92 * v

    return _rgb_to_hex([gamma(r_lin) * 255, gamma(g_lin) * 255, gamma(b_lin) * 255])


def _lab_distance(a: str, b: str) -> float:
    lab_a = _rgb_to_lab(a)
    lab_b = _rgb_to_lab(b)
    return sum((x - y) ** 2 for x, y in zip(lab_a, lab_b, strict=True)) ** 0.5


def _chroma(lab: Sequence[float]) -> float:
    return (lab[1] ** 2 + lab[2] ** 2) ** 0.5


def _lab_adjust(color: str, lightness: float | None = None, chroma: float | None = None) -> str:
    l_val, a_val, b_val = _rgb_to_lab(color)
    old_chroma = _chroma((l_val, a_val, b_val))
    if chroma is not None and old_chroma > 0:
        scale = max(0, chroma) / old_chroma
        a_val *= scale
        b_val *= scale
    if lightness is not None:
        l_val = max(0, min(100, lightness))
    return _lab_to_hex((l_val, a_val, b_val))


def _blend_lab(a: str, b: str, amount: float) -> str:
    lab_a = _rgb_to_lab(a)
    lab_b = _rgb_to_lab(b)
    lab = tuple(x * (1 - amount) + y * amount for x, y in zip(lab_a, lab_b, strict=True))
    return _lab_to_hex(lab)


def _readable_on_white(colors: Sequence[str]) -> list[str]:
    visible = []
    colorful = []
    for color in colors:
        l_val, a_val, b_val = _rgb_to_lab(color)
        chroma = (a_val**2 + b_val**2) ** 0.5
        if 12 <= l_val <= 82:
            visible.append(color)
            if chroma >= 5:
                colorful.append(color)
    return colorful or visible or list(colors)


def _theme_candidate_pool(name: str, n: int) -> HexList:
    sample_n = max(24, min(240, n))
    colors: HexList = []
    colors.extend(palette(name))
    colors.extend(sequential(name, sample_n))
    colors.extend(diverging(name, sample_n))
    return list(dict.fromkeys(colors))


def _interpolate(colors: Sequence[str], n: int | None, space: Literal["rgb", "lab"] = "lab") -> HexList:
    unique = list(dict.fromkeys(colors))
    if n is None:
        return list(unique)
    if n <= len(unique):
        return list(unique[:n])
    values = [_hex_to_rgb(c) if space == "rgb" else _rgb_to_lab(c) for c in unique]
    out: HexList = []
    segments = len(values) - 1
    for idx in range(n):
        pos = idx / (n - 1) * segments
        left = min(int(pos), segments - 1)
        frac = pos - left
        value = tuple(values[left][j] * (1 - frac) + values[left + 1][j] * frac for j in range(3))
        out.append(_rgb_to_hex(value) if space == "rgb" else _lab_to_hex(value))
    return out


def _interpolate_monotone_lightness(colors: Sequence[str], n: int, descending: bool = True) -> HexList:
    if n <= 0:
        return []
    anchors = list(dict.fromkeys(colors))
    if len(anchors) == 1:
        return anchors * n
    base = _interpolate(anchors, n, space="lab")
    labs = [_rgb_to_lab(color) for color in base]
    start_l = labs[0][0]
    end_l = labs[-1][0]
    if descending and start_l < end_l:
        start_l, end_l = end_l, start_l
    if not descending and start_l > end_l:
        start_l, end_l = end_l, start_l
    out: HexList = []
    for idx, lab in enumerate(labs):
        t = idx / max(1, n - 1)
        smooth = t * t * (3 - 2 * t)
        target_l = start_l * (1 - smooth) + end_l * smooth
        out.append(_lab_to_hex((target_l, lab[1], lab[2])))
    return out


def _core_hexes_by_role(rows: Sequence[dict[str, str]]) -> dict[str, str]:
    return {row["role"]: row["hex"] for row in rows}


def _farthest_colors(candidates: Sequence[str], n: int, seed_color: str | None = None) -> HexList:
    colors = list(dict.fromkeys(candidates))
    if n <= 0:
        return []
    if n >= len(colors):
        return colors
    if seed_color and seed_color in colors:
        selected = [seed_color]
    else:
        selected = [max(colors, key=lambda c: _rgb_to_lab(c)[0])]
    while len(selected) < n:
        remaining = [c for c in colors if c not in selected]
        next_color = max(remaining, key=lambda c: min(_lab_distance(c, s) for s in selected))
        selected.append(next_color)
    return selected


def _match_operator(name: str) -> dict[str, str]:
    key = str(name)
    key_lower = key.lower()
    hits = [
        op
        for op in operators()
        if op["name_cn"] == key or op["operator_id"] == key or op["name_key"].lower() == key_lower
    ]
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        raise ValueError(f"查询匹配到多个干员：{key}")
    candidates = [op["name_cn"] for op in operators() if key in op["name_cn"]]
    suffix = f"。候选：{'、'.join(candidates[:8])}" if candidates else ""
    raise KeyError(f"未找到干员：{key}{suffix}")


def names(rarity: int | None = None) -> list[str]:
    rows = operators()
    if rarity is not None:
        rows = [op for op in rows if int(op["rarity"]) == rarity]
    return [op["name_cn"] for op in rows]


def info(name: str) -> dict[str, str]:
    return dict(_match_operator(name))


def _core_rows(name: str) -> list[dict[str, str]]:
    op = _match_operator(name)
    rows = [
        row
        for row in palettes()
        if row["operator_id"] == op["operator_id"] and row["palette_type"] == "core"
    ]
    return sorted(rows, key=lambda row: int(row["rank"]))


def _theme_color(name: str) -> str:
    rows = _core_rows(name)
    by_role = {row["role"]: row["hex"] for row in rows}
    return by_role.get("theme") or rows[0]["hex"]


def palette(name: str, n: int | None = None, kind: Literal["core", "sequential", "diverging"] = "core") -> HexList:
    if kind == "sequential":
        return sequential(name, 256 if n is None else n)
    if kind == "diverging":
        return diverging(name, 257 if n is None else n)
    rows = _core_rows(name)
    return _interpolate([row["hex"] for row in rows], n)


def sequential(name: str, n: int = 256) -> HexList:
    rows = _core_rows(name)
    by_role = _core_hexes_by_role(rows)
    light = by_role.get("light") or max(rows, key=lambda row: float(row["lab_l"]))["hex"]
    dark = by_role.get("dark") or min(rows, key=lambda row: float(row["lab_l"]))["hex"]
    theme = by_role["theme"]
    light_lab = _rgb_to_lab(light)
    dark_lab = _rgb_to_lab(dark)
    theme_lab = _rgb_to_lab(theme)
    light_anchor = _blend_lab(light, "#FAFAF7", 0.38 if light_lab[0] < 88 else 0.18)
    dark_anchor = _lab_adjust(dark, lightness=min(dark_lab[0], 28), chroma=max(_chroma(dark_lab), _chroma(theme_lab) * 0.65))
    anchors = sorted([light_anchor, theme, dark_anchor], key=lambda color: _rgb_to_lab(color)[0], reverse=True)
    return _interpolate_monotone_lightness(anchors, n, descending=True)


def diverging(name: str, n: int = 257) -> HexList:
    rows = _core_rows(name)
    by_role = _core_hexes_by_role(rows)
    theme = by_role["theme"]
    theme_lab = _rgb_to_lab(theme)
    accent_candidates = [
        row["hex"]
        for row in rows
        if row["role"] not in {"theme", "neutral", "light"} and row["hex"] != theme
    ]
    if not accent_candidates:
        accent_candidates = [by_role.get("accent_1") or by_role.get("accent_2") or by_role.get("dark") or theme]
    accent = max(
        accent_candidates,
        key=lambda color: _lab_distance(color, theme) + _chroma(_rgb_to_lab(color)) * 0.2,
    )
    accent_lab = _rgb_to_lab(accent)
    endpoint_l = min(58, max(42, (theme_lab[0] + accent_lab[0]) / 2))
    endpoint_chroma = min(64, max(28, min(_chroma(theme_lab), _chroma(accent_lab)) * 0.92))
    left = _lab_adjust(accent, lightness=endpoint_l, chroma=max(endpoint_chroma, _chroma(accent_lab) * 0.82))
    right = _lab_adjust(theme, lightness=endpoint_l, chroma=max(endpoint_chroma, _chroma(theme_lab) * 0.82))
    neutral = by_role.get("neutral")
    center = _blend_lab(neutral, "#F5F4F0", 0.72) if neutral else "#F5F4F0"
    center = _lab_adjust(center, lightness=94, chroma=min(_chroma(_rgb_to_lab(center)), 4))
    if n <= 1:
        return [center][:n]
    if n % 2 == 1:
        side = n // 2 + 1
        left_half = _interpolate_monotone_lightness([left, center], side, descending=False)
        right_half = _interpolate_monotone_lightness([center, right], side, descending=True)
        return left_half[:-1] + right_half
    side = n // 2
    left_half = _interpolate_monotone_lightness([left, center], side, descending=False)
    right_half = _interpolate_monotone_lightness([center, right], side, descending=True)
    return left_half + right_half


def operator_colors(operator_names: Sequence[str]) -> dict[str, str]:
    return {name: _theme_color(name) for name in operator_names}


def category(
    n: int,
    seed: int | None = None,
    large_n: Literal["warn", "grouped", "force"] = "warn",
    optimize: bool = True,
) -> HexList:
    if n > 30 and large_n == "warn":
        warnings.warn("分类数量超过 30，建议切换到分组、分面或上层注释模式。", stacklevel=2)
    anchors = [
        row
        for row in palettes()
        if row["palette_type"] == "categorical_anchor"
    ]
    anchors = sorted(anchors, key=lambda row: row["operator_id"])
    colors = [row["hex"] for row in anchors]
    if seed is not None:
        shift = seed % len(colors)
        colors = colors[shift:] + colors[:shift]
    if optimize:
        return _farthest_colors(colors, n, seed_color=colors[0] if colors else None)
    if n <= len(colors):
        return colors[:n]
    return _interpolate(colors, n)


def celltype_colors(celltypes: Iterable[str], seed: int | None = 1, large_n: str = "warn") -> dict[str, str]:
    levels = list(dict.fromkeys(str(x) for x in celltypes))
    colors = category(len(levels), seed=seed, large_n=large_n)  # type: ignore[arg-type]
    return dict(zip(levels, colors, strict=True))


def themed_subtype_colors(
    subtype_map: dict[str, Sequence[str]],
    group_operator: dict[str, str],
    candidates_per_group: int = 96,
) -> dict[str, str]:
    result: dict[str, str] = {}
    for group, subtypes in subtype_map.items():
        operator = group_operator[group]
        subtype_count = len(subtypes)
        candidates = _theme_candidate_pool(operator, max(candidates_per_group, subtype_count * 18))
        theme = _theme_color(operator)
        pool = _readable_on_white(candidates)
        picked = _farthest_colors(pool, len(subtypes), seed_color=theme if theme in pool else None)
        for subtype, color in zip(subtypes, picked, strict=True):
            result[str(subtype)] = color
    return result


def to_mpl_cmap(name: str, kind: Literal["sequential", "diverging"] = "sequential", n: int = 256):
    try:
        from matplotlib.colors import LinearSegmentedColormap
    except ImportError as exc:
        raise ImportError("需要安装 matplotlib 才能创建 matplotlib 色图。") from exc
    colors = sequential(name, n) if kind == "sequential" else diverging(name, n)
    return LinearSegmentedColormap.from_list(f"arknights_{name}_{kind}", colors, N=n)


def arkplatte(name: str, n: int | None = None, kind: Literal["core", "seq", "div"] = "core") -> HexList:
    kind_map = {"core": "core", "seq": "sequential", "div": "diverging"}
    return palette(name, n=n, kind=kind_map[kind])  # type: ignore[arg-type]


def arkplatte_seq(name: str, n: int = 256) -> HexList:
    return sequential(name, n)


def arkplatte_div(name: str, n: int = 257) -> HexList:
    return diverging(name, n)


def arkplatte_cat(
    n: int,
    seed: int | None = None,
    large_n: Literal["warn", "grouped", "force"] = "warn",
    optimize: bool = True,
) -> HexList:
    return category(n, seed=seed, large_n=large_n, optimize=optimize)


def arkplatte_cell(celltypes: Iterable[str], seed: int | None = 1, large_n: str = "warn") -> dict[str, str]:
    return celltype_colors(celltypes, seed=seed, large_n=large_n)


def arkplatte_sub(
    subtype_map: dict[str, Sequence[str]],
    group_operator: dict[str, str],
    candidates_per_group: int = 96,
) -> dict[str, str]:
    return themed_subtype_colors(subtype_map, group_operator, candidates_per_group=candidates_per_group)


def arkplatte_names(rarity: int | None = None) -> list[str]:
    return names(rarity=rarity)


def arkplatte_info(name: str) -> dict[str, str]:
    return info(name)


def arkplatte_theme(operator_names: Sequence[str]) -> dict[str, str]:
    return operator_colors(operator_names)


def arkplatte_cmap(name: str, kind: Literal["seq", "div"] = "seq", n: int = 256):
    cmap_kind = "sequential" if kind == "seq" else "diverging"
    return to_mpl_cmap(name, kind=cmap_kind, n=n)
