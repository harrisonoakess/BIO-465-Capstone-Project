library(tidyverse)
library(jsonlite)

args = commandArgs(trailingOnly=TRUE)
input_folder = args[1]

print(input_folder)
