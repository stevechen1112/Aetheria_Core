#!/bin/bash
set -e

cd /opt/aetheria

echo "📥 Pulling latest code..."
git fetch origin
git reset --hard origin/main
git log -1 --oneline

echo ""
echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install -q -r requirements.txt

echo ""
echo "📦 Installing frontend dependencies..."
cd webapp
npm install --silent

echo ""
echo "🏗️ Building frontend..."
npm run build

echo ""
echo "🔄 Restarting service..."
cd /opt/aetheria
systemctl restart aetheria-api.service
sleep 3

echo ""
echo "✅ Deployment completed!"
systemctl status aetheria-api.service --no-pager -l

echo ""
echo "🧪 Testing health endpoint..."
sleep 2
curl -s http://localhost:5001/health || echo "Health check failed"
