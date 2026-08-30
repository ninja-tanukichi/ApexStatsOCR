# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.15.0] - 2026-08-30

### Added

- Contributingに、READMEのスクリーンショット用デモデータを更新したい場合は
  `docs/demo-data/generate_demo_stats.py` で架空データを生成できる旨を追記。
  必須のPRチェック項目ではなく、参考情報として独立した一文にした

## [1.14.0] - 2026-08-30

### Changed

- `docs/images/`から`generate_demo_stats.py`/`demo_apex_stats.csv`を`docs/demo-data/`へ移動。
  `docs/images/`には画像ファイルのみが置かれるように整理した

## [1.13.0] - 2026-08-30

### Added

- READMEの「動作要件」に、既にPython環境を持つユーザー向けの任意選択として仮想環境(venv)の
  利用手順を追記。実行のしやすさを損なわないよう既存の手順は変更せず、追加の選択肢として案内する形にした

## [1.12.0] - 2026-08-30

### Added

- READMEに「スクリーンショット」セクションを追加し、ダッシュボードの表示例(サンプルデータ)を掲載
  (`docs/images/dashboard-kpi.png`, `docs/images/dashboard-charts.png`)。個人の実データは使用していない

## [1.11.0] - 2026-08-30

### Added

- `docs/config.md`を新設。`config.json`の全項目の説明、および`regions`のキー(=CSVの列名)が
  実際にどのApex Legendsのスタッツを指すかの一覧を記載。あわせて、これまでドキュメント化されて
  いなかった`ocr.num_allowlist`/`ocr.threshold`が現在未使用であることも明記した
- READMEの機能概要から`docs/config.md`へリンク

## [1.10.0] - 2026-08-30

### Changed

- `apex_dashboard_v3.html` を `apex_dashboard.html` にリネーム。ファイル名にバージョン番号を
  埋め込む方式をやめ、プロジェクト全体のバージョン管理(CHANGELOG.md/gitタグ)に一本化した
- ダッシュボード内に静的に書かれていた `Version 1.0.0` / `Build 2026-06-12` の表示を廃止し、
  新設した `version.js`(`DASHBOARD_VERSION`, `CSV_SCHEMA_VERSION`)から`<script src>`経由で
  読み込むように変更。`fetch()`は`file://`で開くとCORSでブロックされるため使えず、
  `<script src>`によるローカルJS読み込みで回避した。ファイル選択の追加や、ダッシュボード表示手順
  (ダブルクリックで開くだけ)の変更は不要
- `config.json` の未使用フィールド `"version": "3.0"` を削除(`main.py`のどこからも参照されておらず、
  上記のバージョン整理と無関係に孤立していたため)

## [1.9.0] - 2026-08-30

### Added

- READMEに「Contributing」セクションを追加(開発環境、PR前の確認事項、設計方針、バージョン管理の運用)

### Changed

- 「動作要件」内の箇条書きの文体を統一(太字見出し+コロン形式を廃し、前半の平文スタイルに統一)

### Removed

- 「リポジトリの配置パスにASCII文字のみを使う」の記載を削除。既に`v1.0.1`で修正済みの過去の不具合であり、
  「動作要件(＝現在有効な制約)」に過去の話を残すのは読者を混乱させるため

## [1.8.0] - 2026-08-30

### Changed

- README.mdの目次を1レベル(H2見出しのみ)に簡略化
- 「動作要件」と「実行時の前提条件」を1つの「動作要件」セクションへ統合
- 「処理の流れ」を`docs/processing-flow.md`へ移動し、READMEからリンクする形に変更

## [1.7.0] - 2026-08-30

### Added

- `docs/anomaly-detection.md`を新設し、異常値検出・修正候補提示の実装詳細
  (MADベース修正z-scoreの計算式、比率列を単調性チェックから除外する理由、修正候補ヒューリスティック等)
  をREADME本文から分離した

### Fixed

- 「`debug/<列名>.png`を確認する」という誤った案内を修正。`debug/`は列名ごとに1枚しか保持されず、
  複数画像を一括処理すると最後に処理した画像の分で上書きされるため、特定シーズンの異常値調査には使えない。
  README.md・AI_PROMPT.mdの該当箇所を、season番号から `input/<シーズン番号>.png` を直接確認する案内に修正

## [1.6.0] - 2026-08-30

### Removed

- `AI_PROMPT.md`をgit管理から除外(`.gitignore`＋`git rm --cached`)。ローカルには記録として残すが、
  公開リポジトリには含めない。README.mdの「AIエージェントによる実行・検証」節と目次の参照も削除

### Fixed

- README.mdの誤記・表記ゆれを修正(体裁を半角括弧・半角記号に統一、`config.json`の説明に
  `anomaly_detection.mad_z_threshold`を追記、`Python 3.x`の記載を`Python 3.10以上を推奨`に具体化)
- README.mdに目次を追加

## [1.5.0] - 2026-08-30

### Removed

- `legacy/`（旧実装 `test.py` / `test2.py` / `old_main.py`）をgit管理から除外（`.gitignore`＋`git rm --cached`）。
  ローカルには記録として残すが、公開リポジトリには含めない。README.mdの参照も削除

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

[Unreleased]: https://github.com/ninja-tanukichi/ApexStatsOCR/compare/v1.15.0...HEAD
[1.15.0]: https://github.com/ninja-tanukichi/ApexStatsOCR/compare/v1.14.0...v1.15.0
[1.14.0]: https://github.com/ninja-tanukichi/ApexStatsOCR/compare/v1.13.0...v1.14.0
[1.13.0]: https://github.com/ninja-tanukichi/ApexStatsOCR/compare/v1.12.0...v1.13.0
[1.12.0]: https://github.com/ninja-tanukichi/ApexStatsOCR/compare/v1.11.0...v1.12.0
[1.11.0]: https://github.com/ninja-tanukichi/ApexStatsOCR/compare/v1.10.0...v1.11.0
[1.10.0]: https://github.com/ninja-tanukichi/ApexStatsOCR/compare/v1.9.0...v1.10.0
[1.9.0]: https://github.com/ninja-tanukichi/ApexStatsOCR/compare/v1.8.0...v1.9.0
[1.8.0]: https://github.com/ninja-tanukichi/ApexStatsOCR/compare/v1.7.0...v1.8.0
[1.7.0]: https://github.com/ninja-tanukichi/ApexStatsOCR/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/ninja-tanukichi/ApexStatsOCR/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/ninja-tanukichi/ApexStatsOCR/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/ninja-tanukichi/ApexStatsOCR/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/ninja-tanukichi/ApexStatsOCR/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/ninja-tanukichi/ApexStatsOCR/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/ninja-tanukichi/ApexStatsOCR/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/ninja-tanukichi/ApexStatsOCR/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/ninja-tanukichi/ApexStatsOCR/releases/tag/v1.0.0
