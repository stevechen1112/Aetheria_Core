import sqlite3

conn = sqlite3.connect('data/aetheria.db')
cur = conn.cursor()

# 查询用户资料
cur.execute('''
    SELECT user_id, name, birth_year, birth_month, birth_day, 
           birth_hour, birth_minute, birth_location 
    FROM users 
    WHERE user_id LIKE ?
''', ('%0cd3e7eb%',))

row = cur.fetchone()
if row:
    print(f'用户ID: {row[0][:20]}...')
    print(f'姓名: {row[1]}')
    print(f'出生: {row[2]}-{row[3]}-{row[4]} {row[5]}:{row[6]}')
    print(f'地点: {row[7]}')
else:
    print('找不到用户资料')

# 查看所有用户
cur.execute('SELECT user_id, name FROM users')
all_users = cur.fetchall()
print(f'\n数据库中共有 {len(all_users)} 个用户')
for user in all_users:
    print(f'  - {user[0][:20]}... ({user[1]})')

conn.close()
