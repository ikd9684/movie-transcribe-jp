# 外国語動画 日本語字幕生成アプリ

外国語の動画をアップロードするだけで、AI による音声文字起こし・日本語翻訳を自動実行し、**字幕付き動画** と **SRT ファイル** を生成するローカル Web アプリです。

---

## 特徴

- **ローカル完結** — Whisper・Ollama をローカルで動かすため、音声・映像データが外部に送信されない
- **多言語対応** — Whisper による自動言語検出（英語・中国語・韓国語・スペイン語など）
- **文脈付き翻訳** — 前後セグメントを文脈として与えることで自然な日本語訳を生成
- **リアルタイム進捗** — SSE による5ステップの進捗表示
- **設定カスタマイズ** — Whisper モデル・翻訳並列数・字幕スタイルなどをUIから変更可能

---

## 処理フロー

```
動画アップロード
  → 音声抽出 (FFmpeg)
  → 文字起こし (Whisper large-v3)
  → 日本語翻訳 (Ollama)
  → SRT 生成
  → 字幕焼き込み (FFmpeg libass)
  → SRT / 動画ダウンロード
```

---

## 技術スタック

| レイヤー | 技術 |
|---------|------|
| フロントエンド | Vue 3 + Vite + TypeScript |
| バックエンド | Python + FastAPI |
| 文字起こし | faster-whisper (Whisper large-v3) |
| 翻訳 | Ollama REST API |
| 動画処理 | FFmpeg (libass) |
| 進捗配信 | SSE (Server-Sent Events) |

---

## 必要環境

- **macOS** (開発・動作確認環境)
- **Python 3.10+**
- **Node.js 18+**
- **FFmpeg-full** (libass 必須)
- **Ollama** + 翻訳モデル

---

## クイックスタート

### 1. FFmpeg のインストール

字幕焼き込みに libass が必要です。標準の `ffmpeg` では**動作しません**。

```bash
brew install ffmpeg-full
brew link ffmpeg-full

# 確認
ffmpeg -h filter=subtitles | grep "Filter subtitles"
```

### 2. Ollama のセットアップ

```bash
# Ollama をインストール: https://ollama.com
ollama serve
ollama pull gpt-oss:20b   # または任意の LLM モデル
```

### 3. セットアップ

```bash
make setup
# backend/.env の OLLAMA_BASE_URL を環境に合わせて編集
```

### 4. 起動

```bash
make backend   # → http://localhost:8000
make frontend  # → http://localhost:5173
```

ブラウザで `http://localhost:5173` を開き、動画をドラッグ&ドロップしてください。

---

## 設定

アプリ右上の歯車アイコンから設定を変更できます。設定は localStorage に保存されます。

| 設定項目 | デフォルト | 説明 |
|---------|-----------|------|
| Whisper モデル | `large-v3` | 文字起こし精度とメモリのトレードオフ |
| 音声言語 | `auto` | 自動検出 or 明示指定 |
| Ollama URL | `http://localhost:11434` | 別マシンの場合はホスト名に変更 |
| LLM モデル | `gpt-oss:20b` | Ollama にプル済みのモデル名 |
| 翻訳並列数 | `4` | 同時翻訳セグメント数 (1-8) |
| コンテキスト窓 | `2` | 翻訳時に参照する前後セグメント数 |
| フォントサイズ | `24` | 字幕フォントサイズ (px) |
| 字幕位置 | `bottom` | `bottom` / `top` |
| 動画品質 (CRF) | `23` | 小さいほど高画質・大容量 (18-28) |

---

## ドキュメント

| ドキュメント | 内容 |
|------------|------|
| [docs/setup.md](docs/setup.md) | 詳細なセットアップ手順・トラブルシューティング |
| [docs/architecture.md](docs/architecture.md) | システム構成・処理パイプライン・技術選定理由 |
| [docs/api.md](docs/api.md) | REST API 仕様・SSE フォーマット・cURL 例 |
| [docs/spec.md](docs/spec.md) | 機能要件・非機能要件・画面フロー |

---

## ライセンス

MIT
