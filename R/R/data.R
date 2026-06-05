ak_data_path <- function(filename) {
  file.path(system.file("extdata", package = "arknightsPalette"), filename)
}

ak_read_csv <- function(filename) {
  path <- ak_data_path(filename)
  if (!file.exists(path)) {
    stop("缺少数据文件：", filename, call. = FALSE)
  }
  utils::read.csv(path, stringsAsFactors = FALSE, fileEncoding = "UTF-8")
}

ak_operators <- function() {
  ak_read_csv("operators.csv")
}

ak_palettes <- function() {
  ak_read_csv("palettes.csv")
}

