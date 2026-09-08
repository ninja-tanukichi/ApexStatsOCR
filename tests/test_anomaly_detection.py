"""
異常値検出ロジック（main.pyの統計的外れ値検知・修正候補算出）のテスト。
EasyOCRを使わないため高速に実行できる。
"""
import json

import pandas as pd

from main import (
    CORRECTIONS_PLACEHOLDER,
    _build_corrections_snippet,
    _format_warning_tail,
    detect_statistical_outliers,
    suggest_correction,
)


class _ListLogger:
    """テスト用の簡易ロガー。warning呼び出しをリストに記録する。"""

    def __init__(self):
        self.warnings = []

    def warning(self, msg, *args):
        self.warnings.append(msg % args if args else msg)


def test_suggest_correction_finds_divisor_that_fits():
    # median=10, mad=1 の分布で、1000は/100すると10.0になり中央値に一致する
    candidate, divisor = suggest_correction(1000, median=10, mad=1, threshold=3.5)
    assert divisor == 100
    assert candidate == 10.0


def test_suggest_correction_returns_none_when_no_divisor_fits():
    # どの桁で割っても中央値から大きく外れたままのケース
    candidate, divisor = suggest_correction(999_999, median=10, mad=1, threshold=3.5)
    assert candidate is None
    assert divisor is None


def test_detect_statistical_outliers_includes_suggested_value():
    # season_kdrを模した列: 大半が0.5〜0.9、1件だけ44.0（桁が飛んだ想定の異常値）
    df = pd.DataFrame({
        "season": [str(i) for i in range(1, 7)],
        "season_kdr": [0.5, 0.6, 0.7, 0.8, 0.9, 44.0],
    })

    anomalies = detect_statistical_outliers(df, ["season_kdr"], threshold=3.5)

    assert len(anomalies) == 1
    anomaly = anomalies[0]
    assert anomaly["season"] == "6"
    assert anomaly["value"] == 44.0
    assert anomaly["suggested_value"] == 0.44
    assert "修正候補" in anomaly["detail"]


def test_detect_statistical_outliers_no_suggestion_field_omitted_when_normal():
    df = pd.DataFrame({
        "season": [str(i) for i in range(1, 6)],
        "season_kdr": [0.5, 0.6, 0.7, 0.8, 0.9],
    })

    anomalies = detect_statistical_outliers(df, ["season_kdr"], threshold=3.5)

    assert anomalies == []


def test_format_warning_tail_does_not_round_suggested_value():
    # :g だと有効桁6桁に丸められ、貼り付け用JSON側の値とズレていた
    anomaly = {"rule": "statistical_outlier", "suggested_value": 337101.9}

    assert _format_warning_tail(anomaly) == "suggested_value=337101.9"


def test_build_corrections_snippet_uses_suggested_value():
    anomalies = [
        {"season": "11", "column": "season_kdr", "value": 112.0,
         "rule": "statistical_outlier", "suggested_value": 1.12},
    ]

    snippet = json.loads(_build_corrections_snippet(anomalies, _ListLogger()))

    assert snippet == {
        "11": {"season_kdr": {"observed": 112.0, "corrected": 1.12}},
    }


def test_build_corrections_snippet_placeholder_when_no_suggestion():
    anomalies = [
        {"season": "20", "column": "season_kdr", "value": 211.0,
         "rule": "statistical_outlier", "suggested_value": None},
    ]

    snippet = json.loads(_build_corrections_snippet(anomalies, _ListLogger()))

    assert snippet["20"]["season_kdr"]["corrected"] == CORRECTIONS_PLACEHOLDER


def test_build_corrections_snippet_merges_multiple_columns_same_season():
    anomalies = [
        {"season": "29", "column": "season_games", "value": 771.0,
         "rule": "statistical_outlier", "suggested_value": 77.1},
        {"season": "29", "column": "season_damage", "value": 344449.0,
         "rule": "statistical_outlier", "suggested_value": 34444.9},
    ]

    snippet = json.loads(_build_corrections_snippet(anomalies, _ListLogger()))

    assert set(snippet["29"].keys()) == {"season_games", "season_damage"}


def test_build_corrections_snippet_excludes_non_statistical_rules():
    anomalies = [
        {"season": "12", "column": "career_games", "value": "",
         "rule": "type", "detail": "OCR結果が数値に変換できていません"},
    ]

    assert _build_corrections_snippet(anomalies, _ListLogger()) is None


def test_build_corrections_snippet_warns_and_keeps_last_on_collision():
    # 同一season+columnが複数検出された場合（例: 重複ファイル名で同じシーズン番号に
    # 解釈される画像が2枚あった場合）、corrections.jsonのスキーマ上どのみち1件しか
    # 表現できないため後勝ちで上書きしつつ、黙って消さずWARNINGで知らせる
    anomalies = [
        {"season": "9", "column": "season_kdr", "value": 44.0,
         "rule": "statistical_outlier", "suggested_value": 0.44},
        {"season": "9", "column": "season_kdr", "value": 99.0,
         "rule": "statistical_outlier", "suggested_value": 0.99},
    ]
    logger = _ListLogger()

    snippet = json.loads(_build_corrections_snippet(anomalies, logger))

    assert snippet["9"]["season_kdr"]["observed"] == 99.0
    assert len(logger.warnings) == 1
    assert "season=9" in logger.warnings[0]
    assert "column=season_kdr" in logger.warnings[0]
