"""
姓名學 Prompt 模板
Aetheria Core v1.7.0

功能：
1. 五格剖象法解讀
2. 81 數理吉凶分析
3. 三才配置詳解
4. 與八字喜用神整合建議
"""

from typing import Dict, Optional
from src.calculators.name import NameAnalysis


# 系統提示詞
NAME_SYSTEM_PROMPT = """你好，我是 Aetheria。很高興能為您解析這個名字。

你是一位專業的姓名學大師，精通五格剖象法與 81 數理吉凶。

【格式要求】
純文字輸出，不要使用 Markdown（不要出現 #、*、**、>、```、表格或引用）。

【解讀架構】
一、姓名整體評析
二、性格特質分析（人格）
三、事業財運傾向
四、人際關係特點
五、健康注意事項
六、改運建議與期許

請用繁體中文回覆。"""


def generate_basic_analysis_prompt(analysis: NameAnalysis) -> Dict[str, str]:
    """生成基本姓名分析 Prompt"""
    
    # 構建五格詳細資訊
    grid_details = []
    for grid_name in ["天格", "人格", "地格", "外格", "總格"]:
        grid = analysis.grid_analyses[grid_name]
        grid_details.append(
            f"- {grid_name}：{grid.number}（{grid.element}）\n"
            f"  數理：{grid.number_name}（{grid.fortune}）\n"
            f"  含義：{grid.description}\n"
            f"  關鍵詞：{', '.join(grid.keywords)}"
        )
    
    user_prompt = f"""請為以下姓名進行專業的五格剖象法分析：

【基本資料】
姓名：{analysis.full_name}
姓氏：{analysis.surname}（{'、'.join(f'{c}={s}畫' for c, s in zip(analysis.surname, analysis.surname_strokes))}）
名字：{analysis.given_name}（{'、'.join(f'{c}={s}畫' for c, s in zip(analysis.given_name, analysis.given_name_strokes))}）
總筆畫：{analysis.total_strokes} 畫

【五格數理】
{chr(10).join(grid_details)}

【三才配置】
組合：{analysis.three_talents['combination']}（{analysis.three_talents['天格五行']}-{analysis.three_talents['人格五行']}-{analysis.three_talents['地格五行']}）
評價：{analysis.three_talents['fortune']}
說明：{analysis.three_talents['description']}

【整體評價】
{analysis.overall_fortune}

請提供：
1. 姓名整體評析（200字以內）
2. 性格特質分析（根據人格數）
3. 事業財運傾向
4. 人際關係特點
5. 健康注意事項
6. 改運建議（如適用）

請用繁體中文回答，語氣專業但親切。"""

    return {
        "system_prompt": NAME_SYSTEM_PROMPT,
        "user_prompt": user_prompt
    }


def generate_career_prompt(analysis: NameAnalysis) -> Dict[str, str]:
    """生成事業分析 Prompt"""
    
    人格 = analysis.grid_analyses["人格"]
    總格 = analysis.grid_analyses["總格"]
    外格 = analysis.grid_analyses["外格"]
    
    user_prompt = f"""請根據姓名學五格剖象法，分析「{analysis.full_name}」的事業運勢：

【關鍵數據】
人格（主運）：{人格.number}（{人格.element}）- {人格.fortune}
  - {人格.number_name}：{人格.description}

外格（人際運）：{外格.number}（{外格.element}）- {外格.fortune}
  - {外格.number_name}：{外格.description}

總格（後運）：{總格.number}（{總格.element}）- {總格.fortune}
  - {總格.number_name}：{總格.description}

三才配置：{analysis.three_talents['combination']} - {analysis.three_talents['fortune']}

請分析：
1. 適合的職業方向
2. 創業 vs 受僱的建議
3. 與上司/同事的相處模式
4. 財運特點與理財建議
5. 事業發展的黃金時期

請用繁體中文回答。"""

    return {
        "system_prompt": NAME_SYSTEM_PROMPT,
        "user_prompt": user_prompt
    }


def generate_relationship_prompt(analysis: NameAnalysis) -> Dict[str, str]:
    """生成感情/人際關係分析 Prompt"""
    
    地格 = analysis.grid_analyses["地格"]
    外格 = analysis.grid_analyses["外格"]
    人格 = analysis.grid_analyses["人格"]
    
    user_prompt = f"""請根據姓名學五格剖象法，分析「{analysis.full_name}」的感情與人際關係：

【關鍵數據】
人格（主運）：{人格.number}（{人格.element}）- {人格.fortune}
  - 個性特質：{', '.join(人格.keywords)}

地格（家庭運）：{地格.number}（{地格.element}）- {地格.fortune}
  - {地格.number_name}：{地格.description}

外格（人際運）：{外格.number}（{外格.element}）- {外格.fortune}
  - {外格.number_name}：{外格.description}

三才配置：{analysis.three_talents['combination']} - {analysis.three_talents['fortune']}

請分析：
1. 感情觀與擇偶傾向
2. 婚姻運勢與相處模式
3. 與家人的關係
4. 朋友緣與貴人運
5. 改善人際關係的建議

請用繁體中文回答。"""

    return {
        "system_prompt": NAME_SYSTEM_PROMPT,
        "user_prompt": user_prompt
    }


def generate_bazi_integration_prompt(analysis: NameAnalysis, 
                                      bazi_element: str,
                                      bazi_info: Optional[str] = None) -> Dict[str, str]:
    """生成與八字整合的分析 Prompt"""
    
    人格 = analysis.grid_analyses["人格"]
    
    # 五行相生相剋關係
    element_relations = {
        ("木", "木"): "比和",
        ("木", "火"): "相生（木生火）",
        ("木", "土"): "相剋（木剋土）",
        ("木", "金"): "相剋（金剋木）",
        ("木", "水"): "相生（水生木）",
        ("火", "木"): "相生（木生火）",
        ("火", "火"): "比和",
        ("火", "土"): "相生（火生土）",
        ("火", "金"): "相剋（火剋金）",
        ("火", "水"): "相剋（水剋火）",
        ("土", "木"): "相剋（木剋土）",
        ("土", "火"): "相生（火生土）",
        ("土", "土"): "比和",
        ("土", "金"): "相生（土生金）",
        ("土", "水"): "相剋（土剋水）",
        ("金", "木"): "相剋（金剋木）",
        ("金", "火"): "相剋（火剋金）",
        ("金", "土"): "相生（土生金）",
        ("金", "金"): "比和",
        ("金", "水"): "相生（金生水）",
        ("水", "木"): "相生（水生木）",
        ("水", "火"): "相剋（水剋火）",
        ("水", "土"): "相剋（土剋水）",
        ("水", "金"): "相生（金生水）",
        ("水", "水"): "比和",
    }
    
    relation = element_relations.get((bazi_element, 人格.element), "未知關係")
    
    bazi_section = f"\n\n【八字資訊】\n{bazi_info}" if bazi_info else ""
    
    user_prompt = f"""請根據姓名學與八字命理，進行整合分析：

【姓名資料】
姓名：{analysis.full_name}
人格五行：{人格.element}（{人格.number}）
三才配置：{analysis.three_talents['combination']}

【八字喜用神】
喜用神五行：{bazi_element}{bazi_section}

【姓名與八字的關係】
人格五行（{人格.element}）與喜用神（{bazi_element}）：{relation}

請分析：
1. 姓名與八字的配合度（滿分 100）
2. 姓名對八字的補益或損耗
3. 如何透過姓名補強八字所缺
4. 使用別名或筆名的建議
5. 整體命名建議

請用繁體中文回答，結合姓名學與八字理論。"""

    return {
        "system_prompt": NAME_SYSTEM_PROMPT,
        "user_prompt": user_prompt
    }


def generate_name_suggestion_prompt(surname: str, 
                                     surname_strokes: int,
                                     gender: str = "中性",
                                     bazi_element: Optional[str] = None,
                                     desired_traits: Optional[list] = None) -> Dict[str, str]:
    """生成命名建議 Prompt"""
    
    # 計算建議的人格數（吉數）
    lucky_numbers = [1, 3, 5, 6, 7, 8, 11, 13, 15, 16, 17, 18, 21, 23, 24, 25, 29, 31, 32, 33, 35, 37, 39, 41, 45, 47, 48, 52, 57, 61, 63, 65, 67, 68, 81]
    
    # 根據姓氏筆畫建議名字第一字筆畫
    suggested_first_char_strokes = [n - surname_strokes for n in lucky_numbers if 1 <= n - surname_strokes <= 20][:5]
    
    bazi_section = f"八字喜用神：{bazi_element}" if bazi_element else "八字喜用神：未提供"
    traits_section = f"期望特質：{', '.join(desired_traits)}" if desired_traits else "期望特質：未指定"
    
    user_prompt = f"""請根據姓名學五格剖象法，為以下條件提供命名建議：

【命名條件】
姓氏：{surname}（{surname_strokes} 畫）
性別傾向：{gender}
{bazi_section}
{traits_section}

【姓名學建議】
為使人格數為吉數，名字第一字建議筆畫：{', '.join(map(str, suggested_first_char_strokes))} 畫

請提供：
1. 5 個推薦名字（含筆畫分析）
2. 每個名字的五格數理
3. 三才配置分析
4. 名字的含義與寓意
5. 綜合評分（滿分 100）

格式範例：
【名字一】{surname}○○
- 筆畫：姓 X 畫 + 名 Y+Z 畫 = 總 N 畫
- 五格：天格 X、人格 Y、地格 Z、外格 W、總格 N
- 三才：○○○（吉/凶）
- 寓意：...
- 評分：XX/100

請用繁體中文回答。"""

    return {
        "system_prompt": NAME_SYSTEM_PROMPT,
        "user_prompt": user_prompt
    }


def generate_name_prompt(analysis: NameAnalysis, 
                          analysis_type: str = "basic",
                          bazi_element: Optional[str] = None,
                          bazi_info: Optional[str] = None) -> Dict[str, str]:
    """主要 Prompt 生成函數"""
    
    if analysis_type == "basic":
        return generate_basic_analysis_prompt(analysis)
    elif analysis_type == "career":
        return generate_career_prompt(analysis)
    elif analysis_type == "relationship":
        return generate_relationship_prompt(analysis)
    elif analysis_type == "bazi" and bazi_element:
        return generate_bazi_integration_prompt(analysis, bazi_element, bazi_info)
    else:
        return generate_basic_analysis_prompt(analysis)


# 測試
if __name__ == "__main__":
    from name_calculator import NameCalculator
    
    calc = NameCalculator()
    analysis = calc.analyze("陳育助")
    
    # 測試各種 Prompt
    print("=" * 60)
    print("基本分析 Prompt")
    print("=" * 60)
    prompts = generate_basic_analysis_prompt(analysis)
    print(f"System Prompt 長度：{len(prompts['system_prompt'])} 字")
    print(f"User Prompt 長度：{len(prompts['user_prompt'])} 字")
    print()
    
    print("=" * 60)
    print("事業分析 Prompt")
    print("=" * 60)
    prompts = generate_career_prompt(analysis)
    print(f"User Prompt 長度：{len(prompts['user_prompt'])} 字")
    print()
    
    print("=" * 60)
    print("八字整合 Prompt")
    print("=" * 60)
    prompts = generate_bazi_integration_prompt(analysis, "木", "日主為甲木")
    print(f"User Prompt 長度：{len(prompts['user_prompt'])} 字")
    print()
    
    print("=" * 60)
    print("命名建議 Prompt")
    print("=" * 60)
    prompts = generate_name_suggestion_prompt("陳", 16, "男", "木", ["聰明", "穩重"])
    print(f"User Prompt 長度：{len(prompts['user_prompt'])} 字")
    print()
    
    print("✅ 姓名學 Prompt 模板測試完成！")
