"""
天气 MCP 服务器 - 基于美国国家气象局 API

代码结构说明：
本文件实现了一个完整的 MCP 服务器，主要包含：

核心功能（MCP 工具）：
- get_alerts(): 获取美国某州的天气警报
- get_forecast(): 根据经纬度获取天气预报

辅助功能：
- make_nws_request(): 统一的 API 请求处理函数
- format_alert(): 格式化警报信息的工具函数
- 常量定义和服务器初始化

构建 MCP Server 的主要步骤：
1. 导入 FastMCP 框架并创建服务器实例
2. 定义工具函数，使用 @mcp.tool() 装饰器注册
3. 实现具体的业务逻辑（API 调用、数据处理等）
4. 在 __main__ 中启动服务器

参考文档：https://modelcontextprotocol.io/quickstart/server
"""

from typing import Any  # 导入类型注解
import httpx  # 导入异步 HTTP 客户端库
from mcp.server.fastmcp import FastMCP  # 导入 FastMCP 框架


# 步骤1：初始化 FastMCP 服务器
mcp = FastMCP("weather")

# 常量定义
NWS_API_BASE = "https://api.weather.gov"  # 美国国家气象局 API 基础 URL
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """向 NWS API 发送请求并处理错误"""
    headers = {  # 设置 HTTP 请求头
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    # 创建异步 HTTP 客户端并发送请求
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)  # 发送 GET 请求，30秒超时
            response.raise_for_status()  # 检查 HTTP 状态码，如果是错误状态则抛出异常
            return response.json()  # 解析并返回 JSON 响应
        except Exception:  # 捕获所有异常
            return None  # 出错时返回 None

def format_alert(feature: dict) -> str:
    """格式化天气警报信息为可读字符串"""
    props = feature["properties"]  # 提取警报属性数据
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""

# 步骤2：定义 MCP 工具函数
@mcp.tool()  # 使用装饰器注册为 MCP 工具
async def get_alerts(state: str) -> str:
    """获取美国州的天气预警
    
    Args:
        state: 美国州的两字母代码，如CA、NY、TX
        
    Returns:
        格式化的预警信息字符串，如果无预警则返回相应消息
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"  # 构建 API URL
    data = await make_nws_request(url)  # 发送请求获取数据

    # 数据验证和错误处理
    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    # 处理和格式化警报数据
    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool()  # 使用装饰器注册为 MCP 工具
async def get_forecast(latitude: float, longitude: float) -> str:
    """根据经纬度获取天气预报
    
    Args:
        latitude: 位置的纬度坐标（-90 到 90）
        longitude: 位置的经度坐标（-180 到 180）
        
    Returns:
        格式化的未来5个时段天气预报字符串，包含温度、风况和详细预报
    """
    # 步骤3：实现业务逻辑 - 天气预报需要两次 API 调用
    
    # 第一步：获取预报网格端点信息
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # 第二步：从第一次响应中获取预报数据 URL
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # 第三步：格式化预报信息为用户友好的格式
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # 只显示接下来 5 个时间段，避免信息过载
        forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)  # 使用分隔符连接多个预报时段

# 步骤4：启动服务器
if __name__ == "__main__":
    # 使用 stdio 传输启动 MCP 服务器，这是标准的 MCP 通信方式
    mcp.run(transport='stdio')
