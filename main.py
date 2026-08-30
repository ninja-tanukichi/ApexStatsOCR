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


# =========================
# 異常値検出
# =========================
# career_kdr / career_damage_avg 等の比率列は、キャリブレーション上の
# 「その時点までの累計」であり単調増加を保証できないため単調性チェックの対象外とする
RATIO_SUFFIXES = ("_kdr", "_avg")


def is_ratio_column(name):
    return name.endswith(RATIO_SUFFIXES)


def to_number(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    return None


def detect_type_anomalies(df, columns):
    anomalies = []
    for col in columns:
        for idx, value in df[col].items():
            if to_number(value) is None:
                anomalies.append({
                    "season": df.at[idx, "season"],
                    "column": col,
                    "value": value,
                    "rule": "type",
                    "detail": "OCR結果が数値に変換できていません",
                })
    return anomalies


def detect_monotonicity_anomalies(df, columns):
    anomalies = []
    season_num = pd.to_numeric(df["season"], errors="coerce")
    ordered = df.assign(_season_num=season_num).sort_values("_season_num")

    for col in columns:
        prev_value = None
        prev_season = None
        for _, row in ordered.iterrows():
            value = to_number(row[col])
            if value is None:
                continue
            if prev_value is not None and value < prev_value:
                anomalies.append({
                    "season": row["season"],
                    "column": col,
                    "value": value,
                    "rule": "monotonicity",
                    "detail": f"season {prev_season}の値({prev_value})より減少しています（累積値のため通常は減らない）",
                })
            prev_value = value
            prev_season = row["season"]
    return anomalies


# Iglewicz & Hoaglin (1993) の推奨値。中央値絶対偏差(MAD)ベースの
# 修正z-scoreにより、固定の値域を決め打ちせずデータのばらつきから外れ値を判定する
DEFAULT_MAD_Z_THRESHOLD = 3.5
MIN_SAMPLES_FOR_STATS = 4


def detect_statistical_outliers(df, columns, threshold):
    anomalies = []
    for col in columns:
        idxs, values = [], []
        for idx, raw in df[col].items():
            value = to_number(raw)
            if value is not None:
                idxs.append(idx)
                values.append(value)

        if len(values) < MIN_SAMPLES_FOR_STATS:
            continue

        arr = np.array(values, dtype=float)
        median = np.median(arr)
        mad = np.median(np.abs(arr - median))

        if mad == 0:
            continue

        modified_z = 0.6745 * (arr - median) / mad

        for idx, z, value in zip(idxs, modified_z, values):
            if abs(z) > threshold:
                anomalies.append({
                    "season": df.at[idx, "season"],
                    "column": col,
                    "value": value,
                    "rule": "statistical_outlier",
                    "detail": f"中央値={median:.2f}から外れ値（修正z-score={z:.2f}）",
                })
    return anomalies


def validate_anomalies(df, regions, anomaly_config, logger):
    value_columns = list(regions.keys())
    ratio_columns = [c for c in value_columns if is_ratio_column(c)]
    career_count_columns = [
        c for c in value_columns
        if c.startswith("career_") and c not in ratio_columns
    ]
    season_columns = [c for c in value_columns if c.startswith("season_")]

    threshold = anomaly_config.get("mad_z_threshold", DEFAULT_MAD_Z_THRESHOLD)

    anomalies = (
        detect_type_anomalies(df, value_columns)
        + detect_monotonicity_anomalies(df, career_count_columns)
        + detect_statistical_outliers(df, season_columns, threshold)
    )

    if not anomalies:
        logger.info("異常値検出: 問題ありません")
        return anomalies

    logger.warning("異常値検出: %d件の疑わしい値を検出しました", len(anomalies))
    for a in anomalies:
        logger.warning(
            "  season=%s column=%s value=%s rule=%s detail=%s",
            a["season"], a["column"], a["value"], a["rule"], a["detail"],
        )
    return anomalies


def main():
    config = load_config("config.json")
    logger = init_logger(config.get("log_file", "ocr.log"))

    base_width = config["base_width"]
    base_height = config["base_height"]
    input_dir = config["input_dir"]
    output_file = config["output_file"]
    ocr_config = config["ocr"]
    regions = config["regions"]
    anomaly_config = config.get("anomaly_detection", {})

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
    df = save_csv(rows, output_file, columns, logger)
    validate_anomalies(df, regions, anomaly_config, logger)


if __name__ == "__main__":
    main()


