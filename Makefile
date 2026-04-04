.PHONY: backend frontend setup setup-backend setup-frontend build serve start

PORT ?= 8000

# フロントエンドをビルド
build:
	cd frontend && npm run build

# バックエンド起動（ポータルからはこれを呼ぶ）
serve:
	cd backend && .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port $(PORT)

# ビルド＋起動（初回デプロイ時に手動で実行）
start: build serve

# バックエンド起動（開発用、既存のまま）
backend:
	cd backend && .venv/bin/uvicorn app.main:app --reload

# フロントエンド起動（開発用、既存のまま）
frontend:
	cd frontend && npm run dev

# 初回セットアップ（既存のまま）
setup: setup-backend setup-frontend

setup-backend:
	cd backend && python -m venv .venv && .venv/bin/pip install -r requirements.txt
	@if [ ! -f backend/.env ]; then cp backend/.env.example backend/.env; echo "backend/.env を作成しました。内容を確認してください。"; fi

setup-frontend:
	cd frontend && npm install
