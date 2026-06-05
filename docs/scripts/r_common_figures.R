library(arknightsPalette)

dir.create("figures", showWarnings = FALSE)

arkplatte("浊心斯卡蒂", 6)
arkplatte_seq("塑心", 7)
arkplatte_div("浊心斯卡蒂", 7)
arkplatte_cat(8, seed = 1)

bar_df <- data.frame(
  group = c("basal", "stress", "recovery", "responder", "high risk"),
  value = c(-0.48, -0.22, 0.14, 0.36, 0.58)
)
bar_div <- arkplatte_div("浊心斯卡蒂", 7)
bar_cols <- c(bar_div[7], bar_div[6], bar_div[2], bar_div[1], "#8F3343")
print(list(common_bar = bar_cols))

line_cols <- arkplatte_seq("塑心", 5)[2:4]
heat_cols <- arkplatte_div("乌尔比安", 9)
print(list(common_line = line_cols, common_heatmap = heat_cols))

# 柱状图、折线图、热图、小提琴图可直接把这些颜色传给 ggplot2 或 ComplexHeatmap。
# 详细数据生成见 Python 示例；R 侧保留最小用法模板，方便迁移到真实数据。
subtype_map <- list(
  PT = c("epithelial cell of proximal tubule", "kidney epithelial cell"),
  lymphoid = c("B cell", "CD4-positive, alpha-beta T cell"),
  myeloid = c("classical monocyte", "dendritic cell"),
  non_PT = c("podocyte", "urothelial cell")
)
group_operator <- c(
  PT = "缪尔赛思",
  lymphoid = "令",
  myeloid = "黍",
  non_PT = "维什戴尔"
)
sub_cols <- arkplatte_sub(subtype_map, group_operator, candidates_per_group = 160)
print(list(single_cell_subtypes = sub_cols))
