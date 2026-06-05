from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = ROOT / "arknights_palette"
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
FIGURE_DIR = Path(__file__).resolve().parents[1] / "figures"
sys.path.insert(0, str(PACKAGE_ROOT))

import arknights_palette as akp  # noqa: E402


CDN = "https://datasets.cellxgene.cziscience.com/"
DATA = {
    "lung10k": "c88e0403-da93-40f4-99b5-f5fdeb81a82c.h5ad",
    "kidney50k": "7dafa492-6129-4dff-a794-17bdefde3575.h5ad",
}

DEFAULT_OPERATOR_CYCLE = [
    "凯尔希",
    "浊心斯卡蒂",
    "塑心",
    "乌尔比安",
    "缪尔赛思",
    "令",
    "黍",
    "维什戴尔",
    "丰川祥子",
    "玛恩纳",
    "蕾缪安",
    "新约能天使",
    "望",
    "史尔特尔",
    "空弦",
    "水月",
    "逻各斯",
]
DATASET_OPERATOR_MAP = {
    "lung10k": {
        "endothelial": "凯尔希",
        "epithelial": "浊心斯卡蒂",
        "immune": "塑心",
        "stromal": "乌尔比安",
    },
    "kidney50k": {
        "PT": "缪尔赛思",
        "lymphoid": "令",
        "myeloid": "黍",
        "non_PT": "维什戴尔",
    },
}
DATASET_OPERATOR_POOL = {
    "lung10k": [
        "凯尔希",
        "浊心斯卡蒂",
        "塑心",
        "乌尔比安",
        "丰川祥子",
        "玛恩纳",
        "蕾缪安",
        "新约能天使",
        "望",
        "史尔特尔",
        "空弦",
        "水月",
        "逻各斯",
    ],
    "kidney50k": [
        "缪尔赛思",
        "令",
        "黍",
        "维什戴尔",
        "丰川祥子",
        "玛恩纳",
        "蕾缪安",
        "新约能天使",
        "望",
        "史尔特尔",
        "空弦",
        "水月",
        "逻各斯",
    ],
}
OPERATOR_LABEL = {
    "凯尔希": "凯尔希",
    "浊心斯卡蒂": "浊心斯卡蒂",
    "塑心": "塑心",
    "乌尔比安": "乌尔比安",
    "缪尔赛思": "缪尔赛思",
    "令": "令",
    "黍": "黍",
    "维什戴尔": "维什戴尔",
    "丰川祥子": "丰川祥子",
    "玛恩纳": "玛恩纳",
    "蕾缪安": "蕾缪安",
    "新约能天使": "新约能天使",
    "望": "望",
    "史尔特尔": "史尔特尔",
    "空弦": "空弦",
    "水月": "水月",
    "逻各斯": "逻各斯",
}


def require_omicverse():
    try:
        import omicverse as ov
    except ImportError as exc:
        raise ImportError("请先安装 omicverse，然后运行本脚本。") from exc
    return ov


def fetch(ov, key: str) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    local = DATA_DIR / f"{key}.h5ad"
    if not local.exists():
        ov.datasets.download_data(CDN + DATA[key], str(local))
    return local


def normalize_lung10k(adata):
    adata.obs["age"] = adata.obs["development_stage"].astype(str).str.replace("-year-old stage", "y", regex=False)
    return adata


def describe_adata(adata, dataset: str, coarse_col: str, fine_col: str) -> None:
    obs_columns = list(map(str, adata.obs.columns))
    preview_columns = [col for col in [coarse_col, fine_col, "donor_id", "sex", "age", "tissue", "cell_state"] if col in adata.obs]
    print(f"\n[{dataset}] adata")
    print(adata)
    print(f"[{dataset}] obs columns: {obs_columns[:18]}{' ...' if len(obs_columns) > 18 else ''}")
    print(f"[{dataset}] obs preview:")
    print(adata.obs[preview_columns].head(5).to_string())
    print(f"[{dataset}] {coarse_col} counts:")
    print(adata.obs[coarse_col].astype(str).value_counts().to_string())
    print(f"[{dataset}] {fine_col} count: {adata.obs[fine_col].astype(str).nunique()}")


def assign_fine_operators(
    subtype_map: dict[str, list[str]],
    group_operator: dict[str, str],
    operator_pool: list[str],
) -> dict[str, str]:
    fine_operator: dict[str, str] = {}
    for group in sorted(subtype_map):
        main_operator = group_operator[group]
        candidates = [main_operator] + [operator for operator in operator_pool if operator != main_operator]
        for index, subtype in enumerate(sorted(subtype_map[group])):
            fine_operator[subtype] = candidates[index % len(candidates)]
    return fine_operator


def palette_report(dataset: str, palettes: dict) -> None:
    coarse_labels = {
        group: OPERATOR_LABEL.get(operator, operator)
        for group, operator in palettes["group_operator"].items()
    }
    fine_labels = {
        fine: OPERATOR_LABEL.get(operator, operator)
        for fine, operator in palettes["fine_operator"].items()
    }
    print(f"\n[{dataset}] coarse group operator map:")
    print(coarse_labels)
    print(f"[{dataset}] fine cell-type operator map:")
    print(fine_labels)
    print(f"[{dataset}] fine_colors:")
    print(palettes["fine_colors"])
    print(f"[{dataset}] cluster_palette:")
    print(palettes["cluster_palette"])
    print(f"[{dataset}] track_palette preview:")
    print(palettes["track_palette"][:20])


def build_hierarchical_palettes(adata, dataset: str, coarse_col: str, fine_col: str):
    fine_to_coarse: dict[str, str] = {}
    for fine in sorted(adata.obs[fine_col].astype(str).unique()):
        subset = adata.obs.loc[adata.obs[fine_col].astype(str) == fine, coarse_col].astype(str)
        fine_to_coarse[fine] = subset.value_counts().idxmax()

    coarse_values = sorted(set(fine_to_coarse.values()))
    preset = DATASET_OPERATOR_MAP.get(dataset, {})
    fallback = [operator for operator in DEFAULT_OPERATOR_CYCLE if operator not in preset.values()]
    group_operator: dict[str, str] = {}
    for index, group in enumerate(coarse_values):
        group_operator[group] = preset.get(group, fallback[index % len(fallback)])

    subtype_map: dict[str, list[str]] = defaultdict(list)
    for fine, coarse in fine_to_coarse.items():
        subtype_map[coarse].append(fine)

    operator_pool = DATASET_OPERATOR_POOL.get(dataset, DEFAULT_OPERATOR_CYCLE)
    fine_operator = assign_fine_operators(dict(subtype_map), group_operator, operator_pool)
    operator_subtype_map: dict[str, list[str]] = defaultdict(list)
    for fine, operator in fine_operator.items():
        operator_subtype_map[operator].append(fine)
    operator_identity = {operator: operator for operator in operator_subtype_map}
    max_group_size = max((len(labels) for labels in operator_subtype_map.values()), default=1)
    fine_colors = akp.arkplatte_sub(
        dict(operator_subtype_map),
        operator_identity,
        candidates_per_group=max(160, max_group_size * 24),
    )
    coarse_colors = {
        group: akp.arkplatte_theme([operator])[operator]
        for group, operator in group_operator.items()
    }
    fine_order = sorted(adata.obs[fine_col].astype(str).unique())
    return {
        "fine_order": fine_order,
        "cluster_palette": [fine_colors[label] for label in fine_order],
        "track_palette": list(coarse_colors.values()) + akp.arkplatte_cat(64, large_n="force"),
        "fine_colors": fine_colors,
        "coarse_colors": coarse_colors,
        "group_operator": group_operator,
        "fine_operator": fine_operator,
        "subtype_map": dict(subtype_map),
    }


def plot_lung10k(ov):
    adata = ov.read(str(fetch(ov, "lung10k")))
    adata = normalize_lung10k(adata)
    describe_adata(adata, "lung10k", "compartment", "cell_type")
    palettes = build_hierarchical_palettes(adata, dataset="lung10k", coarse_col="compartment", fine_col="cell_type")
    palette_report("lung10k", palettes)
    ax = ov.pl.plot1cell(
        adata,
        clusters="cell_type",
        basis="X_tSNE",
        tracks=["compartment", "donor_id", "sex", "age"],
        cluster_palette=palettes["cluster_palette"],
        track_palette=palettes["track_palette"],
        point_size=6,
        point_alpha=0.5,
        figsize=(12, 12),
        label_fontsize=5.5,
        bg_color="white",
    )
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    ax.figure.savefig(FIGURE_DIR / "omicverse_lung10k_plot1cell_arknights.png", dpi=240, bbox_inches="tight")
    return palettes


def plot_kidney50k(ov):
    adata = ov.read(str(fetch(ov, "kidney50k")))
    describe_adata(adata, "kidney50k", "compartment", "cell_type")
    palettes = build_hierarchical_palettes(adata, dataset="kidney50k", coarse_col="compartment", fine_col="cell_type")
    palette_report("kidney50k", palettes)
    ax = ov.pl.plot1cell(
        adata,
        clusters="cell_type",
        basis="X_umap",
        tracks=["compartment", "tissue", "sex", "cell_state"],
        cluster_palette=palettes["cluster_palette"],
        track_palette=palettes["track_palette"],
        point_size=2,
        point_alpha=0.35,
        figsize=(12, 12),
        label_fontsize=6,
        bg_color="white",
    )
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    ax.figure.savefig(FIGURE_DIR / "omicverse_kidney50k_plot1cell_arknights.png", dpi=240, bbox_inches="tight")
    return palettes


def main() -> None:
    ov = require_omicverse()
    ov.style(font_path="arial")
    palettes_by_dataset = {
        "lung10k": plot_lung10k(ov),
        "kidney50k": plot_kidney50k(ov),
    }
    for dataset, palettes in palettes_by_dataset.items():
        mapping = {group: OPERATOR_LABEL.get(operator, operator) for group, operator in palettes["group_operator"].items()}
        print(dataset, mapping)
    print(f"saved plot1cell figures to {FIGURE_DIR}")


if __name__ == "__main__":
    main()
