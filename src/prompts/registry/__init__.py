"""
Prompt Registry - 統一管理所有 AI Prompt 與策略
支援版本控制、回滾、A/B 測試
"""

from .persona import AETHERIA_PERSONA
from .safety_policy import SAFETY_POLICY
from .conversation_strategies import ConversationStrategy, STRATEGY_TEMPLATES
from .emotional_intelligence import EmotionalIntelligence, EMOTIONAL_RESPONSES

__all__ = [
    'AETHERIA_PERSONA',
    'SAFETY_POLICY',
    'ConversationStrategy',
    'STRATEGY_TEMPLATES',
    'EmotionalIntelligence',
    'EMOTIONAL_RESPONSES'
]
