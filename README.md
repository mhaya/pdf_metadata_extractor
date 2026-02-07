# PDF Metadata Extractor

Ollama経由でLLMを使用し、PDFファイルから書誌メタデータを抽出するCLIツール。

## 機能

### LLM抽出メタデータ
PDFから抽出したテキストをLLMに送り、以下の書誌情報を抽出します：
- タイトル
- 著者
- 雑誌名
- 巻・号・ページ
- 出版年
- DOI
- 要約（論文全体から生成）
- キーワード
- 文書カテゴリ
- 言語検出

### ファイル属性（PDFから直接取得）
- ページ数
- ファイルサイズ
- PDFバージョン
- 作成日/更新日

※出力言語はPDFの内容言語に自動で合わせます（`--language` で変更可能）。

## 前提条件

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (パッケージマネージャー)
- [Ollama](https://ollama.ai/) がインストール・起動済み
- LLMモデルがダウンロード済み

```bash
# Ollamaのインストール後
ollama pull llama3.2
ollama serve  # サーバー起動
```

## セットアップ

```bash
# リポジトリをクローン
git clone <repository-url>
cd llamaprg

# 依存関係をインストール（uv.lockから再現）
uv sync
```

## 使用方法

### 基本的な使い方

```bash
uv run python -m pdf_metadata_extractor input.pdf
```

### オプション

| 引数 | 説明 | デフォルト |
|-----|------|-----------|
| `file` | 対象PDFファイルパス | (必須) |
| `--output`, `-o` | 出力形式 (text/json) | text |
| `--model`, `-m` | Ollamaモデル名 | llama3.2 |
| `--language`, `-l` | すべての抽出項目の出力言語 | 自動検出 |
| `--no-llm` | LLM抽出をスキップ（ファイル属性のみ） | False |
| `--debug` | デバッグ出力（中間データをstderrに表示） | False |

### 使用例

```bash
# テキスト形式で出力（デフォルト）
uv run python -m pdf_metadata_extractor document.pdf

# JSON形式で出力
uv run python -m pdf_metadata_extractor document.pdf --output json

# より高精度なモデルを使用
uv run python -m pdf_metadata_extractor document.pdf --model gemma3:12b

# ファイル属性のみ（LLMなし、高速）
uv run python -m pdf_metadata_extractor document.pdf --no-llm

# 出力言語を英語に指定（日本語PDFでも英語で要約・キーワード出力）
uv run python -m pdf_metadata_extractor document.pdf --language English

# 出力言語を日本語に指定
uv run python -m pdf_metadata_extractor document.pdf -l Japanese

# デバッグ出力（抽出テキスト・LLM生レスポンス等を表示）
uv run python -m pdf_metadata_extractor document.pdf --debug
```

### 出力例

#### テキスト形式
```
==================================================
PDF Metadata
==================================================

[Document Metadata]
  Title:        生成AI とオープンデータ
  Author:       黒橋 禎夫
  Journal:      情報の科学と技術
  Volume:       74
  Number:       8
  Pages:        292～297
  Year:         2024
  Language:     Japanese
  Category:     情報科学
  Keywords:     生成AI, オープンデータ, デジタルアーカイブ

  Summary:
    現代社会は複雑な課題に直面しており、
    知識の共有と活用が不可欠である。...

[File Properties]
  Pages:        6
  File Size:    1007.5 KB
  PDF Version:  PDF 1.6

==================================================
```

#### JSON形式
```json
{
  "file": {
    "page_count": 6,
    "file_size": 1031727,
    "pdf_version": "PDF 1.6",
    "created_at": null,
    "modified_at": null
  },
  "llm": {
    "title": "生成AI とオープンデータ",
    "author": "黒橋 禎夫",
    "journal": "情報の科学と技術",
    "volume": "74",
    "number": "8",
    "pages": "292～297",
    "year": "2024",
    "doi": null,
    "summary": "現代社会は複雑な課題に直面しており...",
    "keywords": ["生成AI", "オープンデータ", "デジタルアーカイブ"],
    "category": "情報科学",
    "language": "Japanese"
  }
}
```

## モデル選択のガイド

抽出精度はモデルのサイズに大きく依存します。使用するPDFの言語と求める精度に応じてモデルを選択してください。

### モデル比較表

| モデル | パラメータ数 | 日本語精度 | 英語精度 | 速度 | 備考 |
|-------|-----------|----------|---------|------|------|
| llama3.2 | 3B | 低 | 中 | 速い | デフォルト。英語文書向き |
| qwen2.5:7b | 7B | 中 | 中 | 普通 | 日本語対応が比較的良好 |
| gemma3:12b | 12B | 高 | 高 | 遅い | 書誌情報の抽出精度が高い。推奨 |

### モデルのインストールと使用

```bash
# モデルのダウンロード
ollama pull llama3.2      # デフォルト（3B、軽量）
ollama pull qwen2.5:7b    # 日本語対応（7B）
ollama pull gemma3:12b    # 高精度（12B、推奨）

# モデル指定で実行
uv run python -m pdf_metadata_extractor document.pdf --model gemma3:12b
```

### 選択の指針

- **英語文書のみ**: `llama3.2`（デフォルト）で十分
- **日本語文書**: `gemma3:12b` を推奨。`qwen2.5:7b` も選択肢
- **高精度が必要**: `gemma3:12b` を使用。タイトル・著者・雑誌名の抽出精度が大幅に向上
- **速度優先**: `llama3.2` が最速だが、精度は低下

## プロジェクト構成

```
pdf_metadata_extractor/
├── __init__.py       # パッケージエクスポート
├── __main__.py       # モジュールエントリーポイント
├── cli.py            # CLIインターフェース（argparse）
├── extractor.py      # メイン抽出オーケストレーション
├── llm_client.py     # Ollama API連携（few-shot + JSONスキーマ）
├── models.py         # Pydanticデータモデル
└── pdf_parser.py     # PDF解析・テキスト抽出（PyMuPDF）
```

## 依存ライブラリ

| ライブラリ | 用途 |
|-----------|------|
| pymupdf | PDF解析・テキスト抽出 |
| ollama | Ollama Python クライアント |
| pydantic | データモデル定義・バリデーション |

## トラブルシューティング

### Ollamaに接続できない
```
Error: Cannot connect to Ollama. Please ensure Ollama is running: ollama serve
```
→ `ollama serve` でOllamaサーバーを起動してください。

### モデルが見つからない
```
Error: Model 'llama3.2' not found. Please run: ollama pull llama3.2
```
→ `ollama pull llama3.2` でモデルをダウンロードしてください。

### 抽出精度が低い
→ `--debug` フラグで中間データを確認し、`--model` でより大きなモデルを試してください。

## ライセンス

MIT
