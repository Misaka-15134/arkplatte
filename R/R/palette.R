ak_match_operator <- function(name) {
  operators <- ak_operators()
  key <- as.character(name)
  hit <- operators[
    operators$name_cn == key |
      operators$operator_id == key |
      operators$name_key == tolower(key),
  , drop = FALSE]
  if (nrow(hit) == 1) {
    return(hit[1, ])
  }
  if (nrow(hit) > 1) {
    stop("查询匹配到多个干员：", key, call. = FALSE)
  }
  candidates <- operators$name_cn[agrep(key, operators$name_cn, max.distance = 0.35)]
  suffix <- if (length(candidates)) {
    paste0("。候选：", paste(utils::head(candidates, 8), collapse = "、"))
  } else {
    ""
  }
  stop("未找到干员：", key, suffix, call. = FALSE)
}

ak_names <- function(rarity = NULL) {
  operators <- ak_operators()
  if (!is.null(rarity)) {
    operators <- operators[operators$rarity == rarity, , drop = FALSE]
  }
  operators$name_cn
}

ak_info <- function(name) {
  ak_match_operator(name)
}

ak_core_rows <- function(name) {
  op <- ak_match_operator(name)
  palettes <- ak_palettes()
  rows <- palettes[
    palettes$operator_id == op$operator_id &
      palettes$palette_type == "core",
  , drop = FALSE]
  rows[order(rows$rank), , drop = FALSE]
}

ak_theme_color <- function(name) {
  rows <- ak_core_rows(name)
  theme <- rows$hex[rows$role == "theme"][1]
  if (is.na(theme)) rows$hex[1] else theme
}

ak_interpolate <- function(colors, n) {
  colors <- unique(colors)
  if (is.null(n)) {
    return(colors)
  }
  if (n <= length(colors)) {
    return(colors[seq_len(n)])
  }
  grDevices::colorRampPalette(colors, space = "Lab")(n)
}

ak_hex_to_lab <- function(colors) {
  grDevices::convertColor(t(grDevices::col2rgb(colors)) / 255, from = "sRGB", to = "Lab")
}

ak_lab_to_hex <- function(lab) {
  rgb <- grDevices::convertColor(matrix(lab, nrow = 1), from = "Lab", to = "sRGB")
  rgb <- pmax(0, pmin(1, rgb))
  grDevices::rgb(rgb[1, 1], rgb[1, 2], rgb[1, 3])
}

ak_chroma <- function(lab) {
  sqrt(lab[2]^2 + lab[3]^2)
}

ak_adjust_lab <- function(color, lightness = NULL, chroma = NULL) {
  lab <- as.numeric(ak_hex_to_lab(color)[1, ])
  old_chroma <- ak_chroma(lab)
  if (!is.null(chroma) && old_chroma > 0) {
    scale <- max(0, chroma) / old_chroma
    lab[2] <- lab[2] * scale
    lab[3] <- lab[3] * scale
  }
  if (!is.null(lightness)) {
    lab[1] <- max(0, min(100, lightness))
  }
  ak_lab_to_hex(lab)
}

ak_blend_lab <- function(a, b, amount) {
  lab_a <- as.numeric(ak_hex_to_lab(a)[1, ])
  lab_b <- as.numeric(ak_hex_to_lab(b)[1, ])
  ak_lab_to_hex(lab_a * (1 - amount) + lab_b * amount)
}

ak_interpolate_monotone_lightness <- function(colors, n, descending = TRUE) {
  if (n <= 0) return(character(0))
  colors <- unique(colors)
  if (length(colors) == 1) return(rep(colors, n))
  base <- grDevices::colorRampPalette(colors, space = "Lab")(n)
  lab <- ak_hex_to_lab(base)
  start_l <- lab[1, 1]
  end_l <- lab[n, 1]
  if (descending && start_l < end_l) {
    tmp <- start_l
    start_l <- end_l
    end_l <- tmp
  }
  if (!descending && start_l > end_l) {
    tmp <- start_l
    start_l <- end_l
    end_l <- tmp
  }
  out <- character(n)
  for (idx in seq_len(n)) {
    t <- if (n == 1) 0 else (idx - 1) / (n - 1)
    smooth <- t * t * (3 - 2 * t)
    lab[idx, 1] <- start_l * (1 - smooth) + end_l * smooth
    out[idx] <- ak_lab_to_hex(lab[idx, ])
  }
  out
}

ak_lab_distance <- function(color, selected) {
  lab <- ak_hex_to_lab(c(color, selected))
  sqrt(rowSums((lab[-1, , drop = FALSE] - lab[1, ])^2))
}

ak_farthest_colors <- function(candidates, n, seed_color = NULL) {
  candidates <- unique(candidates)
  if (n <= 0) return(character(0))
  if (n >= length(candidates)) return(candidates)
  selected <- if (!is.null(seed_color) && seed_color %in% candidates) {
    seed_color
  } else {
    lab <- ak_hex_to_lab(candidates)
    candidates[which.max(lab[, 1])]
  }
  while (length(selected) < n) {
    remaining <- setdiff(candidates, selected)
    score <- vapply(remaining, function(x) min(ak_lab_distance(x, selected)), numeric(1))
    selected <- c(selected, remaining[which.max(score)])
  }
  selected
}

ak_readable_on_white <- function(colors) {
  lab <- ak_hex_to_lab(colors)
  chroma <- sqrt(lab[, 2]^2 + lab[, 3]^2)
  visible <- lab[, 1] >= 12 & lab[, 1] <= 82
  colorful <- visible & chroma >= 5
  if (any(colorful)) {
    colors[colorful]
  } else if (any(visible)) {
    colors[visible]
  } else {
    colors
  }
}

ak_theme_candidate_pool <- function(name, n) {
  sample_n <- max(24, min(240, n))
  unique(c(ak_palette(name), ak_sequential(name, sample_n), ak_diverging(name, sample_n)))
}

ak_palette <- function(name, n = NULL, type = "core") {
  rows <- ak_core_rows(name)
  if (type == "core") {
    return(ak_interpolate(rows$hex, n))
  }
  if (type == "sequential") {
    return(ak_sequential(name, n = if (is.null(n)) 256 else n))
  }
  if (type == "diverging") {
    return(ak_diverging(name, n = if (is.null(n)) 257 else n))
  }
  stop("未知配色类型：", type, call. = FALSE)
}

ak_sequential <- function(name, n = 256) {
  rows <- ak_core_rows(name)
  light <- rows$hex[rows$role == "light"][1]
  theme <- rows$hex[rows$role == "theme"][1]
  dark <- rows$hex[rows$role == "dark"][1]
  if (is.na(light)) light <- rows$hex[which.max(as.numeric(rows$lab_l))]
  if (is.na(dark)) dark <- rows$hex[which.min(as.numeric(rows$lab_l))]
  light_lab <- as.numeric(ak_hex_to_lab(light)[1, ])
  dark_lab <- as.numeric(ak_hex_to_lab(dark)[1, ])
  theme_lab <- as.numeric(ak_hex_to_lab(theme)[1, ])
  light_anchor <- ak_blend_lab(light, "#FAFAF7", if (light_lab[1] < 88) 0.38 else 0.18)
  dark_anchor <- ak_adjust_lab(
    dark,
    lightness = min(dark_lab[1], 28),
    chroma = max(ak_chroma(dark_lab), ak_chroma(theme_lab) * 0.65)
  )
  anchors <- c(light_anchor, theme, dark_anchor)
  anchor_lab <- ak_hex_to_lab(anchors)
  anchors <- anchors[order(anchor_lab[, 1], decreasing = TRUE)]
  ak_interpolate_monotone_lightness(anchors, n, descending = TRUE)
}

ak_diverging <- function(name, n = 257) {
  rows <- ak_core_rows(name)
  theme <- rows$hex[rows$role == "theme"][1]
  theme_lab <- as.numeric(ak_hex_to_lab(theme)[1, ])
  accent_candidates <- rows$hex[
    !(rows$role %in% c("theme", "neutral", "light")) &
      rows$hex != theme
  ]
  if (!length(accent_candidates)) {
    accent_candidates <- rows$hex[rows$role == "accent_1"][1]
  }
  if (is.na(accent_candidates[1])) {
    accent_candidates <- rows$hex[rows$role == "accent_2"][1]
  }
  if (is.na(accent_candidates[1])) {
    accent_candidates <- rows$hex[rows$role == "dark"][1]
  }
  score <- vapply(accent_candidates, function(color) {
    ak_lab_distance(color, theme) + ak_chroma(as.numeric(ak_hex_to_lab(color)[1, ])) * 0.2
  }, numeric(1))
  accent <- accent_candidates[which.max(score)]
  accent_lab <- as.numeric(ak_hex_to_lab(accent)[1, ])
  neutral <- rows$hex[rows$role == "neutral"][1]
  endpoint_l <- min(58, max(42, (theme_lab[1] + accent_lab[1]) / 2))
  endpoint_chroma <- min(64, max(28, min(ak_chroma(theme_lab), ak_chroma(accent_lab)) * 0.92))
  left <- ak_adjust_lab(
    accent,
    lightness = endpoint_l,
    chroma = max(endpoint_chroma, ak_chroma(accent_lab) * 0.82)
  )
  right <- ak_adjust_lab(
    theme,
    lightness = endpoint_l,
    chroma = max(endpoint_chroma, ak_chroma(theme_lab) * 0.82)
  )
  center <- if (is.na(neutral)) {
    "#F5F4F0"
  } else {
    ak_blend_lab(neutral, "#F5F4F0", 0.72)
  }
  center <- ak_adjust_lab(center, lightness = 94, chroma = min(ak_chroma(as.numeric(ak_hex_to_lab(center)[1, ])), 4))
  if (n <= 1) {
    return(utils::head(center, n))
  }
  if (n %% 2 == 1) {
    side <- floor(n / 2) + 1
    left_half <- ak_interpolate_monotone_lightness(c(left, center), side, descending = FALSE)
    right_half <- ak_interpolate_monotone_lightness(c(center, right), side, descending = TRUE)
    return(c(utils::head(left_half, -1), right_half))
  }
  side <- n / 2
  c(
    ak_interpolate_monotone_lightness(c(left, center), side, descending = FALSE),
    ak_interpolate_monotone_lightness(c(center, right), side, descending = TRUE)
  )
}

ak_operator_colors <- function(names) {
  stats::setNames(vapply(names, function(x) {
    ak_theme_color(x)
  }, character(1)), names)
}

ak_category <- function(n, seed = NULL, large_n = c("warn", "grouped", "force"), optimize = TRUE) {
  large_n <- match.arg(large_n)
  if (n > 30 && large_n == "warn") {
    warning("分类数量超过 30，建议切换到分组、分面或上层注释模式。", call. = FALSE)
  }
  palettes <- ak_palettes()
  anchors <- palettes[palettes$palette_type == "categorical_anchor", , drop = FALSE]
  anchors <- anchors[order(anchors$operator_id), , drop = FALSE]
  colors <- anchors$hex
  if (!is.null(seed)) {
    shift <- seed %% length(colors)
    if (shift > 0) colors <- c(colors[(shift + 1):length(colors)], colors[1:shift])
  }
  if (optimize) return(ak_farthest_colors(colors, n, seed_color = colors[1]))
  if (n <= length(colors)) {
    return(colors[seq_len(n)])
  }
  grDevices::colorRampPalette(colors, space = "Lab")(n)
}

ak_celltype_colors <- function(celltypes, palette = "six_star", seed = 1, large_n = "warn") {
  levels <- unique(as.character(celltypes))
  colors <- ak_category(length(levels), seed = seed, large_n = large_n)
  stats::setNames(colors, levels)
}

ak_themed_subtype_colors <- function(subtype_map, group_operator, candidates_per_group = 96) {
  result <- c()
  for (group in names(subtype_map)) {
    subtypes <- subtype_map[[group]]
    operator <- group_operator[group]
    subtype_count <- length(subtypes)
    candidates <- ak_theme_candidate_pool(operator, max(candidates_per_group, subtype_count * 18))
    candidates <- ak_readable_on_white(candidates)
    theme <- ak_theme_color(operator)
    seed_color <- if (theme %in% candidates) theme else NULL
    picked <- ak_farthest_colors(candidates, length(subtypes), seed_color = seed_color)
    result[subtypes] <- picked
  }
  result
}

ak_display <- function(name, n = NULL) {
  colors <- ak_palette(name, n = n)
  old <- graphics::par(no.readonly = TRUE)
  on.exit(graphics::par(old))
  graphics::par(mar = c(1, 1, 1, 1))
  graphics::plot(
    seq_along(colors),
    rep(1, length(colors)),
    col = colors,
    pch = 15,
    cex = 8,
    axes = FALSE,
    xlab = "",
    ylab = ""
  )
  invisible(colors)
}

arkplatte <- function(name, n = NULL, type = c("core", "seq", "div")) {
  type <- match.arg(type)
  if (type == "seq") return(ak_sequential(name, if (is.null(n)) 256 else n))
  if (type == "div") return(ak_diverging(name, if (is.null(n)) 257 else n))
  ak_palette(name, n = n, type = "core")
}

arkplatte_seq <- function(name, n = 256) {
  ak_sequential(name, n)
}

arkplatte_div <- function(name, n = 257) {
  ak_diverging(name, n)
}

arkplatte_cat <- function(n, seed = NULL, large_n = c("warn", "grouped", "force"), optimize = TRUE) {
  ak_category(n, seed = seed, large_n = large_n, optimize = optimize)
}

arkplatte_cell <- function(celltypes, seed = 1, large_n = "warn") {
  ak_celltype_colors(celltypes, seed = seed, large_n = large_n)
}

arkplatte_sub <- function(subtype_map, group_operator, candidates_per_group = 96) {
  ak_themed_subtype_colors(subtype_map, group_operator, candidates_per_group = candidates_per_group)
}

arkplatte_names <- function(rarity = NULL) {
  ak_names(rarity = rarity)
}

arkplatte_info <- function(name) {
  ak_info(name)
}

arkplatte_theme <- function(names) {
  ak_operator_colors(names)
}

arkplatte_show <- function(name, n = NULL) {
  ak_display(name, n = n)
}
