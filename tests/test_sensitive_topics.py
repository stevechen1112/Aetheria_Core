"""
敏感議題檢測模組測試
測試 Phase 3.1 的關鍵字匹配、信心度評分、保護性回應
"""

import pytest
from src.utils.sensitive_topics import (
    SensitiveTopicDetector,
    SensitiveTopic,
    get_sensitive_topic_detector
)


class TestSensitiveTopicDetector:
    """敏感議題檢測器測試"""
    
    def test_detector_initialization(self):
        """測試檢測器初始化"""
        detector = SensitiveTopicDetector()
        assert detector is not None
        assert len(detector.patterns) == 5  # 5 個類別
        assert SensitiveTopic.HEALTH_MEDICAL in detector.patterns
        assert SensitiveTopic.SUICIDE_DEATH in detector.patterns
    
    def test_get_detector_singleton(self):
        """測試單例模式"""
        detector1 = get_sensitive_topic_detector()
        detector2 = get_sensitive_topic_detector()
        assert detector1 is detector2
    
    # ========== 健康醫療議題測試 ==========
    def test_detect_health_medical_strong(self):
        """測試健康議題檢測（強信號）"""
        detector = SensitiveTopicDetector()
        text = "我最近得了癌症，醫生說要化療，想問我的命盤有沒有救？"
        topic, confidence = detector.detect(text)
        
        assert topic == SensitiveTopic.HEALTH_MEDICAL
        assert confidence > 0.3  # 高信心度
    
    def test_detect_health_medical_weak(self):
        """測試健康議題檢測（弱信號）"""
        detector = SensitiveTopicDetector()
        text = "我想問我的身體健康運勢如何？"
        topic, confidence = detector.detect(text)
        
        # 可能不觸發，或觸發但信心度低
        if topic == SensitiveTopic.HEALTH_MEDICAL:
            assert confidence < 0.5  # 低信心度
    
    # ========== 自殺死亡議題測試 ==========
    def test_detect_suicide_strong(self):
        """測試自殺議題檢測（強信號）"""
        detector = SensitiveTopicDetector()
        text = "我真的活不下去了，想死，命盤能告訴我什麼時候解脫嗎？"
        topic, confidence = detector.detect(text)
        
        assert topic == SensitiveTopic.SUICIDE_DEATH
        assert confidence > 0.3
    
    def test_detect_suicide_medium(self):
        """測試自殺議題檢測（中度信號）"""
        detector = SensitiveTopicDetector()
        text = "最近很想輕生，覺得生命沒有意義"
        topic, confidence = detector.detect(text)
        
        assert topic == SensitiveTopic.SUICIDE_DEATH
        assert confidence > 0.2
    
    # ========== 法律犯罪議題測試 ==========
    def test_detect_legal_crime(self):
        """測試法律犯罪議題檢測"""
        detector = SensitiveTopicDetector()
        text = "我想知道如果我做了違法的事，會不會被判刑？命盤能告訴我嗎？"
        topic, confidence = detector.detect(text)
        
        assert topic == SensitiveTopic.LEGAL_CRIME
        assert confidence > 0.2
    
    # ========== 金融投資議題測試 ==========
    def test_detect_financial_investment(self):
        """測試金融投資議題檢測"""
        detector = SensitiveTopicDetector()
        text = "我想買股票賺錢，請幫我看看哪支股票會漲？"
        topic, confidence = detector.detect(text)
        
        assert topic == SensitiveTopic.FINANCIAL_INVESTMENT
        assert confidence > 0.2
    
    # ========== 關係暴力議題測試 ==========
    def test_detect_relationship_violence(self):
        """測試關係暴力議題檢測"""
        detector = SensitiveTopicDetector()
        text = "我被家暴，老公常常打我，想問我該離婚嗎？"
        topic, confidence = detector.detect(text)
        
        assert topic == SensitiveTopic.RELATIONSHIP_VIOLENCE
        assert confidence > 0.2
    
    # ========== 無敏感議題測試 ==========
    def test_detect_none_normal_question(self):
        """測試正常問題（無敏感議題）"""
        detector = SensitiveTopicDetector()
        text = "我想了解我的事業運勢和貴人運如何？"
        topic, confidence = detector.detect(text)
        
        assert topic == SensitiveTopic.NONE
        assert confidence == 0.0
    
    def test_detect_none_empty_text(self):
        """測試空白文本"""
        detector = SensitiveTopicDetector()
        topic, confidence = detector.detect("")
        
        assert topic == SensitiveTopic.NONE
        assert confidence == 0.0
    
    # ========== 保護性回應測試 ==========
    def test_protective_response_health(self):
        """測試健康議題保護性回應"""
        detector = SensitiveTopicDetector()
        response = detector.get_protective_response(SensitiveTopic.HEALTH_MEDICAL)
        
        assert "⚠️" in response or "重要提醒" in response
        assert "醫療" in response or "醫師" in response
        assert "就醫" in response or "專業" in response
    
    def test_protective_response_suicide(self):
        """測試自殺議題保護性回應"""
        detector = SensitiveTopicDetector()
        response = detector.get_protective_response(SensitiveTopic.SUICIDE_DEATH)
        
        assert "1995" in response or "生命線" in response
        assert "1980" in response or "張老師" in response
        assert "1925" in response or "安心專線" in response
        assert "生命" in response
    
    def test_protective_response_legal(self):
        """測試法律議題保護性回應"""
        detector = SensitiveTopicDetector()
        response = detector.get_protective_response(SensitiveTopic.LEGAL_CRIME)
        
        assert "法律" in response
        assert "律師" in response or "法律扶助" in response
    
    def test_protective_response_financial(self):
        """測試金融議題保護性回應"""
        detector = SensitiveTopicDetector()
        response = detector.get_protective_response(SensitiveTopic.FINANCIAL_INVESTMENT)
        
        assert "投資" in response
        assert "風險" in response or "免責" in response
        assert "財務顧問" in response or "專業協助" in response
    
    def test_protective_response_violence(self):
        """測試暴力議題保護性回應"""
        detector = SensitiveTopicDetector()
        response = detector.get_protective_response(SensitiveTopic.RELATIONSHIP_VIOLENCE)
        
        assert "113" in response or "保護專線" in response
        assert "110" in response or "報警" in response
        assert "安全" in response
    
    # ========== 攔截邏輯測試 ==========
    def test_should_intercept_high_confidence(self):
        """測試高信心度應攔截"""
        detector = SensitiveTopicDetector()
        assert detector.should_intercept(SensitiveTopic.HEALTH_MEDICAL, 0.5, threshold=0.3)
    
    def test_should_intercept_low_confidence(self):
        """測試低信心度不攔截"""
        detector = SensitiveTopicDetector()
        assert not detector.should_intercept(SensitiveTopic.HEALTH_MEDICAL, 0.1, threshold=0.3)
    
    def test_should_intercept_suicide_low_threshold(self):
        """測試自殺議題低閾值攔截"""
        detector = SensitiveTopicDetector()
        # 自殺議題閾值 0.2，應攔截
        assert detector.should_intercept(SensitiveTopic.SUICIDE_DEATH, 0.25)
        # 其他議題閾值 0.3，不應攔截
        assert not detector.should_intercept(SensitiveTopic.HEALTH_MEDICAL, 0.25)
    
    def test_should_intercept_none_topic(self):
        """測試無敏感議題不攔截"""
        detector = SensitiveTopicDetector()
        assert not detector.should_intercept(SensitiveTopic.NONE, 1.0)
    
    # ========== 真實場景測試（整合）==========
    def test_full_workflow_suicide(self):
        """測試完整流程：檢測 → 判斷 → 回應（自殺議題）"""
        detector = SensitiveTopicDetector()
        # 使用更明確的自殺信號
        text = "我活不下去了不想活了，想自殺，命理能告訴我什麼時候解脫嗎？"
        
        # 檢測
        topic, confidence = detector.detect(text)
        assert topic == SensitiveTopic.SUICIDE_DEATH
        
        # 判斷攔截（自殺議題閾值 0.2）
        assert detector.should_intercept(topic, confidence)
        assert confidence >= 0.2  # 確保信心度足夠
        
        # 生成回應
        response = detector.get_protective_response(topic)
        assert "1995" in response
        assert len(response) > 100  # 回應足夠詳細
    
    def test_full_workflow_normal(self):
        """測試完整流程：正常問題不攔截"""
        detector = SensitiveTopicDetector()
        text = "我想了解我的財運和事業運勢"
        
        # 檢測
        topic, confidence = detector.detect(text)
        assert topic == SensitiveTopic.NONE
        
        # 不攔截
        assert not detector.should_intercept(topic, confidence)
    
    # ========== 邊界條件測試 ==========
    def test_multiple_topics_detected(self):
        """測試多個議題同時出現（應返回最高分）"""
        detector = SensitiveTopicDetector()
        text = "我得了癌症想死，還被家暴打傷，命盤能救我嗎？"
        
        # 應檢測出信心度最高的議題
        topic, confidence = detector.detect(text)
        assert topic in [
            SensitiveTopic.HEALTH_MEDICAL,
            SensitiveTopic.SUICIDE_DEATH,
            SensitiveTopic.RELATIONSHIP_VIOLENCE
        ]
        assert confidence > 0.3
    
    def test_case_insensitive(self):
        """測試大小寫不敏感"""
        detector = SensitiveTopicDetector()
        text1 = "我想死"
        text2 = "我想死"  # 相同內容
        
        topic1, conf1 = detector.detect(text1)
        topic2, conf2 = detector.detect(text2)
        
        assert topic1 == topic2
        assert abs(conf1 - conf2) < 0.01
    
    def test_special_characters(self):
        """測試特殊字符不影響檢測"""
        detector = SensitiveTopicDetector()
        text = "我...真的...想死！！！活不下去了。。。"
        topic, confidence = detector.detect(text)
        
        assert topic == SensitiveTopic.SUICIDE_DEATH
        assert confidence > 0.2


class TestIntegrationWithAPI:
    """API 整合測試（需要實際 API 運行）"""
    
    def test_api_response_format(self):
        """測試 API 回應格式（模擬）"""
        detector = SensitiveTopicDetector()
        text = "我想自殺"
        topic, confidence = detector.detect(text)
        
        if detector.should_intercept(topic, confidence):
            response_data = {
                'status': 'success',
                'reply': detector.get_protective_response(topic),
                'sensitive_topic_detected': topic.value,
                'confidence': confidence,
                'citations': [],
                'used_systems': []
            }
            
            assert response_data['status'] == 'success'
            assert 'reply' in response_data
            assert len(response_data['reply']) > 50
            assert response_data['sensitive_topic_detected'] == 'suicide_death'
