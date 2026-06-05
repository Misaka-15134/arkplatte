ak_require_ggplot2 <- function() {
  if (!requireNamespace("ggplot2", quietly = TRUE)) {
    stop("需要安装 ggplot2。", call. = FALSE)
  }
}

scale_color_arknights <- function(palette = "伊内丝", discrete = TRUE, n = NULL, ...) {
  ak_require_ggplot2()
  if (discrete) {
    values <- if (palette == "six_star") ak_category(ifelse(is.null(n), 30, n)) else ak_palette(palette, n = n)
    ggplot2::scale_color_manual(values = values, ...)
  } else {
    ggplot2::scale_color_gradientn(colors = ak_sequential(palette, n = ifelse(is.null(n), 256, n)), ...)
  }
}

scale_fill_arknights <- function(palette = "伊内丝", discrete = TRUE, n = NULL, ...) {
  ak_require_ggplot2()
  if (discrete) {
    values <- if (palette == "six_star") ak_category(ifelse(is.null(n), 30, n)) else ak_palette(palette, n = n)
    ggplot2::scale_fill_manual(values = values, ...)
  } else {
    ggplot2::scale_fill_gradientn(colors = ak_sequential(palette, n = ifelse(is.null(n), 256, n)), ...)
  }
}

scale_color_ak_continuous <- function(palette = "伊内丝", n = 256, ...) {
  ak_require_ggplot2()
  ggplot2::scale_color_gradientn(colors = ak_sequential(palette, n = n), ...)
}

scale_fill_ak_continuous <- function(palette = "伊内丝", n = 256, ...) {
  ak_require_ggplot2()
  ggplot2::scale_fill_gradientn(colors = ak_sequential(palette, n = n), ...)
}

scale_color_ak_diverging <- function(palette = "伊内丝", n = 257, ...) {
  ak_require_ggplot2()
  ggplot2::scale_color_gradientn(colors = ak_diverging(palette, n = n), ...)
}

scale_fill_ak_diverging <- function(palette = "伊内丝", n = 257, ...) {
  ak_require_ggplot2()
  ggplot2::scale_fill_gradientn(colors = ak_diverging(palette, n = n), ...)
}

