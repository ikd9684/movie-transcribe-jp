# 実装タスクリスト — 外国語動画 日本語字幕生成アプリ

## フェーズ 0: ドキュメント整備 ✅

- [x] `docs/spec.md` — アプリ仕様書
- [x] `docs/architecture.md` — アーキテクチャ設計書
- [x] `docs/api.md` — API仕様書
- [x] `tasks/todo.md` — タスクリスト（本ファイル）
- [x] `tasks/lessons.md` — 教訓ログ

---

## フェーズ 1: プロジェクト基盤構築 ✅

### 1.1 Backend セットアップ

- [x] `backend/` ディレクトリ構造を作成
  - `app/`, `app/api/routes/`, `app/services/`, `app/models/`, `app/core/`
- [x] `backend/requirements.txt` を作成
  - fastapi, uvicorn, python-multipart, faster-whisper, httpx, python-dotenv, aiofiles
- [x] `backend/.env.example` を作成
  - `OLLAMA_BASE_URL`, `STORAGE_ROOT`, `MAX_UPLOAD_SIZE_MB`, `CORS_ORIGINS`
- [x] `backend/app/core/config.py` を実装
  - Pydantic Settings で環境変数を型安全に読み込み
- [x] `backend/app/main.py` を実装
  - FastAPI アプリ初期化・CORS・ルーター登録
- [x] `backend/app/models/schemas.py` を実装
  - `JobStatus`, `JobSettings`（9設定項目）, `JobInfo`, `UploadResponse`, `Segment`
- [x] `backend/app/core/job_manager.py` を実装
  - シングルトン `JobManager`・`Job` dataclass（settings 格納）・スレッドセーフ
- [x] `backend/app/api/routes/upload.py` を実装
  - `POST /api/upload`: settings JSON 受け取り・バリデーション・ジョブ登録
- [x] `backend/app/api/routes/jobs.py` を実装
  - status / stream / download/srt / download/video エンドポイント（stub 含む）

### 1.2 Frontend セットアップ

- [x] `frontend/` に Vue 3 + Vite + TypeScript プロジェクトを初期化
  - `npm create vite@latest` (vue-ts テンプレート)
- [x] 依存パッケージインストール: axios
- [x] `frontend/vite.config.ts` に `/api` → `localhost:8000` プロキシ設定
- [x] 不要なボイラープレートを削除・クリーンアップ

### 1.3 設定画面実装

- [x] `frontend/src/composables/useSettings.ts` を実装
  - 9項目の `AppSettings` 型・`DEFAULT_SETTINGS`・localStorage 読み書き
- [x] `frontend/src/components/SettingsModal.vue` を実装
  - 9設定項目の UI・保存/リセットボタン・ESC/オーバーレイで閉じる
- [x] `frontend/src/App.vue` を実装
  - ヘッダーにギアアイコン・`SettingsModal` 統合
- [x] `frontend/src/api/client.ts` を実装
  - `uploadVideo(file, settings)`: multipart/form-data で settings を JSON 送信

---

## フェーズ 2: Backend コア実装 ✅

### 2.1 スキーマ定義

- [x] `backend/app/models/schemas.py` を実装（フェーズ 1 で完了済み）

### 2.2 ジョブ管理

- [x] `backend/app/core/job_manager.py` を実装（フェーズ 1 で完了済み）

### 2.3 サービス層

- [x] `backend/app/services/video.py` を実装
- [x] `backend/app/services/transcription.py` を実装
- [x] `backend/app/services/translation.py` を実装
- [x] `backend/app/services/subtitle.py` を実装

### 2.4 処理パイプライン

- [x] `backend/app/core/pipeline.py` を実装
  - 5ステップ: 音声抽出→文字起こし→翻訳→SRT生成→字幕焼き込み
  - 進捗 0→20→50→75→85→100%

### 2.5 API ルート実装

- [x] `backend/app/api/routes/upload.py` を修正
  - `BackgroundTasks` DI 修正・`run_pipeline` 有効化
- [x] `backend/app/api/routes/jobs.py` を修正
  - SSE: while ループ + 0.5s sleep で完全実装
  - download エンドポイント: 409 チェック追加

---

## フェーズ 3: Frontend 実装 ✅

### 3.1 API クライアント

- [x] `frontend/src/api/client.ts` を実装（フェーズ 1 で完了済み）

### 3.2 Composable

- [x] `frontend/src/composables/useJob.ts` を実装
  - `EventSource` で SSE 購読
  - reactive な `status`, `progress`, `step`, `error` を返す
  - done/error でクリーンアップ
  - `downloadSRT`, `downloadVideo` 関数

### 3.3 コンポーネント実装

- [x] `frontend/src/components/VideoUploader.vue` を実装
  - ドラッグ&ドロップエリア + クリック選択
  - ファイル情報表示（名前・サイズ）
  - 拡張子バリデーション（mp4/mov/avi/mkv/webm/m4v）
  - アップロード中スピナー

- [x] `frontend/src/components/ProcessingStatus.vue` を実装
  - プログレスバー（0.5s transition）
  - 5ステップ一覧（チェックマーク付き）
  - エラー時: エラーメッセージ + 「やり直す」ボタン

- [x] `frontend/src/components/ResultDownloader.vue` を実装
  - SRT/動画ダウンロードボタン
  - 「別の動画を処理する」ボタン

### 3.4 App.vue 統合

- [x] `frontend/src/App.vue` を修正
  - ページ状態管理: `upload` / `processing` / `done`
  - 各状態でコンポーネント切り替え
  - `job_id` を状態として保持

---

## フェーズ 4: 結合テスト・品質確認

### 4.1 Backend 単体確認

- [x] `uvicorn app.main:app --reload` で起動確認
- [x] cURL でアップロード・SSE・ダウンロード動作確認
- [ ] 小さい動画ファイルで全パイプライン動作確認

### 4.2 Frontend 動作確認

- [x] `npm run dev` で起動確認（TypeScript ビルドエラーなし）
- [ ] ドラッグ&ドロップが機能するか確認
- [ ] SSE が正しく進捗を表示するか確認
- [ ] ダウンロードボタンが機能するか確認

### 4.3 E2E 動作確認

- [ ] 英語動画でフルパイプライン実行
- [ ] SRT ファイルの内容が正しいか確認
- [ ] 字幕焼き込み動画を再生して字幕が表示されるか確認
- [ ] エラーケース（音声なし動画、壊れたファイル）の動作確認

---

## フェーズ 5: 品質改善（オプション）

- [ ] 翻訳品質の調整（システムプロンプトチューニング）
- [ ] 長時間動画での並列翻訳のパフォーマンス確認
- [ ] 字幕スタイル（フォント・サイズ・位置）の調整
- [ ] エラーリカバリーの改善

---

## レビューセクション

### フェーズ 1 完了レビュー（2026-03-01）

**実装内容:**
- Vue 3 + Vite + TypeScript フロントエンド基盤を構築
- 9項目の設定を localStorage で永続化する `useSettings.ts` composable を実装
- `SettingsModal.vue` で設定 UI（カテゴリ別グルーピング、保存/リセット）を実装
- `App.vue` にヘッダーギアアイコンとモーダル統合
- `api/client.ts` でアップロード時に設定を JSON として multipart に付与
- FastAPI バックエンド基盤（CORS・ルーター）を構築
- `JobSettings` Pydantic モデル（9設定項目、バリデーション付き）を定義
- `JobManager` シングルトン（スレッドセーフ、settings 格納）を実装
- `/api/upload` エンドポイントで設定受け取りとジョブ登録を実装

---

### フェーズ 2 完了レビュー（2026-03-02）

**実装内容:**
- `services/subtitle.py`: SRT 生成（`HH:MM:SS,mmm` 変換、空セグメントスキップ）
- `services/video.py`: FFmpeg 音声抽出・字幕焼き込み（`run_in_executor` でオフロード）
- `services/transcription.py`: faster-whisper ラッパー（`threading.Lock` キャッシュ、language="auto"→None 変換）
- `services/translation.py`: Ollama 並列翻訳（`asyncio.Semaphore` + `asyncio.gather`、文脈付きプロンプト）
- `core/pipeline.py`: 5ステップパイプライン統合（進捗更新、エラーハンドリング）
- `api/routes/upload.py`: `BackgroundTasks` DI 修正、`run_pipeline` 有効化
- `api/routes/jobs.py`: SSE 完全実装、download に 409 チェック追加

---

### フェーズ 3 完了レビュー（2026-03-03）

**実装内容:**
- `composables/useJob.ts`: EventSource SSE購読・status/step/progress/error管理・done/errorで自動クローズ・`onUnmounted`クリーンアップ・downloadSRT/downloadVideo
- `components/VideoUploader.vue`: ドラッグ&ドロップ+クリック選択・拡張子バリデーション（6形式）・アップロード中スピナー・`emit('uploaded', job_id)`
- `components/ProcessingStatus.vue`: 5ステップ定義（threshold方式）・0.5s transitionプログレスバー・error時「やり直す」ボタン・`watch(status)`でdone emit
- `components/ResultDownloader.vue`: SRT/動画ダウンロードボタン・`useJob`のdownload関数利用・restart emit
- `App.vue`: PageState型（upload/processing/done）・3コンポーネント条件切り替え・onUploaded/onRetry/onRestart ハンドラ

---

### フェーズ 4 部分完了レビュー（2026-03-03）

**実施内容:**
- `services/video.py` Bug Fix:
  - `alignment` `6`（中段右）→ `8`（上段中央）に修正（subtitle_position="top" 時）
  - SRT パスエスケープにシングルクォート `'` → `\'` を追加
- Backend 全モジュール import チェック: 全11モジュール OK
- uvicorn 起動・`/docs` Swagger UI (HTTP 200) 確認
- Frontend `npm run build` TypeScript コンパイル・Vite ビルド成功
- cURL 検証:
  - `GET /api/jobs/nonexistent/status` → 404 "Job not found" ✅
  - `POST /api/upload` → 202 job_id 返却 ✅
  - `GET /api/jobs/{id}/status` → pipeline 起動・FFmpeg エラーで "error" 遷移 ✅
  - `GET /api/jobs/{id}/stream` → SSE でエラー状態を配信して終了 ✅

---

_最終更新: 2026-03-03_
