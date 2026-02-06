"""
情緒感知與同理心系統 (Emotional Intelligence)
版本: v1.0.0
最後更新: 2026-02-05
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import re


@dataclass
class EmotionalSignal:
    """情緒信號"""
    emotion: str  # 'anxiety', 'distress', 'impatient', 'skeptical', 'excited', 'neutral'
    confidence: float  # 0.0 - 1.0
    distress_level: float  # 0.0 - 1.0
    impatient: bool
    keywords_matched: List[str]


class EmotionalIntelligence:
    """情緒感知引擎"""
    
    # 情緒關鍵詞庫
    EMOTION_PATTERNS = {
        "anxiety": {
            "keywords": ["擔心", "怕", "不確定", "焦慮", "緊張", "忐忑", "不安"],
            "weight": 0.8
        },
        "distress": {
            "keywords": ["難過", "痛苦", "沮喪", "絕望", "無助", "崩潰", "撐不下去"],
            "weight": 1.0
        },
        "impatient": {
            "keywords": ["快點", "直接說", "結論", "重點", "別囉嗦", "簡單講"],
            "weight": 0.7
        },
        "skeptical": {
            "keywords": ["真的嗎", "不太信", "算命準嗎", "騙人", "迷信", "懷疑"],
            "weight": 0.6
        },
        "excited": {
            "keywords": ["好期待", "太好了", "很想知道", "超好奇", "開心", "興奮"],
            "weight": 0.5
        }
    }
    
    @classmethod
    def detect_emotion(cls, text: str) -> EmotionalSignal:
        """
        偵測文本中的情緒信號
        
        Args:
            text: 使用者輸入文本
            
        Returns:
            EmotionalSignal
        """
        text_lower = text.lower()
        emotion_scores = {}
        matched_keywords = []
        
        # 計算各情緒得分
        for emotion, config in cls.EMOTION_PATTERNS.items():
            score = 0.0
            for keyword in config["keywords"]:
                if keyword in text_lower:
                    score += config["weight"]
                    matched_keywords.append(keyword)
            emotion_scores[emotion] = score
        
        # 找出最高分情緒
        if not emotion_scores or max(emotion_scores.values()) == 0:
            return EmotionalSignal(
                emotion="neutral",
                confidence=1.0,
                distress_level=0.0,
                impatient=False,
                keywords_matched=[]
            )
        
        dominant_emotion = max(emotion_scores, key=emotion_scores.get)
        confidence = min(emotion_scores[dominant_emotion], 1.0)
        
        # 計算痛苦程度
        distress_level = (
            emotion_scores.get('distress', 0) * 1.0 + 
            emotion_scores.get('anxiety', 0) * 0.5
        ) / 1.5
        distress_level = min(distress_level, 1.0)
        
        return EmotionalSignal(
            emotion=dominant_emotion,
            confidence=confidence,
            distress_level=distress_level,
            impatient=emotion_scores.get('impatient', 0) > 0.5,
            keywords_matched=matched_keywords
        )
    
    @classmethod
    def analyze_message_style(cls, text: str) -> Dict:
        """
        分析訊息風格
        
        Args:
            text: 使用者輸入文本
            
        Returns:
            {
                "is_short": bool,  # 短句（少於 20 字）
                "is_question": bool,  # 是問句
                "is_command": bool,  # 是命令式
                "has_negative_words": bool,  # 有負面詞彙
                "sentence_count": int
            }
        """
        is_short = len(text) < 20
        is_question = '?' in text or '？' in text or any(
            word in text for word in ['嗎', '呢', '吧', '如何', '怎麼', '什麼']
        )
        is_command = any(word in text for word in ['快', '趕快', '立刻', '馬上', '直接'])
        
        negative_words = ['不', '沒', '別', '不要', '不好', '糟', '差', '難']
        has_negative_words = any(word in text for word in negative_words)
        
        # 簡單句子計數（以句號、問號、驚嘆號分隔）
        sentence_count = len(re.split(r'[。！？.!?]', text)) - 1
        if sentence_count == 0:
            sentence_count = 1
        
        return {
            "is_short": is_short,
            "is_question": is_question,
            "is_command": is_command,
            "has_negative_words": has_negative_words,
            "sentence_count": sentence_count
        }


EMOTIONAL_RESPONSES = {
    "anxiety": {
        "acknowledgment": [
            "我理解你的擔心。",
            "聽起來你對這個滿在意的。",
            "這種不確定感確實不好受。"
        ],
        "approach": [
            "我們一起來看看有沒有什麼線索。",
            "讓我幫你理清楚狀況。",
            "也許命盤能給你一些方向。"
        ],
        "tone_adjustment": "放慢節奏，先給安慰再分析"
    },
    
    "distress": {
        "acknowledgment": [
            "聽起來最近真的不容易。",
            "我能感受到你現在的壓力。",
            "辛苦你了，這段時間一定很難熬。"
        ],
        "approach": [
            "要不要先跟我聊聊發生了什麼？",
            "我會陪著你一起看看有沒有什麼可以做的。",
            "我們慢慢來，不急。"
        ],
        "tone_adjustment": "溫暖、支持性、避免說教"
    },
    
    "impatient": {
        "acknowledgment": [
            "好的，我直接說重點。",
            "了解，我不繞圈子。",
            "沒問題，簡單講。"
        ],
        "approach": [
            "結論是...",
            "最重要的是...",
            "建議..."
        ],
        "tone_adjustment": "精簡、直接、減少鋪陳"
    },
    
    "skeptical": {
        "acknowledgment": [
            "我理解你的疑慮。",
            "對命理保持懷疑是正常的。",
            "這個問題很好。"
        ],
        "approach": [
            "我的角色是提供參考，而不是給你絕對答案。",
            "命理是一種工具，幫助我們理解趨勢，但不是定論。",
            "你可以把我說的當作一個角度，最終還是要結合實際情況判斷。"
        ],
        "tone_adjustment": "謙遜、理性、不辯駁"
    },
    
    "excited": {
        "acknowledgment": [
            "你的好奇心我很喜歡！",
            "很高興你這麼有興趣。",
            "你的熱情感染到我了。"
        ],
        "approach": [
            "那我們來好好聊聊。",
            "我可以跟你分享很多有趣的細節。",
            "這部分有很多可以探討的。"
        ],
        "tone_adjustment": "活潑、可以多分享細節"
    },
    
    "neutral": {
        "acknowledgment": [
            "好的。",
            "我明白了。",
            "嗯嗯。"
        ],
        "approach": [
            "讓我看看...",
            "我們來討論一下...",
            "這個問題我們可以這樣看..."
        ],
        "tone_adjustment": "正常節奏"
    }
}


def get_emotional_response_template(emotion: str) -> Dict:
    """
    取得特定情緒的回應模板
    
    Args:
        emotion: 情緒類型
        
    Returns:
        回應模板 dict
    """
    return EMOTIONAL_RESPONSES.get(emotion, EMOTIONAL_RESPONSES["neutral"])


def should_prioritize_empathy(emotional_signal: EmotionalSignal) -> bool:
    """
    判斷是否應優先使用同理心回應
    
    Args:
        emotional_signal: 情緒信號
        
    Returns:
        True 如果應該優先同理
    """
    return (
        emotional_signal.emotion in ["distress", "anxiety"] and 
        emotional_signal.confidence > 0.6
    ) or emotional_signal.distress_level > 0.7
