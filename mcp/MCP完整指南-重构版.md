# Model Context Protocol (MCP) 完整指南

> **作者**: Claude Code Assistant  
> **版本**: 2.0  
> **最后更新**: 2025年01月  
> **适用范围**: AI应用开发者、系统架构师、产品经理

---

## 文档概览

本指南为你提供 Model Context Protocol (MCP) 的全面理解，从基础概念到高级实现，涵盖理论与实践。无论你是初学者还是经验丰富的开发者，都能在这里找到所需的知识。

### 学习路径  
- **视频学习**: 按三段式观看：概念理解 → 快速实践 → 生态了解
- **新手入门**: 第1章概念 → 第4章快速实践 → 生态总览
- **开发实战**: 第2章原理 → 第4章开发指南 → 生态项目选择
- **架构设计**: 第2章架构 → 第3章配置 → 协议标准

---

## 目录结构

### 第一部分：概念讲解（什么是MCP）
1. [MCP 核心概念](#1-mcp-核心概念)
   - 1.1 基础概念和价值
   - 1.2 核心架构设计
   - 1.3 MCP vs Function Call
2. [MCP 怎么工作](#2-mcp-怎么工作)
   - 2.1 AI如何选择和调用工具
   - 2.2 三大核心原语详解
   - 2.3 双向通信机制

### 第二部分：安装配置（怎么用MCP）
3. [MCP 安装配置指南](#3-mcp-安装配置指南)
   - 3.1 claude mcp 命令概述
   - 3.2 配置管理基础
   - 3.3 安装方式一：Claude Desktop导入
   - 3.4 安装方式二：JSON配置方式
   - 3.5 安装方式三：命令行方式

### 第三部分：开发实战（怎么开发MCP）
4. [开发实战指南](#4-开发实战指南)
   - 4.1 开发环境配置
   - 4.2 5分钟创建第一个MCP工具

### 第四部分：生态总览（有哪些MCP）
5. [MCP生态总览](#5-mcp生态总览)
  - 热门MCP项目推荐
  - Claude Desktop兼容性  
  - 生态发展现状
  - 项目选择指南
- [总结](#总结)

---

## 1. MCP 核心概念

### 1.1 什么是 MCP？

**Model Context Protocol (MCP)** 是由 Anthropic 于 2024年11月25日 发布的开放协议，专门用于标准化 AI 应用程序与外部数据源和工具之间的交互方式。

### MCP 核心架构

MCP 采用客户端-服务器架构设计，AI应用通过MCP客户端与多个MCP服务器建立一对一连接：

![MCP核心架构图](images/mcp_official_architecture.png)

**架构说明**：
- **MCP Host (AI应用)**：如Claude Desktop、VS Code等，负责协调管理多个MCP客户端
- **MCP Client**：每个客户端维护与一个MCP服务器的专用连接
- **MCP Server**：提供具体功能的服务端，如Sentry、文件系统、数据库等

**连接模式**：采用一对一连接模式，确保每个MCP客户端与对应的MCP服务器建立独立的通信通道。

#### 核心类比：AI 世界的 USB-C
就像 USB-C 为各种设备提供了统一的连接标准，MCP 为 AI 模型与外部资源提供了统一的交互协议。

```
传统方式 (混乱):
AI应用 ──┬─→ OpenAI Functions ──→ 工具A
         ├─→ Google Extensions ──→ 工具B  
         └─→ 自定义API ──→ 工具C

MCP方式 (统一):
AI应用 ──→ MCP协议 ──┬─→ MCP服务器A
                      ├─→ MCP服务器B
                      └─→ MCP服务器C
```

### 1.2 为什么需要MCP？

#### Prompt Engineering 发展的必然产物

MCP的出现是 **Prompt Engineering 发展的自然结果**。更结构化的上下文信息对模型性能提升是显著的：

```
发展阶段对比：
┌─────────────────────────────────────────────┐
│ 手工Prompt时代                               │
│ ├─ 人工从数据库筛选信息                      │
│ ├─ 手动复制粘贴到prompt中                    │
│ └─ 问题复杂度↑ = 手工成本↑↑                 │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Function Call时代                           │
│ ├─ 预定义函数获取数据                        │
│ ├─ 自动化水平显著提升                        │
│ └─ 但平台依赖性强，兼容性差                  │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ MCP统一协议时代                             │
│ ├─ 标准化工具调用接口                        │
│ ├─ 跨平台兼容，生态共享                      │
│ └─ 数据安全，本地处理                        │
└─────────────────────────────────────────────┘
```

#### 🚫 Function Call 的根本局限性

**平台依赖性问题**：
```python
# OpenAI 方式
functions=[{
    "name": "get_weather", 
    "parameters": {"type": "object", "properties": {...}}
}]

# Google 方式  
tools=[vertexai.generative_models.Tool(
    function_declarations=[...]
)]

# 切换模型 = 重写所有代码！
```

**核心痛点对比**：

| Function Call 问题 | MCP 解决方案 |
|-------------------|-------------|
| **API不兼容**: OpenAI ≠ Google ≠ Claude | **统一标准**: 一套API，所有模型通用 |
| **厂商锁定**: 切换模型需重写代码 | **模型无关**: 无缝切换AI应用 |
| **数据上云**: 敏感信息必须传输 | **本地处理**: 数据不离开设备 |
| **重复造轮**: 每个平台都要适配 | **生态共享**: 社区共建工具库 |

#### MCP的核心洞察

**设计哲学**: "数据与工具是客观存在的，连接方式应该标准化"

```
传统困境:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   工具A     │    │   工具B     │    │   工具C     │
│  (MySQL)    │    │ (文件系统)   │    │  (API调用)  │
└─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │
    专用接口           专用接口           专用接口
       │                  │                  │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  OpenAI     │    │   Google    │    │   Claude    │
│ Functions   │    │ Extensions  │    │ Tool Use    │
└─────────────┘    └─────────────┘    └─────────────┘

MCP方案:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│MCP Server A │    │MCP Server B │    │MCP Server C │
│  (MySQL)    │    │ (文件系统)   │    │  (API调用)  │
└─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │
         \                │                /
          \               │               /
           ──────── MCP Protocol ────────
                         │
    ┌─────────────────────────────────────────┐
    │        任何支持MCP的AI应用                │
    │   OpenAI, Google, Claude, 自定义...      │
    └─────────────────────────────────────────┘
```

### 1.3 MCP的核心价值

#### 四大技术优势

**1. 生态统一** - 一次开发，处处运行
- 100+ 现成MCP服务器可直接使用
- 社区共建，避免重复造轮

**2. 平台无关** - 告别厂商锁定  
- 同一套工具适配所有AI模型
- 自由选择最佳模型方案

**3. 数据安全** - 本地处理，精确控制
- 敏感数据无需上传云端
- 用户完全控制数据访问权限

**4. 标准化** - 统一接口，降低复杂度
- JSON-RPC 2.0 标准协议
- 类型安全的参数验证

#### 不同角色的价值

**对开发者**
- 减少 80% 的重复工作：一次开发，多平台复用
- 降低学习曲线：统一的开发模式和 API
- 丰富的生态：100+ 现成的 MCP 服务器可直接使用

**对企业**
- 数据安全：敏感数据留在本地，精确控制访问权限  
- 降低成本：避免厂商锁定，灵活选择 AI 模型
- 快速集成：标准化接口，加速 AI 项目落地

**对用户**
- 更智能的 AI：能访问实时数据和专业工具
- 无缝体验：在不同应用间保持上下文连续性
- 隐私保护：数据处理透明可控

---

## 2. MCP 怎么工作

### 2.1 三大核心原语

MCP 定义了三种核心原语，涵盖 AI 与外部系统交互的主要场景：

#### Tools (工具) - 让AI执行操作

**概念**：可执行的函数，AI 可以调用来执行具体操作

**特点**：
- **需要用户授权**：确保安全性
- **可以修改状态**：能够执行写操作  
- **支持复杂参数**：类型检查和验证
- **返回结构化数据**：JSON 或文本格式

**示例场景**：
```python
@mcp.tool()
def search_files(pattern: str, directory: str = ".") -> str:
    """在指定目录中搜索文件"""
    # 实际搜索逻辑...
    return "找到的文件列表"
```

#### Resources (资源) - 为AI提供上下文

**概念**：为 AI 提供上下文信息的只读数据源

**特点**：
- 📖 **只读访问**：不能修改数据
- **标准化URI**：如 `config://app-settings`
- **支持订阅**：可以监听资源变化
- **结构化数据**：通常返回 JSON 格式

**示例场景**：
```python
@mcp.resource("config://app-settings")
def get_app_settings() -> str:
    """获取应用程序配置信息"""
    return json.dumps(config_data)
```

#### 💬 Prompts (提示模板) - 标准化交互

**概念**：可重用的交互模板，帮助构建标准化的提示

**特点**：
- **参数化模板**：支持动态参数
- **可重用性**：标准化的提示格式
- **最佳实践**：集成专业知识
- **自定义格式**：灵活的输出要求

**示例场景**：
```python
@mcp.prompt()
def code_review_prompt(code: str, language: str) -> str:
    """代码审查提示模板"""
    return f"请审查以下{language}代码：\n{code}"
```

### 2.2 双向通信机制

#### 分层架构设计

MCP采用**双层架构**设计，将协议逻辑与传输方式解耦：

**数据层（内层）**：定义消息结构（JSON-RPC 2.0）
**传输层（外层）**：STDIO（本地）+ HTTP/SSE（远程）

#### 客户端原语

除了服务器提供的工具，MCP还支持**反向能力**：

**Sampling（AI推理）**：服务器请求AI生成内容
**Elicitation（用户交互）**：服务器请求用户确认
**Logging（日志记录）**：服务器发送日志信息

#### 实时通知

**动态更新能力**：
```
传统方式：需要重启应用才能识别新工具
MCP方式：运行时动态加载新工具，无需重启
```

### 2.3 AI工具选择机制详解

#### 工具选择的基本原理

**核心机制**: AI模型通过 **Prompt Engineering** 来理解和选择工具，而非魔法！

<details>
<summary>点击查看：工具发现的代码实现</summary>

```python
# 1. 系统收集所有可用工具的描述
all_tools = []
for server in mcp_servers:
    tools = await server.list_tools()
    all_tools.extend(tools)

# 2. 将工具信息格式化为文本描述
tools_description = "\n".join([
    f"Tool: {tool.name}\n"
    f"Description: {tool.description}\n" 
    f"Arguments: {tool.format_arguments()}"
    for tool in all_tools
])

# 3. 构造系统提示，告诉AI有哪些工具可用
system_message = f"""
You are a helpful assistant with access to these tools:

{tools_description}

Choose the appropriate tool based on the user's question.
When you need to use a tool, respond with JSON format:
{{"tool": "tool-name", "arguments": {{"param": "value"}}}}
"""
```
</details>

#### 完整的工具调用流程

```
步骤1: 工具发现阶段
┌─────────────────────────────────────────────┐
│ MCP Client 向所有 Server 请求工具列表        │
│ └─ await server.list_tools()                │
└─────────────────────────────────────────────┘
                    ↓
步骤2: 工具描述生成
┌─────────────────────────────────────────────┐
│ 将工具信息转换为LLM可理解的文本描述          │
│ ├─ 工具名称 (from function name)             │
│ ├─ 功能描述 (from docstring)                │
│ └─ 参数说明 (from type annotations)         │
└─────────────────────────────────────────────┘
                    ↓
步骤3: AI决策阶段  
┌─────────────────────────────────────────────┐
│ AI基于用户请求 + 工具描述做出选择决策         │
│ ├─ 分析用户意图                             │
│ ├─ 匹配合适工具                             │
│ └─ 生成结构化调用请求                        │
└─────────────────────────────────────────────┘
                    ↓
步骤4: 工具执行阶段
┌─────────────────────────────────────────────┐
│ MCP Client 执行选定的工具                   │
│ ├─ JSON解析和参数验证                        │
│ ├─ 调用对应的MCP Server                     │
│ └─ 获取执行结果                             │
└─────────────────────────────────────────────┘
                    ↓
步骤5: 结果处理阶段
┌─────────────────────────────────────────────┐
│ 将工具执行结果反馈给AI生成最终回复           │
│ └─ AI将原始数据转换为自然语言回复            │
└─────────────────────────────────────────────┘
```

#### 工具描述是如何生成的？

从Python代码角度看，工具的描述信息来源于：

<details>
<summary>点击查看：工具描述自动生成机制</summary>

```python
@mcp.tool()
def search_files(pattern: str, directory: str = ".") -> str:
    """在指定目录中搜索文件模式
    
    Args:
        pattern: 搜索模式，支持通配符
        directory: 搜索目录，默认当前目录
        
    Returns:
        找到的文件列表，每行一个文件路径
    """
    import glob
    files = glob.glob(f"{directory}/{pattern}")
    return "\n".join(sorted(files))

# 自动转换为工具描述：
# Tool: search_files
# Description: 在指定目录中搜索文件模式
# Arguments:
# - pattern: 搜索模式，支持通配符 (required)  
# - directory: 搜索目录，默认当前目录 (optional)
```
</details>

#### 错误处理：AI幻觉怎么办？

<details>
<summary>点击查看：错误处理和验证机制</summary>

```python
async def process_llm_response(llm_response: str):
    try:
        # 尝试解析JSON格式的工具调用
        tool_call = json.loads(llm_response)
        tool_name = tool_call.get("tool")
        arguments = tool_call.get("arguments", {})
        
        # 验证工具是否存在
        if tool_name not in available_tools:
            return "Error: Tool not found, please use available tools only"
            
        # 执行工具调用
        result = await execute_tool(tool_name, arguments)
        return result
        
    except json.JSONDecodeError:
        # 不是工具调用，直接返回自然语言回复
        return llm_response
    except Exception as e:
        # 工具执行失败，返回错误信息
        return f"Tool execution failed: {str(e)}"
```
</details>

---

## 3. MCP 安装配置指南

### 3.1 claude mcp 命令概述

#### 核心命令介绍

`claude mcp` 是 Claude Code 提供的专用命令行工具，用于管理 MCP 服务器的完整生命周期。

**命令结构**：
```bash
claude mcp [子命令] [选项] [参数...]
```

**主要子命令**：
```bash
claude mcp add        # 添加MCP服务器
claude mcp list       # 列出所有配置的服务器
claude mcp get        # 查看特定服务器详情
claude mcp remove     # 删除MCP服务器
claude mcp serve      # 将Claude Code作为MCP服务器运行
claude mcp reset-project-choices  # 重置项目范围的批准选择
```

#### 常用命令参数详解

<details>
<summary>📋 点击查看：命令参数完整说明</summary>

**claude mcp add 参数**：
```bash
claude mcp add [选项] <name> [command] [args...]
claude mcp add --transport <type> [选项] <name> <url>

# 通用选项
-s, --scope <scope>          # 设置范围：local（默认）/project/user
-e, --env <key=value>        # 设置环境变量
--transport <type>           # 传输类型：stdio（默认）/sse/http

# STDIO 特定参数
<command>                    # 服务器启动命令
[args...]                   # 命令参数

# SSE/HTTP 特定参数  
<url>                       # 服务器URL
--header <key=value>        # 设置HTTP请求头（HTTP传输）
```

**claude mcp list 参数**：
```bash
claude mcp list [选项]

-s, --scope <scope>         # 仅显示特定范围的服务器
--format <format>           # 输出格式：table（默认）/json
```

**claude mcp remove 参数**：
```bash
claude mcp remove [选项] <name>

-s, --scope <scope>         # 指定要删除的服务器范围
--force                     # 强制删除，无需确认
```

**claude mcp serve 参数**：
```bash
claude mcp serve [选项]

--stdio                     # STDIO模式（默认）
--http                      # HTTP模式
--host <host>               # HTTP监听主机（默认：localhost）
--port <port>               # HTTP监听端口（默认：3000）
```

**导入导出命令**：
```bash
# 从JSON导入
claude mcp add-from-json <file-or-url>

# 从Claude Desktop导入  
claude mcp import-from-claude-desktop [选项]
--server <name>             # 仅导入特定服务器
--preserve-scope            # 保持原有作用域设置
```

</details>

### 3.2 配置管理基础

#### MCP 安装范围详解

MCP 服务器可以在三个不同的范围级别配置，了解这些范围有助于选择最佳配置方式：

**🏠 本地范围（Local）**：
- **存储位置**：项目特定用户设置  
- **适用场景**：个人开发、实验配置、敏感凭据
- **访问权限**：仅当前项目目录可用
- **命令示例**：`claude mcp add -s local my-server`

**👥 项目范围（Project）**：
- **存储位置**：项目根目录的 `.mcp.json` 文件
- **适用场景**：团队共享、项目特定工具、版本控制
- **访问权限**：所有团队成员（需要批准）
- **命令示例**：`claude mcp add -s project team-tools`

**👤 用户范围（User）**：
- **存储位置**：用户级配置文件
- **适用场景**：个人工具、开发环境、跨项目服务
- **访问权限**：用户所有项目可用
- **命令示例**：`claude mcp add -s user dev-tools`

#### 🌐 环境变量扩展支持

Claude Code 在配置文件中支持环境变量扩展，提供灵活的配置管理：

**支持语法**：
```bash
${VAR}              # 环境变量VAR的值
${VAR:-default}     # VAR的值，如果未设置则使用default
```

**可扩展位置**：
- `command` - 服务器可执行文件路径
- `args` - 命令行参数  
- `env` - 环境变量
- `url` - SSE/HTTP服务器URL  
- `headers` - 身份验证Headers

**实际应用示例**：
```json
{
  "mcpServers": {
    "my-server": {
      "command": "${PYTHON_PATH:-python3}",
      "args": ["${PROJECT_ROOT}/server.py"],
      "env": {
        "API_KEY": "${API_KEY}",
        "LOG_LEVEL": "${LOG_LEVEL:-info}"
      }
    }
  }
}
```

#### 🔄 范围优先级和冲突解决

当多个范围中存在同名服务器时，系统按以下优先级解决冲突：

```
Local (本地) > Project (项目) > User (用户)
```

这确保个人配置可以覆盖共享配置，提供最大的灵活性。

### 3.3 安装方式一：Claude Desktop导入

**适用场景**：已在 Claude Desktop 中配置了 MCP 服务器，希望在 Claude Code 中复用

<details>
<summary>📋 点击查看：Claude Desktop导入详细步骤</summary>

**Step 1: 检查 Claude Desktop 配置**
```bash
# 查看 Claude Desktop 配置文件位置
# macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
# Windows: %APPDATA%/Claude/claude_desktop_config.json

# 检查现有配置
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | jq .mcpServers
```

**Step 2: 导入所有配置**
```bash
# 导入所有Claude Desktop的MCP配置
claude mcp import-from-claude-desktop

# 查看导入结果
claude mcp list
```

**Step 3: 选择性导入**
```bash
# 仅导入特定服务器
claude mcp import-from-claude-desktop --server filesystem --server github

# 导入时保持原有作用域设置
claude mcp import-from-claude-desktop --preserve-scope
```

**Step 4: 验证导入结果**
```bash
# 列出所有导入的服务器
claude mcp list

# 查看特定服务器配置
claude mcp get filesystem

# 在Claude Code中测试
/mcp
```

</details>

### 3.4 安装方式二：JSON配置方式

**适用场景**：批量配置、团队协作、配置文件管理

<details>
<summary>📋 点击查看：JSON配置详细方法</summary>

**方法一：从JSON文件导入**
```bash
# 从本地JSON文件添加配置
claude mcp add-from-json ./mcp-config.json

# 从远程URL添加配置
claude mcp add-from-json https://example.com/team-mcp-config.json
```

**方法二：直接编辑配置文件**

**全局配置文件位置**：
```bash
# macOS/Linux
~/.claude.json

# Windows  
%USERPROFILE%\.claude.json
```

**项目配置文件**：
```bash
# 项目根目录
.mcp.json
```

**标准JSON格式**：
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "${HOME}/Documents"],
      "env": {}
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "sentry": {
      "transport": "http",
      "url": "https://mcp.sentry.dev/mcp",
      "headers": {
        "Authorization": "Bearer ${SENTRY_TOKEN}"
      }
    }
  }
}
```

**团队协作配置示例**：
```json
{
  "mcpServers": {
    "team-database": {
      "command": "${PROJECT_PYTHON_PATH:-python}",
      "args": ["-m", "custom_mcp_server"],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}",
        "API_KEY": "${API_KEY:-development-key}"
      }
    },
    "shared-tools": {
      "command": "${HOME}/.local/bin/team-tools",
      "args": ["--config", "${PROJECT_ROOT}/config.yaml"],
      "env": {
        "TEAM_ID": "${TEAM_ID}",
        "ENV": "${ENVIRONMENT:-development}"
      }
    }
  }
}
```

**配置后重启Claude Code使配置生效**

</details>

### 3.5 安装方式三：命令行方式

**适用场景**：快速安装、单个服务器配置、脚本自动化

#### 3.5.1 STDIO服务器（本地进程）

**适用场景**：需要直接系统访问或自定义脚本的工具

<details>
<summary>📋 点击查看：STDIO服务器配置详解</summary>

**基本语法**：
```bash
claude mcp add [选项] <name> <command> [args...]
```

**常用STDIO服务器示例**：
```bash
# 文件系统访问（最常用）
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem ~/Documents

# GitHub集成（需要Token）
claude mcp add github --env GITHUB_TOKEN=ghp_xxxx -- npx -y @modelcontextprotocol/server-github

# Airtable数据库
claude mcp add airtable --env AIRTABLE_API_KEY=key123 -- npx -y airtable-mcp-server

# ClickUp项目管理
claude mcp add clickup --env CLICKUP_API_KEY=pk_123 --env CLICKUP_TEAM_ID=456 -- npx -y @hauptsache.net/clickup-mcp
```

**不同范围的配置**：
```bash
# 本地范围（默认）- 仅当前项目
claude mcp add -s local my-server -- npx -y @example/server

# 项目范围 - 团队共享，存储在.mcp.json
claude mcp add -s project shared-db -- npx -y @team/database-server

# 用户范围 - 跨项目可用
claude mcp add -s user dev-tools -- npx -y @personal/dev-server
```

</details>

#### 3.5.2 SSE服务器（实时流连接）

**适用场景**：需要实时更新的云服务

<details>
<summary>📋 点击查看：SSE服务器配置详解</summary>

**基本语法**：
```bash
claude mcp add --transport sse [选项] <name> <url>
```

**官方SSE服务器示例**：
```bash
# Asana工作空间项目管理
claude mcp add --transport sse asana https://mcp.asana.com/sse

# Atlassian Jira和Confluence
claude mcp add --transport sse atlassian https://mcp.atlassian.com/v1/sse

# Linear问题跟踪
claude mcp add --transport sse linear https://mcp.linear.app/sse

# Monday.com看板管理
claude mcp add --transport sse monday https://mcp.monday.com/sse

# Plaid银行数据
claude mcp add --transport sse plaid https://api.dashboard.plaid.com/mcp/sse

# Square支付API
claude mcp add --transport sse square https://mcp.squareup.com/sse

# InVideo视频创建
claude mcp add --transport sse invideo https://mcp.invideo.io/sse
```

**带作用域的SSE配置**：
```bash
# 用户范围SSE服务器
claude mcp add -s user --transport sse asana https://mcp.asana.com/sse

# 项目范围SSE服务器  
claude mcp add -s project --transport sse linear https://mcp.linear.app/sse
```

</details>

#### 3.5.3 HTTP服务器（标准请求响应）

**适用场景**：REST API和标准Web服务

<details>
<summary>📋 点击查看：HTTP服务器配置详解</summary>

**基本语法**：
```bash
claude mcp add --transport http [选项] <name> <url>
```

**官方HTTP服务器示例**：
```bash
# Sentry错误监控
claude mcp add --transport http sentry https://mcp.sentry.dev/mcp

# Socket依赖安全分析
claude mcp add --transport http socket https://mcp.socket.dev/

# HuggingFace AI模型
claude mcp add --transport http hugging-face https://huggingface.co/mcp

# Jam调试记录
claude mcp add --transport http jam https://mcp.jam.dev/mcp

# Intercom客户服务
claude mcp add --transport http intercom https://mcp.intercom.com/mcp

# Notion文档管理
claude mcp add --transport http notion https://mcp.notion.com/mcp

# Box企业内容
claude mcp add --transport http box https://mcp.box.com/

# Fireflies会议分析
claude mcp add --transport http fireflies https://api.fireflies.ai/mcp

# HubSpot CRM
claude mcp add --transport http hubspot https://mcp.hubspot.com/anthropic

# PayPal支付
claude mcp add --transport http paypal https://mcp.paypal.com/mcp

# Stripe财务
claude mcp add --transport http stripe https://mcp.stripe.com

# Figma设计（需要本地Dev Mode服务器）
claude mcp add --transport http figma-dev-mode-mcp-server http://127.0.0.1:3845/mcp

# Canva设计
claude mcp add --transport http canva https://mcp.canva.com/mcp

# Netlify部署
claude mcp add --transport http netlify https://netlify-mcp.netlify.app/mcp

# Vercel项目管理
claude mcp add --transport http vercel https://mcp.vercel.com/

# Stytch认证
claude mcp add --transport http stytch http://mcp.stytch.dev/mcp
```

**需要认证的HTTP服务器**：
```bash
# 许多HTTP服务器需要OAuth认证
# Claude Code会自动处理OAuth流程，打开浏览器进行授权
claude mcp add --transport http github-enterprise https://api.github.company.com/mcp
```

</details>

#### 配置验证和管理

**验证配置**：
```bash
# 列出所有配置的服务器
claude mcp list

# 查看特定服务器详情
claude mcp get server-name

# 在Claude Code中检查状态
/mcp
```

**配置管理**：
```bash
# 删除服务器（指定范围）
claude mcp remove server-name -s local
claude mcp remove team-tools -s project
claude mcp remove dev-tools -s user

# 重置项目范围批准
claude mcp reset-project-choices
```

**使用MCP功能**：
```bash
# 引用MCP资源
@resource-name
@server-name/resource-path

# 使用MCP提示命令
/prompt-name
/code-review "review this function"

# 列出可用功能
/mcp resources
/mcp prompts
```

---

## 4. 开发实战指南 (动手实践)

### 4.1 开发环境配置

#### 🐍 Python 开发环境

```bash
# 1. 安装现代 Python 包管理器
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 创建项目
mkdir my-mcp-server && cd my-mcp-server
uv init --python=3.11

# 3. 安装依赖
uv add "mcp[cli]" "fastapi" "pydantic" "aiofiles"

# 4. 创建项目结构
mkdir -p src/{server,client,tools,config}
touch src/server/__init__.py
touch src/tools/__init__.py
```

#### 📁 推荐的项目结构

```
my-mcp-server/
├── pyproject.toml              # 项目配置
├── README.md                   # 项目说明
├── .env.example               # 环境变量模板
├── requirements.txt           # 依赖列表
├── src/
│   ├── server/                # 服务器实现
│   │   ├── __init__.py
│   │   ├── main.py           # 主服务器逻辑
│   │   └── config.py         # 配置管理
│   ├── tools/                 # 工具实现
│   │   ├── __init__.py
│   │   ├── file_tools.py     # 文件操作工具
│   │   ├── api_tools.py      # API 集成工具
│   │   └── data_tools.py     # 数据处理工具
│   └── client/                # 客户端工具
│       ├── __init__.py
│       └── test_client.py    # 测试客户端
├── tests/                     # 测试代码
│   ├── test_tools.py
│   └── test_server.py
└── docs/                      # 文档
    ├── api.md
    └── examples.md
```

### 4.2 5分钟创建第一个MCP工具

#### 目标：创建一个文件计数器
让Claude能够统计你桌面上的文件数量

#### 三步搞定

**Step 1: 环境搭建**
```bash
# 安装依赖
pip install "mcp[cli]"

# 创建文件
touch file_counter.py
```

**Step 2: 核心代码**

<details>
<summary>📄 点击展开完整代码 (file_counter.py)</summary>

```python
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# 创建MCP服务器
mcp = FastMCP("文件计数器")

@mcp.tool()
def count_files(directory: str = "Desktop") -> str:
    """统计指定目录的文件数量
    
    Args:
        directory: 目录名称，默认Desktop
        
    Returns:
        文件统计结果
    """
    username = os.getenv("USER") or os.getenv("USERNAME")
    dir_path = Path(f"/Users/{username}/{directory}")
    
    if not dir_path.exists():
        return f"目录 {directory} 不存在"
    
    files = list(dir_path.glob("*"))
    file_count = len([f for f in files if f.is_file()])
    folder_count = len([f for f in files if f.is_dir()])
    
    return f"{directory} 目录统计:\n📄 文件: {file_count} 个\n📁 文件夹: {folder_count} 个"

if __name__ == "__main__":
    mcp.run()
```

</details>

**Step 3: 配置Claude Code**

<details>
<summary>点击展开配置步骤</summary>

```bash
# 在当前项目中添加MCP服务器
claude mcp add file-counter -- python file_counter.py

# 验证配置
claude mcp list

# 在Claude Code中测试
/mcp
```

</details>

#### 测试效果

在Claude中说："帮我统计一下桌面文件数量"

Claude会自动调用你的工具并返回结果！

#### 核心要点
- **装饰器 `@mcp.tool()`**：将普通函数变成MCP工具
- **文档字符串**：AI理解工具功能的关键
- **类型注解**：确保参数验证和错误处理

---

## 5. MCP生态总览

### 热门MCP项目推荐

#### 官方维护项目

| 项目名称 | 功能描述 | 维护状态 |
|---------|---------|---------|
| [**filesystem**](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) | 文件系统操作 | 官方维护 |
| [**brave-search**](https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search) | Brave搜索引擎 | 官方维护 |
| [**slack**](https://github.com/modelcontextprotocol/servers/tree/main/src/slack) | Slack消息集成 | 官方维护 |
| [**postgres**](https://github.com/modelcontextprotocol/servers/tree/main/src/postgres) | PostgreSQL数据库 | 官方维护 |
| [**git**](https://github.com/modelcontextprotocol/servers/tree/main/src/git) | Git版本控制 | 官方维护 |

#### 社区热门项目

| 项目名称 | 功能描述 | Stars | 类型 |
|---------|---------|-------|------|
| [**playwright**](https://github.com/browserbase/mcp-server-playwright) | 浏览器自动化 | 19k+ | 网页操作 |
| [**github**](https://github.com/github/gh-mcp) | GitHub官方服务器 | 22k+ | 代码管理 |
| [**aws**](https://github.com/aws/mcp-server-aws) | AWS云服务集成 | 6.2k+ | 云服务 |
| [**browser-mcp**](https://github.com/UI-TARS/browser-mcp) | 浏览器控制 | 4.1k+ | 网页交互 |
| [**whatsapp**](https://github.com/semioz/whatsapp-mcp-server) | WhatsApp消息 | 4.8k+ | 消息通信 |

#### 工具与服务分类

| 项目名称 | 功能描述 | 适用场景 |
|---------|---------|---------|
| [**linear**](https://github.com/abdulrahman305/mcp-server-linear) | Linear项目管理 | 任务跟踪、项目协作 |
| [**jira**](https://github.com/joshuarileydev/mcp-server-jira) | Jira集成 | Issue管理、敏捷开发 |
| [**docker**](https://github.com/donghyun-chae/mcp-server-docker) | Docker容器管理 | 容器操作、部署自动化 |
| [**salesforce**](https://github.com/nabeelkausari/mcp-server-salesforce) | CRM系统集成 | 客户关系管理 |
| [**notion**](https://github.com/v-3/notion-mcp-server) | Notion知识库 | 文档管理、知识协作 |
| [**gmail**](https://github.com/adhikasp/mcp-server-gmail) | Gmail邮件服务 | 邮件自动化处理 |
| [**screenshot**](https://github.com/BrowserLoop/mcp-server-screenshot) | 屏幕截图 | 自动截图、图像分析 |
| [**sqlite**](https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite) | SQLite数据库 | 本地数据查询管理 |

### Claude Desktop兼容性

已验证兼容的MCP服务器包括：
- **文件操作**: filesystem, git, sqlite
- **网络服务**: brave-search, fetch, slack  
- **数据处理**: postgres, memory, puppeteer

<details>
<summary>查看Claude Desktop配置示例</summary>

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/username"]
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": { "BRAVE_API_KEY": "your-api-key" }
    },
    "postgres": {
      "command": "npx", 
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": { "POSTGRES_CONNECTION_STRING": "postgresql://user:pass@localhost/db" }
    }
  }
}
```

</details>

### 生态发展现状

#### 增长数据

| 时间 | 项目数量 | 发展阶段 |
|------|---------|---------|
| 2024年11月 | 10个 | Anthropic发布 |
| 2024年12月 | 100个 | 早期采用 |
| 2025年01月 | 500+ | 社区爆发 |
| 2025年03月 | 1000+ | 企业采用 |

#### 编程语言分布

| 语言 | 占比 | 项目数 |
|------|------|-------|
| Python | 45% | 250+ |
| TypeScript/JavaScript | 35% | 200+ |
| Go | 12% | 60+ |
| Rust | 5% | 30+ |
| 其他 | 3% | 15+ |

### 项目选择指南

#### 评估标准

| 标准 | 重要性 | 评估要点 |
|------|-------|---------|
| 活跃度 | 高 | 更新频率、Issue响应 |
| 文档质量 | 高 | README、示例完整性 |
| 社区支持 | 中 | Star数、贡献者数量 |
| 功能匹配 | 高 | 业务需求契合度 |

#### 发现资源

**官方资源**：
- [Awesome MCP Servers](https://github.com/modelcontextprotocol/servers)
- [MCP官网项目列表](https://modelcontextprotocol.io/servers)

**社区资源**：
- GitHub Topic: `mcp-server`
- Reddit: r/ModelContextProtocol

---

## 总结

### 核心要点回顾

1. **什么是MCP**：标准化AI与外部工具连接的开放协议
2. **为什么需要**：解决Function Call平台依赖和重复开发问题  
3. **如何使用**：装饰器 + 配置文件创建强大工具
4. **生态现状**：1000+项目，企业级应用快速落地

### MCP的价值

MCP带来的不只是技术协议，更是AI应用开发范式的转变：

- **从平台绑定到标准开放**
- **从重复开发到生态共享**  
- **从数据上云到本地安全**
- **从割裂工具到统一接口**

未来，每个AI应用都将支持MCP，每个开发者都能轻松为AI赋能。这是开放生态的胜利。