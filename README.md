# ApexStatsOCR

Apex Legendsの「トラッカー（成績）」画面のスクリーンショットをOCR（[EasyOCR](https://github.com/JaidedAI/EasyOCR)）で読み取り、シーズンごとの各種スタッツをCSVへ集計。さらにHTMLダッシュボードで推移をグラフ表示するツール。

> **注記**: 本ツールはApex Legendsのファンメイドの非公式ツールであり、Electronic Arts Inc. / Respawn Entertainmentとは一切関係ありません。ゲーム画面のUIレイアウトが変更された場合、`config.json` の座標がずれてOCRが正しく機能しなくなることがあります。

## 機能概要

| ファイル | 役割 |
| --- | --- |
| [main.py](main.py) | OCRパイプライン本体。`input/` 内の画像を読み込み、`config.json` の座標定義に従って各項目を切り出しOCR、`output/apex_stats.csv` へ出力する |
| [config.json](config.json) | 画像の基準解像度、入出力パス、OCR設定（言語・許可文字・拡大率など）、各スタッツ項目の切り出し座標（`regions`）を定義 |
| [apex_dashboard_v3.html](apex_dashboard_v3.html) | 生成したCSVをブラウザで読み込み、Plotly.jsでシーズン推移（勝率・KDR・ダメージ等）をグラフ表示するダッシュボード。サーバ不要、ローカルで開くだけで動作 |
| [legacy/test.py](legacy/test.py) | EasyOCRの動作確認用の単発スクリプト（1枚の画像を丸ごとOCRするだけの検証用） |
| [legacy/test2.py](legacy/test2.py) / [legacy/old_main.py](legacy/old_main.py) | 座標定義（`top_stats`/`damage_stats`等のブロック単位）が現行の`config.json`と異なる旧方式の実装。**現在は未使用（参考・実験用）** |
| `input/` | OCR対象のスクリーンショット（`シーズン番号.png`）を置くディレクトリ。**個人の成績画像のため`.gitignore`済み**（`.gitkeep`のみ管理） |
| `output/` | 生成されたCSVの出力先。**個人データのため`.gitignore`済み** |
| `debug/` | OCR時に切り出した各領域の画像が項目名ごとに保存される（座標調整・誤認識調査用）。**`.gitignore`済み** |
| `ocr.log` | 実行時のOCRログ（読み取り結果・変換後の値）。**`.gitignore`済み** |

### 処理の流れ

1. `input/` 内の画像ごとに、ファイル名から数字（シーズン番号）を抽出
2. `config.json` の `regions` に定義された矩形座標を画像解像度に合わせてスケーリングし、各項目を切り出し
3. グレースケール化＋拡大（`resize_scale`）した上でEasyOCRにより数値を読み取り（`allowlist`で数字・`,` `.` `/` `K` `M` のみ許可）
4. `K`/`M`表記の数値化、小数点のOCR誤認識補正（`merge_decimal`）などの後処理を実施
5. 全画像分の結果を1行ずつまとめ、`output/apex_stats.csv` へ出力

## 動作要件

- Python 3.x
- [requirements.txt](requirements.txt) に記載の依存パッケージ（`opencv-python`, `easyocr`, `pandas`）

```bash
pip install -r requirements.txt
```

## 実行時の前提条件

- **インターネット接続が必要**: `main.py` 初回実行時、EasyOCRが認識モデルをネット経由でダウンロードする。社内プロキシ・オフライン環境では失敗する
- **`input/` に画像を配置してから実行する**: 空のまま実行してもエラーにはならず、ヘッダーのみの空CSVが生成される（一見動いていないように見えるだけ）
- **リポジトリの配置パスにASCII文字のみを使う**（旧バージョンの既知の問題）: 過去バージョンではWindows上で日本語などの非ASCIIパスに配置するとOCRが無音で失敗する不具合があったが、現行版では`np.fromfile`/`cv2.imdecode`経由の読み込みに修正済み
- **1920x1080・英語UIの成績画面を前提**: `config.json` の `regions` 座標は解像度に応じてスケーリングされるが、アスペクト比やUI言語が異なると数値を正しく切り出せない場合がある

## How to run

### 0. 元画像データを準備

1. 各シーズン毎の成績画面をスクリーンショット
2. `シーズン名.png` に名前を変更（例：`15.png`）
3. 上記ファイルを以下へ保存: `\ApexStatsOCR\input\`

### 1. ダッシュボード用データ作成

1. コマンドプロンプト起動
2. `ApexStatsOCR` へ移動
3. `python main.py`
4. `\ApexStatsOCR\output\apex_stats.csv` にデータが作成される

### 2. ダッシュボード表示

1. `apex_dashboard_v3.html` を起動
2. 画面上部のファイル選択をクリック
3. `\ApexStatsOCR\output\apex_stats.csv` を選択

## 注意

異常値があればCSVデータを修正してください。
（ダッシュボード上で明らかな外れ値が見つかるはずです。例: 小数点のOCR誤認識で `season_kdr` が `44.0` のような桁違いの値になるケースあり）

## AIエージェントによる実行・検証

[AI_PROMPT.md](AI_PROMPT.md) に、AIコーディングエージェント（Claude Code等）へそのまま渡すことで
「依存インストール → `main.py` 実行 → `output/apex_stats.csv` の異常値検証（型・値域・累積値の単調性）→
結果報告」までを自律的に行わせるためのプロンプトを用意している。

## ライセンス

[MIT License](LICENSE)

## 変更履歴

[CHANGELOG.md](CHANGELOG.md) を参照。バージョンは [Semantic Versioning](https://semver.org/) に従う。
