# 视频脚本3：MCP开发实战
**时长预估：15-18分钟**

## 开场白 (0:00-0:30)
欢迎来到MCP系列第三期！前两期我们学习了MCP的概念和技术原理，今天终于要动手实践了！

**今天的核心目标**：
手把手带你开发第一个MCP工具 - 天气服务器，让Claude能够实时查询美国天气预报和灾害预警。

**为什么选择天气服务器？**
1. **官方推荐示例**：基于Anthropic官方教程，权威可靠
2. **真实API集成**：调用美国国家气象局API，有实用价值
3. **技术点全面**：涵盖异步编程、错误处理、数据格式化
4. **5分钟见效**：代码不到100行，快速看到效果

让我们开始吧！

## 第一部分：项目环境搭建 (0:30-2:30)

### 工具准备：为什么选择uv？
**传统pip的痛点**：
- 依赖解析慢，经常冲突
- 虚拟环境管理复杂
- 包安装速度慢

**uv的优势**：
- 用Rust编写，速度快10-100倍
- 自动管理虚拟环境
- 依赖解析更智能

### 逐步环境搭建演示

**第一步：安装uv**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**第二步：创建项目**
```bash
# 创建项目目录
mkdir weather-server && cd weather-server

# 初始化Python项目（自动创建虚拟环境）
uv init --python=3.11

# 安装依赖
uv add "mcp[cli]" httpx

# 创建主要代码文件
touch weather.py
```

**【屏幕演示】**：
- 展示uv的安装速度
- 展示项目目录结构
- 展示pyproject.toml配置文件

## 第二部分：核心代码逐行开发 (2:30-12:00)

### 阶段一：基础架构搭建 (2:30-4:00)

**导入和初始化（代码第1-10行）**
```python
"""
天气 MCP 服务器 - 基于美国国家气象局 API

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
```

**【逐行讲解重点】**：
1. **文档字符串的重要性**：让代码自解释
2. **type hints的作用**：提高代码可读性和IDE支持
3. **FastMCP的优势**：相比原生MCP SDK更简单
4. **常量配置**：API基础URL和User-Agent的最佳实践

### 阶段二：HTTP请求封装 (4:00-6:30)

**异步HTTP请求函数（代码第13-25行）**
```python
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
```

**【技术要点讲解】**：
1. **async/await语法**：异步编程的核心概念
2. **上下文管理器**：`async with` 确保资源正确释放
3. **错误处理策略**：捕获所有异常，返回None而不是崩溃
4. **HTTP头部设置**：User-Agent和Accept的API礼仪
5. **超时设置**：30秒超时防止无限等待

### 阶段三：数据格式化工具 (6:30-7:30)

**警报格式化函数（代码第27-36行）**
```python
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
```

**【设计思路讲解】**：
1. **字典安全访问**：使用`.get()`方法防止KeyError
2. **默认值策略**：提供有意义的默认值
3. **多行字符串格式化**：f-string的高级用法
4. **数据结构理解**：GeoJSON格式的properties字段

### 阶段四：MCP工具函数开发 (7:30-11:00)

**工具1：获取天气预警（代码第39-55行）**
```python
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
```

**【MCP核心概念讲解】**：
1. **@mcp.tool()装饰器**：这就是MCP的"魔法"
2. **函数签名的重要性**：AI根据这个理解工具用途
3. **docstring的作用**：AI选择工具的重要依据
4. **数据验证的必要性**：API调用的容错处理
5. **列表推导式**：Python的优雅语法

**工具2：获取天气预报（代码第57-91行）**
```python
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
```

**【复杂业务逻辑讲解】**：
1. **两阶段API调用**：为什么需要先获取points再获取forecast
2. **地理坐标处理**：latitude和longitude的有效范围
3. **数据切片技巧**：`periods[:5]` 限制返回数量
4. **字符串连接策略**：使用分隔符提高可读性

### 阶段五：服务器启动 (11:00-11:30)

**启动代码（代码第94-96行）**
```python
# 步骤4：启动服务器
if __name__ == "__main__":
    # 使用 stdio 传输启动 MCP 服务器，这是标准的 MCP 通信方式
    mcp.run(transport='stdio')
```

**【启动机制讲解】**：
1. **`if __name__ == "__main__"`**：Python模块的标准实践
2. **stdio传输**：MCP的标准通信方式，通过标准输入输出
3. **为什么是stdio**：简单、可靠、跨平台兼容

## 第三部分：测试和部署 (12:00-15:00)

### 独立测试（官方推荐流程）(12:00-13:00)

**第一步：服务器独立运行测试**
```bash
# 启动MCP服务器（独立运行模式）
uv run weather.py
```

**【测试要点讲解】**：
- **预期行为**：服务器启动后等待输入，没有输出是正常的
- **验证目标**：代码语法正确、依赖正常加载、服务器能启动
- **停止方法**：Ctrl+C 停止服务器
- **这一步的重要性**：在配置Claude之前先确保代码没问题

### Claude Code集成配置 (13:00-14:00)

**第二步：配置到Claude Code**
```bash
# 在当前项目中添加MCP服务器
claude mcp add weather -- uv run weather.py

# 验证配置
claude mcp list

# 查看详细信息
claude mcp get weather
```

**【配置过程演示】**：
1. **配置命令详解**：`--` 后面是启动命令
2. **配置验证**：确保服务器正确注册
3. **配置文件位置**：Claude Code如何管理MCP配置

### 实际使用测试 (14:00-15:00)

**测试场景1：天气预报查询**
```
提问："萨克拉门托的天气怎么样？"
```
**【演示过程】**：
1. Claude识别需要地理坐标
2. 自动调用get_forecast工具
3. 展示完整的API调用过程
4. 格式化的天气信息展示

**测试场景2：灾害预警查询**
```
提问："德克萨斯州有什么天气预警吗？"
```
**【演示过程】**：
1. Claude理解州代码需求
2. 调用get_alerts工具
3. 展示预警信息或无预警提示

**【AI工具选择观察】**：
- Claude如何理解用户意图
- 工具选择的智能程度
- 错误处理的表现

## 第四部分：扩展和优化建议 (15:00-15:30)

### 可以尝试的改进方向

**功能扩展**：
1. **添加新工具**：历史天气数据、天气地图
2. **支持更多地区**：国际天气API集成
3. **缓存机制**：避免重复API调用

**代码优化**：
1. **配置外部化**：使用环境变量管理API配置
2. **日志记录**：添加详细的调试信息
3. **类型安全**：更严格的类型注解

**用户体验**：
1. **错误信息优化**：更友好的错误提示
2. **数据格式化**：图表化天气展示
3. **多语言支持**：中文天气信息

## 总结与预告 (15:30-16:00)

### 今天学到的关键技能
1. **MCP开发全流程**：从环境搭建到部署测试
2. **异步编程实践**：现代Python的核心技能
3. **API集成模式**：真实项目的开发经验
4. **错误处理策略**：生产环境的代码质量

### 作业挑战
基于今天的天气服务器，尝试添加一个新功能：
- 天气历史数据查询
- 多城市天气对比
- 天气趋势分析

把你的代码分享到评论区，我们一起交流！

### 下期预告
第4期：**MCP部署配置与生态应用**
- 企业级MCP服务器部署
- 100+现成MCP工具推荐
- 团队协作和权限管理
- 构建MCP工具生态

感谢观看，记得点赞订阅，我们下期见！

---

## 制作补充说明

### 演示环境要求
1. **开发环境**：macOS/Linux/Windows均可
2. **Python版本**：3.11+
3. **必要工具**：uv包管理器、Claude Code
4. **网络要求**：能访问GitHub和美国气象局API

### 视频制作要点
1. **代码演示**：使用大字体，确保代码清晰可见
2. **分屏展示**：代码编写 + 实际运行效果
3. **错误演示**：故意制造一个错误并修复，增强教学效果
4. **节奏控制**：关键概念重复强调，给观众消化时间

### 互动元素
1. **弹幕互动**：在关键节点询问观众理解程度
2. **评论作业**：鼓励观众分享改进代码
3. **资源下载**：提供完整代码和配置文件