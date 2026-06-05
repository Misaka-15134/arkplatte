# arknightsPalette

明日方舟科研配色 R 包。固定颜色表覆盖 417 名干员，其中 131 名六星干员保留人工校准表。

## 安装

```r
install.packages("remotes")
remotes::install_github("Misaka-15134/arkplatte", subdir = "R")
```

本地开发：

```r
install.packages("devtools")
devtools::install("R")
```

## 快速使用

```r
library(arknightsPalette)

arkplatte("浊心斯卡蒂", 6)
arkplatte_seq("塑心", 7)
arkplatte_div("浊心斯卡蒂", 7)
arkplatte_cat(8, seed = 1)
```

## 函数

| 函数 | 用途 |
|---|---|
| `arkplatte(name, n = NULL, type = "core")` | 核心色入口；`type` 可设为 `"core"`、`"seq"`、`"div"`。 |
| `arkplatte_seq(name, n = 256)` | 单向连续色，适合非负数值。 |
| `arkplatte_div(name, n = 257)` | 双向连续色，适合正负方向数值。 |
| `arkplatte_cat(n, seed = NULL, large_n = "warn", optimize = TRUE)` | 跨角色分类色；超过 30 类默认提醒。 |
| `arkplatte_cell(celltypes, seed = 1, large_n = "warn")` | 细胞类型分类色。 |
| `arkplatte_sub(subtype_map, group_operator)` | 大类绑定角色主题，小类自动挑选同主题内分散颜色。 |
| `arkplatte_names(rarity = NULL)` | 默认返回全部干员；设为 `6` 返回六星。 |
| `arkplatte_info(name)` | 查询干员元数据。 |
| `arkplatte_theme(names)` | 提取多个角色主题色。 |
| `arkplatte_show(name, n = NULL)` | 快速预览角色色板。 |

## 单细胞示例

```r
celltypes <- seurat_obj$cell_type
cluster_palette <- arkplatte_cell(celltypes, seed = 4)
```

```r
subtype_palette <- arkplatte_sub(
  list(Immune = c("T cell", "B cell"), Epithelial = c("AT1", "AT2")),
  c(Immune = "凯尔希", Epithelial = "浊心斯卡蒂")
)
```
