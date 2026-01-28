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
    
    # 已知的命宮雙星組合（紫微斗數規則）
    # 這些星曜在特定條件下必定同宮
    KNOWN_PAIRS = {
        '天同': ['太陰'],      # 天同太陰同宮（特定宮位）
        '太陰': ['天同'],      # 反向對應
        '紫微': ['天府'],      # 紫府同宮（特定宮位）
        '天府': ['紫微'],
        '武曲': ['天相', '貪狼', '七殺', '破軍'],  # 武曲可能的同宮星
        '太陽': ['太陰', '巨門'],  # 太陽可能的同宮星
    }
    
    def __init__(self):
        self.validation_warnings = []
    
    def validate_palace_stars(self, palace_name: str, stars: List[str], earthly_branch: str) -> Tuple[List[str], List[str]]:
        """
        驗證宮位主星的完整性
        
        Args:
            palace_name: 宮位名稱（如 '命宮'）
            stars: 提取到的主星列表
            earthly_branch: 地支（如 '戌'）
            
        Returns:
            (validated_stars, warnings): 驗證後的星曜列表和警告訊息
        """
        warnings = []
        validated_stars = list(stars)
        
        # 規則 1: 天同在戌宮必有太陰同宮
        if '天同' in validated_stars and earthly_branch == '戌':
            if '太陰' not in validated_stars:
                warnings.append(f"警告：{palace_name}({earthly_branch}宮)有天同但缺少太陰，已自動補充")
                validated_stars.append('太陰')
        
        # 規則 2: 太陰在戌宮必有天同同宮
        if '太陰' in validated_stars and earthly_branch == '戌':
            if '天同' not in validated_stars:
                warnings.append(f"警告：{palace_name}({earthly_branch}宮)有太陰但缺少天同，已自動補充")
                validated_stars.append('天同')
        
        # 規則 3: 天同在酉宮也可能有太陰（視命盤而定）
        # 這裡不強制補充，只記錄可能的遺漏
        
        return validated_stars, warnings
    
    def extract_json_structure(self, llm_response: str) -> Optional[Dict]:
        """
        從 AI 回應中提取 JSON 格式的命盤結構
        
        Args:
            llm_response: AI 的原始回應文字
            
        Returns:
            解析後的 JSON 結構，若無法解析則返回 None
        """
        # 1) 尋找 ```json ... ``` 區塊
        json_pattern = r'```json\s*([\s\S]*?)\s*```'
        match = re.search(json_pattern, llm_response)
        if match:
            json_str = match.group(1).strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"JSON 解析錯誤: {e}")

        # 2) 尋找「【結構化命盤資料】」後的 JSON（無 code fence）
        marker = '【結構化命盤資料】'
        marker_index = llm_response.find(marker)
        search_text = llm_response[marker_index + len(marker):] if marker_index != -1 else llm_response
        brace_index = search_text.find('{')
        if brace_index != -1:
            json_candidate = self._extract_brace_block(search_text[brace_index:])
            if json_candidate:
                try:
                    return json.loads(json_candidate)
                except json.JSONDecodeError as e:
                    print(f"JSON 解析錯誤: {e}")

        return None

    def _extract_brace_block(self, text: str) -> Optional[str]:
        """
        從文字中擷取第一個完整的 JSON 大括號區塊
        """
        depth = 0
        in_string = False
        escape = False
        start_index = None

        for i, ch in enumerate(text):
            if ch == '"' and not escape:
                in_string = not in_string
            if ch == '\\' and not escape:
                escape = True
                continue
            escape = False

            if in_string:
                continue

            if ch == '{':
                if depth == 0:
                    start_index = i
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0 and start_index is not None:
                    return text[start_index:i + 1].strip()

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
        self.validation_warnings = []  # 重置警告
        
        # 優先嘗試提取 JSON 結構
        json_structure = self.extract_json_structure(llm_response)
        
        if json_structure:
            # 取得命宮資訊
            ming_gong = json_structure.get('命宮', {})
            ming_branch = ming_gong.get('地支')
            ming_stars = ming_gong.get('主星', [])
            
            # 驗證命宮主星完整性
            validated_ming_stars, ming_warnings = self.validate_palace_stars(
                '命宮', ming_stars, ming_branch
            )
            self.validation_warnings.extend(ming_warnings)
            
            # 使用 JSON 結構，並標準化格式
            structure = {
                '命宮': {
                    '宮位': ming_branch,
                    '主星': validated_ming_stars,  # 使用驗證後的星曜
                    '輔星': ming_gong.get('輔星', []),
                    '四化': None
                },
                '格局': json_structure.get('格局', ['未明確提及']),
                '五行局': json_structure.get('五行局'),
                '十二宮': {},
                '四化': json_structure.get('四化', {}),
                '原始分析': llm_response[:500] + '...' if len(llm_response) > 500 else llm_response,
                '提取方式': 'JSON',
                '驗證警告': self.validation_warnings if self.validation_warnings else None
            }
            
            # 轉換十二宮格式，並驗證每個宮位
            if '十二宮' in json_structure:
                for palace_name, palace_data in json_structure['十二宮'].items():
                    palace_branch = palace_data.get('地支')
                    palace_stars = palace_data.get('主星', [])
                    
                    # 驗證該宮位的主星
                    validated_stars, warnings = self.validate_palace_stars(
                        palace_name, palace_stars, palace_branch
                    )
                    self.validation_warnings.extend(warnings)
                    
                    structure['十二宮'][palace_name] = {
                        '宮位': palace_branch,
                        '主星': validated_stars,  # 使用驗證後的星曜
                        '輔星': palace_data.get('輔星', []),
                        '四化': None
                    }
            
            # 更新驗證警告
            structure['驗證警告'] = self.validation_warnings if self.validation_warnings else None

            # 補齊十二宮
            structure = self.ensure_complete_twelve_palaces(structure)
            
            return structure
        
        # 回退：使用正則表達式提取（舊方法）
        structure = {
            '命宮': self.extract_life_palace(llm_response),
            '格局': self.extract_patterns(llm_response),
            '五行局': self.extract_element_bureau(llm_response),
            '十二宮': self.extract_twelve_palaces(llm_response),
            '四化': self.extract_transformations(llm_response),
            '原始分析': llm_response[:500] + '...' if len(llm_response) > 500 else llm_response,
            '提取方式': 'Regex',
            '驗證警告': None
        }
        
        # 對 Regex 提取的結果也進行驗證
        ming_gong = structure['命宮']
        if ming_gong.get('宮位') and ming_gong.get('主星'):
            validated_stars, warnings = self.validate_palace_stars(
                '命宮', ming_gong['主星'], ming_gong['宮位']
            )
            structure['命宮']['主星'] = validated_stars
            structure['驗證警告'] = warnings if warnings else None

        # 補齊十二宮
        structure = self.ensure_complete_twelve_palaces(structure)
        
        return structure

    def ensure_complete_twelve_palaces(self, structure: Dict) -> Dict:
        """
        補齊十二宮資料，確保所有宮位都有基本結構
        """
        if '十二宮' not in structure or not isinstance(structure['十二宮'], dict):
            structure['十二宮'] = {}

        for palace_name in self.PALACES:
            if palace_name not in structure['十二宮']:
                structure['十二宮'][palace_name] = {
                    '宮位': None,
                    '主星': [],
                    '輔星': [],
                    '四化': None
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
    你出生於 23:58，屬於晚子時。依本系統規則採「日不進位、時歸子時」（23:00-00:00 仍算當日）。
    
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
