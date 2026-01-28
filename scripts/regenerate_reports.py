"""從 users.json 復原用戶資料並重新生成報告"""
import json
import requests

# 直接使用已知的 chen_youzhu 資料
user_id = 'a5833e2756dd4354b53472bf73004789'
chinese_name = '陳宥竹'
birth_date = '1979-11-12'
birth_time = '23:58'
birth_location = '彰化縣'
gender = '男'

print(f"用戶: {chinese_name}")
print(f"  生日: {birth_date}")
print(f"  時間: {birth_time}")
print(f"  地點: {birth_location}")
print(f"  性別: {gender}")

# 呼叫 API 重新生成報告
print("\n正在重新生成報告（約需 3-5 分鐘）...")
data = {
    "user_id": user_id,
    "chinese_name": chinese_name,
    "birth_date": birth_date,
    "birth_time": birth_time,
    "birth_location": birth_location,
    "gender": gender,
    "force_regenerate": True
}

response = requests.post(
    "http://localhost:5001/api/profile/save-and-analyze",
    json=data,
    timeout=600
)

result = response.json()
print(f"\n結果: {result.get('status')}")
print(f"已生成報告: {result.get('reports_generated')}")
print(f"耗時: {result.get('total_time_seconds')} 秒")
if result.get('generation_errors'):
    print(f"錯誤: {result.get('generation_errors')}")
