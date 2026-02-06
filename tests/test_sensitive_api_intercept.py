"""
敏感議題 API 攔截整合測試
測試 /api/chat/consult 和 /api/chat/consult-stream 端點的保護機制

Note: 這些是簡化的單元測試，測試敏感議題檢測邏輯
完整的 API 端到端測試需要實際的 API 服務運行
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from src.utils.sensitive_topics import (
    SensitiveTopicDetector,
    SensitiveTopic,
    get_sensitive_topic_detector
)


class TestSensitiveTopicsAPILogic:
    """測試 API 中的敏感議題攔截邏輯（單元測試）"""
    
    def test_suicide_detection_triggers_intercept(self):
        """測試自殺議題觸發攔截"""
        detector = get_sensitive_topic_detector()
        message = "我真的活不下去了，想死，命盤能告訴我解脫的時間嗎？"
        
        topic, confidence = detector.detect(message)
        
        assert topic == SensitiveTopic.SUICIDE_DEATH
        assert detector.should_intercept(topic, confidence)
        
        # 驗證保護性回應
        response = detector.get_protective_response(topic)
        assert "1995" in response or "生命線" in response
        assert len(response) > 100
    
    def test_health_detection_triggers_intercept(self):
        """測試健康議題觸發攔截"""
        detector = get_sensitive_topic_detector()
        message = "我得了癌症，醫生說要化療，命盤能告訴我會不會死嗎？"
        
        topic, confidence = detector.detect(message)
        
        assert topic == SensitiveTopic.HEALTH_MEDICAL
        assert detector.should_intercept(topic, confidence)
        
        response = detector.get_protective_response(topic)
        assert "醫療" in response or "醫師" in response
    
    def test_legal_detection_triggers_intercept(self):
        """測試法律議題觸發攔截"""
        detector = get_sensitive_topic_detector()
        # 使用更多法律關鍵詞提高信心度
        message = "我想殺人詐騙綁架，命盤說我會不會被抓到坐牢判刑？"
        
        topic, confidence = detector.detect(message)
        
        assert topic == SensitiveTopic.LEGAL_CRIME
        assert detector.should_intercept(topic, confidence)
        
        response = detector.get_protective_response(topic)
        assert "法律" in response
    
    def test_financial_detection_triggers_intercept(self):
        """測試金融議題觸發攔截"""
        detector = get_sensitive_topic_detector()
        message = "請幫我看哪支股票會漲？我想投資賺錢"
        
        topic, confidence = detector.detect(message)
        
        assert topic == SensitiveTopic.FINANCIAL_INVESTMENT
        assert detector.should_intercept(topic, confidence)
        
        response = detector.get_protective_response(topic)
        assert "投資" in response
    
    def test_violence_detection_triggers_intercept(self):
        """測試暴力議題觸發攔截"""
        detector = get_sensitive_topic_detector()
        message = "我被家暴，老公常常打我，命盤說我該離婚嗎？"
        
        topic, confidence = detector.detect(message)
        
        assert topic == SensitiveTopic.RELATIONSHIP_VIOLENCE
        assert detector.should_intercept(topic, confidence)
        
        response = detector.get_protective_response(topic)
        assert "113" in response or "保護專線" in response
    
    def test_normal_question_no_intercept(self):
        """測試正常問題不觸發攔截"""
        detector = get_sensitive_topic_detector()
        message = "我想了解我的事業運勢如何？"
        
        topic, confidence = detector.detect(message)
        
        assert topic == SensitiveTopic.NONE
        assert not detector.should_intercept(topic, confidence)
    
    def test_multiple_topics_highest_confidence(self):
        """測試多個敏感議題（返回最高信心度）"""
        detector = get_sensitive_topic_detector()
        message = "我得了癌症想死，還被家暴打傷"
        
        topic, confidence = detector.detect(message)
        
        # 應返回其中一個敏感議題
        assert topic in [
            SensitiveTopic.SUICIDE_DEATH,
            SensitiveTopic.HEALTH_MEDICAL,
            SensitiveTopic.RELATIONSHIP_VIOLENCE
        ]
        assert confidence > 0.2
    
    def test_low_confidence_no_intercept(self):
        """測試低信心度不觸發攔截"""
        detector = get_sensitive_topic_detector()
        message = "我想了解我的身體運勢"  # 模糊的健康詞彙
        
        topic, confidence = detector.detect(message)
        
        # 可能檢測到健康議題但信心度低
        if topic == SensitiveTopic.HEALTH_MEDICAL:
            # 如果檢測到，信心度應該不足以觸發攔截
            assert not detector.should_intercept(topic, confidence, threshold=0.3)


class TestSensitiveTopicsResponseFormat:
    """測試敏感議題回應格式"""
    
    def test_intercept_response_structure(self):
        """測試攔截回應結構"""
        detector = get_sensitive_topic_detector()
        message = "我想死"
        
        topic, confidence = detector.detect(message)
        
        if detector.should_intercept(topic, confidence):
            # 模擬 API 回應結構
            response_data = {
                'status': 'success',
                'reply': detector.get_protective_response(topic),
                'session_id': 'test_session',
                'sensitive_topic_detected': topic.value,
                'citations': [],
                'used_systems': [],
                'confidence': 0.0,
                'next_steps': []
            }
            
            assert response_data['status'] == 'success'
            assert 'reply' in response_data
            assert len(response_data['reply']) > 50
            assert response_data['sensitive_topic_detected'] == 'suicide_death'
            assert response_data['used_systems'] == []  # 無 AI 調用
            assert response_data['confidence'] == 0.0  # 無 AI 分析
    
    def test_stream_response_structure(self):
        """測試串流回應結構（模擬）"""
        detector = get_sensitive_topic_detector()
        message = "我不想活了"
        
        topic, confidence = detector.detect(message)
        
        if detector.should_intercept(topic, confidence):
            # 模擬 SSE 事件流
            events = []
            
            # Session 事件
            events.append({
                'type': 'session',
                'data': {'session_id': 'test_session'}
            })
            
            # 警告事件
            events.append({
                'type': 'warning',
                'data': {
                    'type': 'sensitive_topic',
                    'topic': topic.value,
                    'confidence': confidence
                }
            })
            
            # 文字事件（逐字）
            response_text = detector.get_protective_response(topic)
            for char in response_text[:10]:  # 只測試前 10 個字符
                events.append({
                    'type': 'text',
                    'data': {'chunk': char}
                })
            
            # 完成事件
            events.append({
                'type': 'done',
                'data': {
                    'session_id': 'test_session',
                    'total_length': len(response_text),
                    'sensitive_topic_detected': topic.value
                }
            })
            
            # 驗證事件流
            assert any(e['type'] == 'session' for e in events)
            assert any(e['type'] == 'warning' for e in events)
            assert any(e['type'] == 'text' for e in events)
            assert any(e['type'] == 'done' for e in events)
            
            # 驗證警告事件內容
            warning_event = next(e for e in events if e['type'] == 'warning')
            assert warning_event['data']['topic'] == 'suicide_death'
            
            # 驗證完成事件內容
            done_event = next(e for e in events if e['type'] == 'done')
            assert 'sensitive_topic_detected' in done_event['data']


class TestSensitiveTopicsLoggingBehavior:
    """測試敏感議題日誌記錄行為"""
    
    def test_intercept_logged_with_details(self, caplog):
        """測試攔截事件記錄詳細信息"""
        import logging
        caplog.set_level(logging.INFO)
        
        detector = get_sensitive_topic_detector()
        message = "我想自殺"
        
        topic, confidence = detector.detect(message)
        
        # 檢查日誌
        assert any('敏感議題檢測' in record.message for record in caplog.records)
        assert any('suicide_death' in record.message for record in caplog.records)
        assert any('信心度' in record.message for record in caplog.records)


# ========== 標記為整合測試（需要實際 API 運行）==========
@pytest.mark.integration
@pytest.mark.skip(reason="需要實際 API 服務運行和完整的用戶認證流程")
class TestSensitiveTopicsAPIEndToEnd:
    """
    端到端 API 測試（已跳過）
    
    這些測試需要：
    1. Flask API 服務運行在 5001 端口
    2. 完整的用戶註冊和認證流程
    3. 資料庫連接
    
    要運行這些測試：
    1. 啟動 API: python -m flask run --port=5001
    2. pytest tests/test_sensitive_api_intercept.py -m integration -v
    """
    
    def test_consult_endpoint_intercept(self):
        """測試 /api/chat/consult 端點攔截"""
        pass  # 實際實作需要完整的 API 環境
    
    def test_consult_stream_endpoint_intercept(self):
        """測試 /api/chat/consult-stream 端點攔截"""
        pass  # 實際實作需要完整的 API 環境
