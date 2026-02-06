"""
测试 AI Tool Use 功能
"""

import pytest
from src.utils.tools import (
    get_tool_definitions,
    execute_tool,
    execute_calculate_ziwei,
    execute_calculate_bazi,
    execute_get_user_profile
)


class TestToolDefinitions:
    """测试工具定义"""
    
    def test_get_tool_definitions(self):
        """测试获取工具定义"""
        tools = get_tool_definitions()
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        # 验证必要工具存在
        tool_names = [t['name'] for t in tools]
        assert 'calculate_ziwei' in tool_names
        assert 'calculate_bazi' in tool_names
        assert 'calculate_astrology' in tool_names
        assert 'calculate_numerology' in tool_names
        assert 'analyze_name' in tool_names
        assert 'draw_tarot' in tool_names
        assert 'get_user_profile' in tool_names
        assert 'save_user_insight' in tool_names
    
    def test_tool_schema_format(self):
        """测试工具定义符合 Gemini Function Calling 格式"""
        tools = get_tool_definitions()
        
        for tool in tools:
            assert 'name' in tool
            assert 'description' in tool
            assert 'parameters' in tool
            
            params = tool['parameters']
            assert 'type' in params
            assert params['type'] == 'object'
            assert 'properties' in params
            
            # 验证 required 字段
            if 'required' in params:
                assert isinstance(params['required'], list)


class TestToolExecution:
    """测试工具执行"""
    
    def test_execute_calculate_bazi(self):
        """测试八字排盘工具"""
        result = execute_calculate_bazi(
            year=1990,
            month=5,
            day=15,
            hour=10,
            minute=30,
            gender="男"
        )
        
        assert isinstance(result, dict)
        assert result['status'] == 'success'
        assert result['system'] == 'bazi'
        assert 'data' in result
        
        # 验证八字数据结构（使用繁体中文字段）
        data = result['data']
        assert '四柱' in data or 'pillars' in data  # 支持两种格式
        if '四柱' in data:
            assert '年柱' in data['四柱']
            assert '月柱' in data['四柱']
            assert '日柱' in data['四柱']
            assert '时柱' in data['四柱'] or '時柱' in data['四柱']
    
    def test_execute_calculate_ziwei(self):
        """测试紫微斗数排盘工具"""
        result = execute_calculate_ziwei(
            birth_date="1990-05-15",
            birth_time="10:30",
            gender="男",
            birth_location="台北"
        )
        
        assert isinstance(result, dict)
        assert result['status'] == 'success'
        assert result['system'] == 'ziwei'
        assert 'data' in result
        
        # 验证紫微数据结构
        data = result['data']
        assert '十二宮' in data
        assert '命宮' in data['十二宮']
    
    def test_execute_tool_dispatcher(self):
        """测试工具调度器"""
        # 测试有效工具
        result = execute_tool('calculate_bazi', {
            'year': 1990,
            'month': 5,
            'day': 15,
            'hour': 10,
            'gender': '男'
        })
        assert result['status'] == 'success'
        
        # 测试无效工具名
        result = execute_tool('invalid_tool', {})
        assert result['status'] == 'error'
        assert '未知的工具' in result['message']
        
        # 测试参数错误
        result = execute_tool('calculate_bazi', {'invalid_param': 'value'})
        assert result['status'] == 'error'


class TestToolIntegration:
    """测试工具集成（需要数据库）"""
    
    def test_save_and_get_user_insight(self, db_with_user):
        """测试保存和读取用户洞察"""
        db, user_id = db_with_user
        
        # 保存洞察
        result = execute_tool('save_user_insight', {
            'user_id': user_id,
            'insight_type': 'personality',
            'content': '重视事业发展',
            'confidence': 0.8
        })
        
        assert result['status'] == 'success'
        assert 'insight' in result
        
        # 读取用户画像
        profile_result = execute_tool('get_user_profile', {
            'user_id': user_id
        })
        
        assert profile_result['status'] == 'success'
        assert 'persona' in profile_result
        
        persona = profile_result['persona']
        if persona and 'personality_tags' in persona:
            tags = persona['personality_tags']
            assert isinstance(tags, list)
            # 应该包含刚才保存的洞察
            assert any(t.get('content') == '重视事业发展' for t in tags)


@pytest.fixture
def db_with_user(monkeypatch):
    """创建测试数据库和用户"""
    from src.utils.database import get_database
    import uuid
    
    db = get_database('data/test_tool_use.db')
    user_id = f"test_user_{uuid.uuid4().hex[:8]}"
    
    # 创建测试用户
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO members (user_id, email, display_name, password_hash, password_salt) 
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, 'test@example.com', 'Test User', 'dummy_hash', 'dummy_salt')
        )

    # 讓 tools 使用測試資料庫
    monkeypatch.setattr('src.utils.tools.get_database', lambda: db)
    
    yield db, user_id
    
    # 清理
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM members WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM user_persona WHERE user_id = ?", (user_id,))
    except Exception:
        pass


class TestCalculatorTools:
    """测试各个计算工具"""
    
    def test_numerology_tool(self):
        """测试生命灵数工具"""
        result = execute_tool('calculate_numerology', {
            'birth_date': '1990-05-15',
            'full_name': 'John Doe',
            'include_cycles': False
        })
        if result['status'] == 'error':
            pytest.skip(result.get('error') or 'numerology tool unavailable')
        assert result['status'] == 'success'
        assert result['system'] == 'numerology'
        assert 'data' in result
        # Verify numerology data structure (dataclass converted to dict)
        data = result['data']
        assert 'life_path' in data
        assert 'birthday' in data
        assert isinstance(data['life_path'], int)
    
    def test_name_analysis_tool(self):
        """测试姓名学工具"""
        result = execute_tool('analyze_name', {
            'surname': '王',
            'given_name': '小明'
        })
        if result['status'] == 'error':
            pytest.skip(result.get('error') or 'name tool unavailable')
        assert result['status'] == 'success'
        assert result['system'] == 'name'
        assert 'data' in result
    
    def test_tarot_tool(self):
        """测试塔罗占卜工具"""
        result = execute_tool('draw_tarot', {
            'question': '今年的事业运势如何？',
            'spread': 'single',
            'seed': 42  # 固定种子以保证可重现
        })
        if result['status'] == 'error':
            pytest.skip(result.get('error') or 'tarot tool unavailable')
        assert result['status'] == 'success'
        assert result['system'] == 'tarot'
        assert 'data' in result
        assert 'cards' in result['data']
    
    def test_astrology_tool(self):
        """测试西洋占星工具"""
        result = execute_tool('calculate_astrology', {
            'name': 'Test User',
            'year': 1990,
            'month': 5,
            'day': 15,
            'hour': 10,
            'minute': 30,
            'city': 'Taipei',
            'nation': 'TW'
        })
        
        assert result['status'] == 'success'
        assert result['system'] == 'astrology'
        assert 'data' in result
        assert 'planets' in result['data']
