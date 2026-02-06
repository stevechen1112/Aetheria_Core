"""
對話狀態機與策略管理 (Conversation State Machine & Strategies)
版本: v1.0.0
最後更新: 2026-02-05
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


class ConversationStage(Enum):
    """對話階段"""
    INITIAL_CONTACT = "initial_contact"  # 初次見面
    TRUST_BUILDING = "trust_building"    # 建立信任
    DATA_COLLECTION = "data_collection"  # 資料收集
    DEEP_CONSULTATION = "deep_consultation"  # 深度諮詢
    CONCLUSION = "conclusion"            # 總結收尾


class ConversationStrategy(Enum):
    """對話策略"""
    WARM_WELCOME = "warm_welcome"        # 友善歡迎
    GENTLE_INQUIRY = "gentle_inquiry"    # 溫和詢問
    EMPATHY_FIRST = "empathy_first"      # 同理優先
    DEEP_ANALYSIS = "deep_analysis"      # 深度分析
    CONCISE_ANSWER = "concise_answer"    # 精簡回答
    EXPLORATORY = "exploratory"          # 探索性對話


@dataclass
class UserState:
    """使用者狀態"""
    is_first_visit: bool = True
    has_complete_birth_info: bool = False
    conversation_count: int = 0
    last_interaction_hours: Optional[float] = None
    preferred_communication_style: Optional[str] = None  # 'direct' or 'gentle'
    emotional_state: Optional[str] = None  # 'distress', 'curious', 'skeptical', etc.


STRATEGY_TEMPLATES = {
    ConversationStrategy.WARM_WELCOME: {
        "description": "友善歡迎新使用者",
        "guidelines": [
            "簡短自我介紹",
            "詢問對方想了解什麼",
            "不急著收集生辰資料",
            "語氣輕鬆、不給壓力"
        ],
        "example_opening": "你好，我是 Aetheria！很高興認識你。今天有什麼想聊的嗎？不管是想了解運勢、個性，還是只是好奇命理，我都很樂意跟你聊聊。😊",
        "tone": "friendly, casual"
    },
    
    ConversationStrategy.GENTLE_INQUIRY: {
        "description": "溫和地收集所需資訊",
        "guidelines": [
            "將資料收集融入自然對話",
            "解釋為什麼需要這些資訊",
            "給對方選擇不提供的空間",
            "避免「填表單」的感覺"
        ],
        "example_opening": "如果要幫你看得更準確，我需要知道你的出生年月日和時間。不過如果不方便提供也沒關係，我們可以先聊聊你關心的事。",
        "tone": "gentle, patient, non-pushy"
    },
    
    ConversationStrategy.EMPATHY_FIRST: {
        "description": "優先同理回應，適用於情緒低落或焦慮時",
        "guidelines": [
            "先承認對方的感受",
            "避免立即分析或給建議",
            "用理解性的語言",
            "放慢節奏，留空間讓對方表達"
        ],
        "example_opening": "聽起來最近真的不容易。我理解這種感覺。要不要先跟我聊聊發生了什麼？我會陪著你一起看看有沒有什麼線索或方向。",
        "tone": "warm, supportive, slow-paced"
    },
    
    ConversationStrategy.DEEP_ANALYSIS: {
        "description": "深度解讀命盤，適用於已有完整資料且對方準備好聽",
        "guidelines": [
            "調用工具獲取真實命盤數據",
            "用敘事方式解讀，而非羅列數據",
            "連結命盤與對方的實際處境",
            "給出可行動的洞察"
        ],
        "example_opening": "好，我現在看一下你的命盤。讓我先看看整體格局，然後再聚焦到你關心的部分。",
        "tone": "professional, insightful, narrative"
    },
    
    ConversationStrategy.CONCISE_ANSWER: {
        "description": "精簡回答，適用於對方急躁或要求「直接說」",
        "guidelines": [
            "開門見山，先說結論",
            "減少鋪陳和比喻",
            "用條列或分點",
            "避免過多背景說明"
        ],
        "example_opening": "直接說結論：你的命盤顯示今年事業運不錯，有貴人相助。建議把握 3-5 月的機會期。",
        "tone": "direct, efficient, clear"
    },
    
    ConversationStrategy.EXPLORATORY: {
        "description": "探索性對話，用於了解深層需求",
        "guidelines": [
            "多用開放式問題",
            "鼓勵對方說更多",
            "找出表層問題背後的真正擔憂",
            "不急著給答案"
        ],
        "example_opening": "你提到對工作運有點擔心。可以多說一點嗎？是最近遇到什麼狀況，還是在考慮某個決定？",
        "tone": "curious, open, exploratory"
    }
}


class ConversationStateManager:
    """對話狀態管理器"""
    
    def __init__(self):
        self.current_stage = ConversationStage.INITIAL_CONTACT
        self.current_strategy = ConversationStrategy.WARM_WELCOME
        self.user_state = UserState()
    
    def determine_strategy(
        self, 
        user_state: UserState,
        conversation_history: List[Dict],
        emotional_signal: Optional[Dict] = None
    ) -> ConversationStrategy:
        """
        根據使用者狀態、對話歷史和情緒信號，決定對話策略
        
        Args:
            user_state: 使用者狀態
            conversation_history: 對話歷史
            emotional_signal: 情緒信號 (from EmotionalIntelligence)
            
        Returns:
            ConversationStrategy
        """
        # 情緒優先判斷
        if emotional_signal and emotional_signal.get('distress_level', 0) > 0.7:
            return ConversationStrategy.EMPATHY_FIRST
        
        if emotional_signal and emotional_signal.get('impatient', False):
            return ConversationStrategy.CONCISE_ANSWER
        
        # 根據使用者狀態判斷
        if user_state.is_first_visit:
            return ConversationStrategy.WARM_WELCOME
        
        if user_state.has_complete_birth_info:
            return ConversationStrategy.DEEP_ANALYSIS
        
        # 根據對話歷史判斷
        if len(conversation_history) > 0:
            last_message = conversation_history[-1].get('content', '')
            
            # 偵測探索性需求
            if any(word in last_message for word in ['擔心', '不確定', '考慮', '猶豫']):
                return ConversationStrategy.EXPLORATORY
        
        # 預設：溫和詢問
        return ConversationStrategy.GENTLE_INQUIRY
    
    def update_stage(self, user_state: UserState) -> ConversationStage:
        """
        根據使用者狀態更新對話階段
        
        Args:
            user_state: 使用者狀態
            
        Returns:
            ConversationStage
        """
        if user_state.conversation_count == 0:
            return ConversationStage.INITIAL_CONTACT
        
        if user_state.conversation_count <= 3:
            return ConversationStage.TRUST_BUILDING
        
        if not user_state.has_complete_birth_info:
            return ConversationStage.DATA_COLLECTION
        
        if user_state.conversation_count > 10:
            return ConversationStage.CONCLUSION
        
        return ConversationStage.DEEP_CONSULTATION
    
    def get_strategy_guidance(self, strategy: ConversationStrategy) -> Dict:
        """
        取得特定策略的指引
        
        Args:
            strategy: 對話策略
            
        Returns:
            策略指引 dict
        """
        return STRATEGY_TEMPLATES.get(strategy, {})


def get_strategy_description(strategy: ConversationStrategy) -> str:
    """取得策略描述"""
    template = STRATEGY_TEMPLATES.get(strategy, {})
    return template.get('description', '')


def get_strategy_guidelines(strategy: ConversationStrategy) -> List[str]:
    """取得策略指引"""
    template = STRATEGY_TEMPLATES.get(strategy, {})
    return template.get('guidelines', [])
