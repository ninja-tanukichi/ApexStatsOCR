# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.4.0] - 2026-08-30

### Added

- `main.py`: 統計的外れ値として検出した値について、10・100・1000で割った候補のうち統計的に妥当な
  範囲へ収まる最初の値を「修正候補」として`ocr.log`に併記するようにした（`suggest_correction`）。
  小数点の桁がOCRでずれるケース（例: `0.44`が`44`と誤読される）を想定したヒューリスティックであり、
  正しさは保証されない。CSVは自動修正せず、目視確認を前提とする。「要目視確認」の注記はサマリ行
  （`異常値検出: N件の疑わしい値を検出しました`）の末尾へ1回だけ出力し、各異常値の行は
  修正候補の値（`修正候補: <値>`）を出力するところまでとした
  - 実データ検証: 既知の3件の異常値（`season_kdr=44.0`→`0.44`、`season_damage_avg=1431.4`→`143.14`、
    `season_damage_avg=32208.0`→`322.08`）に対し、事前に手計算した推定値と完全に一致する候補を出力した
- `tests/test_anomaly_detection.py`を追加（`suggest_correction`・`detect_statistical_outliers`の単体テスト）

### Documentation

- README.mdに修正候補の仕組みと出力例を追記

## [1.3.0] - 2026-08-30

### Added

- `main.py`: CSV出力時、既に同名ファイルが存在する場合は上書きする前に
  `apex_stats_<タイムスタンプ>.csv` として同ディレクトリへバックアップしてから新規作成するように変更
  （`backup_existing_file`）。バックアップは自動削除されないため`output/`に蓄積する
- `tests/test_save_csv.py`を追加（EasyOCR不要、`save_csv`のバックアップ挙動を検証）
  - 実装時、同じ秒内に複数回保存するとタイムスタンプ（秒精度）が衝突し、直前のバックアップを
    上書きして消してしまうバグをテストで実際に検出。バックアップパスが既に存在する場合は
    連番を付けて回避するよう修正した

## [1.2.0] - 2026-08-30

### Added

- 回帰テストを追加（`tests/test_ocr_pipeline.py`）。個人データを含む実画像はテストに使えないため、
  `tests/fixtures/generate_sample.py` が `config.json` の座標定義から合成画像
  （`tests/fixtures/sample_input/1.png`）と期待値（`tests/fixtures/expected_values.json`）を生成する
  - 画像描画は当初`cv2.putText`（Hersheyフォント）で試したが、小さいフォントサイズで桁区切りの
    カンマがピリオドに誤読される問題を実機のEasyOCRで確認したため、PIL＋Boldフォント
    （OS標準フォントを検索し、無ければPillow内蔵フォントへフォールバック）に変更して解消した
  - 実機検証で31項目全て期待値と一致することを確認済み
- `requirements-dev.txt`を追加（`pytest`。エンドユーザー向けの`requirements.txt`とは分離）

### Changed

- README.mdに回帰テストの実行方法を追記

## [1.1.0] - 2026-08-30

### Added

- `main.py`: CSV出力後に異常値を自動検出する機能を追加
  - 型チェック（全列）: OCR変換失敗による文字列残留を検出
  - 単調性チェック（`career_*`の累積カウンタ列）: シーズン順で値が減少していないか検証
  - 統計的外れ値検知（`season_*`列）: 中央値絶対偏差（MAD）ベースの修正z-score（閾値3.5、
    [Iglewicz & Hoaglin, 1993](https://www.itl.nist.gov/div898/handbook/eda/section3/eda35h.htm)）
  - 検出結果は`ocr.log`へ`WARNING`として出力。ネットワーク通信は行わず、既存のオフライン実行特性を維持
- `config.json`: `anomaly_detection.mad_z_threshold` を追加（既定値3.5）
- 実データ検証により、過去に見逃していた`season=10`の`season_damage_avg=32208.0`という
  外れ値を新たに検出（修正z-score=390.17）

### Changed

- README.md / AI_PROMPT.mdを自動異常値検出の仕様に合わせて更新
- `requirements.txt`にnumpyを明示的に追加（`main.py`が直接importするため）

## [1.0.1] - 2026-08-30

### Fixed

- `main.py`: Windows上で非ASCII（日本語等）パスに配置すると`cv2.imread`/`cv2.imwrite`が無音で失敗し、
  全画像が読み込めないまま空のCSVが出力される不具合を修正。`np.fromfile`/`cv2.imdecode`経由の
  読み込み・書き込みに変更

### Documentation

- README.md / AI_PROMPT.mdに実行時の前提条件（インターネット接続必須、`input/`を空のまま実行した場合の挙動、
  想定解像度・UI言語）を明記

## [1.0.0] - 2026-08-30

### Added

- README.mdに機能概要・実行手順・免責事項・ライセンス表記を整備
- AIエージェント向け実行プロンプト（AI_PROMPT.md）を追加
- requirements.txtを追加（opencv-python, easyocr, pandas）
- LICENSE（MIT）を追加
- .gitignoreを追加し、個人の成績スクリーンショット・生成CSV・OCRログをgit管理から除外

### Changed

- 旧実装（test.py, test2.py, old_main.py）を legacy/ へ整理

### Removed

- 過去コミット履歴に含まれていた個人データ（成績画像・CSV・OCRログ）を履歴ごと削除し、公開リポジトリとして再構成

[Unreleased]: https://github.com/ninja-tanukichi/ApexStatsOCR/compare/v1.4.0...HEAD
[1.4.0]: https://github.com/ninja-tanukichi/ApexStatsOCR/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/ninja-tanukichi/ApexStatsOCR/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/ninja-tanukichi/ApexStatsOCR/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/ninja-tanukichi/ApexStatsOCR/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/ninja-tanukichi/ApexStatsOCR/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/ninja-tanukichi/ApexStatsOCR/releases/tag/v1.0.0
