# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/ninja-tanukichi/ApexStatsOCR/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/ninja-tanukichi/ApexStatsOCR/releases/tag/v1.0.0
