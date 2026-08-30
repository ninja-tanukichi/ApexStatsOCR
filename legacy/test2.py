import os
import re
import json

import cv2
import easyocr
import pandas as pd


with open(
    "config.json",
    "r",
    encoding="utf-8"
) as f:

    CONFIG = json.load(f)


INPUT_DIR = CONFIG["input_dir"]
OUTPUT_FILE = CONFIG["output_file"]

REGIONS = CONFIG["regions"]

OCR_CONFIG = CONFIG["ocr"]


reader = easyocr.Reader(
    OCR_CONFIG["languages"],
    gpu=OCR_CONFIG["gpu"]
)


def preprocess(img):

    gray = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2GRAY
    )

    gray = cv2.resize(
        gray,
        None,
        fx=OCR_CONFIG["resize_scale"],
        fy=OCR_CONFIG["resize_scale"],
        interpolation=cv2.INTER_CUBIC
    )

    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    _, binary = cv2.threshold(
        gray,
        170,
        255,
        cv2.THRESH_BINARY
    )

    return binary


def normalize(text):

    text = text.upper()

    text = text.replace("O", "0")
    text = text.replace("I", "1")
    text = text.replace("L", "1")
    text = text.replace("己", "2")
    text = text.replace("こ", "2")

    return text


def block_ocr(img, rect):

    x1, y1, x2, y2 = rect

    crop = img[y1:y2, x1:x2]

    crop = preprocess(crop)

    result = reader.readtext(
        crop,
        detail=0,
        paragraph=False,
        allowlist="0123456789.,KkMm"
    )
    cv2.imwrite(
    f"debug_{rect[0]}_{rect[1]}.png",
    crop
)

    return [
        normalize(x)
        for x in result
    ]


def parse_km(value):

    value = value.replace(",", "")

    if value.endswith("K"):

        return int(
            float(
                value[:-1]
            ) * 1000
        )

    if value.endswith("M"):

        return int(
            float(
                value[:-1]
            ) * 1000000
        )

    try:

        if "." in value:
            return float(value)

        return int(value)

    except:

        return None


def process_image(path):

    img = cv2.imread(path)

    top = block_ocr(
        img,
        REGIONS["top_stats"]
    )

    damage = block_ocr(
        img,
        REGIONS["damage_stats"]
    )

    kills = block_ocr(
        img,
        REGIONS["kill_stats"]
    )

    bottom = block_ocr(
        img,
        REGIONS["bottom_stats"]
    )

    print()
    print("TOP")
    print(top)

    print()
    print("DAMAGE")
    print(damage)

    print()
    print("KILLS")
    print(kills)

    print()
    print("BOTTOM")
    print(bottom)

    #
    # 数値だけ抽出
    #
    top_nums = []

    for x in top:

        if re.fullmatch(
            r'[\d,.KM]+',
            x
        ):
            top_nums.append(
                parse_km(x)
            )

    damage_nums = []

    for x in damage:

        if re.fullmatch(
            r'[\d,.KM]+',
            x
        ):
            damage_nums.append(
                parse_km(x)
            )

    kill_nums = []

    for x in kills:

        if re.fullmatch(
            r'[\d,.KM]+',
            x
        ):
            kill_nums.append(
                parse_km(x)
            )

    bottom_nums = []

    for x in bottom:

        if re.fullmatch(
            r'[\d,.KM]+',
            x
        ):
            bottom_nums.append(
                parse_km(x)
            )

    row = {}

    #
    # 上段
    #
    if len(top_nums) >= 3:

        row["games"] = top_nums[0]
        row["wins"] = top_nums[1]
        row["top5"] = top_nums[2]

    #
    # ダメージ
    #
    if len(damage_nums) >= 3:

        row["damage"] = damage_nums[0]
        row["damage_max"] = damage_nums[1]
        row["damage_avg"] = damage_nums[2]

    #
    # キル
    #
    if len(kill_nums) >= 3:

        row["kills"] = kill_nums[0]
        row["deaths"] = kill_nums[1]
        row["kdr"] = kill_nums[2]

    #
    # 下段
    #
    if len(bottom_nums) >= 6:

        row["max_kills"] = bottom_nums[0]
        row["max_winstreak"] = bottom_nums[1]
        row["knockdowns"] = bottom_nums[2]
        row["revives"] = bottom_nums[3]
        row["assists"] = bottom_nums[4]
        row["respawns"] = bottom_nums[5]

    return row


rows = []

for file in os.listdir(INPUT_DIR):

    if not file.lower().endswith(
        (".png", ".jpg", ".jpeg")
    ):
        continue

    path = os.path.join(
        INPUT_DIR,
        file
    )

    row = process_image(path)

    season = re.search(
        r'(\d+)',
        file
    )

    row["season"] = (
        season.group(1)
        if season
        else ""
    )

    rows.append(row)

df = pd.DataFrame(rows)

os.makedirs(
    os.path.dirname(
        OUTPUT_FILE
    ),
    exist_ok=True
)

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print(df)