# 戰略側寫 API（v1.9.0）

本文件提供兩個新端點的簡化範例資料與測試用例（不包含回傳內容）。

## 1) 全息側寫

### Endpoint
POST /api/strategic/profile

### 範例 Payload
```json
{
  "birth_date": "1979-11-12",
  "birth_time": "23:58",
  "chinese_name": "陳宥竹",
  "english_name": "CHEN YOU ZHU",
  "gender": "男",
  "analysis_focus": "career",
  "include_bazi": true,
  "include_astrology": true,
  "include_tarot": true,
  "longitude": 120.54,
  "latitude": 24.08,
  "timezone": "Asia/Taipei",
  "city": "Changhua",
  "nation": "TW"
}
```

### 測試重點
- 未提供 `birth_time` 時，應回傳 `warnings` 且略過八字/占星。
- `analysis_focus` 可測 `general/career/relationship/wealth/health`。

---

## 2) 生辰校正

### Endpoint
POST /api/strategic/birth-rectify

### 範例 Payload
```json
{
  "birth_date": "1979-11-12",
  "gender": "男",
  "traits": [
    "強勢領導",
    "偏好獨立作業",
    "重大轉職"
  ],
  "longitude": 120.54
}
```

### 測試重點
- `traits` 為必填且至少 1 條。
- 應回傳 12 時辰候選摘要與 Top 3 推薦。
