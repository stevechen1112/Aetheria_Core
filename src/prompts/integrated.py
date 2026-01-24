"""
整合分析 Prompt 模板
Aetheria Core v1.8.0

功能：
1. 靈數學 + 姓名學整合分析
2. 靈數學 + 姓名學 + 八字整合
3. 完整命理檔案生成
"""

from typing import Dict, Optional
from src.calculators.numerology import NumerologyProfile
from src.calculators.name import NameAnalysis


# 整合分析系統提示詞
INTEGRATED_SYSTEM_PROMPT = """你是一位精通多種命理系統的高級命理分析師，專長包括：
- 畢達哥拉斯靈數學
- 五格剖象法姓名學
- 八字命理（如有提供）

【核心原則】
1. **系統整合**：各系統的分析要互相呼應，找出共同主題
2. **有所本**：所有解讀都必須基於各命理系統的傳統理論
3. **深度洞察**：發掘各系統間的關聯性與互補性
4. **實用建議**：提供具體可行的人生指引

【分析重點】
- 靈數學揭示靈魂層面的使命與潛能
- 姓名學反映社會層面的運勢與互動
- 八字命理呈現先天格局與流年運勢
- 三者結合可得到更完整的命理藍圖

請用繁體中文回覆，語氣專業但親切。"""


def generate_integrated_prompt(
    numerology_profile: NumerologyProfile,
    name_analysis: NameAnalysis,
    calc_numerology,
    include_bazi: bool = False,
    bazi_data: Optional[Dict] = None,
    analysis_focus: str = "general",
    gender: str = "未指定"
) -> Dict[str, str]:
    """
    生成靈數學+姓名學整合分析 Prompt
    
    Args:
        numerology_profile: 靈數學檔案
        name_analysis: 姓名學分析結果
        calc_numerology: 靈數學計算器
        include_bazi: 是否包含八字
        bazi_data: 八字資料
        analysis_focus: 分析焦點 (general/career/love/wealth/health)
        gender: 性別（男/女/未指定）
    """
    
    # 性別稱謂
    if gender == "男":
        honorific = "先生"
    elif gender == "女":
        honorific = "女士"
    else:
        honorific = ""
    
    # 靈數學資訊
    lp_meaning = calc_numerology.get_number_meaning(numerology_profile.life_path, "life_path")
    py_meaning = calc_numerology.get_number_meaning(numerology_profile.personal_year, "personal_year")
    
    numerology_section = f"""【基本資料】
姓名：{name_analysis.full_name}{honorific}
性別：{gender}
出生日期：{numerology_profile.birth_date.strftime('%Y年%m月%d日')}

【靈數學分析】

◆ 核心數字
• 生命靈數：{numerology_profile.life_path}{"（主數）" if numerology_profile.life_path_master else ""} - {lp_meaning.get('name', '')}
  特質關鍵詞：{', '.join(lp_meaning.get('keywords', [])[:5])}
• 生日數：{numerology_profile.birthday}
• 流年數：{numerology_profile.personal_year} - {py_meaning.get('theme', '')}
• 流月數：{numerology_profile.personal_month}
• 流日數：{numerology_profile.personal_day}

◆ 高峰期（當前年齡相關）
"""
    for p in numerology_profile.pinnacles:
        age_range = f"{p['age_start']}-{p['age_end']}歲" if p['age_end'] else f"{p['age_start']}歲至終生"
        master_note = "（主數）" if p.get('is_master') else ""
        numerology_section += f"• {p['name']}（{age_range}）：{p['pinnacle']}{master_note}\n"
    
    numerology_section += "\n◆ 人生挑戰\n"
    for c in numerology_profile.challenges:
        numerology_section += f"• {c['name']}：{c['challenge']}\n"
    
    if numerology_profile.karmic_debts:
        numerology_section += "\n◆ 業力債\n"
        for debt in numerology_profile.karmic_debts:
            numerology_section += f"• {debt['number']}（{debt['source']}）：{debt['lesson']}\n"
    
    # 姓名學資訊
    name_section = f"""
【姓名學分析】
姓名：{name_analysis.full_name}
姓氏：{name_analysis.surname}（{'、'.join(f'{c}={s}畫' for c, s in zip(name_analysis.surname, name_analysis.surname_strokes))}）
名字：{name_analysis.given_name}（{'、'.join(f'{c}={s}畫' for c, s in zip(name_analysis.given_name, name_analysis.given_name_strokes))}）
總筆畫：{name_analysis.total_strokes} 畫

◆ 五格數理
"""
    for grid_name in ["天格", "人格", "地格", "外格", "總格"]:
        grid = name_analysis.grid_analyses[grid_name]
        name_section += f"• {grid_name}：{grid.number}（{grid.element}）- {grid.fortune}\n"
        name_section += f"  {grid.number_name}：{grid.description[:50]}...\n"
    
    name_section += f"""
◆ 三才配置
組合：{name_analysis.three_talents['combination']}（{name_analysis.three_talents['fortune']}）
說明：{name_analysis.three_talents['description']}

◆ 整體評價：{name_analysis.overall_fortune}
"""

    # 八字資訊（如果有）
    bazi_section = ""
    if include_bazi and bazi_data:
        bazi_section = f"""
【八字命理】
四柱：{bazi_data.get('year_pillar', '')} {bazi_data.get('month_pillar', '')} {bazi_data.get('day_pillar', '')} {bazi_data.get('hour_pillar', '')}
日主：{bazi_data.get('day_master', '')}
喜用神：{bazi_data.get('favorable_elements', '')}
忌神：{bazi_data.get('unfavorable_elements', '')}
"""

    # 整合分析指引
    integration_guide = """
【系統整合要點】

◆ 靈數與姓名的關聯
"""
    # 分析生命靈數與人格數的關係
    lp_element = _get_numerology_element(numerology_profile.life_path)
    person_grid_element = name_analysis.grid_analyses["人格"].element
    
    integration_guide += f"• 生命靈數 {numerology_profile.life_path} 的能量特質 vs 姓名人格數 {name_analysis.grid_analyses['人格'].number}（{person_grid_element}）的五行\n"
    integration_guide += f"• 生命靈數的能量傾向：{lp_element}\n"
    integration_guide += f"• 姓名人格的五行：{person_grid_element}\n"
    
    # 分析焦點
    focus_prompts = {
        "general": """
請提供【完整命理整合分析】：

1. **整合概述**（300字）
   綜合靈數學與姓名學的發現，描繪此人的核心特質與人生主題

2. **性格特質深度分析**（400字）
   - 靈魂層面（來自靈數）
   - 社會層面（來自姓名）
   - 兩者的一致性與張力

3. **人生使命與天賦**（300字）
   結合生命靈數的使命與姓名數理的才能分析

4. **運勢週期分析**（300字）
   - 當前流年能量（靈數）
   - 姓名格數的運勢週期

5. **潛在挑戰與成長機會**（250字）
   整合挑戰數與姓名中的半凶/凶數分析

6. **實用建議**
   提供 5-7 條具體可行的人生指引

7. **總結**（150字）
   給予整體評價與祝福""",

        "career": """
請提供【事業發展整合分析】：

1. **天賦才能分析**（300字）
   結合靈數與姓名揭示的職業天賦

2. **適合的職業方向**
   列出 5-7 個最適合的職業領域，並說明原因

3. **工作風格與領導力**（250字）
   - 個人工作模式
   - 與上司/同事的互動模式
   - 領導潛能分析

4. **財運與事業發展**（250字）
   - 財富觀念與理財傾向
   - 事業黃金期預測

5. **今年事業運勢**（200字）
   根據流年數與姓名數理分析

6. **事業發展建議**
   提供 5 條具體的職業發展建議""",

        "love": """
請提供【感情與人際關係整合分析】：

1. **感情觀與愛情模式**（300字）
   結合靈數學與姓名學分析愛情傾向

2. **理想伴侶類型**（200字）
   根據靈數與姓名推斷適合的伴侶特質

3. **婚姻運勢分析**（250字）
   - 姓名地格（家庭運）分析
   - 靈數的關係模式

4. **人際關係特點**（200字）
   - 外格（人際運）分析
   - 靈數學的社交傾向

5. **感情建議**
   提供 5 條改善感情與人際關係的建議""",

        "wealth": """
請提供【財富與金錢整合分析】：

1. **財富觀念分析**（250字）
   結合靈數與姓名揭示的金錢觀

2. **賺錢模式與能力**（300字）
   - 適合的收入來源
   - 創業 vs 受僱建議

3. **理財傾向分析**（200字）
   - 投資偏好
   - 風險承受度

4. **財運週期**（200字）
   - 流年財運
   - 人生財富高峰期

5. **財富建議**
   提供 5 條具體的理財與財富建議""",

        "health": """
請提供【身心健康整合分析】：

1. **體質傾向分析**（250字）
   根據姓名五行與靈數分析

2. **需注意的健康面向**（200字）
   - 三才配置的健康影響
   - 靈數揭示的能量失衡

3. **心理健康與壓力**（200字）
   - 情緒模式分析
   - 壓力來源與因應

4. **養生建議**
   提供 5 條具體的身心健康建議"""
    }
    
    user_prompt = f"""請為以下命主進行【靈數學 + 姓名學】深度整合分析：

{numerology_section}
{name_section}
{bazi_section}
{integration_guide}
{focus_prompts.get(analysis_focus, focus_prompts['general'])}

請用專業但親切的語氣，提供有深度的整合分析（總共約 1500-2000 字）。"""

    return {
        "system_prompt": INTEGRATED_SYSTEM_PROMPT,
        "user_prompt": user_prompt
    }


def _get_numerology_element(number: int) -> str:
    """將靈數對應到能量特質"""
    elements = {
        1: "火（領導、開創）",
        2: "水（合作、敏感）",
        3: "火（創意、表達）",
        4: "土（穩定、實際）",
        5: "風（自由、變化）",
        6: "土（責任、愛）",
        7: "水（智慧、靈性）",
        8: "土（權力、成就）",
        9: "火（智慧、慈悲）",
        11: "風（直覺、靈性啟示）",
        22: "土（宏觀建設）",
        33: "火（慈悲大師）"
    }
    return elements.get(number, "中性")


def generate_quick_profile_prompt(
    birth_date_str: str,
    chinese_name: str,
    english_name: str = ""
) -> Dict[str, str]:
    """
    快速檔案分析 Prompt
    """
    user_prompt = f"""請為以下個人資料提供快速命理概覽：

出生日期：{birth_date_str}
中文姓名：{chinese_name}
英文姓名：{english_name if english_name else '未提供'}

請根據以上資訊，快速計算並提供：

1. **靈數學速覽**
   - 生命靈數及其含義
   - 今年流年數及主題

2. **姓名學速覽**
   - 五格數理概要
   - 三才配置評價

3. **整合建議**
   3 條最重要的人生指引

請用簡潔有力的方式呈現（約 400-500 字）。"""

    return {
        "system_prompt": INTEGRATED_SYSTEM_PROMPT,
        "user_prompt": user_prompt
    }


def generate_comparison_prompt(
    profile1: dict,
    profile2: dict
) -> Dict[str, str]:
    """
    兩人比對分析 Prompt（靈數+姓名）
    """
    user_prompt = f"""請為以下兩人進行【靈數學 + 姓名學】相容性整合分析：

【甲方】
姓名：{profile1.get('name', '')}
出生日期：{profile1.get('birth_date', '')}
生命靈數：{profile1.get('life_path', '')}
姓名人格數：{profile1.get('personality_grid', '')}（{profile1.get('personality_element', '')}）
三才配置：{profile1.get('three_talents', '')}

【乙方】
姓名：{profile2.get('name', '')}
出生日期：{profile2.get('birth_date', '')}
生命靈數：{profile2.get('life_path', '')}
姓名人格數：{profile2.get('personality_grid', '')}（{profile2.get('personality_element', '')}）
三才配置：{profile2.get('three_talents', '')}

請提供：

1. **靈數相容性分析**（250字）
   兩人生命靈數的互動模式

2. **姓名相容性分析**（250字）
   五行生剋關係與互補性

3. **整體相容度評分**
   給予 1-100 的相容度分數

4. **相處優勢與挑戰**
   各列出 3 點

5. **相處建議**
   5 條具體的相處與溝通建議

請用專業但親切的語氣分析。"""

    return {
        "system_prompt": INTEGRATED_SYSTEM_PROMPT,
        "user_prompt": user_prompt
    }


# 測試
if __name__ == "__main__":
    print("=" * 60)
    print("整合分析 Prompt 模板測試")
    print("=" * 60)
    
    # 這裡只測試 Prompt 生成邏輯
    print("✅ 整合分析 Prompt 模板載入成功！")
    print("支援的分析焦點：general, career, love, wealth, health")
    print("=" * 60)
