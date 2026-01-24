# Aetheria 进阶功能测试指南

## 📋 测试前准备

### 步骤 1：确保 API 服务运行

```powershell
# 启动 API 服务（在后台运行）
Start-Job -Name "AetheriaAPI" -ScriptBlock { 
    Set-Location C:\Users\User\Desktop\Aetheria_Core
    python api_server.py 
}

# 检查服务状态
Get-Job -Name "AetheriaAPI"
```

### 步骤 2：创建测试用户

**重要**：进阶功能测试需要两个已定盘的用户：
- `test_user_001` - 农历68年9月23日 23:58, 台湾彰化市, 男
- `test_user_002` - 农历70年5月15日 14:30, 台湾台北市, 女

#### 方法 1：使用快速创建脚本（推荐）

```powershell
# 在新终端窗口执行
python create_user_002.py
```

#### 方法 2：手动创建

```powershell
# 步骤 2.1：分析命盘
Invoke-RestMethod -Uri http://localhost:5000/api/analysis -Method Post -Body (@{
    user_id = "test_user_002"
    birth_date = "农历70年5月15日"
    birth_time = "14:30"
    birth_location = "台湾台北市"
    gender = "女"
} | ConvertTo-Json) -ContentType "application/json"

# 步骤 2.2：锁定命盘
Start-Sleep -Seconds 2
Invoke-RestMethod -Uri http://localhost:5000/api/lock -Method Post -Body (@{
    user_id = "test_user_002"
} | ConvertTo-Json) -ContentType "application/json"
```

#### 方法 3：使用 Python 脚本

```python
import requests
import time

# 分析命盘
r1 = requests.post('http://localhost:5000/api/analysis', json={
    'user_id': 'test_user_002',
    'birth_date': '农历70年5月15日',
    'birth_time': '14:30',
    'birth_location': '台湾台北市',
    'gender': '女'
})
print("分析:", r1.status_code)

# 锁定命盘
time.sleep(2)
r2 = requests.post('http://localhost:5000/api/lock', json={
    'user_id': 'test_user_002'
})
print("锁定:", r2.status_code)
```

### 步骤 3：验证用户状态

```powershell
# 检查 test_user_001
Invoke-RestMethod -Uri http://localhost:5000/api/lock/test_user_001

# 检查 test_user_002
Invoke-RestMethod -Uri http://localhost:5000/api/lock/test_user_002
```

如果返回命盘结构，表示用户已准备好。

---

## 🧪 运行测试

### 测试 1：自动化测试（推荐）

```powershell
python test_advanced_auto.py
```

**测试项目**：
1. 快速合盘评估
2. 开业择日
3. 合夥关系分析

**优点**：
- 自动检查并创建 test_user_002
- 无需交互，全自动运行
- 适合快速验证功能

### 测试 2：互动式测试

```powershell
python test_advanced.py
```

**测试项目**：
1. 婚配合盘分析
2. 合夥关系分析
3. 快速合盘评估
4. 婚嫁择日
5. 开业择日
6. 搬家入宅择日
7. 执行所有测试

**优点**：
- 可选择特定功能测试
- 可多次测试同一功能
- 查看完整输出

---

## 📊 功能说明

### 合盘功能（3个端点）

#### 1. 婚配合盘 (`/api/synastry/marriage`)
- **用途**：评估两人婚配相性
- **分析维度**：8维度评分（个性契合、价值观、情感连结等）
- **输出长度**：2500-3000字
- **包含内容**：
  - 整体相性评分
  - 命盘相性分析
  - 个性契合度
  - 事业与财运配合
  - 情感与沟通模式
  - 家庭与子女运势
  - 危机预警与化解
  - 终身建议与祝福

#### 2. 合夥合盘 (`/api/synastry/partnership`)
- **用途**：评估事业合夥相性
- **分析维度**：7维度评分（能力互补、决策风格、风险承受等）
- **输出长度**：2000-2500字
- **包含内容**：
  - 合夥相性评分
  - 命盘相性分析
  - 角色分工建议
  - 财务规划建议
  - 风险预警与管控
  - 合夥成功策略
  - 终极建议与评估

#### 3. 快速合盘 (`/api/synastry/quick`)
- **用途**：快速评估两人关系
- **输出长度**：500-800字
- **包含内容**：
  - 整体相性评分
  - 三大优势
  - 三大挑战
  - 关键建议
  - 一句话总结

### 择日功能（3个端点）

#### 1. 婚嫁择日 (`/api/date-selection/marriage`)
- **用途**：选择结婚吉日良辰
- **输出长度**：3000-4000字
- **包含内容**：
  - 年度总体评估
  - 推荐吉日 Top 10
  - 次选日期 5个备选
  - 时辰选择指南
  - 婚礼流程择时建议
  - 风水与禁忌提醒
  - 婚后吉日建议
  - 总结与祝福

#### 2. 开业择日 (`/api/date-selection/business`)
- **用途**：选择开业吉日
- **输出长度**：2500-3500字
- **包含内容**：
  - 年度事业运势评估
  - 推荐开业吉日 Top 10
  - 开业时辰指南
  - 开业流程择时建议
  - 风水与禁忌提醒
  - 财运提升建议
  - 行业特殊建议
  - 总结与祝福

#### 3. 搬家择日 (`/api/date-selection/moving`)
- **用途**：选择搬家入宅吉日
- **输出长度**：2500-3500字
- **包含内容**：
  - 年度迁移运势评估
  - 推荐搬家吉日 Top 10
  - 搬家流程择时指南
  - 方位与风水建议
  - 家庭成员配合
  - 注意事项与禁忌
  - 入宅后吉日建议
  - 总结与祝福

---

## 📈 测试示例

### 示例 1：快速合盘评估

```python
import requests

response = requests.post(
    'http://localhost:5000/api/synastry/quick',
    json={
        'user_a_id': 'test_user_001',
        'user_b_id': 'test_user_002',
        'analysis_type': '婚配'  # 或 '合夥'
    }
)

result = response.json()
print(result['analysis'])
```

### 示例 2：开业择日

```python
import requests

response = requests.post(
    'http://localhost:5000/api/date-selection/business',
    json={
        'owner_id': 'test_user_001',
        'target_year': 2026,
        'business_type': 'AI 命理咨询工作室',
        'business_nature': '服务业',
        'preferred_months': '3月、4月、9月'
    }
)

result = response.json()
print(result['analysis'][:1000])  # 显示前1000字
```

---

## 🐛 常见问题

### Q1：显示"两位用户都需要先完成定盘"

**原因**：test_user_002 尚未创建或未锁定命盘

**解决**：
```powershell
python create_user_002.py
```

### Q2：显示"无法连接到 API 服务"

**原因**：API 服务未启动

**解决**：
```powershell
# 检查服务状态
Get-Job -Name "AetheriaAPI"

# 如果没有运行，启动服务
Start-Job -Name "AetheriaAPI" -ScriptBlock { 
    Set-Location C:\Users\User\Desktop\Aetheria_Core
    python api_server.py 
}
```

### Q3：分析结果不完整或中断

**原因**：网络延迟或 API 响应超时

**解决**：
- 等待更长时间（某些分析需要 30-60 秒）
- 检查 API Key 配额是否充足
- 查看 API 服务日志：`Receive-Job -Name "AetheriaAPI" -Keep`

---

## 📝 测试检查清单

在运行测试前，确认以下事项：

- [ ] API 服务正在运行（端口 5000）
- [ ] test_user_001 已定盘
- [ ] test_user_002 已定盘
- [ ] .env 文件中的 API Key 有效
- [ ] 网络连接正常

---

## 🎯 预期结果

### 成功标志
- ✅ 所有 API 调用返回 200 状态码
- ✅ 每个分析输出包含完整结构
- ✅ 合盘评分在 1-10 之间
- ✅ 择日功能至少返回 5 个吉日

### 失败处理
如果测试失败：
1. 检查错误信息
2. 验证用户是否已定盘
3. 查看 API 服务日志
4. 确认 Gemini API Key 有效

---

## 📞 需要帮助？

如果遇到问题，请提供：
1. 错误信息完整内容
2. API 服务日志（`Receive-Job -Name "AetheriaAPI" -Keep`）
3. 测试命令和参数
4. Python 版本和依赖包版本

---

**祝测试顺利！✨**
