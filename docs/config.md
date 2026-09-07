# config.json リファレンス

`config.json` の各設定項目の説明。`regions` のキー名はそのまま `output/apex_stats.csv` の列名になるため、CSVの列の意味もここで説明する。

## トップレベル

| キー | 意味 |
| --- | --- |
| `base_width` / `base_height` | `regions` の座標の基準となる解像度。実際の画像がこれと異なる解像度の場合、`main.py`が比率でスケーリングする |
| `input_dir` | OCR対象画像を置くディレクトリ |
| `output_file` | 出力CSVのパス |
| `corrections_file` | 訂正値を記録するファイルのパス(既定`corrections.json`)。詳細は[README](../README.md#異常値の訂正を記録する)を参照 |
| `log_file` | ログの出力先パス(既定`ocr.log`) |
| `log_level` | ログレベル(既定`INFO`)。OCR結果の詳細(切り出した各項目のOCR生テキスト・変換後の値)は`DEBUG`でのみ出力されるため、OCR誤読の原因調査時は`DEBUG`に変更する |

## `ocr`

| キー | 意味 |
| --- | --- |
| `languages` | EasyOCRに渡す言語コードのリスト |
| `allowlist` | OCR時に認識対象とする文字集合(数字・`,` `.` `/` `K` `M`) |
| `gpu` | GPUを使うかどうか |
| `resize_scale` | 切り出した領域を拡大する倍率(小さい文字ほどOCR精度が上がるため) |
| `num_allowlist` | **現在未使用**。`main.py`のどこからも参照されていない |
| `threshold` | **現在未使用**。2値化処理(`preprocess`内でコメントアウトされているコード)向けの値で、有効化されていない |

## `anomaly_detection`

| キー | 意味 |
| --- | --- |
| `mad_z_threshold` | 統計的外れ値検知の閾値。詳細は[docs/anomaly-detection.md](anomaly-detection.md)を参照 |

## `dashboard`

CSV出力後にダッシュボードを自動表示する機能の設定。詳細は[README](../README.md#3-ダッシュボード表示)を参照。

| キー | 意味 |
| --- | --- |
| `auto_open` | `true`の場合、CSV出力後に自動生成したダッシュボードHTMLをデフォルトブラウザで開く。`false`にすると従来通り手動で`apex_dashboard.html`を開く運用に戻る |
| `template_file` | 埋め込み元となるダッシュボードのテンプレートファイル(通常は`apex_dashboard.html`) |
| `output_file` | CSVデータを埋め込んだ生成先ファイル名。個人データを含むため`.gitignore`済みで、実行のたびに上書きされる(バックアップは作られない) |

## `regions`(CSV列の意味)

各キーは画像上の切り出し矩形 `[x1, y1, x2, y2]`(左上・右下のピクセル座標、`base_width`/`base_height`基準)を表す。キー名はそのまま `output/apex_stats.csv` の列名になる。

`career_*` はプレイヤーの通算(キャリア)成績、`season_*` は選択中シーズンの成績。両者は同じ意味の項目が対になっている。

| 列名(career_/season_) | 意味 |
| --- | --- |
| `games` | プレイ試合数 |
| `wins` | 優勝(1位)回数 |
| `top5` | Top5フィニッシュ回数 |
| `damage` | 与ダメージ合計 |
| `damage_max` | 1試合の最大与ダメージ(自己ベスト) |
| `damage_avg` | 1試合あたりの平均与ダメージ |
| `kills` | キル数 |
| `deaths` | デス数 |
| `kdr` | キル/デス比(Kill Death Ratio) |
| `max_kills` | 1試合の最大キル数(自己ベスト) |
| `knockdowns` | ノックダウン数 |
| `assists` | アシスト数 |
| `win_streak` | 最大連勝記録 |
| `revives` | リバイブ(味方蘇生)数 |
| `respawns` | リスポーン(復活)数 |

`season`列(regions外)は、ファイル名(`<シーズン番号>.png`)から抽出したシーズン番号。
