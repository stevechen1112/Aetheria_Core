"""
完整系统测试 - 包括所有 AI 分析
自动运行所有测试，无需用户交互
"""

import requests
import json
from datetime import datetime
import time

BASE_URL = "http://localhost:5001"

# 使用 test_user_001 (Steve) 的数据
STEVE = {
    "user_id": "test_user_001",
    "year": 1979,
    "month": 10,
    "day": 11,
    "hour": 23,
    "minute": 58,
    "gender": "male",
    "longitude": 120.52
}


def print_section(title):
    """打印分节标题"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def test_bazi_calculate():
    """测试1：八字排盘计算（快速）"""
    print_section("测试 1/5：八字排盘计算")
    
    url = f"{BASE_URL}/api/bazi/calculate"
    response = requests.post(url, json=STEVE)
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            bazi = result['data']
            print(f"\n✓ 八字排盘成功")
            print(f"  四柱：{bazi['四柱']['年柱']['天干']}{bazi['四柱']['年柱']['地支']} "
                  f"{bazi['四柱']['月柱']['天干']}{bazi['四柱']['月柱']['地支']} "
                  f"{bazi['四柱']['日柱']['天干']}{bazi['四柱']['日柱']['地支']} "
                  f"{bazi['四柱']['时柱']['天干']}{bazi['四柱']['时柱']['地支']}")
            print(f"  日主：{bazi['日主']['天干']}（{bazi['日主']['五行']}）")
            print(f"  强弱：{bazi['强弱']['结论']}（{bazi['强弱']['评分']}/100）")
            print(f"  用神：{', '.join(bazi['用神']['用神'])}")
            return True, bazi
    
    print(f"\n✗ 测试失败：{response.text}")
    return False, None


def test_bazi_analysis():
    """测试2：八字命理分析（AI）"""
    print_section("测试 2/5：八字命理分析（AI）")
    print("预计耗时：30-45 秒...\n")
    
    url = f"{BASE_URL}/api/bazi/analysis"
    
    start_time = time.time()
    try:
        response = requests.post(url, json=STEVE, timeout=120)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            if result['status'] == 'success':
                analysis = result['data']['analysis']
                print(f"✓ 八字分析成功（耗时：{duration:.1f}秒）")
                print(f"  分析长度：{len(analysis)} 字符")
                print(f"\n前 300 字预览：")
                print("-" * 80)
                print(analysis[:300] + "...")
                print("-" * 80)
                
                # 保存完整分析
                filename = f"output_bazi_analysis_steve_{datetime.now().strftime('%H%M%S')}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Steve 的八字命理分析\n{'='*80}\n\n")
                    f.write(analysis)
                print(f"\n完整分析已保存：{filename}")
                
                return True, analysis
        
        print(f"\n✗ 测试失败：{response.text}")
        return False, None
        
    except requests.exceptions.Timeout:
        print(f"\n✗ 请求超时（>{120}秒）")
        return False, None
    except Exception as e:
        print(f"\n✗ 错误：{str(e)}")
        return False, None


def test_bazi_fortune():
    """测试3：八字流年运势（AI）"""
    print_section("测试 3/5：八字流年运势分析（AI）")
    print("预计耗时：30-45 秒...\n")
    
    test_data = {**STEVE, "query_year": 2026, "query_month": None}
    url = f"{BASE_URL}/api/bazi/fortune"
    
    start_time = time.time()
    try:
        response = requests.post(url, json=test_data, timeout=120)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            if result['status'] == 'success':
                fortune = result['data']['fortune_analysis']
                print(f"✓ 运势分析成功（耗时：{duration:.1f}秒）")
                print(f"  分析长度：{len(fortune)} 字符")
                print(f"\n前 300 字预览：")
                print("-" * 80)
                print(fortune[:300] + "...")
                print("-" * 80)
                
                # 保存完整分析
                filename = f"output_bazi_fortune_2026_steve_{datetime.now().strftime('%H%M%S')}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Steve 的 2026 年八字流年运势\n{'='*80}\n\n")
                    f.write(fortune)
                print(f"\n完整分析已保存：{filename}")
                
                return True, fortune
        
        print(f"\n✗ 测试失败：{response.text}")
        return False, None
        
    except requests.exceptions.Timeout:
        print(f"\n✗ 请求超时（>{120}秒）")
        return False, None
    except Exception as e:
        print(f"\n✗ 错误：{str(e)}")
        return False, None


def test_ziwei_status():
    """测试4：检查紫微锁盘状态"""
    print_section("测试 4/5：紫微命盘锁定状态")
    
    url = f"{BASE_URL}/api/chart/get-lock?user_id={STEVE['user_id']}"
    response = requests.get(url)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('locked'):
            chart = result['chart_structure']['命宮']
            print(f"\n✓ Steve 的紫微命盘已锁定")
            print(f"  命宫：{chart['宮位']}")
            main_stars = chart.get('主星', [])
            if main_stars:
                print(f"  主星：{', '.join(main_stars)}")
            else:
                print(f"  主星：无主星（空宫）")
            print(f"  锁定时间：{result['locked_at']}")
            return True, result
    
    print(f"\n✗ Steve 未锁定紫微命盘")
    print(f"  提示：需要先进行紫微定盘并锁定")
    return False, None


def test_cross_validation():
    """测试5：交叉验证分析（AI）"""
    print_section("测试 5/5：紫微+八字交叉验证（AI）")
    print("预计耗时：60-90 秒...\n")
    
    url = f"{BASE_URL}/api/cross-validation/ziwei-bazi"
    
    start_time = time.time()
    try:
        response = requests.post(url, json=STEVE, timeout=180)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            if result['status'] == 'success':
                data = result['data']
                validation = data['cross_validation_analysis']
                
                print(f"✓ 交叉验证成功（耗时：{duration:.1f}秒）")
                print(f"  分析长度：{len(validation)} 字符")
                
                # 显示紫微和八字摘要
                print(f"\n紫微命盘：")
                ziwei = data['ziwei_chart']
                print(f"  命宫：{ziwei['locked_palace']}")
                print(f"  主星：{', '.join(ziwei['main_stars'])}")
                
                print(f"\n八字命盘：")
                bazi = data['bazi_chart']
                pillars = bazi['四柱']
                print(f"  四柱：{pillars['年柱']['天干']}{pillars['年柱']['地支']} "
                      f"{pillars['月柱']['天干']}{pillars['月柱']['地支']} "
                      f"{pillars['日柱']['天干']}{pillars['日柱']['地支']} "
                      f"{pillars['时柱']['天干']}{pillars['时柱']['地支']}")
                
                print(f"\n前 300 字预览：")
                print("-" * 80)
                print(validation[:300] + "...")
                print("-" * 80)
                
                # 保存完整分析
                filename = f"output_cross_validation_steve_{datetime.now().strftime('%H%M%S')}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Steve 的紫微+八字交叉验证分析\n{'='*80}\n\n")
                    f.write(f"紫微命盘：\n")
                    f.write(f"  命宫：{ziwei['locked_palace']}\n")
                    f.write(f"  主星：{', '.join(ziwei['main_stars'])}\n\n")
                    f.write(f"八字命盘：\n")
                    f.write(f"  四柱：{pillars['年柱']['天干']}{pillars['年柱']['地支']} "
                           f"{pillars['月柱']['天干']}{pillars['月柱']['地支']} "
                           f"{pillars['日柱']['天干']}{pillars['日柱']['地支']} "
                           f"{pillars['时柱']['天干']}{pillars['时柱']['地支']}\n")
                    f.write(f"  日主：{bazi['日主']['天干']}（{bazi['日主']['五行']}）\n\n")
                    f.write(f"{'='*80}\n\n")
                    f.write(validation)
                print(f"\n完整分析已保存：{filename}")
                
                return True, validation
        
        print(f"\n✗ 测试失败：{response.text}")
        return False, None
        
    except requests.exceptions.Timeout:
        print(f"\n✗ 请求超时（>{180}秒）")
        return False, None
    except Exception as e:
        print(f"\n✗ 错误：{str(e)}")
        return False, None


def main():
    """主测试流程"""
    print("\n" + "="*80)
    print("  Aetheria Core v1.3.0 - 完整系统测试")
    print("  测试用户：Steve (test_user_001)")
    print("  测试时间：" + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("="*80)
    
    # 检查 API
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("\n✗ API 服务未运行")
            return
        print("\n✓ API 服务运行正常")
    except:
        print("\n✗ 无法连接到 API 服务")
        print("  请先运行：python api_server.py")
        return
    
    results = []
    total_time = time.time()
    
    # 测试1：八字排盘
    success, bazi_data = test_bazi_calculate()
    results.append(("八字排盘计算", success))
    
    if not success:
        print("\n⚠️ 八字排盘失败，后续测试可能受影响")
    
    # 测试2：八字分析
    success, _ = test_bazi_analysis()
    results.append(("八字命理分析", success))
    
    # 测试3：八字运势
    success, _ = test_bazi_fortune()
    results.append(("八字流年运势", success))
    
    # 测试4：紫微状态
    success, ziwei_data = test_ziwei_status()
    results.append(("紫微锁盘状态", success))
    
    # 测试5：交叉验证（仅在紫微已锁定时）
    if ziwei_data:
        success, _ = test_cross_validation()
        results.append(("交叉验证分析", success))
    else:
        print("\n⚠️ 跳过交叉验证测试（需要先锁定紫微命盘）")
        results.append(("交叉验证分析", False))
    
    total_duration = time.time() - total_time
    
    # 测试总结
    print_section("测试总结")
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name:20s}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n总计：{passed}/{total} 项测试通过")
    print(f"总耗时：{total_duration:.1f} 秒")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统运行正常！")
    else:
        print(f"\n⚠️ {total - passed} 项测试失败")
    
    print("\n" + "="*80)
    print("  测试报告文件：")
    print("  - output_bazi_analysis_steve_*.txt")
    print("  - output_bazi_fortune_2026_steve_*.txt")
    print("  - output_cross_validation_steve_*.txt")
    print("="*80)


if __name__ == "__main__":
    main()
