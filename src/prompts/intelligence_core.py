"""
AI 智慧核心 (AI Intelligence Core)
整合人設、安全政策、對話策略、情緒感知

版本: v1.0.0
最後更新: 2026-02-05
"""

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
        include_strategy_hints: bool = True
    ) -> str:
        """
        建構增強的 System Prompt
        
        Args:
            intelligence_context: 智慧上下文
            include_strategy_hints: 是否包含策略提示
            
        Returns:
            完整的 System Prompt
        """
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
