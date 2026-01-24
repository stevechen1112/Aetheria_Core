"""
Aetheria 銝?湔扳葫閰西??

?格?嚗葫閰?Gemini 3 Pro 撠?銝?箇?鞈???????湔?
?寞?嚗??API 10 甈∴?瘥?蝯??皞?獢??訾撮摨?

?箸?蝑?嚗??芣銋???Gemini 3 Pro 撠店嚗?
- ?賢悅嚗云?堆??悅嚗?
- ?澆?嚗?蒂????璇?
- 摰正摰殷?憭拇???嚗?摰殷?
- 鞎∪?摰殷?憭拇?嚗?摰殷?
- 憭怠氖摰殷?甇行?正+憭拍嚗摰殷?
- ?扳嚗?敦?押澈??璇?
"""

import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

# 頛?啣?霈
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# ============================================
# ?箸?蝑?嚗銋??迤蝣?Gemini 撠店嚗?
# ============================================

GROUND_TRUTH = {
    "?賢悅": {
        "摰桐?": "??,
        "銝餅?": ["憭芷"],
        "keywords": ["憭芷", "?悅", "??]
    },
    "?澆?": {
        "?迂": ["?交?銝行?", "璈???"],
        "keywords": ["?交?銝行?", "璈???", "?交?", "璈?"]
    },
    "摰正摰?: {
        "摰桐?": "撖?,
        "銝餅?": ["憭拇?"],
        "??": "??",
        "keywords": ["憭拇?", "??", "撖悅", "摰正"]
    },
    "鞎∪?摰?: {
        "摰桐?": "??,
        "銝餅?": ["憭拇?"],
        "keywords": ["憭拇?", "?悅", "鞎∪?"]
    },
    "憭怠氖摰?: {
        "摰桐?": "??,
        "銝餅?": ["甇行", "憭拍"],
        "??": "?正",
        "keywords": ["甇行", "?正", "憭拍", "?喳悅", "憭怠氖"]
    },
    "?扳?寡釭": {
        "keywords": ["?舀?", "蝝啗", "皞怠?", "????, "?詨", "??", "憭芷"]
    },
    "?航炊??": {
        "?賢悅蝯???: ["?渲?", "?喳悅", "畾箇??],
        "?澆?蝯???: ["畾箇??],
        "?扳蝯???: ["?游?", "銵?", "霈樴?, "銝?"]
    }
}

# ============================================
# 皜祈岫?
# ============================================

BIRTH_INFO = {
    'date': '颲脫?68撟???3??,
    'time': '23:58',
    'location': '?啁敶啣?撣?,
    'gender': '??
}

TEST_ITERATIONS = 10  # 皜祈岫甈⊥
MODEL_NAME = 'gemini-3-pro-preview'
TEMPERATURE = 0.4  # ?迤撘葫閰衣??

# ============================================
# ?內閰?蝪∪???撠釣?澆?斤?瑽?
# ============================================

SYSTEM_INSTRUCTION = """
雿 Aetheria嚗移?換敺格??貊? AI ?賜?憿批???

????嚗?
1. 皞Ⅱ?扳???嚗??舐楊????
2. ????23:00-01:00嚗??文??摩閬?蝣箄牧??
3. 敹??Ⅱ隤芸?賢悅雿蔭?蜓?撅

頛詨憸冽嚗?瑽??堆??牧?賜蝯?嚗?隤芣扳??
"""

USER_PROMPT_TEMPLATE = """
隢隞乩??冽??蝝怠凝??賜??嚗?瘜冽?賜蝯?嚗?

?箇??交?嚗date}
?箇???嚗time}
?箇??圈?嚗location}
?批嚗gender}

隢?隞乩??澆?頛詨嚗?800摮?嚗?

### 銝??文蝷?瑽?
1. **?劓?文?**嚗牧??23:58 憒???嚗?摮?蝞?交??嚗?
2. **?賢悅**嚗??澆?悅雿?銝餅??臭?暻潘?
3. **?詨??澆?**嚗惇?潔?暻潭撅嚗?憒?蒂?捏?渡蝑?
4. **?摰桐?**嚗?
   - 摰正摰殷?鈭平嚗?摰桐??蜓????
   - 鞎∪?摰殷?鞎⊿?嚗?摰桐??蜓??
   - 憭怠氖摰殷???嚗?摰桐??蜓????

### 鈭扳?寡釭嚗?00摮?
?冽撣貉?閮?膩嚗敹??菔??喳?5??

**瘜冽?**嚗???蝣箄牧?箏悅雿?憒?摰柴摰柴?嚗??舀芋蝟葆??
"""

# ============================================
# ???賢?
# ============================================

def extract_chart_structure(response_text):
    """
    敺?LLM ??銝剜???斤?瑽?
    雿輻?閰??
    """
    
    result = {
        "raw_text": response_text[:500],  # ??00摮?潮??
        "?賢悅": {"found": False, "content": ""},
        "?澆?": {"found": False, "content": ""},
        "摰正摰?: {"found": False, "content": ""},
        "鞎∪?摰?: {"found": False, "content": ""},
        "憭怠氖摰?: {"found": False, "content": ""},
        "?扳": {"found": False, "content": ""},
        "?航炊??": []
    }
    
    text_lower = response_text.lower()
    
    # 瑼Ｘ?航炊??
    for wrong_keyword in GROUND_TRUTH["?航炊??"]["?賢悅蝯???]:
        if wrong_keyword in response_text:
            result["?航炊??"].append(f"?賢悅?航炊嚗??唬??wrong_keyword}??)
    
    for wrong_keyword in GROUND_TRUTH["?航炊??"]["?澆?蝯???]:
        if wrong_keyword in response_text:
            result["?航炊??"].append(f"?澆??航炊嚗??唬??wrong_keyword}??)
    
    # ???賢悅
    for keyword in GROUND_TRUTH["?賢悅"]["keywords"]:
        if keyword in response_text:
            result["?賢悅"]["found"] = True
            result["?賢悅"]["content"] += keyword + " "
    
    # ???澆?
    for keyword in GROUND_TRUTH["?澆?"]["keywords"]:
        if keyword in response_text:
            result["?澆?"]["found"] = True
            result["?澆?"]["content"] += keyword + " "
    
    # ??摰正摰?
    for keyword in GROUND_TRUTH["摰正摰?]["keywords"]:
        if keyword in response_text:
            result["摰正摰?]["found"] = True
            result["摰正摰?]["content"] += keyword + " "
    
    # ??鞎∪?摰?
    for keyword in GROUND_TRUTH["鞎∪?摰?]["keywords"]:
        if keyword in response_text:
            result["鞎∪?摰?]["found"] = True
            result["鞎∪?摰?]["content"] += keyword + " "
    
    # ??憭怠氖摰?
    for keyword in GROUND_TRUTH["憭怠氖摰?]["keywords"]:
        if keyword in response_text:
            result["憭怠氖摰?]["found"] = True
            result["憭怠氖摰?]["content"] += keyword + " "
    
    # ???扳?閰?
    for keyword in GROUND_TRUTH["?扳?寡釭"]["keywords"]:
        if keyword in response_text:
            result["?扳"]["found"] = True
            result["?扳"]["content"] += keyword + " "
    
    return result

def calculate_accuracy(extracted):
    """
    閮?皞Ⅱ摨血???
    """
    
    scores = {
        "?賢悅": 0,
        "?澆?": 0,
        "摰正摰?: 0,
        "鞎∪?摰?: 0,
        "憭怠氖摰?: 0,
        "?扳": 0,
        "?航炊???": 0
    }
    
    # ?賢悅嚗???嚗?0??
    if extracted["?賢悅"]["found"] and "憭芷" in extracted["?賢悅"]["content"]:
        if "?? in extracted["?賢悅"]["content"]:
            scores["?賢悅"] = 40  # 摰甇?Ⅱ
        else:
            scores["?賢悅"] = 20  # ??雿悅雿??Ⅱ
    
    # ?澆?嚗?0??
    if extracted["?澆?"]["found"]:
        if "?交?銝行?" in extracted["?澆?"]["content"] or "璈???" in extracted["?澆?"]["content"]:
            scores["?澆?"] = 20
        else:
            scores["?澆?"] = 5  # ???唳撅雿?撠?
    
    # 摰正摰殷?15??
    if extracted["摰正摰?]["found"] and "憭拇?" in extracted["摰正摰?]["content"]:
        if "??" in extracted["摰正摰?]["content"]:
            scores["摰正摰?] = 15
        else:
            scores["摰正摰?] = 8
    
    # 鞎∪?摰殷?10??
    if extracted["鞎∪?摰?]["found"] and "憭拇?" in extracted["鞎∪?摰?]["content"]:
        scores["鞎∪?摰?] = 10
    
    # 憭怠氖摰殷?10??
    if extracted["憭怠氖摰?]["found"] and "甇行" in extracted["憭怠氖摰?]["content"]:
        scores["憭怠氖摰?] = 10
    
    # ?扳嚗???
    if extracted["?扳"]["found"]:
        keyword_count = len([k for k in GROUND_TRUTH["?扳?寡釭"]["keywords"] 
                           if k in extracted["?扳"]["content"]])
        scores["?扳"] = min(5, keyword_count)
    
    # ?航炊???嚗?憭50??
    scores["?航炊???"] = -min(50, len(extracted["?航炊??"]) * 25)
    
    total = sum(scores.values())
    total = max(0, total)  # 銝???
    
    return total, scores

# ============================================
# 銝餅葫閰行?蝔?
# ============================================

def run_single_test(iteration):
    """
    ?瑁??格活皜祈岫
    """
    
    print(f"\n{'='*60}")
    print(f"?妒 蝚?{iteration + 1}/{TEST_ITERATIONS} 甈⊥葫閰?)
    print(f"{'='*60}")
    
    try:
        # 撱箇?璅∪?
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        # 蝯??亥岷
        user_prompt = USER_PROMPT_TEMPLATE.format(**BIRTH_INFO)
        
        # ????
        print("??甇??澆 API...")
        response = model.generate_content(
            user_prompt,
            generation_config=genai.GenerationConfig(
                temperature=TEMPERATURE,
                top_p=0.95,
                top_k=40,
                max_output_tokens=2048,  # 蝪∪???銝?閬云??
            ),
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
        )
        
        # 瑼Ｘ摰?蕪
        if not response.candidates:
            print(f"???∪??")
            print(f"prompt_feedback: {response.prompt_feedback}")
            raise Exception("摰?蕪?券甇Ｖ?????")
        
        candidate = response.candidates[0]
        print(f"finish_reason: {candidate.finish_reason}")
        print(f"safety_ratings: {candidate.safety_ratings}")
        
        if candidate.finish_reason != 1:  # 1 = STOP (甇?虜摰?)
            raise Exception(f"???芣迤撣詨???finish_reason = {candidate.finish_reason}")
        
        result_text = response.text
        print(f"?????瑕漲嚗len(result_text)} 摮?)
        
        # ??蝯?
        extracted = extract_chart_structure(result_text)
        
        # 閮?皞Ⅱ摨?
        accuracy, scores = calculate_accuracy(extracted)
        
        # 憿舐內蝯?
        print(f"\n?? 蝯???嚗?)
        print(f"  ?賢悅嚗'??' if extracted['?賢悅']['found'] else '??'}{extracted['?賢悅']['content']}")
        print(f"  ?澆?嚗'??' if extracted['?澆?']['found'] else '??'}{extracted['?澆?']['content']}")
        print(f"  摰正摰殷?{'??' if extracted['摰正摰?]['found'] else '??'}{extracted['摰正摰?]['content']}")
        print(f"  鞎∪?摰殷?{'??' if extracted['鞎∪?摰?]['found'] else '??'}{extracted['鞎∪?摰?]['content']}")
        print(f"  憭怠氖摰殷?{'??' if extracted['憭怠氖摰?]['found'] else '??'}{extracted['憭怠氖摰?]['content']}")
        
        if extracted['?航炊??']:
            print(f"\n??  ?航炊??嚗?)
            for error in extracted['?航炊??']:
                print(f"    - {error}")
        
        print(f"\n? 皞Ⅱ摨西???{accuracy}/100")
        print(f"   閰喟敦?嚗scores}")
        
        return {
            'iteration': iteration + 1,
            'success': True,
            'accuracy': accuracy,
            'scores': scores,
            'extracted': extracted,
            'full_text': result_text
        }
        
    except Exception as e:
        print(f"??皜祈岫憭望?嚗e}")
        return {
            'iteration': iteration + 1,
            'success': False,
            'error': str(e)
        }

def run_consistency_test():
    """
    ?瑁?摰銝?湔扳葫閰?
    """
    
    print("\n" + "="*60)
    print("? Aetheria 銝?湔扳葫閰?)
    print("="*60)
    print(f"皜祈岫撠情嚗BIRTH_INFO['date']} {BIRTH_INFO['time']}")
    print(f"皜祈岫甈⊥嚗TEST_ITERATIONS}")
    print(f"雿輻璅∪?嚗MODEL_NAME}")
    print(f"皞怠漲?嚗TEMPERATURE}")
    print("="*60)
    
    results = []
    
    # ?瑁?皜祈岫
    for i in range(TEST_ITERATIONS):
        result = run_single_test(i)
        results.append(result)
    
    # 蝯梯???
    print("\n\n" + "="*60)
    print("?? 蝯梯???")
    print("="*60)
    
    successful_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]
    
    print(f"\n??甈⊥嚗len(successful_tests)}/{TEST_ITERATIONS}")
    print(f"憭望?甈⊥嚗len(failed_tests)}/{TEST_ITERATIONS}")
    
    if successful_tests:
        accuracies = [r['accuracy'] for r in successful_tests]
        avg_accuracy = sum(accuracies) / len(accuracies)
        min_accuracy = min(accuracies)
        max_accuracy = max(accuracies)
        
        print(f"\n?? 皞Ⅱ摨衣絞閮?")
        print(f"  撟喳??嚗avg_accuracy:.1f}/100")
        print(f"  ?擃??賂?{max_accuracy}/100")
        print(f"  ?雿??賂?{min_accuracy}/100")
        print(f"  璅?撌殷?{calculate_std_dev(accuracies):.1f}")
        
        # 銝?湔批摰?
        print(f"\n? 銝?湔扯?隡堆?")
        
        if avg_accuracy >= 90:
            consistency = "?虜擃???
            recommendation = "LLM ?虜?舫?嚗隞亦?乩蝙?券??A嚗? LLM 摰嚗?
        elif avg_accuracy >= 70:
            consistency = "銝剔? ??"
            recommendation = "LLM ?典??舫?嚗遣霅圈??A + 蝣箏??折?霅?瘛瑕??寞?嚗?
        else:
            consistency = "雿???
            recommendation = "LLM 銝??舫?嚗遣霅唬蝙?函Ⅱ摰抒頂蝯望???+ LLM 閰桅?"
        
        print(f"  銝?湔抒?蝝?{consistency}")
        print(f"  撱箄降?寞?嚗recommendation}")
        
        # ?琿?????
        print(f"\n?? 閰喟敦??嚗?)
        
        # 蝯梯????迤蝣箇?
        fields = ["?賢悅", "?澆?", "摰正摰?, "鞎∪?摰?, "憭怠氖摰?]
        for field in fields:
            correct_count = sum(1 for r in successful_tests if r['extracted'][field]['found'])
            rate = correct_count / len(successful_tests) * 100
            status = "?? if rate >= 80 else "??" if rate >= 50 else "??
            print(f"  {field}嚗status} {rate:.0f}% ({correct_count}/{len(successful_tests)})")
        
        # 瑼Ｘ?臬??隤?
        error_count = sum(1 for r in successful_tests if r['extracted']['?航炊??'])
        if error_count > 0:
            print(f"\n??  霅血?嚗error_count}/{len(successful_tests)} 甈∪?曉?隤歹?憒摰桅隤歹?")
    
    # ?脣?蝯?
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
                'consistency_level': consistency if successful_tests else "?芰"
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n? 摰蝯?撌脣摮嚗filename}")
    
    # ???勗?
    generate_report(results, filename)
    
    return results

def calculate_std_dev(numbers):
    """閮?璅?撌?""
    if not numbers:
        return 0
    mean = sum(numbers) / len(numbers)
    variance = sum((x - mean) ** 2 for x in numbers) / len(numbers)
    return variance ** 0.5

def generate_report(results, json_filename):
    """??皜祈岫?勗?"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"consistency_report_{timestamp}.txt"
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("Aetheria 銝?湔扳葫閰血?n")
        f.write("="*60 + "\n\n")
        
        f.write(f"皜祈岫??嚗datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"皜祈岫撠情嚗BIRTH_INFO['date']} {BIRTH_INFO['time']} {BIRTH_INFO['location']} {BIRTH_INFO['gender']}\n")
        f.write(f"皜祈岫甈⊥嚗TEST_ITERATIONS}\n")
        f.write(f"雿輻璅∪?嚗MODEL_NAME}\n")
        f.write(f"皞怠漲?嚗TEMPERATURE}\n\n")
        
        successful = [r for r in results if r['success']]
        
        if successful:
            accuracies = [r['accuracy'] for r in successful]
            avg = sum(accuracies) / len(accuracies)
            
            f.write("="*60 + "\n")
            f.write("蝯梯?蝯?\n")
            f.write("="*60 + "\n\n")
            f.write(f"撟喳?皞Ⅱ摨佗?{avg:.1f}/100\n")
            f.write(f"?擃??賂?{max(accuracies)}/100\n")
            f.write(f"?雿??賂?{min(accuracies)}/100\n")
            f.write(f"璅?撌殷?{calculate_std_dev(accuracies):.1f}\n\n")
            
            f.write("="*60 + "\n")
            f.write("瘥活皜祈岫閰單?\n")
            f.write("="*60 + "\n\n")
            
            for r in successful:
                f.write(f"蝚?{r['iteration']} 甈⊥葫閰佗?{r['accuracy']}/100\n")
                f.write(f"  ?賢悅嚗r['extracted']['?賢悅']['content']}\n")
                f.write(f"  ?澆?嚗r['extracted']['?澆?']['content']}\n")
                if r['extracted']['?航炊??']:
                    f.write(f"  ?航炊嚗', '.join(r['extracted']['?航炊??'])}\n")
                f.write("\n")
        
        f.write(f"\n摰?豢?隢??{json_filename}\n")
    
    print(f"?? 皜祈岫?勗?撌脣摮嚗report_filename}")

# ============================================
# 銝餌?撘??
# ============================================

if __name__ == "__main__":
    run_consistency_test()

