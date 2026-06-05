from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = ROOT / "arknights_palette"
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
FIGURE_DIR = Path(__file__).resolve().parents[1] / "figures"
sys.path.insert(0, str(PACKAGE_ROOT))

from python_omicverse_plot1cell_lung_kidney import (  # noqa: E402
    build_hierarchical_palettes,
    describe_adata,
    palette_report,
)


CDN = "https://datasets.cellxgene.cziscience.com/"
DATA = {
    "kidney50k": "7dafa492-6129-4dff-a794-17bdefde3575.h5ad",
}


def fetch(ov, key: str) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    local = DATA_DIR / f"{key}.h5ad"
    if not local.exists():
        ov.datasets.download_data(CDN + DATA[key], str(local))
    return local


def main() -> None:
    import omicverse as ov

    adata = ov.read(str(fetch(ov, "kidney50k")))
    describe_adata(adata, "kidney50k_umap", "compartment", "cell_type")
    palettes = build_hierarchical_palettes(adata, "kidney50k", "compartment", "cell_type")
    palette_report("kidney50k_umap", palettes)
    colors = palettes["fine_colors"]
    cell_type = adata.obs["cell_type"].astype(str)
    xy = adata.obsm["X_umap"]
    fig, ax = plt.subplots(figsize=(5.2, 4.5))
    for label in sorted(cell_type.unique()):
        mask = cell_type == label
        ax.scatter(xy[mask, 0], xy[mask, 1], s=1.5, color=colors[label], alpha=0.65, linewidths=0)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("UMAP 1")
    ax.set_ylabel("UMAP 2")
    ax.set_title("kidney50k cell_type UMAP")
    ax.spines[["top", "right"]].set_visible(False)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_DIR / "single_cell_umap_kidney50k_arknights.png", dpi=260, bbox_inches="tight")
    fig.savefig(FIGURE_DIR / "single_cell_umap_kidney50k_arknights.svg", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
