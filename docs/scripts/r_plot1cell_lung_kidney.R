library(arknightsPalette)

# 依赖：
# remotes::install_github("TheHumphreysLab/plot1cell")
# install.packages(c("Seurat", "reticulate"))
# BiocManager::install(c("zellkonverter", "SingleCellExperiment"))

CDN <- "https://datasets.cellxgene.cziscience.com/"
DATA <- c(
  lung10k = "c88e0403-da93-40f4-99b5-f5fdeb81a82c.h5ad",
  kidney50k = "7dafa492-6129-4dff-a794-17bdefde3575.h5ad"
)

DEFAULT_OPERATOR_CYCLE <- c(
  "凯尔希", "浊心斯卡蒂", "塑心", "乌尔比安",
  "缪尔赛思", "令", "黍", "维什戴尔",
  "丰川祥子", "玛恩纳", "蕾缪安", "新约能天使",
  "望", "史尔特尔", "空弦", "水月", "逻各斯"
)
DATASET_OPERATOR_MAP <- list(
  lung10k = c(
    endothelial = "凯尔希",
    epithelial = "浊心斯卡蒂",
    immune = "塑心",
    stromal = "乌尔比安"
  ),
  kidney50k = c(
    PT = "缪尔赛思",
    lymphoid = "令",
    myeloid = "黍",
    non_PT = "维什戴尔"
  )
)
DATASET_OPERATOR_POOL <- list(
  lung10k = c(
    "凯尔希", "浊心斯卡蒂", "塑心", "乌尔比安",
    "丰川祥子", "玛恩纳", "蕾缪安", "新约能天使",
    "望", "史尔特尔", "空弦", "水月", "逻各斯"
  ),
  kidney50k = c(
    "缪尔赛思", "令", "黍", "维什戴尔",
    "丰川祥子", "玛恩纳", "蕾缪安", "新约能天使",
    "望", "史尔特尔", "空弦", "水月", "逻各斯"
  )
)

DATA_DIR <- "data"
FIGURE_DIR <- "figures"
dir.create(DATA_DIR, showWarnings = FALSE)
dir.create(FIGURE_DIR, showWarnings = FALSE)

fetch <- function(key) {
  path <- file.path(DATA_DIR, paste0(key, ".h5ad"))
  if (!file.exists(path)) {
    download.file(paste0(CDN, DATA[key]), path, mode = "wb")
  }
  path
}

build_hierarchical_palettes <- function(meta, dataset, coarse_col, fine_col) {
  fine_values <- sort(unique(as.character(meta[[fine_col]])))
  fine_to_coarse <- setNames(character(length(fine_values)), fine_values)
  for (fine in fine_values) {
    coarse <- meta[as.character(meta[[fine_col]]) == fine, coarse_col]
    fine_to_coarse[fine] <- names(sort(table(as.character(coarse)), decreasing = TRUE))[1]
  }
  coarse_values <- sort(unique(fine_to_coarse))
  preset <- DATASET_OPERATOR_MAP[[dataset]]
  fallback <- setdiff(DEFAULT_OPERATOR_CYCLE, preset)
  group_operator <- setNames(character(length(coarse_values)), coarse_values)
  for (index in seq_along(coarse_values)) {
    group <- coarse_values[index]
    group_operator[group] <- if (group %in% names(preset)) {
      preset[group]
    } else {
      fallback[((index - 1) %% length(fallback)) + 1]
    }
  }
  subtype_map <- lapply(coarse_values, function(group) names(fine_to_coarse)[fine_to_coarse == group])
  names(subtype_map) <- coarse_values

  operator_pool <- DATASET_OPERATOR_POOL[[dataset]]
  fine_operator <- c()
  for (group in sort(names(subtype_map))) {
    main_operator <- group_operator[group]
    candidates <- c(main_operator, setdiff(operator_pool, main_operator))
    subtypes <- sort(subtype_map[[group]])
    assigned <- candidates[((seq_along(subtypes) - 1) %% length(candidates)) + 1]
    names(assigned) <- subtypes
    fine_operator <- c(fine_operator, assigned)
  }
  operator_subtype_map <- split(names(fine_operator), fine_operator)
  operator_identity <- stats::setNames(names(operator_subtype_map), names(operator_subtype_map))
  fine_colors <- arkplatte_sub(operator_subtype_map, operator_identity, candidates_per_group = 160)
  coarse_colors <- arkplatte_theme(group_operator)
  names(coarse_colors) <- names(group_operator)
  print(list(dataset = dataset, group_operator = group_operator, fine_operator = fine_operator, fine_colors = fine_colors))
  list(
    fine_order = fine_values,
    fine_colors = fine_colors,
    cluster_colors = fine_colors[fine_values],
    coarse_colors = coarse_colors,
    group_operator = group_operator,
    fine_operator = fine_operator
  )
}

read_h5ad_as_seurat <- function(path, basis_key, cluster_col) {
  sce <- zellkonverter::readH5AD(path)
  seu <- Seurat::as.Seurat(sce, counts = "X", data = NULL)
  meta <- as.data.frame(SingleCellExperiment::colData(sce))
  extra_cols <- setdiff(colnames(meta), colnames(seu@meta.data))
  seu@meta.data <- cbind(seu@meta.data, meta[colnames(seu), extra_cols, drop = FALSE])
  reduced_names <- SingleCellExperiment::reducedDimNames(sce)
  reduced_key <- basis_key
  if (!basis_key %in% reduced_names && gsub("^X_", "", basis_key) %in% reduced_names) {
    reduced_key <- gsub("^X_", "", basis_key)
  }
  reduced <- SingleCellExperiment::reducedDim(sce, reduced_key)
  reduction_name <- gsub("^X_", "", basis_key)
  colnames(reduced) <- paste0(reduction_name, "_", 1:2)
  seu[[reduction_name]] <- Seurat::CreateDimReducObject(
    embeddings = reduced,
    key = paste0(reduction_name, "_")
  )
  Idents(seu) <- seu@meta.data[[cluster_col]]
  seu
}

plot_lung10k <- function() {
  seu <- read_h5ad_as_seurat(fetch("lung10k"), basis_key = "X_tSNE", cluster_col = "cell_type")
  seu$age <- gsub("-year-old stage", "y", as.character(seu$development_stage), fixed = TRUE)
  print(head(seu@meta.data[, c("compartment", "cell_type", "donor_id", "sex", "age")]))
  palettes <- build_hierarchical_palettes(seu@meta.data, dataset = "lung10k", coarse_col = "compartment", fine_col = "cell_type")
  Idents(seu) <- factor(as.character(seu$cell_type), levels = palettes$fine_order)
  circ_data <- plot1cell::prepare_circlize_data(seu, scale = 0.8)
  png(file.path(FIGURE_DIR, "r_lung10k_plot1cell_arknights.png"), width = 12, height = 12, units = "in", res = 240)
  plot1cell::plot_circlize(circ_data, do.label = TRUE, pt.size = 0.01, col.use = palettes$cluster_colors, bg.color = "white", repel = TRUE, label.cex = 0.45)
  plot1cell::add_track(circ_data, group = "compartment", colors = palettes$coarse_colors, track_num = 2)
  plot1cell::add_track(circ_data, group = "donor_id", track_num = 3)
  plot1cell::add_track(circ_data, group = "sex", track_num = 4)
  plot1cell::add_track(circ_data, group = "age", track_num = 5)
  dev.off()
}

plot_kidney50k <- function() {
  seu <- read_h5ad_as_seurat(fetch("kidney50k"), basis_key = "X_umap", cluster_col = "cell_type")
  print(head(seu@meta.data[, c("compartment", "cell_type", "donor_id", "sex", "tissue", "cell_state")]))
  palettes <- build_hierarchical_palettes(seu@meta.data, dataset = "kidney50k", coarse_col = "compartment", fine_col = "cell_type")
  Idents(seu) <- factor(as.character(seu$cell_type), levels = palettes$fine_order)
  circ_data <- plot1cell::prepare_circlize_data(seu, scale = 0.8)
  png(file.path(FIGURE_DIR, "r_kidney50k_plot1cell_arknights.png"), width = 12, height = 12, units = "in", res = 240)
  plot1cell::plot_circlize(circ_data, do.label = TRUE, pt.size = 0.006, col.use = palettes$cluster_colors, bg.color = "white", repel = TRUE, label.cex = 0.5)
  plot1cell::add_track(circ_data, group = "compartment", colors = palettes$coarse_colors, track_num = 2)
  plot1cell::add_track(circ_data, group = "tissue", track_num = 3)
  plot1cell::add_track(circ_data, group = "sex", track_num = 4)
  plot1cell::add_track(circ_data, group = "cell_state", track_num = 5)
  dev.off()
}

plot_lung10k()
plot_kidney50k()
