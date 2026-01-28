#!/bin/bash
# Aetheria Core - 自動部署腳本
# 使用方式: bash deploy.sh

set -e

echo "=========================================="
echo "   Aetheria Core 自動部署腳本"
echo "=========================================="

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置變數
APP_DIR="/opt/aetheria"
APP_USER="aetheria"
DOMAIN="172.237.19.63"

# 函數：輸出訊息
info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# 1. 系統更新和安裝依賴
info "正在更新系統並安裝依賴..."
apt update
apt install -y python3 python3-pip python3-venv nodejs npm nginx curl git

# 檢查 Node.js 版本
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    warn "Node.js 版本過舊，正在升級..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
fi

# 2. 創建應用目錄
info "正在設置應用目錄..."
mkdir -p $APP_DIR
cd $APP_DIR

# 3. 檢查檔案是否已上傳
if [ ! -f "$APP_DIR/requirements.txt" ]; then
    error "請先上傳專案檔案到 $APP_DIR"
fi

# 4. 設置 Python 虛擬環境
info "正在設置 Python 環境..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. 提示設置環境變數
if [ ! -f "$APP_DIR/.env" ]; then
    warn "請設置環境變數！"
    cat > $APP_DIR/.env << 'ENVEOF'
# 請填入您的 API Keys
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
MODEL_NAME=gemini-2.0-flash
ENVEOF
    echo ""
    echo "=========================================="
    echo "請編輯 $APP_DIR/.env 填入您的 API Keys"
    echo "編輯完成後，重新執行此腳本"
    echo "=========================================="
    exit 0
fi

# 6. 創建 systemd 服務
info "正在創建 systemd 服務..."
cat > /etc/systemd/system/aetheria-api.service << 'SERVICEEOF'
[Unit]
Description=Aetheria API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/aetheria
Environment=PYTHONPATH=/opt/aetheria
EnvironmentFile=/opt/aetheria/.env
ExecStart=/opt/aetheria/venv/bin/python run.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICEEOF

# 7. 構建前端
info "正在構建前端..."
cd $APP_DIR/webapp
npm install
npm run build

# 8. 設置 Nginx
info "正在設置 Nginx..."
cat > /etc/nginx/sites-available/aetheria << NGINXEOF
server {
    listen 80;
    server_name $DOMAIN;

    # 前端靜態檔案
    location / {
        root /opt/aetheria/webapp/dist;
        try_files \$uri \$uri/ /index.html;
        
        # 緩存靜態資源
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
            expires 30d;
            add_header Cache-Control "public, immutable";
        }
    }

    # API 代理
    location /api {
        proxy_pass http://127.0.0.1:5001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:5001/health;
    }
}
NGINXEOF

# 啟用網站配置
ln -sf /etc/nginx/sites-available/aetheria /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 測試 Nginx 配置
nginx -t

# 9. 啟動服務
info "正在啟動服務..."
systemctl daemon-reload
systemctl enable aetheria-api
systemctl restart aetheria-api
systemctl restart nginx

# 10. 等待服務啟動
info "等待服務啟動..."
sleep 5

# 11. 驗證部署
info "正在驗證部署..."
echo ""
echo "=========================================="
echo "   部署完成！"
echo "=========================================="
echo ""

# 檢查 API
if curl -s http://127.0.0.1:5001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} API 服務運行中 (port 5001)"
else
    echo -e "${RED}✗${NC} API 服務啟動失敗"
    echo "  查看日誌: journalctl -u aetheria-api -f"
fi

# 檢查 Nginx
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓${NC} Nginx 運行中 (port 80)"
else
    echo -e "${RED}✗${NC} Nginx 啟動失敗"
fi

echo ""
echo "=========================================="
echo "   訪問地址: http://$DOMAIN"
echo "=========================================="
echo ""
echo "常用命令："
echo "  查看 API 日誌:  journalctl -u aetheria-api -f"
echo "  重啟 API:       systemctl restart aetheria-api"
echo "  查看狀態:       systemctl status aetheria-api"
echo ""
