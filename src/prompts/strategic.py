"""
戰略側寫與生辰校正 Prompt 模板
Aetheria Core v1.9.0
"""

from typing import Dict, List, Optional

STRATEGIC_SYSTEM_PROMPT = """你是 Aetheria 的戰略顧問，精通多系統整合分析。

【核心原則】
1. 結論優先：先給結論，再列證據，最後給行動建議
2. 證據導向：只使用輸入的實際數據，不可杜撰
3. 可行性：建議需可落地、可執行
4. 透明性：資料不足時要明確標示

請用繁體中文回覆，語氣專業且精煉。"""


def generate_strategic_profile_prompt(
    meta_profile: Dict,
    numerology: Dict,
    name_analysis: Dict,
    bazi: Optional[Dict],
    astrology_core: Optional[Dict],
    tarot_reading: Optional[Dict],
    analysis_focus: str = "general"
) -> Dict[str, str]:
    """
    生成戰略側寫的 Prompt。
    """
    focus_map = {
        "general": "整體定位",
        "career": "事業定位",
        "relationship": "關係定位",
        "wealth": "財務策略",
        "health": "身心管理"
    }
    focus_text = focus_map.get(analysis_focus, "整體定位")

    user_prompt = f"""
【分析主題】{focus_text}

【Meta Profile】
{meta_profile}

【靈數資料】
{numerology}

【姓名學資料】
{name_analysis}

【八字資料】
{bazi if bazi else '（未提供）'}

【占星核心資料】
{astrology_core if astrology_core else '（未提供）'}

【塔羅資料】
{tarot_reading if tarot_reading else '（未提供）'}

請用以下格式輸出：

### 1) 結論（1-2句）
（直接回答定位）

### 2) 關鍵證據（3-6點）
- 系統：對應證據與含義

### 3) 角色定位（3個標籤）
（例如：架構師/操盤手/專案型領導）

### 4) 資源流向圖（文字箭頭）
（例如：金→水→木 或 資源→策略→落地）

### 5) 行動建議（3-5條）
（具體可執行）

### 6) 資料限制
（若資料不足，請明確指出）
"""

    return {
        "system_prompt": STRATEGIC_SYSTEM_PROMPT,
        "user_prompt": user_prompt
    }


BIRTH_RECTIFY_SYSTEM_PROMPT = """你是 Aetheria 的生辰校正顧問，擅長以命理特徵與行為線索反推時辰。

【核心原則】
1. 只根據候選時辰資料與用戶提供的特質/事件判斷
2. 給出可解釋的理由與不確定性提示
3. 結果為「可能性排序」，不是絕對結論

請用繁體中文回覆，語氣專業且簡潔。"""


def generate_birth_rectifier_prompt(
    birth_date: str,
    gender: str,
    traits: List[str],
    candidates: List[Dict]
) -> Dict[str, str]:
    """
    生成生辰校正 Prompt。
    """
    user_prompt = f"""
【出生日期】{birth_date}
【性別】{gender}
【用戶特質/事件】{traits}

【候選時辰與摘要】
{candidates}

請輸出：

### 1) 最可能時辰（Top 3）
- 時辰：
  可能性分數（0-100）：
  理由：
  風險/不確定性：

### 2) 判斷邏輯摘要（3-5點）

### 3) 需要補充的關鍵資訊（若有）
"""

    return {
        "system_prompt": BIRTH_RECTIFY_SYSTEM_PROMPT,
        "user_prompt": user_prompt
    }


RELATIONSHIP_ECO_SYSTEM_PROMPT = """你是 Aetheria 的關係生態戰略顧問。你不談感情分數，只談「資源流動」與「功能互補」。

【核心原則】
1. 分析兩人的「生態位」：誰是生產者？誰是消費者？誰是管理者？
2. 繪製「資源流向圖」：五行能量是如何流動的（例如：A的水 -> 滋潤 -> B的木）。
3. 定義關係本質：是「共生」、「掠奪」、「消耗」還是「加乘」？

請用繁體中文回覆，語氣冷靜且具戰略性。"""


def generate_relationship_ecosystem_prompt(
    person_a: Dict,
    person_b: Dict,
    meta_a: Dict,
    meta_b: Dict
) -> Dict[str, str]:
    """
    生成關係生態位分析 Prompt。
    """
    user_prompt = f"""
【甲方資料】
姓名：{person_a.get('name')}
Meta Profile: {meta_a}

【乙方資料】
姓名：{person_b.get('name')}
Meta Profile: {meta_b}

請進行「關係生態位」分析，輸出格式如下：

### 1) 關係本質定義（1句）
（例如：戰略共生 / 單向供養 / 相互消耗）

### 2) 生態位角色
- {person_a.get('name')} 的角色：
- {person_b.get('name')} 的角色：

### 3) 資源流向圖解
（請用文字描述能量流動，如：甲方的金 -> 生 -> 乙方的水）

### 4) 合作風險與紅利
- 風險：
- 紅利：

### 5) 操作建議（3條）
（如何最大化這段關係的價值）
"""
    return {
        "system_prompt": RELATIONSHIP_ECO_SYSTEM_PROMPT,
        "user_prompt": user_prompt
    }


DECISION_SANDBOX_SYSTEM_PROMPT = """你是 Aetheria 的決策沙盒模擬器。你負責推演不同決策路徑的後果。

【核心原則】
1. 不做道德判斷，只做因果推演。
2. 結合「塔羅牌陣」與「命主特質」進行模擬。
3. 明確對比路徑 A 與路徑 B 的「代價」與「收益」。

請用繁體中文回覆，語氣客觀中立。"""


def generate_decision_sandbox_prompt(
    user_name: str,
    question: str,
    option_a: str,
    option_b: str,
    cards_a: str,
    cards_b: str,
    meta_profile: Dict
) -> Dict[str, str]:
    """
    生成決策沙盒模擬 Prompt。
    """
    user_prompt = f"""
【決策者】{user_name}
【Meta Profile】{meta_profile}
【核心問題】{question}

【路徑 A：{option_a}】
塔羅模擬結果：
{cards_a}

【路徑 B：{option_b}】
塔羅模擬結果：
{cards_b}

請進行沙盒推演，輸出格式如下：

### 1) 推演結論（1句）
（哪條路徑符合命主的最大利益？）

### 2) 路徑 A 預演：{option_a}
- 預期發展：
- 隱藏代價：
- 成功機率：

### 3) 路徑 B 預演：{option_b}
- 預期發展：
- 隱藏代價：
- 成功機率：

### 4) 關鍵變數
（影響成敗的核心因素是什麼？）
"""
    return {
        "system_prompt": DECISION_SANDBOX_SYSTEM_PROMPT,
        "user_prompt": user_prompt
    }
