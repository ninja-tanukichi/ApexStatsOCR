# 処理の流れ

`main.py` の内部処理フローの詳細。ユーザー向けの使い方は[README.md の「使い方」](../README.md#使い方)を参照。

1. `input/` 内の画像ごとに、ファイル名から数字(シーズン番号)を抽出
2. `config.json` の `regions` に定義された矩形座標を画像解像度に合わせてスケーリングし、各項目を切り出し
3. グレースケール化＋拡大(`resize_scale`)した上でEasyOCRにより数値を読み取り(`allowlist`で数字・`,` `.` `/` `K` `M` のみ許可)
4. `K`/`M`表記の数値化、小数点のOCR誤認識補正(`merge_decimal`)などの後処理を実施
5. `config.json` の `corrections_file`(既定`corrections.json`)を読み込み、全画像分の結果に適用する(`apply_corrections`)。ファイルが存在しない場合は空の`{}`で自動作成する
   - 各エントリは `{season: {列名: {"observed": 記録時のOCR生値, "corrected": 訂正値}}}` の形式
   - 現在のOCR生値が記録済みの`observed`と一致する場合のみ訂正を適用し、`ocr.log`にINFOで記録する
   - 一致しない場合(画像を差し替えて再OCRした等)は訂正を適用せず、最新のOCR結果をそのまま採用した上で`ocr.log`にWARNINGを出す(古い訂正データより最新の画像データを優先する)
   - 詳細は[config.md](config.md#トップレベル)を参照
6. 全画像分の結果(訂正適用後)を1行ずつまとめ、`output/apex_stats.csv` へ出力
   - 既に同名のCSVが存在する場合は、上書きする前に `apex_stats_<タイムスタンプ>.csv` として同じディレクトリへバックアップしてから新規作成する
7. 出力結果(訂正適用後の値)を自動検証し、疑わしい値があれば `ocr.log` に警告を出力(詳細は[anomaly-detection.md](anomaly-detection.md)を参照)
8. `config.json` の `dashboard.auto_open` が有効な場合、生成したCSVを `apex_dashboard.html`(`dashboard.template_file`)に埋め込んだ `apex_dashboard_latest.html`(`dashboard.output_file`)を生成し、デフォルトブラウザで自動的に開く
   - 埋め込みはテンプレート内のプレースホルダ(`<script id="embedded-data" type="application/json">null</script>`)をCSVテキストのJSON文字列に置換する形で行う(`build_dashboard_with_data`)。`</script>`によるタグの途中終了を防ぐため `</` はエスケープする
   - 生成先ファイルは実行のたびに上書きされ、バックアップは作られない(CSVとは異なりダッシュボードは常にCSVから再生成できる派生物のため)。ブラウザ側も実行のたびに新規タブが開く(既存タブの再利用・自動クローズはしない)
   - 設定の詳細は[config.md](config.md#dashboard)を参照
