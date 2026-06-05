# arknights_palette

明日方舟科研配色 Python 库。固定颜色表覆盖 417 名干员，其中 131 名六星干员保留人工校准表。

## 安装

```bash
pip install "git+https://github.com/Misaka-15134/arkplatte.git#subdirectory=python"
```

本地开发：

```bash
cd python
pip install -e ".[test,plot]"
python -m pytest tests -q
```

## 快速使用

```python
import arknights_palette as akp

akp.arkplatte("浊心斯卡蒂", 6)
akp.arkplatte_seq("塑心", 7)
akp.arkplatte_div("浊心斯卡蒂", 7)
akp.arkplatte_cat(8, seed=1)
```

## 函数

| 函数 | 用途 |
|---|---|
| `arkplatte(name, n=None, kind="core")` | 核心色入口；`kind` 可设为 `"core"`、`"seq"`、`"div"`。 |
| `arkplatte_seq(name, n=256)` | 单向连续色，适合非负数值。 |
| `arkplatte_div(name, n=257)` | 双向连续色，适合正负方向数值。 |
| `arkplatte_cat(n, seed=None, large_n="warn", optimize=True)` | 跨角色分类色；超过 30 类默认提醒。 |
| `arkplatte_cell(celltypes, seed=1, large_n="warn")` | 细胞类型分类色。 |
| `arkplatte_sub(subtype_map, group_operator)` | 大类绑定角色主题，小类自动挑选同主题内分散颜色。 |
| `arkplatte_names(rarity=None)` | 默认返回全部干员；设为 `6` 返回六星。 |
| `arkplatte_info(name)` | 查询干员元数据。 |
| `arkplatte_theme(names)` | 提取多个角色主题色。 |
| `arkplatte_cmap(name, kind="seq", n=256)` | 生成 Matplotlib 颜色映射。 |

## 单细胞示例

```python
celltypes = adata.obs["cell_type"].astype(str)
cluster_palette = akp.arkplatte_cell(celltypes, seed=4)
```

```python
subtype_palette = akp.arkplatte_sub(
    {"Immune": ["T cell", "B cell"], "Epithelial": ["AT1", "AT2"]},
    {"Immune": "凯尔希", "Epithelial": "浊心斯卡蒂"},
)
```
