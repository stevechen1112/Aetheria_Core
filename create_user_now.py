#!/usr/bin/env python3
"""快速创建 test_user_002"""
import requests
import time
import sys

def main():
    base_url = "http://localhost:5000"
    
    print("=" * 60)
    print("创建 test_user_002")
    print("=" * 60)
    
    # 步骤1：分析命盘
    print("\n[1/3] 开始命盘分析...")
    try:
        r1 = requests.post(
            f"{base_url}/api/chart/initial-analysis",
            json={
                "user_id": "test_user_002",
                "birth_date": "农历70年5月15日",
                "birth_time": "14:30",
                "birth_location": "台湾台北市",
                "gender": "女"
            },
            timeout=120
        )
        if r1.status_code == 200:
            print("✓ 分析完成")
        else:
            print(f"✗ 分析失败 (状态码: {r1.status_code})")
            print(f"响应: {r1.text}")
            sys.exit(1)
    except Exception as e:
        print(f"✗ 错误: {e}")
        sys.exit(1)
    
    # 等待2秒
    print("\n等待 2 秒...")
    time.sleep(2)
    
    # 步骤2：锁定命盘
    print("\n[2/3] 锁定命盘...")
    try:
        r2 = requests.post(
            f"{base_url}/api/chart/lock",
            json={"user_id": "test_user_002"},
            timeout=10
        )
        if r2.status_code == 200:
            print("✓ 命盘已锁定")
        else:
            print(f"✗ 锁定失败 (状态码: {r2.status_code})")
            print(f"响应: {r2.text}")
            sys.exit(1)
    except Exception as e:
        print(f"✗ 错误: {e}")
        sys.exit(1)
    
    # 验证
    print("\n[3/3] 验证创建结果...")
    try:
        verify = requests.get(f"{base_url}/api/chart/lock/test_user_002", timeout=10)
        if verify.status_code == 200:
            print("✓ test_user_002 创建成功！")
            print("\n" + "=" * 60)
            print("用户信息:")
            print("  用户ID: test_user_002")
            print("  出生: 农历70年5月15日 14:30")
            print("  地点: 台湾台北市")
            print("  性别: 女")
            print("=" * 60)
            print("\n✓ 现在可以运行合盘测试了！")
        else:
            print(f"✗ 验证失败 (状态码: {verify.status_code})")
            sys.exit(1)
    except Exception as e:
        print(f"✗ 错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
