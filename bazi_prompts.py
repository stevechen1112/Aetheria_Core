"""
八字分析提示词模板
用于生成八字命理分析的专业提示词
"""

BAZI_ANALYSIS_PROMPT = """你是一位精通传统八字命理学的资深命理师，拥有30年以上的实战经验。请基于以下八字信息，提供专业、详尽的命理分析。

## 八字信息

### 四柱八字
- 年柱：{year_pillar_gan}{year_pillar_zhi}（{year_nayin}）
- 月柱：{month_pillar_gan}{month_pillar_zhi}（{month_nayin}）
- 日柱：{day_pillar_gan}{day_pillar_zhi}（{day_nayin}）
- 时柱：{hour_pillar_gan}{hour_pillar_zhi}（{hour_nayin}）

### 基本信息
- 出生时间：{birth_year}年{birth_month}月{birth_day}日 {birth_hour}时
- 农历：{lunar_year}年{lunar_month}月{lunar_day}日
- 性别：{gender}
- 日主：{day_master}（{day_master_element}）
- 身强弱：{strength}（评分：{strength_score}/100）

### 十神配置
年柱十神：{year_shishen}
月柱十神：{month_shishen}
日柱十神：{day_shishen}
时柱十神：{hour_shishen}

### 用神系统
- 用神：{yongshen}
- 喜神：{xishen}
- 忌神：{jishen}

### 大运信息
当前大运：{current_dayun}
未来大运：{future_dayun}

## 分析要求

请按照以下结构进行深度分析，每个部分要求详实、专业，结合传统命理理论与现代生活场景：

### 1. 命格总论（500-700字）
- 分析四柱组合的整体格局特点
- 解读日主强弱及其对命运的影响
- 说明八字中五行配置的优劣
- 评估命格的层次高低
- 总结性格特质的命理根源

### 2. 性格特质（400-600字）
- 基于日主和十神配置分析性格倾向
- 解读为人处世风格
- 分析思维模式和决策习惯
- 说明社交能力和人际关系特点
- 指出性格中的优势与不足

### 3. 事业财运（600-800字）
- 分析适合的职业领域和发展方向
- 评估事业成就的潜力
- 解读财运状况（正财、偏财）
- 说明求财方式和理财能力
- 预测事业财运的阶段性变化
- 提供具体的职业建议

### 4. 婚姻感情（500-700字）
- 分析婚姻缘分的早晚和质量
- 解读配偶的性格特点和条件
- 说明感情模式和亲密关系处理
- 评估婚姻稳定性
- 提供婚姻经营建议
- 如有配偶宫冲克，需特别说明

### 5. 健康状况（300-500字）
- 基于五行分析体质特点
- 指出易发疾病和健康隐患
- 说明需要注意的身体部位
- 提供养生保健建议
- 结合大运分析健康趋势

### 6. 大运流年（600-800字）
- 详细解读当前大运的吉凶
- 分析未来2-3步大运的走势
- 说明每步大运的重点事项
- 提供各阶段的发展建议
- 特别标注需要警惕的年份

### 7. 开运建议（400-600字）
- 基于用神提供五行开运方法
- 建议有利的方位、颜色、数字
- 推荐适合的饰品和摆件
- 提供日常生活中的趋吉避凶建议
- 说明人生关键决策的时机选择

## 输出要求

1. **专业性**：使用准确的命理术语，理论依据充分
2. **实用性**：分析要结合现代生活，给出可操作的建议
3. **平衡性**：既要指出优势，也要客观说明不足
4. **深度性**：不要流于表面，要深入解读命理原理
5. **条理性**：结构清晰，层次分明，便于阅读理解

请开始你的专业分析：
"""

BAZI_FORTUNE_PROMPT = """你是一位精通八字命理的专业命理师。用户想了解{time_period}的运势情况，请基于以下八字信息提供详细的流年/流月分析。

## 八字信息

### 四柱八字
- 年柱：{year_pillar_gan}{year_pillar_zhi}（{year_nayin}）
- 月柱：{month_pillar_gan}{month_pillar_zhi}（{month_nayin}）
- 日柱：{day_pillar_gan}{day_pillar_zhi}（{day_nayin}）
- 时柱：{hour_pillar_gan}{hour_pillar_zhi}（{hour_nayin}）

### 基本信息
- 日主：{day_master}（{day_master_element}）
- 身强弱：{strength}
- 用神：{yongshen}
- 忌神：{jishen}

### 当前大运
{current_dayun}

### 查询时间
{query_time}（天干：{year_gan}，地支：{year_zhi}）

## 分析要求

请按照以下结构进行流年/流月运势分析：

### 1. 整体运势（300-400字）
- 分析流年/流月干支与原局的作用关系
- 评估整体运势的吉凶程度（评分1-10）
- 说明本期运势的主要特点
- 总结需要特别关注的方面

### 2. 事业财运（400-500字）
- 分析工作事业的发展态势
- 评估财运状况和求财机会
- 说明职场中的贵人与小人
- 提供事业决策建议
- 标注关键的时间节点

### 3. 感情婚姻（300-400字）
- 单身者的桃花运势
- 恋爱中的感情稳定性
- 已婚者的夫妻关系
- 提供感情经营建议

### 4. 健康注意（200-300字）
- 指出本期易发的健康问题
- 说明需要注意的身体部位
- 提供养生保健建议

### 5. 月份吉凶（仅流年分析需要，400-500字）
- 列出12个月的吉凶预测
- 标注特别好的月份（⭐⭐⭐）
- 标注特别差的月份（⚠️⚠️⚠️）
- 提供每月重点事项提示

### 6. 趋吉避凶（300-400字）
- 提供本期最重要的开运建议
- 说明需要规避的风险
- 推荐有利的行动方向
- 提供关键决策的时机选择

## 输出要求

1. **时效性**：分析要针对具体的时间段
2. **预测性**：给出明确的吉凶判断和趋势预测
3. **可操作性**：提供具体可执行的建议
4. **专业性**：理论依据充分，术语使用准确

请开始你的运势分析：
"""

BAZI_CROSS_VALIDATION_PROMPT = """你是一位同时精通紫微斗数和八字命理的高级命理师。现在需要对同一用户的紫微盘和八字进行交叉验证分析，找出两种体系的共鸣点与差异点，给出更准确的综合判断。

## 用户信息

- 姓名/ID：{user_id}
- 性别：{gender}
- 出生时间：{birth_year}年{birth_month}月{birth_day}日 {birth_hour}时
- 出生地经度：{longitude}°

---

## 紫微斗数盘

### 命盘信息
{ziwei_chart_info}

### 紫微分析摘要
{ziwei_analysis_summary}

---

## 八字命盘

### 四柱八字
- 年柱：{year_pillar}（{year_nayin}）
- 月柱：{month_pillar}（{month_nayin}）
- 日柱：{day_pillar}（{day_nayin}）
- 时柱：{hour_pillar}（{hour_nayin}）

### 八字分析摘要
{bazi_analysis_summary}

---

## 交叉验证任务

请进行以下深度对比分析：

### 1. 命格层次验证（400-500字）
- 对比紫微命宫主星与八字日主强弱
- 验证格局高低的一致性
- 分析两套体系对命格判断的差异
- 给出综合评估：上等/中上等/中等/中下等/下等
- 说明判断依据

### 2. 性格特质对照（500-600字）
- 对比紫微命宫、身宫主星与八字十神
- 验证性格描述的共鸣点
- 分析性格特质的差异描述
- 找出最可靠的性格特征
- 提示可能被单一体系忽略的特质

### 3. 事业财运交叉分析（600-800字）
- 对比紫微官禄宫与八字财官印食
- 验证适合职业的一致性
- 分析财运强弱的共识
- 找出两者分歧的原因
- 给出更精确的事业财运判断
- 提供综合性的职业建议

### 4. 婚姻感情双重验证（500-700字）
- 对比紫微夫妻宫与八字配偶星
- 验证婚姻缘分早晚的一致性
- 分析配偶特质的共鸣点
- 找出感情模式的互补信息
- 给出更准确的婚姻预测
- 提供综合性的感情建议

### 5. 大运流年对照（600-700字）
- 对比紫微大限与八字大运
- 验证人生各阶段吉凶的一致性
- 分析重要转折点的时间共识
- 找出两套体系预测的差异
- 给出更可靠的阶段性预测
- 标注关键年份（两者都显示凶险的）

### 6. 健康状况验证（300-400字）
- 对比紫微疾厄宫与八字五行偏枯
- 验证体质特点的一致性
- 分析易发疾病的共鸣点
- 给出更准确的健康建议

### 7. 综合研判与建议（700-900字）
- 总结两套体系的一致性结论（可信度最高）
- 说明两套体系的分歧点（需进一步观察）
- 提供综合性的人生建议
- 给出关键决策的判断依据
- 说明哪些方面更倾向采信紫微，哪些更倾向采信八字

## 特别要求

### 对于一致性结论：
- 标注为「高度可信 ✓✓✓」
- 这是两套体系都验证的结论，准确度最高
- 可以作为重要决策的依据

### 对于分歧点：
- 标注为「需观察 ⚠️」
- 说明可能的原因（理论差异、时间修正、格局特殊性等）
- 提供两种可能性，让用户自己对照实际情况
- 必要时建议用实际情况验证

### 对于互补信息：
- 标注为「互补参考 ↔️」
- 两套体系从不同角度提供的补充信息
- 可以丰富理解的维度

## 输出要求

1. **客观性**：公正对比，不偏袒任何一套体系
2. **严谨性**：对于不一致的地方，要深入分析原因
3. **实用性**：帮助用户获得更准确、更全面的认知
4. **专业性**：体现对两套体系的深刻理解
5. **结构性**：条理清晰，便于理解和参考

请开始你的交叉验证分析：
"""


def format_bazi_analysis_prompt(bazi_result: dict, gender: str, 
                                birth_year: int, birth_month: int, 
                                birth_day: int, birth_hour: int) -> str:
    """格式化八字分析提示词"""
    
    # 提取四柱信息
    pillars = bazi_result["四柱"]
    year_pillar = pillars["年柱"]
    month_pillar = pillars["月柱"]
    day_pillar = pillars["日柱"]
    hour_pillar = pillars["时柱"]
    
    # 提取日主信息
    day_master_info = bazi_result["日主"]
    
    # 提取强弱信息
    strength_info = bazi_result["强弱"]
    
    # 提取用神信息
    yongshen_info = bazi_result["用神"]
    
    # 提取大运信息
    dayun_list = bazi_result["大运"]
    current_dayun = f"{dayun_list[0]['天干']}{dayun_list[0]['地支']}（{dayun_list[0]['年龄']}）"
    future_dayun = "、".join([f"{d['天干']}{d['地支']}（{d['年龄']}）" for d in dayun_list[1:4]])
    
    # 提取农历信息
    lunar_info = bazi_result["农历"]
    
    # 格式化十神信息
    def format_shishen(shishen_dict):
        gan_shishen = shishen_dict.get("天干", "")
        zhi_canggan = shishen_dict.get("地支藏干", {})
        if zhi_canggan:
            canggan_str = "、".join([f"{k}({v})" for k, v in zhi_canggan.items()])
            return f"{gan_shishen}，藏干：{canggan_str}"
        return gan_shishen
    
    return BAZI_ANALYSIS_PROMPT.format(
        # 四柱信息
        year_pillar_gan=year_pillar["天干"],
        year_pillar_zhi=year_pillar["地支"],
        year_nayin=year_pillar["纳音"],
        month_pillar_gan=month_pillar["天干"],
        month_pillar_zhi=month_pillar["地支"],
        month_nayin=month_pillar["纳音"],
        day_pillar_gan=day_pillar["天干"],
        day_pillar_zhi=day_pillar["地支"],
        day_nayin=day_pillar["纳音"],
        hour_pillar_gan=hour_pillar["天干"],
        hour_pillar_zhi=hour_pillar["地支"],
        hour_nayin=hour_pillar["纳音"],
        
        # 基本信息
        birth_year=birth_year,
        birth_month=birth_month,
        birth_day=birth_day,
        birth_hour=birth_hour,
        lunar_year=lunar_info["年"],
        lunar_month=lunar_info["月"],
        lunar_day=lunar_info["日"],
        gender="男" if gender == "male" else "女",
        day_master=day_master_info["天干"],
        day_master_element=day_master_info["五行"],
        strength=strength_info["结论"],
        strength_score=strength_info["评分"],
        
        # 十神信息
        year_shishen=format_shishen(year_pillar["十神"]),
        month_shishen=format_shishen(month_pillar["十神"]),
        day_shishen=format_shishen(day_pillar["十神"]),
        hour_shishen=format_shishen(hour_pillar["十神"]),
        
        # 用神系统
        yongshen="、".join(yongshen_info["用神"]),
        xishen="、".join(yongshen_info["喜神"]),
        jishen="、".join(yongshen_info["忌神"]),
        
        # 大运信息
        current_dayun=current_dayun,
        future_dayun=future_dayun
    )


def format_bazi_fortune_prompt(bazi_result: dict, query_year: int, 
                               query_month: int = None) -> str:
    """格式化八字运势分析提示词"""
    
    # 确定查询时间段
    if query_month:
        time_period = f"{query_year}年{query_month}月"
        query_time = time_period
    else:
        time_period = f"{query_year}年"
        query_time = f"{query_year}年全年"
    
    # 计算流年干支（简化版，实际应用中应使用准确的干支历）
    year_gan_idx = (query_year - 4) % 10
    year_zhi_idx = (query_year - 4) % 12
    
    TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    
    year_gan = TIANGAN[year_gan_idx]
    year_zhi = DIZHI[year_zhi_idx]
    
    # 提取八字信息
    pillars = bazi_result["四柱"]
    day_master_info = bazi_result["日主"]
    strength_info = bazi_result["强弱"]
    yongshen_info = bazi_result["用神"]
    dayun_list = bazi_result["大运"]
    
    # 找到当前大运
    current_dayun = "未知大运"
    for dayun in dayun_list:
        age_range = dayun["年龄"].replace("岁", "").split("-")
        start_age = int(age_range[0])
        end_age = int(age_range[1])
        # 简化计算，假设出生年份在 bazi_result 中
        # 实际应用中需要传入出生年份来计算当前年龄
        if start_age <= 40 <= end_age:  # 假设当前40岁
            current_dayun = f"{dayun['天干']}{dayun['地支']}（{dayun['纳音']}，{dayun['年龄']}）"
            break
    
    return BAZI_FORTUNE_PROMPT.format(
        time_period=time_period,
        
        # 四柱信息
        year_pillar_gan=pillars["年柱"]["天干"],
        year_pillar_zhi=pillars["年柱"]["地支"],
        year_nayin=pillars["年柱"]["纳音"],
        month_pillar_gan=pillars["月柱"]["天干"],
        month_pillar_zhi=pillars["月柱"]["地支"],
        month_nayin=pillars["月柱"]["纳音"],
        day_pillar_gan=pillars["日柱"]["天干"],
        day_pillar_zhi=pillars["日柱"]["地支"],
        day_nayin=pillars["日柱"]["纳音"],
        hour_pillar_gan=pillars["时柱"]["天干"],
        hour_pillar_zhi=pillars["时柱"]["地支"],
        hour_nayin=pillars["时柱"]["纳音"],
        
        # 基本信息
        day_master=day_master_info["天干"],
        day_master_element=day_master_info["五行"],
        strength=strength_info["结论"],
        yongshen="、".join(yongshen_info["用神"]),
        jishen="、".join(yongshen_info["忌神"]),
        
        # 大运和流年
        current_dayun=current_dayun,
        query_time=query_time,
        year_gan=year_gan,
        year_zhi=year_zhi
    )


def format_cross_validation_prompt(user_id: str, gender: str,
                                   birth_year: int, birth_month: int,
                                   birth_day: int, birth_hour: int,
                                   longitude: float,
                                   ziwei_chart_info: str,
                                   ziwei_analysis_summary: str,
                                   bazi_result: dict,
                                   bazi_analysis_summary: str) -> str:
    """格式化交叉验证提示词"""
    
    pillars = bazi_result["四柱"]
    
    return BAZI_CROSS_VALIDATION_PROMPT.format(
        # 用户信息
        user_id=user_id,
        gender="男" if gender == "male" else "女",
        birth_year=birth_year,
        birth_month=birth_month,
        birth_day=birth_day,
        birth_hour=birth_hour,
        longitude=longitude,
        
        # 紫微信息
        ziwei_chart_info=ziwei_chart_info,
        ziwei_analysis_summary=ziwei_analysis_summary,
        
        # 八字信息
        year_pillar=f"{pillars['年柱']['天干']}{pillars['年柱']['地支']}",
        year_nayin=pillars["年柱"]["纳音"],
        month_pillar=f"{pillars['月柱']['天干']}{pillars['月柱']['地支']}",
        month_nayin=pillars["月柱"]["纳音"],
        day_pillar=f"{pillars['日柱']['天干']}{pillars['日柱']['地支']}",
        day_nayin=pillars["日柱"]["纳音"],
        hour_pillar=f"{pillars['时柱']['天干']}{pillars['时柱']['地支']}",
        hour_nayin=pillars["时柱"]["纳音"],
        bazi_analysis_summary=bazi_analysis_summary
    )
