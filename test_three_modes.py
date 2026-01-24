"""
紫微斗数 + 八字命理 交叉验证测试
测试三种模式的完整流程
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

TEST_USER = {
    "user_id": "test_user_001",  # 使用已锁定的测试用户
    "year": 1979,
    "month": 10,
    "day": 11,
    "hour": 23,
    "minute": 58,
    "gender": "male",
    "longitude": 120.52
}


def test_mode_1_ziwei_only():
    """模式1：仅使用紫微斗数"""
    print("\n" + "="*70)
    print("模式1：紫微斗数单独分析")
    print("="*70)
    
    # 检查是否已锁定
    url = f"{BASE_URL}/api/chart/get-lock?user_id={TEST_USER['user_id']}"
    response = requests.get(url)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('locked'):
            print(f"\n✓ 用户已锁定紫微命盘")
            print(f"  命宫：{result['chart_structure']['命宮']['宮位']}")
            main_stars = result['chart_structure']['命宮'].get('主星', [])
            if main_stars:
                print(f"  主星：{', '.join(main_stars)}")
            else:
                print(f"  主星：无主星（空宫）")
            print(f"  锁定时间：{result['locked_at']}")
            return True
    
    print(f"\n⚠️ 用户未锁定紫微命盘")
    print(f"  提示：需先通过 /api/chart/initial-analysis 进行定盘并锁定")
    return False


def test_mode_2_bazi_only():
    """模式2：仅使用八字命理"""
    print("\n" + "="*70)
    print("模式2：八字命理单独分析")
    print("="*70)
    
    url = f"{BASE_URL}/api/bazi/calculate"
    response = requests.post(url, json=TEST_USER)
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            bazi_data = result['data']
            print(f"\n✓ 八字排盘成功")
            print(f"  四柱：{bazi_data['四柱']['年柱']['天干']}{bazi_data['四柱']['年柱']['地支']} " +
                  f"{bazi_data['四柱']['月柱']['天干']}{bazi_data['四柱']['月柱']['地支']} " +
                  f"{bazi_data['四柱']['日柱']['天干']}{bazi_data['四柱']['日柱']['地支']} " +
                  f"{bazi_data['四柱']['时柱']['天干']}{bazi_data['四柱']['时柱']['地支']}")
            print(f"  日主：{bazi_data['日主']['天干']}（{bazi_data['日主']['五行']}）")
            print(f"  身强弱：{bazi_data['强弱']['结论']}")
            return True
        else:
            print(f"\n✗ 八字排盘失败：{result.get('message')}")
            return False
    else:
        print(f"\n✗ 请求失败：{response.text}")
        return False


def test_mode_3_cross_validation():
    """模式3：紫微+八字交叉验证"""
    print("\n" + "="*70)
    print("模式3：紫微斗数 + 八字命理 交叉验证")
    print("="*70)
    print("\n提示：此测试需要调用 Gemini AI，预计耗时 60-90 秒...")
    
    url = f"{BASE_URL}/api/cross-validation/ziwei-bazi"
    
    print(f"\n发送请求时间：{datetime.now().strftime('%H:%M:%S')}")
    start_time = datetime.now()
    
    response = requests.post(url, json=TEST_USER, timeout=180)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n状态码：{response.status_code}")
    print(f"响应时间：{duration:.2f} 秒")
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            data = result['data']
            
            print("\n✓ 交叉验证分析成功！")
            
            # 紫微信息
            print(f"\n紫微命盘：")
            print(f"  命宫：{data['ziwei_chart']['locked_palace']}")
            print(f"  身宫：{data['ziwei_chart']['body_palace']}")
            print(f"  主星：{', '.join(data['ziwei_chart']['main_stars'])}")
            
            # 八字信息
            bazi = data['bazi_chart']
            print(f"\n八字命盘：")
            print(f"  四柱：{bazi['四柱']['年柱']['天干']}{bazi['四柱']['年柱']['地支']} " +
                  f"{bazi['四柱']['月柱']['天干']}{bazi['四柱']['月柱']['地支']} " +
                  f"{bazi['四柱']['日柱']['天干']}{bazi['四柱']['日柱']['地支']} " +
                  f"{bazi['四柱']['时柱']['天干']}{bazi['四柱']['时柱']['地支']}")
            print(f"  日主：{bazi['日主']['天干']}（{bazi['日主']['五行']}）")
            
            # 交叉验证分析
            analysis = data['cross_validation_analysis']
            print(f"\n交叉验证分析长度：{len(analysis)} 字符")
            print(f"\n分析内容预览（前500字）：")
            print("-" * 70)
            print(analysis[:500] + "...")
            print("-" * 70)
            
            # 保存完整分析
            filename = f"cross_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"紫微斗数 + 八字命理 交叉验证分析报告\n")
                f.write(f"="*70 + "\n")
                f.write(f"用户：{TEST_USER['user_id']}\n")
                f.write(f"生辰：{TEST_USER['year']}年{TEST_USER['month']}月{TEST_USER['day']}日 {TEST_USER['hour']}时\n")
                f.write(f"分析时间：{data['timestamp']}\n")
                f.write(f"="*70 + "\n\n")
                
                f.write(f"【紫微命盘】\n")
                f.write(f"命宫：{data['ziwei_chart']['locked_palace']}\n")
                f.write(f"身宫：{data['ziwei_chart']['body_palace']}\n")
                f.write(f"主星：{', '.join(data['ziwei_chart']['main_stars'])}\n\n")
                
                f.write(f"【八字命盘】\n")
                f.write(f"四柱：{bazi['四柱']['年柱']['天干']}{bazi['四柱']['年柱']['地支']} " +
                       f"{bazi['四柱']['月柱']['天干']}{bazi['四柱']['月柱']['地支']} " +
                       f"{bazi['四柱']['日柱']['天干']}{bazi['四柱']['日柱']['地支']} " +
                       f"{bazi['四柱']['时柱']['天干']}{bazi['四柱']['时柱']['地支']}\n")
                f.write(f"日主：{bazi['日主']['天干']}（{bazi['日主']['五行']}）\n")
                f.write(f"身强弱：{bazi['强弱']['结论']}\n")
                f.write(f"用神：{', '.join(bazi['用神']['用神'])}\n\n")
                
                f.write(f"="*70 + "\n")
                f.write(f"【交叉验证分析】\n\n")
                f.write(analysis)
            
            print(f"\n完整交叉验证分析已保存到：{filename}")
            
            return True
        else:
            print(f"\n✗ 交叉验证失败：{result.get('message')}")
            return False
    else:
        print(f"\n✗ 请求失败：{response.text}")
        return False


def main():
    print("\n" + "="*70)
    print("Aetheria 三种模式完整测试")
    print("="*70)
    print(f"\n测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API 地址：{BASE_URL}")
    print(f"测试用户：{TEST_USER['user_id']}")
    
    # 检查 API
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("\n✗ API 服务未运行")
            return
    except:
        print("\n✗ 无法连接到 API 服务")
        return
    
    print("\n✓ API 服务运行正常")
    
    # 测试三种模式
    results = []
    
    print("\n" + "="*70)
    print("开始测试...")
    print("="*70)
    
    # 模式1：紫微斗数（检查是否已锁定）
    results.append(("模式1: 紫微斗数单独分析", test_mode_1_ziwei_only()))
    
    # 模式2：八字命理
    results.append(("模式2: 八字命理单独分析", test_mode_2_bazi_only()))
    
    # 询问是否测试模式3
    if results[0][1]:  # 如果紫微已锁定
        print("\n" + "="*70)
        user_input = input("\n是否测试模式3（交叉验证）？需要 Gemini API，约 60-90 秒 [y/N]: ")
        
        if user_input.lower() == 'y':
            results.append(("模式3: 紫微+八字交叉验证", test_mode_3_cross_validation()))
        else:
            print("\n跳过模式3测试")
    else:
        print("\n⚠️ 模式1未通过，跳过模式3测试")
        print("提示：请先使用 test_user_cross_validation 进行紫微定盘并锁定")
    
    # 总结
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败/跳过"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n总计：{passed}/{total} 项测试通过")
    
    print("\n" + "="*70)
    print("三种使用模式说明：")
    print("="*70)
    print("1. 紫微斗数单独分析：使用 /api/chart/* 端点")
    print("2. 八字命理单独分析：使用 /api/bazi/* 端点")
    print("3. 交叉验证分析：使用 /api/cross-validation/ziwei-bazi 端点")
    print("\n用户可根据需求选择任一模式或组合使用")


if __name__ == "__main__":
    main()
