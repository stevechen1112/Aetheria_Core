"""
Aetheria 命盤結構提取工具
從 Gemini 3 Pro 的回應中提取結構化的命盤資料
"""

import re
import json
from typing import Dict, List, Optional, Tuple


class ChartExtractor:
    """
    命盤結構提取器
    """
    
    # 十二宮位對照
    PALACES = [
        '命宮', '兄弟宮', '夫妻宮', '子女宮', '財帛宮', '疾厄宮',
        '遷移宮', '奴僕宮', '官祿宮', '田宅宮', '福德宮', '父母宮'
    ]
    
    # 十二地支
    EARTHLY_BRANCHES = [
        '子', '丑', '寅', '卯', '辰', '巳',
        '午', '未', '申', '酉', '戌', '亥'
    ]
    
    # 十四主星
    MAJOR_STARS = [
        '紫微', '天機', '太陽', '武曲', '天同', '廉貞', '天府',
        '太陰', '貪狼', '巨門', '天相', '天梁', '七殺', '破軍'
    ]
    
    # 四化
    TRANSFORMATIONS = ['化祿', '化權', '化科', '化忌']
    
    # 常見格局
    PATTERNS = [
        '機月同梁', '日月並明', '殺破狼', '府相朝垣', '紫府同宮',
        '機梁加會', '巨日同宮', '陽梁昌祿', '明珠出海', '石中隱玉'
    ]
    
    def __init__(self):
        pass
    
    def extract_json_structure(self, llm_response: str) -> Optional[Dict]:
        """
        從 AI 回應中提取 JSON 格式的命盤結構
        
        Args:
            llm_response: AI 的原始回應文字
            
        Returns:
            解析後的 JSON 結構，若無法解析則返回 None
        """
        # 尋找 ```json ... ``` 區塊
        json_pattern = r'```json\s*([\s\S]*?)\s*```'
        match = re.search(json_pattern, llm_response)
        
        if match:
            json_str = match.group(1).strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"JSON 解析錯誤: {e}")
                return None
        return None
    
    def extract_full_structure(self, llm_response: str) -> Dict:
        """
        提取完整命盤結構
        優先使用 JSON 格式，若無則使用正則表達式回退方案
        
        Args:
            llm_response: Gemini 3 Pro 的原始回應文字
            
        Returns:
            結構化的命盤資料
        """
        
        # 優先嘗試提取 JSON 結構
        json_structure = self.extract_json_structure(llm_response)
        
        if json_structure:
            # 使用 JSON 結構，並標準化格式
            structure = {
                '命宮': {
                    '宮位': json_structure.get('命宮', {}).get('地支'),
                    '主星': json_structure.get('命宮', {}).get('主星', []),
                    '輔星': json_structure.get('命宮', {}).get('輔星', []),
                    '四化': None
                },
                '格局': json_structure.get('格局', ['未明確提及']),
                '五行局': json_structure.get('五行局'),
                '十二宮': {},
                '四化': json_structure.get('四化', {}),
                '原始分析': llm_response[:500] + '...' if len(llm_response) > 500 else llm_response,
                '提取方式': 'JSON'
            }
            
            # 轉換十二宮格式
            if '十二宮' in json_structure:
                for palace_name, palace_data in json_structure['十二宮'].items():
                    structure['十二宮'][palace_name] = {
                        '宮位': palace_data.get('地支'),
                        '主星': palace_data.get('主星', []),
                        '四化': None
                    }
            
            return structure
        
        # 回退：使用正則表達式提取（舊方法）
        structure = {
            '命宮': self.extract_life_palace(llm_response),
            '格局': self.extract_patterns(llm_response),
            '五行局': self.extract_element_bureau(llm_response),
            '十二宮': self.extract_twelve_palaces(llm_response),
            '四化': self.extract_transformations(llm_response),
            '原始分析': llm_response[:500] + '...' if len(llm_response) > 500 else llm_response,
            '提取方式': 'Regex'
        }
        
        return structure
    
    def extract_life_palace(self, text: str) -> Dict:
        """
        提取命宮資訊
        
        Returns:
            {
                '宮位': '戌',
                '主星': ['太陰', '天同'],
                '輔星': ['文昌'],
                '四化': None
            }
        """
        result = {
            '宮位': None,
            '主星': [],
            '輔星': [],
            '四化': None
        }
        
        # 尋找命宮段落
        patterns = [
            r'命宮[：:]\s*(?:位於\s*)?[「『]?(\w+)宮?[」』]?',
            r'命宮.*?(\w+)宮',
            r'命宮座落在?\s*[「『]?(\w+)宮?[」』]?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                palace = match.group(1)
                if palace in self.EARTHLY_BRANCHES:
                    result['宮位'] = palace
                    break
        
        # 提取主星（在命宮段落中）
        life_palace_section = self._extract_section(text, '命宮', 300)
        
        for star in self.MAJOR_STARS:
            if star in life_palace_section:
                result['主星'].append(star)
        
        # 提取輔星（簡化：只找文昌文曲左右）
        for aux_star in ['文昌', '文曲', '左輔', '右弼']:
            if aux_star in life_palace_section:
                result['輔星'].append(aux_star)
        
        # 提取四化
        for trans in self.TRANSFORMATIONS:
            if trans in life_palace_section:
                result['四化'] = trans
                break
        
        return result
    
    def extract_patterns(self, text: str) -> List[str]:
        """
        提取格局
        
        Returns:
            ['機月同梁', '日月並明']
        """
        patterns = []
        
        for pattern in self.PATTERNS:
            if pattern in text:
                patterns.append(pattern)
        
        return patterns if patterns else ['未明確提及']
    
    def extract_element_bureau(self, text: str) -> Optional[str]:
        """
        提取五行局
        
        Returns:
            '火六局' or None
        """
        match = re.search(r'(水二局|木三局|金四局|土五局|火六局)', text)
        return match.group(1) if match else None
    
    def extract_twelve_palaces(self, text: str) -> Dict:
        """
        提取十二宮資訊
        
        Returns:
            {
                '命宮': {'宮位': '戌', '主星': ['太陰']},
                '兄弟宮': {'宮位': '酉', '主星': ['武曲', '貪狼']},
                ...
            }
        """
        palaces = {}
        
        for palace_name in self.PALACES:
            section = self._extract_section(text, palace_name, 200)
            
            if not section:
                continue
            
            palace_info = {
                '宮位': None,
                '主星': [],
                '四化': None
            }
            
            # 提取宮位
            for branch in self.EARTHLY_BRANCHES:
                if branch + '宮' in section or f'位於{branch}' in section:
                    palace_info['宮位'] = branch
                    break
            
            # 提取主星
            for star in self.MAJOR_STARS:
                if star in section:
                    palace_info['主星'].append(star)
            
            # 提取四化
            for trans in self.TRANSFORMATIONS:
                if trans in section:
                    palace_info['四化'] = trans
                    break
            
            palaces[palace_name] = palace_info
        
        return palaces
    
    def extract_transformations(self, text: str) -> Dict:
        """
        提取四化資訊
        
        Returns:
            {
                '化祿': '武曲',
                '化權': '貪狼',
                '化科': '天梁',
                '化忌': '文曲'
            }
        """
        transformations = {}
        
        for trans in self.TRANSFORMATIONS:
            # 尋找「XX化祿」模式
            for star in self.MAJOR_STARS + ['文昌', '文曲']:
                pattern = f'{star}{trans}'
                if pattern in text:
                    transformations[trans] = star
                    break
        
        return transformations
    
    def _extract_section(self, text: str, keyword: str, length: int = 200) -> str:
        """
        提取包含關鍵字的段落
        
        Args:
            text: 完整文字
            keyword: 關鍵字（如「命宮」）
            length: 提取長度
            
        Returns:
            段落文字
        """
        index = text.find(keyword)
        if index == -1:
            return ''
        
        start = max(0, index - 50)
        end = min(len(text), index + length)
        return text[start:end]
    
    def validate_structure(self, structure: Dict) -> Tuple[bool, List[str]]:
        """
        驗證結構完整性
        
        Returns:
            (是否有效, 錯誤訊息列表)
        """
        errors = []
        warnings = []
        
        # 檢查提取方式
        extraction_method = structure.get('提取方式', 'Unknown')
        
        # 檢查命宮
        if not structure.get('命宮', {}).get('宮位'):
            errors.append('命宮宮位缺失')
        
        ming_gong_stars = structure.get('命宮', {}).get('主星', [])
        if not ming_gong_stars:
            errors.append('命宮主星缺失')
        elif len(ming_gong_stars) > 3:
            # 紫微斗數規則：每個宮位最多 2-3 顆主星
            errors.append(f'命宮主星數量異常（{len(ming_gong_stars)}顆），可能提取錯誤')
        
        # 檢查五行局
        if not structure.get('五行局'):
            warnings.append('五行局未提取')
        
        # 檢查格局
        if not structure.get('格局') or structure['格局'] == ['未明確提及']:
            warnings.append('格局資訊缺失')
        
        # 檢查十二宮（若使用 JSON 提取則應有完整十二宮）
        twelve_palaces = structure.get('十二宮', {})
        if extraction_method == 'JSON':
            required_palaces = ['命宮', '官祿宮', '財帛宮', '夫妻宮']
            for palace in required_palaces:
                if palace not in twelve_palaces:
                    errors.append(f'{palace}資訊缺失')
                elif len(twelve_palaces[palace].get('主星', [])) > 3:
                    errors.append(f'{palace}主星數量異常')
        else:
            # Regex 提取，只檢查關鍵三宮
            key_palaces = ['官祿宮', '財帛宮', '夫妻宮']
            for palace in key_palaces:
                if palace not in twelve_palaces:
                    warnings.append(f'{palace}資訊缺失')
        
        # 驗證四化（應該有4個）
        si_hua = structure.get('四化', {})
        if extraction_method == 'JSON' and len(si_hua) < 4:
            warnings.append(f'四化不完整（僅有{len(si_hua)}項）')
        
        # 嚴格模式：有錯誤則失敗
        # 寬鬆模式：只有警告也算通過
        is_valid = len(errors) == 0
        
        all_messages = errors + [f'(警告) {w}' for w in warnings]
        
        return is_valid, all_messages
    
    def to_json(self, structure: Dict, indent: int = 2) -> str:
        """
        轉換為 JSON 格式
        """
        return json.dumps(structure, ensure_ascii=False, indent=indent)
    
    def compare_structures(self, struct1: Dict, struct2: Dict) -> Dict:
        """
        比較兩個命盤結構的差異
        
        Returns:
            {
                '相同': ['命宮宮位', '格局'],
                '不同': {
                    '命宮主星': (['太陰'], ['破軍'])
                }
            }
        """
        same = []
        different = {}
        
        # 比較命宮宮位
        if struct1.get('命宮', {}).get('宮位') == struct2.get('命宮', {}).get('宮位'):
            same.append('命宮宮位')
        else:
            different['命宮宮位'] = (
                struct1.get('命宮', {}).get('宮位'),
                struct2.get('命宮', {}).get('宮位')
            )
        
        # 比較命宮主星
        stars1 = set(struct1.get('命宮', {}).get('主星', []))
        stars2 = set(struct2.get('命宮', {}).get('主星', []))
        if stars1 == stars2:
            same.append('命宮主星')
        else:
            different['命宮主星'] = (list(stars1), list(stars2))
        
        # 比較格局
        patterns1 = set(struct1.get('格局', []))
        patterns2 = set(struct2.get('格局', []))
        if patterns1 == patterns2:
            same.append('格局')
        else:
            different['格局'] = (list(patterns1), list(patterns2))
        
        return {
            '相同': same,
            '不同': different
        }


# 使用範例
if __name__ == '__main__':
    # 測試用的 LLM 回應
    sample_response = """
    ### 一、命盤基礎結構
    
    #### 1. 時辰判定
    你出生於 23:58，屬於晚子時，排盤以農曆24日計算。
    
    #### 2. 命宮：位於「戌宮」
    命宮座落在戌宮，主星為天同星、太陰星。文昌星同宮。
    
    #### 3. 核心格局：機月同梁格
    你的命盤屬於「機月同梁」格局，適合公職或專業技術。
    
    #### 4. 關鍵宮位
    
    - 官祿宮（事業）：位於寅宮，天梁化科
    - 財帛宮（財運）：位於午宮，天機
    - 夫妻宮（感情）：位於申宮，太陽巨門
    """
    
    extractor = ChartExtractor()
    structure = extractor.extract_full_structure(sample_response)
    
    print('=== 提取結果 ===')
    print(extractor.to_json(structure))
    
    print('\n=== 驗證結果 ===')
    is_valid, errors = extractor.validate_structure(structure)
    print(f'有效: {is_valid}')
    if errors:
        print('錯誤:')
        for error in errors:
            print(f'  - {error}')
