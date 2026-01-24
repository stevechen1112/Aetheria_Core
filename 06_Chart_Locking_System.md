# 定盤系統設計文檔（Chart Locking System）

## 測試結果回顧

**測試日期**：2026-01-24  
**測試次數**：10 次  
**關鍵發現**：
- ✅ 命宮結構：100% 一致（太陰戌宮）
- ✅ 格局判定：100% 一致（機月同梁）
- ✅ 官祿宮：100% 一致（天梁化科寅宮）
- ✅ 財帛宮：100% 一致（天機午宮）
- ✅ 夫妻宮：100% 一致（申宮）

**結論**：LLM 排盤結構高度一致，可採用 LLM-First 策略，但需要定盤機制作為保險。

---

## 系統架構

### 核心流程

```
用戶註冊/首次分析
    ↓
呼叫 Gemini 3 Pro 生成完整命盤
    ↓
提取關鍵結構（命宮、格局、十二宮）
    ↓
存入資料庫（chart_lock 表）
    ↓
顯示給用戶確認
    ↓
[用戶確認正確] → 鎖定命盤
    ↓
後續所有對話都注入此結構
```

### 資料結構

#### 1. 用戶基本資料（users 表）

```json
{
  "user_id": "uuid",
  "name": "張三",
  "birth_date_lunar": "68年9月23日",
  "birth_time": "23:58",
  "birth_location": "台灣彰化市",
  "gender": "男",
  "created_at": "2026-01-24T01:00:00Z"
}
```

#### 2. 鎖定命盤結構（chart_locks 表）

```json
{
  "lock_id": "uuid",
  "user_id": "uuid",
  "version": 1,
  "locked_at": "2026-01-24T01:30:00Z",
  "is_active": true,
  
  "chart_structure": {
    "命宮": {
      "宮位": "戌",
      "主星": ["太陰"],
      "輔星": ["文昌"],
      "四化": null
    },
    "身宮": {
      "位置": "戌",
      "說明": "命身同宮"
    },
    "核心格局": ["機月同梁", "日月並明"],
    "五行局": "火六局",
    
    "十二宮": {
      "兄弟宮": {"宮位": "酉", "主星": ["武曲", "貪狼"]},
      "夫妻宮": {"宮位": "申", "主星": ["太陽", "巨門"]},
      "子女宮": {"宮位": "未", "主星": ["天府"]},
      "財帛宮": {"宮位": "午", "主星": ["天機"], "四化": null},
      "疾厄宮": {"宮位": "巳", "主星": ["紫微", "七殺"]},
      "遷移宮": {"宮位": "辰", "主星": [], "四化": "文曲化忌"},
      "奴僕宮": {"宮位": "卯", "主星": ["天相"]},
      "官祿宮": {"宮位": "寅", "主星": ["天機", "太陰"], "四化": "天梁化科"},
      "田宅宮": {"宮位": "丑", "主星": ["天同"]},
      "福德宮": {"宮位": "子", "主星": ["天梁"]},
      "父母宮": {"宮位": "亥", "主星": ["破軍"]}
    }
  },
  
  "original_analysis": "完整的首次分析文字（2000字）...",
  "confirmation_status": "confirmed",
  "confirmed_by_user_at": "2026-01-24T01:35:00Z"
}
```

#### 3. 對話歷史（conversations 表）

```json
{
  "conversation_id": "uuid",
  "user_id": "uuid",
  "chart_lock_id": "uuid",
  "messages": [
    {
      "role": "user",
      "content": "我最近工作不順利，怎麼辦？",
      "timestamp": "2026-01-24T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "根據你的命盤（命宮太陰戌宮，機月同梁格局）...",
      "timestamp": "2026-01-24T10:00:15Z",
      "chart_structure_injected": true
    }
  ]
}
```

---

## Prompt 注入策略

### 首次分析 Prompt

```markdown
你是 Aetheria，精通紫微斗數的 AI 命理顧問。

請為以下用戶提供完整的紫微斗數命盤分析：

出生日期：{lunar_date}
出生時間：{time}
出生地點：{location}
性別：{gender}

**重要**：請按照以下格式輸出，確保結構清晰：

### 一、命盤基礎結構（必須包含）
1. 時辰判定（如晚子時的處理）
2. 命宮：位於哪個宮位？主星是什麼？
3. 核心格局：屬於什麼格局？
4. 十二宮概覽：
   - 命宮（戌宮）：主星
   - 兄弟宮（酉宮）：主星
   - 夫妻宮（申宮）：主星
   ...（其他宮位）

### 二、詳細分析（1500字）
（官祿、財帛、夫妻等詳細解讀）

### 三、性格與建議（500字）
```

### 後續對話 Prompt（注入鎖定結構）

```markdown
你是 Aetheria，正在與用戶 {name} 對話。

【已鎖定的命盤結構】（此為用戶首次分析時確認的正確命盤，請在所有回應中依據此結構）

命宮：太陰（戌宮）
格局：機月同梁、日月並明
五行局：火六局

十二宮配置：
- 命宮（戌）：太陰、文昌
- 兄弟宮（酉）：武曲化祿、貪狼化權
- 夫妻宮（申）：太陽、巨門
- 子女宮（未）：天府
- 財帛宮（午）：天機
- 疾厄宮（巳）：紫微、七殺
- 遷移宮（辰）：文曲化忌
- 奴僕宮（卯）：天相
- 官祿宮（寅）：天機、太陰（借星），天梁化科
- 田宅宮（丑）：天同
- 福德宮（子）：天梁
- 父母宮（亥）：破軍

【用戶當前問題】
{user_question}

【回應要求】
1. 必須基於上述鎖定的命盤結構
2. 不要重新排盤或改變宮位配置
3. 深入分析當前問題與命盤的關聯
4. 提供具體可行的建議
```

---

## API 實作範例

### 1. 首次命盤分析 API

```python
@app.route('/api/chart/initial-analysis', methods=['POST'])
def initial_analysis():
    """
    首次命盤分析
    """
    data = request.json
    user_id = data['user_id']
    
    # 1. 呼叫 Gemini 3 Pro
    chart_analysis = call_gemini_for_chart(
        date=data['birth_date'],
        time=data['birth_time'],
        location=data['birth_location'],
        gender=data['gender']
    )
    
    # 2. 提取結構（使用 LLM 或正則表達式）
    structure = extract_chart_structure(chart_analysis)
    
    # 3. 暫存到資料庫（待確認）
    temp_lock = {
        'user_id': user_id,
        'chart_structure': structure,
        'original_analysis': chart_analysis,
        'confirmation_status': 'pending',
        'created_at': datetime.now()
    }
    db.chart_locks.insert_one(temp_lock)
    
    # 4. 返回給前端確認
    return jsonify({
        'analysis': chart_analysis,
        'structure': structure,
        'lock_id': str(temp_lock['_id']),
        'needs_confirmation': True
    })
```

### 2. 用戶確認 API

```python
@app.route('/api/chart/confirm-lock', methods=['POST'])
def confirm_lock():
    """
    用戶確認命盤正確
    """
    data = request.json
    lock_id = data['lock_id']
    
    # 更新確認狀態
    db.chart_locks.update_one(
        {'_id': ObjectId(lock_id)},
        {
            '$set': {
                'confirmation_status': 'confirmed',
                'confirmed_at': datetime.now(),
                'is_active': True
            }
        }
    )
    
    return jsonify({'status': 'locked', 'message': '命盤已鎖定'})
```

### 3. 後續對話 API

```python
@app.route('/api/chat/message', methods=['POST'])
def chat_message():
    """
    後續對話（自動注入鎖定結構）
    """
    data = request.json
    user_id = data['user_id']
    message = data['message']
    
    # 1. 取得鎖定的命盤
    chart_lock = db.chart_locks.find_one({
        'user_id': user_id,
        'is_active': True
    })
    
    if not chart_lock:
        return jsonify({'error': '請先完成命盤定盤'}), 400
    
    # 2. 組合 Prompt（注入結構）
    prompt = f"""
    【已鎖定的命盤結構】
    {format_chart_structure(chart_lock['chart_structure'])}
    
    【用戶問題】
    {message}
    
    請基於鎖定的命盤回答用戶問題。
    """
    
    # 3. 呼叫 Gemini
    response = call_gemini_chat(
        system_instruction=SYSTEM_INSTRUCTION,
        user_message=prompt,
        conversation_history=get_history(user_id)
    )
    
    # 4. 儲存對話
    save_conversation(user_id, message, response)
    
    return jsonify({'response': response})
```

### 4. 重新定盤 API

```python
@app.route('/api/chart/relock', methods=['POST'])
def relock_chart():
    """
    重新定盤（需用戶明確確認）
    """
    data = request.json
    user_id = data['user_id']
    reason = data.get('reason', '用戶要求重新定盤')
    
    # 1. 停用舊的鎖定
    db.chart_locks.update_many(
        {'user_id': user_id},
        {'$set': {'is_active': False}}
    )
    
    # 2. 重新分析
    new_analysis = call_gemini_for_chart(...)
    
    # 3. 創建新版本
    new_lock = {
        'user_id': user_id,
        'version': get_latest_version(user_id) + 1,
        'chart_structure': extract_chart_structure(new_analysis),
        'original_analysis': new_analysis,
        'relock_reason': reason,
        'created_at': datetime.now()
    }
    db.chart_locks.insert_one(new_lock)
    
    return jsonify({'status': 'relocked', 'new_lock_id': str(new_lock['_id'])})
```

---

## 前端流程設計

### 首次註冊流程

```
1. 用戶填寫出生資料
   ↓
2. 顯示載入畫面（"Aetheria 正在為你排盤..."）
   ↓
3. 顯示完整命盤分析
   ↓
4. 顯示關鍵結構確認框：
   「請確認以下命盤結構是否正確：
   
   命宮：太陰（戌宮）
   格局：機月同梁、日月並明
   官祿宮：天梁化科（寅宮）
   財帛宮：天機（午宮）
   夫妻宮：申宮
   
   ✅ 確認正確  |  ❌ 重新定盤」
   ↓
5. [確認] → 鎖定命盤，進入對話介面
   [重新定盤] → 重新呼叫 API
```

### 對話介面

```
頂部：顯示命盤摘要（可收合）
「你的命盤：太陰戌宮 | 機月同梁格局」

對話區：
用戶：「我最近想換工作，適合嗎？」
Aetheria：「根據你的命盤，官祿宮天梁化科在寅宮...」
```

---

## 錯誤處理

### 情境 1：用戶反饋命盤不準

```
用戶：「我命宮不是太陰，是破軍才對」
系統回應：
「Aetheria 注意到你對命盤結構有疑慮。

當前鎖定的命盤：
- 命宮：太陰（戌宮）
- 格局：機月同梁

你認為應該是：
- 命宮：破軍

這可能的原因：
1. 出生時間需要更精確（如晚子時的判定）
2. 農曆/國曆轉換問題
3. 不同流派的排盤方式

是否要「重新定盤」？
[重新定盤] [保持現狀] [查看詳細說明]
```

### 情境 2：LLM 回應與鎖定結構矛盾

```python
def validate_response(response, locked_structure):
    """
    驗證 LLM 回應是否偏離鎖定結構
    """
    # 檢查是否提到錯誤的命宮
    if '破軍' in response and locked_structure['命宮']['主星'] == ['太陰']:
        return False, '回應提到了錯誤的命宮主星'
    
    # 檢查是否提到錯誤的格局
    if '殺破狼' in response and '機月同梁' in locked_structure['核心格局']:
        return False, '回應提到了錯誤的格局'
    
    return True, None
```

---

## 未來擴展

### 1. 多版本命盤

允許用戶保存多個命盤版本（如不同時辰的可能性），可切換比較。

### 2. 命盤分享

生成唯一連結，讓用戶分享命盤給朋友或命理師確認。

### 3. 大師審核模式

付費用戶可以邀請真人命理師審核鎖定的命盤結構。

### 4. 時空校正

整合天文曆法資料，提供更精確的時辰判定（考慮真太陽時）。

---

## 測試檢查清單

- [ ] 首次分析能正確提取結構
- [ ] 鎖定後的結構能正確注入後續對話
- [ ] 重新定盤功能正常運作
- [ ] 多用戶隔離（不會拿到別人的命盤）
- [ ] 版本控制（歷史版本可追溯）
- [ ] 錯誤檢測能捕捉 LLM 偏離
- [ ] 前端確認流程直覺易用

---

## 結論

定盤系統是 Aetheria LLM-First 策略的核心保險機制。通過「首次確認 + 結構鎖定 + Prompt 注入」的三重機制，確保命理分析的一致性和準確性。

**下一步**：實作 MVP（最小可行產品），先完成單用戶的定盤流程。
