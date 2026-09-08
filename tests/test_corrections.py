"""
load_corrections() / apply_corrections() の挙動のテスト。
"""
import json
import logging
import os

from main import apply_corrections, load_corrections

logger = logging.getLogger("ApexStatsOCR.test")
logger.addHandler(logging.NullHandler())


def test_load_corrections_creates_empty_file_when_missing(tmp_path):
    path = str(tmp_path / "corrections.json")

    result = load_corrections(path, logger)

    assert result == {}
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        assert json.load(f) == {}


def test_load_corrections_reads_existing_file(tmp_path):
    path = tmp_path / "corrections.json"
    path.write_text(
        json.dumps({"9": {"season_kdr": {"observed": 44.0, "corrected": 0.44}}}),
        encoding="utf-8",
    )

    result = load_corrections(str(path), logger)

    assert result == {"9": {"season_kdr": {"observed": 44.0, "corrected": 0.44}}}


def test_apply_corrections_replaces_value_when_observed_matches():
    rows = [{"season": "9", "season_kdr": 44.0}]
    corrections = {"9": {"season_kdr": {"observed": 44.0, "corrected": 0.44}}}

    apply_corrections(rows, corrections, logger)

    assert rows[0]["season_kdr"] == 0.44


def test_apply_corrections_skips_when_observed_does_not_match():
    rows = [{"season": "9", "season_kdr": 37.0}]
    corrections = {"9": {"season_kdr": {"observed": 44.0, "corrected": 0.44}}}

    apply_corrections(rows, corrections, logger)

    assert rows[0]["season_kdr"] == 37.0


def test_apply_corrections_ignores_unrelated_seasons_and_columns():
    rows = [{"season": "10", "season_kdr": 1.0, "season_games": 100}]
    corrections = {"9": {"season_kdr": {"observed": 44.0, "corrected": 0.44}}}

    apply_corrections(rows, corrections, logger)

    assert rows[0] == {"season": "10", "season_kdr": 1.0, "season_games": 100}
