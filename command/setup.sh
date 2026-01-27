#!/bin/bash
# 初回セットアップスクリプト（依存関係インストール）

set -e

echo "🔧 Setting up development environment..."
echo ""

# プロジェクトルートに移動
cd "$(dirname "$0")"

# バックエンドのセットアップ
echo "📦 Installing backend dependencies..."
if ! command -v uv &> /dev/null; then
  echo "❌ Error: uv is not installed"
  echo "   Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
fi
uv sync
echo "✅ Backend dependencies installed"
echo ""

# フロントエンドのセットアップ
echo "🎨 Installing frontend dependencies..."
cd frontend
if ! command -v npm &> /dev/null; then
  echo "❌ Error: npm is not installed"
  echo "   Install Node.js from: https://nodejs.org/"
  exit 1
fi
npm install
echo "✅ Frontend dependencies installed"
echo ""

cd ..
echo "✅ Setup complete!"
echo ""
echo "Run './dev.sh' to start development servers"
