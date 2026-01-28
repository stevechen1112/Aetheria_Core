"""單獨重新生成紫微斗數報告"""
import requests
import sqlite3

user_id = 'a5833e2756dd4354b53472bf73004789'

# 先刪除現有的紫微報告
conn = sqlite3.connect('data/aetheria.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM system_reports WHERE user_id = ? AND system_type = 'ziwei'", (user_id,))
deleted = cursor.rowcount
conn.commit()
conn.close()
print(f"已刪除 {deleted} 筆紫微報告")

# 重新生成
print("\n正在重新生成紫微斗數報告（約需 1-2 分鐘）...")
data = {
    "user_id": user_id,
    "chinese_name": "陳宥竹",
    "birth_date": "1979-11-12",
    "birth_time": "23:58",
    "birth_location": "彰化縣",
    "gender": "男",
    "force_regenerate": True
}

try:
    response = requests.post(
        "http://localhost:5001/api/profile/save-and-analyze",
        json=data,
        timeout=300
    )
    result = response.json()
    print(f"\n結果: {result.get('status')}")
    print(f"已生成: {result.get('reports_generated')}")
    
    # 檢查報告長度
    r = requests.get(f"http://localhost:5001/api/reports/get?user_id={user_id}&system=ziwei", timeout=10)
    report = r.json()
    if report.get('found'):
        length = len(report.get('report', {}).get('analysis', ''))
        print(f"\n紫微報告長度: {length} 字元")
        if length > 3000:
            print("✅ 報告完整")
        else:
            print("⚠️ 報告可能不完整")
except Exception as e:
    print(f"錯誤: {e}")
