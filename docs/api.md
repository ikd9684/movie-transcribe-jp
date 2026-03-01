# API仕様書 — 外国語動画 日本語字幕生成アプリ

## 共通仕様

| 項目 | 値 |
|------|-----|
| ベース URL | `http://localhost:8000` |
| Content-Type (リクエスト) | `application/json` or `multipart/form-data` |
| Content-Type (レスポンス) | `application/json` |
| 認証 | なし（ローカル実行のため） |
| エラー形式 | `{ "detail": "エラーメッセージ" }` |

---

## エンドポイント一覧

| Method | Path | 説明 |
|--------|------|------|
| POST | `/api/upload` | 動画アップロード |
| GET | `/api/jobs/{job_id}/stream` | SSE 進捗ストリーム |
| GET | `/api/jobs/{job_id}/status` | ジョブステータス取得 |
| GET | `/api/jobs/{job_id}/download/srt` | SRT ファイルダウンロード |
| GET | `/api/jobs/{job_id}/download/video` | 字幕付き動画ダウンロード |

---

## POST `/api/upload`

動画ファイルをアップロードし、バックグラウンド処理ジョブを開始する。

### リクエスト

```
Content-Type: multipart/form-data

Form Fields:
  file:     (binary) 動画ファイル
  settings: (string, JSON) ジョブ設定（省略時はデフォルト値）
```

#### settings フィールド（JSON オブジェクト）

| キー | 型 | デフォルト | 説明 |
|------|----|-----------|------|
| `whisper_model` | string | `"large-v3"` | Whisper モデル名 (`tiny`/`base`/`small`/`medium`/`large-v3`) |
| `whisper_language` | string | `"auto"` | 音声言語コード (`auto`/`en`/`zh`/`ko` 等) |
| `ollama_base_url` | string | `"http://localhost:11434"` | Ollama サーバー URL |
| `translation_model` | string | `"gpt-oss:20b"` | 翻訳に使用する LLM モデル名 |
| `translation_parallel` | integer (1-8) | `4` | 翻訳並列数 |
| `translation_context_window` | integer (0-4) | `2` | 翻訳コンテキスト窓（前後セグメント数） |
| `subtitle_font_size` | integer (12-48) | `24` | 字幕フォントサイズ (px) |
| `subtitle_position` | string | `"bottom"` | 字幕位置 (`"bottom"` / `"top"`) |
| `output_crf` | integer (18-28) | `23` | 出力動画品質 CRF 値（小さいほど高画質） |

### バリデーション

- ファイル拡張子: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm` のみ
- MIME タイプ: `video/*` のみ
- ファイルサイズ: 2 GB 以下

### レスポンス — 成功 `202 Accepted`

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "処理を開始しました"
}
```

### レスポンス — エラー

| HTTP Status | 条件 | レスポンス |
|-------------|------|-----------|
| 400 | 非対応フォーマット | `{"detail": "対応フォーマット (mp4/mov/avi/mkv/webm) のファイルをアップロードしてください"}` |
| 413 | ファイルサイズ超過 | `{"detail": "ファイルサイズは 2GB 以下にしてください"}` |
| 500 | サーバーエラー | `{"detail": "ファイルの保存に失敗しました"}` |

---

## GET `/api/jobs/{job_id}/stream`

SSE（Server-Sent Events）でジョブ進捗をリアルタイム配信する。

### リクエスト

```
GET /api/jobs/550e8400-e29b-41d4-a716-446655440000/stream
Accept: text/event-stream
```

### パスパラメータ

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `job_id` | string (UUID v4) | ジョブ識別子 |

### レスポンス — `200 OK`

```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

SSE イベントストリーム（0.5 秒間隔でポーリング）:

```
data: {"step": "音声抽出中", "progress": 10, "status": "processing"}

data: {"step": "文字起こし中", "progress": 35, "status": "processing"}

data: {"step": "翻訳中", "progress": 62, "status": "processing"}

data: {"step": "SRT生成中", "progress": 80, "status": "processing"}

data: {"step": "字幕焼き込み中", "progress": 92, "status": "processing"}

data: {"step": "完了", "progress": 100, "status": "done"}
```

エラー時:
```
data: {"step": "エラー", "progress": 35, "status": "error", "error_message": "音声の文字起こしに失敗しました"}
```

### SSE イベントフィールド

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `step` | string | 現在の処理ステップ名 |
| `progress` | integer (0-100) | 全体進捗率 |
| `status` | string | `queued` / `processing` / `done` / `error` |
| `error_message` | string (optional) | エラー時のみ。エラー詳細メッセージ |

- `status` が `done` または `error` になった時点で接続を切断する
- ジョブが存在しない場合は即座に接続を切断し `{"status": "error", "error_message": "ジョブが見つかりません"}` を送信

---

## GET `/api/jobs/{job_id}/status`

ジョブの現在ステータスを1回取得する（SSE 不使用のポーリング代替）。

### リクエスト

```
GET /api/jobs/550e8400-e29b-41d4-a716-446655440000/status
```

### パスパラメータ

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `job_id` | string (UUID v4) | ジョブ識別子 |

### レスポンス — 成功 `200 OK`

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "step": "翻訳中",
  "progress": 62,
  "created_at": "2026-03-01T10:00:00Z",
  "updated_at": "2026-03-01T10:05:30Z",
  "error_message": null
}
```

完了時:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "done",
  "step": "完了",
  "progress": 100,
  "created_at": "2026-03-01T10:00:00Z",
  "updated_at": "2026-03-01T10:12:00Z",
  "error_message": null
}
```

### レスポンスフィールド

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `job_id` | string | ジョブ識別子 |
| `status` | string | `queued` / `processing` / `done` / `error` |
| `step` | string | 現在ステップ名 |
| `progress` | integer | 進捗率 (0-100) |
| `created_at` | string (ISO 8601) | ジョブ作成日時 |
| `updated_at` | string (ISO 8601) | 最終更新日時 |
| `error_message` | string or null | エラー時のメッセージ |

### レスポンス — エラー

| HTTP Status | 条件 | レスポンス |
|-------------|------|-----------|
| 404 | ジョブ未発見 | `{"detail": "指定されたジョブが見つかりません"}` |

---

## GET `/api/jobs/{job_id}/download/srt`

生成された SRT ファイルをダウンロードする。

### リクエスト

```
GET /api/jobs/550e8400-e29b-41d4-a716-446655440000/download/srt
```

### レスポンス — 成功 `200 OK`

```
Content-Type: text/plain; charset=utf-8
Content-Disposition: attachment; filename="subtitle.srt"

1
00:00:01,000 --> 00:00:04,500
これはサンプルの字幕です。

2
00:00:05,000 --> 00:00:08,200
翻訳された日本語テキストが表示されます。
```

### レスポンス — エラー

| HTTP Status | 条件 | レスポンス |
|-------------|------|-----------|
| 404 | ジョブ未発見 | `{"detail": "指定されたジョブが見つかりません"}` |
| 409 | 処理未完了 | `{"detail": "処理がまだ完了していません。status が done になるまでお待ちください"}` |
| 500 | ファイル読み取りエラー | `{"detail": "SRT ファイルの取得に失敗しました"}` |

---

## GET `/api/jobs/{job_id}/download/video`

字幕焼き込み済み動画ファイルをダウンロードする。

### リクエスト

```
GET /api/jobs/550e8400-e29b-41d4-a716-446655440000/download/video
```

### レスポンス — 成功 `200 OK`

```
Content-Type: video/mp4
Content-Disposition: attachment; filename="output.mp4"
Content-Length: (ファイルサイズ)

(バイナリストリーム)
```

- 大容量ファイルのため `FileResponse` によるストリーミング配信
- Range リクエストには非対応（将来課題）

### レスポンス — エラー

| HTTP Status | 条件 | レスポンス |
|-------------|------|-----------|
| 404 | ジョブ未発見 | `{"detail": "指定されたジョブが見つかりません"}` |
| 409 | 処理未完了 | `{"detail": "処理がまだ完了していません。status が done になるまでお待ちください"}` |
| 500 | ファイル読み取りエラー | `{"detail": "動画ファイルの取得に失敗しました"}` |

---

## 進捗率の対応表

| 処理フェーズ | 進捗範囲 | ステップ名 |
|------------|---------|-----------|
| キュー待機 | 0% | `"待機中"` |
| 音声抽出 (FFmpeg) | 0 → 20% | `"音声抽出中"` |
| 文字起こし (Whisper) | 20 → 50% | `"文字起こし中"` |
| 日本語翻訳 (Ollama) | 50 → 75% | `"翻訳中"` |
| SRT 生成 | 75 → 85% | `"SRT生成中"` |
| 字幕焼き込み (FFmpeg) | 85 → 100% | `"字幕焼き込み中"` |
| 完了 | 100% | `"完了"` |

---

## cURL コマンド例

### アップロード（デフォルト設定）

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/path/to/video.mp4"
```

### アップロード（カスタム設定）

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/path/to/video.mp4" \
  -F 'settings={"whisper_model":"small","translation_parallel":2,"output_crf":20}'
```

### SSE ストリーム購読

```bash
curl -N http://localhost:8000/api/jobs/550e8400-e29b-41d4-a716-446655440000/stream
```

### ステータス確認

```bash
curl http://localhost:8000/api/jobs/550e8400-e29b-41d4-a716-446655440000/status
```

### SRT ダウンロード

```bash
curl -o subtitle.srt \
  http://localhost:8000/api/jobs/550e8400-e29b-41d4-a716-446655440000/download/srt
```

### 動画ダウンロード

```bash
curl -o output.mp4 \
  http://localhost:8000/api/jobs/550e8400-e29b-41d4-a716-446655440000/download/video
```
