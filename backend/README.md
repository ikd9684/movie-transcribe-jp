# Backend — 外国語動画 日本語字幕生成アプリ

Python + FastAPI によるバックエンドです。

## 起動

```bash
# 初回のみ
python -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env

# サーバー起動
.venv/bin/uvicorn app.main:app --reload   # http://localhost:8000
```

`.env` の主要項目:

| 環境変数 | デフォルト | 説明 |
|---------|-----------|------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama サーバーの URL |
| `STORAGE_ROOT` | `../storage` | アップロード・出力ファイルの保存先 |
| `MAX_UPLOAD_SIZE_MB` | `2048` | アップロード上限 (MB) |
| `CORS_ORIGINS` | `http://localhost:5173` | 許可するフロントエンドの Origin |

## 構成

```
app/
├── main.py                    # FastAPI アプリ初期化・CORS・ルーター登録
├── core/
│   ├── config.py              # Pydantic Settings（環境変数読み込み）
│   ├── job_manager.py         # ジョブ状態管理シングルトン
│   └── pipeline.py            # 5ステップ処理パイプライン
├── api/routes/
│   ├── upload.py              # POST /api/upload
│   └── jobs.py                # SSE / status / download エンドポイント
├── models/
│   └── schemas.py             # Pydantic スキーマ定義
└── services/
    ├── video.py               # FFmpeg 音声抽出・字幕焼き込み
    ├── transcription.py       # faster-whisper ラッパー
    ├── translation.py         # Ollama 並列翻訳
    └── subtitle.py            # SRT ファイル生成
```

## API

詳細は [docs/api.md](../docs/api.md) を参照。

| エンドポイント | 説明 |
|--------------|------|
| `POST /api/upload` | 動画アップロード・ジョブ登録 |
| `GET /api/jobs/{id}/stream` | SSE による進捗配信 |
| `GET /api/jobs/{id}/status` | ジョブ状態 JSON |
| `GET /api/jobs/{id}/download/srt` | SRT ダウンロード |
| `GET /api/jobs/{id}/download/video` | 字幕付き動画ダウンロード |
