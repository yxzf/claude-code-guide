# 视频脚本2：MCP技术深入与开发实战
**时长预估：15-18分钟**

## 开场白 (0:00-0:45)
欢迎回来！上期我们了解了MCP的基本概念，相信很多朋友已经迫不及待想要动手实践了。

今天这期视频，我们要做两件事：
1. **深入MCP技术架构**：彻底搞懂服务器原语和客户端原语
2. **实战开发第一个MCP工具**：5分钟写出文件计数器

特别是第二部分，我会带你从零开始，写代码、配置、测试，让你的Claude拥有读取本地文件的超能力！

准备好了吗？我们开始！

## 第一部分：MCP核心原语深度解析 (0:45-6:00)

### 服务器原语详解 (0:45-3:30)

#### Tools - 工具调用（使用频率90%+）
**定义**：MCP服务器向客户端公开的可调用函数

让我用代码来展示：
```python
@mcp.tool()
def get_weather(city: str, unit: str = "celsius") -> str:
    """获取指定城市的天气信息
    
    Args:
        city: 城市名称  
        unit: 温度单位，celsius或fahrenheit
    """
    # 实际的天气查询逻辑
    return f"{city}今天多云，温度22°C"
```

**工具调用的完整流程**：
1. **工具发现**：AI调用`list_tools()`查看可用工具
2. **智能选择**：根据用户需求选择合适工具
3. **参数验证**：根据JSON Schema验证参数
4. **执行调用**：`call_tool(name, arguments)`
5. **结果返回**：结构化响应给AI

#### Resources - 资源访问（使用频率<20%）
**适用场景**：提供AI上下文信息

```python
@mcp.resource("config://app/settings")
def get_app_config():
    return {
        "name": "My App", 
        "version": "1.0.0",
        "debug": False
    }
```

**实际使用**：大多数情况下，通过Tools获取数据更直接高效。

#### Prompts - 提示模板（使用频率<5%）
**适用场景**：复杂任务的标准化模板

```python
@mcp.prompt()
def code_review_prompt(code: str) -> str:
    return f"""请审查以下代码的：
    1. 代码规范
    2. 潜在bug
    3. 性能优化建议
    
    代码：\n{code}"""
```

### 客户端原语详解 (3:30-6:00)

#### Sampling - 模型推理
**作用**：服务器请求客户端使用AI生成内容

```python
# 服务器可以这样请求AI生成代码
response = client.sampling.create_message(
    messages=[{"role": "user", "content": "生成Python排序函数"}],
    max_tokens=500,
    temperature=0.7
)
```

#### Elicitation - 用户交互  
**作用**：服务器请求客户端获取用户输入

```python
# 交互式配置
api_key = client.elicitation.request_input(
    prompt="请输入您的API密钥：",
    input_type="password"
)

env = client.elicitation.request_choice(
    prompt="选择运行环境：",
    choices=["development", "staging", "production"]
)
```

#### Logging - 日志记录
**作用**：服务器向客户端发送日志消息

```python
client.logging.log_message(
    level="INFO",
    message="文件处理完成，共处理123个文件"
)
```

### AI工具选择机制 (6:00-7:30)

这里我要分享一个重要机制：AI是如何智能选择工具的？

**选择算法核心要素**：
1. **功能匹配度**：工具描述与用户需求的相似度
2. **参数复杂度**：优先选择参数简单的工具
3. **历史成功率**：基于过往调用成功率
4. **上下文相关性**：当前对话上下文的匹配度

**实际示例**：
用户说："帮我看看桌面文件"
- 匹配到`list_files()`工具
- 参数验证：directory="Desktop"
- 智能推理：用户想查看文件列表
- 执行调用：返回文件清单

这个机制让MCP工具的使用变得智能化，用户无需记忆具体命令。

## 第二部分：5分钟开发实战 (7:30-15:00)

### 开发环境准备 (7:30-8:30)

首先准备开发环境：

```bash
# 1. 安装Python包管理器
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 创建项目目录
mkdir my-first-mcp && cd my-first-mcp

# 3. 安装MCP开发依赖
pip install "mcp[cli]"

# 4. 创建主文件
touch file_counter.py
```

### 核心代码实现 (8:30-12:00)

现在让我们一步步写代码。我会在屏幕上实时编码：

```python
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# 创建MCP服务器实例
mcp = FastMCP("文件计数器")

@mcp.tool()
def count_files(directory: str = "Desktop") -> str:
    """统计指定目录的文件数量
    
    Args:
        directory: 目录名称，默认Desktop
        
    Returns:
        文件统计结果字符串
    """
    # 获取用户名，兼容不同操作系统
    username = os.getenv("USER") or os.getenv("USERNAME")
    
    # 构建目录路径
    if username:
        dir_path = Path(f"/Users/{username}/{directory}")
    else:
        dir_path = Path.home() / directory
    
    # 检查目录是否存在
    if not dir_path.exists():
        return f"错误：目录 {directory} 不存在"
    
    # 统计文件和文件夹
    try:
        items = list(dir_path.iterdir())
        files = [f for f in items if f.is_file()]
        folders = [f for f in items if f.is_dir()]
        
        result = f"""📁 {directory} 目录统计结果：
📄 文件数量：{len(files)} 个
📂 文件夹数量：{len(folders)} 个
📋 总计：{len(items)} 个项目"""
        
        return result
        
    except PermissionError:
        return f"错误：没有权限访问 {directory} 目录"
    except Exception as e:
        return f"错误：{str(e)}"

# 启动服务器
if __name__ == "__main__":
    mcp.run()
```

**代码解析要点**：
1. **装饰器 `@mcp.tool()`**：这是关键，将普通函数变成MCP工具
2. **文档字符串**：AI理解工具功能的重要依据
3. **类型注解**：确保参数验证正确
4. **错误处理**：提供友好的错误信息
5. **跨平台兼容**：处理不同操作系统的路径问题

### Claude Code配置 (12:00-13:30)

代码写好了，现在配置Claude Code：

```bash
# 1. 添加MCP服务器到Claude Code
claude mcp add file-counter -- python file_counter.py

# 2. 验证配置
claude mcp list

# 3. 查看详细信息
claude mcp get file-counter
```

你会看到类似这样的输出：
```
✅ file-counter
   Command: python file_counter.py
   Status: Ready
   Tools: count_files
```

### 实际测试效果 (13:30-15:00)

现在是激动人心的测试时刻！

**在Claude Code中测试**：

1. **基本测试**：
   输入："帮我统计一下桌面文件数量"
   
   Claude会自动：
   - 识别需要文件统计功能
   - 调用我们的`count_files`工具
   - 返回格式化的统计结果

2. **高级测试**：
   输入："比较一下我的桌面和文档文件夹，哪个文件更多？"
   
   Claude会：
   - 两次调用`count_files`工具
   - 分别统计Desktop和Documents
   - 对比结果给出分析

3. **错误处理测试**：
   输入："统计一下不存在的文件夹"
   
   看看我们的错误处理是否生效

**演示效果预告**：
我会现场演示这些测试，你会看到Claude如何智能地调用我们的工具，处理各种情况。

## 第三部分：进阶开发技巧 (15:00-17:00)

### 完整MCP服务器架构预览

基础版本很简单，但实际项目需要更多功能：

```python
# 完整版本包含：
# 1. 多个工具函数
@mcp.tool()
def count_files(): pass

@mcp.tool() 
def list_files(): pass

@mcp.tool()
def find_files(): pass

# 2. 资源提供
@mcp.resource("system://info")
def system_info(): pass

# 3. 提示模板
@mcp.prompt()
def analyze_files_prompt(): pass
```

### 开发最佳实践

1. **工具设计原则**：
   - 单一职责：每个工具做好一件事
   - 参数明确：清晰的类型注解和文档
   - 错误友好：提供有用的错误信息

2. **性能优化**：
   - 避免长时间阻塞操作
   - 合理设置超时机制
   - 缓存常用数据

3. **安全考虑**：
   - 验证用户权限
   - 限制文件访问范围
   - 防止路径遍历攻击

## 结尾与预告 (17:00-18:00)

### 今天学到的核心内容
1. **MCP六大原语详解**：服务器原语与客户端原语的具体用法
2. **AI工具选择机制**：智能化工具调用的底层逻辑  
3. **实战开发经验**：从零到一完成MCP工具开发

### 下期预告
下期视频我们将深入：
- **MCP部署配置全攻略**：3种安装方式详解
- **生产环境最佳实践**：企业级MCP服务器部署
- **热门MCP项目推荐**：100+现成工具直接使用

### 作业与互动
**今天的作业**：
尝试在文件计数器基础上，添加一个新功能：
- 按文件类型分类统计（.txt, .pdf, .jpg等）
- 在评论区分享你的实现代码

**互动话题**：
你最希望开发什么样的MCP工具？文件管理、API集成，还是数据分析？评论区告诉我！

记得点赞订阅，我们下期见！

## 补充制作说明

### 屏幕录制要点
1. **代码编写过程**：完整录制编码过程，展示思路
2. **命令行操作**：清晰显示每个命令的输入和输出
3. **Claude测试**：实时演示AI调用工具的过程

### 视觉辅助材料
1. **架构图解**：MCP原语关系图
2. **代码高亮**：关键代码片段的注解
3. **流程动画**：工具选择机制的可视化

### 语言节奏
- 理论部分：语速适中，重点信息停顿强调
- 实战部分：语速稍快，保持动手实践的节奏感
- 每个重要概念后留出2-3秒思考时间