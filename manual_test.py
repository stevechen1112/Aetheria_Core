import requests
import json

def test():
    url = 'http://localhost:5001/api/fortune/annual'
    payload = {'user_id': 'test_user_001', 'target_year': 2026}
    try:
        r = requests.post(url, json=payload, timeout=120)
        print(f"Status: {r.status_code}")
        data = r.json()
        print(f"Keys: {list(data.keys())}")
        analysis = data.get('analysis')
        print(f"Analysis type: {type(analysis)}")
        if analysis is None:
            print("Analysis is None!")
        else:
            print(f"Analysis length: {len(analysis)}")
            print("Preview:")
            print(analysis[:200])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test()
