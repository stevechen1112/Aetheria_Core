"""
安全政策與倫理邊界 (Safety Policy)
版本: v1.0.0
最後更新: 2026-02-05
"""

SAFETY_POLICY = {
    "version": "1.0.0",
    "sensitive_topics": {
        "health_medical": {
            "keywords": ["病", "癌", "症狀", "診斷", "治療", "藥", "手術", "疾病", "健康問題"],
            "response": "命盤可以看整體健康趨勢，但具體症狀請務必諮詢專業醫生。命理不能取代醫療診斷。",
            "severity": "high"
        },
        "life_death": {
            "keywords": ["壽命", "活多久", "什麼時候死", "死亡", "陽壽", "大限"],
            "response": "這類問題不在命理能回答的範圍。命理更適合看人生方向和階段性的轉變，而不是預測生死。",
            "severity": "critical"
        },
        "investment_finance": {
            "keywords": ["買股票", "投資", "基金", "期貨", "選擇權", "加密貨幣", "賺多少錢"],
            "response": "財運趨勢可以作為參考，但具體投資決策請諮詢專業理財顧問。命理不能保證投資結果。",
            "severity": "high"
        },
        "legal_lawsuit": {
            "keywords": ["官司", "訴訟", "會不會被告", "法院", "判決", "律師"],
            "response": "法律問題建議諮詢專業律師，命盤只能看大方向的運勢起伏，不能預測具體判決結果。",
            "severity": "high"
        },
        "suicide_selfharm": {
            "keywords": ["自殺", "不想活", "了結", "輕生", "自我傷害", "想死"],
            "response": "我很擔心你現在的狀態。這種時候專業的心理諮詢會更有幫助。台灣自殺防治專線：1925（24小時免費）。請讓專業人員陪伴你度過這段艱難時期。",
            "severity": "critical",
            "requires_intervention": True
        },
        "gambling": {
            "keywords": ["賭", "簽牌", "賭博", "賭場", "下注", "會不會贏"],
            "response": "命理不能用來預測賭博結果。如果賭博已經影響到生活，建議尋求專業協助（戒賭專線：0800-005-880）。",
            "severity": "high"
        }
    },
    "ethical_guidelines": [
        "不做任何形式的生死預測",
        "不診斷或預測疾病",
        "不給具體投資建議或預測股市",
        "不預測訴訟或法律糾紛結果",
        "不鼓勵賭博或投機行為",
        "不過度製造焦慮或恐懼",
        "不建立使用者對命理的過度依賴",
        "遇到自殺/自傷傾向立即轉介專業資源"
    ],
    "dependency_prevention": {
        "excessive_consultation_signals": [
            "每日多次諮詢",
            "決策前必問",
            "焦慮性重複提問相同問題",
            "表達「沒有命理建議就不敢行動」"
        ],
        "intervention_message": "我注意到你最近問了很多類似的問題。命理是一種參考工具，幫助我們了解自己和趨勢，但人生的選擇權永遠在你手上。有時候，給自己一點空間消化，反而能看得更清楚。要不要我們過幾天再聊？",
        "cooldown_suggestion": "建議每次諮詢後至少間隔 24 小時"
    },
    "privacy_protection": {
        "principles": [
            "只收集命理分析必要的資訊",
            "敏感資料加密儲存",
            "不將用戶資料用於訓練或分享第三方",
            "提供資料刪除功能"
        ],
        "pii_detection_patterns": [
            r"\d{10}",  # 可能是身分證號
            r"\d{4}-\d{4}-\d{4}-\d{4}",  # 信用卡號
            r"[A-Z]\d{9}",  # 台灣身分證格式
        ]
    },
    "periodic_reminders": [
        "記得，命理是一種參考工具，幫助我們了解自己和趨勢，但人生的選擇權永遠在你手上。",
        "命盤提供的是可能性，而非必然性。你的行動和選擇會影響最終結果。",
        "我的建議僅供參考，重要決策還是要結合實際情況和專業意見。"
    ]
}


def check_sensitive_topic(text: str) -> dict:
    """
    檢查文本是否涉及敏感話題
    
    Args:
        text: 使用者輸入文本
        
    Returns:
        {
            "is_sensitive": bool,
            "topic": str | None,
            "severity": str | None,
            "response": str | None,
            "requires_intervention": bool
        }
    """
    from src.utils.sensitive_topics import get_sensitive_topic_detector, SensitiveTopic

    if not text:
        return {
            "is_sensitive": False,
            "topic": None,
            "severity": None,
            "response": None,
            "requires_intervention": False
        }

    detector = get_sensitive_topic_detector()
    topic, confidence = detector.detect(text)

    topic_mapping = {
        SensitiveTopic.HEALTH_MEDICAL: "health_medical",
        SensitiveTopic.SUICIDE_DEATH: "suicide_selfharm",
        SensitiveTopic.LEGAL_CRIME: "legal_lawsuit",
        SensitiveTopic.FINANCIAL_INVESTMENT: "investment_finance",
        SensitiveTopic.RELATIONSHIP_VIOLENCE: "relationship_violence"
    }

    if topic != SensitiveTopic.NONE and detector.should_intercept(topic, confidence):
        policy_key = topic_mapping.get(topic)
        if policy_key and policy_key in SAFETY_POLICY["sensitive_topics"]:
            topic_config = SAFETY_POLICY["sensitive_topics"][policy_key]
            return {
                "is_sensitive": True,
                "topic": policy_key,
                "severity": topic_config["severity"],
                "response": topic_config["response"],
                "requires_intervention": topic_config.get("requires_intervention", False)
            }

    text_lower = text.lower()
    for topic_name, topic_config in SAFETY_POLICY["sensitive_topics"].items():
        for keyword in topic_config["keywords"]:
            if keyword in text_lower:
                return {
                    "is_sensitive": True,
                    "topic": topic_name,
                    "severity": topic_config["severity"],
                    "response": topic_config["response"],
                    "requires_intervention": topic_config.get("requires_intervention", False)
                }

    return {
        "is_sensitive": False,
        "topic": None,
        "severity": None,
        "response": None,
        "requires_intervention": False
    }


def get_safety_guidelines() -> list:
    """取得倫理守則清單"""
    return SAFETY_POLICY["ethical_guidelines"]


def should_show_reminder(conversation_length: int) -> str | None:
    """
    判斷是否該顯示週期性提醒
    
    Args:
        conversation_length: 當前對話輪數
        
    Returns:
        提醒訊息或 None
    """
    reminders = SAFETY_POLICY["periodic_reminders"]
    
    # 每 15 輪對話顯示一次提醒
    if conversation_length > 0 and conversation_length % 15 == 0:
        import random
        return random.choice(reminders)
    
    return None
