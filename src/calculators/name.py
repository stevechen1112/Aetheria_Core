"""
姓名學計算器 - 五格剖象法
Aetheria Core v1.7.0

功能：
1. 五格計算（天格、人格、地格、外格、總格）
2. 81 數理吉凶判斷
3. 三才配置分析
4. 與八字喜用神整合建議
"""

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import unicodedata


@dataclass
class FiveGrids:
    """五格數據"""
    天格: int
    人格: int
    地格: int
    外格: int
    總格: int


@dataclass
class GridAnalysis:
    """單一格的分析結果"""
    name: str
    number: int
    element: str
    fortune: str
    number_name: str
    description: str
    keywords: List[str]


@dataclass
class NameAnalysis:
    """姓名分析完整結果"""
    surname: str
    given_name: str
    full_name: str
    surname_strokes: List[int]
    given_name_strokes: List[int]
    total_strokes: int
    five_grids: FiveGrids
    grid_analyses: Dict[str, GridAnalysis]
    three_talents: Dict
    overall_fortune: str
    recommendations: List[str]


class NameCalculator:
    """姓名學計算器"""
    
    # 康熙字典特殊筆畫對照（部首特殊計算）
    KANGXI_SPECIAL = {
        # 水部
        '氵': 4, '水': 4,
        # 火部  
        '灬': 4, '火': 4,
        # 手部
        '扌': 4, '手': 4,
        # 心部
        '忄': 4, '心': 4,
        # 犬部
        '犭': 4, '犬': 4,
        # 玉部
        '王': 5, '玉': 5,
        # 示部
        '礻': 5, '示': 5,
        # 衣部
        '衤': 6, '衣': 6,
        # 肉部
        '月': 6,  # 作為肉字旁時算6畫
        # 草部
        '艹': 6, '艸': 6,
        # 邑部（右耳旁）
        '阝': 7,  # 在右邊時
        # 阜部（左耳旁）
        # '阝': 8,  # 在左邊時（需要根據位置判斷）
        # 網部
        '罒': 6,
        # 老部
        '耂': 6,
    }
    
    # 常用字康熙筆畫（部分特殊字）
    KANGXI_STROKES = {
        # 常見姓氏
        '王': 4, '李': 7, '張': 11, '劉': 15, '陳': 16,
        '楊': 13, '黃': 12, '趙': 14, '周': 8, '吳': 7,
        '徐': 10, '孫': 10, '馬': 10, '朱': 6, '胡': 11,
        '郭': 15, '何': 7, '林': 8, '高': 10, '羅': 20,
        '鄭': 19, '梁': 11, '謝': 17, '宋': 7, '唐': 10,
        '許': 11, '韓': 17, '馮': 12, '鄧': 19, '曹': 11,
        '彭': 12, '曾': 12, '蕭': 18, '田': 5, '董': 15,
        '潘': 16, '袁': 10, '蔡': 17, '蔣': 17, '余': 7,
        '杜': 7, '葉': 15, '程': 12, '魏': 18, '蘇': 22,
        '呂': 7, '丁': 2, '任': 6, '盧': 16, '姚': 9,
        '沈': 8, '鍾': 17, '姜': 9, '崔': 11, '譚': 19,
        '陸': 16, '范': 15, '汪': 8, '廖': 14, '石': 5,
        '金': 8, '韋': 9, '賈': 13, '夏': 10, '付': 5,
        '方': 4, '鄒': 17, '熊': 14, '白': 5, '孟': 8,
        '秦': 10, '邱': 12, '侯': 9, '江': 7, '尹': 4,
        '薛': 19, '閻': 16, '段': 9, '雷': 13, '龍': 16,
        '史': 5, '陶': 16, '黎': 15, '賀': 12, '毛': 4,
        '郝': 14, '顧': 21, '龔': 22, '邵': 12, '萬': 15,
        '錢': 16, '嚴': 20, '洪': 10, '武': 8, '莫': 13,
        # 常見名字用字
        '明': 8, '國': 11, '華': 14, '建': 9, '文': 4,
        '志': 7, '偉': 11, '強': 11, '軍': 9, '平': 5,
        '東': 8, '海': 11, '波': 9, '雲': 12, '天': 4,
        '成': 7, '思': 9, '家': 10, '安': 6, '宏': 7,
        '新': 13, '民': 5, '永': 5, '子': 3, '小': 3,
        '芳': 10, '娟': 10, '敏': 11, '靜': 16, '麗': 19,
        '英': 11, '玲': 10, '桂': 10, '秀': 7, '蘭': 23,
        '梅': 11, '燕': 16, '霞': 17, '紅': 9, '春': 9,
        '美': 9, '婷': 12, '雅': 12, '慧': 15, '琳': 13,
        '佳': 8, '欣': 8, '怡': 9, '詩': 13, '雨': 8,
        '夢': 14, '晨': 11, '旭': 6, '陽': 17, '俊': 9,
        '傑': 12, '浩': 11, '宇': 6, '澤': 17, '博': 12,
        '銘': 14, '哲': 10, '睿': 14, '翔': 12, '瑞': 14,
        '嘉': 14, '豪': 14, '辰': 7, '軒': 10, '皓': 12,
        '一': 1, '二': 2, '三': 3, '四': 4, '五': 4,
        '六': 4, '七': 2, '八': 2, '九': 2, '十': 2,
        '百': 6, '千': 3, '萬': 15, '億': 15,
        '月': 4, '日': 4, '星': 9, '光': 6, '風': 9,
        '水': 4, '火': 4, '木': 4, '金': 8, '土': 3,
        '山': 3, '川': 3, '河': 9, '湖': 13, '江': 7,
        '德': 15, '仁': 4, '義': 13, '禮': 18, '智': 12,
        '信': 9, '忠': 8, '孝': 7, '勇': 9, '廉': 13,
        # 補充常用字
        '宥': 9, '竹': 6, '育': 10, '助': 7,
        '彥': 9, '廷': 7, '庭': 10, '恩': 10, '祥': 11,
        '翰': 16, '霖': 16, '峰': 10, '鑫': 24, '淵': 12,
        '維': 14, '聖': 13, '賢': 15, '毅': 15, '凱': 12,
        '承': 8, '廷': 7, '恆': 10, '宸': 10, '祐': 10,
    }
    
    def __init__(self):
        """初始化計算器（v2.1：載入外部康熙筆畫資料庫）"""
        root_dir = Path(__file__).parent.parent.parent
        data_file = root_dir / "data" / "name_analysis.json"
        with open(data_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.eighty_one = self.data["eighty_one_numbers"]
        self.three_talents_data = self.data["three_talents"]
        self.number_to_element = self.data["number_to_element"]
        
        # v2.1: 載入外部康熙筆畫資料庫
        kangxi_file = root_dir / "data" / "kangxi_strokes.json"
        self._external_kangxi = {}
        try:
            if kangxi_file.exists():
                with open(kangxi_file, 'r', encoding='utf-8') as f:
                    self._external_kangxi = json.load(f)
                # 合併到 KANGXI_STROKES（外部資料庫優先級低於類定義的硬編碼值）
                for char, strokes in self._external_kangxi.items():
                    if char not in self.KANGXI_STROKES:
                        self.KANGXI_STROKES[char] = strokes
        except Exception:
            pass  # 外部檔案不存在時使用內建表
    
    def get_stroke_count(self, char: str) -> int:
        """取得單一字的康熙筆畫數"""
        # 優先查找預定義表
        if char in self.KANGXI_STROKES:
            return self.KANGXI_STROKES[char]
        
        # 使用 Unicode 資料庫估算（不完全準確）
        try:
            # CJK 統一漢字基本上可以用這個方法
            name = unicodedata.name(char, '')
            if 'CJK' in name:
                # 嘗試從 Unihan 資料估算，這裡用簡化方法
                # 實際應用中應該使用完整的康熙字典資料庫
                return self._estimate_strokes(char)
        except:
            pass
        
        return 0
    
    def _estimate_strokes(self, char: str) -> int:
        """估算筆畫（簡化方法）"""
        # 這是一個簡化的估算方法
        # 實際應用中應該使用完整的康熙字典資料庫
        code = ord(char)
        
        # 簡單的估算規則（僅供參考）
        if 0x4E00 <= code <= 0x9FFF:  # CJK 基本區
            # 大致按區間估算
            if code < 0x5000:
                return 4
            elif code < 0x6000:
                return 7
            elif code < 0x7000:
                return 9
            elif code < 0x8000:
                return 11
            elif code < 0x9000:
                return 13
            else:
                return 15
        
        return 10  # 預設值
    
    def parse_name(self, full_name: str) -> Tuple[str, str]:
        """解析姓名，分離姓氏與名字"""
        full_name = full_name.strip()
        
        # 複姓列表
        compound_surnames = [
            '歐陽', '上官', '司馬', '諸葛', '司徒', '慕容', '公孫',
            '皇甫', '令狐', '東方', '西門', '南宮', '尉遲', '長孫'
        ]
        
        # 檢查是否為複姓
        for surname in compound_surnames:
            if full_name.startswith(surname):
                return surname, full_name[len(surname):]
        
        # 單姓
        if len(full_name) >= 2:
            return full_name[0], full_name[1:]
        
        return full_name, ''
    
    def calculate_five_grids(self, surname: str, given_name: str) -> FiveGrids:
        """計算五格"""
        # 計算各字筆畫
        surname_strokes = [self.get_stroke_count(c) for c in surname]
        given_name_strokes = [self.get_stroke_count(c) for c in given_name]
        
        total_surname = sum(surname_strokes)
        total_given = sum(given_name_strokes)
        total = total_surname + total_given
        
        # 天格：單姓+1，複姓為姓氏總筆畫
        if len(surname) == 1:
            天格 = surname_strokes[0] + 1
        else:
            天格 = total_surname
        
        # 人格：姓氏最後一字 + 名字第一字
        人格 = surname_strokes[-1] + (given_name_strokes[0] if given_name_strokes else 1)
        
        # 地格：名字總筆畫，單名+1
        if len(given_name) == 1:
            地格 = given_name_strokes[0] + 1
        elif len(given_name) > 1:
            地格 = total_given
        else:
            地格 = 2  # 無名字時預設
        
        # 總格：姓名總筆畫
        總格 = total
        
        # 外格：總格 - 人格 + 1
        外格 = 總格 - 人格 + 1
        if 外格 < 2:
            外格 = 2
        
        return FiveGrids(天格=天格, 人格=人格, 地格=地格, 外格=外格, 總格=總格)
    
    def get_element(self, number: int) -> str:
        """根據數字取得五行"""
        last_digit = str(number % 10)
        return self.number_to_element.get(last_digit, "土")
    
    def get_number_analysis(self, number: int) -> Dict:
        """取得數字的吉凶分析"""
        # 81 數理循環
        effective_number = ((number - 1) % 81) + 1
        return self.eighty_one.get(str(effective_number), self.eighty_one["1"])
    
    def analyze_grid(self, grid_name: str, number: int) -> GridAnalysis:
        """分析單一格"""
        analysis = self.get_number_analysis(number)
        element = self.get_element(number)
        
        return GridAnalysis(
            name=grid_name,
            number=number,
            element=element,
            fortune=analysis.get("fortune", ""),
            number_name=analysis.get("name", ""),
            description=analysis.get("description", ""),
            keywords=analysis.get("keywords", [])
        )
    
    def analyze_three_talents(self, five_grids: FiveGrids) -> Dict:
        """分析三才配置"""
        天_element = self.get_element(five_grids.天格)
        人_element = self.get_element(five_grids.人格)
        地_element = self.get_element(five_grids.地格)
        
        combination = f"{天_element}{人_element}{地_element}"
        
        result = self.three_talents_data["combinations"].get(
            combination,
            {"fortune": "半吉", "description": "需要更多資訊分析"}
        )
        
        return {
            "combination": combination,
            "天格五行": 天_element,
            "人格五行": 人_element,
            "地格五行": 地_element,
            "fortune": result["fortune"],
            "description": result["description"]
        }
    
    def calculate_overall_fortune(self, grid_analyses: Dict[str, GridAnalysis], three_talents: Dict) -> str:
        """計算整體運勢評價"""
        fortunes = {
            "大吉": 4,
            "吉": 3,
            "半吉": 2,
            "半凶": 1,
            "凶": 0
        }
        
        # 人格權重最高
        weights = {
            "天格": 1,
            "人格": 3,
            "地格": 2,
            "外格": 1,
            "總格": 2
        }
        
        total_score = 0
        total_weight = 0
        
        for grid_name, analysis in grid_analyses.items():
            weight = weights.get(grid_name, 1)
            score = fortunes.get(analysis.fortune, 2)
            total_score += score * weight
            total_weight += weight
        
        # 三才配置加權
        three_talents_score = fortunes.get(three_talents["fortune"], 2)
        total_score += three_talents_score * 3
        total_weight += 3
        
        avg_score = total_score / total_weight
        
        if avg_score >= 3.5:
            return "大吉"
        elif avg_score >= 2.8:
            return "吉"
        elif avg_score >= 2.0:
            return "中等"
        elif avg_score >= 1.2:
            return "欠佳"
        else:
            return "凶"
    
    def generate_recommendations(self, grid_analyses: Dict[str, GridAnalysis], 
                                  three_talents: Dict, 
                                  bazi_element: Optional[str] = None) -> List[str]:
        """生成建議"""
        recommendations = []
        
        # 根據人格分析
        人格_analysis = grid_analyses.get("人格")
        if 人格_analysis:
            if 人格_analysis.fortune in ["凶", "半凶"]:
                recommendations.append(f"人格數 {人格_analysis.number}（{人格_analysis.number_name}）屬{人格_analysis.fortune}，"
                                       f"建議在事業發展上多加謹慎，穩紮穩打")
            elif 人格_analysis.fortune in ["大吉", "吉"]:
                recommendations.append(f"人格數 {人格_analysis.number}（{人格_analysis.number_name}）屬{人格_analysis.fortune}，"
                                       f"個人能力與才華有良好發揮空間")
        
        # 根據三才配置
        if three_talents["fortune"] in ["凶"]:
            recommendations.append(f"三才配置「{three_talents['combination']}」不理想，"
                                   f"建議注意人際關係與健康")
        elif three_talents["fortune"] in ["大吉"]:
            recommendations.append(f"三才配置「{three_talents['combination']}」極佳，"
                                   f"天時地利人和，發展順遂")
        
        # 根據八字喜用神（如果有提供）
        if bazi_element:
            人格_element = grid_analyses["人格"].element
            if 人格_element == bazi_element:
                recommendations.append(f"人格五行「{人格_element}」與八字喜用神相合，姓名與命格相輔相成")
            else:
                recommendations.append(f"人格五行「{人格_element}」與八字喜用神「{bazi_element}」不同，"
                                       f"可透過其他方式補強")
        
        # 總格晚年運
        總格_analysis = grid_analyses.get("總格")
        if 總格_analysis:
            if 總格_analysis.fortune in ["大吉", "吉"]:
                recommendations.append(f"總格數 {總格_analysis.number} 主晚年運勢良好，晚景安康")
            elif 總格_analysis.fortune in ["凶", "半凶"]:
                recommendations.append(f"總格數 {總格_analysis.number} 提醒注意晚年規劃，建議提早準備")
        
        return recommendations
    
    def analyze(self, full_name: str, bazi_element: Optional[str] = None) -> NameAnalysis:
        """完整姓名分析"""
        # 解析姓名
        surname, given_name = self.parse_name(full_name)
        
        # 計算筆畫
        surname_strokes = [self.get_stroke_count(c) for c in surname]
        given_name_strokes = [self.get_stroke_count(c) for c in given_name]
        
        # 計算五格
        five_grids = self.calculate_five_grids(surname, given_name)
        
        # 分析各格
        grid_analyses = {
            "天格": self.analyze_grid("天格", five_grids.天格),
            "人格": self.analyze_grid("人格", five_grids.人格),
            "地格": self.analyze_grid("地格", five_grids.地格),
            "外格": self.analyze_grid("外格", five_grids.外格),
            "總格": self.analyze_grid("總格", five_grids.總格),
        }
        
        # 三才配置
        three_talents = self.analyze_three_talents(five_grids)
        
        # 整體運勢
        overall_fortune = self.calculate_overall_fortune(grid_analyses, three_talents)
        
        # 建議
        recommendations = self.generate_recommendations(grid_analyses, three_talents, bazi_element)
        
        return NameAnalysis(
            surname=surname,
            given_name=given_name,
            full_name=full_name,
            surname_strokes=surname_strokes,
            given_name_strokes=given_name_strokes,
            total_strokes=sum(surname_strokes) + sum(given_name_strokes),
            five_grids=five_grids,
            grid_analyses=grid_analyses,
            three_talents=three_talents,
            overall_fortune=overall_fortune,
            recommendations=recommendations
        )
    
    def to_dict(self, analysis: NameAnalysis) -> Dict:
        """轉換為字典格式"""
        return {
            "name_info": {
                "full_name": analysis.full_name,
                "surname": analysis.surname,
                "given_name": analysis.given_name,
                "surname_strokes": analysis.surname_strokes,
                "given_name_strokes": analysis.given_name_strokes,
                "total_strokes": analysis.total_strokes
            },
            "five_grids": {
                "天格": analysis.five_grids.天格,
                "人格": analysis.five_grids.人格,
                "地格": analysis.five_grids.地格,
                "外格": analysis.five_grids.外格,
                "總格": analysis.five_grids.總格
            },
            "grid_analyses": {
                name: {
                    "number": grid.number,
                    "element": grid.element,
                    "fortune": grid.fortune,
                    "number_name": grid.number_name,
                    "description": grid.description,
                    "keywords": grid.keywords
                }
                for name, grid in analysis.grid_analyses.items()
            },
            "three_talents": analysis.three_talents,
            "overall_fortune": analysis.overall_fortune,
            "recommendations": analysis.recommendations
        }
    
    def format_for_prompt(self, analysis: NameAnalysis) -> str:
        """格式化為 Prompt 輸入"""
        lines = [
            f"【姓名分析】{analysis.full_name}",
            f"",
            f"姓氏：{analysis.surname}（{'+'.join(map(str, analysis.surname_strokes))}={sum(analysis.surname_strokes)} 畫）",
            f"名字：{analysis.given_name}（{'+'.join(map(str, analysis.given_name_strokes))}={sum(analysis.given_name_strokes)} 畫）",
            f"總筆畫：{analysis.total_strokes} 畫",
            f"",
            f"【五格數理】",
            f"天格（先天運）：{analysis.five_grids.天格}（{analysis.grid_analyses['天格'].element}）- {analysis.grid_analyses['天格'].fortune}",
            f"人格（主運）：{analysis.five_grids.人格}（{analysis.grid_analyses['人格'].element}）- {analysis.grid_analyses['人格'].fortune}",
            f"地格（前運）：{analysis.five_grids.地格}（{analysis.grid_analyses['地格'].element}）- {analysis.grid_analyses['地格'].fortune}",
            f"外格（副運）：{analysis.five_grids.外格}（{analysis.grid_analyses['外格'].element}）- {analysis.grid_analyses['外格'].fortune}",
            f"總格（後運）：{analysis.five_grids.總格}（{analysis.grid_analyses['總格'].element}）- {analysis.grid_analyses['總格'].fortune}",
            f"",
            f"【三才配置】",
            f"{analysis.three_talents['combination']}（{analysis.three_talents['fortune']}）",
            f"{analysis.three_talents['description']}",
            f"",
            f"【整體評價】{analysis.overall_fortune}"
        ]
        
        return "\n".join(lines)


# 測試程式碼
if __name__ == "__main__":
    calc = NameCalculator()
    
    # 測試姓名
    test_names = ["陳育助", "王小明", "歐陽修文", "李白"]
    
    for name in test_names:
        print("=" * 60)
        analysis = calc.analyze(name)
        print(calc.format_for_prompt(analysis))
        print()
    
    print("✅ 姓名學計算器測試完成！")
