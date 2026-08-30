# ApexStatsOCR

Apex Legendsの「トラッカー(成績)」画面のスクリーンショットをOCR([EasyOCR](https://github.com/JaidedAI/EasyOCR))で読み取り、シーズンごとの各種スタッツをCSVへ集計。さらにHTMLダッシュボードで推移をグラフ表示するツール。

> **注記**: 本ツールはApex Legendsのファンメイドの非公式ツールであり、Electronic Arts Inc. / Respawn Entertainmentとは一切関係ありません。ゲーム画面のUIレイアウトが変更された場合、`config.json` の座標がずれてOCRが正しく機能しなくなることがあります。

## 目次

- [機能概要](#機能概要)
  - [処理の流れ](#処理の流れ)
- [動作要件](#動作要件)
- [実行時の前提条件](#実行時の前提条件)
- [使い方](#使い方)
  - [1. 元画像データを準備](#1-元画像データを準備)
  - [2. CSVデータ作成](#2-csvデータ作成)
  - [3. ダッシュボード表示](#3-ダッシュボード表示)
- [異常値の自動検出](#異常値の自動検出)
  - [修正候補の提示](#修正候補の提示)
- [回帰テスト](#回帰テスト)
- [ライセンス](#ライセンス)
- [変更履歴](#変更履歴)

## 機能概要

| ファイル | 役割 |
| --- | --- |
| [main.py](main.py) | OCRパイプライン本体。`input/` 内の画像を読み込み、`config.json` の座標定義に従って各項目を切り出しOCR、`output/apex_stats.csv` へ出力する |
| [config.json](config.json) | 画像の基準解像度、入出力パス、OCR設定(言語・許可文字・拡大率など)、各スタッツ項目の切り出し座標(`regions`)、異常値検出の閾値(`anomaly_detection.mad_z_threshold`)を定義 |
| [apex_dashboard_v3.html](apex_dashboard_v3.html) | 生成したCSVをブラウザで読み込み、Plotly.jsでシーズン推移(勝率・KDR・ダメージ等)をグラフ表示するダッシュボード。サーバ不要、ローカルで開くだけで動作 |
| `input/` | OCR対象のスクリーンショット(`シーズン番号.png`)を置くディレクトリ。**個人の成績画像のため`.gitignore`済み**(`.gitkeep`のみ管理) |
| `output/` | 生成されたCSVの出力先。**個人データのため`.gitignore`済み** |
| `debug/` | OCR時に切り出した各領域の画像が項目名ごとに保存される(座標調整・誤認識調査用)。**`.gitignore`済み** |
| `ocr.log` | 実行時のOCRログ(読み取り結果・変換後の値)。**`.gitignore`済み** |

### 処理の流れ

1. `input/` 内の画像ごとに、ファイル名から数字(シーズン番号)を抽出
2. `config.json` の `regions` に定義された矩形座標を画像解像度に合わせてスケーリングし、各項目を切り出し
3. グレースケール化＋拡大(`resize_scale`)した上でEasyOCRにより数値を読み取り(`allowlist`で数字・`,` `.` `/` `K` `M` のみ許可)
4. `K`/`M`表記の数値化、小数点のOCR誤認識補正(`merge_decimal`)などの後処理を実施
5. 全画像分の結果を1行ずつまとめ、`output/apex_stats.csv` へ出力
   - 既に同名のCSVが存在する場合は、上書きする前に `apex_stats_<タイムスタンプ>.csv` として同じディレクトリへバックアップしてから新規作成する
6. 出力結果を自動検証し、疑わしい値があれば `ocr.log` に警告を出力(後述)

## 動作要件

- Python 3.10以上を推奨(開発・動作確認はPython 3.14.6)
- [requirements.txt](requirements.txt) に記載の依存パッケージ(`opencv-python`, `easyocr`, `pandas`)

```bash
pip install -r requirements.txt
```

## 実行時の前提条件

- **インターネット接続が必要**: `main.py` 初回実行時、EasyOCRが認識モデルをネット経由でダウンロードする。社内プロキシ・オフライン環境では失敗する
- **`input/` に画像を配置してから実行する**: 空のまま実行してもエラーにはならず、ヘッダーのみの空CSVが生成される(一見動いていないように見えるだけ)
- **リポジトリの配置パスにASCII文字のみを使う**(旧バージョンの既知の問題): 過去バージョンではWindows上で日本語などの非ASCIIパスに配置するとOCRが無音で失敗する不具合があったが、現行版では`np.fromfile`/`cv2.imdecode`経由の読み込みに修正済み
- **バックアップCSVは自動削除されない**: 実行のたびに`apex_stats_<タイムスタンプ>.csv`が`output/`に増えていくため、不要になったら手動で削除する
- **1920x1080・英語UIの成績画面を前提**: `config.json` の `regions` 座標は解像度に応じてスケーリングされるが、アスペクト比やUI言語が異なると数値を正しく切り出せない場合がある

## 使い方

### 1. 元画像データを準備

1. Apex Legendsを起動
2. Apex各シーズン毎の成績画面を開く
3. スクリーンショット(例:Print Screenボタン押下)
4. 取得したスクリーンショットのファイル名を`シーズン番号.png` に変更する(例:`15.png`)
5. 上記ファイルを以下へ保存: `\ApexStatsOCR\input\`
6. 2～5の作業を対象シーズン分繰り返す

### 2. CSVデータ作成

1. コマンドプロンプトを起動
2. `ApexStatsOCR` へ移動
3. `python main.py`
4. `\ApexStatsOCR\output\apex_stats.csv` にデータが作成される
5. 警告有無を確認:`\ApexStatsOCR\ocr.log`

### 3. ダッシュボード表示

1. `apex_dashboard_v3.html` を起動
2. 画面上部のファイル選択ボタンをクリック
3. `\ApexStatsOCR\output\apex_stats.csv` を選択
4. 各種スタッツを表示

## 異常値の自動検出

`main.py` はCSV出力後、以下の3種類のルールで異常値を自動検出し、疑わしい値があれば `ocr.log` に `WARNING` として出力する(ネットワーク通信は行わないため、EasyOCRの初回モデルダウンロード以外はオフラインで完結する)。

| ルール | 対象列 | 内容 |
| --- | --- | --- |
| 型チェック | 全列 | OCR変換に失敗し文字列のまま残っている値を検出 |
| 単調性チェック | `career_*`の純粋な累積カウンタ列(`career_kdr`等の比率列は対象外) | シーズン順に並べたとき、累積値が前より減っていれば検出 |
| 統計的外れ値検知 | `season_*`列 | 列ごとに中央値絶対偏差(MAD)に基づく修正z-score([Iglewicz & Hoaglin, 1993](https://www.itl.nist.gov/div898/handbook/eda/section3/eda35h.htm)の推奨値3.5)で判定。固定の値域を決め打ちせず、データ自体のばらつきから外れ値を判定する |

閾値は `config.json` の `anomaly_detection.mad_z_threshold` で調整できる。検出された異常値は自動修正されない。

### 修正候補の提示

統計的外れ値として検出された値については、小数点の桁がOCRでずれるケース(例: `0.44` が `44` と誤読される)を想定し、元の値を10・100・1000で割った候補のうち、統計的に妥当な範囲に収まる最初の値を「修正候補」として各異常値の行に併記する。「要目視確認」の注記はサマリ行にまとめて出力される。

```text
異常値検出: 3件の疑わしい値を検出しました(要目視確認)
  season=9 column=season_kdr value=44.0 rule=statistical_outlier detail=中央値=0.68から外れ値(修正z-score=324.70) / 修正候補: 0.44
```

修正候補はあくまで統計的な推測であり、正しさは保証されない。**CSVを自動修正することはない**ため、必ず `\ApexStatsOCR\input\シーズン番号.png`で元画像を目視確認してから手動でCSVを修正すること。妥当な候補が見つからない場合は候補なしとしてログに記録される。

## 回帰テスト

個人の成績データを含む実画像はテストに使えないため、`tests/fixtures/generate_sample.py` が
`config.json` の座標定義を使って生成した合成画像(`tests/fixtures/sample_input/1.png`、個人情報を含まない)を
サンプルとして使う。座標や後処理ロジック(`convert_value`等)を変更した際に壊れていないか確認できる。

```bash
pip install -r requirements-dev.txt
pytest tests/
```

`regions` の座標を変更した場合は、`python tests/fixtures/generate_sample.py` でサンプル画像・期待値を再生成すること。

## ライセンス

[MIT License](LICENSE)

## 変更履歴

[CHANGELOG.md](CHANGELOG.md) を参照。バージョンは [Semantic Versioning](https://semver.org/) に従う。
