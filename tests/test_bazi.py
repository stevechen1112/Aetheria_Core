"""
八字系统功能测试脚本
测试三种模式：
1. 八字排盘计算
2. 八字命理分析
3. 八字流年运势
"""

import requests
import json
from datetime import datetime

# API 基础地址
BASE_URL = "http://localhost:5001"

# 测试数据
TEST_USER = {
    "user_id": "test_user_001",
    "year": 1979,
    "month": 10,
    "day": 11,
    "hour": 23,
    "minute": 58,
    "gender": "male",
    "longitude": 120.52,
    "use_apparent_solar_time": True
}


def test_bazi_calculate():
    """测试1：八字排盘计算"""
    print("\n" + "="*60)
    print("测试1：八字排盘计算")
    print("="*60)
    
    url = f"{BASE_URL}/api/bazi/calculate"
    response = requests.post(url, json=TEST_USER)
    
    print(f"\n状态码：{response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            bazi_data = result['data']
            print("\n✓ 八字排盘成功！")
            print(f"\n四柱八字：")
            print(f"  年柱：{bazi_data['四柱']['年柱']['天干']}{bazi_data['四柱']['年柱']['地支']} ({bazi_data['四柱']['年柱']['纳音']})")
            print(f"  月柱：{bazi_data['四柱']['月柱']['天干']}{bazi_data['四柱']['月柱']['地支']} ({bazi_data['四柱']['月柱']['纳音']})")
            print(f"  日柱：{bazi_data['四柱']['日柱']['天干']}{bazi_data['四柱']['日柱']['地支']} ({bazi_data['四柱']['日柱']['纳音']})")
            print(f"  时柱：{bazi_data['四柱']['时柱']['天干']}{bazi_data['四柱']['时柱']['地支']} ({bazi_data['四柱']['时柱']['纳音']})")
            
            print(f"\n日主信息：")
            print(f"  天干：{bazi_data['日主']['天干']}")
            print(f"  五行：{bazi_data['日主']['五行']}")
            
            print(f"\n强弱分析：")
            print(f"  结论：{bazi_data['强弱']['结论']}")
            print(f"  评分：{bazi_data['强弱']['评分']}/100")
            
            print(f"\n用神系统：")
            print(f"  用神：{', '.join(bazi_data['用神']['用神'])}")
            print(f"  喜神：{', '.join(bazi_data['用神']['喜神'])}")
            print(f"  忌神：{', '.join(bazi_data['用神']['忌神'])}")
            
            print(f"\n大运（前3步）：")
            for dayun in bazi_data['大运'][:3]:
                print(f"  {dayun['序号']}. {dayun['天干']}{dayun['地支']} ({dayun['纳音']}) - {dayun['年龄']}")
            
            return True
        else:
            print(f"\n✗ 八字排盘失败：{result.get('message', '未知错误')}")
            return False
    else:
        print(f"\n✗ 请求失败：{response.text}")
        return False


def test_bazi_analysis():
    """测试2：八字命理分析（需要等待AI响应，约30-45秒）"""
    print("\n" + "="*60)
    print("测试2：八字命理分析")
    print("="*60)
    print("\n提示：此测试需要调用 Gemini AI，预计耗时 30-45 秒...")
    
    url = f"{BASE_URL}/api/bazi/analysis"
    
    print(f"\n发送请求时间：{datetime.now().strftime('%H:%M:%S')}")
    start_time = datetime.now()
    
    response = requests.post(url, json=TEST_USER, timeout=120)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n状态码：{response.status_code}")
    print(f"响应时间：{duration:.2f} 秒")
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            data = result['data']
            analysis = data['analysis']
            
            print("\n✓ 八字分析成功！")
            print(f"\n分析内容长度：{len(analysis)} 字符")
            print(f"\n分析内容预览（前500字）：")
            print("-" * 60)
            print(analysis[:500] + "...")
            print("-" * 60)
            
            # 保存完整分析到文件
            filename = f"bazi_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"八字命理分析报告\n")
                f.write(f"="*60 + "\n")
                f.write(f"用户：{TEST_USER['user_id']}\n")
                f.write(f"生辰：{TEST_USER['year']}年{TEST_USER['month']}月{TEST_USER['day']}日 {TEST_USER['hour']}时\n")
                f.write(f"分析时间：{data['timestamp']}\n")
                f.write(f"="*60 + "\n\n")
                f.write(analysis)
            
            print(f"\n完整分析已保存到：{filename}")
            
            return True
        else:
            print(f"\n✗ 八字分析失败：{result.get('message', '未知错误')}")
            return False
    else:
        print(f"\n✗ 请求失败：{response.text}")
        return False


def test_bazi_fortune():
    """测试3：八字流年运势分析"""
    print("\n" + "="*60)
    print("测试3：八字流年运势分析")
    print("="*60)
    print("\n提示：此测试需要调用 Gemini AI，预计耗时 30-45 秒...")
    
    url = f"{BASE_URL}/api/bazi/fortune"
    test_data = {
        **TEST_USER,
        "query_year": 2024,
        "query_month": None  # 全年运势
    }
    
    print(f"\n查询年份：{test_data['query_year']}年全年运势")
    print(f"发送请求时间：{datetime.now().strftime('%H:%M:%S')}")
    start_time = datetime.now()
    
    response = requests.post(url, json=test_data, timeout=120)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n状态码：{response.status_code}")
    print(f"响应时间：{duration:.2f} 秒")
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            data = result['data']
            fortune = data['fortune_analysis']
            
            print("\n✓ 运势分析成功！")
            print(f"\n分析内容长度：{len(fortune)} 字符")
            print(f"\n运势分析预览（前500字）：")
            print("-" * 60)
            print(fortune[:500] + "...")
            print("-" * 60)
            
            # 保存完整分析到文件
            filename = f"bazi_fortune_{test_data['query_year']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"八字流年运势分析报告\n")
                f.write(f"="*60 + "\n")
                f.write(f"用户：{TEST_USER['user_id']}\n")
                f.write(f"生辰：{TEST_USER['year']}年{TEST_USER['month']}月{TEST_USER['day']}日 {TEST_USER['hour']}时\n")
                f.write(f"查询年份：{test_data['query_year']}年\n")
                f.write(f"分析时间：{data['timestamp']}\n")
                f.write(f"="*60 + "\n\n")
                f.write(fortune)
            
            print(f"\n完整运势分析已保存到：{filename}")
            
            return True
        else:
            print(f"\n✗ 运势分析失败：{result.get('message', '未知错误')}")
            return False
    else:
        print(f"\n✗ 请求失败：{response.text}")
        return False


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("Aetheria 八字系统功能测试")
    print("="*60)
    print(f"\n测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API 地址：{BASE_URL}")
    print(f"测试用户：{TEST_USER['user_id']}")
    
    # 检查 API 是否运行
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("\n✗ API 服务未运行，请先启动 api_server.py")
            return
    except:
        print("\n✗ 无法连接到 API 服务，请确保 api_server.py 正在运行")
        return
    
    print("\n✓ API 服务运行正常")
    
    # 运行测试
    results = []
    
    # 测试1：八字排盘计算（快速测试）
    results.append(("八字排盘计算", test_bazi_calculate()))
    
    # 询问是否继续AI测试
    print("\n" + "="*60)
    user_input = input("\n是否继续进行 AI 分析测试？（需要调用 Gemini API，每个测试约 30-45 秒）[y/N]: ")
    
    if user_input.lower() == 'y':
        # 测试2：八字命理分析
        results.append(("八字命理分析", test_bazi_analysis()))
        
        # 测试3：八字流年运势
        results.append(("八字流年运势", test_bazi_fortune()))
    else:
        print("\n跳过 AI 分析测试")
    
    # 测试总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n总计：{passed}/{total} 项测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！八字系统功能正常！")
    else:
        print(f"\n⚠️ {total - passed} 项测试失败，请检查错误信息")


if __name__ == "__main__":
    main()
