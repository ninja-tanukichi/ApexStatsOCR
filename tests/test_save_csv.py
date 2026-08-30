"""
save_csv()の既存ファイルバックアップ挙動のテスト。
EasyOCRを使わないため高速に実行できる。
"""
import glob
import logging
import os

from main import save_csv

logger = logging.getLogger("ApexStatsOCR.test")
logger.addHandler(logging.NullHandler())


def test_creates_csv_when_none_exists(tmp_path):
    output_file = str(tmp_path / "apex_stats.csv")

    save_csv([{"season": "1", "career_games": 100}], output_file, ["season", "career_games"], logger)

    assert os.path.exists(output_file)
    assert len(glob.glob(str(tmp_path / "*"))) == 1


def test_backs_up_existing_file_before_overwriting(tmp_path):
    output_file = str(tmp_path / "apex_stats.csv")

    save_csv([{"season": "1", "career_games": 100}], output_file, ["season", "career_games"], logger)
    save_csv([{"season": "2", "career_games": 200}], output_file, ["season", "career_games"], logger)

    files = sorted(os.path.basename(p) for p in glob.glob(str(tmp_path / "*")))
    assert len(files) == 2
    assert "apex_stats.csv" in files

    backup_files = [f for f in files if f != "apex_stats.csv"]
    assert len(backup_files) == 1
    assert backup_files[0].startswith("apex_stats_")
    assert backup_files[0].endswith(".csv")

    with open(output_file, encoding="utf-8-sig") as f:
        assert "200" in f.read()

    with open(tmp_path / backup_files[0], encoding="utf-8-sig") as f:
        assert "100" in f.read()


def test_repeated_runs_keep_all_backups(tmp_path):
    output_file = str(tmp_path / "apex_stats.csv")

    for season in ("1", "2", "3"):
        save_csv([{"season": season, "career_games": 1}], output_file, ["season", "career_games"], logger)

    files = glob.glob(str(tmp_path / "*"))
    assert len(files) == 3
