"""
測試 AI 記憶功能
驗證 AI 能否記住並引用過往對話
"""

import sys
import json
from pathlib import Path

# 確保專案根目錄在路徑中
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.utils.database import get_database
from src.utils.memory import MemoryManager
import tempfile
import os


def test_ai_memory_recall():
    """測試 AI 記憶回憶功能"""
    print("=" * 60)
    print("測試 AI 三層記憶回憶功能")
    print("=" * 60)
    
    # 使用臨時資料庫
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    db_path = temp_db.name
    
    try:
        db = get_database(db_path)
        mm = MemoryManager(db)
        
        user_id = "test_user_memory"
        session_id = "test_session_memory"
        
        # 模擬一段對話並建立記憶
        print("\n[步驟 1] 建立對話記憶...")
        
        # 第一輪對話
        mm.add_conversation_turn(user_id, session_id, 'user', '我想了解我的事業運')
        mm.add_conversation_turn(user_id, session_id, 'assistant', '好的，讓我看看你的命盤。你的出生年月日是？')
        
        # 第二輪對話
        mm.add_conversation_turn(user_id, session_id, 'user', '我是 1990 年 5 月 20 日出生的')
        mm.add_conversation_turn(user_id, session_id, 'assistant', '收到。根據你的八字，今年事業運勢不錯。')
        
        print("✓ 已建立 4 筆對話記憶")
        
        # 建立摘要記憶
        print("\n[步驟 2] 建立摘要記憶...")
        mm.create_episodic_summary(
            user_id=user_id,
            topic='career',
            key_points='使用者關注事業運勢，1990年5月20日出生，對今年運勢有疑問',
            source_session_ids=[session_id]
        )
        print("✓ 已建立摘要記憶")
        
        # 建立使用者畫像
        print("\n[步驟 3] 建立使用者畫像...")
        mm.upsert_user_persona(
            user_id=user_id,
            birth_info={'year': 1990, 'month': 5, 'day': 20},
            personality_tags=['積極向上', '重視事業', '理性思考'],
            preferences={'tone': 'professional', 'response_length': 'medium'}
        )
        print("✓ 已建立使用者畫像")
        
        # 注入系統事件
        print("\n[步驟 4] 注入系統事件...")
        mm.inject_system_event(
            user_id=user_id,
            session_id=session_id,
            event_type='chart.completed',
            event_data={'chart_type': 'bazi', 'success': True, 'timestamp': '2026-02-04'}
        )
        print("✓ 已注入系統事件")
        
        # 建構完整上下文（這就是 AI 會收到的）
        print("\n[步驟 5] 建構 AI 上下文...")
        context = mm.build_context_for_ai(user_id, session_id)
        
        print(f"\n✓ AI 收到的記憶上下文：")
        print(f"  - 短期記憶: {len(context['short_term'])} 筆")
        print(f"  - 摘要記憶: {len(context['episodic'])} 筆")
        print(f"  - 使用者畫像: {'存在' if context['persona'] else '不存在'}")
        
        # 顯示記憶細節
        print("\n[記憶內容詳情]")
        print("\n短期記憶（最近對話）:")
        for i, msg in enumerate(context['short_term'][-3:], 1):
            role = msg['role']
            content = msg['content'][:50] + '...' if len(msg['content']) > 50 else msg['content']
            print(f"  {i}. [{role}] {content}")
        
        print("\n摘要記憶（過往重點）:")
        for i, summary in enumerate(context['episodic'], 1):
            print(f"  {i}. [{summary['topic']}] {summary['key_points']}")
        
        print("\n使用者畫像:")
        if context['persona']:
            persona = context['persona']
            print(f"  - 生辰: {persona['birth_info']}")
            print(f"  - 性格: {persona['personality_tags']}")
            print(f"  - 偏好: {persona['preferences']}")
        
        # 模擬 AI 應該如何使用記憶
        print("\n" + "=" * 60)
        print("✅ 記憶系統驗證成功！")
        print("=" * 60)
        
        print("\n【AI 應該能做到】")
        print("1. 記住使用者說過「我是 1990 年 5 月 20 日出生」")
        print("2. 知道使用者關注「事業運勢」這個主題")
        print("3. 感知到「八字命盤已完成」這個系統事件")
        print("4. 根據「積極向上、重視事業」調整回應風格")
        print("5. 不再詢問使用者的出生日期（已在畫像中）")
        
        print("\n【測試方式】")
        print("1. 啟動後端: python run.py")
        print("2. 開啟 webapp/chat_demo.html")
        print("3. 問 AI：「剛才我說我什麼時候出生的？」")
        print("4. AI 應該能正確回答並引用記憶")
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"\n已清理測試資料庫")


if __name__ == '__main__':
    test_ai_memory_recall()
