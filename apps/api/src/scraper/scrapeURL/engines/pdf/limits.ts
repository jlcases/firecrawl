import { config } from "../../../../config";

const BYTES_PER_MEBIBYTE = 1024 * 1024;

export const PDF_DOWNLOAD_MAX_FILE_SIZE =
  config.PDF_DOWNLOAD_MAX_FILE_SIZE_MB * BYTES_PER_MEBIBYTE;
