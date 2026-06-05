from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = ROOT / "arknights_palette"
FIGURE_DIR = Path(__file__).resolve().parents[1] / "figures"
sys.path.insert(0, str(PACKAGE_ROOT))

import arknights_palette as akp  # noqa: E402


plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans"],
    "svg.fonttype": "none",
    "font.size": 8,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.8,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "legend.frameon": False,
})


def save(fig: plt.Figure, name: str) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_DIR / f"{name}.png", dpi=260, bbox_inches="tight")
    fig.savefig(FIGURE_DIR / f"{name}.svg", bbox_inches="tight")
    plt.close(fig)


def print_colors(name: str, colors) -> None:
    if isinstance(colors, dict):
        payload = colors
    else:
        payload = list(colors)
    print(f"{name}: {payload}")


def bar_chart() -> None:
    labels = ["basal", "stress", "recovery", "responder", "high risk"]
    values = np.array([-0.48, -0.22, 0.14, 0.36, 0.58])
    err = np.array([0.07, 0.06, 0.05, 0.06, 0.08])
    div = akp.arkplatte_div("浊心斯卡蒂", 7)
    colors = [div[6], div[5], div[1], div[0], "#8F3343"]
    print_colors("common_bar", colors)
    fig, ax = plt.subplots(figsize=(4.6, 3.1))
    ax.axhline(0, color="#AFAFAF", linewidth=0.9)
    ax.bar(labels, values, yerr=err, capsize=3, color=colors, edgecolor="#2A2A2A", linewidth=0.6)
    ax.set_ylabel("signed response")
    ax.set_ylim(-0.68, 0.78)
    ax.set_title("signed bar chart")
    save(fig, "common_bar")


def line_chart() -> None:
    x = np.arange(0, 8)
    base = 1 / (1 + np.exp(-(x - 3)))
    series = {
        "baseline": base * 0.75,
        "model A": base * 0.92 + 0.03,
        "model B": base * 1.04 + 0.02,
    }
    colors = akp.arkplatte_seq("塑心", 5)[1:4]
    print_colors("common_line", colors)
    fig, ax = plt.subplots(figsize=(4.4, 3.0))
    for color, (label, y) in zip(colors, series.items(), strict=True):
        ax.plot(x, y, marker="o", markersize=3.5, linewidth=1.8, color=color, label=label)
        ax.fill_between(x, y - 0.04, y + 0.04, color=color, alpha=0.14, linewidth=0)
    ax.set_xlabel("time")
    ax.set_ylabel("normalised signal")
    ax.legend(loc="lower right")
    ax.set_title("line chart")
    save(fig, "common_line")


def scatter_chart() -> None:
    rng = np.random.default_rng(12)
    groups = ["endothelial", "immune", "stromal"]
    operators = {"endothelial": "凯尔希", "immune": "塑心", "stromal": "乌尔比安"}
    colors = {group: akp.arkplatte_theme([op])[op] for group, op in operators.items()}
    print_colors("common_scatter", colors)
    fig, ax = plt.subplots(figsize=(4.2, 3.2))
    for i, group in enumerate(groups):
        x = rng.normal(i * 0.9, 0.25, 45)
        y = rng.normal(0.3 + i * 0.35, 0.22, 45)
        size = rng.uniform(20, 90, 45)
        ax.scatter(x, y, s=size, color=colors[group], alpha=0.68, label=group, edgecolor="white", linewidth=0.35)
    ax.set_xlabel("module score")
    ax.set_ylabel("effect size")
    ax.legend(loc="upper left")
    ax.set_title("scatter / bubble")
    save(fig, "common_scatter")


def heatmap_chart() -> None:
    rng = np.random.default_rng(7)
    mat = rng.normal(size=(10, 8))
    mat[:4, :3] += 1.3
    mat[6:, 5:] -= 1.2
    fig, ax = plt.subplots(figsize=(4.4, 3.4))
    heat_colors = akp.arkplatte_div("乌尔比安", 9)
    print_colors("common_heatmap", heat_colors)
    im = ax.imshow(mat, cmap=akp.arkplatte_cmap("乌尔比安", "div", 257), vmin=-2.4, vmax=2.4, aspect="auto")
    ax.set_xticks(range(8), [f"S{i+1}" for i in range(8)], rotation=45, ha="right")
    ax.set_yticks(range(10), [f"G{i+1}" for i in range(10)])
    ax.set_title("heatmap")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cbar.set_label("z score")
    save(fig, "common_heatmap")


def violin_chart() -> None:
    rng = np.random.default_rng(31)
    data = [
        rng.normal(0.2, 0.35, 100),
        rng.normal(0.7, 0.32, 100),
        rng.normal(1.0, 0.38, 100),
        rng.normal(1.35, 0.34, 100),
    ]
    colors = akp.arkplatte_seq("缪尔赛思", 5)[1:]
    print_colors("common_violin", colors)
    fig, ax = plt.subplots(figsize=(4.0, 3.0))
    parts = ax.violinplot(data, showmeans=False, showmedians=True)
    for body, color in zip(parts["bodies"], colors, strict=True):
        body.set_facecolor(color)
        body.set_edgecolor("#2A2A2A")
        body.set_alpha(0.72)
    for key in ["cbars", "cmins", "cmaxes", "cmedians"]:
        parts[key].set_color("#2A2A2A")
        parts[key].set_linewidth(0.8)
    ax.set_xticks([1, 2, 3, 4], ["A", "B", "C", "D"])
    ax.set_ylabel("expression")
    ax.set_title("violin plot")
    save(fig, "common_violin")


def forest_chart() -> None:
    labels = ["overall", "female", "male", "young", "aged", "high risk"]
    effects = np.array([0.18, 0.11, 0.24, 0.08, 0.31, 0.42])
    low = effects - np.array([0.08, 0.10, 0.09, 0.12, 0.11, 0.13])
    high = effects + np.array([0.08, 0.11, 0.10, 0.13, 0.12, 0.14])
    core = akp.arkplatte("维什戴尔", 8)
    colors = [core[i] for i in [0, 1, 2, 5, 6, 7]]
    print_colors("common_forest", colors)
    y = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(4.4, 3.2))
    ax.axvline(0, color="#B8B8B8", linewidth=1)
    for idx, color in enumerate(colors):
        ax.errorbar(
            effects[idx],
            y[idx],
            xerr=np.array([[effects[idx] - low[idx]], [high[idx] - effects[idx]]]),
            fmt="o",
            color=color,
            ecolor=color,
            capsize=3,
            markersize=5.2,
            elinewidth=1.15,
        )
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlabel("effect estimate")
    ax.set_title("forest plot")
    save(fig, "common_forest")


def volcano_chart() -> None:
    rng = np.random.default_rng(202)
    log_fc = rng.normal(0, 1.1, 900)
    neg_log_p = np.clip(np.abs(log_fc) * 1.5 + rng.gamma(1.4, 0.9, 900), 0, 8)
    sig_up = (log_fc > 1.1) & (neg_log_p > 3)
    sig_down = (log_fc < -1.1) & (neg_log_p > 3)
    div = akp.arkplatte_div("浊心斯卡蒂", 7)
    print_colors("bio_volcano", div)
    colors = np.full(log_fc.shape, "#B8BEC6", dtype=object)
    colors[sig_down] = div[-1]
    colors[sig_up] = div[0]
    fig, ax = plt.subplots(figsize=(4.5, 3.3))
    ax.scatter(log_fc, neg_log_p, c=colors, s=9, alpha=0.72, linewidths=0)
    ax.axvline(-1.1, color="#C4C4C4", linewidth=0.8, linestyle="--")
    ax.axvline(1.1, color="#C4C4C4", linewidth=0.8, linestyle="--")
    ax.axhline(3, color="#C4C4C4", linewidth=0.8, linestyle="--")
    ax.set_xlabel("log2 fold change")
    ax.set_ylabel("-log10 adjusted p")
    ax.set_title("volcano plot")
    save(fig, "bio_volcano")


def dotplot_chart() -> None:
    rng = np.random.default_rng(77)
    genes = ["MS4A1", "CD79A", "LYZ", "S100A8", "EPCAM", "KRT8"]
    celltypes = ["B cell", "Plasma", "Mono", "DC", "AT1", "AT2"]
    expr = rng.uniform(0.1, 2.5, (len(genes), len(celltypes)))
    pct = rng.uniform(0.12, 0.88, (len(genes), len(celltypes)))
    expr[:2, :2] += 1.4
    expr[2:4, 2:4] += 1.2
    expr[4:, 4:] += 1.3
    cmap = akp.arkplatte_cmap("逻各斯", "seq", 128)
    print_colors("bio_dotplot", akp.arkplatte_seq("逻各斯", 9))
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    for i, gene in enumerate(genes):
        for j, celltype in enumerate(celltypes):
            ax.scatter(
                j,
                i,
                s=40 + pct[i, j] * 210,
                c=[expr[i, j]],
                cmap=cmap,
                vmin=0,
                vmax=4,
                edgecolor="#303030",
                linewidth=0.25,
            )
    ax.set_xticks(range(len(celltypes)), celltypes, rotation=35, ha="right")
    ax.set_yticks(range(len(genes)), genes)
    ax.invert_yaxis()
    ax.set_title("marker dot plot")
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, 4))
    cbar = fig.colorbar(sm, ax=ax, fraction=0.046, pad=0.03)
    cbar.set_label("mean expression")
    save(fig, "bio_dotplot")


def enrichment_chart() -> None:
    terms = ["IFN response", "BCR signaling", "T cell activation", "ECM remodeling", "Oxidative stress", "Angiogenesis"]
    scores = np.array([5.6, 4.8, 4.2, 3.7, 3.1, 2.6])
    operators = ["蕾缪安", "玛恩纳", "史尔特尔", "水月", "空弦", "望"]
    colors = list(akp.arkplatte_theme(operators).values())
    print_colors("bio_enrichment", dict(zip(operators, colors, strict=True)))
    y = np.arange(len(terms))
    fig, ax = plt.subplots(figsize=(4.8, 3.2))
    ax.barh(y, scores, color=colors, edgecolor="#2A2A2A", linewidth=0.55)
    ax.set_yticks(y, terms)
    ax.invert_yaxis()
    ax.set_xlabel("-log10 q value")
    ax.set_title("pathway enrichment")
    save(fig, "bio_enrichment")


def pca_chart() -> None:
    rng = np.random.default_rng(19)
    groups = ["control", "treated", "relapse"]
    operators = {"control": "丰川祥子", "treated": "新约能天使", "relapse": "史尔特尔"}
    colors = akp.arkplatte_theme(list(operators.values()))
    print_colors("bio_pca", colors)
    fig, ax = plt.subplots(figsize=(4.2, 3.3))
    for idx, group in enumerate(groups):
        xy = rng.normal(loc=[idx * 1.2, idx * 0.45], scale=[0.35, 0.28], size=(14, 2))
        operator = operators[group]
        ax.scatter(
            xy[:, 0],
            xy[:, 1],
            s=44,
            color=colors[operator],
            label=group,
            alpha=0.82,
            edgecolor="white",
            linewidth=0.45,
        )
    ax.set_xlabel("PC1 38.2%")
    ax.set_ylabel("PC2 14.7%")
    ax.legend(loc="upper left")
    ax.set_title("sample PCA")
    save(fig, "bio_pca")


def main() -> None:
    bar_chart()
    line_chart()
    scatter_chart()
    heatmap_chart()
    violin_chart()
    forest_chart()
    volcano_chart()
    dotplot_chart()
    enrichment_chart()
    pca_chart()


if __name__ == "__main__":
    main()
