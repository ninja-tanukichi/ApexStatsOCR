import json
import logging
import os
import re
import sys

import cv2
import easyocr
import numpy as np
import pandas as pd


# cv2.imread/imwriteはWindowsで非ASCII(日本語等)パスを扱えず無音で失敗するため、
# np.fromfile/tofile経由でエンコード・デコードする
def imread_unicode(path):
    data = np.fromfile(path, dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def imwrite_unicode(path, img):
    ext = os.path.splitext(path)[1]
    ok, buf = cv2.imencode(ext, img)
    if ok:
        buf.tofile(path)
    return ok


def init_logger(log_file="ocr.log"):
    logger = logging.getLogger("ApexStatsOCR")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def load_config(config_path="config.json"):
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def init_reader(ocr_config):
    return easyocr.Reader(
        ocr_config["languages"],
        gpu=ocr_config.get("gpu", False),
    )


# =========================
# 前処理
# =========================

def preprocess(img, resize_scale):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(
        gray,
        None,
        fx=resize_scale,
        fy=resize_scale,
        interpolation=cv2.INTER_CUBIC,
    )
    return gray

# 2値化
#    gray = cv2.GaussianBlur(
#        gray,
#        (3, 3),
#        0
#    )
#
#    _, binary = cv2.threshold(
#        gray,
#        OCR_CONFIG["threshold"],
#        255,
#        cv2.THRESH_BINARY
#    )
#
#    return binary


# =========================
# OCR補正
# =========================

def normalize_text(text):

    text = text.upper()

    replacements = {
        "O": "0",
        "I": "1",
        "L": "1",
        "S": "5",
        "B": "8",
        "己": "2",
        "こ": "2"
    }

    for src, dst in replacements.items():
        text = text.replace(src, dst)

    return text


# =========================
# K/M対応
# =========================

def convert_value(text):

    if text is None:
        return ""

    #text = normalize_text(text)

    text = text.replace(",", "")

    text = text.strip()

    if not text:
        return ""

    try:

        if text.endswith("K"):

            return int(
                float(text[:-1]) * 1000
            )

        if text.endswith("M"):

            return int(
                float(text[:-1]) * 1000000
            )

        if "." in text:
            return float(text)

        return int(text)

    except:

        return text
    

# =========================
# ドット誤認対応
# =========================
def merge_decimal(parts):

    if len(parts) == 3:

        if parts[1] in [
            "7",
            ".",
            ","
        ]:
            return f"{parts[0]}.{parts[2]}"

    return "".join(parts)


# =========================
# 解像度補正
# =========================

def scale_rect(
    rect,
    scale_x,
    scale_y
):

    x1, y1, x2, y2 = rect

    return (

        int(x1 * scale_x),
        int(y1 * scale_y),

        int(x2 * scale_x),
        int(y2 * scale_y)

    )


# =========================
# OCR
# =========================

def ocr_region(img, rect, scale_x, scale_y, name, reader, ocr_config, logger):
    rect = scale_rect(rect, scale_x, scale_y)
    x1, y1, x2, y2 = rect
    crop = img[y1:y2, x1:x2]

    if crop.size == 0:
        logger.error("%s: 領域エラー", name)
        return ""

    os.makedirs("debug", exist_ok=True)
    imwrite_unicode(f"debug/{name}.png", crop)

    crop = preprocess(crop, ocr_config["resize_scale"])

    result = reader.readtext(
        crop,
        detail=0,
        paragraph=False,
        allowlist=ocr_config.get("allowlist", "0123456789.,/KM"),
    )

    logger.info(result)
    text = merge_decimal(result)
    value = convert_value(text)
    logger.info("%s %-15s OCR='%s' VALUE='%s'", name, "", text, value)
    return value


# =========================
# メイン処理
# =========================

def process_image(file_path, reader, regions, base_width, base_height, ocr_config, logger):
    logger.info("\n解析中: %s", os.path.basename(file_path))

    img = imread_unicode(file_path)
    if img is None:
        logger.error("画像読込失敗: %s", os.path.basename(file_path))
        return None

    h, w = img.shape[:2]
    scale_x = w / base_width
    scale_y = h / base_height

    season_match = re.search(r"(\d+)", os.path.basename(file_path))
    row = {
        "season": season_match.group(1) if season_match else "",
    }

    for key, rect in regions.items():
        row[key] = ocr_region(
            img,
            rect,
            scale_x,
            scale_y,
            key,
            reader,
            ocr_config,
            logger,
        )

    return row


# =========================
# CSV出力
# =========================

def save_csv(rows, output_file, columns, logger):
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    df = pd.DataFrame(rows)
    df = df.reindex(columns=columns)
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    logger.info("\nCSV出力完了 %s", output_file)
    logger.info("\n%s", df)
    return df


def main():
    config = load_config("config.json")
    logger = init_logger(config.get("log_file", "ocr.log"))

    base_width = config["base_width"]
    base_height = config["base_height"]
    input_dir = config["input_dir"]
    output_file = config["output_file"]
    ocr_config = config["ocr"]
    regions = config["regions"]

    reader = init_reader(ocr_config)

    rows = []
    for file_name in os.listdir(input_dir):
        if not file_name.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        path = os.path.join(input_dir, file_name)
        row = process_image(path, reader, regions, base_width, base_height, ocr_config, logger)
        if row is not None:
            rows.append(row)

    columns = ["season"] + list(regions.keys())
    save_csv(rows, output_file, columns, logger)


if __name__ == "__main__":
    main()


