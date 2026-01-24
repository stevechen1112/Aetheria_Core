#!/bin/bash

# 啟動 API 服務和測試的腳本

echo "關閉舊的 API 服務..."
pkill -9 -f api_server.py 2>/dev/null

echo "等待 2 秒..."
sleep 2

echo "啟動 API 服務..."
cd /Users/yuchuchen/Desktop/Aetheria_Core
python api_server.py > api_output.log 2>&1 &
API_PID=$!

echo "API 服務 PID: $API_PID"
echo "等待 10 秒讓 API 服務完全啟動..."
sleep 10

echo "測試 API 健康狀態..."
curl -s http://localhost:5001/health

echo ""
echo "執行 Steve 的測試..."
python test_steve_bazi_cross.py

echo ""
echo "測試完成！"
echo "API 服務仍在背景運行（PID: $API_PID）"
echo "若要停止：kill $API_PID"
