"""查看並刪除報告"""
import sqlite3
import json

conn = sqlite3.connect('data/aetheria.db')
cursor = conn.cursor()

user_id = 'a5833e2756dd4354b53472bf73004789'

# 查看報告
cursor.execute("SELECT system_type, updated_at FROM system_reports WHERE user_id = ?", (user_id,))
rows = cursor.fetchall()
print("目前報告:")
for r in rows:
    print(f"  {r[0]}: {r[1]}")

conn.close()
