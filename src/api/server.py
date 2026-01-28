"""
Aetheria 定盤系統 API
提供命盤分析、鎖定、查詢功能
支持紫微斗数、八字命理、交叉验证
"""

import os
import sys
import json
import re
import uuid
import hmac
import hashlib
import secrets
from datetime import datetime, date, timedelta
from typing import Dict, Optional, Tuple, Any, List
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeoutError

# 確保專案根目錄在 Python 路徑中
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

try:
    from opencc import OpenCC
except Exception:
    OpenCC = None

# 從 src 模組導入計算器
from src.calculators.chart_extractor import ChartExtractor
from src.calculators.fortune import FortuneTeller
from src.calculators.bazi import BaziCalculator
from src.calculators.astrology import AstrologyCalculator
from src.calculators.tarot import TarotCalculator
from src.calculators.numerology import NumerologyCalculator
from src.calculators.name import NameCalculator

# 從 src 模組導入提示詞
from src.prompts.fortune import (
    FORTUNE_ANNUAL_ANALYSIS,
    FORTUNE_MONTHLY_ANALYSIS,
    FORTUNE_QUESTION_ANALYSIS,
    FORTUNE_AUSPICIOUS_DAYS
)
from src.prompts.synastry import (
    SYNASTRY_MARRIAGE_ANALYSIS,
    SYNASTRY_PARTNERSHIP_ANALYSIS,
    SYNASTRY_QUICK_CHECK
)
from src.prompts.date_selection import (
    DATE_SELECTION_MARRIAGE,
    DATE_SELECTION_BUSINESS,
    DATE_SELECTION_MOVING,
    DATE_SELECTION_QUICK
)
from src.prompts.bazi import (
    format_bazi_analysis_prompt,
    format_bazi_fortune_prompt,
    format_cross_validation_prompt
)
from src.prompts.astrology import (
    get_natal_chart_analysis_prompt,
    get_synastry_analysis_prompt,
    get_transit_analysis_prompt,
    get_career_analysis_prompt
)
from src.prompts.tarot import generate_tarot_prompt
from src.prompts.numerology import generate_numerology_prompt
from src.prompts.name import generate_name_prompt, generate_name_suggestion_prompt
from src.prompts.integrated import generate_integrated_prompt, generate_comparison_prompt
from src.prompts.strategic import (
    generate_strategic_profile_prompt,
    generate_birth_rectifier_prompt,
    generate_relationship_ecosystem_prompt,
    generate_decision_sandbox_prompt
)
from src.utils.gemini_client import GeminiClient
from src.utils.logger import get_logger, setup_logger
from src.utils.errors import (
    AetheriaException,
    MissingParameterException,
    UserNotFoundException,
    ChartNotFoundException,
    ChartNotLockedException,
    AIAPIException,
    register_error_handlers
)
from src.utils.database import get_database, AetheriaDatabase
from src.api.blueprints.auth import auth_bp
import src.utils.auth_utils as auth_utils

# 載入環境變數
load_dotenv()


# 初始化 Gemini 客戶端（使用新 SDK）
gemini_client = GeminiClient(
    api_key=os.getenv('GEMINI_API_KEY'),
    model_name=os.getenv('MODEL_NAME', 'gemini-2.0-flash'),
    temperature=float(os.getenv('TEMPERATURE', '0.4')),
    max_output_tokens=int(os.getenv('MAX_OUTPUT_TOKENS', '8192'))
)


def to_zh_tw(text: str) -> str:
    """將簡體中文轉為台灣繁體（s2twp）。"""
    if not text:
        return text
    if OpenCC is None:
        return text
    try:
        return OpenCC('s2twp').convert(text)
    except Exception:
        return text


def sanitize_plain_text(text: str) -> str:
    """基礎清理回應內容，保留核心內容。"""
    if not text:
        return text
    cleaned = text.strip()
    # 移除 ```json 和 ``` 標記，但保留 JSON 內容
    cleaned = re.sub(r'^```json\s*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'^```\s*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'```\s*$', '', cleaned)
    return cleaned.strip()


def strip_first_json_block(text: str) -> str:
    """移除回應中第一段 JSON 區塊（避免前端顯示原始 JSON）。"""
    if not text:
        return text
    json_block = extractor._extract_brace_block(text) if hasattr(extractor, '_extract_brace_block') else None
    if not json_block:
        return text
    cleaned = text.replace(json_block, '')
    cleaned = re.sub(r'【結構化命盤資料】\s*', '', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()

app = Flask(__name__)

# 明確指定允許的前端 origin（開發環境常用 http://172.237.19.63 與本機 dev server）
ALLOWED_ORIGINS = [
    'http://172.237.19.63',
    'http://localhost:5173',
    'http://127.0.0.1:5173'
]

# 使用 flask-cors，並允許帶憑證（若前端使用 cookies / Authorization header）
CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}}, supports_credentials=True)

# 回應 Private Network Access (PNA) 的預檢請求標頭
@app.after_request
def _allow_private_network(response):
    # 處理 Private Network Access (PNA) 以及補強 CORS 回應
    try:
        origin = request.headers.get('Origin')
        # 若 Origin 在允許清單中，則回應中回放該 Origin（不要使用 '*', 因為可能需要帶憑證）
        if origin and origin in ALLOWED_ORIGINS:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Vary'] = 'Origin'

        # 必要的 CORS 標頭（預檢與一般回應）
        response.headers.setdefault('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.setdefault('Access-Control-Allow-Headers', request.headers.get('Access-Control-Request-Headers', 'Authorization,Content-Type'))
        # 若前端在預檢請求中包含 PNA 標頭，則在回應中加入允許標記
        if request.headers.get('Access-Control-Request-Private-Network') == 'true':
            response.headers['Access-Control-Allow-Private-Network'] = 'true'
    except Exception:
        pass
    return response


# 在所有路由上支援 OPTIONS 預檢回應（確保預檢能得到正確的 PNA header）
@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path: str):
    resp = jsonify({'ok': True})
    origin = request.headers.get('Origin')
    if origin and origin in ALLOWED_ORIGINS:
        resp.headers['Access-Control-Allow-Origin'] = origin
        resp.headers['Vary'] = 'Origin'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = request.headers.get('Access-Control-Request-Headers', 'Authorization,Content-Type')
    if request.headers.get('Access-Control-Request-Private-Network') == 'true':
        resp.headers['Access-Control-Allow-Private-Network'] = 'true'
    return resp, 200

# 註冊錯誤處理器
register_error_handlers(app)

# 註冊 Blueprint
app.register_blueprint(auth_bp, url_prefix='/api/auth')


# 初始化日誌系統
logger = setup_logger(log_level='INFO')
logger.info("Aetheria API 服務初始化中...")

# 初始化資料庫
db = get_database(str(ROOT_DIR / 'data' / 'aetheria.db'))
logger.info("SQLite 資料庫已初始化")

# 資料儲存目錄（使用專案根目錄的 data 資料夾）- 保留用於向後相容
DATA_DIR = ROOT_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

USERS_FILE = DATA_DIR / 'users.json'
LOCKS_FILE = DATA_DIR / 'chart_locks.json'

# 初始化資料檔案（向後相容，逐步遷移到 SQLite）
if not USERS_FILE.exists():
    USERS_FILE.write_text('{}', encoding='utf-8')
if not LOCKS_FILE.exists():
    LOCKS_FILE.write_text('{}', encoding='utf-8')

# 初始化西洋占星計算器
astrology_calc = AstrologyCalculator()

# 初始化塔羅牌計算器
tarot_calc = TarotCalculator()

# 初始化靈數學計算器
numerology_calc = NumerologyCalculator()

# 初始化姓名學計算器
name_calc = NameCalculator()

# 初始化提取器
extractor = ChartExtractor()

# ============================================
# Prompt 模板
# ============================================
def build_tarot_fallback(reading, context: str) -> str:
    """以牌義資料建立快速解讀，避免等待 AI。"""
    lines = []
    lines.append("【塔羅解讀】")
    if reading.question:
        lines.append(f"問題：{reading.question}")
    lines.append(f"牌陣：{reading.spread_name}")
    lines.append("")
    lines.append("【抽到的牌】")
    for idx, card in enumerate(reading.cards, start=1):
        meaning = tarot_calc.get_card_meaning(card.id, card.is_reversed, context)
        orientation = "逆位" if card.is_reversed else "正位"
        keywords = "、".join(meaning.get('keywords', []))
        lines.append(f"{idx}. {card.position}：{card.name}（{orientation}）")
        if keywords:
            lines.append(f"   關鍵詞：{keywords}")
        if meaning.get('meaning'):
            lines.append(f"   牌義：{meaning.get('meaning')}")
        if meaning.get('element'):
            lines.append(f"   元素：{meaning.get('element')}")
    lines.append("")
    lines.append("【整體指引】")
    lines.append("以上為牌義的核心提醒，建議你將焦點放在可控的選擇與行動上，透過具體決策來回應當前能量。")
    return "\n".join(lines)

SYSTEM_INSTRUCTION = """
你是 Aetheria，精通紫微斗數的 AI 命理顧問。

重要原則：
1. 準確性最重要，不可編造星曜
2. 晚子時（23:00-00:00）的判定邏輯要明確說明，且不得自作主張改規則
3. 必須明確說出命宮位置、主星、格局
4. 結構清晰，先說命盤結構，再說詳細分析

輸出風格：專業、溫暖、具啟發性
"""

INITIAL_ANALYSIS_PROMPT = """你好，我是 Aetheria。很高興能為你解讀這張紫微鬥數命盤。

請為以下用戶提供完整的紫微鬥數命盤分析：

出生日期：{birth_date}
出生時間：{birth_time}
出生地點：{birth_location}
性別：{gender}

【重要排盤邏輯：晚子時處理】
（本次規則：{late_zi_rule_value}）
{late_zi_logic_md}

【格式要求】
1. 使用 Markdown 格式輸出
2. 標題層級：主要部分使用 ###，子部分使用 ####
3. 重點使用 **粗體**
4. 分隔線使用 ---
5. JSON 區塊務必保留在 「### 【結構化命盤資料】」 之下

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 【結構化命盤資料】
請務必先輸出以下 JSON 格式數據，封裝在 ```json 區塊中：
{{
    "排盤規則": {{
        "晚子時換日": "{late_zi_rule_value}",
        "晚子時區間": "23:00-00:00",
        "排盤日期基準": "{birth_date}"
    }},
  "五行局": "火六局 等",
  "命宮": {{
    "地支": "地支",
    "主星": ["星1", "星2"],
    "輔星": ["輔星1"]
  }},
  "身宮": {{
    "地支": "地支",
    "主星": ["星1"]
  }},
  "十二宮": {{
    "命宮": {{"地支": "X", "主星": ["星1"]}},
    "兄弟宮": {{"地支": "X", "主星": ["星1"]}},
    "夫妻宮": {{"地支": "X", "主星": ["星1"]}},
    "子女宮": {{"地支": "X", "主星": ["星1"]}},
    "財帛宮": {{"地支": "X", "主星": ["星1"]}},
    "疾厄宮": {{"地支": "X", "主星": ["星1"]}},
    "遷移宮": {{"地支": "X", "主星": ["星1"]}},
    "交友宮": {{"地支": "X", "主星": ["星1"]}},
    "官祿宮": {{"地支": "X", "主星": ["星1"]}},
    "田宅宮": {{"地支": "X", "主星": ["星1"]}},
    "福德宮": {{"地支": "X", "主星": ["星1"]}},
    "父母宮": {{"地支": "X", "主星": ["星1"]}}
  }},
  "四化": {{
    "化祿": "星名",
    "化權": "星名",
    "化科": "星名",
    "化忌": "星名"
  }},
  "格局": ["格局1", "格局2"]
}}

---

【紫微鬥數命盤圖】
請以下方 4x4 方格律為基準繪製 ASCII 命盤，中間四格留空或放入核心資訊（如姓名、五行局）：

```text
┌──────┬──────┬──────┬──────┐
│  巳  │  午  │  未  │  申  │
│      │      │      │      │
├──────┼──────┴──────┼──────┤
│  辰  │              │  酉  │
│      │    中  宮    │      │
├──────┤              ├──────┤
│  卯  │   (基本資料)  │  戌  │
│      │              │      │
├──────┼──────┬──────┼──────┤
│  寅  │  丑  │  子  │  亥  │
│      │      │      │      │
└──────┴──────┴──────┴──────┘
```
請將主星、輔星及宮位名稱填入各對應地支格中。

---

#### 一、命盤基礎結構：[加上具體描述，如：溫潤如玉的策劃者]

1. **時辰判定與命身同宮**：說明時辰處理（如晚子時）與命身宮位置的意義。
2. **命宮主星**：詳細解析主星特質。
3. **核心格局**：解析如「機月同梁」等格局的社會定位。

#### 二、十二宮深度解讀
（依序分析重要宮位：命宮、財帛宮、官祿宮、夫妻宮、兄弟宮、遷移宮等）

#### 三、性格特質與人生建議
1. **核心性格關鍵詞**
2. **事業方向建議**
3. **人際與感情建議**
4. **2026年流年提示**

Aetheria 的總結：結尾寄語。
"""

CHAT_WITH_LOCKED_CHART_PROMPT = """
【已鎖定的命盤結構】（此為用戶首次分析時確認的正確命盤，請在所有回應中依據此結構）

{chart_structure}

【用戶當前問題】
{user_question}

【回應要求】
1. 必須基於上述鎖定的命盤結構
2. 不要重新排盤或改變宮位配置
3. 深入分析當前問題與命盤的關聯
4. 提供具體可行的建議
5. 語氣溫暖、專業、具啟發性
"""

CHAT_TEACHER_STYLE_PROMPT = """
你是一位溫暖而專業的命理老師，回答時要像真人對談，有同理心但不誇大、不恐嚇。

語氣偏好：{tone}

回應結構請嚴格遵守：
1) 共感一句（簡短、真誠）
2) 解讀重點（2-4 點，清晰條列）
3) 可行建議（2-3 點，具體可行）
4) 下一步問題（1 句，邀請對話延伸）

注意：
- 避免絕對斷言，改用「可能、傾向、建議」
- 若涉及健康/法律等敏感議題，提醒以專業意見為準
"""

SUMMARY_SYSTEM_INSTRUCTION = """
你是一位對話摘要員，專注提取重點且保持中立。
"""

CONVERSATION_SUMMARY_PROMPT = """
請將以下對話濃縮為 3-5 句摘要，包含：
1) 使用者核心關注點
2) 情緒或狀態
3) 已給的建議方向

對話紀錄：
{conversation}
"""

# ============================================
# 資料存取函式
# ============================================

def load_json(file_path: Path) -> Dict:
    """載入 JSON 檔案"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(file_path: Path, data: Dict):
    """儲存 JSON 檔案"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_birth_time_str(birth_time_str: Optional[str]) -> Optional[Tuple[int, int]]:
    """解析出生時間字串，回傳 (hour, minute)"""
    if not birth_time_str:
        return None
    text = str(birth_time_str).strip()
    match = re.match(r'^(\d{1,2})(?::(\d{1,2}))?$', text)
    if not match:
        return None
    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    if 0 <= hour <= 23 and 0 <= minute <= 59:
        return hour, minute
    return None


_ZIWEI_LATE_ZI_EXPECTED_RULE = "日不進位"
_ZIWEI_LATE_ZI_WINDOW = "23:00-00:00"
_ZIWEI_RULESET_NO_DAY_ADVANCE_ID = "ziwei.late_zi.no_day_advance"
_ZIWEI_RULESET_DAY_ADVANCE_ID = "ziwei.late_zi.day_advance"
_ZIWEI_DEFAULT_RULESET_ID = _ZIWEI_RULESET_NO_DAY_ADVANCE_ID
_ZIWEI_PIPELINE_VERSION = "ziwei.llm_json_extract.v1"
_ZIWEI_LATE_ZI_DAY_ADVANCE_RE = re.compile(
    r"(下一個\s*農曆日|視為\s*下一[個日]\s*農曆日|視為\s*(次日|隔日)|排盤\s*以\s*農曆.{0,8}24\s*日\s*計算|日期\s*進位|跳到\s*隔日|算作\s*隔日)",
    flags=re.IGNORECASE
)
_ZIWEI_LATE_ZI_NO_ADVANCE_RE = re.compile(
    r"(日不進位|不\s*進位|不\s*換日|以\s*當日\s*作為\s*排盤\s*基準)",
    flags=re.IGNORECASE
)


def _normalize_ziwei_ruleset_id(value: Optional[str]) -> str:
    """Map external/UI ruleset values to internal ruleset IDs."""
    if not value:
        return _ZIWEI_DEFAULT_RULESET_ID
    text = str(value).strip().lower()
    if text in {"no_day_advance", "no-advance", "noadvance", _ZIWEI_RULESET_NO_DAY_ADVANCE_ID.lower()}:
        return _ZIWEI_RULESET_NO_DAY_ADVANCE_ID
    if text in {"day_advance", "advance", "day-advance", _ZIWEI_RULESET_DAY_ADVANCE_ID.lower()}:
        return _ZIWEI_RULESET_DAY_ADVANCE_ID
    return _ZIWEI_DEFAULT_RULESET_ID


def _get_ziwei_ruleset_config(ruleset_id: str) -> Dict:
    rid = _normalize_ziwei_ruleset_id(ruleset_id)
    if rid == _ZIWEI_RULESET_DAY_ADVANCE_ID:
        return {
            'ruleset_id': _ZIWEI_RULESET_DAY_ADVANCE_ID,
            'late_zi_rule_value': '日進位',
            'late_zi_logic_md': (
                "若出生時間在 23:00 - 00:00 之間（晚子時），請務必遵循以下原則：\n"
                "1. **日期進位**：晚子時視為隔日作為排盤基準（以門派規則進位）。\n"
                "2. **時辰為子時**：時辰支為「子」。\n"
                "3. **命身宮位置**：以進位後的排盤基準日對應的宮位排布。\n"
            )
        }
    return {
        'ruleset_id': _ZIWEI_RULESET_NO_DAY_ADVANCE_ID,
        'late_zi_rule_value': '日不進位',
        'late_zi_logic_md': (
            "若出生時間在 23:00 - 00:00 之間（晚子時），請務必遵循以下原則：\n"
            "1. **日期不進位**：以該「出生日期」當天作為排盤基準（不跳到隔日）。\n"
            "2. **時辰為子時**：時辰支為「子」。\n"
            "3. **命身宮位置**：以該日（晚子時）對應的宮位排布。\n"
        )
    }


def _is_late_zi_time(birth_time: Optional[str]) -> bool:
    parsed = parse_birth_time_str(birth_time)
    if not parsed:
        return False
    hour, minute = parsed
    return hour == 23 and 0 <= minute <= 59


def _validate_ziwei_rule_consistency(
    *,
    birth_date: str,
    birth_time: str,
    structure: Dict,
    analysis_text: str,
    ruleset_id: str = _ZIWEI_DEFAULT_RULESET_ID
) -> Optional[str]:
    """Validate Ziwei late-zi-hour rule consistency.

    This project adopts a single canonical rule for late-zi-hour (23:00-00:00):
    - date does NOT advance; time branch is 子.
    """
    if not _is_late_zi_time(birth_time):
        return None

    effective_ruleset_id = _normalize_ziwei_ruleset_id(ruleset_id)
    cfg = _get_ziwei_ruleset_config(effective_ruleset_id)
    expected_rule_value = cfg.get('late_zi_rule_value')

    rules = structure.get('排盤規則') if isinstance(structure, dict) else None
    if rules is None:
        return "晚子時規則驗證失敗：JSON 缺少『排盤規則』欄位（無法稽核換日規則）"
    if isinstance(rules, dict):
        rule_value = str(rules.get('晚子時換日') or '').strip()
        base_date = str(rules.get('排盤日期基準') or '').strip()
        window = str(rules.get('晚子時區間') or '').strip()
        if not rule_value:
            return "晚子時規則驗證失敗：JSON 的『排盤規則.晚子時換日』為空"
        if effective_ruleset_id == _ZIWEI_RULESET_NO_DAY_ADVANCE_ID:
            if rule_value != expected_rule_value:
                return f"晚子時換日規則不一致：期望『{expected_rule_value}』，但 JSON 為『{rule_value}』"
            if base_date and base_date != birth_date:
                return f"排盤日期基準不一致：期望『{birth_date}』，但 JSON 為『{base_date}』"
        elif effective_ruleset_id == _ZIWEI_RULESET_DAY_ADVANCE_ID:
            # Allow a few common aliases for "day advance" in JSON.
            if rule_value not in {"日進位", "隔日", "次日", "視為隔日", "視為次日"}:
                return f"晚子時換日規則不一致：期望『日進位/隔日』類型，但 JSON 為『{rule_value}』"
        if window and window != _ZIWEI_LATE_ZI_WINDOW:
            return f"晚子時區間不一致：期望『{_ZIWEI_LATE_ZI_WINDOW}』，但 JSON 為『{window}』"

    # Even if JSON lacks metadata, the narrative must not claim day-advance.
    if analysis_text:
        if effective_ruleset_id == _ZIWEI_RULESET_NO_DAY_ADVANCE_ID:
            if _ZIWEI_LATE_ZI_DAY_ADVANCE_RE.search(analysis_text):
                return "晚子時規則違反：文字敘述出現『隔日/下一個農曆日』等進位說法"
        elif effective_ruleset_id == _ZIWEI_RULESET_DAY_ADVANCE_ID:
            if _ZIWEI_LATE_ZI_NO_ADVANCE_RE.search(analysis_text):
                return "晚子時規則違反：文字敘述出現『日不進位/不換日』等不進位說法"

    return None


def _build_ziwei_source_signature(*, birth_date: str, birth_time: str, birth_location: str, gender: str, ruleset_id: str = _ZIWEI_DEFAULT_RULESET_ID) -> str:
    payload = {
        'pipeline': _ZIWEI_PIPELINE_VERSION,
        'ruleset': _normalize_ziwei_ruleset_id(ruleset_id),
        'birth_date': birth_date,
        'birth_time': birth_time,
        'birth_location': birth_location,
        'gender': gender,
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def _build_ziwei_repair_prompt(*, original_prompt: str, rule_error: str, ruleset_id: str = _ZIWEI_DEFAULT_RULESET_ID) -> str:
    cfg = _get_ziwei_ruleset_config(ruleset_id)
    expected = cfg.get('late_zi_rule_value', _ZIWEI_LATE_ZI_EXPECTED_RULE)
    return (
        "你上一輪輸出違反了本系統的排盤規則或自我矛盾。\n"
        f"問題：{rule_error}\n\n"
        "請重新完整輸出一次（包含 JSON + 命盤圖 + 全文分析），並嚴格遵守：\n"
        f"- 晚子時以 { _ZIWEI_LATE_ZI_WINDOW } 為準\n"
        f"- 晚子時換日規則必須為『{ expected }』\n"
        "- JSON 的『排盤規則』欄位必須存在且自洽\n"
        + ("- 不得出現『下一個農曆日/隔日』等說法\n\n" if expected == '日不進位' else "- 不得出現『日不進位/不換日』等說法\n\n")
        + "以下是原始需求（請依此重做，不要省略欄位）：\n\n"
        + original_prompt
    )

def _build_user_response(user_row: Dict) -> Dict:
    """將資料庫格式轉為舊版使用者格式"""
    if not user_row:
        return {}
    birth_date = user_row.get('gregorian_birth_date')
    if not birth_date and user_row.get('birth_year') and user_row.get('birth_month') and user_row.get('birth_day'):
        birth_date = f"{user_row['birth_year']}-{int(user_row['birth_month']):02d}-{int(user_row['birth_day']):02d}"
    birth_time = None
    if user_row.get('birth_hour') is not None:
        minute = int(user_row.get('birth_minute') or 0)
        birth_time = f"{int(user_row['birth_hour']):02d}:{minute:02d}"
    return {
        'user_id': user_row.get('user_id'),
        'name': user_row.get('name'),
        'full_name': user_row.get('full_name'),
        'gender': user_row.get('gender'),
        'birth_date': birth_date,
        'birth_time': birth_time,
        'birth_location': user_row.get('birth_location'),
        'longitude': user_row.get('longitude'),
        'latitude': user_row.get('latitude'),
        'gregorian_birth_date': user_row.get('gregorian_birth_date'),
        'created_at': user_row.get('created_at'),
        'updated_at': user_row.get('updated_at')
    }

def get_user(user_id: str) -> Optional[Dict]:
    """取得用戶資料"""
    user_row = db.get_user(user_id)
    if user_row:
        return _build_user_response(user_row)
    # 向後相容：JSON 備援
    if USERS_FILE.exists():
        users = load_json(USERS_FILE)
        return users.get(user_id)
    return None

def save_user(user_id: str, user_data: Dict):
    """儲存用戶資料"""
    birth_date = user_data.get('gregorian_birth_date') or user_data.get('birth_date')
    parsed_date = parse_birth_date_str(birth_date)
    parsed_time = parse_birth_time_str(user_data.get('birth_time'))

    db_payload = {
        'user_id': user_id,
        'name': user_data.get('name'),
        'full_name': user_data.get('full_name'),
        'gender': user_data.get('gender'),
        'birth_year': parsed_date[0] if parsed_date else None,
        'birth_month': parsed_date[1] if parsed_date else None,
        'birth_day': parsed_date[2] if parsed_date else None,
        'birth_hour': parsed_time[0] if parsed_time else None,
        'birth_minute': parsed_time[1] if parsed_time else None,
        'birth_location': user_data.get('birth_location'),
        'longitude': user_data.get('longitude'),
        'latitude': user_data.get('latitude'),
        'gregorian_birth_date': birth_date
    }

    existing = db.get_user(user_id)
    if existing:
        update_payload = {k: v for k, v in db_payload.items() if k != 'user_id' and v is not None}
        if update_payload:
            db.update_user(user_id, update_payload)
    else:
        db.create_user(db_payload)

def get_chart_lock(user_id: str, chart_type: str = 'ziwei') -> Optional[Dict]:
    """取得用戶的鎖定命盤（預設：紫微）"""
    record = db.get_chart_lock(user_id, chart_type)
    if record:
        chart_data = record.get('chart_data') or {}
        if record.get('analysis') and not chart_data.get('original_analysis'):
            chart_data['original_analysis'] = record.get('analysis')
        return chart_data
    # 若紫微鎖盤遺失，嘗試從紫微報告回填
    if chart_type == 'ziwei':
        ziwei_report_wrapper = db.get_system_report(user_id, 'ziwei')
        if ziwei_report_wrapper:
            ziwei_report = ziwei_report_wrapper.get('report', {})
            if ziwei_report.get('chart_structure'):
                fallback_lock = {
                    'user_id': user_id,
                    'chart_type': 'ziwei',
                    'chart_structure': ziwei_report.get('chart_structure'),
                    'original_analysis': ziwei_report.get('analysis', ''),
                    'confirmation_status': 'confirmed',
                    'confirmed_at': datetime.now().isoformat(),
                    'is_active': True
                }
                try:
                    save_chart_lock(user_id, fallback_lock)
                except Exception as e:
                    logger.warning(f'回填鎖盤失敗: {str(e)}', user_id=user_id)
                return fallback_lock
    # 向後相容：JSON 備援
    if LOCKS_FILE.exists():
        locks = load_json(LOCKS_FILE)
        return locks.get(user_id)
    return None

def save_chart_lock(user_id: str, lock_data: Dict):
    """儲存鎖定命盤"""
    chart_type = lock_data.get('chart_type') or 'ziwei'
    analysis = lock_data.get('original_analysis') or lock_data.get('analysis')
    db.save_chart_lock(user_id, chart_type, lock_data, analysis)

def migrate_json_to_sqlite():
    """將舊版 JSON 資料遷移到 SQLite（僅首次）"""
    try:
        if USERS_FILE.exists() and len(db.list_users()) == 0:
            users = load_json(USERS_FILE)
            for user_id, user_data in users.items():
                save_user(user_id, user_data)

        if LOCKS_FILE.exists():
            locks = load_json(LOCKS_FILE)
            for user_id, lock_data in locks.items():
                chart_type = (lock_data or {}).get('chart_type') or 'ziwei'
                if db.get_chart_lock(user_id, chart_type) is None:
                    save_chart_lock(user_id, lock_data)
    except Exception as e:
        logger.warning(f'JSON 遷移到 SQLite 失敗: {str(e)}')

def normalize_gender(value: Optional[str]) -> str:
    """統一性別格式為「男/女/未指定」"""
    if not value:
        return "未指定"
    value = str(value).strip().lower()
    if value in ["男", "male", "m", "man", "男性", "boy"]:
        return "男"
    if value in ["女", "female", "f", "woman", "女性", "girl"]:
        return "女"
    return "未指定"

def suggest_next_steps(message: str) -> list:
    """根據使用者問題提供下一步建議"""
    text = (message or "").lower()
    if any(k in text for k in ["感情", "愛情", "婚姻", "伴侶", "關係"]):
        return ["感情走向細節", "伴侶互動建議", "提升關係的具體做法"]
    if any(k in text for k in ["工作", "事業", "職場", "升遷", "轉職"]):
        return ["近期職場策略", "適合的發展方向", "時間點與節奏"]
    if any(k in text for k in ["財", "金錢", "投資", "理財"]):
        return ["財務風險提醒", "可行的理財步驟", "近期財運節奏"]
    if any(k in text for k in ["健康", "疾病", "身體"]):
        return ["生活作息調整", "壓力與能量平衡", "就醫與檢查提醒"]
    return ["事業方向", "感情關係", "近期決策"]

def build_conversation_log(history: list) -> str:
    """將歷史記錄整理成對話文字"""
    lines = []
    for item in history:
        request_data = item.get('request_data') or {}
        response_data = item.get('response_data') or {}
        user_msg = request_data.get('message')
        ai_msg = response_data.get('reply') or response_data.get('response')
        if user_msg:
            lines.append(f"使用者：{user_msg}")
        if ai_msg:
            lines.append(f"命理老師：{ai_msg}")
    return "\n".join(lines)

def hash_password(password: str) -> Dict[str, str]:
    return auth_utils.hash_password(password)

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    return auth_utils.verify_password(password, stored_hash, salt)

def get_auth_token_from_request(data: Optional[Dict] = None) -> Optional[str]:
    return auth_utils.get_auth_token_from_request(data)

def require_auth_user_id() -> str:
    return auth_utils.require_auth_user_id(db)


def parse_birth_date_str(birth_date_str: Optional[str]) -> Optional[Tuple[int, int, int]]:
    """解析出生日期字串，回傳 (year, month, day)"""
    if not birth_date_str:
        return None
    text = str(birth_date_str).strip()
    # 1) ISO 日期
    try:
        dt = date.fromisoformat(text)
        return dt.year, dt.month, dt.day
    except Exception:
        pass
    # 2) 農曆/民國字串，例如「農曆68年9月23日」
    match = re.search(r'(\d{2,4})年(\d{1,2})月(\d{1,2})日', text)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        if year < 1900:
            year += 1911
        return year, month, day
    return None

def get_user_birth_info(user: Dict) -> Optional[Dict[str, int]]:
    """從用戶資料取得出生年月日（優先使用國曆日期）"""
    if not user:
        return None
    # 1) 國曆生日
    gregorian = user.get('gregorian_birth_date')
    parsed = parse_birth_date_str(gregorian)
    if parsed:
        return {'year': parsed[0], 'month': parsed[1], 'day': parsed[2]}
    # 2) 其他日期欄位
    parsed = parse_birth_date_str(user.get('birth_date'))
    if parsed:
        return {'year': parsed[0], 'month': parsed[1], 'day': parsed[2]}
    return None

# 啟動時嘗試遷移舊版 JSON 資料
migrate_json_to_sqlite()


# ============================================
# 請求日誌中間件
# ============================================

@app.before_request
def log_request_info():
    """記錄每個請求的基本資訊"""
    import time
    request.start_time = time.time()
    if request.endpoint != 'health_check':  # 健康檢查不記錄
        logger.debug(f"收到請求: {request.method} {request.path}")


@app.after_request
def log_response_info(response):
    """記錄每個回應的基本資訊"""
    import time
    if hasattr(request, 'start_time') and request.endpoint != 'health_check':
        duration_ms = (time.time() - request.start_time) * 1000
        logger.log_api_response(
            request.path,
            response.status_code,
            duration_ms
        )
    return response


# ============================================
# Gemini API 呼叫
# ============================================

def call_gemini(
    prompt: str,
    system_instruction: str = SYSTEM_INSTRUCTION,
    max_output_tokens: Optional[int] = None,
    response_mime_type: Optional[str] = None
) -> str:
    """
    呼叫 Gemini API（使用新的 google.genai SDK）
    
    Args:
        prompt: 提示詞
        system_instruction: 系統指令（將前置到 prompt 中）
        max_output_tokens: 最大 Token 數
        response_mime_type: 響應格式
        
    Returns:
        繁體中文的回應文字
    """
    import time
    start_time = time.time()
    
    # 新 SDK 支持 system_instruction (或者我們可以繼續前置)
    # 這裡維持原樣，但加入 response_mime_type
    full_prompt = f"{system_instruction}\n\n{prompt}"
    
    try:
        response_text = gemini_client.generate(
            full_prompt, 
            max_output_tokens=max_output_tokens,
            response_mime_type=response_mime_type
        )

        
        # 檢查回應是否有效
        if response_text is None:
            logger.error("Gemini API 返回 None")
            raise AIAPIException("Gemini API 返回空值")
        
        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"Gemini API 呼叫成功", duration_ms=duration_ms)
        return to_zh_tw(response_text)
    except Exception as e:
        logger.error(f"Gemini API 呼叫失敗: {str(e)}")
        raise AIAPIException(str(e))


def build_astrology_core(natal: Dict) -> Dict:
    """萃取戰略側寫所需的占星核心資料"""
    if not natal:
        return {}
    planets = natal.get("planets", {})
    houses = natal.get("houses", {})
    return {
        "sun": planets.get("sun"),
        "moon": planets.get("moon"),
        "ascendant": planets.get("ascendant"),
        "midheaven": planets.get("midheaven"),
        "house_10": houses.get("house_10"),
        "house_6": houses.get("house_6"),
        "house_2": houses.get("house_2")
    }


def build_meta_profile(
    bazi: Optional[Dict],
    numerology_profile: Optional[Dict],
    name_analysis: Optional[Dict],
    astrology_core: Optional[Dict]
) -> Dict:
    """建立全息側寫 Meta Profile（結構化摘要）"""
    meta = {
        "dominant_elements": [],
        "core_numbers": {},
        "career_axis": {},
        "role_tags": [],
        "risk_flags": []
    }

    if bazi:
        day_master = bazi.get("日主")
        strength = bazi.get("強弱", {}).get("结论") if isinstance(bazi.get("強弱"), dict) else bazi.get("強弱")
        use_god = bazi.get("用神", {}).get("用神") if isinstance(bazi.get("用神"), dict) else bazi.get("用神")
        avoid_god = bazi.get("用神", {}).get("忌神") if isinstance(bazi.get("用神"), dict) else None
        if isinstance(day_master, dict) and day_master.get("五行"):
            meta["dominant_elements"].append(day_master.get("五行"))
        if use_god:
            meta["dominant_elements"].extend(use_god if isinstance(use_god, list) else [use_god])
        if strength:
            meta["risk_flags"].append(f"身弱/身強判定：{strength}")
        if avoid_god:
            meta["risk_flags"].append(f"忌神：{avoid_god}")

    if numerology_profile:
        core = numerology_profile.get("core_numbers", {})
        meta["core_numbers"] = {
            "life_path": core.get("life_path"),
            "expression": core.get("expression"),
            "soul_urge": core.get("soul_urge")
        }
        lp = core.get("life_path")
        if isinstance(lp, dict) and lp.get("is_master"):
            meta["role_tags"].append("master_number")

    if name_analysis:
        grid = name_analysis.get("grid_analyses", {})
        personality = grid.get("人格")
        if isinstance(personality, dict) and personality.get("element"):
            meta["dominant_elements"].append(personality.get("element"))

    if astrology_core:
        mc = astrology_core.get("midheaven", {}) or {}
        house_10 = astrology_core.get("house_10", {}) or {}
        mc_sign = mc.get("sign_zh") or house_10.get("sign_zh")
        if mc_sign:
            meta["career_axis"] = {
                "midheaven_sign": mc_sign
            }
        if mc_sign in ["金牛座", "摩羯座", "處女座"]:
            meta["role_tags"].append("builder")

    # 基礎去重
    meta["dominant_elements"] = list(dict.fromkeys(meta["dominant_elements"]))
    meta["role_tags"] = list(dict.fromkeys(meta["role_tags"]))

    return meta


def build_bazi_candidate_summary(bazi: Dict) -> Dict:
    """將八字輸出壓縮為生辰校正摘要"""
    day_master = bazi.get("日主")
    strength = bazi.get("強弱", {}).get("结论") if isinstance(bazi.get("強弱"), dict) else bazi.get("強弱")
    use_god = bazi.get("用神", {}).get("用神") if isinstance(bazi.get("用神"), dict) else bazi.get("用神")
    hour_pillar = bazi.get("時柱") or bazi.get("时柱")
    return {
        "day_master": day_master,
        "strength": strength,
        "use_god": use_god,
        "hour_pillar": hour_pillar
    }


def _truncate_text(text: Optional[str], max_len: int = 140) -> str:
    if not text:
        return ""
    s = str(text).strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "…"


def _safe_get(d: Optional[Dict], *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur.get(k)
    return cur


def build_fortune_facts_from_reports(reports: Dict[str, Dict]) -> Dict[str, Any]:
    """從 system_reports 建立對話用 facts（可引用、可追溯）。

    回傳：
      {
        "facts": [{"id","system","title","content","path"}],
        "meta": {...},
        "available_systems": [...]
      }
    """
    facts = []
    available_systems = []

    def add_fact(fact_id: str, system: str, title: str, content: str, path: str):
        content_s = _truncate_text(content, 220)
        if not content_s:
            return
        facts.append({
            "id": fact_id,
            "system": system,
            "title": title,
            "content": content_s,
            "path": path
        })

    # Ziwei
    ziwei = (reports.get('ziwei') or {}).get('report') or {}
    if ziwei:
        available_systems.append('ziwei')
        structure = ziwei.get('chart_structure') or {}
        if isinstance(structure, dict) and structure:
            add_fact('ziwei:五行局', 'ziwei', '五行局', structure.get('五行局') or structure.get('局') or '', 'ziwei.chart_structure.五行局')
            if isinstance(structure.get('格局'), list) and structure.get('格局'):
                add_fact('ziwei:格局', 'ziwei', '格局', '、'.join(structure.get('格局')), 'ziwei.chart_structure.格局')
            ming = structure.get('命宮')
            if isinstance(ming, dict):
                content = f"地支：{ming.get('地支') or ''}；主星：{'、'.join(ming.get('主星') or [])}；輔星：{'、'.join(ming.get('輔星') or [])}"
                add_fact('ziwei:命宮', 'ziwei', '命宮', content, 'ziwei.chart_structure.命宮')

            twelve = structure.get('十二宮') if isinstance(structure.get('十二宮'), dict) else {}
            key_palaces = ['官祿宮', '財帛宮', '夫妻宮', '福德宮', '疾厄宮', '遷移宮']
            for palace in key_palaces:
                p = twelve.get(palace)
                if isinstance(p, dict):
                    branch = p.get('地支') or p.get('宮位') or ''
                    main = p.get('主星') or []
                    aux = p.get('輔星') or []
                    content = f"地支：{branch}；主星：{'、'.join(main)}；輔星：{'、'.join(aux)}"
                    add_fact(f'ziwei:{palace}', 'ziwei', palace, content, f'ziwei.chart_structure.十二宮.{palace}')

    # Bazi
    bazi = (reports.get('bazi') or {}).get('report') or {}
    bazi_chart = bazi.get('bazi_chart') if isinstance(bazi, dict) else None
    if isinstance(bazi_chart, dict) and bazi_chart:
        available_systems.append('bazi')
        day_master = _safe_get(bazi_chart, '日主', '天干')
        day_wuxing = _safe_get(bazi_chart, '日主', '五行')
        if day_master or day_wuxing:
            add_fact('bazi:日主', 'bazi', '日主', f"{day_master or ''}（{day_wuxing or ''}）", 'bazi.bazi_chart.日主')
        strength = _safe_get(bazi_chart, '強弱', '结论') or _safe_get(bazi_chart, '强弱', '结论')
        if strength:
            add_fact('bazi:強弱', 'bazi', '強弱', str(strength), 'bazi.bazi_chart.強弱.结论')
        yongshen = _safe_get(bazi_chart, '用神', '用神')
        if yongshen:
            add_fact('bazi:用神', 'bazi', '用神', '、'.join(yongshen) if isinstance(yongshen, list) else str(yongshen), 'bazi.bazi_chart.用神.用神')
        pillars = _safe_get(bazi_chart, '四柱') or {}
        if isinstance(pillars, dict) and pillars:
            def pillar_text(p):
                if not isinstance(p, dict):
                    return ''
                return f"{p.get('天干','')}{p.get('地支','')}"
            content = " ".join([
                f"年{pillar_text(pillars.get('年柱'))}",
                f"月{pillar_text(pillars.get('月柱'))}",
                f"日{pillar_text(pillars.get('日柱'))}",
                f"時{pillar_text(pillars.get('時柱') or pillars.get('时柱'))}",
            ]).strip()
            add_fact('bazi:四柱', 'bazi', '四柱', content, 'bazi.bazi_chart.四柱')

    # Numerology
    numerology = (reports.get('numerology') or {}).get('report') or {}
    num_profile = numerology.get('profile') if isinstance(numerology, dict) else None
    if isinstance(num_profile, dict) and num_profile:
        available_systems.append('numerology')
        core = num_profile.get('core_numbers') or {}
        lp = (core.get('life_path') or {}) if isinstance(core.get('life_path'), dict) else {}
        if lp.get('number') is not None:
            add_fact('numerology:生命靈數', 'numerology', '生命靈數', f"{lp.get('number')}{'（主數）' if lp.get('is_master') else ''}", 'numerology.profile.core_numbers.life_path')
        expr = (core.get('expression') or {}) if isinstance(core.get('expression'), dict) else {}
        if expr.get('number') is not None:
            add_fact('numerology:天賦數', 'numerology', '天賦數', f"{expr.get('number')}{'（主數）' if expr.get('is_master') else ''}", 'numerology.profile.core_numbers.expression')
        su = (core.get('soul_urge') or {}) if isinstance(core.get('soul_urge'), dict) else {}
        if su.get('number') is not None:
            add_fact('numerology:靈魂渴望數', 'numerology', '靈魂渴望數', f"{su.get('number')}{'（主數）' if su.get('is_master') else ''}", 'numerology.profile.core_numbers.soul_urge')
        cycles = num_profile.get('cycles') or {}
        py = (cycles.get('personal_year') or {}) if isinstance(cycles.get('personal_year'), dict) else {}
        if py.get('number') is not None:
            add_fact('numerology:流年', 'numerology', '個人流年', f"{py.get('number')}", 'numerology.profile.cycles.personal_year')

    # Name
    name = (reports.get('name') or {}).get('report') or {}
    five_grids = name.get('five_grids') if isinstance(name, dict) else None
    if isinstance(five_grids, dict) and five_grids:
        available_systems.append('name')
        overall = five_grids.get('overall_fortune')
        if overall:
            add_fact('name:總評', 'name', '姓名學總評', str(overall), 'name.five_grids.overall_fortune')
        grids = five_grids.get('five_grids') or {}
        if isinstance(grids, dict) and grids:
            content = f"天格{grids.get('天格')} 人格{grids.get('人格')} 地格{grids.get('地格')} 外格{grids.get('外格')} 總格{grids.get('總格')}"
            add_fact('name:五格', 'name', '五格數理', content, 'name.five_grids.five_grids')
        three = five_grids.get('three_talents') or {}
        if isinstance(three, dict) and three.get('combination'):
            add_fact('name:三才', 'name', '三才配置', f"{three.get('combination')}（{three.get('fortune') or ''}）", 'name.five_grids.three_talents')

    # Astrology
    astrology = (reports.get('astrology') or {}).get('report') or {}
    natal = astrology.get('natal_chart') if isinstance(astrology, dict) else None
    if isinstance(natal, dict) and natal:
        available_systems.append('astrology')
        planets = natal.get('planets') or {}
        sun = planets.get('sun') or {}
        moon = planets.get('moon') or {}
        asc = planets.get('ascendant') or {}
        if isinstance(sun, dict) and sun.get('sign_zh'):
            add_fact('astrology:太陽', 'astrology', '太陽星座', f"{sun.get('sign_zh')}（第{sun.get('house')}宮）", 'astrology.natal_chart.planets.sun')
        if isinstance(moon, dict) and moon.get('sign_zh'):
            add_fact('astrology:月亮', 'astrology', '月亮星座', f"{moon.get('sign_zh')}（第{moon.get('house')}宮）", 'astrology.natal_chart.planets.moon')
        if isinstance(asc, dict) and asc.get('sign_zh'):
            add_fact('astrology:上升', 'astrology', '上升星座', f"{asc.get('sign_zh')}（{asc.get('degree'):.1f}°）", 'astrology.natal_chart.planets.ascendant')
        if natal.get('chart_ruler'):
            add_fact('astrology:命主星', 'astrology', '命主星（Chart Ruler）', str(natal.get('chart_ruler')), 'astrology.natal_chart.chart_ruler')
        if natal.get('dominant_element'):
            add_fact('astrology:主元素', 'astrology', '主導元素', str(natal.get('dominant_element')), 'astrology.natal_chart.dominant_element')

    # Meta profile（供模型抓跨系統一致性，但仍需 cite facts）
    meta_profile = build_meta_profile(
        bazi_chart if isinstance(bazi_chart, dict) else None,
        num_profile if isinstance(num_profile, dict) else None,
        five_grids if isinstance(five_grids, dict) else None,
        build_astrology_core(natal) if isinstance(natal, dict) else None
    )

    # 去重（同 id 只保留第一筆）
    dedup = {}
    for f in facts:
        if f['id'] not in dedup:
            dedup[f['id']] = f

    return {
        'facts': list(dedup.values()),
        'meta': meta_profile,
        'available_systems': list(dict.fromkeys(available_systems))
    }


def compute_reports_signature(reports: Dict[str, Dict]) -> str:
    """以各系統 updated_at 組合成快取簽章，便於判斷 fortune_profile 是否過期。"""
    parts = []
    for system_type in sorted(reports.keys()):
        updated_at = (reports.get(system_type) or {}).get('updated_at') or ''
        parts.append(f"{system_type}:{updated_at}")
    return "|".join(parts)


def parse_json_object(text: str) -> Optional[Dict]:
    """從模型輸出中抓第一個 JSON object。"""
    if not text:
        return None
    s = text.strip()
    # 去掉 ```json ... ``` 包裹
    s = re.sub(r"^```json\s*", "", s, flags=re.IGNORECASE)
    s = re.sub(r"```\s*$", "", s)
    # 直接嘗試
    try:
        obj = json.loads(s)
        return obj if isinstance(obj, dict) else None
    except Exception:
        pass
    # 退而求其次：抓第一段 {...}
    match = re.search(r"\{[\s\S]*\}", s)
    if not match:
        return None
    try:
        obj = json.loads(match.group(0))
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def humanize_citation_path(path: str) -> str:
    """將技術性 path 轉為人類可讀格式
    
    範例：
      bazi.bazi_chart.日主 → 八字 > 四柱 > 日主
      ziwei.chart_structure.命宮 → 紫微斗數 > 命盤結構 > 命宮
    """
    if not path:
        return ''
    
    # 系統名稱映射
    system_map = {
        'ziwei': '紫微斗數',
        'bazi': '八字',
        'astrology': '西洋占星',
        'numerology': '靈數學',
        'name': '姓名學',
        'tarot': '塔羅'
    }
    
    # 中間層級映射
    level_map = {
        'chart_structure': '命盤結構',
        'bazi_chart': '四柱',
        'natal_chart': '本命盤',
        'planets': '行星',
        'profile': '命數檔案',
        'core_numbers': '核心數字',
        'five_grids': '五格',
        'cycles': '流年週期',
        '十二宮': '十二宮',
        # 行星名稱（西洋占星）
        'sun': '太陽',
        'moon': '月亮',
        'mercury': '水星',
        'venus': '金星',
        'mars': '火星',
        'jupiter': '木星',
        'saturn': '土星',
        'uranus': '天王星',
        'neptune': '海王星',
        'pluto': '冥王星',
        'ascendant': '上升點',
        'midheaven': '中天',
        # 靈數學
        'life_path': '生命靈數',
        'expression': '表達數',
        'soul_urge': '靈魂數',
        'birthday': '生日數',
        'personality': '人格數',
        # 姓名學
        'tian_ge': '天格',
        'ren_ge': '人格',
        'di_ge': '地格',
        'wai_ge': '外格',
        'zong_ge': '總格'
    }
    
    parts = path.split('.')
    readable_parts = []
    
    for part in parts:
        # 系統名稱
        if part in system_map:
            readable_parts.append(system_map[part])
        # 中間層級
        elif part in level_map:
            readable_parts.append(level_map[part])
        # 其他保留原樣（通常是中文key）
        else:
            readable_parts.append(part)
    
    return ' > '.join(readable_parts)

# ============================================
# API 路由
# ============================================

@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查"""
    logger.debug("健康檢查請求")
    return jsonify({'status': 'ok', 'service': 'Aetheria Chart Locking API'})

# ============================================
# 會員資料與設定
# ============================================


@app.route('/api/profile', methods=['GET'])
def get_profile():
    """取得會員資料與生辰資料"""
    user_id = require_auth_user_id()
    member = db.get_member_by_user_id(user_id) or {}
    prefs = db.get_member_preferences(user_id) or {}
    consents = db.get_member_consents(user_id) or {}
    
    # 取得生辰資料
    user_data = db.get_user(user_id)
    birth_info = None
    if user_data and user_data.get('user_id'):  # 确保有实际数据
        birth_date = None
        if user_data.get('birth_year') and user_data.get('birth_month') and user_data.get('birth_day'):
            birth_date = f"{user_data.get('birth_year')}-{str(user_data.get('birth_month')).zfill(2)}-{str(user_data.get('birth_day')).zfill(2)}"
        
        birth_time = None
        if user_data.get('birth_hour') is not None:
            hour = str(user_data.get('birth_hour')).zfill(2)
            minute = str(user_data.get('birth_minute', 0)).zfill(2)
            birth_time = f"{hour}:{minute}"
        
        birth_info = {
            'name': user_data.get('name') or user_data.get('full_name'),
            'gender': user_data.get('gender'),
            'birth_date': birth_date,
            'birth_time': birth_time,
            'birth_location': user_data.get('birth_location'),
            'longitude': user_data.get('longitude'),
            'latitude': user_data.get('latitude'),
            'has_chart': db.get_chart_lock(user_id) is not None
        }

    return jsonify({
        'status': 'success',
        'profile': {
            'user_id': user_id,
            'email': member.get('email'),
            'phone': member.get('phone'),
            'display_name': member.get('display_name'),
            'created_at': member.get('created_at')
        },
        'birth_info': birth_info,
        'preferences': prefs,
        'consents': consents
    })

@app.route('/api/profile', methods=['PATCH'])
def update_profile():
    """更新會員資料與偏好"""
    data = request.json or {}
    user_id = require_auth_user_id()

    profile_updates = {}
    for key in ['phone', 'display_name']:
        if key in data:
            profile_updates[key] = data.get(key)

    if profile_updates:
        db.update_member(user_id, profile_updates)

    if 'preferences' in data:
        db.save_member_preferences(user_id, data.get('preferences') or {})

    return jsonify({'status': 'success'})

@app.route('/api/consent', methods=['POST'])
def update_consent():
    """更新會員同意紀錄"""
    data = request.json or {}
    user_id = require_auth_user_id()
    db.save_member_consents(user_id, data)
    return jsonify({'status': 'success'})

@app.route('/api/profile/birth-info', methods=['PUT'])
def update_birth_info():
    """
    更新生辰資料
    
    Request:
    {
        "name": "張小明",
        "gender": "男",
        "birth_date": "1995-03-15",
        "birth_time": "14:30",
        "birth_location": "台灣台北市"
    }
    """
    data = request.json or {}
    user_id = require_auth_user_id()
    
    # 驗證必填欄位
    if not data.get('birth_date') or not data.get('birth_time') or not data.get('birth_location'):
        return jsonify({
            'status': 'error',
            'error': '生辰資料不完整（需要出生日期、時間、地點）'
        }), 400
    
    # 解析日期時間
    birth_date = data.get('birth_date')
    birth_time = data.get('birth_time')
    parsed_date = parse_birth_date_str(birth_date)
    parsed_time = parse_birth_time_str(birth_time)
    
    if not parsed_date or not parsed_time:
        return jsonify({
            'status': 'error',
            'error': '日期或時間格式錯誤'
        }), 400
    
    # 組合更新資料
    update_data = {
        'name': data.get('name'),
        'full_name': data.get('name'),
        'gender': data.get('gender'),
        'birth_year': parsed_date[0],
        'birth_month': parsed_date[1],
        'birth_day': parsed_date[2],
        'birth_hour': parsed_time[0],
        'birth_minute': parsed_time[1],
        'birth_location': data.get('birth_location'),
        'gregorian_birth_date': birth_date
    }
    
    # 如果有經緯度就更新
    if 'longitude' in data:
        update_data['longitude'] = data.get('longitude')
    if 'latitude' in data:
        update_data['latitude'] = data.get('latitude')
    
    # 更新資料庫
    try:
        existing = db.get_user(user_id)
        if existing:
            db.update_user(user_id, update_data)
        else:
            update_data['user_id'] = user_id
            db.create_user(update_data)
        
        return jsonify({
            'status': 'success',
            'message': '生辰資料已更新'
        })
    except Exception as e:
        logger.error(f'更新生辰資料失敗: {str(e)}', user_id=user_id)
        return jsonify({
            'status': 'error',
            'error': '資料更新失敗'
        }), 500

@app.route('/api/chart/initial-analysis', methods=['POST'])
def initial_analysis():
    """
    首次命盤分析
    
    Request:
    {
        "user_id": "user_123",
        "birth_date": "農曆68年9月23日",
        "birth_time": "23:58",
        "birth_location": "台灣彰化市",
        "gender": "男"
    }
    
    Response:
    {
        "analysis": "完整分析文字",
        "structure": {...},
        "lock_id": "user_123",
        "needs_confirmation": true
    }
    """
    import time
    start_time = time.time()
    
    data = request.json
    user_id = data.get('user_id')
    
    # 參數驗證
    if not user_id:
        raise MissingParameterException('user_id')
    
    logger.log_api_request('/api/chart/initial-analysis', 'POST', user_id=user_id)
    
    try:
        requested_ruleset_id = _normalize_ziwei_ruleset_id(data.get('ziwei_ruleset'))
        ruleset_cfg = _get_ziwei_ruleset_config(requested_ruleset_id)

        # 儲存用戶基本資料
        user_data = {
            'user_id': user_id,
            'birth_date': data['birth_date'],
            'birth_time': data['birth_time'],
            'birth_location': data['birth_location'],
            'gender': data['gender'],
            'created_at': datetime.now().isoformat()
        }
        save_user(user_id, user_data)
        
        # 組合 Prompt
        prompt = INITIAL_ANALYSIS_PROMPT.format(
            birth_date=data['birth_date'],
            birth_time=data['birth_time'],
            birth_location=data['birth_location'],
            gender=data['gender'],
            late_zi_rule_value=ruleset_cfg['late_zi_rule_value'],
            late_zi_logic_md=ruleset_cfg['late_zi_logic_md']
        )
        
        # 呼叫 Gemini
        logger.info(f'正在為用戶 {user_id} 生成命盤...', user_id=user_id)
        analysis = call_gemini(prompt)

        # 提取結構
        structure = extractor.extract_full_structure(analysis)

        # 驗證結構
        is_valid, errors = extractor.validate_structure(structure)
        if not is_valid:
            logger.warning(f'命盤結構提取不完整', user_id=user_id, errors=errors)

        # 規則一致性驗證（治本：禁止晚子時規則漂移）
        rule_error = _validate_ziwei_rule_consistency(
            birth_date=data['birth_date'],
            birth_time=data['birth_time'],
            structure=structure,
            analysis_text=analysis,
            ruleset_id=requested_ruleset_id
        )
        if rule_error:
            logger.warning('紫微排盤規則不一致，嘗試修復重算一次', user_id=user_id, rule_error=rule_error)
            repair_prompt = _build_ziwei_repair_prompt(original_prompt=prompt, rule_error=rule_error, ruleset_id=requested_ruleset_id)
            analysis = call_gemini(repair_prompt)
            structure = extractor.extract_full_structure(analysis)
            is_valid, errors = extractor.validate_structure(structure)
            rule_error = _validate_ziwei_rule_consistency(
                birth_date=data['birth_date'],
                birth_time=data['birth_time'],
                structure=structure,
                analysis_text=analysis,
                ruleset_id=requested_ruleset_id
            )
            if rule_error:
                errors = (errors or []) + [f'規則驗證失敗：{rule_error}']
                logger.warning('紫微排盤規則修復後仍不一致', user_id=user_id, rule_error=rule_error)

        # 暫存到資料庫（待確認）
        source_signature = _build_ziwei_source_signature(
            birth_date=data['birth_date'],
            birth_time=data['birth_time'],
            birth_location=data['birth_location'],
            gender=data['gender'],
            ruleset_id=requested_ruleset_id
        )
        temp_lock = {
            'user_id': user_id,
            'chart_type': 'ziwei',
            'chart_structure': structure,
            'original_analysis': analysis,
            'provenance': {
                'ruleset': requested_ruleset_id,
                'pipeline': _ZIWEI_PIPELINE_VERSION,
                'source_signature': source_signature,
                'model_name': getattr(gemini_client, 'model_name', None),
                'temperature': getattr(gemini_client, 'default_config', {}).get('temperature') if hasattr(gemini_client, 'default_config') else None,
            },
            'source_signature': source_signature,
            'confirmation_status': 'pending',
            'created_at': datetime.now().isoformat(),
            'is_active': False
        }
        if errors:
            temp_lock['errors'] = errors
        save_chart_lock(user_id, temp_lock)
        
        duration_ms = (time.time() - start_time) * 1000
        logger.log_api_response('/api/chart/initial-analysis', 200, duration_ms)
        logger.info(f'命盤生成完成，等待用戶確認', user_id=user_id)
        
        return jsonify({
            'status': 'success',
            'analysis': analysis,
            'structure': structure,
            'lock_id': user_id,
            'needs_confirmation': True,
            'warning': None if is_valid else '命盤結構提取不完整',
            'errors': errors if errors else []
        })
        
    except AetheriaException:
        raise  # 讓錯誤處理器處理
    except Exception as e:
        logger.error(f'命盤分析失敗: {str(e)}', user_id=user_id)
        return jsonify({'status': 'error', 'error': str(e)}), 500


@app.route('/api/profile/save-and-analyze', methods=['POST'])
def save_profile_and_analyze():
    """
    儲存個人資料並批次生成所有可用系統的報告
    
    這是新的「儲存資料」流程，一次性生成所有報告
    
    Request:
    {
        "user_id": "user_123",
        "chinese_name": "張小明",
        "gender": "男",
        "birth_date": "1990-01-15",      // 國曆
        "birth_time": "14:30",           // 選填
        "birth_location": "台灣台北市"    // 選填
    }
    
    Response:
    {
        "status": "success",
        "profile_saved": true,
        "reports_generated": {
            "name": true,
            "numerology": true,
            "bazi": true,
            "ziwei": true,
            "astrology": true
        },
        "available_systems": ["tarot", "name", "numerology", "bazi", "ziwei", "astrology"],
        "generation_progress": {...}
    }
    """
    import time
    start_time = time.time()
    
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'error': '缺少請求資料'}), 400
    
    user_id = data.get('user_id')
    
    if not user_id:
        raise MissingParameterException('user_id')
    
    logger.log_api_request('/api/profile/save-and-analyze', 'POST', user_id=user_id)
    
    # 收集資料
    chinese_name = data.get('chinese_name', '')
    gender = data.get('gender', '男')
    birth_date = data.get('birth_date', '')  # 格式: YYYY-MM-DD
    birth_time = data.get('birth_time', '')  # 格式: HH:MM
    birth_location = data.get('birth_location', '')
    force_regenerate = data.get('force_regenerate', False)  # 是否強制重新生成
    requested_ziwei_ruleset_id = _normalize_ziwei_ruleset_id(data.get('ziwei_ruleset'))
    
    # 決定可用的系統
    available_systems = ['tarot']  # 塔羅永遠可用
    if chinese_name:
        available_systems.append('name')
    if birth_date:
        available_systems.append('numerology')
    if birth_date and birth_time:
        available_systems.extend(['bazi', 'ziwei'])
    if birth_date and birth_time and birth_location:
        available_systems.append('astrology')

    # 若指定目標系統，則只生成指定範圍
    requested_systems = data.get('target_systems') or data.get('available_systems')
    if isinstance(requested_systems, list) and requested_systems:
        available_systems = [s for s in available_systems if s in requested_systems]
    
    # 儲存用戶資料
    user_data = {
        'user_id': user_id,
        'name': chinese_name,
        'gender': gender,
        'birth_date': birth_date,
        'birth_time': birth_time,
        'birth_location': birth_location,
        'created_at': datetime.now().isoformat()
    }
    save_user(user_id, user_data)
    
    # 強制重生：先清空舊報告與鎖盤
    if force_regenerate:
        try:
            db.delete_system_reports(user_id)
        except Exception as e:
            logger.warning(f'清除舊報告失敗: {str(e)}', user_id=user_id)
        try:
            db.delete_chart_lock(user_id)
        except Exception as e:
            logger.warning(f'清除鎖盤失敗: {str(e)}', user_id=user_id)
        # 兼容舊 JSON 鎖盤
        try:
            if LOCKS_FILE.exists():
                locks = load_json(LOCKS_FILE)
                if user_id in locks:
                    del locks[user_id]
                    LOCKS_FILE.write_text(json.dumps(locks, ensure_ascii=False, indent=2), encoding='utf-8')
        except Exception as e:
            logger.warning(f'清除 JSON 鎖盤失敗: {str(e)}', user_id=user_id)

    # 批次生成報告
    reports_generated = {}
    generation_errors = {}
    
    # 解析出生日期時間
    birth_year, birth_month, birth_day = None, None, None
    birth_hour, birth_minute = 0, 0
    if birth_date:
        try:
            from datetime import date as date_type
            bd = date_type.fromisoformat(birth_date)
            birth_year, birth_month, birth_day = bd.year, bd.month, bd.day
        except:
            pass
    if birth_time:
        try:
            parts = birth_time.split(':')
            birth_hour = int(parts[0])
            birth_minute = int(parts[1]) if len(parts) > 1 else 0
        except:
            pass
    
    try:
        # 1. 姓名學
        # === 並行生成報告優化 ===
        def run_name_calc():
            try:
                if 'name' not in available_systems or not chinese_name: return ('name', False, None, False)
                
                # Check cache (thread-safe read)
                existing = db.get_system_report(user_id, 'name')
                if existing and not force_regenerate:
                    logger.info('姓名學報告已存在，跳過生成', user_id=user_id)
                    return ('name', True, None, True)
                
                logger.info('生成姓名學報告(Thread)...', user_id=user_id)
                name_analysis_obj = name_calc.analyze(chinese_name)
                name_result = name_calc.to_dict(name_analysis_obj)
                prompts = generate_name_prompt(name_analysis_obj, 'basic')
                full_prompt = f"{prompts['system_prompt']}\n\n{prompts['user_prompt']}"
                name_interpretation = sanitize_plain_text(call_gemini(full_prompt))
                
                return ('name', True, {
                    'chinese_name': chinese_name,
                    'gender': gender,
                    'five_grids': name_result,
                    'analysis': name_interpretation
                }, False)
            except Exception as e:
                return ('name', False, str(e), False)

        def run_numerology_calc():
            try:
                if 'numerology' not in available_systems or not (birth_date and birth_year): return ('numerology', False, None, False)
                existing = db.get_system_report(user_id, 'numerology')
                if existing and not force_regenerate:
                    logger.info('靈數學報告已存在，跳過生成', user_id=user_id)
                    return ('numerology', True, None, True)
                
                logger.info('生成靈數學報告(Thread)...', user_id=user_id)
                from datetime import date as date_type
                bd = date_type(birth_year, birth_month, birth_day)
                profile = numerology_calc.calculate_full_profile(bd, chinese_name or '')
                prompts = generate_numerology_prompt(profile, numerology_calc, 'full', 'general')
                full_prompt = f"{prompts['system_prompt']}\n\n{prompts['user_prompt']}"
                numerology_interpretation = sanitize_plain_text(call_gemini(full_prompt))
                numerology_result = numerology_calc.to_dict(profile)
                
                return ('numerology', True, {
                    'birth_date': birth_date,
                    'name': chinese_name,
                    'profile': numerology_result,
                    'analysis': numerology_interpretation
                }, False)
            except Exception as e:
                return ('numerology', False, str(e), False)

        def run_bazi_calc():
            try:
                if 'bazi' not in available_systems or not (birth_date and birth_time and birth_year): return ('bazi', False, None, False)
                existing = db.get_system_report(user_id, 'bazi')
                if existing and not force_regenerate:
                    logger.info('八字報告已存在，跳過生成', user_id=user_id)
                    return ('bazi', True, None, True)
                
                logger.info('生成八字報告(Thread)...', user_id=user_id)
                bazi_calculator = BaziCalculator()
                gender_normalized = normalize_gender(gender)
                bazi_result = bazi_calculator.calculate_bazi(birth_year, birth_month, birth_day, birth_hour, birth_minute, gender_normalized)
                bazi_prompt = format_bazi_analysis_prompt(bazi_result, gender_normalized, birth_year, birth_month, birth_day, birth_hour)
                bazi_analysis = sanitize_plain_text(call_gemini(bazi_prompt))
                
                return ('bazi', True, {
                    'birth_date': birth_date,
                    'birth_time': birth_time,
                    'gender': gender,
                    'bazi_chart': bazi_result,
                    'analysis': bazi_analysis
                }, False)
            except Exception as e:
                return ('bazi', False, str(e), False)

        def run_ziwei_calc():
            try:
                if 'ziwei' not in available_systems or not (birth_date and birth_time): return ('ziwei', False, None, False)
                existing = db.get_system_report(user_id, 'ziwei')
                if existing and not force_regenerate:
                    logger.info('紫微斗數報告已存在，跳過生成', user_id=user_id)
                    return ('ziwei', True, None, True)

                # Lock-first: if we already have a confirmed Ziwei chart, reuse it to avoid drift.
                lock = get_chart_lock(user_id, 'ziwei')
                if lock and lock.get('chart_structure') and not force_regenerate:
                    logger.info('使用已鎖定紫微命盤生成報告（避免重新排盤漂移）', user_id=user_id)
                    lock_ruleset_id = None
                    try:
                        lock_ruleset_id = (lock.get('provenance') or {}).get('ruleset')
                    except Exception:
                        lock_ruleset_id = None
                    effective_ruleset_id = _normalize_ziwei_ruleset_id(lock_ruleset_id) if lock_ruleset_id else requested_ziwei_ruleset_id

                    # 重要：不要直接沿用舊 raw 分析（可能含「晚子時進位」等歷史漂移敘事），
                    # 一律以鎖定盤面重新解讀，確保後續輸出不再自相矛盾。
                    structure = lock.get('chart_structure') or {}
                    life_palace = structure.get('命宮', {}) if isinstance(structure, dict) else {}
                    main_stars = life_palace.get('主星') or []
                    main_stars_text = ', '.join(main_stars) if main_stars else '未提及'
                    life_palace_pos = life_palace.get('宮位', '未提及')
                    pattern_text = ', '.join(structure.get('格局', []) or []) if isinstance(structure, dict) else ''
                    pattern_text = pattern_text or '未提及'
                    five_elements = structure.get('五行局', '未提及') if isinstance(structure, dict) else '未提及'

                    structure_text = f"""
命宮：{main_stars_text} ({life_palace_pos}宮)
格局：{pattern_text}
五行局：{five_elements}

十二宮配置：
"""
                    for palace, info in (structure.get('十二宮', {}) or {}).items() if isinstance(structure, dict) else []:
                        stars = ', '.join(info.get('主星') or []) if info else '空宮'
                        palace_pos = info.get('宮位') if info else None
                        palace_pos_text = palace_pos if palace_pos else '未提及'
                        structure_text += f"- {palace} ({palace_pos_text}宮): {stars}\n"

                    ruleset_cfg = _get_ziwei_ruleset_config(effective_ruleset_id)
                    interpretation_prompt = (
                        "你是 Aetheria，精通紫微斗數的 AI 命理顧問。\n\n"
                        "【語言要求】全文僅使用台灣繁體中文（zh-TW）。\n\n"
                        "【重要規則】\n"
                        f"- 本次晚子時換日規則：{ruleset_cfg['late_zi_rule_value']}\n"
                        "- 嚴禁重新排盤、嚴禁改動宮位/星曜配置、嚴禁提出『兩種規則都可能』\n\n"
                        "【已鎖定的命盤結構】\n"
                        f"{structure_text}\n\n"
                        "【輸出要求】\n"
                        "請輸出一份完整的紫微斗數解讀報告（Markdown），至少包含：\n"
                        "### 一、命盤基礎結構\n"
                        "### 二、十二宮重點（命/財/官/遷/夫妻）\n"
                        "### 三、性格與決策風格\n"
                        "### 四、事業與財務策略\n"
                        "### 五、關係/婚姻互動建議\n"
                        "最後以 3 條可執行建議收束。\n"
                    )

                    locked_analysis = ''
                    try:
                        locked_analysis = sanitize_plain_text(call_gemini(interpretation_prompt))
                    except Exception as e:
                        logger.warning(f'鎖定盤面解讀失敗，回退使用舊分析摘要: {str(e)}', user_id=user_id)
                        locked_raw = lock.get('original_analysis') or ''
                        locked_analysis = sanitize_plain_text(strip_first_json_block(locked_raw)) if locked_raw else ''

                    return ('ziwei', True, {
                        'birth_date': birth_date,
                        'birth_time': birth_time,
                        'birth_location': birth_location,
                        'gender': gender,
                        'chart_structure': structure,
                        'analysis': locked_analysis,
                        'original_analysis': lock.get('original_analysis') or '',
                        'provenance': {
                            **(lock.get('provenance') or {}),
                            'effective_ruleset': effective_ruleset_id,
                            'requested_ruleset': requested_ziwei_ruleset_id,
                        },
                        'source_signature': lock.get('source_signature'),
                    }, False)
                
                logger.info('生成紫微斗數報告(Thread)...', user_id=user_id)
                ruleset_cfg = _get_ziwei_ruleset_config(requested_ziwei_ruleset_id)
                ziwei_prompt = INITIAL_ANALYSIS_PROMPT.format(
                    birth_date=birth_date,
                    birth_time=birth_time,
                    birth_location=birth_location or '台灣',
                    gender=gender,
                    late_zi_rule_value=ruleset_cfg['late_zi_rule_value'],
                    late_zi_logic_md=ruleset_cfg['late_zi_logic_md']
                )
                raw_ziwei_analysis = call_gemini(ziwei_prompt)
                if not raw_ziwei_analysis: raise ValueError("Gemini API 未返回有效內容")

                structure = extractor.extract_full_structure(raw_ziwei_analysis)

                # 規則一致性驗證（治本：禁止晚子時規則漂移）
                rule_error = _validate_ziwei_rule_consistency(
                    birth_date=birth_date,
                    birth_time=birth_time,
                    structure=structure,
                    analysis_text=raw_ziwei_analysis,
                    ruleset_id=requested_ziwei_ruleset_id
                )
                if rule_error:
                    logger.warning('紫微排盤規則不一致，嘗試修復重算一次', user_id=user_id, rule_error=rule_error)
                    repair_prompt = _build_ziwei_repair_prompt(original_prompt=ziwei_prompt, rule_error=rule_error, ruleset_id=requested_ziwei_ruleset_id)
                    raw_ziwei_analysis = call_gemini(repair_prompt)
                    if not raw_ziwei_analysis:
                        raise ValueError('Gemini API 修復重算未返回有效內容')
                    structure = extractor.extract_full_structure(raw_ziwei_analysis)
                    rule_error = _validate_ziwei_rule_consistency(
                        birth_date=birth_date,
                        birth_time=birth_time,
                        structure=structure,
                        analysis_text=raw_ziwei_analysis,
                        ruleset_id=requested_ziwei_ruleset_id
                    )
                    if rule_error:
                        logger.warning('紫微排盤規則修復後仍不一致（仍保存，但標記 provenance.errors）', user_id=user_id, rule_error=rule_error)

                ziwei_analysis = sanitize_plain_text(strip_first_json_block(raw_ziwei_analysis))

                source_signature = _build_ziwei_source_signature(
                    birth_date=birth_date,
                    birth_time=birth_time,
                    birth_location=birth_location or '台灣',
                    gender=gender,
                    ruleset_id=requested_ziwei_ruleset_id
                )
                provenance = {
                    'ruleset': requested_ziwei_ruleset_id,
                    'pipeline': _ZIWEI_PIPELINE_VERSION,
                    'source_signature': source_signature,
                    'model_name': getattr(gemini_client, 'model_name', None),
                    'temperature': getattr(gemini_client, 'default_config', {}).get('temperature') if hasattr(gemini_client, 'default_config') else None,
                }
                if rule_error:
                    provenance['errors'] = [f'規則驗證失敗：{rule_error}']
                
                return ('ziwei', True, {
                    'birth_date': birth_date,
                    'birth_time': birth_time,
                    'birth_location': birth_location,
                    'gender': gender,
                    'chart_structure': structure,
                    'analysis': ziwei_analysis,
                    'original_analysis': raw_ziwei_analysis,
                    'provenance': provenance,
                    'source_signature': source_signature,
                }, False)
            except Exception as e:
                return ('ziwei', False, str(e), False)

        def run_astrology_calc():
            try:
                if 'astrology' not in available_systems or not (birth_date and birth_time and birth_location and birth_year): return ('astrology', False, None, False)
                existing = db.get_system_report(user_id, 'astrology')
                if existing and not force_regenerate:
                    logger.info('占星報告已存在，跳過生成', user_id=user_id)
                    return ('astrology', True, None, True)
                
                logger.info('生成占星報告(Thread)...', user_id=user_id)
                
                taiwan_cities = {
                    '台北': (25.0330, 121.5654), '台北市': (25.0330, 121.5654),
                    '新北': (25.0169, 121.4628), '新北市': (25.0169, 121.4628),
                    '桃園': (24.9936, 121.3010), '桃園市': (24.9936, 121.3010),
                    '台中': (24.1477, 120.6736), '台中市': (24.1477, 120.6736),
                    '台南': (22.9998, 120.2270), '台南市': (22.9998, 120.2270),
                    '高雄': (22.6273, 120.3014), '高雄市': (22.6273, 120.3014),
                    '基隆': (25.1276, 121.7392), '基隆市': (25.1276, 121.7392),
                    '新竹': (24.8138, 120.9675), '新竹市': (24.8138, 120.9675),
                    '嘉義': (23.4801, 120.4491), '嘉義市': (23.4801, 120.4491),
                    '彰化': (24.0518, 120.5161), '彰化市': (24.0518, 120.5161), '彰化縣': (24.0518, 120.5161),
                    '南投': (23.9609, 120.9719), '南投市': (23.9609, 120.9719), '南投縣': (23.9609, 120.9719),
                    '雲林': (23.7092, 120.4313), '雲林縣': (23.7092, 120.4313),
                    '苗栗': (24.5602, 120.8214), '苗栗市': (24.5602, 120.8214), '苗栗縣': (24.5602, 120.8214),
                    '屏東': (22.6727, 120.4871), '屏東市': (22.6727, 120.4871), '屏東縣': (22.6727, 120.4871),
                    '宜蘭': (24.7570, 121.7533), '宜蘭市': (24.7570, 121.7533), '宜蘭縣': (24.7570, 121.7533),
                    '花蓮': (23.9910, 121.6114), '花蓮市': (23.9910, 121.6114), '花蓮縣': (23.9910, 121.6114),
                    '台東': (22.7583, 121.1444), '台東市': (22.7583, 121.1444), '台東縣': (22.7583, 121.1444),
                    '澎湖': (23.5711, 119.5793), '澎湖縣': (23.5711, 119.5793),
                    '金門': (24.4493, 118.3767), '金門縣': (24.4493, 118.3767),
                    '連江': (26.1505, 119.9499), '連江縣': (26.1505, 119.9499), '馬祖': (26.1505, 119.9499),
                }
                
                lat, lng = None, None
                city_name = birth_location.replace('台灣', '').replace('臺灣', '').strip()
                
                for city_key, (city_lat, city_lng) in taiwan_cities.items():
                    if city_key in city_name:
                        lat, lng = city_lat, city_lng
                        break
                
                if lat is None:
                    lat, lng = 25.0330, 121.5654
                    logger.info(f'無法識別地點 "{birth_location}"，使用台北座標', user_id=user_id)
                
                natal_chart = astrology_calc.calculate_natal_chart(
                    name=chinese_name or '用戶', year=birth_year, month=birth_month, day=birth_day,
                    hour=birth_hour, minute=birth_minute, city="Taiwan", longitude=lng, latitude=lat, timezone_str="Asia/Taipei"
                )
                chart_text = astrology_calc.format_for_gemini(natal_chart)
                astrology_prompt = get_natal_chart_analysis_prompt(chart_text)
                system_instruction = "你是專精西洋占星術的命理分析師，遵循「有所本」原則，所有解釋必須引用占星學經典理論。輸出必須使用繁體中文（台灣用語）。"
                full_prompt = f"{system_instruction}\n\n{astrology_prompt}"
                astrology_analysis = sanitize_plain_text(call_gemini(full_prompt, ""))
                
                return ('astrology', True, {
                    'birth_date': birth_date,
                    'birth_time': birth_time,
                    'birth_location': birth_location,
                    'coordinates': {'latitude': lat, 'longitude': lng},
                    'natal_chart': natal_chart,
                    'analysis': astrology_analysis
                }, False)
            except Exception as e:
                return ('astrology', False, str(e), False)

        timed_out = False
        overall_timeout_seconds = int(os.getenv('SAVE_AND_ANALYZE_TIMEOUT_SECONDS', '180'))

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_sys = {}
            if 'name' in available_systems:
                future_to_sys[executor.submit(run_name_calc)] = 'name'
            if 'numerology' in available_systems:
                future_to_sys[executor.submit(run_numerology_calc)] = 'numerology'
            if 'bazi' in available_systems:
                future_to_sys[executor.submit(run_bazi_calc)] = 'bazi'
            if 'ziwei' in available_systems:
                future_to_sys[executor.submit(run_ziwei_calc)] = 'ziwei'
            if 'astrology' in available_systems:
                future_to_sys[executor.submit(run_astrology_calc)] = 'astrology'

            futures = list(future_to_sys.keys())

            try:
                for future in as_completed(futures, timeout=overall_timeout_seconds):
                    try:
                        res = future.result()
                        if not res:
                            continue
                        sys_name, success, data, is_skip = res

                        if success:
                            reports_generated[sys_name] = True
                            if is_skip:
                                continue

                            db.save_system_report(user_id, sys_name, data)

                            if sys_name == 'ziwei':
                                chart_lock = {
                                    'user_id': user_id,
                                    'chart_type': 'ziwei',
                                    'chart_structure': data.get('chart_structure'),
                                    # Keep raw analysis for auditability; the report stores cleaned analysis.
                                    'original_analysis': data.get('original_analysis') or data.get('analysis'),
                                    'provenance': data.get('provenance'),
                                    'source_signature': data.get('source_signature'),
                                    'confirmation_status': 'confirmed',
                                    'confirmed_at': datetime.now().isoformat(),
                                    'is_active': True
                                }
                                save_chart_lock(user_id, chart_lock)
                        else:
                            logger.error(f'{sys_name} 報告生成失敗: {data}', user_id=user_id)
                            generation_errors[sys_name] = str(data)
                            reports_generated[sys_name] = False
                    except Exception as e:
                        sys_name = future_to_sys.get(future, 'unknown')
                        logger.error(f'{sys_name} 執行緒錯誤: {e}', user_id=user_id)
                        generation_errors[sys_name] = str(e)
                        reports_generated[sys_name] = False
            except FuturesTimeoutError:
                timed_out = True
                pending = [f for f in futures if not f.done()]
                for f in pending:
                    sys_name = future_to_sys.get(f, 'unknown')
                    generation_errors[sys_name] = f'系統生成逾時（>{overall_timeout_seconds}s）'
                    reports_generated[sys_name] = False
                    try:
                        f.cancel()
                    except Exception:
                        pass
        
        duration_ms = (time.time() - start_time) * 1000
        logger.log_api_response('/api/profile/save-and-analyze', 200, duration_ms)
        
        # 回傳各系統的結構化數據給前端顯示
        response_data = {
            'status': 'partial' if (timed_out or generation_errors) else 'success',
            'profile_saved': True,
            'reports_generated': reports_generated,
            'generation_errors': generation_errors if generation_errors else None,
            'available_systems': available_systems,
            'total_time_seconds': round(duration_ms / 1000, 1)
        }
        
        # 附加各系統的關鍵數據（供步驟5顯示）
        # 注意：db.get_system_report 返回 {'report': data, 'created_at': ..., 'updated_at': ...}
        
        # 紫微斗數
        if reports_generated.get('ziwei'):
            ziwei_report_wrapper = db.get_system_report(user_id, 'ziwei')
            if ziwei_report_wrapper:
                ziwei_report = ziwei_report_wrapper.get('report', {})
                if ziwei_report.get('chart_structure'):
                    response_data['ziwei_structure'] = ziwei_report['chart_structure']
        
        # 八字命理
        if reports_generated.get('bazi'):
            bazi_report_wrapper = db.get_system_report(user_id, 'bazi')
            if bazi_report_wrapper:
                bazi_report = bazi_report_wrapper.get('report', {})
                if bazi_report.get('bazi_chart'):
                    response_data['bazi_chart'] = bazi_report['bazi_chart']
        
        # 靈數學
        if reports_generated.get('numerology'):
            numerology_report_wrapper = db.get_system_report(user_id, 'numerology')
            if numerology_report_wrapper:
                numerology_report = numerology_report_wrapper.get('report', {})
                if numerology_report.get('profile'):
                    response_data['numerology_profile'] = numerology_report['profile']
        
        # 姓名學
        if reports_generated.get('name'):
            name_report_wrapper = db.get_system_report(user_id, 'name')
            if name_report_wrapper:
                name_report = name_report_wrapper.get('report', {})
                five_grids_obj = name_report.get('five_grids')
                total_strokes = None
                try:
                    if isinstance(five_grids_obj, dict):
                        total_strokes = (five_grids_obj.get('name_info') or {}).get('total_strokes')
                except Exception:
                    total_strokes = None

                response_data['name_result'] = {
                    'name': name_report.get('chinese_name'),
                    'five_grids': name_report.get('five_grids'),
                    'total_strokes': total_strokes
                }
        
        # 西洋占星
        if reports_generated.get('astrology'):
            astrology_report_wrapper = db.get_system_report(user_id, 'astrology')
            if astrology_report_wrapper:
                astrology_report = astrology_report_wrapper.get('report', {})
                if astrology_report.get('natal_chart'):
                    nc = astrology_report['natal_chart']
                    planets = nc.get('planets', {}) if isinstance(nc, dict) else {}
                    sun = planets.get('sun', {}) if isinstance(planets, dict) else {}
                    moon = planets.get('moon', {}) if isinstance(planets, dict) else {}
                    asc = planets.get('ascendant', {}) if isinstance(planets, dict) else {}
                    response_data['astrology_chart'] = {
                        # Prefer zh labels if available, else fall back to sign abbreviations.
                        'sun_sign': sun.get('sign_zh') or sun.get('sign'),
                        'moon_sign': moon.get('sign_zh') or moon.get('sign'),
                        'ascendant': asc.get('sign_zh') or asc.get('sign')
                    }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f'批次生成報告失敗: {str(e)}', user_id=user_id)
        return jsonify({
            'status': 'partial',
            'profile_saved': True,
            'reports_generated': reports_generated,
            'generation_errors': generation_errors,
            'error': str(e)
        }), 500


@app.route('/api/profile/clear-reports', methods=['POST'])
def clear_reports_only():
    """清空六大系統內容（不重新生成、不呼叫 LLM）。

    預設會刪除：system_reports、fortune_profile 快取。
    若傳入 clear_chart_lock=true，才會額外刪除命盤鎖定（chart_lock）。
    """
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id')
    if not user_id:
        raise MissingParameterException('user_id')

    logger.log_api_request('/api/profile/clear-reports', 'POST', user_id=user_id)

    clear_chart_lock = bool(data.get('clear_chart_lock', False))

    deleted_reports = False
    deleted_chart_lock = False
    deleted_fortune_profile = False
    deleted_json_lock = False

    try:
        deleted_reports = bool(db.delete_system_reports(user_id))
    except Exception as e:
        logger.warning(f'清除舊報告失敗: {str(e)}', user_id=user_id)

    if clear_chart_lock:
        try:
            deleted_chart_lock = bool(db.delete_chart_lock(user_id))
        except Exception as e:
            logger.warning(f'清除鎖盤失敗: {str(e)}', user_id=user_id)

    try:
        deleted_fortune_profile = bool(db.delete_fortune_profile(user_id))
    except Exception as e:
        logger.warning(f'清除 fortune profile 失敗: {str(e)}', user_id=user_id)

    # 兼容舊 JSON 鎖盤（只有在指定清除鎖盤時才處理）
    if clear_chart_lock:
        try:
            if LOCKS_FILE.exists():
                locks = load_json(LOCKS_FILE)
                if user_id in locks:
                    del locks[user_id]
                    LOCKS_FILE.write_text(json.dumps(locks, ensure_ascii=False, indent=2), encoding='utf-8')
                    deleted_json_lock = True
        except Exception as e:
            logger.warning(f'清除 JSON 鎖盤失敗: {str(e)}', user_id=user_id)

    return jsonify({
        'status': 'success',
        'user_id': user_id,
        'deleted_reports': deleted_reports,
        'deleted_chart_lock': deleted_chart_lock,
        'deleted_fortune_profile': deleted_fortune_profile,
        'deleted_json_lock': deleted_json_lock,
        'clear_chart_lock': clear_chart_lock,
    })


@app.route('/api/reports/get', methods=['GET'])
def get_system_reports():
    """
    取得用戶的系統報告
    
    Query: ?user_id=user_123&system=ziwei  (system 選填，不填則返回全部)
    """
    user_id = request.args.get('user_id')
    system_type = request.args.get('system')
    
    if not user_id:
        raise MissingParameterException('user_id')
    
    if system_type:
        report = db.get_system_report(user_id, system_type)
        if not report:
            return jsonify({'found': False, 'message': f'找不到 {system_type} 報告'})
        return jsonify({'found': True, 'system': system_type, **report})
    else:
        reports = db.get_all_system_reports(user_id)
        return jsonify({
            'found': len(reports) > 0,
            'reports': reports,
            'available_systems': list(reports.keys())
        })


@app.route('/api/chat/sessions', methods=['GET'])
def get_chat_sessions():
    """取得用戶的對話列表"""
    user_id = require_auth_user_id()
    sessions = db.get_user_chat_sessions(user_id, limit=50)
    return jsonify({
        'status': 'success',
        'sessions': sessions
    })


@app.route('/api/chat/messages', methods=['GET'])
def get_chat_messages_api():
    """取得特定對話的訊息歷史
    
    Query: ?session_id=xxx&limit=50
    """
    user_id = require_auth_user_id()
    session_id = request.args.get('session_id', '').strip()
    limit = min(int(request.args.get('limit', 50)), 100)
    
    if not session_id:
        raise MissingParameterException('session_id')
    
    # 驗證 session 擁有者
    sess = db.get_chat_session(session_id)
    if not sess or sess.get('user_id') != user_id:
        return jsonify({'status': 'error', 'message': '無效的 session_id'}), 400
    
    messages = db.get_chat_messages(session_id, limit=limit)
    # 格式化訊息，確保前端可用
    formatted = []
    for m in messages:
        payload = m.get('payload') or {}
        formatted.append({
            'role': m.get('role'),
            'content': m.get('content'),
            'citations': payload.get('citations', []),
            'used_systems': payload.get('used_systems', []),
            'confidence': payload.get('confidence', 0.0),
            'next_steps': payload.get('next_steps', []),
            'created_at': m.get('created_at')
        })
    
    return jsonify({
        'status': 'success',
        'session_id': session_id,
        'messages': formatted
    })


@app.route('/api/chat/sessions/<session_id>', methods=['DELETE'])
def delete_chat_session_api(session_id: str):
    """刪除對話"""
    user_id = require_auth_user_id()
    
    if not session_id:
        raise MissingParameterException('session_id')
    
    success = db.delete_chat_session(session_id, user_id)
    if not success:
        return jsonify({'status': 'error', 'message': '刪除失敗或無權限'}), 400
    
    return jsonify({'status': 'success', 'message': '對話已刪除'})


@app.route('/api/chat/consult', methods=['POST'])
def chat_consult():
    """AI 命理顧問對話（有所本）。

    Request:
      {"message": "...", "session_id": "..." (optional), "voice_mode": true/false (optional)}

    Response:
      {"status":"success","session_id":"...","reply":"...","citations":[],"used_systems":[],"confidence":0.0,"next_steps":[]}
    """
    user_id = require_auth_user_id()
    data = request.json or {}
    message = (data.get('message') or data.get('question') or '').strip()
    session_id = (data.get('session_id') or '').strip() or None
    voice_mode = data.get('voice_mode', False)  # 新增：語音模式標記

    if not message:
        raise MissingParameterException('message')

    # Session handling
    if session_id:
        sess = db.get_chat_session(session_id)
        if not sess or sess.get('user_id') != user_id:
            return jsonify({'status': 'error', 'message': '無效的 session_id'}), 400
    else:
        session_id = uuid.uuid4().hex
        title = _truncate_text(message, 32)
        db.create_chat_session(user_id, session_id, title=title)

    # Load reports & fortune_profile cache
    reports = db.get_all_system_reports(user_id)
    signature = compute_reports_signature(reports)
    cached = db.get_fortune_profile(user_id)
    if cached and cached.get('source_signature') == signature and isinstance(cached.get('profile'), dict):
        fortune_profile = cached.get('profile')
    else:
        fortune_profile = build_fortune_facts_from_reports(reports)
        db.upsert_fortune_profile(user_id, signature, fortune_profile)

    facts = fortune_profile.get('facts') if isinstance(fortune_profile, dict) else []
    if not isinstance(facts, list):
        facts = []
    # 控制 token：最多 30 條（減少以加速回覆）
    facts = facts[:30]
    fact_map = {f.get('id'): f for f in facts if isinstance(f, dict) and f.get('id')}
    
    # 語音模式下：加載命盤結構作為額外上下文
    chart_context = ""
    if voice_mode:
        chart_data = db.get_chart_lock(user_id)
        if chart_data:
            chart_struct = chart_data.get('chart_structure', {})
            user_data = db.get_user(user_id)
            user_name = user_data.get('name', '客戶') if user_data else '客戶'
            birth_info = ""
            if user_data:
                birth_info = f"{user_data.get('birth_year')}年{user_data.get('birth_month')}月{user_data.get('birth_day')}日 {user_data.get('birth_hour')}時"
            
            # 提取命盤核心信息
            ming_gong = chart_struct.get('命宮', {})
            chart_context = (
                f"\n\n【客戶命盤信息】\n"
                f"姓名：{user_name}\n"
                f"生辰：{birth_info}\n"
                f"命宮：{ming_gong.get('main_stars', [])} {ming_gong.get('secondary_stars', [])}\n"
                f"命主：{chart_struct.get('命主', '未知')}\n"
                f"身主：{chart_struct.get('身主', '未知')}\n"
                f"(這些是命盤的基礎信息，你可以用來讓回答更個人化、更精準)\n"
            )

    # History（只取最近 6 條以加速）
    history_msgs = db.get_chat_messages(session_id, limit=6)
    history_text_lines = []
    for m in history_msgs:
        role = m.get('role')
        content = m.get('content')
        if not content:
            continue
        if role == 'user':
            history_text_lines.append(f"使用者：{content}")
        elif role == 'assistant':
            history_text_lines.append(f"命理老師：{content}")
    history_text = "\n".join(history_text_lines[-10:])

    # 語音模式 vs 文字模式：不同的 prompt 風格
    if voice_mode:
        consult_system = (
            "你是一位資深命理老師，正在跟客戶進行語音對話諮詢。\n\n"
            "【語音對話風格】\n"
            "- 像老朋友聊天一樣親切自然，帶有一點江湖味道\n"
            "- 可以用「嗯」「喔」「欸」等語氣詞，更有感覺\n"
            "- 偶爾停頓思考，用「讓我看看你的命盤...」營造氛圍\n"
            "- 回覆 160-300 字，像說話一樣一句一句的，可以多講幾句\n"
            "- 可以用命理術語（像「命主」「紫微」），但要自然帶出\n"
            "- 純文字回覆，不要使用任何 Markdown 格式（不要用 **、*、# 等符號）\n\n"
            "【有所本原則】\n"
            "- 只根據 facts 和命盤信息判斷，不可腦補\n"
            "- 引用依據會自動附在回覆下方，不需要在文字中特別說明來源\n"
            "- 可以直接稱呼客戶的名字，更親切\n\n"
            "【語言】繁體中文（台灣用語）\n"
            "【輸出】只輸出 JSON，不要其他文字"
        )
    else:
        consult_system = (
            "你是一位資深命理老師，正在跟客戶面對面諮詢。\n\n"
            "【對話風格】\n"
            "- 像朋友聊天一樣自然，不要寫文章\n"
            "- 給出結論並適度展開說明\n"
            "- 回覆控制在 200-400 字以內\n"
            "- 用口語化表達，可以用「嗯」「喔」「欸」等語助詞\n"
            "- 純文字回覆，不要使用任何 Markdown 格式（不要用 **、*、# 等符號）\n\n"
            "【有所本原則】\n"
            "- 只根據 facts 判斷，不可腦補\n"
            "- 引用依據會自動附在回覆下方，不需要在文字中特別說明來源\n\n"
            "【語言】繁體中文（台灣用語）\n"
            "【輸出】只輸出 JSON，不要其他文字"
        )

    prompt = (
        f"facts（可引用的命盤資料）：\n{json.dumps(facts, ensure_ascii=False)}{chart_context}\n\n"
        f"對話歷史：\n{history_text or '（無）'}\n\n"
        f"客戶問：{message}\n\n"
        "用 JSON 回覆，格式：\n"
        "{\n"
        "  \"reply\": \"簡短口語化的回覆，100-200字\",\n"
        "  \"used_fact_ids\": [\"用到的fact id\"],\n"
        "  \"confidence\": 0.0到1.0,\n"
        "  \"next_steps\": [\"...\"]\n"
        "}\n"
    )

    # Persist user message first
    db.add_chat_message(session_id, 'user', message, payload=None)

    # 呼叫 Gemini API 並處理可能的錯誤
    raw = None
    try:
        raw = call_gemini(prompt, consult_system, response_mime_type='application/json')

        logger.info(f"Gemini 回覆長度: {len(raw) if raw else 0}")
    except Exception as e:
        logger.error(f"Gemini API 呼叫失敗: {e}")
        # 返回友善的錯誤訊息而不是拋出異常
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'reply': f'抱歉，AI 暫時無法回應，請稍後再試。（錯誤：{str(e)[:50]}）',
            'citations': [],
            'used_systems': [],
            'confidence': 0.1,
            'next_steps': ['請稍後重試'],
            'available_systems': []
        })
    
    raw = sanitize_plain_text(raw)
    parsed = parse_json_object(raw)
    
    # 記錄解析結果
    if parsed is None:
        logger.warning(f"JSON 解析失敗，原始回覆: {raw[:200] if raw else 'None'}")

    reply = None
    used_fact_ids: List[str] = []
    confidence = 0.35
    next_steps = []

    if isinstance(parsed, dict):
        reply = (parsed.get('reply') or '').strip() or None
        used_fact_ids = parsed.get('used_fact_ids') or []
        if not isinstance(used_fact_ids, list):
            used_fact_ids = []
        used_fact_ids = [str(x) for x in used_fact_ids if str(x)]
        try:
            confidence = float(parsed.get('confidence'))
        except Exception:
            confidence = 0.35
        confidence = max(0.0, min(1.0, confidence))
        next_steps = parsed.get('next_steps') or []
        if not isinstance(next_steps, list):
            next_steps = []

    if not reply:
        # fallback: use raw text
        reply = (raw or '').strip() or '目前無法生成回覆，請稍後再試。'
        used_fact_ids = []
        confidence = 0.2

    citations = []
    used_systems = []
    for fid in used_fact_ids:
        f = fact_map.get(fid)
        if not f:
            continue
        citations.append({
            'fact_id': fid,
            'system': f.get('system'),
            'title': f.get('title'),
            'excerpt': f.get('content'),
            'path': f.get('path'),
            'path_readable': humanize_citation_path(f.get('path') or '')
        })
        if f.get('system'):
            used_systems.append(f.get('system'))
    used_systems = list(dict.fromkeys(used_systems))

    if not citations:
        # 強制「有所本」：無引用則降低信心並提示
        confidence = min(confidence, 0.35)
        if '資料不足' not in reply and len(facts) == 0:
            reply = (
                "目前我這邊沒有可引用的命盤 facts（可能尚未生成六大系統報告）。\n"
                "建議先到『個人檔案』完成資料並生成報告後，再回來做對話諮詢。\n\n"
                + reply
            )

    if not next_steps:
        next_steps = suggest_next_steps(message)

    payload = {
        'citations': citations,
        'used_systems': used_systems,
        'confidence': confidence,
        'next_steps': next_steps,
        'raw_model_output': raw if isinstance(parsed, dict) else None
    }
    db.add_chat_message(session_id, 'assistant', reply, payload=payload)
    db.touch_chat_session(session_id)

    return jsonify({
        'status': 'success',
        'session_id': session_id,
        'reply': reply,
        'citations': citations,
        'used_systems': used_systems,
        'confidence': confidence,
        'next_steps': next_steps,
        'available_systems': fortune_profile.get('available_systems') if isinstance(fortune_profile, dict) else []
    })


@app.route('/api/chart/confirm-lock', methods=['POST'])
def confirm_lock():
    """
    確認並鎖定命盤
    
    Request:
    {
        "user_id": "user_123"
    }
    
    Response:
    {
        "status": "locked",
        "message": "命盤已鎖定",
        "locked_at": "2026-01-24T02:00:00"
    }
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            raise MissingParameterException('user_id')
        
        # 取得暫存的命盤
        lock = get_chart_lock(user_id)
        
        if not lock:
            raise ChartNotFoundException(user_id, '找不到待確認的命盤')
        
        # 更新確認狀態
        lock['confirmation_status'] = 'confirmed'
        lock['confirmed_at'] = datetime.now().isoformat()
        lock['is_active'] = True
        
        save_chart_lock(user_id, lock)
        
        logger.info(f'用戶 {user_id} 已確認並鎖定命盤', user_id=user_id)
        
        return jsonify({
            'status': 'locked',
            'message': '命盤已鎖定',
            'locked_at': lock['confirmed_at']
        })
        
    except AetheriaException:
        raise
    except Exception as e:
        logger.error(f'確認鎖盤失敗: {str(e)}', user_id=user_id if 'user_id' in dir() else None)
        return jsonify({'error': str(e)}), 500

@app.route('/api/chart/get-lock', methods=['GET'])
def get_lock():
    """
    查詢用戶的鎖定命盤
    
    Query: ?user_id=user_123
    
    Response:
    {
        "locked": true,
        "chart_structure": {...},
        "locked_at": "2026-01-24T02:00:00"
    }
    """
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            raise MissingParameterException('user_id')
        
        lock = get_chart_lock(user_id)
        
        if not lock:
            return jsonify({'locked': False, 'message': '尚未定盤'})
        
        if not lock.get('is_active'):
            return jsonify({'locked': False, 'message': '命盤尚未確認'})
        
        return jsonify({
            'locked': True,
            'chart_structure': lock['chart_structure'],
            'locked_at': lock.get('confirmed_at'),
            'original_analysis': lock.get('original_analysis', '')[:500] + '...'
        })
        
    except AetheriaException:
        raise
    except Exception as e:
        logger.error(f'查詢鎖盤失敗: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/message', methods=['POST'])
def chat_message():
    """
    後續對話（自動注入鎖定結構）
    
    Request:
    {
        "user_id": "user_123",
        "message": "我最近工作不順利，怎麼辦？"
    }
    
    Response:
    {
        "response": "根據你的命盤...",
        "chart_injected": true
    }
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        message = data.get('message')
        tone = data.get('tone')
        
        if not user_id:
            raise MissingParameterException('user_id')
        if not message:
            raise MissingParameterException('message')
        
        # 取得鎖定的命盤
        lock = get_chart_lock(user_id)
        
        if not lock or not lock.get('is_active'):
            raise ChartNotLockedException(user_id)
        
        if not tone:
            prefs = db.get_member_preferences(user_id) or {}
            tone = prefs.get('tone') or '溫暖專業'

        # 格式化命盤結構
        structure = lock.get('chart_structure', {})
        life_palace = structure.get('命宮', {})
        main_stars = life_palace.get('主星') or []
        main_stars_text = ', '.join(main_stars) if main_stars else '未提及'
        life_palace_pos = life_palace.get('宮位', '未提及')
        pattern_text = ', '.join(structure.get('格局', []) or []) or '未提及'
        five_elements = structure.get('五行局', '未提及')

        structure_text = f"""
命宮：{main_stars_text} ({life_palace_pos}宮)
格局：{pattern_text}
五行局：{five_elements}

十二宮配置：
"""

        for palace, info in structure.get('十二宮', {}).items():
            stars = ', '.join(info.get('主星') or []) if info else '空宮'
            trans = f" - {info.get('四化')}" if info and info.get('四化') else ''
            palace_pos = info.get('宮位') if info else None
            palace_pos_text = palace_pos if palace_pos else '未提及'
            structure_text += f"- {palace} ({palace_pos_text}宮): {stars}{trans}\n"

        # 組合 Prompt（注入結構 + 真人感模板）
        prompt = "\n\n".join([
            CHAT_WITH_LOCKED_CHART_PROMPT.format(
                chart_structure=structure_text,
                user_question=message
            ),
            CHAT_TEACHER_STYLE_PROMPT.format(tone=tone)
        ])
        
        # 呼叫 Gemini
        logger.info(f'正在為用戶 {user_id} 回應問題...', user_id=user_id)
        response = call_gemini(prompt)
        next_steps = suggest_next_steps(message)

        db.save_analysis_history(
            user_id,
            'chat_message',
            {'message': message, 'tone': tone},
            {'reply': response}
        )

        conversation_summary = None
        try:
            history = db.get_analysis_history(user_id, limit=12)
            chat_history = [item for item in history if item.get('analysis_type') == 'chat_message']
            chat_history = list(reversed(chat_history))[-6:]
            if chat_history:
                conversation = build_conversation_log(chat_history)
                summary_prompt = CONVERSATION_SUMMARY_PROMPT.format(conversation=conversation)
                conversation_summary = call_gemini(summary_prompt, system_instruction=SUMMARY_SYSTEM_INSTRUCTION)
        except Exception as e:
            logger.warning(f'對話摘要生成失敗: {str(e)}', user_id=user_id)
        
        logger.info(f'回應完成', user_id=user_id)
        
        return jsonify({
            'reply': response,
            'chart_injected': True,
            'tone': tone,
            'next_steps': next_steps,
            'conversation_summary': conversation_summary
        })
        
    except AetheriaException:
        raise
    except Exception as e:
        logger.error(f'對話失敗: {str(e)}', user_id=user_id if 'user_id' in dir() else None)
        return jsonify({'error': str(e)}), 500


# =====================================================================
# OpenAI Realtime Voice API
# =====================================================================

@app.route('/api/voice/session', methods=['POST'])
def create_voice_session():
    """建立 OpenAI Realtime WebRTC 語音會話。
    
    Request:
      {
        "sdp": "...",           # WebRTC SDP offer
        "voice": "alloy",       # 可選: alloy, ash, ballad, coral, echo, sage, shimmer, verse
        "instructions": "..."   # 可選: 系統指令
      }
    
    Response:
      {"sdp": "..."}  # WebRTC SDP answer
    """
    import requests as http_requests
    
    user_id = require_auth_user_id()
    data = request.json or {}
    # 注意：不要 strip() SDP，因為 SDP 末尾的 \r\n 是必要的
    sdp = data.get('sdp') or ''
    voice = data.get('voice', 'alloy')
    instructions = data.get('instructions', '')
    
    # 除錯：顯示原始 SDP
    logger.info(f'原始 SDP 長度: {len(sdp)}, 末尾 20 字元: {repr(sdp[-20:]) if len(sdp) > 20 else repr(sdp)}')
    
    if not sdp:
        raise MissingParameterException('sdp')
    
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        logger.error('OPENAI_API_KEY 未設定')
        return jsonify({'error': 'OpenAI API 未設定'}), 500
    
    # 可用的語音選項（Realtime API 支援的所有語音）
    available_voices = ['alloy', 'ash', 'ballad', 'coral', 'echo', 'sage', 'shimmer', 'verse', 'marin', 'cedar']
    if voice not in available_voices:
        voice = 'marin'  # 預設使用 marin（官方推薦的女聲）
    
    # 取得用戶命盤資料用於系統指令
    user_context = ""
    try:
        reports = db.get_all_system_reports(user_id)
        if reports:
            for sys_type in ['ziwei', 'bazi', 'numerology']:
                if sys_type in reports and reports[sys_type].get('analysis'):
                    user_context += f"\n【{sys_type}】\n{reports[sys_type]['analysis'][:500]}...\n"
    except Exception as e:
        logger.warning(f'取得用戶命盤失敗: {e}')
    
    # 系統指令（命理顧問人設）
    system_instructions = instructions or f"""你是 Aetheria 命理顧問，一位專業、溫暖、有洞察力的命理分析師。

你的溝通風格：
- 使用台灣繁體中文，自然親切的口語表達
- 像朋友聊天一樣，但保持專業深度
- 適當使用命理術語但會解釋其意義
- 回答簡潔有力，通常 2-3 句話即可

你的專長：
- 紫微斗數、八字命理、西洋占星、命理數字、姓名學
- 能整合多系統給予全面分析

{f'用戶命盤摘要：{user_context}' if user_context else ''}

注意：保持語音對話的自然節奏，回答不要太長。"""

    # 設定 session config (Unified Interface format)
    # 注意：/v1/realtime/calls 端點只支援有限的參數
    session_config = {
        'type': 'realtime',
        'model': os.getenv('REALTIME_MODEL', 'gpt-4o-realtime-preview'),
        'audio': {
            'output': {
                'voice': voice
            }
        },
        'instructions': system_instructions
    }
    
    # 呼叫 OpenAI Realtime API (Unified Interface)
    base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com').rstrip('/')
    
    try:
        from requests_toolbelt import MultipartEncoder
        
        # 確保 SDP 使用正確的換行符號 (CRLF for SDP)
        # SDP 協議要求使用 CRLF (\r\n) 作為行結束符
        sdp_normalized = sdp.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\r\n')
        
        # 除錯日誌
        logger.info(f'SDP 長度: {len(sdp_normalized)}, 前 100 字元: {repr(sdp_normalized[:100])}')
        
        # 使用 multipart form data
        m = MultipartEncoder(
            fields={
                'sdp': sdp_normalized,
                'session': json.dumps(session_config)
            }
        )
        
        response = http_requests.post(
            f"{base_url}/v1/realtime/calls",
            headers={
                'Authorization': f'Bearer {openai_api_key}',
                'Content-Type': m.content_type
            },
            data=m,
            timeout=25
        )
        
        if not response.ok:
            error_text = response.text
            logger.error(f'OpenAI Realtime API 失敗: {response.status_code} - {error_text}')
            return jsonify({
                'error': 'OpenAI Realtime API 失敗',
                'status': response.status_code,
                'details': error_text[:500]
            }), 502
        
        answer_sdp = response.text
        logger.info(f'語音會話建立成功', user_id=user_id)
        
        return jsonify({'sdp': answer_sdp})
        
    except ImportError:
        logger.error('請安裝 requests-toolbelt: pip install requests-toolbelt')
        return jsonify({'error': '缺少 requests-toolbelt 套件'}), 500
    except http_requests.Timeout:
        logger.error('OpenAI Realtime API 超時')
        return jsonify({'error': 'API 請求超時'}), 504
    except Exception as e:
        logger.error(f'語音會話建立失敗: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/voice/voices', methods=['GET'])
def get_available_voices():
    """取得可用的語音選項。"""
    voices = [
        # 推薦語音（官方推薦）
        {'id': 'marin', 'name': 'Marin', 'description': '溫暖自然（女聲）', 'gender': 'female', 'recommended': True},
        {'id': 'cedar', 'name': 'Cedar', 'description': '沉穩可靠（男聲）', 'gender': 'male', 'recommended': True},
        # 其他女聲
        {'id': 'shimmer', 'name': 'Shimmer', 'description': '活潑輕快（女聲）', 'gender': 'female'},
        {'id': 'coral', 'name': 'Coral', 'description': '清晰明亮（女聲）', 'gender': 'female'},
        {'id': 'sage', 'name': 'Sage', 'description': '智慧沉穩（女聲）', 'gender': 'female'},
        {'id': 'ballad', 'name': 'Ballad', 'description': '富有情感（女聲）', 'gender': 'female'},
        # 中性語音
        {'id': 'alloy', 'name': 'Alloy', 'description': '中性平衡', 'gender': 'neutral'},
        {'id': 'verse', 'name': 'Verse', 'description': '文藝氣質', 'gender': 'neutral'},
        # 男聲
        {'id': 'ash', 'name': 'Ash', 'description': '溫暖柔和（男聲）', 'gender': 'male'},
        {'id': 'echo', 'name': 'Echo', 'description': '穩重低沉（男聲）', 'gender': 'male'},
    ]
    return jsonify({'voices': voices})


@app.route('/api/chart/relock', methods=['POST'])
def relock_chart():
    """
    重新定盤
    
    Request:
    {
        "user_id": "user_123",
        "reason": "時辰有誤，需重新排盤"
    }
    
    Response:
    {
        "status": "relocked",
        "message": "已重新定盤，請確認新的命盤結構"
    }
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        reason = data.get('reason', '用戶要求重新定盤')
        
        if not user_id:
            raise MissingParameterException('user_id')
        
        # 取得用戶資料
        user = get_user(user_id)
        
        if not user:
            raise UserNotFoundException(user_id)
        
        # 停用舊的鎖定
        old_lock = get_chart_lock(user_id)
        if old_lock:
            old_lock['is_active'] = False
            old_lock['deactivated_at'] = datetime.now().isoformat()
            old_lock['deactivate_reason'] = reason
            save_chart_lock(user_id + '_old', old_lock)
        
        logger.info(f'用戶 {user_id} 重新定盤，原因：{reason}', user_id=user_id)
        
        # 返回前端，讓它重新呼叫 initial-analysis
        return jsonify({
            'status': 'ready_for_reanalysis',
            'message': '已清除舊命盤，請重新進行命盤分析'
        })
        
    except AetheriaException:
        raise
    except Exception as e:
        logger.error(f'重新定盤失敗: {str(e)}')
        return jsonify({'error': str(e)}), 500

# ============================================
# 流年運勢 API
# ============================================

@app.route('/api/fortune/annual', methods=['POST'])
def fortune_annual():
    """
    年度流年運勢分析
    
    Request:
    {
        "user_id": "user_123",
        "target_year": 2026  (可選，默認當前年份)
    }
    
    Response:
    {
        "fortune_data": {...},
        "analysis": "完整流年分析文字"
    }
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        target_year = data.get('target_year', datetime.now().year)
        
        if not user_id:
            raise MissingParameterException('user_id')
        
        # 取得鎖定的命盤
        lock = get_chart_lock(user_id)
        if not lock or not lock.get('is_active'):
            raise ChartNotLockedException(user_id)
        
        # 取得用戶資料
        user = get_user(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        
        # 取得用戶出生日期
        birth_info = get_user_birth_info(user)
        if not birth_info:
            raise InvalidParameterException('birth_date', '用戶缺少可解析的出生日期')
        
        # 創建流年計算器
        ming_gong_branch = lock['chart_structure']['命宮']['宮位']
        teller = FortuneTeller(
            birth_year=birth_info['year'],
            birth_month=birth_info['month'],
            birth_day=birth_info['day'],
            gender=normalize_gender(user.get('gender')),
            ming_gong_branch=ming_gong_branch
        )
        
        # 計算流年運勢
        fortune_data = teller.get_fortune_summary(target_year)
        fortune_text = teller.format_fortune_text(fortune_data)
        
        # 格式化命盤結構
        structure = lock['chart_structure']
        structure_text = f"""
命宮：{', '.join(structure['命宮']['主星'])} ({structure['命宮']['宮位']}宮)
格局：{', '.join(structure['格局'])}
"""
        
        # 組合 Prompt
        prompt = FORTUNE_ANNUAL_ANALYSIS.format(
            chart_structure=structure_text,
            fortune_info=fortune_text,
            target_year=target_year,
            da_xian_number=fortune_data['da_xian']['da_xian_number'],
            da_xian_age_range=f"{fortune_data['da_xian']['age_range'][0]}-{fortune_data['da_xian']['age_range'][1]}",
            da_xian_palace=fortune_data['da_xian']['palace_name'],
            liu_nian_palace=fortune_data['liu_nian']['palace_name'],
            gan_zhi=fortune_data['liu_nian']['gan_zhi']
        )
        
        # 呼叫 Gemini
        logger.info(f'正在生成 {target_year} 年流年分析...', user_id=user_id)
        analysis = call_gemini(prompt)
        
        return jsonify({
            'fortune_data': fortune_data,
            'analysis': analysis
        })
        
    except AetheriaException:
        raise
    except Exception as e:
        logger.error(f'流年分析失敗: {str(e)}', user_id=user_id if 'user_id' in dir() else None)
        return jsonify({'error': str(e)}), 500

@app.route('/api/fortune/monthly', methods=['POST'])
def fortune_monthly():
    """
    流月運勢分析
    
    Request:
    {
        "user_id": "user_123",
        "target_year": 2026,  (可選)
        "target_month": 1     (可選)
    }
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        target_year = data.get('target_year', datetime.now().year)
        target_month = data.get('target_month', datetime.now().month)
        
        if not user_id:
            raise MissingParameterException('user_id')
        
        # 取得鎖定的命盤
        lock = get_chart_lock(user_id)
        if not lock or not lock.get('is_active'):
            raise ChartNotLockedException(user_id)
        
        # 計算流月
        ming_gong_branch = lock['chart_structure']['命宮']['宮位']
        
        user = get_user(user_id)
        birth_info = get_user_birth_info(user)
        if not birth_info:
            raise InvalidParameterException('birth_date', '用戶缺少可解析的出生日期')
        
        teller = FortuneTeller(
            birth_year=birth_info['year'],
            birth_month=birth_info['month'],
            birth_day=birth_info['day'],
            gender=normalize_gender(user.get('gender')),
            ming_gong_branch=ming_gong_branch
        )
        
        fortune_data = teller.get_fortune_summary(target_year, target_month)
        fortune_text = teller.format_fortune_text(fortune_data)
        
        # 格式化命盤結構
        structure = lock['chart_structure']
        structure_text = f"""
命宮：{', '.join(structure['命宮']['主星'])} ({structure['命宮']['宮位']}宮)
格局：{', '.join(structure['格局'])}
"""
        
        # 組合 Prompt
        prompt = FORTUNE_MONTHLY_ANALYSIS.format(
            chart_structure=structure_text,
            fortune_info=fortune_text,
            target_year=target_year,
            target_month=target_month,
            liu_yue_palace=fortune_data['liu_yue']['palace_name']
        )
        
        # 呼叫 Gemini
        logger.info(f'正在生成 {target_year} 年 {target_month} 月流月分析...', user_id=user_id)
        analysis = call_gemini(prompt)
        
        return jsonify({
            'fortune_data': fortune_data,
            'analysis': analysis
        })
        
    except AetheriaException:
        raise
    except Exception as e:
        logger.error(f'流月分析失敗: {str(e)}', user_id=user_id if 'user_id' in dir() else None)
        return jsonify({'error': str(e)}), 500

@app.route('/api/fortune/question', methods=['POST'])
def fortune_question():
    """
    基於流年的特定問題分析
    
    Request:
    {
        "user_id": "user_123",
        "question": "今年適合換工作嗎？"
    }
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        question = data.get('question')
        
        if not user_id:
            raise MissingParameterException('user_id')
        if not question:
            raise MissingParameterException('question')
        
        # 取得鎖定的命盤
        lock = get_chart_lock(user_id)
        if not lock or not lock.get('is_active'):
            raise ChartNotLockedException(user_id)
        
        # 計算當前流年
        ming_gong_branch = lock['chart_structure']['命宮']['宮位']
        
        user = get_user(user_id)
        birth_info = get_user_birth_info(user)
        if not birth_info:
            raise InvalidParameterException('birth_date', '用戶缺少可解析的出生日期')
        
        teller = FortuneTeller(
            birth_year=birth_info['year'],
            birth_month=birth_info['month'],
            birth_day=birth_info['day'],
            gender=normalize_gender(user.get('gender')),
            ming_gong_branch=ming_gong_branch
        )
        
        fortune_data = teller.get_fortune_summary()
        fortune_text = teller.format_fortune_text(fortune_data)
        
        # 格式化命盤結構
        structure = lock['chart_structure']
        structure_text = f"""
命宮：{', '.join(structure['命宮']['主星'])} ({structure['命宮']['宮位']}宮)
格局：{', '.join(structure['格局'])}

十二宮配置：
"""
        for palace, info in structure.get('十二宮', {}).items():
            stars = ', '.join(info['主星']) if info['主星'] else '空宮'
            structure_text += f"- {palace} ({info['宮位']}宮): {stars}\n"
        
        # 組合 Prompt
        prompt = FORTUNE_QUESTION_ANALYSIS.format(
            chart_structure=structure_text,
            fortune_info=fortune_text,
            user_question=question
        )
        
        # 呼叫 Gemini
        logger.info(f'正在分析問題：{question}', user_id=user_id)
        analysis = call_gemini(prompt)
        
        return jsonify({
            'fortune_data': fortune_data,
            'analysis': analysis
        })
        
    except AetheriaException:
        raise
    except Exception as e:
        logger.error(f'流年問題分析失敗: {str(e)}', user_id=user_id if 'user_id' in dir() else None)
        return jsonify({'error': str(e)}), 500

# ============================================
# 合盤分析端點
# ============================================

@app.route('/api/synastry/marriage', methods=['POST'])
def synastry_marriage():
    """合盤分析：婚配相性"""
    try:
        data = request.json
        user_a_id = data.get('user_a_id')
        user_b_id = data.get('user_b_id')
        
        if not user_a_id:
            raise MissingParameterException('user_a_id')
        if not user_b_id:
            raise MissingParameterException('user_b_id')
        
        # 獲取兩位用戶的鎖定命盤
        lock_a = get_chart_lock(user_a_id)
        lock_b = get_chart_lock(user_b_id)
        
        if not lock_a:
            raise ChartNotLockedException(user_a_id)
        if not lock_b:
            raise ChartNotLockedException(user_b_id)
        
        # 獲取用戶資料
        user_a = get_user(user_a_id)
        user_b = get_user(user_b_id)
        
        # 格式化資料
        person_a_info = f"""
姓名代號：{user_a_id}
出生：{user_a.get('birth_date', 'N/A')}
性別：{user_a.get('gender', 'N/A')}
"""
        
        person_b_info = f"""
姓名代號：{user_b_id}
出生：{user_b.get('birth_date', 'N/A')}
性別：{user_b.get('gender', 'N/A')}
"""
        
        # 格式化命盤結構
        chart_a = json.dumps(lock_a['chart_structure'], ensure_ascii=False, indent=2)
        chart_b = json.dumps(lock_b['chart_structure'], ensure_ascii=False, indent=2)
        
        # 組合 Prompt
        prompt = SYNASTRY_MARRIAGE_ANALYSIS.format(
            person_a_info=person_a_info,
            person_a_chart=chart_a,
            person_b_info=person_b_info,
            person_b_chart=chart_b
        )
        
        # 呼叫 Gemini
        logger.info(f'正在分析婚配合盤：{user_a_id} & {user_b_id}')
        analysis = call_gemini(prompt)
        
        return jsonify({
            'user_a_id': user_a_id,
            'user_b_id': user_b_id,
            'analysis_type': '婚配相性',
            'analysis': analysis
        })
        
    except AetheriaException:
        raise
    except Exception as e:
        logger.error(f'婚配合盤分析失敗: {str(e)}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/synastry/partnership', methods=['POST'])
def synastry_partnership():
    """合盤分析：合夥相性"""
    try:
        data = request.json
        user_a_id = data.get('user_a_id')
        user_b_id = data.get('user_b_id')
        partnership_info = data.get('partnership_info', '未提供具體合夥項目資訊')
        
        if not user_a_id:
            raise MissingParameterException('user_a_id')
        if not user_b_id:
            raise MissingParameterException('user_b_id')
        
        # 獲取兩位用戶的鎖定命盤
        lock_a = get_chart_lock(user_a_id)
        lock_b = get_chart_lock(user_b_id)
        
        if not lock_a:
            raise ChartNotLockedException(user_a_id)
        if not lock_b:
            raise ChartNotLockedException(user_b_id)
        
        # 獲取用戶資料
        user_a = get_user(user_a_id)
        user_b = get_user(user_b_id)
        
        # 格式化資料
        person_a_info = f"""
姓名代號：{user_a_id}
出生：{user_a.get('birth_date', 'N/A')}
性別：{user_a.get('gender', 'N/A')}
"""
        
        person_b_info = f"""
姓名代號：{user_b_id}
出生：{user_b.get('birth_date', 'N/A')}
性別：{user_b.get('gender', 'N/A')}
"""
        
        # 格式化命盤結構
        chart_a = json.dumps(lock_a['chart_structure'], ensure_ascii=False, indent=2)
        chart_b = json.dumps(lock_b['chart_structure'], ensure_ascii=False, indent=2)
        
        # 組合 Prompt
        prompt = SYNASTRY_PARTNERSHIP_ANALYSIS.format(
            person_a_info=person_a_info,
            person_a_chart=chart_a,
            person_b_info=person_b_info,
            person_b_chart=chart_b,
            partnership_info=partnership_info
        )
        
        # 呼叫 Gemini
        logger.info(f'正在分析合夥關係：{user_a_id} & {user_b_id}')
        analysis = call_gemini(prompt)
        
        return jsonify({
            'user_a_id': user_a_id,
            'user_b_id': user_b_id,
            'analysis_type': '合夥相性',
            'partnership_info': partnership_info,
            'analysis': analysis
        })
        
    except AetheriaException:
        raise
    except Exception as e:
        logger.error(f'合夥合盤分析失敗: {str(e)}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/synastry/quick', methods=['POST'])
def synastry_quick():
    """快速合盤評估"""
    try:
        data = request.json
        user_a_id = data.get('user_a_id')
        user_b_id = data.get('user_b_id')
        analysis_type = data.get('analysis_type', '婚配')  # 婚配 或 合夥
        
        if not user_a_id:
            raise MissingParameterException('user_a_id')
        if not user_b_id:
            raise MissingParameterException('user_b_id')
        
        # 獲取兩位用戶的鎖定命盤
        lock_a = get_chart_lock(user_a_id)
        lock_b = get_chart_lock(user_b_id)
        
        if not lock_a:
            raise ChartNotLockedException(user_a_id)
        if not lock_b:
            raise ChartNotLockedException(user_b_id)
        
        # 獲取用戶資料
        user_a = get_user(user_a_id)
        user_b = get_user(user_b_id)
        
        # 提取關鍵資訊
        chart_a = lock_a['chart_structure']
        chart_b = lock_b['chart_structure']
        
        ming_gong_a = f"{', '.join(chart_a['命宮']['主星'])} ({chart_a['命宮']['宮位']}宮)"
        ming_gong_b = f"{', '.join(chart_b['命宮']['主星'])} ({chart_b['命宮']['宮位']}宮)"
        
        # 根據分析類型選擇關鍵宮位
        if analysis_type == '婚配':
            key_palace_name = '夫妻宮'
        else:
            key_palace_name = '官祿宮'
        
        key_palace_a = chart_a.get('十二宮', {}).get(key_palace_name, {})
        key_palace_b = chart_b.get('十二宮', {}).get(key_palace_name, {})
        
        key_info_a = f"{', '.join(key_palace_a.get('主星', ['空宮']))} ({key_palace_a.get('宮位', 'N/A')}宮)"
        key_info_b = f"{', '.join(key_palace_b.get('主星', ['空宮']))} ({key_palace_b.get('宮位', 'N/A')}宮)"
        
        # 格式化資料
        person_a_info = f"{user_a_id} - {user_a.get('gender', 'N/A')}"
        person_b_info = f"{user_b_id} - {user_b.get('gender', 'N/A')}"
        
        # 組合 Prompt
        prompt = SYNASTRY_QUICK_CHECK.format(
            person_a_info=person_a_info,
            person_a_ming_gong=ming_gong_a,
            person_a_key_palace=key_info_a,
            person_b_info=person_b_info,
            person_b_ming_gong=ming_gong_b,
            person_b_key_palace=key_info_b,
            analysis_type=analysis_type
        )
        
        # 呼叫 Gemini
        logger.info(f'正在快速合盤：{user_a_id} & {user_b_id} ({analysis_type})')
        analysis = call_gemini(prompt)
        
        return jsonify({
            'user_a_id': user_a_id,
            'user_b_id': user_b_id,
            'analysis_type': f'快速{analysis_type}評估',
            'analysis': analysis
        })
        
    except AetheriaException:
        raise
    except Exception as e:
        logger.error(f'快速合盤失敗: {str(e)}')
        return jsonify({'error': str(e)}), 500


# ============================================
# 擇日功能端點
# ============================================

@app.route('/api/date-selection/marriage', methods=['POST'])
def date_selection_marriage():
    """擇日：婚嫁吉日"""
    try:
        data = request.json
        groom_id = data.get('groom_id')
        bride_id = data.get('bride_id')
        target_year = data.get('target_year', datetime.now().year)
        preferred_months = data.get('preferred_months', '全年皆可')
        avoid_dates = data.get('avoid_dates', '無')
        other_requirements = data.get('other_requirements', '無')
        
        if not groom_id or not bride_id:
            return jsonify({'error': '需要提供新郎和新娘的 ID'}), 400
        
        # 獲取兩位用戶的鎖定命盤
        lock_groom = get_chart_lock(groom_id)
        lock_bride = get_chart_lock(bride_id)
        
        if not lock_groom or not lock_bride:
            return jsonify({'error': '新郎新娘都需要先完成定盤'}), 400
        
        # 獲取用戶資料
        groom = get_user(groom_id)
        bride = get_user(bride_id)
        
        # 計算流年資訊（簡化版，實際需要從出生資料計算）
        # 這裡使用 FortuneTeller 計算
        birth_year_groom = 1979  # 需要從 birth_date 解析
        birth_year_bride = 1980  # 需要從 birth_date 解析
        
        ming_gong_groom = lock_groom['chart_structure']['命宮']['宮位']
        ming_gong_bride = lock_bride['chart_structure']['命宮']['宮位']
        
        teller_groom = FortuneTeller(
            birth_year=birth_year_groom,
            birth_month=9,
            birth_day=23,
            gender=groom.get('gender', '男'),
            ming_gong_branch=ming_gong_groom
        )
        
        teller_bride = FortuneTeller(
            birth_year=birth_year_bride,
            birth_month=5,
            birth_day=15,
            gender=bride.get('gender', '女'),
            ming_gong_branch=ming_gong_bride
        )
        
        da_xian_groom = teller_groom.calculate_da_xian(target_year)
        liu_nian_groom = teller_groom.calculate_liu_nian(target_year)
        
        da_xian_bride = teller_bride.calculate_da_xian(target_year)
        liu_nian_bride = teller_bride.calculate_liu_nian(target_year)
        
        # 格式化資料
        groom_info = f"""
姓名代號：{groom_id}
出生：{groom.get('birth_date', 'N/A')}
性別：{groom.get('gender', 'N/A')}
"""
        
        bride_info = f"""
姓名代號：{bride_id}
出生：{bride.get('birth_date', 'N/A')}
性別：{bride.get('gender', 'N/A')}
"""
        
        groom_chart = json.dumps(lock_groom['chart_structure'], ensure_ascii=False, indent=2)
        bride_chart = json.dumps(lock_bride['chart_structure'], ensure_ascii=False, indent=2)
        
        groom_da_xian_str = f"第{da_xian_groom['da_xian_number']}大限 ({da_xian_groom['age_range'][0]}-{da_xian_groom['age_range'][1]}歲) {da_xian_groom['palace_name']}"
        bride_da_xian_str = f"第{da_xian_bride['da_xian_number']}大限 ({da_xian_bride['age_range'][0]}-{da_xian_bride['age_range'][1]}歲) {da_xian_bride['palace_name']}"
        
        groom_liu_nian_str = f"{liu_nian_groom['year']}年 {liu_nian_groom['gan_zhi']} {liu_nian_groom['palace_name']}"
        bride_liu_nian_str = f"{liu_nian_bride['year']}年 {liu_nian_bride['gan_zhi']} {liu_nian_bride['palace_name']}"
        
        # 組合 Prompt
        prompt = DATE_SELECTION_MARRIAGE.format(
            groom_info=groom_info,
            groom_chart=groom_chart,
            groom_da_xian=groom_da_xian_str,
            groom_liu_nian=groom_liu_nian_str,
            bride_info=bride_info,
            bride_chart=bride_chart,
            bride_da_xian=bride_da_xian_str,
            bride_liu_nian=bride_liu_nian_str,
            target_year=target_year,
            preferred_months=preferred_months,
            avoid_dates=avoid_dates,
            other_requirements=other_requirements
        )
        
        # 呼叫 Gemini
        logger.info(f'正在為婚禮擇日：{groom_id} & {bride_id} ({target_year}年)')
        analysis = call_gemini(prompt)
        
        return jsonify({
            'groom_id': groom_id,
            'bride_id': bride_id,
            'target_year': target_year,
            'analysis_type': '婚嫁擇日',
            'analysis': analysis
        })
        
    except AetheriaException:
        raise
    except Exception as e:
        logger.error(f'婚禮擇日失敗: {str(e)}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/date-selection/business', methods=['POST'])
def date_selection_business():
    """擇日：開業吉日"""
    try:
        data = request.json
        owner_id = data.get('owner_id')
        target_year = data.get('target_year', datetime.now().year)
        business_type = data.get('business_type', '未指定')
        business_nature = data.get('business_nature', '一般商業')
        business_direction = data.get('business_direction', '未指定')
        preferred_months = data.get('preferred_months', '全年皆可')
        avoid_dates = data.get('avoid_dates', '無')
        other_requirements = data.get('other_requirements', '無')
        partner_id = data.get('partner_id')  # 可選
        
        if not owner_id:
            return jsonify({'error': '需要提供負責人 ID'}), 400
        
        # 獲取負責人的鎖定命盤
        lock_owner = get_chart_lock(owner_id)
        
        if not lock_owner:
            return jsonify({'error': '負責人需要先完成定盤'}), 400
        
        owner = get_user(owner_id)
        
        # 計算流年資訊
        birth_year = 1979  # 需要從 birth_date 解析
        ming_gong = lock_owner['chart_structure']['命宮']['宮位']
        
        teller = FortuneTeller(
            birth_year=birth_year,
            birth_month=9,
            birth_day=23,
            gender=owner.get('gender', '男'),
            ming_gong_branch=ming_gong
        )
        
        da_xian = teller.calculate_da_xian(target_year)
        liu_nian = teller.calculate_liu_nian(target_year)
        
        # 格式化資料
        owner_info = f"""
姓名代號：{owner_id}
出生：{owner.get('birth_date', 'N/A')}
性別：{owner.get('gender', 'N/A')}
"""
        
        owner_chart = json.dumps(lock_owner['chart_structure'], ensure_ascii=False, indent=2)
        
        da_xian_str = f"第{da_xian['da_xian_number']}大限 ({da_xian['age_range'][0]}-{da_xian['age_range'][1]}歲) {da_xian['palace_name']}"
        liu_nian_str = f"{liu_nian['year']}年 {liu_nian['gan_zhi']} {liu_nian['palace_name']}"
        
        # 合夥人資訊（如果有）
        partner_chart_str = '無合夥人'
        if partner_id:
            lock_partner = get_chart_lock(partner_id)
            if lock_partner:
                partner_chart_str = json.dumps(lock_partner['chart_structure'], ensure_ascii=False, indent=2)
        
        # 組合 Prompt
        prompt = DATE_SELECTION_BUSINESS.format(
            owner_info=owner_info,
            owner_chart=owner_chart,
            owner_da_xian=da_xian_str,
            owner_liu_nian=liu_nian_str,
            business_type=business_type,
            business_nature=business_nature,
            business_direction=business_direction,
            partner_chart=partner_chart_str,
            target_year=target_year,
            preferred_months=preferred_months,
            avoid_dates=avoid_dates,
            other_requirements=other_requirements
        )
        
        # 呼叫 Gemini
        logger.info(f'正在為開業擇日：{owner_id} ({target_year}年)')
        analysis = call_gemini(prompt)
        
        return jsonify({
            'owner_id': owner_id,
            'target_year': target_year,
            'business_type': business_type,
            'analysis_type': '開業擇日',
            'analysis': analysis
        })
        
    except AetheriaException:
        raise
    except Exception as e:
        logger.error(f'開業擇日失敗: {str(e)}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/date-selection/moving', methods=['POST'])
def date_selection_moving():
    """擇日：搬家入宅"""
    try:
        data = request.json
        owner_id = data.get('owner_id')
        target_year = data.get('target_year', datetime.now().year)
        new_address = data.get('new_address', '未提供')
        new_direction = data.get('new_direction', '未指定')
        house_orientation = data.get('house_orientation', '未指定')
        number_of_people = data.get('number_of_people', 1)
        family_members = data.get('family_members', '僅宅主一人')
        preferred_months = data.get('preferred_months', '全年皆可')
        avoid_dates = data.get('avoid_dates', '無')
        other_requirements = data.get('other_requirements', '無')
        
        if not owner_id:
            return jsonify({'error': '需要提供宅主 ID'}), 400
        
        # 獲取宅主的鎖定命盤
        lock_owner = get_chart_lock(owner_id)
        
        if not lock_owner:
            return jsonify({'error': '宅主需要先完成定盤'}), 400
        
        owner = get_user(owner_id)
        
        # 計算流年資訊
        birth_year = 1979
        ming_gong = lock_owner['chart_structure']['命宮']['宮位']
        
        teller = FortuneTeller(
            birth_year=birth_year,
            birth_month=9,
            birth_day=23,
            gender=owner.get('gender', '男'),
            ming_gong_branch=ming_gong
        )
        
        da_xian = teller.calculate_da_xian(target_year)
        liu_nian = teller.calculate_liu_nian(target_year)
        
        # 格式化資料
        owner_info = f"""
姓名代號：{owner_id}
出生：{owner.get('birth_date', 'N/A')}
性別：{owner.get('gender', 'N/A')}
"""
        
        owner_chart = json.dumps(lock_owner['chart_structure'], ensure_ascii=False, indent=2)
        
        da_xian_str = f"第{da_xian['da_xian_number']}大限 ({da_xian['age_range'][0]}-{da_xian['age_range'][1]}歲) {da_xian['palace_name']}"
        liu_nian_str = f"{liu_nian['year']}年 {liu_nian['gan_zhi']} {liu_nian['palace_name']}"
        
        # 組合 Prompt
        prompt = DATE_SELECTION_MOVING.format(
            owner_info=owner_info,
            owner_chart=owner_chart,
            owner_da_xian=da_xian_str,
            owner_liu_nian=liu_nian_str,
            family_members=family_members,
            new_address=new_address,
            new_direction=new_direction,
            house_orientation=house_orientation,
            number_of_people=number_of_people,
            target_year=target_year,
            preferred_months=preferred_months,
            avoid_dates=avoid_dates,
            other_requirements=other_requirements
        )
        
        # 呼叫 Gemini
        logger.info(f'正在為搬家擇日：{owner_id} ({target_year}年)')
        analysis = call_gemini(prompt)
        
        return jsonify({
            'owner_id': owner_id,
            'target_year': target_year,
            'new_address': new_address,
            'analysis_type': '搬家入宅擇日',
            'analysis': analysis
        })
        
    except AetheriaException:
        raise
    except Exception as e:
        logger.error(f'搬家擇日失敗: {str(e)}')
        return jsonify({'error': str(e)}), 500

# ============================================
# 八字命理 API
# ============================================

@app.route('/api/bazi/calculate', methods=['POST'])
def bazi_calculate():
    """
    八字排盘计算
    
    请求参数：
    {
        "year": 1979,
        "month": 10,
        "day": 11,
        "hour": 23,
        "minute": 58,
        "gender": "male",
        "longitude": 120.52,  # 可选，用于真太阳时修正
        "use_apparent_solar_time": true  # 可选，是否使用真太阳时
    }
    """
    try:
        data = request.json
        
        # 验证必需参数
        required_fields = ['year', 'month', 'day', 'hour', 'gender']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'缺少必需参数：{field}'
                }), 400
        
        # 创建八字计算器
        calculator = BaziCalculator()
        gender = normalize_gender(data['gender'])
        
        # 计算八字
        bazi_result = calculator.calculate_bazi(
            year=data['year'],
            month=data['month'],
            day=data['day'],
            hour=data['hour'],
            minute=data.get('minute', 0),
            gender=gender,
            longitude=data.get('longitude'),
            use_apparent_solar_time=data.get('use_apparent_solar_time', False)
        )
        
        return jsonify({
            'status': 'success',
            'data': bazi_result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'八字计算失败：{str(e)}'
        }), 500


@app.route('/api/bazi/analysis', methods=['POST'])
def bazi_analysis():
    """
    八字命理分析
    
    请求参数：
    {
        "user_id": "test_user_001",
        "year": 1979,
        "month": 10,
        "day": 11,
        "hour": 23,
        "minute": 58,
        "gender": "male",
        "longitude": 120.52,
        "use_apparent_solar_time": true
    }
    """
    try:
        data = request.json
        
        # 验证必需参数
        required_fields = ['year', 'month', 'day', 'hour', 'gender']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'缺少必需参数：{field}'
                }), 400
        
        # 计算八字
        calculator = BaziCalculator()
        gender = normalize_gender(data['gender'])
        bazi_result = calculator.calculate_bazi(
            year=data['year'],
            month=data['month'],
            day=data['day'],
            hour=data['hour'],
            minute=data.get('minute', 0),
            gender=gender,
            longitude=data.get('longitude'),
            use_apparent_solar_time=data.get('use_apparent_solar_time', False)
        )
        
        # 生成分析提示词
        prompt = format_bazi_analysis_prompt(
            bazi_result=bazi_result,
            gender=gender,
            birth_year=data['year'],
            birth_month=data['month'],
            birth_day=data['day'],
            birth_hour=data['hour']
        )
        
        # 调用 AI 进行分析（使用統一的 call_gemini）
        analysis_text = call_gemini(prompt)
        
        return jsonify({
            'status': 'success',
            'data': {
                'bazi_chart': bazi_result,
                'analysis': analysis_text,
                'user_id': data.get('user_id'),
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'八字分析失败：{str(e)}'
        }), 500


@app.route('/api/bazi/fortune', methods=['POST'])
def bazi_fortune():
    """
    八字流年/流月运势分析
    
    请求参数：
    {
        "user_id": "test_user_001",
        "year": 1979,
        "month": 10,
        "day": 11,
        "hour": 23,
        "gender": "male",
        "query_year": 2024,
        "query_month": null,  # 可选，如果为null则分析全年
        "longitude": 120.52
    }
    """
    try:
        data = request.json
        
        # 验证必需参数
        required_fields = ['year', 'month', 'day', 'hour', 'gender', 'query_year']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'缺少必需参数：{field}'
                }), 400
        
        # 计算八字
        calculator = BaziCalculator()
        gender = normalize_gender(data['gender'])
        bazi_result = calculator.calculate_bazi(
            year=data['year'],
            month=data['month'],
            day=data['day'],
            hour=data['hour'],
            minute=data.get('minute', 0),
            gender=gender,
            longitude=data.get('longitude'),
            use_apparent_solar_time=data.get('use_apparent_solar_time', False)
        )
        
        # 生成运势分析提示词
        prompt = format_bazi_fortune_prompt(
            bazi_result=bazi_result,
            query_year=data['query_year'],
            query_month=data.get('query_month')
        )
        
        # 调用 AI 进行分析（使用統一的 call_gemini）
        analysis_text = call_gemini(prompt)
        
        return jsonify({
            'status': 'success',
            'data': {
                'bazi_chart': bazi_result,
                'fortune_analysis': analysis_text,
                'query_year': data['query_year'],
                'query_month': data.get('query_month'),
                'user_id': data.get('user_id'),
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'运势分析失败：{str(e)}'
        }), 500


@app.route('/api/cross-validation/ziwei-bazi', methods=['POST'])
def cross_validation_ziwei_bazi():
    """
    紫微斗数 + 八字命理 交叉验证分析
    
    请求参数：
    {
        "user_id": "test_user_001",
        "year": 1979,
        "month": 10,
        "day": 11,
        "hour": 23,
        "minute": 58,
        "gender": "male",
        "longitude": 120.52,
        "use_apparent_solar_time": true
    }
    """
    try:
        data = request.json
        
        # 验证必需参数
        required_fields = ['year', 'month', 'day', 'hour', 'gender']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'缺少必需参数：{field}'
                }), 400
        
        user_id = data.get('user_id', 'anonymous')
        user_facts = data.get('user_facts', '')
        
        # 1. 获取紫微斗数锁盘信息
        lock_data = get_chart_lock(user_id)
        if not lock_data or not lock_data.get('is_active'):
            return jsonify({
                'status': 'error',
                'message': '用户未锁定紫微命盘，请先完成紫微斗数分析并锁定命盘'
            }), 400
        
        # 2. 计算八字
        calculator = BaziCalculator()
        bazi_result = calculator.calculate_bazi(
            year=data['year'],
            month=data['month'],
            day=data['day'],
            hour=data['hour'],
            minute=data.get('minute', 0),
            gender=data['gender'],
            longitude=data.get('longitude'),
            use_apparent_solar_time=data.get('use_apparent_solar_time', False)
        )
        
        # 3. 准备紫微命盘信息摘要
        chart_structure = lock_data.get('chart_structure', {})
        ming_gong = chart_structure.get('命宮', {})
        
        ziwei_chart_info = f"""
    命宮：{ming_gong.get('宮位', '未知')} 宮
    主星：{', '.join(ming_gong.get('主星', []))}
    輔星：{', '.join(ming_gong.get('輔星', []))}
    格局：{', '.join(chart_structure.get('格局', []))}
    五行局：{chart_structure.get('五行局', '未知')}
        """
        
        # 4. 如果有之前的紫微分析，获取摘要（简化版）
        ziwei_analysis_summary = to_zh_tw(lock_data.get('initial_analysis_summary', 
            "紫微分析摘要：請參考完整的紫微斗數分析報告"))
        
        # 5. 获取八字分析摘要（先进行简短分析）
        bazi_summary_prompt = f"""请用200-300字简要总结以下八字的核心特点：

年柱：{bazi_result['四柱']['年柱']['天干']}{bazi_result['四柱']['年柱']['地支']}
月柱：{bazi_result['四柱']['月柱']['天干']}{bazi_result['四柱']['月柱']['地支']}
日柱：{bazi_result['四柱']['日柱']['天干']}{bazi_result['四柱']['日柱']['地支']}
时柱：{bazi_result['四柱']['时柱']['天干']}{bazi_result['四柱']['时柱']['地支']}

日主：{bazi_result['日主']['天干']}（{bazi_result['日主']['五行']}）
强弱：{bazi_result['强弱']['结论']}
用神：{', '.join(bazi_result['用神']['用神'])}
"""
        
        # 使用統一的 call_gemini
        bazi_analysis_summary = call_gemini(bazi_summary_prompt)
        
        # 6. 生成交叉验证提示词
        prompt = format_cross_validation_prompt(
            user_id=user_id,
            gender=data['gender'],
            birth_year=data['year'],
            birth_month=data['month'],
            birth_day=data['day'],
            birth_hour=data['hour'],
            longitude=data.get('longitude', 120.0),
            ziwei_chart_info=ziwei_chart_info,
            ziwei_analysis_summary=ziwei_analysis_summary,
            bazi_result=bazi_result,
            bazi_analysis_summary=bazi_analysis_summary,
            user_facts=user_facts
        )
        
        # 7. 调用 AI 进行交叉验证分析（使用統一的 call_gemini）
        validation_text = call_gemini(prompt)

        body_palace = chart_structure.get('身宮', {}).get('宮位', '未知')
        
        return jsonify({
            'status': 'success',
            'data': {
                'ziwei_chart': {
                    'locked_palace': ming_gong.get('宮位', '未知'),
                    'body_palace': body_palace,
                    'main_stars': ming_gong.get('主星', []),
                    'aux_stars': ming_gong.get('輔星', []),
                    'patterns': chart_structure.get('格局', [])
                },
                'bazi_chart': bazi_result,
                'cross_validation_analysis': validation_text,
                'ziwei_summary': ziwei_analysis_summary,
                'bazi_summary': bazi_analysis_summary,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'交叉验证分析失败：{str(e)}'
        }), 500


# ============================================
# 西洋占星術 API
# ============================================

@app.route('/api/astrology/natal', methods=['POST'])
def astrology_natal_chart():
    """
    西洋占星術本命盤分析
    
    Request Body:
    {
        "name": "姓名",
        "year": 1979,
        "month": 11,
        "day": 12,
        "hour": 23,
        "minute": 58,
        "city": "彰化市",  # 可選
        "longitude": 120.52,  # 可選，若有則優先使用
        "latitude": 24.08,  # 可選
        "timezone": "Asia/Taipei",  # 可選
        "user_facts": {  # 可選，用於交叉驗證
            "性格特質": "...",
            "職業": "..."
        }
    }
    """
    try:
        data = request.json
        
        # 必填欄位
        name = data.get('name')
        year = data.get('year')
        month = data.get('month')
        day = data.get('day')
        hour = data.get('hour')
        minute = data.get('minute')
        
        if not all([name, year, month, day, hour is not None, minute is not None]):
            return jsonify({
                'status': 'error',
                'message': '缺少必要參數：name, year, month, day, hour, minute'
            }), 400
        
        # 可選欄位
        city = data.get('city', 'Taipei')
        longitude = data.get('longitude')
        latitude = data.get('latitude')
        timezone_str = data.get('timezone', 'Asia/Taipei')
        user_facts = data.get('user_facts', None)

        # 若未提供經緯度，嘗試解析台灣常見地名
        if longitude is None or latitude is None:
            taiwan_cities = {
                '台北': (25.0330, 121.5654), '台北市': (25.0330, 121.5654),
                '新北': (25.0169, 121.4628), '新北市': (25.0169, 121.4628),
                '桃園': (24.9936, 121.3010), '桃園市': (24.9936, 121.3010),
                '台中': (24.1477, 120.6736), '台中市': (24.1477, 120.6736),
                '台南': (22.9998, 120.2270), '台南市': (22.9998, 120.2270),
                '高雄': (22.6273, 120.3014), '高雄市': (22.6273, 120.3014),
                '基隆': (25.1276, 121.7392), '基隆市': (25.1276, 121.7392),
                '新竹': (24.8138, 120.9675), '新竹市': (24.8138, 120.9675),
                '嘉義': (23.4801, 120.4491), '嘉義市': (23.4801, 120.4491),
                '彰化': (24.0518, 120.5161), '彰化市': (24.0518, 120.5161), '彰化縣': (24.0518, 120.5161),
                '南投': (23.9609, 120.9719), '南投市': (23.9609, 120.9719), '南投縣': (23.9609, 120.9719),
                '雲林': (23.7092, 120.4313), '雲林縣': (23.7092, 120.4313),
                '苗栗': (24.5602, 120.8214), '苗栗市': (24.5602, 120.8214), '苗栗縣': (24.5602, 120.8214),
                '屏東': (22.6727, 120.4871), '屏東市': (22.6727, 120.4871), '屏東縣': (22.6727, 120.4871),
                '宜蘭': (24.7570, 121.7533), '宜蘭市': (24.7570, 121.7533), '宜蘭縣': (24.7570, 121.7533),
                '花蓮': (23.9910, 121.6114), '花蓮市': (23.9910, 121.6114), '花蓮縣': (23.9910, 121.6114),
                '台東': (22.7583, 121.1444), '台東市': (22.7583, 121.1444), '台東縣': (22.7583, 121.1444),
                '澎湖': (23.5711, 119.5793), '澎湖縣': (23.5711, 119.5793),
                '金門': (24.4493, 118.3767), '金門縣': (24.4493, 118.3767),
                '連江': (26.1505, 119.9499), '連江縣': (26.1505, 119.9499), '馬祖': (26.1505, 119.9499),
            }

            city_name = (city or '').replace('台灣', '').replace('臺灣', '').strip()
            for city_key, (city_lat, city_lng) in taiwan_cities.items():
                if city_key in city_name:
                    latitude, longitude = city_lat, city_lng
                    break
        
        # 計算本命盤
        natal_chart = astrology_calc.calculate_natal_chart(
            name=name,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            city=city,
            longitude=longitude,
            latitude=latitude,
            timezone_str=timezone_str
        )
        
        # 格式化為文本
        chart_text = astrology_calc.format_for_gemini(natal_chart)
        
        # 生成 Gemini 分析提示詞
        prompt = get_natal_chart_analysis_prompt(chart_text, user_facts)
        
        # 調用 Gemini 分析（使用統一的 call_gemini）
        system_instruction = "你是專精西洋占星術的命理分析師，遵循「有所本」原則，所有解釋必須引用占星學經典理論。輸出必須使用繁體中文（台灣用語）。"
        full_prompt = f"{system_instruction}\n\n{prompt}"
        analysis = call_gemini(full_prompt, "")
        
        return jsonify({
            'status': 'success',
            'data': {
                'natal_chart': natal_chart,
                'chart_text': chart_text,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'本命盤分析失敗：{str(e)}'
        }), 500


@app.route('/api/astrology/synastry', methods=['POST'])
def astrology_synastry():
    """
    西洋占星術合盤分析（兩人關係）
    
    Request Body:
    {
        "person1": {
            "name": "...",
            "year": 1979,
            "month": 11,
            "day": 12,
            "hour": 23,
            "minute": 58,
            "longitude": 120.52,
            "latitude": 24.08,
            "timezone": "Asia/Taipei"
        },
        "person2": {
            "name": "...",
            "year": 1985,
            ...
        },
        "relationship_facts": {  # 可選
            "關係類型": "情侶",
            "認識時間": "2020年"
        }
    }
    """
    try:
        data = request.json
        person1_data = data.get('person1')
        person2_data = data.get('person2')
        relationship_facts = data.get('relationship_facts', None)
        
        if not person1_data or not person2_data:
            return jsonify({
                'status': 'error',
                'message': '缺少必要參數：person1, person2'
            }), 400
        
        # 計算兩人的本命盤
        chart1 = astrology_calc.calculate_natal_chart(**person1_data)
        chart2 = astrology_calc.calculate_natal_chart(**person2_data)
        
        # 格式化為文本
        chart1_text = astrology_calc.format_for_gemini(chart1)
        chart2_text = astrology_calc.format_for_gemini(chart2)
        
        # 生成合盤分析提示詞
        prompt = get_synastry_analysis_prompt(chart1_text, chart2_text, relationship_facts)
        
        # 調用 Gemini 分析
        system_instruction = "你是專精合盤分析的西洋占星師，遵循「有所本」與「實證導向」原則。輸出必須使用繁體中文（台灣用語）。"
        full_prompt = f"{system_instruction}\n\n{prompt}"
        analysis = sanitize_plain_text(call_gemini(full_prompt, max_output_tokens=1200))
        
        return jsonify({
            'status': 'success',
            'data': {
                'person1_chart': chart1,
                'person2_chart': chart2,
                'synastry_analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'合盤分析失敗：{str(e)}'
        }), 500


@app.route('/api/astrology/transit', methods=['POST'])
def astrology_transit():
    """
    西洋占星術流年運勢分析
    
    Request Body:
    {
        "name": "...",
        "year": 1979,
        "month": 11,
        "day": 12,
        "hour": 23,
        "minute": 58,
        "longitude": 120.52,
        "latitude": 24.08,
        "timezone": "Asia/Taipei",
        "transit_date": "2026-01-24"  # 要分析的日期
    }
    """
    try:
        data = request.json
        transit_date = data.get('transit_date')
        
        if not transit_date:
            return jsonify({
                'status': 'error',
                'message': '缺少必要參數：transit_date'
            }), 400
        
        # 計算本命盤
        natal_chart = astrology_calc.calculate_natal_chart(
            name=data.get('name'),
            year=data.get('year'),
            month=data.get('month'),
            day=data.get('day'),
            hour=data.get('hour'),
            minute=data.get('minute'),
            longitude=data.get('longitude'),
            latitude=data.get('latitude'),
            timezone_str=data.get('timezone', 'Asia/Taipei')
        )
        
        chart_text = astrology_calc.format_for_gemini(natal_chart)
        
        # 生成流年分析提示詞
        prompt = get_transit_analysis_prompt(chart_text, transit_date)
        
        # 調用 Gemini 分析
        system_instruction = "你是專精流年運勢的西洋占星師，遵循「有所本」原則。輸出必須使用繁體中文（台灣用語）。"
        full_prompt = f"{system_instruction}\n\n{prompt}"
        analysis = sanitize_plain_text(call_gemini(full_prompt, max_output_tokens=800))
        
        return jsonify({
            'status': 'success',
            'data': {
                'natal_chart': natal_chart,
                'transit_date': transit_date,
                'transit_analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'流年分析失敗：{str(e)}'
        }), 500


@app.route('/api/astrology/career', methods=['POST'])
def astrology_career():
    """
    西洋占星術事業發展分析
    
    Request Body:
    {
        "name": "...",
        "year": 1979,
        "month": 11,
        "day": 12,
        "hour": 23,
        "minute": 58,
        "longitude": 120.52,
        "latitude": 24.08,
        "timezone": "Asia/Taipei",
        "career_facts": {  # 可選
            "current_job": "軟體工程師",
            "work_history": "10年科技業經驗",
            "career_goal": "創業"
        }
    }
    """
    try:
        data = request.json
        career_facts = data.get('career_facts', None)
        
        # 計算本命盤
        natal_chart = astrology_calc.calculate_natal_chart(
            name=data.get('name'),
            year=data.get('year'),
            month=data.get('month'),
            day=data.get('day'),
            hour=data.get('hour'),
            minute=data.get('minute'),
            longitude=data.get('longitude'),
            latitude=data.get('latitude'),
            timezone_str=data.get('timezone', 'Asia/Taipei')
        )
        
        chart_text = astrology_calc.format_for_gemini(natal_chart)
        
        # 生成事業分析提示詞
        prompt = get_career_analysis_prompt(chart_text, career_facts)
        
        # 調用 Gemini 分析
        system_instruction = "你是專精事業占星的分析師，遵循「有所本」與「實證導向」原則。輸出必須使用繁體中文（台灣用語）。"
        full_prompt = f"{system_instruction}\n\n{prompt}"
        analysis = call_gemini(full_prompt)
        
        return jsonify({
            'status': 'success',
            'data': {
                'natal_chart': natal_chart,
                'career_analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'事業分析失敗：{str(e)}'
        }), 500


# ============================================
# 塔羅牌 API
# ============================================

@app.route('/api/tarot/reading', methods=['POST'])
def tarot_reading():
    """
    塔羅牌解讀
    
    POST /api/tarot/reading
    {
        "spread_type": "single|three_card|celtic_cross|relationship|decision",
        "question": "問題（可選）",
        "context": "general|love|career|finance|health",
        "allow_reversed": true/false（預設 true）
    }
    
    Returns:
        牌陣資訊、抽牌結果、AI 解讀
    """
    try:
        data = request.get_json(silent=True) or {}
        
        spread_type = data.get('spread_type', 'single')
        question = data.get('question')
        context = data.get('context', 'general')
        allow_reversed = data.get('allow_reversed', True)
        
        # 驗證牌陣類型
        valid_spreads = ['single', 'three_card', 'celtic_cross', 'relationship', 'decision']
        if spread_type not in valid_spreads:
            return jsonify({
                'status': 'error',
                'message': f'不支援的牌陣類型。支援：{valid_spreads}'
            }), 400
        
        # 驗證問題情境
        valid_contexts = ['general', 'love', 'career', 'finance', 'health']
        if context not in valid_contexts:
            return jsonify({
                'status': 'error',
                'message': f'不支援的問題情境。支援：{valid_contexts}'
            }), 400
        
        # 抽牌
        reading = tarot_calc.draw_cards(
            spread_type=spread_type,
            question=question,
            allow_reversed=allow_reversed
        )
        
        # 生成解讀（預設快速模式）
        fast_mode = data.get('fast_mode', True)
        if fast_mode:
            analysis = build_tarot_fallback(reading, context)
        else:
            # AI 深度解讀模式，失敗時自動降級為快速模式
            try:
                prompts = generate_tarot_prompt(reading, context)
                system_instruction = prompts['system_prompt'] + "\n\n輸出必須使用繁體中文（台灣用語）。"
                full_prompt = f"{system_instruction}\n\n{prompts['user_prompt']}"
                analysis = sanitize_plain_text(call_gemini(full_prompt, max_output_tokens=1200))
                if not analysis or len(analysis.strip()) < 50:
                    # AI 回傳空內容或過短，降級為快速模式
                    logger.warning('塔羅 AI 解讀回傳內容不足，降級為快速模式')
                    analysis = build_tarot_fallback(reading, context) + "\n\n（註：AI 深度解讀暫時無法使用，已改為基本解讀）"
            except Exception as ai_err:
                logger.warning(f'塔羅 AI 解讀失敗，降級為快速模式: {str(ai_err)}')
                analysis = build_tarot_fallback(reading, context) + "\n\n（註：AI 深度解讀暫時無法使用，已改為基本解讀）"
        
        # 準備回傳資料
        reading_data = tarot_calc.to_dict(reading)
        
        return jsonify({
            'status': 'success',
            'data': {
                'reading_id': reading.reading_id,
                'spread_type': spread_type,
                'spread_name': reading.spread_name,
                'question': question,
                'context': context,
                'cards': reading_data['cards'],
                'interpretation': analysis,
                'timestamp': reading.timestamp
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'塔羅牌解讀失敗：{str(e)}'
        }), 500


@app.route('/api/tarot/daily', methods=['GET'])
def tarot_daily():
    """
    每日一牌
    
    GET /api/tarot/daily
    
    Returns:
        今日指引（單張牌 + 簡短解讀）
    """
    try:
        # 抽一張牌
        reading = tarot_calc.draw_cards(
            spread_type='single',
            question='今日指引',
            allow_reversed=True
        )
        
        # 生成解讀（預設快速模式）
        fast_mode = request.args.get('fast_mode', 'true').lower() != 'false'
        if fast_mode:
            analysis = build_tarot_fallback(reading, 'general')
        else:
            prompts = generate_tarot_prompt(reading, 'general')
            system_instruction = prompts['system_prompt'] + "\n\n輸出必須使用繁體中文（台灣用語）。請簡潔扼要，總字數控制在 300-400 字內。"
            full_prompt = f"{system_instruction}\n\n{prompts['user_prompt']}"
            analysis = sanitize_plain_text(call_gemini(full_prompt, max_output_tokens=800))
        
        # 取得牌卡資訊
        card = reading.cards[0]
        card_meaning = tarot_calc.get_card_meaning(card.id, card.is_reversed)
        
        return jsonify({
            'status': 'success',
            'data': {
                'card': {
                    'name': card.name,
                    'name_en': card.name_en,
                    'is_reversed': card.is_reversed,
                    'orientation': '逆位' if card.is_reversed else '正位',
                    'keywords': card_meaning.get('keywords', []),
                    'element': card_meaning.get('element'),
                    'arcana': card_meaning.get('arcana')
                },
                'interpretation': analysis,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'timestamp': reading.timestamp
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'每日一牌失敗：{str(e)}'
        }), 500


@app.route('/api/tarot/spreads', methods=['GET'])
def tarot_spreads():
    """
    取得支援的牌陣列表
    
    GET /api/tarot/spreads
    
    Returns:
        所有支援的牌陣資訊
    """
    try:
        spreads = tarot_calc.spreads
        spread_list = []
        for spread_type, spread_info in spreads.items():
            positions = spread_info.get('positions', [])
            spread_list.append({
                'type': spread_type,
                'name': spread_info.get('name', spread_type),
                'name_en': spread_info.get('name_en', ''),
                'cards': len(positions),
                'positions': positions,
                'description': spread_info.get('description', ''),
                'variations': spread_info.get('variations', [])
            })
        
        return jsonify({
            'status': 'success',
            'data': {
                'spreads': spread_list,
                'spreads_dict': spreads,
                'total': len(spread_list)
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'取得牌陣列表失敗：{str(e)}'
        }), 500


@app.route('/api/tarot/card/<int:card_id>', methods=['GET'])
def tarot_card_info(card_id: int):
    """
    取得單張牌的詳細資訊
    
    GET /api/tarot/card/<card_id>
    
    Returns:
        牌卡完整資訊（正位與逆位牌義）
    """
    try:
        if card_id < 0 or card_id > 77:
            return jsonify({
                'status': 'error',
                'message': '牌卡 ID 必須在 0-77 之間'
            }), 400
        
        upright = tarot_calc.get_card_meaning(card_id, is_reversed=False)
        reversed_meaning = tarot_calc.get_card_meaning(card_id, is_reversed=True)
        
        return jsonify({
            'status': 'success',
            'data': {
                'card_id': card_id,
                'name': upright.get('name'),
                'name_en': upright.get('name_en'),
                'number': upright.get('number'),
                'arcana': upright.get('arcana'),
                'suit': upright.get('suit'),
                'element': upright.get('element'),
                'keywords': upright.get('keywords'),
                'symbolism': upright.get('symbolism'),
                'archetype': upright.get('archetype'),
                'upright': upright.get('all_meanings'),
                'reversed': reversed_meaning.get('all_meanings')
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'取得牌卡資訊失敗：{str(e)}'
        }), 500


# ============================================
# 靈數學 API 端點
# ============================================

@app.route('/api/numerology/profile', methods=['POST'])
def numerology_profile():
    """
    計算完整靈數學檔案
    
    POST /api/numerology/profile
    {
        "birth_date": "1979-11-12",      # 必填：出生日期
        "full_name": "CHEN YU CHU",       # 選填：英文全名（用於計算天賦數等）
        "analysis_type": "full",          # 選填：分析類型 (life_path/full/personal_year/career)
        "context": "general"              # 選填：情境 (general/love/career/finance/health)
    }
    """
    try:
        data = request.json
        
        # 解析出生日期
        birth_date_str = data.get('birth_date')
        if not birth_date_str:
            return jsonify({
                'status': 'error',
                'message': '缺少必要參數：birth_date'
            }), 400
        
        from datetime import date
        birth_date = date.fromisoformat(birth_date_str)
        
        full_name = data.get('full_name', '')
        analysis_type = data.get('analysis_type', 'full')
        context = data.get('context', 'general')
        
        # 計算靈數檔案
        profile = numerology_calc.calculate_full_profile(birth_date, full_name)
        
        # 生成 Prompt
        prompts = generate_numerology_prompt(profile, numerology_calc, analysis_type, context)
        
        # 呼叫 Gemini
        full_prompt = f"{prompts['system_prompt']}\n\n{prompts['user_prompt']}"
        interpretation = call_gemini(full_prompt)
        
        # 組合結果
        result = numerology_calc.to_dict(profile)
        result['interpretation'] = interpretation
        result['analysis_type'] = analysis_type
        result['context'] = context
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': f'日期格式錯誤：{str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'靈數學分析失敗：{str(e)}'
        }), 500


@app.route('/api/numerology/life-path', methods=['POST'])
def numerology_life_path():
    """
    計算生命靈數（快速版）
    
    POST /api/numerology/life-path
    {
        "birth_date": "1979-11-12"
    }
    """
    try:
        data = request.json
        
        birth_date_str = data.get('birth_date')
        if not birth_date_str:
            return jsonify({
                'status': 'error',
                'message': '缺少必要參數：birth_date'
            }), 400
        
        from datetime import date
        birth_date = date.fromisoformat(birth_date_str)
        
        # 計算生命靈數
        life_path, is_master, details = numerology_calc.calculate_life_path(birth_date)
        meaning = numerology_calc.get_number_meaning(life_path, 'life_path')
        
        return jsonify({
            'status': 'success',
            'data': {
                'life_path': life_path,
                'is_master_number': is_master,
                'name': meaning.get('name', ''),
                'name_en': meaning.get('name_en', ''),
                'keywords': meaning.get('keywords', []),
                'description': meaning.get('description', ''),
                'calculation_details': details
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'生命靈數計算失敗：{str(e)}'
        }), 500


@app.route('/api/numerology/personal-year', methods=['POST'])
def numerology_personal_year():
    """
    計算流年運勢
    
    POST /api/numerology/personal-year
    {
        "birth_date": "1979-11-12",
        "year": 2026  # 選填，預設為當前年份
    }
    """
    try:
        data = request.json
        
        birth_date_str = data.get('birth_date')
        if not birth_date_str:
            return jsonify({
                'status': 'error',
                'message': '缺少必要參數：birth_date'
            }), 400
        
        from datetime import date, datetime
        birth_date = date.fromisoformat(birth_date_str)
        target_year = data.get('year', datetime.now().year)
        
        # 計算流年
        personal_year, is_master, details = numerology_calc.calculate_personal_year(birth_date, target_year)
        meaning = numerology_calc.get_number_meaning(personal_year, 'personal_year')
        
        # 計算流月和流日
        personal_month, _, _ = numerology_calc.calculate_personal_month(birth_date, target_year, datetime.now().month)
        personal_day, _, _ = numerology_calc.calculate_personal_day(birth_date)
        
        return jsonify({
            'status': 'success',
            'data': {
                'year': target_year,
                'personal_year': personal_year,
                'is_master_number': is_master,
                'theme': meaning.get('theme', ''),
                'keywords': meaning.get('keywords', []),
                'description': meaning.get('description', ''),
                'advice': meaning.get('advice', ''),
                'personal_month': personal_month,
                'personal_day': personal_day,
                'calculation_details': details
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'流年計算失敗：{str(e)}'
        }), 500


@app.route('/api/numerology/compatibility', methods=['POST'])
def numerology_compatibility():
    """
    靈數相容性分析
    
    POST /api/numerology/compatibility
    {
        "person1": {
            "birth_date": "1979-11-12",
            "full_name": "CHEN YU CHU"
        },
        "person2": {
            "birth_date": "1985-05-20",
            "full_name": "WANG XIAO MING"
        }
    }
    """
    try:
        data = request.json
        
        person1_data = data.get('person1', {})
        person2_data = data.get('person2', {})
        
        if not person1_data.get('birth_date') or not person2_data.get('birth_date'):
            return jsonify({
                'status': 'error',
                'message': '缺少必要參數：兩人的 birth_date'
            }), 400
        
        from datetime import date
        birth_date1 = date.fromisoformat(person1_data['birth_date'])
        birth_date2 = date.fromisoformat(person2_data['birth_date'])
        
        full_name1 = person1_data.get('full_name', '')
        full_name2 = person2_data.get('full_name', '')
        
        # 計算兩人的靈數檔案
        profile1 = numerology_calc.calculate_full_profile(birth_date1, full_name1)
        profile2 = numerology_calc.calculate_full_profile(birth_date2, full_name2)
        
        # 生成相容性分析 Prompt
        prompts = generate_numerology_prompt(
            profile1, numerology_calc, 
            analysis_type='compatibility',
            profile2=profile2
        )
        
        # 呼叫 Gemini
        full_prompt = f"{prompts['system_prompt']}\n\n{prompts['user_prompt']}"
        interpretation = call_gemini(full_prompt)
        
        # 基本相容性評估
        compatibility = numerology_calc.calculate_compatibility(
            profile1.life_path, profile2.life_path
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'person1': {
                    'birth_date': birth_date1.isoformat(),
                    'life_path': profile1.life_path,
                    'expression': profile1.expression,
                    'soul_urge': profile1.soul_urge
                },
                'person2': {
                    'birth_date': birth_date2.isoformat(),
                    'life_path': profile2.life_path,
                    'expression': profile2.expression,
                    'soul_urge': profile2.soul_urge
                },
                'compatibility': compatibility,
                'interpretation': interpretation
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'相容性分析失敗：{str(e)}'
        }), 500


@app.route('/api/numerology/numbers', methods=['GET'])
def numerology_numbers():
    """
    取得所有數字的含義
    
    GET /api/numerology/numbers?type=life_path
    
    Query params:
        type: life_path (default), personal_year, birthday
    """
    try:
        number_type = request.args.get('type', 'life_path')
        
        if number_type == 'life_path':
            numbers = numerology_calc.data['life_path_numbers']['numbers']
        elif number_type == 'personal_year':
            numbers = numerology_calc.data['personal_year']['numbers']
        elif number_type == 'birthday':
            numbers = numerology_calc.data['birthday_number']['numbers']
        else:
            numbers = numerology_calc.data['life_path_numbers']['numbers']
        
        return jsonify({
            'status': 'success',
            'data': {
                'type': number_type,
                'numbers': numbers
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'取得數字含義失敗：{str(e)}'
        }), 500


# ============================================
# 姓名學 API 端點
# ============================================

@app.route('/api/name/analyze', methods=['POST'])
def name_analyze():
    """
    姓名分析 - 五格剖象法完整分析
    
    Request Body:
    {
        "name": "王小明",
        "analysis_type": "basic",  // basic, career, relationship
        "bazi_element": "木",  // 可選，八字喜用神
        "include_ai": true  // 是否包含 AI 解讀
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        name = data.get('name', '').strip()
        analysis_type = data.get('analysis_type', 'basic')
        bazi_element = data.get('bazi_element')
        include_ai = data.get('include_ai', True)
        
        if not name or len(name) < 2:
            return jsonify({
                'status': 'error',
                'message': '請提供有效的姓名（至少兩個字）'
            }), 400
        
        # 計算姓名分析
        analysis = name_calc.analyze(name, bazi_element)
        result = name_calc.to_dict(analysis)
        
        # AI 解讀
        if include_ai:
            prompts = generate_name_prompt(analysis, analysis_type, bazi_element)
            full_prompt = f"{prompts['system_prompt']}\n\n{prompts['user_prompt']}"
            result['ai_interpretation'] = call_gemini(full_prompt)
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'姓名分析失敗：{str(e)}'
        }), 500


@app.route('/api/name/five-grids', methods=['POST'])
def name_five_grids():
    """
    五格數理計算 - 快速計算五格
    
    Request Body:
    {
        "name": "王小明"
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        name = data.get('name', '').strip()
        
        if not name or len(name) < 2:
            return jsonify({
                'status': 'error',
                'message': '請提供有效的姓名'
            }), 400
        
        # 計算
        analysis = name_calc.analyze(name)
        
        return jsonify({
            'status': 'success',
            'data': {
                'name': name,
                'surname': analysis.surname,
                'given_name': analysis.given_name,
                'surname_strokes': analysis.surname_strokes,
                'given_name_strokes': analysis.given_name_strokes,
                'total_strokes': analysis.total_strokes,
                'five_grids': {
                    '天格': analysis.five_grids.天格,
                    '人格': analysis.five_grids.人格,
                    '地格': analysis.five_grids.地格,
                    '外格': analysis.five_grids.外格,
                    '總格': analysis.five_grids.總格
                },
                'grid_fortunes': {
                    name: grid.fortune
                    for name, grid in analysis.grid_analyses.items()
                },
                'three_talents': analysis.three_talents,
                'overall_fortune': analysis.overall_fortune
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'五格計算失敗：{str(e)}'
        }), 500


@app.route('/api/name/suggest', methods=['POST'])
def name_suggest():
    """
    命名建議 - 根據姓氏與條件建議名字
    
    Request Body:
    {
        "surname": "陳",
        "gender": "男",  // 男, 女, 中性
        "bazi_element": "木",  // 可選
        "desired_traits": ["聰明", "穩重"]  // 可選
    }
    """
    try:
        data = request.get_json()
        surname = data.get('surname', '').strip()
        gender = data.get('gender', '中性')
        bazi_element = data.get('bazi_element')
        desired_traits = data.get('desired_traits', [])
        
        if not surname:
            return jsonify({
                'status': 'error',
                'message': '請提供姓氏'
            }), 400
        
        # 計算姓氏筆畫
        surname_strokes = sum(name_calc.get_stroke_count(c) for c in surname)
        
        # 生成 Prompt
        prompts = generate_name_suggestion_prompt(
            surname, surname_strokes, gender, bazi_element, desired_traits
        )
        
        # AI 生成建議
        full_prompt = f"{prompts['system_prompt']}\n\n{prompts['user_prompt']}"
        suggestions = call_gemini(full_prompt)
        
        return jsonify({
            'status': 'success',
            'data': {
                'surname': surname,
                'surname_strokes': surname_strokes,
                'gender': gender,
                'bazi_element': bazi_element,
                'desired_traits': desired_traits,
                'suggestions': suggestions
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'命名建議失敗：{str(e)}'
        }), 500


@app.route('/api/name/number/<int:number>', methods=['GET'])
def name_number_meaning(number):
    """
    81 數理吉凶查詢
    
    GET /api/name/number/21
    """
    try:
        # 81 數理循環
        effective_number = ((number - 1) % 81) + 1
        
        meaning = name_calc.eighty_one.get(str(effective_number))
        
        if not meaning:
            return jsonify({
                'status': 'error',
                'message': f'找不到數字 {number} 的含義'
            }), 404
        
        # 計算五行
        element = name_calc.get_element(number)
        
        return jsonify({
            'status': 'success',
            'data': {
                'number': number,
                'effective_number': effective_number,
                'element': element,
                **meaning
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'查詢失敗：{str(e)}'
        }), 500


@app.route('/api/name/stroke/<char>', methods=['GET'])
def name_stroke_count(char):
    """
    查詢單字康熙筆畫
    
    GET /api/name/stroke/陳
    """
    try:
        if len(char) != 1:
            return jsonify({
                'status': 'error',
                'message': '請提供單一漢字'
            }), 400
        
        strokes = name_calc.get_stroke_count(char)
        
        return jsonify({
            'status': 'success',
            'data': {
                'character': char,
                'strokes': strokes,
                'element': name_calc.get_element(strokes)
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'查詢失敗：{str(e)}'
        }), 500


# ============================================
# 整合分析 API 端點（靈數學 + 姓名學）
# ============================================

@app.route('/api/integrated/profile', methods=['POST'])
def integrated_profile():
    """
    完整命理檔案 - 靈數學 + 姓名學整合分析
    
    Request Body:
    {
        "birth_date": "1979-11-12",    # 必填：出生日期
        "chinese_name": "陳宥竹",       # 必填：中文姓名
        "english_name": "CHEN YU CHU", # 選填：英文姓名（用於靈數天賦數等）
        "analysis_focus": "general",    # 選填：分析焦點 (general/career/love/wealth/health)
        "include_bazi": false,          # 選填：是否包含八字
        "bazi_data": {}                 # 選填：八字資料
    }
    """
    try:
        data = request.get_json()
        
        birth_date_str = data.get('birth_date')
        chinese_name = data.get('chinese_name', '').strip()
        english_name = data.get('english_name', '').strip()
        analysis_focus = data.get('analysis_focus', 'general')
        include_bazi = data.get('include_bazi', False)
        bazi_data = data.get('bazi_data')
        gender = data.get('gender', '未指定')
        
        if not birth_date_str:
            return jsonify({
                'status': 'error',
                'message': '缺少必要參數：birth_date'
            }), 400
        
        if not chinese_name or len(chinese_name) < 2:
            return jsonify({
                'status': 'error',
                'message': '請提供有效的中文姓名（至少兩個字）'
            }), 400
        
        from datetime import date
        birth_date = date.fromisoformat(birth_date_str)
        
        # 計算靈數學檔案
        numerology_profile = numerology_calc.calculate_full_profile(birth_date, english_name)
        
        # 計算姓名學分析
        name_analysis = name_calc.analyze(chinese_name)
        
        # 生成整合分析 Prompt
        prompts = generate_integrated_prompt(
            numerology_profile=numerology_profile,
            name_analysis=name_analysis,
            calc_numerology=numerology_calc,
            include_bazi=include_bazi,
            bazi_data=bazi_data,
            analysis_focus=analysis_focus,
            gender=gender
        )
        
        # 呼叫 Gemini 進行深度分析
        full_prompt = f"{prompts['system_prompt']}\n\n{prompts['user_prompt']}"
        interpretation = call_gemini(full_prompt)
        
        # 組合結果
        result = {
            "profile_type": "integrated",
            "analysis_focus": analysis_focus,
            "birth_date": birth_date_str,
            "names": {
                "chinese": chinese_name,
                "english": english_name if english_name else None
            },
            "numerology": numerology_calc.to_dict(numerology_profile),
            "name_analysis": name_calc.to_dict(name_analysis),
            "integrated_interpretation": interpretation
        }
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': f'參數錯誤：{str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'整合分析失敗：{str(e)}'
        }), 500


@app.route('/api/integrated/quick', methods=['POST'])
def integrated_quick():
    """
    快速命理概覽 - 精簡版整合分析
    
    Request Body:
    {
        "birth_date": "1979-11-12",
        "chinese_name": "陳宥竹",
        "english_name": "CHEN YU CHU"  # 選填
    }
    """
    try:
        data = request.get_json()
        
        birth_date_str = data.get('birth_date')
        chinese_name = data.get('chinese_name', '').strip()
        english_name = data.get('english_name', '').strip()
        
        if not birth_date_str or not chinese_name:
            return jsonify({
                'status': 'error',
                'message': '缺少必要參數：birth_date 和 chinese_name'
            }), 400
        
        from datetime import date
        birth_date = date.fromisoformat(birth_date_str)
        
        # 快速計算
        life_path, is_master, _ = numerology_calc.calculate_life_path(birth_date)
        personal_year, _, _ = numerology_calc.calculate_personal_year(birth_date)
        
        name_analysis = name_calc.analyze(chinese_name)
        
        lp_meaning = numerology_calc.get_number_meaning(life_path, 'life_path')
        py_meaning = numerology_calc.get_number_meaning(personal_year, 'personal_year')
        
        return jsonify({
            'status': 'success',
            'data': {
                "profile_type": "quick",
                "birth_date": birth_date_str,
                "chinese_name": chinese_name,
                "numerology_summary": {
                    "life_path": life_path,
                    "is_master": is_master,
                    "life_path_name": lp_meaning.get('name', ''),
                    "life_path_keywords": lp_meaning.get('keywords', [])[:5],
                    "personal_year": personal_year,
                    "personal_year_theme": py_meaning.get('theme', '')
                },
                "name_summary": {
                    "five_grids": {
                        "天格": name_analysis.five_grids.天格,
                        "人格": name_analysis.five_grids.人格,
                        "地格": name_analysis.five_grids.地格,
                        "外格": name_analysis.five_grids.外格,
                        "總格": name_analysis.five_grids.總格
                    },
                    "three_talents": name_analysis.three_talents['combination'],
                    "three_talents_fortune": name_analysis.three_talents['fortune'],
                    "overall_fortune": name_analysis.overall_fortune,
                    "personality_number": name_analysis.grid_analyses['人格'].number,
                    "personality_fortune": name_analysis.grid_analyses['人格'].fortune
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'快速分析失敗：{str(e)}'
        }), 500


@app.route('/api/integrated/compatibility', methods=['POST'])
def integrated_compatibility():
    """
    雙人整合相容性分析 - 靈數學 + 姓名學
    
    Request Body:
    {
        "person1": {
            "birth_date": "1979-11-12",
            "chinese_name": "陳宥竹",
            "english_name": "CHEN YU CHU"
        },
        "person2": {
            "birth_date": "1985-05-20",
            "chinese_name": "王小美",
            "english_name": "WANG XIAO MEI"
        }
    }
    """
    try:
        data = request.get_json()
        
        person1 = data.get('person1', {})
        person2 = data.get('person2', {})
        
        if not person1.get('birth_date') or not person1.get('chinese_name'):
            return jsonify({
                'status': 'error',
                'message': '請提供甲方的 birth_date 和 chinese_name'
            }), 400
        
        if not person2.get('birth_date') or not person2.get('chinese_name'):
            return jsonify({
                'status': 'error',
                'message': '請提供乙方的 birth_date 和 chinese_name'
            }), 400
        
        from datetime import date
        
        # 計算甲方
        bd1 = date.fromisoformat(person1['birth_date'])
        profile1 = numerology_calc.calculate_full_profile(bd1, person1.get('english_name', ''))
        name1 = name_calc.analyze(person1['chinese_name'])
        
        # 計算乙方
        bd2 = date.fromisoformat(person2['birth_date'])
        profile2 = numerology_calc.calculate_full_profile(bd2, person2.get('english_name', ''))
        name2 = name_calc.analyze(person2['chinese_name'])
        
        # 準備比對資料
        person1_data = {
            'name': person1['chinese_name'],
            'birth_date': person1['birth_date'],
            'life_path': profile1.life_path,
            'personality_grid': name1.grid_analyses['人格'].number,
            'personality_element': name1.grid_analyses['人格'].element,
            'three_talents': name1.three_talents['combination']
        }
        
        person2_data = {
            'name': person2['chinese_name'],
            'birth_date': person2['birth_date'],
            'life_path': profile2.life_path,
            'personality_grid': name2.grid_analyses['人格'].number,
            'personality_element': name2.grid_analyses['人格'].element,
            'three_talents': name2.three_talents['combination']
        }
        
        # 生成比對分析 Prompt
        prompts = generate_comparison_prompt(person1_data, person2_data)
        
        # 呼叫 Gemini
        full_prompt = f"{prompts['system_prompt']}\n\n{prompts['user_prompt']}"
        interpretation = call_gemini(full_prompt)
        
        # 靈數相容性
        numerology_compat = numerology_calc.calculate_compatibility(
            profile1.life_path, profile2.life_path
        )
        
        # 姓名五行相容性
        e1 = name1.grid_analyses['人格'].element
        e2 = name2.grid_analyses['人格'].element
        name_compat = _analyze_element_compatibility(e1, e2)
        
        return jsonify({
            'status': 'success',
            'data': {
                'person1': {
                    **person1_data,
                    'expression': profile1.expression,
                    'soul_urge': profile1.soul_urge,
                    'overall_fortune': name1.overall_fortune
                },
                'person2': {
                    **person2_data,
                    'expression': profile2.expression,
                    'soul_urge': profile2.soul_urge,
                    'overall_fortune': name2.overall_fortune
                },
                'compatibility': {
                    'numerology': numerology_compat,
                    'name_elements': name_compat
                },
                'interpretation': interpretation
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'相容性分析失敗：{str(e)}'
        }), 500


@app.route('/api/integrated/yearly-forecast', methods=['POST'])
def integrated_yearly_forecast():
    """
    年度運勢預測 - 整合靈數流年與姓名運勢
    
    Request Body:
    {
        "birth_date": "1979-11-12",
        "chinese_name": "陳宥竹",
        "year": 2026  # 選填，預設當前年
    }
    """
    try:
        data = request.get_json()
        
        birth_date_str = data.get('birth_date')
        chinese_name = data.get('chinese_name', '').strip()
        
        if not birth_date_str or not chinese_name:
            return jsonify({
                'status': 'error',
                'message': '缺少必要參數'
            }), 400
        
        from datetime import date, datetime
        birth_date = date.fromisoformat(birth_date_str)
        target_year = data.get('year', datetime.now().year)
        
        # 計算靈數
        personal_year, is_master, _ = numerology_calc.calculate_personal_year(birth_date, target_year)
        py_meaning = numerology_calc.get_number_meaning(personal_year, 'personal_year')
        
        # 計算各月流月
        monthly_forecast = []
        for month in range(1, 13):
            pm, _, _ = numerology_calc.calculate_personal_month(birth_date, target_year, month)
            pm_meaning = numerology_calc.get_number_meaning(pm, 'personal_year')
            monthly_forecast.append({
                'month': month,
                'personal_month': pm,
                'theme': pm_meaning.get('theme', ''),
                'keywords': pm_meaning.get('keywords', [])[:3]
            })
        
        # 姓名分析
        name_analysis = name_calc.analyze(chinese_name)
        
        # 生成年度預測 Prompt
        prompt = f"""請為以下命主提供【{target_year}年度完整運勢預測】：

【基本資料】
姓名：{chinese_name}
出生日期：{birth_date_str}
{target_year}年流年數：{personal_year}{"（主數）" if is_master else ""}
流年主題：{py_meaning.get('theme', '')}

【姓名格局】
人格數：{name_analysis.grid_analyses['人格'].number}（{name_analysis.grid_analyses['人格'].element}）- {name_analysis.grid_analyses['人格'].fortune}
三才配置：{name_analysis.three_talents['combination']}（{name_analysis.three_talents['fortune']}）

【各月流月數】
""" + '\n'.join([f"{m['month']}月：{m['personal_month']}（{m['theme']}）" for m in monthly_forecast]) + """

請提供：

1. **年度總運勢**（300字）
   結合流年數與姓名格局的整體能量

2. **各領域運勢**（各100字）
   - 事業運
   - 感情運
   - 財運
   - 健康運

3. **重要月份提醒**
   標出需特別注意的月份及原因

4. **年度開運建議**
   5 條具體的開運指南

請用繁體中文回答。"""

        interpretation = call_gemini(prompt)
        
        return jsonify({
            'status': 'success',
            'data': {
                'year': target_year,
                'birth_date': birth_date_str,
                'chinese_name': chinese_name,
                'personal_year': {
                    'number': personal_year,
                    'is_master': is_master,
                    'theme': py_meaning.get('theme', ''),
                    'description': py_meaning.get('description', ''),
                    'advice': py_meaning.get('advice', '')
                },
                'monthly_forecast': monthly_forecast,
                'name_influence': {
                    'personality_grid': name_analysis.grid_analyses['人格'].number,
                    'personality_fortune': name_analysis.grid_analyses['人格'].fortune,
                    'three_talents': name_analysis.three_talents['combination']
                },
                'interpretation': interpretation
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'年度預測失敗：{str(e)}'
        }), 500


# ============================================
# 戰略側寫與生辰校正 API 端點
# ============================================

@app.route('/api/strategic/profile', methods=['POST'])
def strategic_profile():
    """
    戰略側寫 - 多系統整合分析（結論優先）

    Request Body:
    {
        "birth_date": "1979-11-12",
        "birth_time": "23:58",              # 選填
        "chinese_name": "陳宥竹",
        "english_name": "CHEN YOU ZHU",     # 選填
        "gender": "男",
        "analysis_focus": "career",         # general/career/relationship/wealth/health
        "include_bazi": true,
        "include_astrology": true,
        "include_tarot": true,
        "longitude": 120.54,
        "latitude": 24.08,
        "timezone": "Asia/Taipei",
        "city": "Changhua",
        "nation": "TW"
    }
    """
    try:
        data = request.get_json()

        birth_date_str = data.get('birth_date')
        birth_time_str = data.get('birth_time')
        chinese_name = data.get('chinese_name', '').strip()
        english_name = data.get('english_name', '').strip()
        gender = data.get('gender', '未指定')
        analysis_focus = data.get('analysis_focus', 'general')

        if not birth_date_str:
            return jsonify({
                'status': 'error',
                'message': '缺少必要參數：birth_date'
            }), 400

        if not chinese_name:
            return jsonify({
                'status': 'error',
                'message': '缺少必要參數：chinese_name'
            }), 400

        from datetime import date
        birth_date = date.fromisoformat(birth_date_str)
        parsed_time = parse_birth_time_str(birth_time_str)

        include_bazi = data.get('include_bazi', True)
        include_astrology = data.get('include_astrology', True)

        warnings = []
        include_tarot = data.get('include_tarot', True)

        warnings = []

        # 1) 靈數與姓名（固定）
        numerology_profile = numerology_calc.calculate_full_profile(birth_date, english_name)
        numerology_dict = numerology_calc.to_dict(numerology_profile)
        name_analysis = name_calc.analyze(chinese_name)
        name_dict = name_calc.to_dict(name_analysis)

        # 2) 八字
        bazi_data = None
        if include_bazi:
            if not parsed_time:
                warnings.append('未提供 birth_time，已略過八字計算')
            else:
                hour, minute = parsed_time
                bazi_calc = BaziCalculator()
                bazi_data = bazi_calc.calculate_bazi(
                    year=birth_date.year,
                    month=birth_date.month,
                    day=birth_date.day,
                    hour=hour,
                    minute=minute,
                    gender=gender,
                    longitude=float(data.get('longitude', 121.0)),
                    use_apparent_solar_time=True
                )

        # 3) 占星
        astrology_core = None
        if include_astrology:
            if not parsed_time:
                warnings.append('未提供 birth_time，已略過占星計算')
            else:
                hour, minute = parsed_time
                natal = astrology_calc.calculate_natal_chart(
                    name=chinese_name or "User",
                    year=birth_date.year,
                    month=birth_date.month,
                    day=birth_date.day,
                    hour=hour,
                    minute=minute,
                    city=data.get('city', 'Taipei'),
                    nation=data.get('nation', 'TW'),
                    longitude=float(data.get('longitude', 121.0)),
                    latitude=float(data.get('latitude', 25.0)),
                    timezone_str=data.get('timezone', 'Asia/Taipei')
                )
                astrology_core = build_astrology_core(natal)

        # 4) 塔羅
        tarot_text = None
        if include_tarot:
            seed = int(f"{birth_date.year}{birth_date.month:02d}{birth_date.day:02d}")
            tarot_reading = tarot_calc.draw_cards(
                spread_type="three_card",
                question=f"{chinese_name}的{analysis_focus}戰略定位",
                allow_reversed=True,
                seed=seed
            )
            tarot_text = tarot_calc.format_reading_for_prompt(tarot_reading, context=analysis_focus)

        # 5) Meta Profile
        meta_profile = build_meta_profile(bazi_data, numerology_dict, name_dict, astrology_core)

        # 6) 生成戰略側寫
        prompt = generate_strategic_profile_prompt(
            meta_profile=meta_profile,
            numerology=numerology_dict,
            name_analysis=name_dict,
            bazi=bazi_data,
            astrology_core=astrology_core,
            tarot_reading=tarot_text,
            analysis_focus=analysis_focus
        )
        full_prompt = f"{prompt['system_prompt']}\n\n{prompt['user_prompt']}"
        strategic_interpretation = call_gemini(full_prompt)

        return jsonify({
            'status': 'success',
            'data': {
                'meta_profile': meta_profile,
                'analysis_focus': analysis_focus,
                'numerology': numerology_dict,
                'name_analysis': name_dict,
                'bazi': bazi_data,
                'astrology_core': astrology_core,
                'tarot': tarot_text,
                'strategic_interpretation': strategic_interpretation,
                'warnings': warnings
            }
        })

    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': f'參數錯誤：{str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'戰略側寫失敗：{str(e)}'
        }), 500


@app.route('/api/strategic/birth-rectify', methods=['POST'])
def strategic_birth_rectify():
    """
    生辰校正 - 以特質/事件反推時辰（Top 3）

    Request Body:
    {
        "birth_date": "1979-11-12",
        "gender": "男",
        "traits": ["強勢領導", "偏好獨立作業"],
        "longitude": 120.54
    }
    """
    try:
        data = request.get_json()

        birth_date_str = data.get('birth_date')
        gender = data.get('gender', '未指定')
        traits = data.get('traits', [])

        if not birth_date_str:
            return jsonify({
                'status': 'error',
                'message': '缺少必要參數：birth_date'
            }), 400

        if not traits:
            return jsonify({
                'status': 'error',
                'message': '缺少必要參數：traits（請提供特質/事件清單）'
            }), 400

        from datetime import date
        birth_date = date.fromisoformat(birth_date_str)

        shichen = [
            ("子時", 23, 30), ("丑時", 1, 30), ("寅時", 3, 30), ("卯時", 5, 30),
            ("辰時", 7, 30), ("巳時", 9, 30), ("午時", 11, 30), ("未時", 13, 30),
            ("申時", 15, 30), ("酉時", 17, 30), ("戌時", 19, 30), ("亥時", 21, 30)
        ]

        bazi_calc = BaziCalculator()
        candidates = []
        for name, hour, minute in shichen:
            bazi = bazi_calc.calculate_bazi(
                year=birth_date.year,
                month=birth_date.month,
                day=birth_date.day,
                hour=hour,
                minute=minute,
                gender=gender,
                longitude=float(data.get('longitude', 121.0)),
                use_apparent_solar_time=True
            )
            candidates.append({
                "shichen": name,
                "time": f"{hour:02d}:{minute:02d}",
                "bazi_summary": build_bazi_candidate_summary(bazi)
            })

        prompt = generate_birth_rectifier_prompt(
            birth_date=birth_date_str,
            gender=gender,
            traits=traits,
            candidates=candidates
        )
        full_prompt = f"{prompt['system_prompt']}\n\n{prompt['user_prompt']}"
        interpretation = call_gemini(full_prompt)

        return jsonify({
            'status': 'success',
            'data': {
                'birth_date': birth_date_str,
                'traits': traits,
                'candidates': candidates,
                'interpretation': interpretation
            }
        })

    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': f'參數錯誤：{str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'生辰校正失敗：{str(e)}'
        }), 500


@app.route('/api/strategic/relationship', methods=['POST'])
def strategic_relationship():
    """
    關係生態位分析 - 資源流向與角色定義

    Request Body:
    {
        "person_a": { "name": "陳宥竹", "birth_date": "1979-11-12", "birth_time": "23:58" },
        "person_b": { "name": "張小姐", "birth_date": "1985-05-20", "birth_time": "12:00" },
        "include_bazi": true,
        "include_astrology": true
    }
    """
    try:
        data = request.get_json()
        person_a = data.get('person_a', {})
        person_b = data.get('person_b', {})

        if not person_a.get('birth_date') or not person_b.get('birth_date'):
            return jsonify({'status': 'error', 'message': '雙方皆需提供出生日期'}), 400

        include_bazi = data.get('include_bazi', True)
        include_astrology = data.get('include_astrology', True)

        def get_meta(p):
            from datetime import date
            bd = date.fromisoformat(p['birth_date'])
            pt = parse_birth_time_str(p.get('birth_time'))
            
            # 1. Numerology & Name
            num_prof = numerology_calc.calculate_full_profile(bd, "")
            num_dict = numerology_calc.to_dict(num_prof)
            name_an = name_calc.analyze(p.get('name', 'User'))
            name_dict = name_calc.to_dict(name_an)

            # 2. Bazi
            bazi_data = None
            if include_bazi and pt:
                bazi_data = BaziCalculator().calculate_bazi(
                    year=bd.year, month=bd.month, day=bd.day, 
                    hour=pt[0], minute=pt[1], gender=p.get('gender', '未指定'),
                    use_apparent_solar_time=True
                )
            
            if include_bazi and not pt:
                warnings.append('未提供 birth_time，已略過八字計算')

            # 3. Astro
            astro_core = None
            if include_astrology and pt:
                natal = AstrologyCalculator().calculate_natal_chart(
                    name=p.get('name', 'User'),
                    year=bd.year, month=bd.month, day=bd.day,
                    hour=pt[0], minute=pt[1],
                    city="Taipei", nation="TW"
                )
                astro_core = build_astrology_core(natal)

            if include_astrology and not pt:
                warnings.append('未提供 birth_time，已略過占星計算')
            
            return build_meta_profile(bazi_data, num_dict, name_dict, astro_core)

        meta_a = get_meta(person_a)
        meta_b = get_meta(person_b)

        prompt = generate_relationship_ecosystem_prompt(
            person_a=person_a,
            person_b=person_b,
            meta_a=meta_a,
            meta_b=meta_b
        )
        full_prompt = f"{prompt['system_prompt']}\n\n{prompt['user_prompt']}"
        interpretation = call_gemini(full_prompt)

        return jsonify({
            'status': 'success',
            'data': {
                'person_a_meta': meta_a,
                'person_b_meta': meta_b,
                'interpretation': interpretation,
                'warnings': warnings
            }
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'關係分析失敗：{str(e)}'}), 500


@app.route('/api/strategic/decision', methods=['POST'])
def strategic_decision():
    """
    決策模擬沙盒 - 雙路徑模擬

    Request Body:
    {
        "user_name": "陳宥竹",
        "birth_date": "1979-11-12",
        "question": "公司轉型方向",
        "option_a": "激進擴張",
        "option_b": "穩健保守"
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        user_name = data.get('user_name', 'User')
        birth_date_str = data.get('birth_date')
        birth_time_str = data.get('birth_time')
        question = data.get('question')
        option_a = data.get('option_a')
        option_b = data.get('option_b')

        if not all([birth_date_str, question, option_a, option_b]):
            return jsonify({'status': 'error', 'message': '缺少必要參數'}), 400

        # Get User Meta
        from datetime import date
        bd = date.fromisoformat(birth_date_str)
        parsed_time = parse_birth_time_str(birth_time_str)

        warnings = []

        num_prof = numerology_calc.calculate_full_profile(bd, "")
        name_analysis = name_calc.analyze(user_name)
        name_dict = name_calc.to_dict(name_analysis)

        bazi_data = None
        astro_core = None
        if parsed_time:
            hour, minute = parsed_time
            bazi_data = BaziCalculator().calculate_bazi(
                year=bd.year,
                month=bd.month,
                day=bd.day,
                hour=hour,
                minute=minute,
                gender=data.get('gender', '未指定'),
                longitude=float(data.get('longitude', 121.0)),
                use_apparent_solar_time=True
            )
            natal = astrology_calc.calculate_natal_chart(
                name=user_name or "User",
                year=bd.year,
                month=bd.month,
                day=bd.day,
                hour=hour,
                minute=minute,
                city=data.get('city', 'Taipei'),
                nation=data.get('nation', 'TW'),
                longitude=float(data.get('longitude', 121.0)),
                latitude=float(data.get('latitude', 25.0)),
                timezone_str=data.get('timezone', 'Asia/Taipei')
            )
            astro_core = build_astrology_core(natal)
        else:
            warnings.append('未提供 birth_time，已略過八字與占星計算')

        meta_profile = build_meta_profile(bazi_data, numerology_calc.to_dict(num_prof), name_dict, astro_core)

        # Draw Tarot for Path A
        reading_a = tarot_calc.draw_cards(spread_type="three_card", question=f"路徑A：{option_a}", allow_reversed=True)
        text_a = tarot_calc.format_reading_for_prompt(reading_a)

        # Draw Tarot for Path B
        reading_b = tarot_calc.draw_cards(spread_type="three_card", question=f"路徑B：{option_b}", allow_reversed=True)
        text_b = tarot_calc.format_reading_for_prompt(reading_b)

        prompt = generate_decision_sandbox_prompt(
            user_name=user_name,
            question=question,
            option_a=option_a,
            option_b=option_b,
            cards_a=text_a,
            cards_b=text_b,
            meta_profile=meta_profile
        )
        full_prompt = f"{prompt['system_prompt']}\n\n{prompt['user_prompt']}"
        interpretation = call_gemini(full_prompt)

        return jsonify({
            'status': 'success',
            'data': {
                'option_a': option_a,
                'option_b': option_b,
                'cards_a': [c.name for c in reading_a.cards],
                'cards_b': [c.name for c in reading_b.cards],
                'interpretation': interpretation,
                'warnings': warnings
            }
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'決策模擬失敗：{str(e)}'}), 500


def _analyze_element_compatibility(element1: str, element2: str) -> Dict:
    """分析兩個五行的相容性"""
    relations = {
        ("木", "木"): ("比和", "相同能量，理解彼此"),
        ("木", "火"): ("相生", "木生火，互相扶持"),
        ("木", "土"): ("相剋", "木剋土，需要調和"),
        ("木", "金"): ("相剋", "金剋木，存在壓力"),
        ("木", "水"): ("相生", "水生木，獲得滋養"),
        ("火", "火"): ("比和", "熱情相投"),
        ("火", "土"): ("相生", "火生土，穩定發展"),
        ("火", "金"): ("相剋", "火剋金，需要包容"),
        ("火", "水"): ("相剋", "水剋火，存在挑戰"),
        ("土", "土"): ("比和", "穩重踏實"),
        ("土", "金"): ("相生", "土生金，互利共贏"),
        ("土", "水"): ("相剋", "土剋水，需要溝通"),
        ("金", "金"): ("比和", "目標一致"),
        ("金", "水"): ("相生", "金生水，相互成就"),
        ("水", "水"): ("比和", "心靈相通"),
    }
    
    key = (element1, element2)
    reverse_key = (element2, element1)
    
    if key in relations:
        relation, desc = relations[key]
    elif reverse_key in relations:
        relation, desc = relations[reverse_key]
    else:
        relation, desc = "未知", "需要更多分析"
    
    return {
        "element1": element1,
        "element2": element2,
        "relation": relation,
        "description": desc
    }


# ============================================
# 啟動服務
# ============================================

if __name__ == '__main__':
    print('='*60)
    print('Aetheria 定盤系統 API (v1.9.0)')
    print('='*60)
    print('服務位址：http://localhost:5001')
    print('健康檢查：http://localhost:5001/health')
    print('\n🆕 新增功能（v1.8.0）- 整合分析：')
    print('  • 完整命理檔案：POST /api/integrated/profile')
    print('  • 快速概覽：POST /api/integrated/quick')
    print('  • 雙人相容性：POST /api/integrated/compatibility')
    print('  • 年度運勢：POST /api/integrated/yearly-forecast')
    print('\n🆕 新增功能（v1.9.0）- 戰略側寫：')
    print('  • 全息側寫：POST /api/strategic/profile')
    print('  • 生辰校正：POST /api/strategic/birth-rectify')
    print('  • 關係生態：POST /api/strategic/relationship')
    print('  • 決策模擬：POST /api/strategic/decision')
    print('\n姓名學（v1.7.0）：')
    print('  • 姓名分析：POST /api/name/analyze')
    print('  • 五格計算：POST /api/name/five-grids')
    print('  • 命名建議：POST /api/name/suggest')
    print('  • 數理含義：GET /api/name/number/<num>')
    print('  • 筆畫查詢：GET /api/name/stroke/<char>')
    print('\n靈數學（v1.6.0）：')
    print('  • 靈數學檔案：POST /api/numerology/profile')
    print('  • 生命靈數：POST /api/numerology/life-path')
    print('  • 流年運勢：POST /api/numerology/personal-year')
    print('  • 靈數相容：POST /api/numerology/compatibility')
    print('  • 數字含義：GET /api/numerology/numbers')
    print('\n塔羅牌（v1.5.0）：')
    print('  • 塔羅牌解讀：POST /api/tarot/reading')
    print('  • 每日一牌：GET /api/tarot/daily')
    print('  • 牌陣列表：GET /api/tarot/spreads')
    print('  • 牌卡資訊：GET /api/tarot/card/<id>')
    print('\n西洋占星術（v1.4.0）：')
    print('  • 本命盤：POST /api/astrology/natal')
    print('  • 合盤：POST /api/astrology/synastry')
    print('  • 流年：POST /api/astrology/transit')
    print('  • 事業：POST /api/astrology/career')
    print('='*60)
    
    app.run(host='0.0.0.0', port=5001, debug=False)
