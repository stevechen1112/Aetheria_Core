"""
塔羅牌計算器 (Tarot Calculator)
Aetheria Core v1.5.0

功能：
- 抽牌邏輯（單張、三張、賽爾特十字等牌陣）
- 正逆位隨機
- 牌義查詢
- 牌陣解讀結構化
"""

import json
import random
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict

# 資料檔案路徑（使用專案根目錄的 data 資料夾）
ROOT_DIR = Path(__file__).parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
TAROT_CARDS_FILE = DATA_DIR / "tarot_cards.json"


@dataclass
class DrawnCard:
    """抽出的牌卡"""
    id: int
    name: str
    name_en: str
    is_reversed: bool  # 是否逆位
    position: str  # 牌陣位置
    position_index: int  # 位置索引


@dataclass
class TarotReading:
    """塔羅牌解讀結果"""
    spread_type: str
    spread_name: str
    question: Optional[str]
    cards: List[DrawnCard]
    timestamp: str
    reading_id: str


class TarotCalculator:
    """塔羅牌計算器"""
    
    def __init__(self):
        """初始化塔羅牌計算器"""
        self.cards_data = self._load_cards_data()
        self.all_cards = self._build_cards_list()
        self.spreads = self.cards_data.get("spreads", {})
    
    def _load_cards_data(self) -> Dict:
        """載入塔羅牌資料"""
        if not TAROT_CARDS_FILE.exists():
            raise FileNotFoundError(f"塔羅牌資料檔案不存在：{TAROT_CARDS_FILE}")
        
        with open(TAROT_CARDS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _build_cards_list(self) -> List[Dict]:
        """建立完整牌卡列表（78張）"""
        cards = []
        
        # 大阿爾克那（22張）
        for card in self.cards_data.get("major_arcana", []):
            card["arcana"] = "major"
            card["suit"] = None
            cards.append(card)
        
        # 小阿爾克那（56張）
        minor = self.cards_data.get("minor_arcana", {})
        for suit_name, suit_data in minor.items():
            for card in suit_data.get("cards", []):
                card["arcana"] = "minor"
                card["suit"] = suit_name
                card["element"] = suit_data.get("element")
                card["suit_meaning"] = suit_data.get("suit_meaning")
                cards.append(card)
        
        return cards
    
    def get_card_by_id(self, card_id: int) -> Optional[Dict]:
        """根據 ID 取得牌卡資料"""
        for card in self.all_cards:
            if card.get("id") == card_id:
                return card
        return None
    
    def get_spread_info(self, spread_type: str) -> Optional[Dict]:
        """取得牌陣資訊"""
        return self.spreads.get(spread_type)
    
    def draw_cards(
        self,
        spread_type: str = "single",
        question: Optional[str] = None,
        allow_reversed: bool = True,
        seed: Optional[int] = None
    ) -> TarotReading:
        """
        抽牌
        
        Args:
            spread_type: 牌陣類型（single, three_card, celtic_cross, relationship, decision）
            question: 問題（可選）
            allow_reversed: 是否允許逆位
            seed: 隨機種子（用於測試）
        
        Returns:
            TarotReading: 解讀結果
        """
        if seed is not None:
            random.seed(seed)
        
        # 取得牌陣資訊
        spread = self.get_spread_info(spread_type)
        if spread is None:
            raise ValueError(f"不支援的牌陣類型：{spread_type}")
        
        positions = spread.get("positions", ["當前指引"])
        num_cards = len(positions)
        
        # 洗牌並抽取
        deck = list(range(78))  # 0-77
        random.shuffle(deck)
        drawn_ids = deck[:num_cards]
        
        # 建立抽牌結果
        cards = []
        for i, card_id in enumerate(drawn_ids):
            card_data = self.get_card_by_id(card_id)
            is_reversed = allow_reversed and random.choice([True, False])
            
            drawn_card = DrawnCard(
                id=card_id,
                name=card_data.get("name", ""),
                name_en=card_data.get("name_en", ""),
                is_reversed=is_reversed,
                position=positions[i],
                position_index=i
            )
            cards.append(drawn_card)
        
        # 生成解讀 ID
        reading_id = f"tarot_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"
        
        return TarotReading(
            spread_type=spread_type,
            spread_name=spread.get("name", spread_type),
            question=question,
            cards=cards,
            timestamp=datetime.now().isoformat(),
            reading_id=reading_id
        )
    
    def get_card_meaning(
        self,
        card_id: int,
        is_reversed: bool = False,
        context: str = "general"
    ) -> Dict:
        """
        取得牌卡解讀
        
        Args:
            card_id: 牌卡 ID
            is_reversed: 是否逆位
            context: 問題情境（general, love, career, finance, health）
        
        Returns:
            牌義詳情
        """
        card = self.get_card_by_id(card_id)
        if card is None:
            return {"error": f"找不到牌卡 ID: {card_id}"}
        
        orientation = "reversed" if is_reversed else "upright"
        meanings = card.get(orientation, {})
        
        return {
            "card_id": card_id,
            "name": card.get("name"),
            "name_en": card.get("name_en"),
            "number": card.get("number"),
            "arcana": card.get("arcana"),
            "suit": card.get("suit"),
            "element": card.get("element"),
            "keywords": card.get("keywords", []),
            "is_reversed": is_reversed,
            "orientation": "逆位" if is_reversed else "正位",
            "meaning": meanings.get(context, meanings.get("general", "")),
            "all_meanings": meanings,
            "symbolism": card.get("symbolism"),
            "archetype": card.get("archetype")
        }
    
    def format_reading_for_prompt(
        self,
        reading: TarotReading,
        context: str = "general"
    ) -> str:
        """
        將解讀結果格式化為 Prompt 輸入
        
        Args:
            reading: 塔羅牌解讀結果
            context: 問題情境
        
        Returns:
            格式化的字串
        """
        lines = []
        lines.append(f"【牌陣】{reading.spread_name}（{reading.spread_type}）")
        
        if reading.question:
            lines.append(f"【問題】{reading.question}")
        
        lines.append("")
        lines.append("【抽到的牌】")
        
        for card in reading.cards:
            card_meaning = self.get_card_meaning(card.id, card.is_reversed, context)
            orientation = "逆位" if card.is_reversed else "正位"
            
            lines.append(f"\n{card.position_index + 1}. {card.position}：{card.name}（{orientation}）")
            lines.append(f"   英文名：{card.name_en}")
            lines.append(f"   關鍵詞：{', '.join(card_meaning.get('keywords', []))}")
            lines.append(f"   牌義：{card_meaning.get('meaning', '')}")
            
            if card_meaning.get("element"):
                lines.append(f"   元素：{card_meaning.get('element')}")
            
            if card_meaning.get("symbolism"):
                lines.append(f"   象徵：{card_meaning.get('symbolism')}")
        
        return "\n".join(lines)
    
    def to_dict(self, reading: TarotReading) -> Dict:
        """將解讀結果轉為字典"""
        result = {
            "reading_id": reading.reading_id,
            "spread_type": reading.spread_type,
            "spread_name": reading.spread_name,
            "question": reading.question,
            "timestamp": reading.timestamp,
            "cards": []
        }
        
        for card in reading.cards:
            card_data = asdict(card)
            card_data["meaning"] = self.get_card_meaning(card.id, card.is_reversed)
            result["cards"].append(card_data)
        
        return result


def main():
    """測試塔羅牌計算器"""
    print("=" * 60)
    print("塔羅牌計算器測試")
    print("=" * 60)
    
    calculator = TarotCalculator()
    
    # 測試 1：單張牌
    print("\n【測試 1】單張牌")
    print("-" * 40)
    reading = calculator.draw_cards(
        spread_type="single",
        question="今天的指引是什麼？",
        seed=42
    )
    print(calculator.format_reading_for_prompt(reading))
    
    # 測試 2：三張牌
    print("\n\n【測試 2】三張牌（過去-現在-未來）")
    print("-" * 40)
    reading = calculator.draw_cards(
        spread_type="three_card",
        question="我的感情發展如何？",
        seed=123
    )
    print(calculator.format_reading_for_prompt(reading, context="love"))
    
    # 測試 3：賽爾特十字
    print("\n\n【測試 3】賽爾特十字")
    print("-" * 40)
    reading = calculator.draw_cards(
        spread_type="celtic_cross",
        question="我該不該換工作？",
        seed=456
    )
    print(calculator.format_reading_for_prompt(reading, context="career"))
    
    # 測試 4：輸出 JSON 格式
    print("\n\n【測試 4】JSON 格式輸出")
    print("-" * 40)
    reading = calculator.draw_cards(spread_type="single", seed=789)
    result = calculator.to_dict(reading)
    print(json.dumps(result, ensure_ascii=False, indent=2)[:1000] + "...")
    
    # 統計資訊
    print("\n\n【統計資訊】")
    print("-" * 40)
    print(f"總牌數：{len(calculator.all_cards)}")
    print(f"大阿爾克那：{len([c for c in calculator.all_cards if c.get('arcana') == 'major'])}")
    print(f"小阿爾克那：{len([c for c in calculator.all_cards if c.get('arcana') == 'minor'])}")
    print(f"支援牌陣：{list(calculator.spreads.keys())}")
    
    print("\n✅ 塔羅牌計算器測試完成！")


if __name__ == "__main__":
    main()
