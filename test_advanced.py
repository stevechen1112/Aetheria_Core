"""
測試 Aetheria 進階功能
- 合盤分析（婚配/合夥）
- 擇日功能（婚嫁/開業/搬家）
"""

import requests
import json

BASE_URL = 'http://localhost:5000'

def test_synastry_marriage():
    """測試婚配合盤"""
    print("\n" + "="*60)
    print("【測試 1】婚配合盤分析")
    print("="*60)
    
    response = requests.post(
        f'{BASE_URL}/api/synastry/marriage',
        json={
            'user_a_id': 'test_user_001',
            'user_b_id': 'test_user_002'
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ 對象 A: {result['user_a_id']}")
        print(f"✓ 對象 B: {result['user_b_id']}")
        print(f"✓ 分析類型: {result['analysis_type']}")
        print(f"\n✓ 分析結果:")
        print("-" * 60)
        # 只顯示前 1000 字
        analysis = result['analysis']
        print(analysis[:1000] if len(analysis) > 1000 else analysis)
        if len(analysis) > 1000:
            print("\n... (後續內容省略) ...")
        print("-" * 60)
    else:
        print(f"✗ 錯誤: {response.text}")


def test_synastry_partnership():
    """測試合夥合盤"""
    print("\n" + "="*60)
    print("【測試 2】合夥關係分析")
    print("="*60)
    
    response = requests.post(
        f'{BASE_URL}/api/synastry/partnership',
        json={
            'user_a_id': 'test_user_001',
            'user_b_id': 'test_user_002',
            'partnership_info': '計劃合作開設 AI 命理諮詢工作室，預計投資 500 萬，股權分配未定'
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ 合夥人 A: {result['user_a_id']}")
        print(f"✓ 合夥人 B: {result['user_b_id']}")
        print(f"✓ 合夥項目: {result['partnership_info']}")
        print(f"\n✓ 分析結果:")
        print("-" * 60)
        analysis = result['analysis']
        print(analysis[:1000] if len(analysis) > 1000 else analysis)
        if len(analysis) > 1000:
            print("\n... (後續內容省略) ...")
        print("-" * 60)
    else:
        print(f"✗ 錯誤: {response.text}")


def test_synastry_quick():
    """測試快速合盤"""
    print("\n" + "="*60)
    print("【測試 3】快速合盤評估")
    print("="*60)
    
    response = requests.post(
        f'{BASE_URL}/api/synastry/quick',
        json={
            'user_a_id': 'test_user_001',
            'user_b_id': 'test_user_002',
            'analysis_type': '婚配'
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ 對象 A: {result['user_a_id']}")
        print(f"✓ 對象 B: {result['user_b_id']}")
        print(f"✓ 評估類型: {result['analysis_type']}")
        print(f"\n✓ 快速評估:")
        print("-" * 60)
        print(result['analysis'])
        print("-" * 60)
    else:
        print(f"✗ 錯誤: {response.text}")


def test_date_selection_marriage():
    """測試婚嫁擇日"""
    print("\n" + "="*60)
    print("【測試 4】婚嫁擇日")
    print("="*60)
    
    response = requests.post(
        f'{BASE_URL}/api/date-selection/marriage',
        json={
            'groom_id': 'test_user_001',
            'bride_id': 'test_user_002',
            'target_year': 2026,
            'preferred_months': '5月、6月、10月',
            'avoid_dates': '週一至週五',
            'other_requirements': '希望選在週末，便於親友參加'
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ 新郎: {result['groom_id']}")
        print(f"✓ 新娘: {result['bride_id']}")
        print(f"✓ 目標年份: {result['target_year']}")
        print(f"\n✓ 擇日分析:")
        print("-" * 60)
        analysis = result['analysis']
        print(analysis[:1200] if len(analysis) > 1200 else analysis)
        if len(analysis) > 1200:
            print("\n... (後續內容省略) ...")
        print("-" * 60)
    else:
        print(f"✗ 錯誤: {response.text}")


def test_date_selection_business():
    """測試開業擇日"""
    print("\n" + "="*60)
    print("【測試 5】開業擇日")
    print("="*60)
    
    response = requests.post(
        f'{BASE_URL}/api/date-selection/business',
        json={
            'owner_id': 'test_user_001',
            'target_year': 2026,
            'business_type': 'AI 命理諮詢工作室',
            'business_nature': '服務業',
            'business_direction': '東方',
            'preferred_months': '3月、4月、9月',
            'other_requirements': '希望選在週末開幕，方便舉辦開幕活動'
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ 負責人: {result['owner_id']}")
        print(f"✓ 目標年份: {result['target_year']}")
        print(f"✓ 事業類型: {result['business_type']}")
        print(f"\n✓ 擇日分析:")
        print("-" * 60)
        analysis = result['analysis']
        print(analysis[:1200] if len(analysis) > 1200 else analysis)
        if len(analysis) > 1200:
            print("\n... (後續內容省略) ...")
        print("-" * 60)
    else:
        print(f"✗ 錯誤: {response.text}")


def test_date_selection_moving():
    """測試搬家擇日"""
    print("\n" + "="*60)
    print("【測試 6】搬家入宅擇日")
    print("="*60)
    
    response = requests.post(
        f'{BASE_URL}/api/date-selection/moving',
        json={
            'owner_id': 'test_user_001',
            'target_year': 2026,
            'new_address': '台北市大安區',
            'new_direction': '東北方（相對於舊居）',
            'house_orientation': '坐北朝南',
            'number_of_people': 3,
            'family_members': '宅主、配偶、一名子女',
            'preferred_months': '2月、3月、11月',
            'other_requirements': '希望避開農曆七月，選在週末搬遷'
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ 宅主: {result['owner_id']}")
        print(f"✓ 目標年份: {result['target_year']}")
        print(f"✓ 新居地址: {result['new_address']}")
        print(f"\n✓ 擇日分析:")
        print("-" * 60)
        analysis = result['analysis']
        print(analysis[:1200] if len(analysis) > 1200 else analysis)
        if len(analysis) > 1200:
            print("\n... (後續內容省略) ...")
        print("-" * 60)
    else:
        print(f"✗ 錯誤: {response.text}")


def setup_test_users():
    """設置測試用戶（假設已經完成定盤）"""
    print("\n" + "="*60)
    print("準備測試環境")
    print("="*60)
    print("\n注意：此測試假設以下用戶已完成定盤：")
    print("  - test_user_001 (農曆68年9月23日 23:58, 台灣彰化市, 男)")
    print("  - test_user_002 (需要另外創建)")
    print("\n如果這些用戶尚未定盤，請先執行 test_client.py 完成定盤。")
    input("\n按 Enter 繼續測試...")


def main():
    """主測試流程"""
    print("="*60)
    print("Aetheria 進階功能測試")
    print("="*60)
    
    setup_test_users()
    
    # 測試選單
    while True:
        print("\n" + "="*60)
        print("請選擇測試項目：")
        print("="*60)
        print("1. 婚配合盤分析")
        print("2. 合夥關係分析")
        print("3. 快速合盤評估")
        print("4. 婚嫁擇日")
        print("5. 開業擇日")
        print("6. 搬家入宅擇日")
        print("7. 執行所有測試")
        print("0. 退出")
        print("="*60)
        
        choice = input("\n請輸入選項 (0-7): ").strip()
        
        if choice == '1':
            test_synastry_marriage()
        elif choice == '2':
            test_synastry_partnership()
        elif choice == '3':
            test_synastry_quick()
        elif choice == '4':
            test_date_selection_marriage()
        elif choice == '5':
            test_date_selection_business()
        elif choice == '6':
            test_date_selection_moving()
        elif choice == '7':
            print("\n執行所有測試...")
            test_synastry_marriage()
            input("\n按 Enter 繼續下一個測試...")
            test_synastry_partnership()
            input("\n按 Enter 繼續下一個測試...")
            test_synastry_quick()
            input("\n按 Enter 繼續下一個測試...")
            test_date_selection_marriage()
            input("\n按 Enter 繼續下一個測試...")
            test_date_selection_business()
            input("\n按 Enter 繼續下一個測試...")
            test_date_selection_moving()
            print("\n" + "="*60)
            print("所有測試完成！")
            print("="*60)
        elif choice == '0':
            print("\n感謝使用 Aetheria 測試工具！")
            break
        else:
            print("\n✗ 無效的選項，請重新輸入")


if __name__ == '__main__':
    main()
