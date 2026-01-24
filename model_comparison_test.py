"""
Gemini 模型對比測試
測試 gemini-3-pro vs gemini-3-flash-preview 的品質差異
"""

import os
import json
import time
from dotenv import load_dotenv
import google.generativeai as genai
from chart_extractor import ChartExtractor
from fortune_teller import FortuneTeller

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# 測試用戶數據
TEST_USER = {
    "user_id": "test_user_001",
    "birth_date": "農曆68年9月23日 23:58",
    "birth_place": "台灣彰化市",
    "gender": "男"
}

# 兩個模型配置
MODELS = {
    "Gemini 3 Pro": "gemini-3-pro-preview",
    "Gemini 3 Flash": "gemini-3-flash-preview"
}

def generate_chart_analysis(model_name, user_data):
    """使用指定模型生成命盤分析"""
    prompt = f"""請根據以下資訊，進行完整的紫微斗數命盤排盤與分析：

出生資訊：
- 出生日期：{user_data['birth_date']}
- 出生地點：{user_data['birth_place']}
- 性別：{user_data['gender']}

請按照以下步驟進行：

1. 【排盤計算】
   - 確定命宮位置（根據出生時辰與月份）
   - 安排十二宮位（命宮、兄弟、夫妻、子女、財帛、疾厄、遷移、交友、官祿、田宅、福德、父母）
   - 安置主星與輔星（紫微、天機、太陽、武曲、天同、廉貞、天府、太陰、貪狼、巨門、天相、天梁、七殺、破軍、文昌、文曲、左輔、右弼、天魁、天鉞、祿存、天馬等）
   - 標註四化（化祿、化權、化科、化忌）

2. 【格局判定】
   識別命盤中的重要格局（如：紫府同宮、日月並明、巨日同宮、機梁加會等）

3. 【個性分析】
   根據命宮主星與格局，分析性格特質、思維模式、行為傾向

4. 【事業運勢】
   分析官祿宮，評估適合的職業方向、事業發展潛力

5. 【財富運勢】
   分析財帛宮，評估財運狀況、理財能力、財富累積方式

6. 【感情婚姻】
   分析夫妻宮，評估感情態度、婚姻運勢、配偶特質

7. 【健康狀況】
   分析疾厄宮，提示需要注意的健康問題

8. 【人際關係】
   分析交友宮與兄弟宮，評估人際互動模式

請以專業、溫暖且精準的語氣進行分析，字數約 2000 字。"""

    model = genai.GenerativeModel(model_name)
    
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
    }
    
    start_time = time.time()
    response = model.generate_content(prompt, generation_config=generation_config)
    duration = time.time() - start_time
    
    return {
        "text": response.text,
        "duration": duration,
        "usage": response.usage_metadata if hasattr(response, 'usage_metadata') else None
    }

def generate_fortune_analysis(model_name, user_data, chart_structure):
    """使用指定模型生成流年分析"""
    # 從命盤結構中提取命宮地支
    ming_gong_info = chart_structure.get('命宮', {})
    ming_gong_branch = ming_gong_info.get('位置', '戌')  # 默認用戌宮
    
    # 計算流年資訊
    fortune_teller = FortuneTeller(1979, 9, 23, '男', ming_gong_branch)
    da_xian = fortune_teller.calculate_da_xian(2026)
    liu_nian = fortune_teller.calculate_liu_nian(2026)
    
    prompt = f"""你是 Aetheria，一個專精於紫微斗數的 AI 命理顧問。請根據以下資訊進行流年運勢分析。

【用戶資料】
- 出生：{user_data['birth_date']}
- 性別：{user_data['gender']}
- 現年：{fortune_teller.calculate_current_age(2026)} 歲

【命盤結構】
{json.dumps(chart_structure, ensure_ascii=False, indent=2)}

【流年資訊】
- 大限：第{da_xian['da_xian_number']}大限 ({da_xian['age_range'][0]}-{da_xian['age_range'][1]}歲)
- 大限宮位：{da_xian['palace_name']} ({da_xian['palace_branch']})
- 流年：{liu_nian['year']}年 {liu_nian['gan_zhi']}
- 流年宮位：{liu_nian['palace_name']} ({liu_nian['palace_branch']})

請分析 2026 年的整體運勢，包含：
1. 大限與流年概況
2. 事業運勢
3. 財運狀況
4. 感情婚姻
5. 健康提醒
6. 趨吉避凶建議

分析字數約 1500 字，語氣溫暖專業。"""

    model = genai.GenerativeModel(model_name)
    
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
    }
    
    start_time = time.time()
    response = model.generate_content(prompt, generation_config=generation_config)
    duration = time.time() - start_time
    
    return {
        "text": response.text,
        "duration": duration,
        "usage": response.usage_metadata if hasattr(response, 'usage_metadata') else None
    }

def extract_and_validate_structure(text):
    """提取並驗證命盤結構"""
    extractor = ChartExtractor()
    structure = extractor.extract_full_structure(text)
    
    # 驗證關鍵欄位
    validation = {
        "has_ming_gong": bool(structure.get("命宮")),
        "has_main_stars": bool(structure.get("主星") or structure.get("命宮", {}).get("主星")),
        "has_patterns": bool(structure.get("格局")),
        "palace_count": len([k for k in structure.keys() if "宮" in k]),
    }
    
    return structure, validation

def compare_results(pro_result, flash_result):
    """對比兩個模型的結果"""
    print("\n" + "="*60)
    print("【對比分析】")
    print("="*60)
    
    # 1. 速度對比
    print(f"\n1. 生成速度:")
    print(f"   Gemini 3 Pro:   {pro_result['duration']:.2f} 秒")
    print(f"   Gemini 3 Flash: {flash_result['duration']:.2f} 秒")
    speedup = pro_result['duration'] / flash_result['duration']
    print(f"   速度提升: {speedup:.2f}x")
    
    # 2. Token 使用量對比（如果有）
    if pro_result.get('usage') and flash_result.get('usage'):
        print(f"\n2. Token 使用量:")
        print(f"   Gemini 3 Pro:")
        print(f"      輸入: {pro_result['usage'].prompt_token_count}")
        print(f"      輸出: {pro_result['usage'].candidates_token_count}")
        print(f"      總計: {pro_result['usage'].total_token_count}")
        print(f"   Gemini 3 Flash:")
        print(f"      輸入: {flash_result['usage'].prompt_token_count}")
        print(f"      輸出: {flash_result['usage'].candidates_token_count}")
        print(f"      總計: {flash_result['usage'].total_token_count}")
    
    # 3. 內容長度對比
    print(f"\n3. 內容長度:")
    print(f"   Gemini 3 Pro:   {len(pro_result['text'])} 字")
    print(f"   Gemini 3 Flash: {len(flash_result['text'])} 字")
    
    # 4. 結構驗證對比
    if 'structure' in pro_result and 'structure' in flash_result:
        print(f"\n4. 命盤結構完整性:")
        print(f"   Gemini 3 Pro:")
        print(f"      命宮: {'✓' if pro_result['validation']['has_ming_gong'] else '✗'}")
        print(f"      主星: {'✓' if pro_result['validation']['has_main_stars'] else '✗'}")
        print(f"      格局: {'✓' if pro_result['validation']['has_patterns'] else '✗'}")
        print(f"      宮位數: {pro_result['validation']['palace_count']}")
        print(f"   Gemini 3 Flash:")
        print(f"      命宮: {'✓' if flash_result['validation']['has_ming_gong'] else '✗'}")
        print(f"      主星: {'✓' if flash_result['validation']['has_main_stars'] else '✗'}")
        print(f"      格局: {'✓' if flash_result['validation']['has_patterns'] else '✗'}")
        print(f"      宮位數: {flash_result['validation']['palace_count']}")

def print_sample_output(model_name, text, max_length=800):
    """顯示輸出樣本"""
    print(f"\n【{model_name} 輸出樣本】")
    print("-" * 60)
    sample = text[:max_length]
    if len(text) > max_length:
        sample += "\n... (後續內容省略) ..."
    print(sample)
    print("-" * 60)

def main():
    print("="*60)
    print("Aetheria 模型對比測試")
    print("Gemini 3 Pro vs Gemini 3 Flash Preview")
    print("="*60)
    
    # 測試 1: 基礎命盤分析
    print("\n\n【測試 1】基礎命盤排盤與分析")
    print("-" * 60)
    
    print("\n正在測試 Gemini 3 Pro...")
    pro_chart = generate_chart_analysis(MODELS["Gemini 3 Pro"], TEST_USER)
    pro_structure, pro_validation = extract_and_validate_structure(pro_chart['text'])
    pro_chart['structure'] = pro_structure
    pro_chart['validation'] = pro_validation
    print("✓ 完成")
    
    print("\n正在測試 Gemini 3 Flash...")
    flash_chart = generate_chart_analysis(MODELS["Gemini 3 Flash"], TEST_USER)
    flash_structure, flash_validation = extract_and_validate_structure(flash_chart['text'])
    flash_chart['structure'] = flash_structure
    flash_chart['validation'] = flash_validation
    print("✓ 完成")
    
    # 對比結果
    compare_results(pro_chart, flash_chart)
    
    # 顯示輸出樣本
    print_sample_output("Gemini 3 Pro", pro_chart['text'])
    print_sample_output("Gemini 3 Flash", flash_chart['text'])
    
    # 測試 2: 流年運勢分析
    print("\n\n【測試 2】流年運勢分析")
    print("-" * 60)
    
    # 使用 Pro 的命盤結構作為基準
    if pro_structure:
        print("\n正在測試 Gemini 3 Pro...")
        pro_fortune = generate_fortune_analysis(MODELS["Gemini 3 Pro"], TEST_USER, pro_structure)
        print("✓ 完成")
        
        print("\n正在測試 Gemini 3 Flash...")
        flash_fortune = generate_fortune_analysis(MODELS["Gemini 3 Flash"], TEST_USER, pro_structure)
        print("✓ 完成")
        
        # 對比結果
        compare_results(pro_fortune, flash_fortune)
        
        # 顯示輸出樣本
        print_sample_output("Gemini 3 Pro", pro_fortune['text'])
        print_sample_output("Gemini 3 Flash", flash_fortune['text'])
    
    # 總結建議
    print("\n\n" + "="*60)
    print("【總結與建議】")
    print("="*60)
    
    total_speedup = (pro_chart['duration'] + pro_fortune['duration']) / \
                    (flash_chart['duration'] + flash_fortune['duration'])
    
    print(f"\n1. 整體速度提升: {total_speedup:.2f}x")
    
    print("\n2. 品質評估:")
    pro_quality = sum([
        pro_validation['has_ming_gong'],
        pro_validation['has_main_stars'],
        pro_validation['has_patterns'],
        pro_validation['palace_count'] >= 10
    ])
    flash_quality = sum([
        flash_validation['has_ming_gong'],
        flash_validation['has_main_stars'],
        flash_validation['has_patterns'],
        flash_validation['palace_count'] >= 10
    ])
    
    print(f"   Gemini 3 Pro 結構完整度:   {pro_quality}/4")
    print(f"   Gemini 3 Flash 結構完整度: {flash_quality}/4")
    
    print("\n3. 建議:")
    if flash_quality >= pro_quality and total_speedup > 1.5:
        print("   ✓ Gemini 3 Flash 品質相當且速度明顯更快，建議使用")
    elif flash_quality >= pro_quality - 1:
        print("   → Gemini 3 Flash 品質略遜但可接受，視成本考量決定")
    else:
        print("   ✗ Gemini 3 Flash 品質明顯不足，建議繼續使用 Pro")
    
    print("\n4. 使用場景建議:")
    print("   - 基礎分析、日常諮詢: Gemini 3 Flash")
    print("   - 詳細排盤、定盤驗證: Gemini 3 Pro")
    print("   - 複雜分析、合盤擇日: Gemini 3 Pro")

if __name__ == "__main__":
    main()
