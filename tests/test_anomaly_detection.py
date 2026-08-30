"""
異常値検出ロジック（main.pyの統計的外れ値検知・修正候補算出）のテスト。
EasyOCRを使わないため高速に実行できる。
"""
import pandas as pd

from main import detect_statistical_outliers, suggest_correction


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
