#!/usr/bin/env python3
"""
Aetheria Core - 啟動入口
=========================

啟動 API 服務的統一入口點

使用方式：
    python run.py              # 啟動 API 服務（預設 port 5001）
    python run.py --port 8080  # 指定端口
    python run.py --debug      # 開發模式
"""

import sys
import os
import argparse

# 將專案根目錄加入 Python 路徑
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

def main():
    """主程式入口"""
    parser = argparse.ArgumentParser(
        description='Aetheria Core - 六大命理系統 API 服務'
    )
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=5001,
        help='API 服務端口（預設：5001）'
    )
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='API 服務主機（預設：0.0.0.0）'
    )
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='啟用除錯模式'
    )
    
    args = parser.parse_args()
    
    # 導入並啟動 API 服務
    from src.api.server import app
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║          Aetheria Core - 六大命理系統 API v1.8.0          ║
╠══════════════════════════════════════════════════════════╣
║  系統：紫微斗數 | 八字命理 | 西洋占星術                    ║
║        靈數學   | 姓名學   | 塔羅牌                        ║
╠══════════════════════════════════════════════════════════╣
║  服務地址：http://{args.host}:{args.port}                       ║
║  健康檢查：http://{args.host}:{args.port}/health                ║
║  除錯模式：{'開啟' if args.debug else '關閉'}                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )


if __name__ == '__main__':
    main()
