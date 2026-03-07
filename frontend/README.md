# Frontend — 外国語動画 日本語字幕生成アプリ

Vue 3 + Vite + TypeScript によるフロントエンドです。

## 起動

```bash
npm install
npm run dev   # http://localhost:5173
```

バックエンド (`http://localhost:8000`) が起動している必要があります。
`/api` へのリクエストは Vite の開発サーバープロキシで転送されます。

## ビルド

```bash
npm run build   # dist/ に出力
```

## 構成

```
src/
├── App.vue                    # ルートコンポーネント（画面遷移管理）
├── api/
│   └── client.ts              # axios ベース API クライアント
├── components/
│   ├── VideoUploader.vue      # ドラッグ&ドロップアップロード UI
│   ├── ProcessingStatus.vue   # SSE 購読・進捗表示 UI
│   ├── ResultDownloader.vue   # ダウンロードリンク UI
│   └── SettingsModal.vue      # 設定モーダル
└── composables/
    ├── useJob.ts              # SSE 購読・ジョブ状態管理
    └── useSettings.ts         # 設定の localStorage 永続化
```
