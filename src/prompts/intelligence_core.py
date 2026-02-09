"""
AI 智慧核心 (AI Intelligence Core)
整合人設、安全政策、對話策略、情緒感知、記憶格式化、離題偵測

版本: v1.1.0
最後更新: 2026-02-08
"""

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

from .registry.persona import get_persona_system_prompt
from .registry.safety_policy import check_sensitive_topic, should_show_reminder
from .registry.conversation_strategies import (
    ConversationStrategy, 
    ConversationStateManager,
    UserState
)
from .registry.emotional_intelligence import (
    EmotionalIntelligence,
    EmotionalSignal,
    get_emotional_response_template,
    should_prioritize_empathy
)

from src.utils.logger import get_logger

logger = get_logger()


@dataclass
class IntelligenceContext:
    """智慧核心上下文"""
    user_state: UserState
    emotional_signal: EmotionalSignal
    recommended_strategy: ConversationStrategy
    safety_check: Dict
    should_show_reminder: bool
    strategy_guidance: Dict


class AIIntelligenceCore:
    """
    AI 智慧核心
    
    負責：
    1. 分析使用者輸入（情緒、意圖、風格）
    2. 決定對話策略
    3. 檢查安全邊界
    4. 生成增強的 System Prompt
    """
    
    def __init__(self):
        self.conversation_manager = ConversationStateManager()
        self.emotional_intelligence = EmotionalIntelligence()
    
    def analyze_user_input(
        self,
        user_message: str,
        user_state: UserState,
        conversation_history: List[Dict]
    ) -> IntelligenceContext:
        """
        分析使用者輸入，返回智慧上下文
        
        Args:
            user_message: 使用者訊息
            user_state: 使用者狀態
            conversation_history: 對話歷史
            
        Returns:
            IntelligenceContext
        """
        # 1. 情緒感知
        emotional_signal = self.emotional_intelligence.detect_emotion(user_message)
        
        logger.info(f"情緒偵測: {emotional_signal.emotion} (信心度: {emotional_signal.confidence:.2f})")
        
        # 2. 安全檢查
        safety_check = check_sensitive_topic(user_message)
        
        if safety_check['is_sensitive']:
            logger.warning(f"敏感話題偵測: {safety_check['topic']} (嚴重度: {safety_check['severity']})")
        
        # 3. 決定對話策略
        recommended_strategy = self.conversation_manager.determine_strategy(
            user_state=user_state,
            conversation_history=conversation_history,
            emotional_signal=asdict(emotional_signal)
        )
        
        logger.info(f"推薦策略: {recommended_strategy.value}")
        
        # 4. 取得策略指引
        strategy_guidance = self.conversation_manager.get_strategy_guidance(recommended_strategy)
        
        # 5. 檢查是否需要顯示提醒
        should_remind = should_show_reminder(len(conversation_history))
        
        return IntelligenceContext(
            user_state=user_state,
            emotional_signal=emotional_signal,
            recommended_strategy=recommended_strategy,
            safety_check=safety_check,
            should_show_reminder=should_remind is not None,
            strategy_guidance=strategy_guidance
        )
    
    def build_enhanced_system_prompt(
        self,
        intelligence_context: IntelligenceContext,
        include_strategy_hints: bool = True,
        base_prompt: Optional[str] = None
    ) -> str:
        """
        建構增強的 System Prompt
        
        Args:
            intelligence_context: 智慧上下文
            include_strategy_hints: 是否包含策略提示
            base_prompt: 自訂的基礎 prompt（若未提供則使用 persona registry）
            
        Returns:
            完整的 System Prompt
        """
        # Fix A: 支援使用 agent_persona 作為 base_prompt
        if base_prompt is None:
            base_prompt = get_persona_system_prompt()
        
        # 如果沒有特殊情境，直接返回基礎 prompt
        if not include_strategy_hints:
            return base_prompt
        
        # 建構策略提示
        strategy_hints = []
        
        # 情緒提示
        if intelligence_context.emotional_signal.emotion != "neutral":
            emotion = intelligence_context.emotional_signal.emotion
            response_template = get_emotional_response_template(emotion)
            
            strategy_hints.append(f"""
【當前情境提示】
使用者情緒狀態: {emotion} (信心度: {intelligence_context.emotional_signal.confidence:.1f})
建議語氣調整: {response_template.get('tone_adjustment', '正常')}
""")
        
        # 策略提示
        strategy_guidance = intelligence_context.strategy_guidance
        if strategy_guidance:
            guidelines = strategy_guidance.get('guidelines', [])
            if guidelines:
                strategy_hints.append(f"""
【推薦對話策略】
策略: {strategy_guidance.get('description', '')}
指引:
{chr(10).join(f'• {g}' for g in guidelines)}
""")
        
        # 安全警告
        if intelligence_context.safety_check.get('is_sensitive'):
            strategy_hints.append(f"""
【⚠️ 安全提示】
偵測到敏感話題: {intelligence_context.safety_check['topic']}
請使用以下回應模板:
「{intelligence_context.safety_check['response']}」

並遵守倫理原則，不做超出命理範疇的預測。
""")
        
        # 組合完整 prompt
        if strategy_hints:
            enhanced_prompt = base_prompt + "\n\n" + "\n".join(strategy_hints)
        else:
            enhanced_prompt = base_prompt
        
        return enhanced_prompt
    
    def should_block_response(self, intelligence_context: IntelligenceContext) -> Tuple[bool, Optional[str]]:
        """
        判斷是否應該阻擋回應（例如自殺風險）
        
        Args:
            intelligence_context: 智慧上下文
            
        Returns:
            (should_block: bool, override_response: str | None)
        """
        safety_check = intelligence_context.safety_check
        
        if safety_check.get('requires_intervention'):
            # 自殺/自傷風險 - 立即介入
            return True, safety_check['response']
        
        return False, None
    
    def extract_user_insights(self, conversation_history: List[Dict]) -> List[str]:
        """
        從對話歷史中提取使用者洞察
        
        Args:
            conversation_history: 對話歷史
            
        Returns:
            洞察標籤列表
        """
        insights = []
        
        # 簡單啟發式規則（未來可用 AI 優化）
        for turn in conversation_history:
            if turn.get('role') == 'user':
                content = turn.get('content', '').lower()
                
                # 關注議題偵測
                if any(word in content for word in ['工作', '事業', '職業', '公司']):
                    insights.append('關注事業發展')
                
                if any(word in content for word in ['感情', '愛情', '對象', '結婚', '分手']):
                    insights.append('關注感情議題')
                
                if any(word in content for word in ['健康', '身體', '病']):
                    insights.append('關注健康議題')
                
                # 溝通風格偵測
                if any(word in content for word in ['快點', '直接說', '簡單講']):
                    insights.append('偏好直接溝通')
                
                if len(content) > 100:
                    insights.append('善於表達，喜歡詳細說明')
        
        # 去重
        return list(set(insights))


# 全局實例（單例模式）
_intelligence_core_instance = None

def get_intelligence_core() -> AIIntelligenceCore:
    """取得 AI 智慧核心實例（單例）"""
    global _intelligence_core_instance
    if _intelligence_core_instance is None:
        _intelligence_core_instance = AIIntelligenceCore()
    return _intelligence_core_instance


# ==================== 共用記憶格式化（Gap 4 修復）====================

def format_memory_context(memory_context: Dict, max_length: int = 1200) -> str:
    """
    將三層記憶 dict 格式化成人類可讀的提示文字。
    
    此函式統一了串流與非串流端點的記憶注入格式，
    確保 Gemini 收到結構化、好理解的記憶內容。
    
    Args:
        memory_context: MemoryManager.build_context_for_ai() 的回傳值
        max_length: 最大輸出字元數（超過則截斷）
    
    Returns:
        格式化的記憶提示文字
    """
    if not memory_context:
        return "（無歷史記憶）"
    
    hints: List[str] = []
    
    # Layer 1: 短期記憶 — 檢查系統事件
    short_term = memory_context.get('short_term', [])
    system_events = [m for m in short_term if m.get('role') == 'system_event']
    if system_events:
        hints.append("【系統事件】")
        for evt in system_events[-3:]:
            try:
                evt_data = json.loads(evt.get('content', '{}'))
                evt_type = evt_data.get('type', 'unknown')
                hints.append(f"- {evt_type}: {evt_data.get('data', {})}")
            except Exception:
                pass
    
    # Layer 2: 摘要記憶 — 過往重要討論
    episodic_summaries = memory_context.get('episodic', [])
    if episodic_summaries:
        hints.append("\n【過往討論摘要】")
        for summary in episodic_summaries[:3]:
            topic = summary.get('topic', 'general')
            key_points = summary.get('key_points', '')
            summary_date = summary.get('summary_date', '')
            date_prefix = f"({summary_date}) " if summary_date else ""
            hints.append(f"- {date_prefix}[{topic}] {key_points}")
    
    # Layer 3: 使用者畫像 — 深層特質
    persona = memory_context.get('persona')
    if persona:
        tags = persona.get('personality_tags', [])
        prefs = persona.get('preferences', {})
        if tags or prefs:
            hints.append("\n【使用者特質】")
            if tags:
                normalized_tags = []
                for t in tags[:5]:
                    if isinstance(t, str):
                        normalized_tags.append(t)
                    elif isinstance(t, dict):
                        label = t.get('content') or t.get('tag') or t.get('label')
                        if label:
                            normalized_tags.append(str(label))
                if normalized_tags:
                    hints.append(f"- 性格標籤: {', '.join(normalized_tags)}")
            if prefs:
                tone = prefs.get('tone')
                if tone:
                    hints.append(f"- 偏好語氣: {tone}")
                topics = prefs.get('topics')
                if topics and isinstance(topics, list):
                    hints.append(f"- 關注議題: {', '.join(topics[:5])}")
    
    text = "\n".join(hints) if hints else "（無歷史記憶）"
    if len(text) > max_length:
        text = text[:max_length] + "...（已截斷）"
    return text


# ==================== 離題偵測與引導（Gap 5 修復）====================

# 命理相關關鍵詞（廣義）
_FORTUNE_KEYWORDS = [
    # 命理系統
    "紫微", "八字", "占星", "星盤", "塔羅", "靈數", "姓名學", "命盤", "排盤",
    # 運勢議題
    "運勢", "流年", "流月", "大運", "命運", "命格", "格局", "吉凶",
    # 生活議題（命理可以回應的）
    "事業", "工作", "感情", "愛情", "婚姻", "健康", "財運", "人際", "學業",
    "轉職", "創業", "投資", "桃花", "結婚", "離婚", "考試",
    # 命理諮詢慣用語
    "幫我看", "算一下", "怎麼樣", "適不適合", "會不會", "有沒有機會",
    "什麼時候", "好不好", "該不該", "能不能",
    # 情緒/生活（命理師可以回應的範圍）
    "迷惘", "困惑", "煩惱", "不安", "擔心", "焦慮", "壓力",
    # 出生資訊
    "出生", "生日", "生辰", "時辰", "農曆", "國曆",
]

# 明確離題的關鍵詞
_OFF_TOPIC_KEYWORDS = [
    "寫程式", "coding", "python", "javascript", "程式碼", "debug",
    "食譜", "怎麼煮", "料理", "菜單",
    "翻譯", "translate", "幫我翻",
    "數學題", "方程式", "微積分",
    "寫文章", "寫作業", "幫我寫報告",
    "天氣", "幾度", "會下雨嗎",
    "電影", "影集", "推薦一部", "好看的劇", "音樂", "歌曲",
    "新聞", "股票", "比特幣", "匯率",
]


# 用戶回答/回應型訊息的模式（不應算離題）
_REPLY_PATTERNS = [
    # 短回答
    "好", "好的", "嗯", "嗯嗯", "ok", "可以", "沒問題", "對", "是", "不是",
    "謝謝", "掰掰", "再見", "了解", "知道了", "明白",
    # 回答 AI 提問
    "準備好了", "開始", "請開始", "繼續", "請繼續", "沒問題",
    # 否定/不理解
    "不懂", "不太懂", "不了解", "不知道", "不確定", "不清楚",
    # 提供個人資訊（回答 AI 詢問）
    "男", "女", "男性", "女性",
]


def _is_answering_ai_question(message: str, history_msgs: List[Dict]) -> bool:
    """判斷用戶是否在回答 AI 的問題（而非主動離題）"""
    if not history_msgs:
        return False
    
    # 找到最近的 AI 訊息
    last_ai_msg = None
    for m in reversed(history_msgs):
        if m.get('role') == 'assistant':
            last_ai_msg = m.get('content', '')
            break
    
    if not last_ai_msg:
        return False
    
    # 如果 AI 的上一條訊息以問句結尾，用戶的回覆就是在回答問題
    ai_lower = last_ai_msg.strip()
    if ai_lower.endswith('？') or ai_lower.endswith('?'):
        return True
    
    # 如果 AI 訊息包含「請問」「可以告訴我」「方便提供」等詢問語句
    ask_patterns = [
        '請問', '可以告訴', '方便提供', '方便告訴', '你覺得', '你認為',
        '想請問', '可以分享', '要不要', '準備好', '有沒有', '是否',
    ]
    if any(p in ai_lower for p in ask_patterns):
        return True
    
    return False


def _message_contains_personal_info(message: str) -> bool:
    """判斷訊息是否包含個人資訊（如生辰、姓名、個性描述等）"""
    personal_patterns = [
        # 年份（出生年）
        r'19[5-9]\d|200[0-9]|201[0-9]|202[0-6]',
        # 時間
        r'\d{1,2}[：:]\d{2}',
        # 地點
        '台灣', '台北', '台中', '高雄', '彰化', '新竹', '嘉義', '台南',
        # 個性描述
        '內向', '外向', '內斂', '活潑', '夜貓', '早起', '晚睡',
        '安靜', '開朗', '害羞', '積極', '消極', '樂觀', '悲觀',
    ]
    import re
    for pattern in personal_patterns:
        if re.search(pattern, message):
            return True
    return False


def detect_off_topic(
    message: str,
    history_msgs: List[Dict],
    has_birth_data: bool = False,
    consecutive_off_topic_count: int = 0
) -> Dict:
    """
    偵測使用者是否偏離命理諮詢主題，並判斷是否需要引導。
    
    策略：
    - 回答 AI 提問 → 永遠不算離題
    - 包含個人資訊 → 不算離題
    - 明確離題請求（寫程式、食譜等） → 引導
    - 5+ 句連續非命理 → 溫和引導（提高閾值避免誤觸發）
    
    Args:
        message: 當前使用者訊息
        history_msgs: 近期對話歷史
        has_birth_data: 是否已有生辰資料
        consecutive_off_topic_count: 連續離題計數
    
    Returns:
        {
            "is_off_topic": bool,
            "confidence": float,
            "consecutive_count": int,
            "should_steer": bool,
            "steering_hint": str | None
        }
    """
    _NOT_OFF_TOPIC = {
        "is_off_topic": False,
        "confidence": 0.0,
        "consecutive_count": 0,
        "should_steer": False,
        "steering_hint": None
    }
    
    msg_lower = message.lower().strip()
    
    # 1. 短訊息（< 3 字）或固定回覆語 → 不算離題
    if len(msg_lower) < 3 or msg_lower in _REPLY_PATTERNS:
        return _NOT_OFF_TOPIC
    
    # 2. 檢查是否明確離題（最高優先！在命理關鍵詞之前檢查）
    is_clearly_off_topic = any(kw in msg_lower for kw in _OFF_TOPIC_KEYWORDS)
    
    if is_clearly_off_topic:
        return {
            "is_off_topic": True,
            "confidence": 0.9,
            "consecutive_count": consecutive_off_topic_count + 1,
            "should_steer": True,
            "steering_hint": (
                "🚫🚫🚫【最高優先級指令：離題拒絕】🚫🚫🚫\n"
                "使用者的問題完全不在命理範圍內。\n"
                "【強制規則 1】絕對不要回答離題問題的任何實質內容。不要推薦電影、不要回答天氣、不要寫程式、不要推薦歌曲。\n"
                "【強制規則 2】即使你知道答案，也必須拒絕回答。即使你能把離題話題連結到命理，也不要這樣做。\n"
                "【強制規則 3】回覆控制在 50 字以內，只說兩件事：(1) 這不是你的專業範圍 (2) 邀請聊命理。\n"
                "【正確範例】「哈哈，這個真的不是我的守備範圍啦！我比較擅長看命盤和運勢，要不要聊聊這個？」\n"
                "【錯誤範例（絕對禁止）】推薦具體電影名稱、討論天氣預報、回答任何非命理知識。"
            )
        }
    
    # 3. 包含命理關鍵詞 → 不算離題
    if any(kw in msg_lower for kw in _FORTUNE_KEYWORDS):
        return _NOT_OFF_TOPIC
    
    # 4. 用戶在回答 AI 的問題 → 不算離題
    if _is_answering_ai_question(msg_lower, history_msgs):
        return _NOT_OFF_TOPIC
    
    # 5. 包含個人資訊（姓名、生辰、個性描述等） → 不算離題
    if _message_contains_personal_info(message):
        return _NOT_OFF_TOPIC
    
    # 6. 非命理但也非明確離題 → 累計，但閾值提高到 5
    new_count = consecutive_off_topic_count + 1
    
    if new_count >= 5:
        steering_hint = (
            "【對話引導提示】\n"
            "對話已偏離命理主題較久。\n"
            "請自然地引導：「對了，我們聊了很多，要不要回來看看"
            "命理方面有什麼可以幫你的？」"
        )
        return {
            "is_off_topic": True,
            "confidence": 0.6,
            "consecutive_count": new_count,
            "should_steer": True,
            "steering_hint": steering_hint
        }
    
    # 未達閾值 → 不干預
    return {
        "is_off_topic": False,
        "confidence": 0.3,
        "consecutive_count": new_count,
        "should_steer": False,
        "steering_hint": None
    }
