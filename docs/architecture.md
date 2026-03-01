# アーキテクチャ設計書 — 外国語動画 日本語字幕生成アプリ

## 1. システム全体構成

```
┌─────────────────────────────────────────────────────────────────┐
│                        ユーザーブラウザ                           │
│                    Vue 3 + Vite (SPA)                           │
│   VideoUploader │ ProcessingStatus │ ResultDownloader            │
└───────────────────────┬─────────────────────────────────────────┘
                        │ HTTP / SSE
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI (Python)                               │
│                                                                  │
│  POST /api/upload   GET /api/jobs/{id}/stream                   │
│  GET /api/jobs/{id}/status                                       │
│  GET /api/jobs/{id}/download/srt                                 │
│  GET /api/jobs/{id}/download/video                               │
│                                                                  │
│  ┌──────────────┐   ┌───────────────┐   ┌──────────────────┐   │
│  │ JobManager   │   │ BackgroundTask│   │  File Storage     │   │
│  │ (in-memory + │──▶│ asyncio Queue │   │  uploads/         │   │
│  │  JSON state) │   │               │   │  outputs/         │   │
│  └──────────────┘   └───────┬───────┘   └──────────────────┘   │
└───────────────────────────┬─┴───────────────────────────────────┘
                            │ subprocess / library calls
                ┌───────────┼────────────────┐
                ▼           ▼                ▼
         ┌──────────┐ ┌──────────┐   ┌──────────────┐
         │  FFmpeg  │ │  Whisper │   │   Ollama     │
         │ (音声抽出 │ │ large-v3 │   │ gpt-oss:20b  │
         │  字幕焼込)│ │ (ローカル)│   │ (REST API)   │
         └──────────┘ └──────────┘   └──────────────┘
```

---

## 2. 処理パイプライン詳細

### フェーズ 1: 動画アップロード

```
クライアント
  ─── multipart/form-data POST /api/upload ──▶ FastAPI
                                                  │
                                            UUID v4 生成 (job_id)
                                                  │
                                    uploads/{job_id}/original.{ext} 保存
                                                  │
                                         JobManager に登録 (status: queued)
                                                  │
                                    BackgroundTask としてキューに積む
                                                  │
                              ◀── { job_id } JSON レスポンス
```

### フェーズ 2: バックグラウンド処理パイプライン

```
JobManager
  │
  ├─[STEP 1] 音声抽出 (progress: 0→20%)
  │    FFmpeg: original.{ext} → audio.wav (16kHz, mono)
  │
  ├─[STEP 2] 文字起こし (progress: 20→50%)
  │    Whisper large-v3:
  │      入力: audio.wav
  │      出力: [ {start, end, text}, ... ] (セグメントリスト)
  │
  ├─[STEP 3] 日本語翻訳 (progress: 50→75%)
  │    Ollama API (gpt-oss:20b):
  │      各セグメントを前後 2 件の文脈とともに翻訳
  │      並列数: 4 コルーチン (asyncio.gather)
  │      出力: [ {start, end, ja_text}, ... ]
  │
  ├─[STEP 4] SRT 生成 (progress: 75→85%)
  │    subtitle.py: セグメントリスト → outputs/{job_id}/subtitle.srt
  │
  └─[STEP 5] 字幕焼き込み (progress: 85→100%)
       FFmpeg: original.{ext} + subtitle.srt → outputs/{job_id}/output.mp4
       オプション: -vf "subtitles=subtitle.srt:force_style='..."
```

### フェーズ 3: 進捗配信 (SSE)

```
クライアント
  ─── GET /api/jobs/{job_id}/stream (EventSource) ──▶ FastAPI
                                                          │
                                                    JobManager を定期ポーリング
                                                    (0.5秒間隔)
                                                          │
                                                    ◀── data: {"step": "...",
                                                               "progress": 65,
                                                               "status": "processing"}
                                                          │
                                                    (status=done or error で接続終了)
```

---

## 3. ディレクトリ構造

```
movie-transcribe-jp/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI アプリ・ミドルウェア設定
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── upload.py       # POST /api/upload
│   │   │       └── jobs.py         # GET /api/jobs/... (SSE/status/download)
│   │   ├── services/
│   │   │   ├── transcription.py    # Whisper large-v3 ラッパー
│   │   │   ├── translation.py      # Ollama HTTP クライアント
│   │   │   ├── subtitle.py         # SRT フォーマット生成
│   │   │   └── video.py            # FFmpeg subprocess ラッパー
│   │   ├── models/
│   │   │   └── schemas.py          # Pydantic モデル定義
│   │   └── core/
│   │       ├── config.py           # 環境変数・設定値
│   │       └── job_manager.py      # ジョブ状態管理 (シングルトン)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.vue                 # ルートコンポーネント
│   │   ├── components/
│   │   │   ├── VideoUploader.vue   # ドラッグ&ドロップ UI
│   │   │   ├── ProcessingStatus.vue# SSE 購読・進捗 UI
│   │   │   └── ResultDownloader.vue# ダウンロードリンク UI
│   │   ├── composables/
│   │   │   └── useJob.ts           # SSE 購読ロジック (EventSource)
│   │   └── api/
│   │       └── client.ts           # axios ベース API クライアント
│   ├── package.json
│   └── vite.config.ts              # /api プロキシ設定
├── tasks/
│   ├── todo.md
│   └── lessons.md
└── docs/
    ├── spec.md
    ├── architecture.md
    └── api.md
```

---

## 4. 技術選定理由

### Backend: FastAPI (Python)

- Whisper / Ollama ともに Python エコシステムとの親和性が高い
- `async`/`await` ネイティブ対応で SSE 実装が簡潔
- `BackgroundTasks` によるジョブ非同期実行が組み込み
- Pydantic による型安全なスキーマ管理

### Frontend: Vue 3 + Vite

- Composition API + TypeScript で composable パターンが使いやすい
- Vite の開発サーバープロキシで CORS 問題を回避
- 軽量・高速な開発体験

### 文字起こし: Whisper large-v3 (ローカル)

- 外部 API 不要でデータがローカルに閉じる
- 多言語対応・精度が最高水準
- `faster-whisper` ライブラリで高速化可能

### 翻訳: Ollama (gpt-oss:20b)

- ローカル LLM でプライバシー安全
- REST API でシンプルに呼び出し可能
- 20B モデルで翻訳品質と速度のバランスが良好

### 動画処理: FFmpeg

- 業界標準。あらゆる動画フォーマットに対応
- libass による高品質字幕焼き込み
- subprocess 経由でシンプルに統合

---

## 5. データフロー図

```
[ブラウザ]
  │ 1. POST /api/upload (動画ファイル)
  ▼
[FastAPI]
  │ 2. ファイル保存 + job_id 返却
  │ 3. BackgroundTask 起動
  ▼
[JobManager]
  │ 4. queued → processing
  ▼
[video.py: FFmpeg]    ── uploads/{id}/audio.wav
  │
  ▼
[transcription.py: Whisper]  ── segments [{start,end,text},...]
  │
  ▼
[translation.py: Ollama]    ── segments [{start,end,ja_text},...]
  │
  ▼
[subtitle.py]           ── outputs/{id}/subtitle.srt
  │
  ▼
[video.py: FFmpeg]      ── outputs/{id}/output.mp4
  │
  ▼
[JobManager]  status: done

[ブラウザ]  ←── SSE stream (進捗) ──  [FastAPI]
  │ 5. GET /api/jobs/{id}/download/srt
  │ 6. GET /api/jobs/{id}/download/video
  ▼
[ファイル受信]
```

---

## 6. ジョブ状態遷移

```
queued ──▶ processing ──▶ done
                │
                └──▶ error
```

| 状態 | 説明 |
|------|------|
| `queued` | アップロード完了、処理待ち |
| `processing` | バックグラウンド処理実行中 |
| `done` | 全処理完了、ダウンロード可能 |
| `error` | 処理失敗 (error_message に詳細) |

---

## 7. ファイルストレージ設計

```
storage/
├── uploads/
│   └── {job_id}/
│       ├── original.mp4   (アップロードされた動画)
│       └── audio.wav      (抽出音声、処理後削除可)
└── outputs/
    └── {job_id}/
        ├── subtitle.srt   (生成SRT)
        └── output.mp4     (字幕焼き込み動画)
```

- ストレージパスは `config.py` の `STORAGE_ROOT` で設定
- 古いジョブファイルの自動削除は将来課題（初期実装では手動削除）
