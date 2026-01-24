"""
自動將 server.py 中的舊 genai API 替換為新的 gemini_client
"""

import re

def migrate_genai_calls(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 模式 1: 簡單的兩行模式
    # model = genai.GenerativeModel('xxx')
    # response = model.generate_content(prompt)
    pattern1 = r"(\s+)model = genai\.GenerativeModel\(['\"]([^'\"]+)['\"]\)\s+(\w+) = model\.generate_content\(([^)]+)\)"
    
    def replace1(match):
        indent = match.group(1)
        model_name = match.group(2)
        var_name = match.group(3)
        prompt_var = match.group(4)
        return f"{indent}{var_name} = gemini_client.generate({prompt_var})"
    
    content = re.sub(pattern1, replace1, content)
    
    # 模式 2: 帶 MODEL_NAME 常數的
    pattern2 = r"(\s+)model = genai\.GenerativeModel\(MODEL_NAME\)\s+(\w+) = model\.generate_content\(([^)]+)\)"
    
    def replace2(match):
        indent = match.group(1)
        var_name = match.group(2)
        prompt_var = match.group(3)
        return f"{indent}{var_name} = gemini_client.generate({prompt_var})"
    
    content = re.sub(pattern2, replace2, content)
    
    # 模式 3: 多行的 GenerativeModel 創建（帶參數）
    # 這種情況下我們只替換 generate_content 呼叫
    content = re.sub(
        r"(\s+)model = genai\.GenerativeModel\(",
        r"\1# model = genai.GenerativeModel(  # 已遷移到 gemini_client\n\1# 以下使用 gemini_client.generate() 替代\n\1_unused_model = genai.GenerativeModel(",
        content
    )
    
    # 檢查是否有變更
    if content != original_content:
        # 備份原始檔案
        backup_path = filepath + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"✅ 原始檔案已備份到: {backup_path}")
        
        # 寫入新內容
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 已更新檔案: {filepath}")
        print(f"   總共進行了 {len(re.findall('gemini_client.generate', content))} 處替換")
    else:
        print("ℹ️  沒有找到需要替換的模式")

if __name__ == '__main__':
    migrate_genai_calls('src/api/server.py')
