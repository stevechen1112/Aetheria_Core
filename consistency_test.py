"""
Aetheria 一致性測試腳本

目標：測試 Gemini 3 Pro 對同一出生資料重複排盤的一致性
方法：呼叫 API 10 次，比對結果與基準答案的相似度

基準答案（來自您之前的 Gemini 3 Pro 對話）：
- 命宮：太陰（戌宮）
- 格局：日月並明、機月同梁
- 官祿宮：天梁化科（寅宮）
- 財帛宮：天機（午宮）
- 夫妻宮：武曲化祿+天相（申宮）
- 性格：斯文、細膩、溫和、有條理
"""

import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

# 載入環境變數
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# ============================================
# 基準答案（您之前的正確 Gemini 對話）
# ============================================

GROUND_TRUTH = {
    "命宮": {
        "宮位": "戌",
        "主星": ["太陰"],
        "keywords": ["太陰", "戌宮", "戌"]
    },
    "格局": {
        "名稱": ["日月並明", "機月同梁"],
        "keywords": ["日月並明", "機月同梁", "日月", "機梁"]
    },
    "官祿宮": {
        "宮位": "寅",
        "主星": ["天梁"],
        "四化": "化科",
        "keywords": ["天梁", "化科", "寅宮", "官祿"]
    },
    "財帛宮": {
        "宮位": "午",
        "主星": ["天機"],
        "keywords": ["天機", "午宮", "財帛"]
    },
    "夫妻宮": {
        "宮位": "申",
        "主星": ["武曲", "天相"],
        "四化": "化祿",
        "keywords": ["武曲", "化祿", "天相", "申宮", "夫妻"]
    },
    "性格特質": {
        "keywords": ["斯文", "細膩", "溫和", "有條理", "書卷", "文昌", "太陰"]
    },
    "錯誤指標": {
        "命宮絕不是": ["破軍", "申宮", "殺破狼"],
        "格局絕不是": ["殺破狼"],
        "性格絕不是": ["破壞", "衝動", "變色龍", "不安"]
    }
}

# ============================================
# 測試參數
# ============================================

BIRTH_INFO = {
    'date': '農曆68年9月23日',
    'time': '23:58',
    'location': '台灣彰化市',
    'gender': '男'
}

TEST_ITERATIONS = 10  # 測試次數
MODEL_NAME = 'gemini-3-pro-preview'
TEMPERATURE = 0.4  # 與正式測試相同

# ============================================
# 提示詞（簡化版，專注於命盤結構）
# ============================================

SYSTEM_INSTRUCTION = """
你是 Aetheria，精通紫微斗數的 AI 命理顧問。

重要原則：
1. 準確性最重要，不可編造星曜
2. 晚子時（23:00-01:00）的判定邏輯要明確說明
3. 必須明確說出命宮位置、主星、格局

輸出風格：結構清晰，先說命盤結構，再說性格。
"""

USER_PROMPT_TEMPLATE = """
請為以下用戶提供紫微斗數命盤分析（專注於命盤結構）：

出生日期：{date}
出生時間：{time}
出生地點：{location}
性別：{gender}

請按以下格式輸出（約800字）：

### 一、命盤基礎結構
1. **時辰判定**：說明 23:58 如何處理（晚子時算當日或隔日）
2. **命宮**：位於哪個宮位？主星是什麼？
3. **核心格局**：屬於什麼格局？（如日月並明、殺破狼等）
4. **關鍵宮位**：
   - 官祿宮（事業）：宮位、主星、四化
   - 財帛宮（財運）：宮位、主星
   - 夫妻宮（感情）：宮位、主星、四化

### 二、性格特質（200字）
用日常語言描述，核心關鍵詞至少5個。

**注意**：必須明確說出宮位（如「戌宮」「申宮」），不可模糊帶過。
"""

# ============================================
# 分析函式
# ============================================

def extract_chart_structure(response_text):
    """
    從 LLM 回應中提取命盤結構
    使用關鍵詞匹配
    """
    
    result = {
        "raw_text": response_text[:500],  # 前500字用於除錯
        "命宮": {"found": False, "content": ""},
        "格局": {"found": False, "content": ""},
        "官祿宮": {"found": False, "content": ""},
        "財帛宮": {"found": False, "content": ""},
        "夫妻宮": {"found": False, "content": ""},
        "性格": {"found": False, "content": ""},
        "錯誤指標": []
    }
    
    text_lower = response_text.lower()
    
    # 檢查錯誤指標
    for wrong_keyword in GROUND_TRUTH["錯誤指標"]["命宮絕不是"]:
        if wrong_keyword in response_text:
            result["錯誤指標"].append(f"命宮錯誤：提到了「{wrong_keyword}」")
    
    for wrong_keyword in GROUND_TRUTH["錯誤指標"]["格局絕不是"]:
        if wrong_keyword in response_text:
            result["錯誤指標"].append(f"格局錯誤：提到了「{wrong_keyword}」")
    
    # 提取命宮
    for keyword in GROUND_TRUTH["命宮"]["keywords"]:
        if keyword in response_text:
            result["命宮"]["found"] = True
            result["命宮"]["content"] += keyword + " "
    
    # 提取格局
    for keyword in GROUND_TRUTH["格局"]["keywords"]:
        if keyword in response_text:
            result["格局"]["found"] = True
            result["格局"]["content"] += keyword + " "
    
    # 提取官祿宮
    for keyword in GROUND_TRUTH["官祿宮"]["keywords"]:
        if keyword in response_text:
            result["官祿宮"]["found"] = True
            result["官祿宮"]["content"] += keyword + " "
    
    # 提取財帛宮
    for keyword in GROUND_TRUTH["財帛宮"]["keywords"]:
        if keyword in response_text:
            result["財帛宮"]["found"] = True
            result["財帛宮"]["content"] += keyword + " "
    
    # 提取夫妻宮
    for keyword in GROUND_TRUTH["夫妻宮"]["keywords"]:
        if keyword in response_text:
            result["夫妻宮"]["found"] = True
            result["夫妻宮"]["content"] += keyword + " "
    
    # 提取性格關鍵詞
    for keyword in GROUND_TRUTH["性格特質"]["keywords"]:
        if keyword in response_text:
            result["性格"]["found"] = True
            result["性格"]["content"] += keyword + " "
    
    return result

def calculate_accuracy(extracted):
    """
    計算準確度分數
    """
    
    scores = {
        "命宮": 0,
        "格局": 0,
        "官祿宮": 0,
        "財帛宮": 0,
        "夫妻宮": 0,
        "性格": 0,
        "錯誤扣分": 0
    }
    
    # 命宮（最重要，40分）
    if extracted["命宮"]["found"] and "太陰" in extracted["命宮"]["content"]:
        if "戌" in extracted["命宮"]["content"]:
            scores["命宮"] = 40  # 完全正確
        else:
            scores["命宮"] = 20  # 星對但宮位不明確
    
    # 格局（20分）
    if extracted["格局"]["found"]:
        if "日月並明" in extracted["格局"]["content"] or "機月同梁" in extracted["格局"]["content"]:
            scores["格局"] = 20
        else:
            scores["格局"] = 5  # 有提到格局但不對
    
    # 官祿宮（15分）
    if extracted["官祿宮"]["found"] and "天梁" in extracted["官祿宮"]["content"]:
        if "化科" in extracted["官祿宮"]["content"]:
            scores["官祿宮"] = 15
        else:
            scores["官祿宮"] = 8
    
    # 財帛宮（10分）
    if extracted["財帛宮"]["found"] and "天機" in extracted["財帛宮"]["content"]:
        scores["財帛宮"] = 10
    
    # 夫妻宮（10分）
    if extracted["夫妻宮"]["found"] and "武曲" in extracted["夫妻宮"]["content"]:
        scores["夫妻宮"] = 10
    
    # 性格（5分）
    if extracted["性格"]["found"]:
        keyword_count = len([k for k in GROUND_TRUTH["性格特質"]["keywords"] 
                           if k in extracted["性格"]["content"]])
        scores["性格"] = min(5, keyword_count)
    
    # 錯誤扣分（最多扣50分）
    scores["錯誤扣分"] = -min(50, len(extracted["錯誤指標"]) * 25)
    
    total = sum(scores.values())
    total = max(0, total)  # 不低於0
    
    return total, scores

# ============================================
# 主測試流程
# ============================================

def run_single_test(iteration):
    """
    執行單次測試
    """
    
    print(f"\n{'='*60}")
    print(f"[TEST] 第 {iteration + 1}/{TEST_ITERATIONS} 次測試")
    print(f"{'='*60}")
    
    try:
        # 建立模型
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        # 組合查詢
        user_prompt = USER_PROMPT_TEMPLATE.format(**BIRTH_INFO)
        
        # 生成回應
        print("[API] 正在呼叫 API...")
        response = model.generate_content(
            user_prompt,
            generation_config=genai.GenerationConfig(
                temperature=TEMPERATURE,
                top_p=0.95,
                top_k=40
                # 移除 max_output_tokens - 會導致 finish_reason=2 bug
            ),
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
        )
        
        # 檢查安全過濾
        print(f"[DEBUG] prompt_feedback: {response.prompt_feedback}")
        
        if not response.candidates:
            print(f"[ERROR] 無候選回應")
            raise Exception("安全過濾器阻止了回應生成")
        
        candidate = response.candidates[0]
        print(f"[DEBUG] finish_reason: {candidate.finish_reason}")
        print(f"[DEBUG] safety_ratings: {candidate.safety_ratings}")
        print(f"[DEBUG] content: {candidate.content if hasattr(candidate, 'content') else 'N/A'}")
        
        if candidate.finish_reason != 1:  # 1 = STOP (正常完成)
            raise Exception(f"回應未正常完成，finish_reason = {candidate.finish_reason}")
        
        result_text = response.text
        print(f"[OK] 回應長度：{len(result_text)} 字")
        
        # 提取結構
        extracted = extract_chart_structure(result_text)
        
        # 計算準確度
        accuracy, scores = calculate_accuracy(extracted)
        
        # 顯示結果
        print(f"\n[ANALYSIS] 結構分析：")
        print(f"  命宮：{'[OK] ' if extracted['命宮']['found'] else '[X] '}{extracted['命宮']['content']}")
        print(f"  格局：{'[OK] ' if extracted['格局']['found'] else '[X] '}{extracted['格局']['content']}")
        print(f"  官祿宮：{'[OK] ' if extracted['官祿宮']['found'] else '[X] '}{extracted['官祿宮']['content']}")
        print(f"  財帛宮：{'[OK] ' if extracted['財帛宮']['found'] else '[X] '}{extracted['財帛宮']['content']}")
        print(f"  夫妻宮：{'[OK] ' if extracted['夫妻宮']['found'] else '[X] '}{extracted['夫妻宮']['content']}")
        
        if extracted['錯誤指標']:
            print(f"\n[WARNING] 錯誤指標：")
            for error in extracted['錯誤指標']:
                print(f"    - {error}")
        
        print(f"\n[SCORE] 準確度評分：{accuracy}/100")
        print(f"   詳細分數：{scores}")
        
        return {
            'iteration': iteration + 1,
            'success': True,
            'accuracy': accuracy,
            'scores': scores,
            'extracted': extracted,
            'full_text': result_text
        }
        
    except Exception as e:
        print(f"[ERROR] 測試失敗：{e}")
        return {
            'iteration': iteration + 1,
            'success': False,
            'error': str(e)
        }

def run_consistency_test():
    """
    執行完整一致性測試
    """
    
    print("\n" + "="*60)
    print(" Aetheria 一致性測試")
    print("="*60)
    print(f"測試對象：{BIRTH_INFO['date']} {BIRTH_INFO['time']}")
    print(f"測試次數：{TEST_ITERATIONS}")
    print(f"使用模型：{MODEL_NAME}")
    print(f"溫度參數：{TEMPERATURE}")
    print("="*60)
    
    results = []
    
    # 執行測試
    for i in range(TEST_ITERATIONS):
        result = run_single_test(i)
        results.append(result)
    
    # 統計分析
    print("\n\n" + "="*60)
    print("[STATS] 統計分析")
    print("="*60)
    
    successful_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]
    
    print(f"\n成功次數：{len(successful_tests)}/{TEST_ITERATIONS}")
    print(f"失敗次數：{len(failed_tests)}/{TEST_ITERATIONS}")
    
    if successful_tests:
        accuracies = [r['accuracy'] for r in successful_tests]
        avg_accuracy = sum(accuracies) / len(accuracies)
        min_accuracy = min(accuracies)
        max_accuracy = max(accuracies)
        
        print(f"\n📈 準確度統計：")
        print(f"  平均分數：{avg_accuracy:.1f}/100")
        print(f"  最高分數：{max_accuracy}/100")
        print(f"  最低分數：{min_accuracy}/100")
        print(f"  標準差：{calculate_std_dev(accuracies):.1f}")
        
        # 一致性判定
        print(f"\n🎯 一致性評估：")
        
        if avg_accuracy >= 90:
            consistency = "非常高 [OK]"
            recommendation = "LLM 非常可靠，可以直接使用選項 A（純 LLM 定盤）"
        elif avg_accuracy >= 70:
            consistency = "中等 ⚠️"
            recommendation = "LLM 部分可靠，建議選項 A + 確定性驗證（混合方案）"
        else:
            consistency = "低 ❌"
            recommendation = "LLM 不夠可靠，建議使用確定性系統排盤 + LLM 詮釋"
        
        print(f"  一致性等級：{consistency}")
        print(f"  建議方案：{recommendation}")
        
        # 具體問題分析
        print(f"\n🔍 詳細分析：")
        
        # 統計各項的正確率
        fields = ["命宮", "格局", "官祿宮", "財帛宮", "夫妻宮"]
        for field in fields:
            correct_count = sum(1 for r in successful_tests if r['extracted'][field]['found'])
            rate = correct_count / len(successful_tests) * 100
            status = "✅" if rate >= 80 else "⚠️" if rate >= 50 else "❌"
            print(f"  {field}：{status} {rate:.0f}% ({correct_count}/{len(successful_tests)})")
        
        # 檢查是否有嚴重錯誤
        error_count = sum(1 for r in successful_tests if r['extracted']['錯誤指標'])
        if error_count > 0:
            print(f"\n⚠️  警告：{error_count}/{len(successful_tests)} 次出現嚴重錯誤（如命宮錯誤）")
    
    # 儲存結果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"consistency_test_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'test_info': {
                'birth_info': BIRTH_INFO,
                'model': MODEL_NAME,
                'temperature': TEMPERATURE,
                'iterations': TEST_ITERATIONS,
                'timestamp': timestamp
            },
            'ground_truth': GROUND_TRUTH,
            'results': results,
            'statistics': {
                'avg_accuracy': avg_accuracy if successful_tests else 0,
                'consistency_level': consistency if successful_tests else "未知"
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 完整結果已儲存到：{filename}")
    
    # 生成報告
    generate_report(results, filename)
    
    return results

def calculate_std_dev(numbers):
    """計算標準差"""
    if not numbers:
        return 0
    mean = sum(numbers) / len(numbers)
    variance = sum((x - mean) ** 2 for x in numbers) / len(numbers)
    return variance ** 0.5

def generate_report(results, json_filename):
    """生成測試報告"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"consistency_report_{timestamp}.txt"
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("Aetheria 一致性測試報告\n")
        f.write("="*60 + "\n\n")
        
        f.write(f"測試時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"測試對象：{BIRTH_INFO['date']} {BIRTH_INFO['time']} {BIRTH_INFO['location']} {BIRTH_INFO['gender']}\n")
        f.write(f"測試次數：{TEST_ITERATIONS}\n")
        f.write(f"使用模型：{MODEL_NAME}\n")
        f.write(f"溫度參數：{TEMPERATURE}\n\n")
        
        successful = [r for r in results if r['success']]
        
        if successful:
            accuracies = [r['accuracy'] for r in successful]
            avg = sum(accuracies) / len(accuracies)
            
            f.write("="*60 + "\n")
            f.write("統計結果\n")
            f.write("="*60 + "\n\n")
            f.write(f"平均準確度：{avg:.1f}/100\n")
            f.write(f"最高分數：{max(accuracies)}/100\n")
            f.write(f"最低分數：{min(accuracies)}/100\n")
            f.write(f"標準差：{calculate_std_dev(accuracies):.1f}\n\n")
            
            f.write("="*60 + "\n")
            f.write("每次測試詳情\n")
            f.write("="*60 + "\n\n")
            
            for r in successful:
                f.write(f"第 {r['iteration']} 次測試：{r['accuracy']}/100\n")
                f.write(f"  命宮：{r['extracted']['命宮']['content']}\n")
                f.write(f"  格局：{r['extracted']['格局']['content']}\n")
                if r['extracted']['錯誤指標']:
                    f.write(f"  錯誤：{', '.join(r['extracted']['錯誤指標'])}\n")
                f.write("\n")
        
        f.write(f"\n完整數據請查看：{json_filename}\n")
    
    print(f"[SAVE] 測試報告已儲存到：{report_filename}")

# ============================================
# 主程式入口
# ============================================

if __name__ == "__main__":
    run_consistency_test()
