# Tool Use 实现总结

## 已完成功能

### 1. 工具定义 (src/utils/tools.py)
- ✅ 8个工具的 JSON Schema 定义（符合 Gemini Function Calling 格式）
  - calculate_ziwei（紫微斗数）
  - calculate_bazi（八字）
  - calculate_astrology（西洋占星）
  - calculate_numerology（生命灵数）
  - analyze_name（姓名学）
  - draw_tarot（塔罗牌）
  - get_user_profile（用户画像查询）
  - save_user_insight（保存用户洞察）

### 2. 工具执行器
- ✅ 每个工具都有独立的执行函数
- ✅ 统一的错误处理与日志记录
- ✅ execute_tool() 调度器

### 3. Gemini Client 增强 (src/utils/gemini_client.py)
- ✅ generate() 方法支持 tools 参数
- ✅ 返回完整 response 对象（而非仅文本）供后续处理

### 4. 工具调用循环 (src/api/server.py)
- ✅ call_gemini_with_tools() 函数实现多轮工具调用
- ✅ 最多支持 5 次迭代
- ✅ 自动注入 user_id 参数
- ✅ 工具结果自动加入对话上下文

### 5. API 端点集成 (/api/chat/consult)
- ✅ System instruction 添加工具使用指导
- ✅ 根据 enable_tools 标志切换模式（当前全面启用）
- ✅ 返回 tool_calls 历史记录（payload + response）

### 6. 测试覆盖 (tests/test_tool_use.py)
- ✅ 工具定义格式验证
- ✅ 八字、紫微排盘工具测试通过
- ✅ 占星工具测试通过
- ⚠️ 部分工具需进一步调试（numerology, name, tarot）

## 使用方式

当用户在对话中提供生辰信息时，AI 会自动调用相应排盘工具：

```
用户：我是1990年5月15日10:30出生的男生，帮我看看今年运势
AI：（自动调用 calculate_bazi 和 calculate_ziwei）
    根据您的八字命盘...（基于工具返回结果回答）
```

## 下一步优化

1. 修复剩余 3 个工具的执行错误
2. 添加智能工具选择逻辑（根据问题类型自动选择工具）
3. 添加工具调用进度通知（via SSE）
4. 实现工具结果缓存（避免重复排盘）
5. 完整的端到端测试

## 测试命令

```bash
# 测试工具定义
python -m pytest tests/test_tool_use.py::TestToolDefinitions -v

# 测试工具执行
python -m pytest tests/test_tool_use.py::TestToolExecution -v

# 全部测试
python -m pytest tests/test_tool_use.py -v
```

## API 调用示例

```python
import requests

response = requests.post('http://localhost:5001/api/chat/consult', json={
    "message": "我是1990年5月15日10:30出生的，性别男，帮我排个八字",
    "session_id": "test_session_123"
}, headers={
    "Authorization": "Bearer YOUR_TOKEN"
})

data = response.json()
print(data['reply'])  # AI 回复
print(data['tool_calls'])  # 工具调用历史
```

## 已通过测试

```
tests/test_tool_use.py::TestToolDefinitions::test_get_tool_definitions PASSED
tests/test_tool_use.py::TestToolDefinitions::test_tool_schema_format PASSED
tests/test_tool_use.py::TestToolExecution::test_execute_calculate_bazi PASSED
tests/test_tool_use.py::TestToolExecution::test_execute_calculate_ziwei PASSED
tests/test_tool_use.py::TestToolExecution::test_execute_tool_dispatcher PASSED
tests/test_tool_use.py::TestCalculatorTools::test_astrology_tool PASSED
```

6 / 10 tests passing (60%)
