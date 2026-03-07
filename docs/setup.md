# セットアップガイド

## 必要な外部ツール

### 1. FFmpeg（libass 付き）

字幕焼き込みに **libass** が必要です。Homebrew の標準 `ffmpeg` は libass を含まないため、`ffmpeg-full` をインストールしてください。

```bash
# ffmpeg-full をインストール（既存の ffmpeg とリンクが競合する場合は unlink してから）
brew unlink ffmpeg 2>/dev/null; brew install ffmpeg-full
brew link ffmpeg-full
```

インストール確認：

```bash
ffmpeg -h filter=subtitles | grep "Filter subtitles"
# → "Filter subtitles" と表示されれば OK
```

> **注意:** 標準の `brew install ffmpeg` ではインストールできません。`ffmpeg-full` が必要です。

---

### 2. Ollama

翻訳に使用する Ollama サーバーと翻訳モデルを用意します。

**ローカルで起動する場合:**

```bash
ollama serve
ollama pull gpt-oss:20b
```

**別マシンで起動している場合:**

Ollama がリモートマシン（例: `http://ollama-server:11434`）で起動していれば、そのまま利用可能です。

---

## バックエンドのセットアップ

### 1. 仮想環境と依存パッケージ

```bash
cd backend
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env.example` をコピーして `.env` を作成し、環境に合わせて編集します。

```bash
cp .env.example .env
```

```env
# backend/.env
OLLAMA_BASE_URL=http://localhost:11434   # Ollama の URL（別マシンの場合はそのホスト名に変更）
STORAGE_ROOT=./storage
MAX_UPLOAD_SIZE_MB=2048
CORS_ORIGINS=http://localhost:5173
```

### 3. 起動

```bash
cd backend
.venv/bin/uvicorn app.main:app --reload
# → http://localhost:8000 で起動
```

---

## フロントエンドのセットアップ

### 1. 依存パッケージ

```bash
cd frontend
npm install
```

### 2. 起動

```bash
npm run dev
# → http://localhost:5173 で起動
```

---

## アプリの設定

ブラウザで `http://localhost:5173` を開き、画面右上の設定アイコンから設定を変更できます。

| 設定項目 | デフォルト | 説明 |
|---------|-----------|------|
| Ollama Base URL | `http://localhost:11434` | Ollama サーバーのアドレス |
| Translation Model | `gpt-oss:20b` | 使用する翻訳モデル名 |
| Whisper Model | `large-v3` | 使用する Whisper モデル |
| その他 | — | 字幕フォントサイズ・位置・並列数など |

設定は localStorage に保存され、次回以降も維持されます。

> **Ollama が別マシンの場合:** 設定モーダルで Ollama Base URL を変更してください（例: `http://ollama-server:11434`）。`.env` の `OLLAMA_BASE_URL` はバックエンドのデフォルト値ですが、フロントエンドから送信された設定が優先されます。

---

## よくあるトラブル

### 字幕焼き込みで FFmpeg エラーが出る

`subtitles` フィルタが見つからない場合、`ffmpeg-full` がインストールされていないか、パスが通っていません。

```bash
# 確認
ffmpeg -h filter=subtitles

# 修正
brew install ffmpeg-full && brew link ffmpeg-full
```

### 翻訳で接続エラーが出る（ConnectError）

Ollama サーバーに接続できない場合です。

1. Ollama が起動しているか確認: `ollama list`
2. フロントエンドの設定モーダルで Ollama Base URL が正しいか確認
3. ブラウザの DevTools コンソールで localStorage をリセットして再設定:
   ```js
   localStorage.removeItem('movie-transcribe-settings')
   ```

### エラーメッセージが「不明なエラー」と表示される

バックエンドのログ（uvicorn のターミナル出力）に詳細なスタックトレースが出力されます。ログを確認してください。
