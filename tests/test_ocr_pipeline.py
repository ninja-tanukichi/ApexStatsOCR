"""
合成サンプル画像（tests/fixtures/sample_input/1.png）を使った回帰テスト。

実際のゲーム画面は個人の成績データを含み公開できないため、
tests/fixtures/generate_sample.py が生成したダミー画像を使う。
EasyOCRのモデルダウンロードが必要なため、初回のみインターネット接続が要る
（実行方法は README.md の「実行時の前提条件」を参照）。
"""
import json
import os

import pytest

from main import init_reader, load_config, process_image

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
SAMPLE_IMAGE = os.path.join(FIXTURE_DIR, "sample_input", "1.png")
EXPECTED_PATH = os.path.join(FIXTURE_DIR, "expected_values.json")


@pytest.fixture(scope="module")
def config():
    return load_config(os.path.join(os.path.dirname(__file__), "..", "config.json"))


@pytest.fixture(scope="module")
def expected():
    with open(EXPECTED_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def ocr_row(config):
    import logging

    logger = logging.getLogger("ApexStatsOCR.test")
    logger.addHandler(logging.NullHandler())

    reader = init_reader(config["ocr"])
    row = process_image(
        SAMPLE_IMAGE,
        reader,
        config["regions"],
        config["base_width"],
        config["base_height"],
        config["ocr"],
        logger,
    )
    assert row is not None, "サンプル画像の読み込みに失敗しました"
    return row


def test_sample_image_exists():
    assert os.path.exists(SAMPLE_IMAGE), (
        "サンプル画像が無い場合は `python tests/fixtures/generate_sample.py` で生成してください"
    )


def test_season_extracted_from_filename(ocr_row, expected):
    assert ocr_row["season"] == expected["season"]


@pytest.mark.parametrize("column", [
    "career_games", "career_wins", "career_top5",
    "career_damage", "career_damage_max", "career_damage_avg",
    "career_kills", "career_deaths", "career_kdr",
    "career_max_kills", "career_knockdowns", "career_assists",
    "career_win_streak", "career_revives", "career_respawns",
    "season_games", "season_wins", "season_top5",
    "season_damage", "season_damage_max", "season_damage_avg",
    "season_kills", "season_deaths", "season_kdr",
    "season_max_kills", "season_knockdowns", "season_assists",
    "season_win_streak", "season_revives", "season_respawns",
])
def test_ocr_value_matches_expected(ocr_row, expected, column):
    assert ocr_row[column] == expected[column]
