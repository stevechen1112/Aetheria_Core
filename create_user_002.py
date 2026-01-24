"""
快速创建测试用户 test_user_002
"""
import requests
import time

BASE_URL = 'http://localhost:5000'

print("="*60)
print("创建测试用户 test_user_002")
print("="*60)

# 1. 分析命盘
print("\n正在分析命盘...")
response = requests.post(
    f'{BASE_URL}/api/analysis',
    json={
        'user_id': 'test_user_002',
        'birth_date': '农历70年5月15日',
        'birth_time': '14:30',
        'birth_location': '台湾台北市',
        'gender': '女'
    }
)

if response.status_code == 200:
    print("✓ 命盘分析完成")
    
    # 2. 锁定命盘
    time.sleep(2)
    print("\n正在锁定命盘...")
    lock_response = requests.post(
        f'{BASE_URL}/api/lock',
        json={'user_id': 'test_user_002'}
    )
    
    if lock_response.status_code == 200:
        print("✓ 命盘已锁定")
        print("\n" + "="*60)
        print("✓ test_user_002 创建成功！")
        print("="*60)
        print("\n现在可以运行测试了：")
        print("  python test_advanced_auto.py")
    else:
        print(f"✗ 锁定失败: {lock_response.text}")
else:
    print(f"✗ 分析失败: {response.text}")
