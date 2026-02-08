"""
AI Tool Use 定义与执行器
为 Gemini Function Calling 提供工具定义和执行逻辑
"""

from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
import json
import logging

from ..calculators.bazi import BaziCalculator
from ..calculators.astrology import AstrologyCalculator
from ..calculators.ziwei_hard import ZiweiHardCalculator
from ..calculators.numerology import NumerologyCalculator
from ..calculators.name import NameCalculator
from ..calculators.tarot import TarotCalculator
from .database import get_database

logger = logging.getLogger(__name__)


# ============================================================================
# Tool Definitions (Gemini Function Calling Format)
# ============================================================================

TOOL_DEFINITIONS = [
    {
        "name": "calculate_ziwei",
        "description": "计算紫微斗数命盘。需要用户提供：出生日期（阳历）、出生时间、性别、出生地点。注意：如果系统提示中的「命盘摘要」已包含紫微数据，则无需重复调用此工具，直接引用已有数据分析即可。",
        "parameters": {
            "type": "object",
            "properties": {
                "birth_date": {
                    "type": "string",
                    "description": "出生日期，格式：YYYY-MM-DD（阳历）"
                },
                "birth_time": {
                    "type": "string",
                    "description": "出生时间，格式：HH:MM（24小时制）"
                },
                "gender": {
                    "type": "string",
                    "description": "性别：男 或 女",
                    "enum": ["男", "女"]
                },
                "birth_location": {
                    "type": "string",
                    "description": "出生地点，如：台北、上海、香港"
                }
            },
            "required": ["birth_date", "birth_time", "gender", "birth_location"]
        }
    },
    {
        "name": "calculate_bazi",
        "description": "计算八字命盘（四柱八字、大运、流年）。需要用户提供：出生年月日时、性别。注意：如果系统提示中的「命盘摘要」已包含八字数据，则无需重复调用此工具，直接引用已有数据分析即可。",
        "parameters": {
            "type": "object",
            "properties": {
                "year": {
                    "type": "integer",
                    "description": "出生年（公历）"
                },
                "month": {
                    "type": "integer",
                    "description": "出生月（公历）"
                },
                "day": {
                    "type": "integer",
                    "description": "出生日（公历）"
                },
                "hour": {
                    "type": "integer",
                    "description": "出生时（24小时制，0-23）"
                },
                "minute": {
                    "type": "integer",
                    "description": "出生分（0-59）",
                    "default": 0
                },
                "gender": {
                    "type": "string",
                    "description": "性别：男 或 女",
                    "enum": ["男", "女"]
                },
                "longitude": {
                    "type": "number",
                    "description": "出生地经度（用于真太阳时校正），默认120.0",
                    "default": 120.0
                }
            },
            "required": ["year", "month", "day", "hour", "gender"]
        }
    },
    {
        "name": "calculate_astrology",
        "description": "计算西洋占星本命盘（行星、宫位、相位）。需要用户提供：出生年月日时、出生地点。注意：如果系统提示中的「命盘摘要」已包含占星数据，则无需重复调用此工具。",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "姓名（可选，用于标识）",
                    "default": "User"
                },
                "year": {
                    "type": "integer",
                    "description": "出生年（公历）"
                },
                "month": {
                    "type": "integer",
                    "description": "出生月（公历）"
                },
                "day": {
                    "type": "integer",
                    "description": "出生日（公历）"
                },
                "hour": {
                    "type": "integer",
                    "description": "出生时（24小时制）"
                },
                "minute": {
                    "type": "integer",
                    "description": "出生分（0-59）"
                },
                "city": {
                    "type": "string",
                    "description": "出生城市，如：Taipei, Shanghai, Hong Kong",
                    "default": "Taipei"
                },
                "nation": {
                    "type": "string",
                    "description": "国家代码，如：TW, CN",
                    "default": "TW"
                }
            },
            "required": ["year", "month", "day", "hour", "minute"]
        }
    },
    {
        "name": "calculate_numerology",
        "description": "计算生命灵数（生命数、表现数、灵魂数、人格数、流年运势）。需要用户提供：出生日期、姓名（可选）",
        "parameters": {
            "type": "object",
            "properties": {
                "birth_date": {
                    "type": "string",
                    "description": "出生日期，格式：YYYY-MM-DD"
                },
                "full_name": {
                    "type": "string",
                    "description": "全名（用于计算表现数、灵魂数等），可选",
                    "default": ""
                },
                "include_cycles": {
                    "type": "boolean",
                    "description": "是否包含流年周期运势",
                    "default": False
                }
            },
            "required": ["birth_date"]
        }
    },
    {
        "name": "analyze_name",
        "description": "分析姓名学（五格、三才、81数理）。需要用户提供：姓氏、名字",
        "parameters": {
            "type": "object",
            "properties": {
                "surname": {
                    "type": "string",
                    "description": "姓氏（繁体中文）"
                },
                "given_name": {
                    "type": "string",
                    "description": "名字（繁体中文）"
                }
            },
            "required": ["surname", "given_name"]
        }
    },
    {
        "name": "draw_tarot",
        "description": "进行塔罗牌占卜（单张、三张、凯尔特十字等牌阵）。需要用户提供：问题、牌阵类型",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "占卜问题"
                },
                "spread": {
                    "type": "string",
                    "description": "牌阵类型：single（单张）、three_card（过去现在未来）、celtic_cross（凯尔特十字）",
                    "enum": ["single", "three_card", "celtic_cross"],
                    "default": "single"
                },
                "seed": {
                    "type": "integer",
                    "description": "随机种子（可选，用于复现结果）"
                }
            },
            "required": ["question"]
        }
    },
    {
        "name": "get_location",
        "description": "查询地点的经纬度信息",
        "parameters": {
            "type": "object",
            "properties": {
                "location_name": {
                    "type": "string",
                    "description": "地点名称，如：高雄市左營區"
                },
                "nation": {
                    "type": "string",
                    "description": "国家代码（可选），如：TW",
                    "default": "TW"
                }
            },
            "required": ["location_name"]
        }
    },
    {
        "name": "get_user_profile",
        "description": "获取用户的基本资料与已保存的命盘数据（如有）",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "用户ID"
                }
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "save_user_insight",
        "description": "保存对用户的重要洞察或标签（如：关注事业、情绪敏感、决策果断等）",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "用户ID"
                },
                "insight_type": {
                    "type": "string",
                    "description": "洞察类型：personality（性格特质）、concern（关注议题）、preference（沟通偏好）",
                    "enum": ["personality", "concern", "preference"]
                },
                "content": {
                    "type": "string",
                    "description": "洞察内容描述"
                },
                "confidence": {
                    "type": "number",
                    "description": "置信度（0-1），表示这个洞察的确定程度",
                    "default": 0.5
                }
            },
            "required": ["user_id", "insight_type", "content"]
        }
    },
    {
        "name": "search_conversation_history",
        "description": "搜索用户的过往对话记录，用于回忆之前讨论过的话题",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "用户ID"
                },
                "keyword": {
                    "type": "string",
                    "description": "搜索关键词"
                },
                "topic": {
                    "type": "string",
                    "description": "主题过滤（可选）：career, relationship, health, wealth, general",
                    "enum": ["career", "relationship", "health", "wealth", "general"]
                },
                "limit": {
                    "type": "integer",
                    "description": "返回结果数量上限",
                    "default": 5
                }
            },
            "required": ["user_id", "keyword"]
        }
    }
]


# ============================================================================
# Tool Execution Functions
# ============================================================================

def execute_calculate_ziwei(birth_date: str, birth_time: str, gender: str, birth_location: str) -> Dict[str, Any]:
    """执行紫微斗数排盘"""
    try:
        calc = ZiweiHardCalculator()
        chart = calc.calculate_chart(
            birth_date=birth_date,
            birth_time=birth_time,
            gender=gender,
            birth_location=birth_location
        )
        return {
            "status": "success",
            "system": "ziwei",
            "data": chart
        }
    except Exception as e:
        logger.error(f"紫微排盘失败: {e}", exc_info=True)
        return {
            "status": "error",
            "system": "ziwei",
            "error": str(e)
        }


def execute_calculate_bazi(year: int, month: int, day: int, hour: int, minute: int = 0, 
                           gender: str = "男", longitude: float = 120.0) -> Dict[str, Any]:
    """执行八字排盘"""
    try:
        calc = BaziCalculator()
        chart = calc.calculate_bazi(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            gender=gender,
            longitude=longitude
        )
        return {
            "status": "success",
            "system": "bazi",
            "data": chart
        }
    except Exception as e:
        logger.error(f"八字排盘失败: {e}", exc_info=True)
        return {
            "status": "error",
            "system": "bazi",
            "error": str(e)
        }


def execute_calculate_astrology(name: str = "User", year: int = None, month: int = None, 
                                day: int = None, hour: int = None, minute: int = None,
                                city: str = "Taipei", nation: str = "TW") -> Dict[str, Any]:
    """执行西洋占星排盘"""
    try:
        if any(v is None for v in [year, month, day, hour, minute]):
            raise ValueError("缺少必要的出生日期或时间参数")
        calc = AstrologyCalculator()
        city_map = {
            "Taipei": {"longitude": 121.5654, "latitude": 25.0330, "timezone": "Asia/Taipei"},
            "台北": {"longitude": 121.5654, "latitude": 25.0330, "timezone": "Asia/Taipei"},
            "臺北": {"longitude": 121.5654, "latitude": 25.0330, "timezone": "Asia/Taipei"}
        }

        if city in city_map:
            coords = city_map[city]
            chart = calc.calculate_natal_chart(
                name=name,
                year=year,
                month=month,
                day=day,
                hour=hour,
                minute=minute,
                longitude=coords["longitude"],
                latitude=coords["latitude"],
                timezone_str=coords["timezone"]
            )
        else:
            chart = calc.calculate_natal_chart(
                name=name,
                year=year,
                month=month,
                day=day,
                hour=hour,
                minute=minute,
                city=city,
                nation=nation
            )
        return {
            "status": "success",
            "system": "astrology",
            "data": chart
        }
    except Exception as e:
        logger.error(f"占星排盘失败: {e}", exc_info=True)
        return {
            "status": "error",
            "system": "astrology",
            "error": str(e)
        }


def execute_calculate_numerology(birth_date: str, full_name: str = "", 
                                 include_cycles: bool = False) -> Dict[str, Any]:
    """执行生命灵数计算"""
    try:
        from datetime import datetime
        date_obj = datetime.strptime(birth_date, "%Y-%m-%d").date()
        
        calc = NumerologyCalculator()
        profile = calc.calculate_full_profile(
            birth_date=date_obj,
            full_name=full_name
        )
        
        # Convert NumerologyProfile dataclass to dict
        from dataclasses import asdict
        profile_dict = asdict(profile)
        
        # Format dates as strings for JSON serialization
        profile_dict['birth_date'] = profile.birth_date.isoformat()
        
        return {
            "status": "success",
            "system": "numerology",
            "data": profile_dict
        }
    except Exception as e:
        logger.error(f"生命灵数计算失败: {e}", exc_info=True)
        return {
            "status": "error",
            "system": "numerology",
            "error": str(e)
        }


def execute_analyze_name(surname: str, given_name: str) -> Dict[str, Any]:
    """执行姓名学分析"""
    try:
        analyzer = NameCalculator()
        # Combine surname and given_name for analyze method
        full_name = surname + given_name
        analysis = analyzer.analyze(full_name=full_name)
        # Convert dataclass to dict
        result = analyzer.to_dict(analysis)
        return {
            "status": "success",
            "system": "name",
            "data": result
        }
    except Exception as e:
        logger.error(f"姓名学分析失败: {e}", exc_info=True)
        return {
            "status": "error",
            "system": "name",
            "error": str(e)
        }


def execute_draw_tarot(question: str, spread: str = "single", seed: Optional[int] = None) -> Dict[str, Any]:
    """执行塔罗牌占卜"""
    try:
        calc = TarotCalculator()
        reading = calc.draw_cards(question=question, spread_type=spread, seed=seed)
        result = calc.to_dict(reading)
        return {
            "status": "success",
            "system": "tarot",
            "data": result
        }
    except Exception as e:
        logger.error(f"塔罗占卜失败: {e}", exc_info=True)
        return {
            "status": "error",
            "system": "tarot",
            "error": str(e)
        }


def execute_get_location(location_name: str, nation: str = "TW") -> Dict[str, Any]:
    """执行地点经纬度查询（内建常用地点）"""
    try:
        location = location_name.strip()
        mapping = {
            "台北": (25.0330, 121.5654),
            "臺北": (25.0330, 121.5654),
            "新北": (25.0124, 121.4657),
            "台中": (24.1477, 120.6736),
            "臺中": (24.1477, 120.6736),
            "台南": (22.9997, 120.2270),
            "臺南": (22.9997, 120.2270),
            "高雄": (22.6273, 120.3014)
        }
        lat = lon = None
        for key, (lat_val, lon_val) in mapping.items():
            if key in location:
                lat, lon = lat_val, lon_val
                break
        if lat is None or lon is None:
            return {
                "status": "error",
                "message": f"無法解析地點: {location_name}"
            }
        return {
            "status": "success",
            "location": location_name,
            "nation": nation,
            "latitude": lat,
            "longitude": lon
        }
    except Exception as e:
        logger.error(f"地點查詢失敗: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def execute_get_user_profile(user_id: str) -> Dict[str, Any]:
    """获取用户画像与命盘数据"""
    try:
        db = get_database()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            # 查询用户基本信息（避免回传敏感字段）
            cursor.execute(
                "SELECT user_id, display_name, created_at FROM members WHERE user_id = ?",
                (user_id,)
            )
            member = cursor.fetchone()
            if not member:
                return {
                    "status": "error",
                    "message": "用户不存在"
                }
            
            # 查询用户画像
            cursor.execute(
                "SELECT birth_info, chart_data, personality_tags, preferences FROM user_persona WHERE user_id = ?",
                (user_id,)
            )
            persona = cursor.fetchone()
        
        result = {
            "status": "success",
            "user_info": {
                "user_id": member["user_id"],
                "display_name": member["display_name"],
                "registered_at": member["created_at"]
            }
        }
        
        if persona:
            result["persona"] = {
                "birth_info": json.loads(persona[0]) if persona[0] else None,
                "chart_data": json.loads(persona[1]) if persona[1] else None,
                "personality_tags": json.loads(persona[2]) if persona[2] else [],
                "preferences": json.loads(persona[3]) if persona[3] else {}
            }
        else:
            result["persona"] = None
        
        return result
        
    except Exception as e:
        logger.error(f"获取用户画像失败: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }


def execute_save_user_insight(user_id: str, insight_type: str, content: str, confidence: float = 0.5) -> Dict[str, Any]:
    """保存用户洞察"""
    try:
        db = get_database()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 获取或创建用户画像
            cursor.execute(
                "SELECT personality_tags FROM user_persona WHERE user_id = ?",
                (user_id,)
            )
            persona = cursor.fetchone()
            
            if persona:
                tags = json.loads(persona[0]) if persona[0] else []
            else:
                # 创建新画像
                cursor.execute(
                    """INSERT INTO user_persona (user_id, personality_tags, created_at, updated_at) 
                       VALUES (?, '[]', datetime('now'), datetime('now'))""",
                    (user_id,)
                )
                tags = []
            
            # 添加新洞察
            new_tag = {
                "type": insight_type,
                "content": content,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat()
            }
            tags.append(new_tag)
            
            # 更新数据库
            cursor.execute(
                "UPDATE user_persona SET personality_tags = ?, updated_at = datetime('now') WHERE user_id = ?",
                (json.dumps(tags, ensure_ascii=False), user_id)
            )
        
        return {
            "status": "success",
            "message": "洞察已保存",
            "insight": new_tag
        }
        
    except Exception as e:
        logger.error(f"保存用户洞察失败: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }


def execute_search_conversation_history(
    user_id: str, keyword: str, topic: Optional[str] = None, limit: int = 5
) -> Dict[str, Any]:
    """搜索用戶過往對話記錄與摘要記憶"""
    try:
        db = get_database()
        results = []

        with db.get_connection() as conn:
            cursor = conn.cursor()

            # 搜索 episodic_summary（Layer 2 摘要記憶）
            if topic:
                cursor.execute("""
                    SELECT summary_date, topic, key_points
                    FROM episodic_summary
                    WHERE user_id = ? AND key_points LIKE ? AND topic = ?
                    ORDER BY summary_date DESC LIMIT ?
                """, (user_id, f"%{keyword}%", topic, limit))
            else:
                cursor.execute("""
                    SELECT summary_date, topic, key_points
                    FROM episodic_summary
                    WHERE user_id = ? AND key_points LIKE ?
                    ORDER BY summary_date DESC LIMIT ?
                """, (user_id, f"%{keyword}%", limit))

            for row in cursor.fetchall():
                results.append({
                    "source": "episodic_summary",
                    "date": row["summary_date"],
                    "topic": row["topic"],
                    "content": row["key_points"]
                })

            # 搜索 conversation_memory（Layer 1 對話記錄）
            remaining = max(0, limit - len(results))
            if remaining > 0:
                cursor.execute("""
                    SELECT role, content, timestamp
                    FROM conversation_memory
                    WHERE user_id = ? AND content LIKE ? AND role IN ('user', 'assistant')
                    ORDER BY id DESC LIMIT ?
                """, (user_id, f"%{keyword}%", remaining))

                for row in cursor.fetchall():
                    results.append({
                        "source": "conversation",
                        "role": row["role"],
                        "content": row["content"][:200],
                        "timestamp": row["timestamp"]
                    })

        return {
            "status": "success",
            "keyword": keyword,
            "results_count": len(results),
            "results": results
        }

    except Exception as e:
        logger.error(f"搜索對話歷史失敗: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


# ============================================================================
# Tool Registry & Dispatcher
# ============================================================================

TOOL_EXECUTORS: Dict[str, Callable] = {
    "calculate_ziwei": execute_calculate_ziwei,
    "calculate_bazi": execute_calculate_bazi,
    "calculate_astrology": execute_calculate_astrology,
    "calculate_numerology": execute_calculate_numerology,
    "analyze_name": execute_analyze_name,
    "draw_tarot": execute_draw_tarot,
    "get_location": execute_get_location,
    "get_user_profile": execute_get_user_profile,
    "save_user_insight": execute_save_user_insight,
    "search_conversation_history": execute_search_conversation_history
}


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行指定的工具
    
    Args:
        tool_name: 工具名称
        arguments: 工具参数
    
    Returns:
        工具执行结果
    """
    if tool_name not in TOOL_EXECUTORS:
        return {
            "status": "error",
            "message": f"未知的工具: {tool_name}"
        }
    
    try:
        executor = TOOL_EXECUTORS[tool_name]
        result = executor(**arguments)
        return result
    except TypeError as e:
        logger.error(f"工具参数错误: {tool_name}, {arguments}, {e}")
        return {
            "status": "error",
            "message": f"工具参数错误: {str(e)}"
        }
    except Exception as e:
        logger.error(f"工具执行失败: {tool_name}, {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"工具执行失败: {str(e)}"
        }


def get_tool_definitions() -> List[Dict[str, Any]]:
    """获取所有工具定义（用于传递给 Gemini API）"""
    return TOOL_DEFINITIONS
