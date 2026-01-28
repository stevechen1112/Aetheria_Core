"""單獨生成剩餘的報告"""
import requests

user_id = 'a5833e2756dd4354b53472bf73004789'
chinese_name = '陳宥竹'
birth_date = '1979-11-12'
birth_time = '23:58'
birth_location = '彰化縣'
gender = '男'

# 只生成八字
print("正在生成八字報告...")
data = {
    "user_id": user_id,
    "chinese_name": chinese_name,
    "birth_date": birth_date,
    "birth_time": birth_time,
    "birth_location": birth_location,
    "gender": gender,
    "available_systems": ["bazi"],
    "force_regenerate": True
}

try:
    response = requests.post(
        "http://localhost:5001/api/profile/save-and-analyze",
        json=data,
        timeout=600
    )
    result = response.json()
    print(f"結果: {result.get('reports_generated')}")
except Exception as e:
    print(f"錯誤: {e}")
