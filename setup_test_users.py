"""
准备测试环境 - 创建测试用户
"""

import requests
import json
import time

BASE_URL = 'http://localhost:5000'

def create_and_lock_user(user_id, birth_date, birth_time, birth_location, gender):
    """创建用户并完成定盘"""
    print(f"\n正在创建用户：{user_id}")
    
    # 1. 分析命盘
    response = requests.post(
        f'{BASE_URL}/api/analysis',
        json={
            'user_id': user_id,
            'birth_date': birth_date,
            'birth_time': birth_time,
            'birth_location': birth_location,
            'gender': gender
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"  ✓ 命盘分析完成")
        print(f"  命宫：{result['chart_structure']['命宫']['宫位']}宫")
        print(f"  主星：{', '.join(result['chart_structure']['命宫']['主星'])}")
        
        # 2. 锁定命盘
        time.sleep(1)
        lock_response = requests.post(
            f'{BASE_URL}/api/lock',
            json={'user_id': user_id}
        )
        
        if lock_response.status_code == 200:
            print(f"  ✓ 命盘已锁定")
            return True
        else:
            print(f"  ✗ 锁定失败: {lock_response.text}")
            return False
    else:
        print(f"  ✗ 分析失败: {response.text}")
        return False


def check_user_exists(user_id):
    """检查用户是否已存在并已定盘"""
    response = requests.get(f'{BASE_URL}/api/lock/{user_id}')
    return response.status_code == 200


def main():
    print("="*60)
    print("Aetheria 测试环境准备")
    print("="*60)
    
    # 检查 API 服务
    try:
        response = requests.get(f'{BASE_URL}/health', timeout=2)
        if response.status_code == 200:
            print("\n✓ API 服务运行正常")
        else:
            print("\n✗ API 服务异常")
            return
    except:
        print("\n✗ 无法连接到 API 服务")
        print("请先启动 API 服务：python api_server.py")
        return
    
    # 准备测试用户
    users = [
        {
            'user_id': 'test_user_001',
            'birth_date': '农历68年9月23日',
            'birth_time': '23:58',
            'birth_location': '台湾彰化市',
            'gender': '男'
        },
        {
            'user_id': 'test_user_002',
            'birth_date': '农历70年5月15日',
            'birth_time': '14:30',
            'birth_location': '台湾台北市',
            'gender': '女'
        }
    ]
    
    print("\n" + "="*60)
    print("准备测试用户")
    print("="*60)
    
    for user in users:
        if check_user_exists(user['user_id']):
            print(f"\n用户 {user['user_id']} 已存在且已定盘")
        else:
            success = create_and_lock_user(
                user['user_id'],
                user['birth_date'],
                user['birth_time'],
                user['birth_location'],
                user['gender']
            )
            if not success:
                print(f"\n✗ 用户 {user['user_id']} 设置失败")
                return
        
        time.sleep(1)
    
    print("\n" + "="*60)
    print("✓ 所有测试用户准备完成")
    print("="*60)
    print("\n可以执行以下测试：")
    print("  - python test_advanced.py        (互动式测试)")
    print("  - python test_advanced_auto.py   (自动化测试)")
    print("  - python test_fortune.py         (流年运势测试)")


if __name__ == '__main__':
    main()
