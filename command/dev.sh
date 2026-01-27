#!/bin/bash
# ローカル開発サーバー起動スクリプト（Dockerなし）

set -e

echo "🚀 Starting development servers..."
echo ""

# バックエンド起動（バックグラウンド）
echo "📦 Starting backend server..."
cd "$(dirname "$0")"
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
echo ""

# フロントエンド起動（フォアグラウンド）
echo "🎨 Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
echo ""

echo "✅ Development servers started!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop all servers"

# シグナルハンドラー
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# プロセスを待機
wait
