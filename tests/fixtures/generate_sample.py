"""
回帰テスト用の合成トラッカー画面画像を生成するスクリプト。

実際のゲーム画面は個人の成績データを含み公開できないため、config.json の
regions座標を使って、各項目の位置にダミーの数値テキストを描画した合成画像を作る。
生成物（画像・期待値JSON）は共にリポジトリにコミットして良い（個人情報を含まない）。

実行方法:
    python tests/fixtures/generate_sample.py
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from main import convert_value  # noqa: E402

FIXTURE_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.join(FIXTURE_DIR, "..", "..")
IMAGE_PATH = os.path.join(FIXTURE_DIR, "sample_input", "1.png")
EXPECTED_PATH = os.path.join(FIXTURE_DIR, "expected_values.json")

# 主要OS標準のBoldフォントを優先的に探し、見つからなければPillow内蔵フォントへ
# フォールバックする（どの環境でもスクリプトが再実行できるようにするため）
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\segoeuib.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
]

# 画像に描画する表示テキスト（OCRが読み取る文字列そのもの）。
# 期待値（変換後の値）はこの文字列から convert_value() で自動算出するため、
# 表示テキストと期待値が食い違うことはない。
RAW_TEXT = {
    "career_games": "17.8K",
    "career_wins": "827",
    "career_top5": "5.0K",
    "career_damage": "6,873,432",
    "career_damage_max": "3,205",
    "career_damage_avg": "385.39",
    "career_kills": "14,266",
    "career_deaths": "17,920",
    "career_kdr": "0.8",
    "career_max_kills": "14",
    "career_knockdowns": "19,159",
    "career_assists": "11,919",
    "career_win_streak": "3",
    "career_revives": "7,023",
    "career_respawns": "1,851",
    "season_games": "372",
    "season_wins": "14",
    "season_top5": "129",
    "season_damage": "119,814",
    "season_damage_max": "1,748",
    "season_damage_avg": "322.08",
    "season_kills": "201",
    "season_deaths": "324",
    "season_kdr": "0.62",
    "season_max_kills": "6",
    "season_knockdowns": "258",
    "season_assists": "122",
    "season_win_streak": "2",
    "season_revives": "119",
    "season_respawns": "28",
}

SEASON = "1"


def find_font_path():
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return path
    return None


def load_font(size):
    path = find_font_path()
    if path:
        return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def fit_font(text, rect_w, rect_h, draw, padding=10):
    size = 60
    while size > 8:
        font = load_font(size)
        bbox = draw.textbbox((0, 0), text, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if w <= rect_w - padding and h <= rect_h - padding:
            return font, bbox
        size -= 1
    return font, bbox


def draw_regions(draw, regions):
    for name, rect in regions.items():
        text = RAW_TEXT[name]
        x1, y1, x2, y2 = rect
        rect_w, rect_h = x2 - x1, y2 - y1

        font, bbox = fit_font(text, rect_w, rect_h, draw)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

        origin_x = x1 + (rect_w - text_w) // 2 - bbox[0]
        origin_y = y1 + (rect_h - text_h) // 2 - bbox[1]

        draw.text((origin_x, origin_y), text, font=font, fill=(255, 255, 255))


def main():
    config_path = os.path.join(REPO_ROOT, "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    base_width = config["base_width"]
    base_height = config["base_height"]
    regions = config["regions"]

    missing = set(regions.keys()) - set(RAW_TEXT.keys())
    if missing:
        raise SystemExit(f"RAW_TEXTに未定義の項目があります: {missing}")

    img = Image.new("RGB", (base_width, base_height), (30, 24, 20))
    draw = ImageDraw.Draw(img)
    draw_regions(draw, regions)

    os.makedirs(os.path.dirname(IMAGE_PATH), exist_ok=True)
    img.save(IMAGE_PATH)
    print(f"生成: {IMAGE_PATH} (font={find_font_path() or 'Pillow default'})")

    expected = {"season": SEASON}
    for name in regions:
        expected[name] = convert_value(RAW_TEXT[name])

    with open(EXPECTED_PATH, "w", encoding="utf-8") as f:
        json.dump(expected, f, ensure_ascii=False, indent=2)
    print(f"生成: {EXPECTED_PATH}")


if __name__ == "__main__":
    main()
