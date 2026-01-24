"""
靈數學 Prompt 模板
Aetheria Core v1.6.0

為 Gemini AI 生成靈數學解讀的專業 Prompt
"""

from typing import Dict
from src.calculators.numerology import NumerologyProfile, NumerologyCalculator


# 系統提示詞
NUMEROLOGY_SYSTEM_PROMPT = """你是一位專業的畢達哥拉斯靈數學分析師，擁有深厚的數字命理學知識。

【核心原則】
1. **有所本**：所有解讀都必須基於畢達哥拉斯靈數學的傳統理論
2. **整體觀**：綜合分析所有數字的相互作用，而非孤立解讀
3. **建設性**：即使是挑戰性的數字也要給予積極的成長指引
4. **尊重性**：數字提供的是傾向和潛能，而非絕對命運

【解讀風格】
- 語氣專業但親切，避免過於神秘或嚇人的描述
- 提供具體可行的建議，而非空泛的預言
- 強調個人成長和自我實現的可能性
- 適度引用數字的象徵意義來支持解讀

【數字核心意義】
1 - 領導、獨立、開創
2 - 合作、平衡、敏感
3 - 創意、表達、樂觀
4 - 穩定、實際、建設
5 - 自由、變化、冒險
6 - 責任、愛、服務
7 - 智慧、分析、靈性
8 - 權力、成就、財富
9 - 智慧、慈悲、完成
11 - 直覺、靈性啟示（主數）
22 - 宏觀建設、實現夢想（主數）
33 - 慈悲大師、無私服務（主數）

請用繁體中文回覆。"""


def get_life_path_prompt(profile: NumerologyProfile, calc: NumerologyCalculator) -> str:
    """生成生命靈數解讀的 Prompt"""
    meaning = calc.get_number_meaning(profile.life_path, "life_path")
    
    master_note = ""
    if profile.life_path_master:
        master_note = f"""

【主數特別說明】
此人的生命靈數 {profile.life_path} 是主數（Master Number），代表更高層次的使命與挑戰。
主數不會化約為單一數字，象徵著特殊的靈性任務和更大的潛能，但同時也帶來更大的壓力和責任。"""
    
    return f"""請為以下命主進行【生命靈數】深度解讀：

【基本資料】
出生日期：{profile.birth_date.strftime('%Y年%m月%d日')}
生命靈數：{profile.life_path}
數字名稱：{meaning.get('name', '')} ({meaning.get('name_en', '')})
對應元素：{meaning.get('element', '')}
對應行星：{meaning.get('planet', '')}
{master_note}

【核心關鍵詞】
{', '.join(meaning.get('keywords', []))}

【正面特質】
{', '.join(meaning.get('positive_traits', []))}

【需注意特質】
{', '.join(meaning.get('negative_traits', []))}

【人生使命】
{meaning.get('life_purpose', '')}

【人生課題】
{meaning.get('life_lessons', '')}

請提供：
1. 此生命靈數的核心能量解讀（300-400字）
2. 性格特質與行為模式分析
3. 人生使命與成長方向
4. 具體可行的生活建議（3-5條）
5. 本靈數的潛能發揮秘訣"""


def get_full_profile_prompt(profile: NumerologyProfile, calc: NumerologyCalculator) -> str:
    """生成完整靈數檔案解讀的 Prompt"""
    
    formatted = calc.format_profile_for_prompt(profile, "general")
    
    return f"""請為以下命主進行【完整靈數學檔案】深度解讀：

{formatted}

【解讀要求】
請依序提供以下分析：

**一、核心數字解析**
分析生命靈數、天賦數、靈魂渴望數、人格數之間的關係與整體意義。

**二、內外一致性分析**
- 靈魂渴望數（內在渴望）vs 人格數（外在形象）的差異與整合
- 生命靈數（人生使命）vs 天賦數（天生才能）的配合

**三、流年運勢指引**
根據當前流年數，提供今年的主題、機會與注意事項。

**四、人生階段分析**
根據高峰期數字，說明不同人生階段的主題與能量。

**五、挑戰與成長**
根據挑戰數，說明需要克服的課題與成長建議。

**六、綜合建議**
整合所有數字，給予 3-5 條具體可行的人生建議。

請用專業但親切的語氣，提供有深度的分析（總共約 800-1200 字）。"""


def get_personal_year_prompt(profile: NumerologyProfile, calc: NumerologyCalculator, year: int = None) -> str:
    """生成流年運勢的 Prompt"""
    from datetime import datetime
    
    if year is None:
        year = datetime.now().year
    
    py_meaning = calc.get_number_meaning(profile.personal_year, "personal_year")
    lp_meaning = calc.get_number_meaning(profile.life_path, "life_path")
    
    return f"""請為以下命主進行【{year}年流年運勢】解讀：

【基本資料】
出生日期：{profile.birth_date.strftime('%Y年%m月%d日')}
生命靈數：{profile.life_path} - {lp_meaning.get('name', '')}

【流年資訊】
{year}年流年數：{profile.personal_year}
流年主題：{py_meaning.get('theme', '')}
關鍵詞：{', '.join(py_meaning.get('keywords', []))}

【流年基本含義】
{py_meaning.get('description', '')}

【官方建議】
{py_meaning.get('advice', '')}

【當前流月】
{datetime.now().month}月流月數：{profile.personal_month}

【今日能量】
流日數：{profile.personal_day}

請提供：
1. **年度總運勢**：今年的整體能量與主題（200-300字）
2. **各領域運勢**：
   - 事業/學業運勢
   - 感情/人際運勢  
   - 財運/投資運勢
   - 健康/身心狀態
3. **月度運勢重點**：標出今年特別重要的月份
4. **年度行動指南**：5-7 條具體建議
5. **本月特別提醒**：根據當前流月數給予指引"""


def get_compatibility_prompt(profile1: NumerologyProfile, profile2: NumerologyProfile, 
                            calc: NumerologyCalculator) -> str:
    """生成靈數相容性分析的 Prompt"""
    
    compat = calc.calculate_compatibility(profile1.life_path, profile2.life_path)
    
    lp1_meaning = calc.get_number_meaning(profile1.life_path, "life_path")
    lp2_meaning = calc.get_number_meaning(profile2.life_path, "life_path")
    
    return f"""請進行【靈數相容性】深度分析：

【甲方資料】
出生日期：{profile1.birth_date.strftime('%Y年%m月%d日')}
生命靈數：{profile1.life_path} - {lp1_meaning.get('name', '')}
天賦數：{profile1.expression}
靈魂渴望數：{profile1.soul_urge}
人格數：{profile1.personality}

【乙方資料】
出生日期：{profile2.birth_date.strftime('%Y年%m月%d日')}
生命靈數：{profile2.life_path} - {lp2_meaning.get('name', '')}
天賦數：{profile2.expression}
靈魂渴望數：{profile2.soul_urge}
人格數：{profile2.personality}

【初步相容性評估】
相容程度：{compat['compatibility_level']}
基本描述：{compat['description']}

請提供完整的相容性分析：

**一、生命靈數相容性**（核心分析）
分析兩人生命靈數 {profile1.life_path} 與 {profile2.life_path} 的互動模式與挑戰。

**二、靈魂層面相容性**
分析兩人靈魂渴望數的匹配程度，了解深層需求是否契合。

**三、外在互動相容性**
分析兩人人格數的配合，預測日常相處的模式。

**四、成長方向相容性**
分析兩人天賦數，看彼此是否能在發展上互相支持。

**五、關係優勢與挑戰**
- 這段關係的 3 個主要優勢
- 這段關係的 3 個主要挑戰

**六、相處建議**
提供 5 條具體的相處與溝通建議。

**七、總評**
給予整體關係評分（1-10）與總結。"""


def get_career_prompt(profile: NumerologyProfile, calc: NumerologyCalculator) -> str:
    """生成事業分析的 Prompt"""
    
    lp_meaning = calc.get_number_meaning(profile.life_path, "life_path")
    
    career_suggestions = lp_meaning.get('career_suggestions', [])
    
    return f"""請為以下命主進行【靈數事業分析】：

【基本資料】
出生日期：{profile.birth_date.strftime('%Y年%m月%d日')}
生命靈數：{profile.life_path} - {lp_meaning.get('name', '')}
天賦數：{profile.expression}
人格數：{profile.personality}
生日數：{profile.birthday}

【人生使命】
{lp_meaning.get('life_purpose', '')}

【建議職業方向】
{', '.join(career_suggestions)}

【當前流年】
流年數：{profile.personal_year}（影響今年事業運勢）

【高峰期資訊】
""" + "\n".join([f"• {p['name']}（{p['age_start']}-{p['age_end'] if p['age_end'] else '終生'}歲）：{p['pinnacle']}" 
                 for p in profile.pinnacles]) + f"""

請提供詳細的事業分析：

**一、天賦才能分析**
根據生命靈數和天賦數，分析最適合發揮的工作能力。

**二、最佳職業方向**
列出 5-7 個最適合的職業領域，並說明原因。

**三、工作風格特點**
描述在工作中的行為模式、優勢與需注意事項。

**四、領導與合作模式**
分析適合的工作角色（領導/獨立/團隊）。

**五、財運與收入模式**
根據靈數分析適合的賺錢方式與財富觀。

**六、今年事業運勢**
根據流年數 {profile.personal_year}，分析今年事業發展方向。

**七、事業發展建議**
提供 5 條具體的職業發展建議。"""


def generate_numerology_prompt(profile: NumerologyProfile, calc: NumerologyCalculator,
                               analysis_type: str = "full", 
                               context: str = "general",
                               profile2: NumerologyProfile = None) -> Dict[str, str]:
    """
    生成靈數學解讀的完整 Prompt
    
    Args:
        profile: 命主的靈數檔案
        calc: 靈數學計算器實例
        analysis_type: 分析類型
            - "life_path": 生命靈數解讀
            - "full": 完整檔案解讀
            - "personal_year": 流年運勢
            - "compatibility": 相容性分析（需要 profile2）
            - "career": 事業分析
        context: 情境（general, love, career, finance, health）
        profile2: 第二位命主的靈數檔案（相容性分析用）
        
    Returns:
        包含 system_prompt 和 user_prompt 的字典
    """
    
    system_prompt = NUMEROLOGY_SYSTEM_PROMPT
    
    if analysis_type == "life_path":
        user_prompt = get_life_path_prompt(profile, calc)
    elif analysis_type == "full":
        user_prompt = get_full_profile_prompt(profile, calc)
    elif analysis_type == "personal_year":
        user_prompt = get_personal_year_prompt(profile, calc)
    elif analysis_type == "compatibility" and profile2:
        user_prompt = get_compatibility_prompt(profile, profile2, calc)
    elif analysis_type == "career":
        user_prompt = get_career_prompt(profile, calc)
    else:
        # 預設使用完整檔案
        user_prompt = get_full_profile_prompt(profile, calc)
    
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt
    }


# 測試
if __name__ == "__main__":
    from datetime import date
    
    print("=" * 60)
    print("靈數學 Prompt 模板測試")
    print("=" * 60)
    
    calc = NumerologyCalculator()
    
    # 測試資料
    test_date = date(1979, 11, 12)
    test_name = "CHEN YU CHU"
    profile = calc.calculate_full_profile(test_date, test_name)
    
    print(f"\n測試資料：")
    print(f"  出生日期：{test_date}")
    print(f"  英文姓名：{test_name}")
    print(f"  生命靈數：{profile.life_path}")
    
    # 測試各種 Prompt
    test_types = ["life_path", "full", "personal_year", "career"]
    
    for analysis_type in test_types:
        prompts = generate_numerology_prompt(profile, calc, analysis_type)
        print(f"\n【{analysis_type}】Prompt 長度：")
        print(f"  System Prompt：{len(prompts['system_prompt'])} 字")
        print(f"  User Prompt：{len(prompts['user_prompt'])} 字")
    
    # 測試相容性 Prompt
    test_date2 = date(1985, 5, 20)
    test_name2 = "WANG XIAO MING"
    profile2 = calc.calculate_full_profile(test_date2, test_name2)
    
    prompts = generate_numerology_prompt(profile, calc, "compatibility", profile2=profile2)
    print(f"\n【compatibility】Prompt 長度：")
    print(f"  System Prompt：{len(prompts['system_prompt'])} 字")
    print(f"  User Prompt：{len(prompts['user_prompt'])} 字")
    
    # 顯示一個完整的 Prompt 範例
    print("\n" + "=" * 60)
    print("完整 Prompt 範例（生命靈數）")
    print("=" * 60)
    prompts = generate_numerology_prompt(profile, calc, "life_path")
    print("\n【User Prompt 預覽（前 500 字）】")
    print("-" * 40)
    print(prompts['user_prompt'][:500] + "...")
    
    print("\n" + "=" * 60)
    print("✅ 靈數學 Prompt 模板測試完成！")
    print("=" * 60)
