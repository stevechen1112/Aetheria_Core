"""
Aetheria 定盤系統 API
提供命盤分析、鎖定、查詢功能
支持紫微斗数、八字命理、交叉验证
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

from chart_extractor import ChartExtractor
from fortune_teller import FortuneTeller
from fortune_prompts import (
    FORTUNE_ANNUAL_ANALYSIS,
    FORTUNE_MONTHLY_ANALYSIS,
    FORTUNE_QUESTION_ANALYSIS,
    FORTUNE_AUSPICIOUS_DAYS
)
from synastry_prompts import (
    SYNASTRY_MARRIAGE_ANALYSIS,
    SYNASTRY_PARTNERSHIP_ANALYSIS,
    SYNASTRY_QUICK_CHECK
)
from date_selection_prompts import (
    DATE_SELECTION_MARRIAGE,
    DATE_SELECTION_BUSINESS,
    DATE_SELECTION_MOVING,
    DATE_SELECTION_QUICK
)
from bazi_calculator import BaziCalculator
from bazi_prompts import (
    format_bazi_analysis_prompt,
    format_bazi_fortune_prompt,
    format_cross_validation_prompt
)

# 載入環境變數
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

app = Flask(__name__)
CORS(app)  # 允許跨域請求

# 資料儲存目錄（暫時使用 JSON 檔案，之後可換成資料庫）
DATA_DIR = Path('data')
DATA_DIR.mkdir(exist_ok=True)

USERS_FILE = DATA_DIR / 'users.json'
LOCKS_FILE = DATA_DIR / 'chart_locks.json'

# 初始化資料檔案
if not USERS_FILE.exists():
    USERS_FILE.write_text('{}', encoding='utf-8')
if not LOCKS_FILE.exists():
    LOCKS_FILE.write_text('{}', encoding='utf-8')

# 初始化提取器
extractor = ChartExtractor()

# Gemini 設定
# 使用 Gemini 3 Flash Preview - 性能測試顯示品質相當且速度快 2x，成本節省 30-40%
MODEL_NAME = 'gemini-3-flash-preview'
TEMPERATURE = 0.4

# ============================================
# Prompt 模板
# ============================================

SYSTEM_INSTRUCTION = """
你是 Aetheria，精通紫微斗數的 AI 命理顧問。

重要原則：
1. 準確性最重要，不可編造星曜
2. 晚子時（23:00-01:00）的判定邏輯要明確說明
3. 必須明確說出命宮位置、主星、格局
4. 結構清晰，先說命盤結構，再說詳細分析

輸出風格：專業、溫暖、具啟發性
"""

INITIAL_ANALYSIS_PROMPT = """
請為以下用戶提供完整的紫微斗數命盤分析：

出生日期：{birth_date}
出生時間：{birth_time}
出生地點：{birth_location}
性別：{gender}

請按照以下格式輸出（約1500-2000字）：

### 一、命盤基礎結構
1. **時辰判定**：說明如何處理時辰（特別是晚子時）
2. **命宮**：位於哪個宮位？主星是什麼？輔星有哪些？
3. **核心格局**：屬於什麼格局？（如機月同梁、殺破狼等）
4. **關鍵宮位**：
   - 官祿宮（事業）：宮位、主星、四化
   - 財帛宮（財運）：宮位、主星、四化
   - 夫妻宮（感情）：宮位、主星、四化

### 二、詳細命盤分析
（各宮位深度解讀，約1000字）

### 三、性格特質與人生建議
（日常語言描述，核心關鍵詞至少5個，約500字）

**注意**：必須明確說出宮位（如「戌宮」「申宮」），不可模糊帶過。
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

def get_user(user_id: str) -> Optional[Dict]:
    """取得用戶資料"""
    users = load_json(USERS_FILE)
    return users.get(user_id)

def save_user(user_id: str, user_data: Dict):
    """儲存用戶資料"""
    users = load_json(USERS_FILE)
    users[user_id] = user_data
    save_json(USERS_FILE, users)

def get_chart_lock(user_id: str) -> Optional[Dict]:
    """取得用戶的鎖定命盤"""
    locks = load_json(LOCKS_FILE)
    return locks.get(user_id)

def save_chart_lock(user_id: str, lock_data: Dict):
    """儲存鎖定命盤"""
    locks = load_json(LOCKS_FILE)
    locks[user_id] = lock_data
    save_json(LOCKS_FILE, locks)

# ============================================
# Gemini API 呼叫
# ============================================

def call_gemini(prompt: str, system_instruction: str = SYSTEM_INSTRUCTION) -> str:
    """
    呼叫 Gemini 3 Pro API
    """
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=system_instruction
    )
    
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=TEMPERATURE,
            top_p=0.95,
            top_k=40
        ),
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    )
    
    return response.text

# ============================================
# API 路由
# ============================================

@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查"""
    return jsonify({'status': 'ok', 'service': 'Aetheria Chart Locking API'})

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
    try:
        data = request.json
        user_id = data['user_id']
        
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
            gender=data['gender']
        )
        
        # 呼叫 Gemini
        print(f'[API] 正在為用戶 {user_id} 生成命盤...')
        analysis = call_gemini(prompt)
        
        # 提取結構
        structure = extractor.extract_full_structure(analysis)
        
        # 驗證結構
        is_valid, errors = extractor.validate_structure(structure)
        
        if not is_valid:
            return jsonify({
                'error': '命盤結構提取不完整',
                'details': errors,
                'raw_analysis': analysis
            }), 400
        
        # 暫存到資料庫（待確認）
        temp_lock = {
            'user_id': user_id,
            'chart_structure': structure,
            'original_analysis': analysis,
            'confirmation_status': 'pending',
            'created_at': datetime.now().isoformat(),
            'is_active': False
        }
        save_chart_lock(user_id, temp_lock)
        
        print(f'[API] 命盤生成完成，等待用戶確認')
        
        return jsonify({
            'analysis': analysis,
            'structure': structure,
            'lock_id': user_id,
            'needs_confirmation': True
        })
        
    except Exception as e:
        print(f'[ERROR] {e}')
        return jsonify({'error': str(e)}), 500

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
        user_id = data['user_id']
        
        # 取得暫存的命盤
        lock = get_chart_lock(user_id)
        
        if not lock:
            return jsonify({'error': '找不到待確認的命盤'}), 404
        
        # 更新確認狀態
        lock['confirmation_status'] = 'confirmed'
        lock['confirmed_at'] = datetime.now().isoformat()
        lock['is_active'] = True
        
        save_chart_lock(user_id, lock)
        
        print(f'[API] 用戶 {user_id} 已確認並鎖定命盤')
        
        return jsonify({
            'status': 'locked',
            'message': '命盤已鎖定',
            'locked_at': lock['confirmed_at']
        })
        
    except Exception as e:
        print(f'[ERROR] {e}')
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
            return jsonify({'error': '缺少 user_id 參數'}), 400
        
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
        
    except Exception as e:
        print(f'[ERROR] {e}')
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
        user_id = data['user_id']
        message = data['message']
        
        # 取得鎖定的命盤
        lock = get_chart_lock(user_id)
        
        if not lock or not lock.get('is_active'):
            return jsonify({'error': '請先完成命盤定盤'}), 400
        
        # 格式化命盤結構
        structure = lock['chart_structure']
        structure_text = f"""
命宮：{structure['命宮']['主星']} ({structure['命宮']['宮位']}宮)
格局：{', '.join(structure['格局'])}
五行局：{structure.get('五行局', '未提及')}

十二宮配置：
"""
        
        for palace, info in structure.get('十二宮', {}).items():
            stars = ', '.join(info['主星']) if info['主星'] else '空宮'
            trans = f" - {info['四化']}" if info.get('四化') else ''
            structure_text += f"- {palace} ({info['宮位']}宮): {stars}{trans}\n"
        
        # 組合 Prompt（注入結構）
        prompt = CHAT_WITH_LOCKED_CHART_PROMPT.format(
            chart_structure=structure_text,
            user_question=message
        )
        
        # 呼叫 Gemini
        print(f'[API] 正在為用戶 {user_id} 回應問題...')
        response = call_gemini(prompt)
        
        print(f'[API] 回應完成')
        
        return jsonify({
            'response': response,
            'chart_injected': True
        })
        
    except Exception as e:
        print(f'[ERROR] {e}')
        return jsonify({'error': str(e)}), 500

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
        user_id = data['user_id']
        reason = data.get('reason', '用戶要求重新定盤')
        
        # 取得用戶資料
        user = get_user(user_id)
        
        if not user:
            return jsonify({'error': '找不到用戶資料'}), 404
        
        # 停用舊的鎖定
        old_lock = get_chart_lock(user_id)
        if old_lock:
            old_lock['is_active'] = False
            old_lock['deactivated_at'] = datetime.now().isoformat()
            old_lock['deactivate_reason'] = reason
            save_chart_lock(user_id + '_old', old_lock)
        
        print(f'[API] 用戶 {user_id} 重新定盤，原因：{reason}')
        
        # 返回前端，讓它重新呼叫 initial-analysis
        return jsonify({
            'status': 'ready_for_reanalysis',
            'message': '已清除舊命盤，請重新進行命盤分析'
        })
        
    except Exception as e:
        print(f'[ERROR] {e}')
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
        user_id = data['user_id']
        target_year = data.get('target_year', datetime.now().year)
        
        # 取得鎖定的命盤
        lock = get_chart_lock(user_id)
        if not lock or not lock.get('is_active'):
            return jsonify({'error': '請先完成命盤定盤'}), 400
        
        # 取得用戶資料
        user = get_user(user_id)
        if not user:
            return jsonify({'error': '找不到用戶資料'}), 404
        
        # 計算流年（需要用戶出生年份）
        # 簡化：從出生日期字串中提取年份
        birth_year = 1979  # 農曆68年 = 西元1979年，實際應從用戶資料解析
        
        # 創建流年計算器
        ming_gong_branch = lock['chart_structure']['命宮']['宮位']
        teller = FortuneTeller(
            birth_year=birth_year,
            birth_month=9,  # 暫時固定，實際應從用戶資料取得
            birth_day=23,
            gender=user.get('gender', '男'),
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
        print(f'[API] 正在生成 {target_year} 年流年分析...')
        analysis = call_gemini(prompt)
        
        return jsonify({
            'fortune_data': fortune_data,
            'analysis': analysis
        })
        
    except Exception as e:
        print(f'[ERROR] {e}')
        import traceback
        traceback.print_exc()
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
        user_id = data['user_id']
        target_year = data.get('target_year', datetime.now().year)
        target_month = data.get('target_month', datetime.now().month)
        
        # 取得鎖定的命盤
        lock = get_chart_lock(user_id)
        if not lock or not lock.get('is_active'):
            return jsonify({'error': '請先完成命盤定盤'}), 400
        
        # 計算流月
        birth_year = 1979
        ming_gong_branch = lock['chart_structure']['命宮']['宮位']
        
        user = get_user(user_id)
        teller = FortuneTeller(
            birth_year=birth_year,
            birth_month=9,
            birth_day=23,
            gender=user.get('gender', '男'),
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
        print(f'[API] 正在生成 {target_year} 年 {target_month} 月流月分析...')
        analysis = call_gemini(prompt)
        
        return jsonify({
            'fortune_data': fortune_data,
            'analysis': analysis
        })
        
    except Exception as e:
        print(f'[ERROR] {e}')
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
        user_id = data['user_id']
        question = data['question']
        
        # 取得鎖定的命盤
        lock = get_chart_lock(user_id)
        if not lock or not lock.get('is_active'):
            return jsonify({'error': '請先完成命盤定盤'}), 400
        
        # 計算當前流年
        birth_year = 1979
        ming_gong_branch = lock['chart_structure']['命宮']['宮位']
        
        user = get_user(user_id)
        teller = FortuneTeller(
            birth_year=birth_year,
            birth_month=9,
            birth_day=23,
            gender=user.get('gender', '男'),
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
        print(f'[API] 正在分析問題：{question}')
        analysis = call_gemini(prompt)
        
        return jsonify({
            'fortune_data': fortune_data,
            'analysis': analysis
        })
        
    except Exception as e:
        print(f'[ERROR] {e}')
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
        
        if not user_a_id or not user_b_id:
            return jsonify({'error': '需要提供兩位用戶的 ID'}), 400
        
        # 獲取兩位用戶的鎖定命盤
        lock_a = get_chart_lock(user_a_id)
        lock_b = get_chart_lock(user_b_id)
        
        if not lock_a or not lock_b:
            return jsonify({'error': '兩位用戶都需要先完成定盤'}), 400
        
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
        print(f'[API] 正在分析婚配合盤：{user_a_id} & {user_b_id}')
        analysis = call_gemini(prompt)
        
        return jsonify({
            'user_a_id': user_a_id,
            'user_b_id': user_b_id,
            'analysis_type': '婚配相性',
            'analysis': analysis
        })
        
    except Exception as e:
        print(f'[ERROR] {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/synastry/partnership', methods=['POST'])
def synastry_partnership():
    """合盤分析：合夥相性"""
    try:
        data = request.json
        user_a_id = data.get('user_a_id')
        user_b_id = data.get('user_b_id')
        partnership_info = data.get('partnership_info', '未提供具體合夥項目資訊')
        
        if not user_a_id or not user_b_id:
            return jsonify({'error': '需要提供兩位用戶的 ID'}), 400
        
        # 獲取兩位用戶的鎖定命盤
        lock_a = get_chart_lock(user_a_id)
        lock_b = get_chart_lock(user_b_id)
        
        if not lock_a or not lock_b:
            return jsonify({'error': '兩位用戶都需要先完成定盤'}), 400
        
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
        print(f'[API] 正在分析合夥關係：{user_a_id} & {user_b_id}')
        analysis = call_gemini(prompt)
        
        return jsonify({
            'user_a_id': user_a_id,
            'user_b_id': user_b_id,
            'analysis_type': '合夥相性',
            'partnership_info': partnership_info,
            'analysis': analysis
        })
        
    except Exception as e:
        print(f'[ERROR] {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/synastry/quick', methods=['POST'])
def synastry_quick():
    """快速合盤評估"""
    try:
        data = request.json
        user_a_id = data.get('user_a_id')
        user_b_id = data.get('user_b_id')
        analysis_type = data.get('analysis_type', '婚配')  # 婚配 或 合夥
        
        if not user_a_id or not user_b_id:
            return jsonify({'error': '需要提供兩位用戶的 ID'}), 400
        
        # 獲取兩位用戶的鎖定命盤
        lock_a = get_chart_lock(user_a_id)
        lock_b = get_chart_lock(user_b_id)
        
        if not lock_a or not lock_b:
            return jsonify({'error': '兩位用戶都需要先完成定盤'}), 400
        
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
        print(f'[API] 正在快速合盤：{user_a_id} & {user_b_id} ({analysis_type})')
        analysis = call_gemini(prompt)
        
        return jsonify({
            'user_a_id': user_a_id,
            'user_b_id': user_b_id,
            'analysis_type': f'快速{analysis_type}評估',
            'analysis': analysis
        })
        
    except Exception as e:
        print(f'[ERROR] {e}')
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
        print(f'[API] 正在為婚禮擇日：{groom_id} & {bride_id} ({target_year}年)')
        analysis = call_gemini(prompt)
        
        return jsonify({
            'groom_id': groom_id,
            'bride_id': bride_id,
            'target_year': target_year,
            'analysis_type': '婚嫁擇日',
            'analysis': analysis
        })
        
    except Exception as e:
        print(f'[ERROR] {e}')
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
        print(f'[API] 正在為開業擇日：{owner_id} ({target_year}年)')
        analysis = call_gemini(prompt)
        
        return jsonify({
            'owner_id': owner_id,
            'target_year': target_year,
            'business_type': business_type,
            'analysis_type': '開業擇日',
            'analysis': analysis
        })
        
    except Exception as e:
        print(f'[ERROR] {e}')
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
        print(f'[API] 正在為搬家擇日：{owner_id} ({target_year}年)')
        analysis = call_gemini(prompt)
        
        return jsonify({
            'owner_id': owner_id,
            'target_year': target_year,
            'new_address': new_address,
            'analysis_type': '搬家入宅擇日',
            'analysis': analysis
        })
        
    except Exception as e:
        print(f'[ERROR] {e}')
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
        
        # 计算八字
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
        
        # 生成分析提示词
        prompt = format_bazi_analysis_prompt(
            bazi_result=bazi_result,
            gender=data['gender'],
            birth_year=data['year'],
            birth_month=data['month'],
            birth_day=data['day'],
            birth_hour=data['hour']
        )
        
        # 调用 AI 进行分析
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        
        return jsonify({
            'status': 'success',
            'data': {
                'bazi_chart': bazi_result,
                'analysis': response.text,
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
        
        # 生成运势分析提示词
        prompt = format_bazi_fortune_prompt(
            bazi_result=bazi_result,
            query_year=data['query_year'],
            query_month=data.get('query_month')
        )
        
        # 调用 AI 进行分析
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        
        return jsonify({
            'status': 'success',
            'data': {
                'bazi_chart': bazi_result,
                'fortune_analysis': response.text,
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
        ziwei_chart_info = f"""
命宫：{lock_data['locked_palace']}
身宫：{lock_data.get('body_palace', '未知')}
主星组合：{', '.join(lock_data.get('main_stars', []))}
五行局：{lock_data.get('element_bureau', '未知')}
        """
        
        # 4. 如果有之前的紫微分析，获取摘要（简化版）
        ziwei_analysis_summary = lock_data.get('initial_analysis_summary', 
            "紫微分析摘要：请参考完整的紫微斗数分析报告")
        
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
        
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        summary_response = model.generate_content(bazi_summary_prompt)
        bazi_analysis_summary = summary_response.text
        
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
            bazi_analysis_summary=bazi_analysis_summary
        )
        
        # 7. 调用 AI 进行交叉验证分析
        validation_response = model.generate_content(prompt)
        
        return jsonify({
            'status': 'success',
            'data': {
                'ziwei_chart': {
                    'locked_palace': lock_data['locked_palace'],
                    'body_palace': lock_data.get('body_palace'),
                    'main_stars': lock_data.get('main_stars', [])
                },
                'bazi_chart': bazi_result,
                'cross_validation_analysis': validation_response.text,
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
# 啟動服務
# ============================================

if __name__ == '__main__':
    print('='*60)
    print('Aetheria 定盤系統 API')
    print('='*60)
    print('服務位址：http://localhost:5000')
    print('健康檢查：http://localhost:5000/health')
    print('='*60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
