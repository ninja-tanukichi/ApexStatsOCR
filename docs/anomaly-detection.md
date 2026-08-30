# 異常値検出アルゴリズム

`main.py` の異常値自動検出ロジック（型チェック・単調性チェック・統計的外れ値検知・修正候補の提示）の実装詳細をまとめたもの。運用手順（ユーザー向け）は [README.md の「異常値の自動検出」](../README.md#異常値の自動検出)を参照。

## 検出ルール

### 1. 型チェック（`detect_type_anomalies`）

対象: `season`を除く全列。

`convert_value()` がOCRテキストを数値変換できなかった場合、値は文字列のまま残る。各列の値がint/floatかどうかを判定し、そうでなければ異常として記録する。

### 2. 単調性チェック（`detect_monotonicity_anomalies`）

対象: `career_*`のうち、比率列（列名が`_kdr`または`_avg`で終わるもの。例: `career_kdr`, `career_damage_avg`）を除いた純粋な累積カウンタ列。

`career_*`系はプレイヤーの「これまでの累計」を表すため、season番号の昇順に並べたとき値が前より減っていれば異常とみなす。

比率列を除外する理由: `career_kdr`・`career_damage_avg`は累積キル数/累積デス数のような比率であり、分子分母の増加速度によっては一時的に前より下がることが理論上あり得るため、単調性チェックの対象外としている。

### 3. 統計的外れ値検知（`detect_statistical_outliers`）

対象: `season_*`列（シーズンごとの独立した実測値のため、シーズン間で統計的に比較可能）。

中央値絶対偏差（MAD: Median Absolute Deviation）に基づく修正z-score（Modified Z-Score）で判定する。

```python
median = median(値)
mad = median(|値 - median|)
modified_z = 0.6745 * (値 - median) / mad
```

`0.6745`は標準正規分布の75パーセンタイル点（`Φ⁻¹(0.75)`）で、MADを標準偏差相当のスケールに揃えるための定数。[Iglewicz & Hoaglin (1993)](https://www.itl.nist.gov/div898/handbook/eda/section3/eda35h.htm)が提唱した手法で、閾値には推奨値である`3.5`を採用している（`config.json`の`anomaly_detection.mad_z_threshold`で変更可能）。

中央値・MADを使う理由: 平均・標準偏差は外れ値自体に引っ張られて歪むため、外れ値の影響を受けにくい頑健な統計量を使うことで、少数の異常値が混ざっていても正常なデータのばらつきを正しく捉えられる。

ガード条件:

- サンプル数が4未満（`MIN_SAMPLES_FOR_STATS`）の列は判定をスキップする。中央値・MADが安定して計算できないため
- MADが0（値が完全に同一）の場合もスキップする。ばらつきがゼロだと判定不能なため

## 修正候補の提示（`suggest_correction`）

統計的外れ値として検出された値について、小数点の桁がOCRでずれるケース（例: `0.44`が`44`と誤読される）を想定し、元の値を10・100・1000で割った候補のうち、統計的に妥当な範囲（`|修正z-score| <= threshold`）に収まる最初の値を「修正候補」として提示する。

```python
CORRECTION_DIVISORS = (10, 100, 1000)

def suggest_correction(value, median, mad, threshold):
    for divisor in CORRECTION_DIVISORS:
        candidate = value / divisor
        z = 0.6745 * (candidate - median) / mad
        if abs(z) <= threshold:
            return candidate, divisor
    return None, None
```

あくまで統計的な推測であり正しさは保証されない。CSVを自動修正することはなく、`ocr.log`に候補値を出力するのみ。

## 実データでの検証例

このロジックを実データに適用したところ、以下の3件を検出した（詳細は[CHANGELOG.md](../CHANGELOG.md)のv1.1.0/v1.4.0を参照）。

| season | 列 | 検出値 | 修正候補 | 実際の原因 |
| --- | --- | --- | --- | --- |
| 9 | season_kdr | 44.0 | 0.44 | EasyOCRが小数点を認識できず`['0', '44']`を単純結合していた |
| 24 | season_damage_avg | 1431.4 | 143.14 | 小数点の桁ズレ |
| 10 | season_damage_avg | 32208.0 | 322.08 | 小数点の桁ズレ |

3件とも手計算した推定値と修正候補が完全に一致することを確認済み。
