.PHONY: backend frontend setup setup-backend setup-frontend

# バックエンド起動
backend:
	cd backend && .venv/bin/uvicorn app.main:app --reload

# フロントエンド起動
frontend:
	cd frontend && npm run dev

# 初回セットアップ
setup: setup-backend setup-frontend

setup-backend:
	cd backend && python -m venv .venv && .venv/bin/pip install -r requirements.txt
	@if [ ! -f backend/.env ]; then cp backend/.env.example backend/.env; echo "backend/.env を作成しました。内容を確認してください。"; fi

setup-frontend:
	cd frontend && npm install
