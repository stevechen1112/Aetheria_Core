"""刪除報告並重新生成"""
import sqlite3

conn = sqlite3.connect('data/aetheria.db')
cursor = conn.cursor()

user_id = 'a5833e2756dd4354b53472bf73004789'

# 刪除報告
cursor.execute("DELETE FROM system_reports WHERE user_id = ?", (user_id,))
deleted = cursor.rowcount
conn.commit()
conn.close()

print(f"已刪除 {deleted} 筆報告")
print("請使用前端重新生成，或呼叫 API 重新生成")
