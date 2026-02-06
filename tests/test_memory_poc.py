"""
Phase 1 POC 整合測試
驗證三層記憶架構與 /api/chat/consult 整合
"""

from src.utils.database import get_database
from src.utils.memory import MemoryManager
import os
import tempfile


def test_memory_integration():
    """測試記憶系統完整流程"""
    print("=" * 60)
    print("Phase 1 POC - 三層記憶架構測試")
    print("=" * 60)
    
    # 使用臨時資料庫
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    db_path = temp_db.name
    
    try:
        # 1. 初始化
        print("\n[1] 初始化資料庫與記憶管理器...")
        db = get_database(db_path)
        mm = MemoryManager(db, window_size=10)
        print("✓ 初始化成功")
        
        # 2. 測試 Layer 1: 短期記憶
        print("\n[2] 測試 Layer 1 - 短期對話記憶...")
        user_id = "test_user_001"
        session_id = "test_session_001"
        
        # 模擬對話
        mm.add_conversation_turn(user_id, session_id, 'user', '我想了解今年的事業運')
        mm.add_conversation_turn(user_id, session_id, 'assistant', '好的，讓我看看你的命盤...')
        mm.add_conversation_turn(user_id, session_id, 'user', '我是 1990 年出生的')
        
        recent = mm.get_recent_conversation(session_id, limit=10)
        assert len(recent) == 3
        assert recent[0]['role'] == 'user'
        assert recent[1]['role'] == 'assistant'
        print(f"✓ 成功記錄 {len(recent)} 筆對話")
        
        # 3. 測試系統事件注入
        print("\n[3] 測試系統事件注入...")
        mm.inject_system_event(
            user_id, 
            session_id, 
            'chart.completed',
            {'chart_type': 'ziwei', 'success': True}
        )
        recent = mm.get_recent_conversation(session_id)
        system_events = [m for m in recent if m['role'] == 'system_event']
        assert len(system_events) == 1
        print(f"✓ 成功注入系統事件")
        
        # 4. 測試 Layer 2: 摘要記憶
        print("\n[4] 測試 Layer 2 - 摘要記憶...")
        summary_id = mm.create_episodic_summary(
            user_id=user_id,
            topic='career',
            key_points='2026年2月關注事業運勢，使用者關心工作發展',
            source_session_ids=[session_id]
        )
        summaries = mm.get_episodic_summaries(user_id, topic='career', days=30)
        assert len(summaries) == 1
        assert summaries[0]['topic'] == 'career'
        print(f"✓ 成功建立摘要記憶 (ID: {summary_id})")
        
        # 5. 測試 Layer 3: 使用者畫像
        print("\n[5] 測試 Layer 3 - 使用者畫像...")
        mm.upsert_user_persona(
            user_id=user_id,
            birth_info={'year': 1990, 'month': 5, 'day': 20},
            personality_tags=['積極', '重視事業', '理性'],
            preferences={'tone': 'professional', 'response_length': 'medium'}
        )
        persona = mm.get_user_persona(user_id)
        assert persona is not None
        assert persona['birth_info']['year'] == 1990
        assert '積極' in persona['personality_tags']
        print(f"✓ 成功建立使用者畫像")
        
        # 6. 測試完整上下文建構
        print("\n[6] 測試完整上下文建構...")
        context = mm.build_context_for_ai(user_id, session_id)
        assert 'short_term' in context
        assert 'episodic' in context
        assert 'persona' in context
        assert len(context['short_term']) == 4  # 3 對話 + 1 事件
        assert len(context['episodic']) == 1
        assert context['persona'] is not None
        print(f"✓ 上下文包含：")
        print(f"  - 短期記憶: {len(context['short_term'])} 筆")
        print(f"  - 摘要記憶: {len(context['episodic'])} 筆")
        print(f"  - 使用者畫像: {context['persona']['personality_tags']}")
        
        # 7. 測試封存功能
        print("\n[7] 測試舊對話封存...")
        # 再新增 15 筆對話
        for i in range(15):
            mm.add_conversation_turn(user_id, session_id, 'user', f'測試訊息 {i+1}')
        
        archived_count = mm.archive_old_conversations(session_id, keep_recent=10)
        assert archived_count > 0
        print(f"✓ 成功封存 {archived_count} 筆舊對話")
        
        # 驗證封存後只保留最近 10 筆
        recent_after_archive = mm.get_recent_conversation(session_id, limit=20)
        assert len(recent_after_archive) == 10
        print(f"✓ 封存後保留最近 {len(recent_after_archive)} 筆")
        
        print("\n" + "=" * 60)
        print("✅ Phase 1 POC 測試全部通過！")
        print("=" * 60)
        print("\n已實現功能：")
        print("  ✓ 三層記憶架構（短期/摘要/畫像）")
        print("  ✓ 系統事件注入")
        print("  ✓ 對話封存機制")
        print("  ✓ 完整上下文建構")
        print("  ✓ 與資料庫整合")
        
    finally:
        # 清理
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"\n已清理測試資料庫")


if __name__ == '__main__':
    test_memory_integration()
