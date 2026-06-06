# arkplatte 推广文案

用途：公众号和小红书发布前的文案底稿。  
项目链接：[https://github.com/Misaka-15134/arkplatte](https://github.com/Misaka-15134/arkplatte)  
在线教程：[https://misaka-15134.github.io/arkplatte/](https://misaka-15134.github.io/arkplatte/)

## 写作参考

同类科研配色内容常见写法有几个固定动作：

- 先说痛点：科研图丑、配色不统一、单细胞注释颜色太随机。
- 再给结果：能直接复制代码，能直接装包，图能马上变好看。
- 展示图比长解释更重要：先放色板和示例图，再解释方法。
- 强调用途：热图、火山图、柱状图、森林图、UMAP、plot1cell。
- 强调配色逻辑：连续色、双向色、分类色分开讲。

参考内容包括：

- `ggsci`：面向 `ggplot2` 的期刊和科幻主题配色包，核心卖点是科学期刊风格配色。
- R2Omics 配色教程：先介绍常用 R 配色包，再给 `ggplot2` 示例。
- 科研配色网站：常用“顶刊配色”“SCI 配色”“HEX 色值”“可复制”这些入口。
- 科研配色建议类页面：强调对比度、可读性、避免刺眼颜色和色盲友好。

---

# 公众号版

## 标题备选

1. 我做了一个明日方舟干员主题科研配色包：arkplatte
2. 科研绘图配色又多了一个选择：用明日方舟干员色板画 UMAP、热图和森林图
3. 从浊心斯卡蒂到塑心：一个面向 R 和 Python 的明日方舟科研配色包
4. 让科研图稍微有点灵魂：arkplatte 明日方舟配色包

## 摘要

我最近做了一个配色包：`arkplatte`。它把明日方舟干员的主题色整理成可以直接用于科研绘图的 R 包和 Python 库，支持核心色、单向连续色、双向连续色、分类色，以及单细胞细胞类型注释配色。

项目目前覆盖 417 名干员，每名干员有 8 个核心色和 1 个分类锚点色。六星干员做了人工校准，尽量让颜色来自角色本体，减少立绘背景、特效和召唤物对主题色的影响。

GitHub：  
[https://github.com/Misaka-15134/arkplatte](https://github.com/Misaka-15134/arkplatte)

在线教程：  
[https://misaka-15134.github.io/arkplatte/](https://misaka-15134.github.io/arkplatte/)

## 正文

### 1. 为什么做这个

科研绘图里最烦人的一件事，是图已经画出来了，但颜色怎么看都不对。

默认配色经常太随机。  
自己手动挑颜色又很容易一会儿偏灰，一会儿偏艳，一会儿像 PPT 模板。  
单细胞图更麻烦，细胞类型一多，颜色之间的距离不够，图例看着还行，UMAP 上直接糊成一片。

所以我想做一个稍微有趣一点，也真的能用的配色包：

把明日方舟干员的角色主题色提取出来，整理成固定色表，再按照科研绘图的需求生成不同类型的色板。

### 2. arkplatte 是什么

`arkplatte` 是一个明日方舟干员主题科研配色库。

它同时提供：

- Python 库：`arknights_palette`
- R 包：`arknightsPalette`
- HTML 在线教程
- 常见科研图示例
- 单细胞 UMAP 和 plot1cell 示例

它支持的配色类型包括：

- 核心色：直接获取某个干员的 5 到 10 个代表色
- 单向连续色：适合 0 到 1、表达量、丰度、得分
- 双向连续色：适合 -1 到 1、差异值、残差、相关系数
- 分类色：适合分组、细胞类型、样本注释
- 分层分类色：适合单细胞大类和小类注释

### 3. 安装

Python：

```bash
pip install "git+https://github.com/Misaka-15134/arkplatte.git#subdirectory=python"
```

R：

```r
install.packages("remotes")
remotes::install_github("Misaka-15134/arkplatte", subdir = "R")
```

### 4. 最小用法

Python：

```python
import arknights_palette as akp

akp.arkplatte("浊心斯卡蒂", 6)
akp.arkplatte_seq("塑心", 7)
akp.arkplatte_div("浊心斯卡蒂", 7)
akp.arkplatte_cat(8, seed=1)
```

R：

```r
library(arknightsPalette)

arkplatte("浊心斯卡蒂", 6)
arkplatte_seq("塑心", 7)
arkplatte_div("浊心斯卡蒂", 7)
arkplatte_cat(8, seed = 1)
```

### 5. 举几个例子

比如用浊心斯卡蒂的双向色板画正负柱状图：

```python
div = akp.arkplatte_div("浊心斯卡蒂", 7)
colors = [div[6], div[5], div[1], div[0], "#8F3343"]
ax.axhline(0, color="#AFAFAF")
ax.bar(labels, values, yerr=err, color=colors)
```

用乌尔比安的双向色板画热图：

```python
cmap = akp.arkplatte_cmap("乌尔比安", "div", 9)
ax.imshow(mat, cmap=cmap, vmin=-2.4, vmax=2.4)
```

用维什戴尔的颜色画森林图：

```python
colors = akp.arkplatte("维什戴尔", 8)
ax.errorbar(effect, y, xerr=ci, fmt="o", color=colors[i])
```

### 6. 单细胞图怎么用

普通细胞类型注释：

```python
celltypes = adata.obs["cell_type"].astype(str)
cluster_palette = akp.arkplatte_cell(celltypes, seed=4)
```

如果有大类和小类，可以把大类绑定到不同干员主题，小类在同一个干员主题里自动挑选更合适的颜色：

```python
subtype_map = {
    "Immune": ["T cell", "B cell", "Macrophage"],
    "Epithelial": ["AT1", "AT2"],
}

group_operator = {
    "Immune": "凯尔希",
    "Epithelial": "浊心斯卡蒂",
}

subtype_palette = akp.arkplatte_sub(subtype_map, group_operator)
```

这个功能对单细胞图比较重要。因为 UMAP 里颜色需要同时考虑细胞类型数量、类别层级和颜色距离。`arkplatte_sub()` 会根据每个大类下面的小类数量扩展候选色，再选出距离更合适的颜色。

### 7. 目前覆盖范围

当前版本覆盖 417 名干员。

每名干员提供：

- 8 个核心色
- 1 个分类锚点色
- 单向连续色
- 双向连续色
- 分类色候选

六星干员保留人工校准表。自动取色优先使用头像近景，尽量减少立绘背景和特效对主题色的干扰。

### 8. 我希望它解决什么问题

这个包主要想解决三个问题：

第一，科研图配色可以稳定复现。  
同一个干员在不同图里始终对应同一套颜色。

第二，配色不用每张图从头调。  
柱状图、热图、火山图、森林图、UMAP 都能从同一套函数里取色。

第三，单细胞图的分类色更可控。  
尤其是大类和小类同时出现的时候，可以保留层级关系，也能让小类之间有足够区分度。

### 9. 项目地址

GitHub：  
[https://github.com/Misaka-15134/arkplatte](https://github.com/Misaka-15134/arkplatte)

在线教程：  
[https://misaka-15134.github.io/arkplatte/](https://misaka-15134.github.io/arkplatte/)

如果你也刚好写 R、Python、单细胞分析，或者只是受够了默认配色，可以试一下。

---

# 小红书版

## 标题备选

1. 我把明日方舟干员做成科研绘图配色包了
2. 科研图配色救一下：明日方舟干员主题色板
3. 用浊心斯卡蒂、塑心、乌尔比安画科研图
4. R 和 Python 都能用的明日方舟科研配色包
5. 单细胞 UMAP 也能用干员主题色了

## 正文短版

最近做了一个小东西：`arkplatte`。

它是一个明日方舟干员主题的科研配色包，R 和 Python 都能用。

GitHub：  
https://github.com/Misaka-15134/arkplatte

在线教程：  
https://misaka-15134.github.io/arkplatte/

它能做什么：

- 按干员名取色，比如浊心斯卡蒂、塑心、乌尔比安
- 生成单向连续色，适合表达量、丰度、得分
- 生成双向连续色，适合差异值、相关系数、残差
- 生成分类色，适合分组、样本、细胞类型
- 支持单细胞 UMAP 和 plot1cell 配色
- 大类和小类细胞类型可以分层配色

安装：

```bash
pip install "git+https://github.com/Misaka-15134/arkplatte.git#subdirectory=python"
```

```r
install.packages("remotes")
remotes::install_github("Misaka-15134/arkplatte", subdir = "R")
```

Python 用法：

```python
import arknights_palette as akp

akp.arkplatte("浊心斯卡蒂", 6)
akp.arkplatte_seq("塑心", 7)
akp.arkplatte_div("浊心斯卡蒂", 7)
akp.arkplatte_cat(8, seed=1)
```

R 用法：

```r
library(arknightsPalette)

arkplatte("浊心斯卡蒂", 6)
arkplatte_seq("塑心", 7)
arkplatte_div("浊心斯卡蒂", 7)
arkplatte_cat(8, seed = 1)
```

目前覆盖 417 名干员。  
每名干员有 8 个核心色和 1 个分类锚点色。  
六星干员做了人工校准，尽量让颜色来自角色本体，少被背景和特效带偏。

我自己主要想用它画：

- 热图
- 火山图
- 森林图
- 分组小提琴图
- 样本注释图
- 单细胞 UMAP
- plot1cell 圆形图

如果你也经常被科研图配色折磨，可以试一下。

## 小红书正文长版

写科研图的时候，最容易卡住的地方经常在颜色。

默认颜色太随机，手动挑色又很容易越调越怪。尤其是单细胞图，细胞类型一多，颜色很容易挤在一起，看图的时候已经不知道哪个群是哪一个。

所以我做了一个配色包：`arkplatte`。

它把明日方舟干员的角色主题色整理成固定色板，然后封装成 Python 库和 R 包。

目前能直接用在：

- `ggplot2`
- `matplotlib`
- 单细胞 UMAP
- `plot1cell`
- 热图
- 火山图
- 森林图
- 小提琴图
- 样本和基因表达量可视化

核心函数很简单：

```python
akp.arkplatte("浊心斯卡蒂", 6)
akp.arkplatte_seq("塑心", 7)
akp.arkplatte_div("浊心斯卡蒂", 7)
akp.arkplatte_cat(8, seed=1)
```

R 里也基本同一套名字：

```r
arkplatte("浊心斯卡蒂", 6)
arkplatte_seq("塑心", 7)
arkplatte_div("浊心斯卡蒂", 7)
arkplatte_cat(8, seed = 1)
```

如果是单细胞：

```python
cluster_palette = akp.arkplatte_cell(adata.obs["cell_type"], seed=4)
```

如果有大类和小类：

```python
subtype_palette = akp.arkplatte_sub(subtype_map, group_operator)
```

比如 B 细胞类群绑定凯尔希主题，下面的 Plasma cell、Memory B cell 会在凯尔希主题里面自动找更合适、更能区分的小类颜色。

这点对 UMAP 很有用。颜色需要好看，也需要能读。

项目地址：  
https://github.com/Misaka-15134/arkplatte

在线教程：  
https://misaka-15134.github.io/arkplatte/

有兴趣可以直接装一下。  
也欢迎提 issue，尤其是如果你觉得某个干员颜色还不像本人。

## 小红书标签

#科研绘图  
#R语言  
#Python  
#单细胞  
#生信分析  
#UMAP  
#ggplot2  
#matplotlib  
#明日方舟  
#科研配色  
#数据可视化

---

# 配图建议

## 公众号

建议配图顺序：

1. 12 名干员色板总览图
2. 浊心斯卡蒂双向柱状图
3. 乌尔比安热图
4. 维什戴尔森林图
5. lung10k 或 kidney50k 单细胞 UMAP
6. plot1cell 圆形图

## 小红书

建议做成 6 到 8 张图：

1. 封面：明日方舟科研配色包 arkplatte
2. 角色色板九宫格
3. 安装命令
4. 四个核心函数
5. 常见科研图拼图
6. 单细胞 UMAP
7. plot1cell 示例
8. GitHub 和在线教程链接

---

# 发布前检查

- GitHub 链接可打开。
- GitHub Pages 已启用，在线教程能打开。
- README 中安装命令可复制。
- 公众号正文里的代码块格式正常。
- 小红书正文不要一次塞太多代码，图片里放结果更重要。
- 如果展示 UMAP，图注里说明数据来源和示例用途。
