# 桌面txt文件统计 MCP服务器

一个基于Model Context Protocol (MCP)的Python服务器，用于统计和管理当前用户桌面上的txt文件。

## 🌟 功能特性

- **📊 文件统计**：统计桌面上txt文件的数量和总大小
- **📋 文件列表**：获取所有txt文件的详细列表
- **🔍 文件搜索**：按文件名模式查找特定txt文件
- **🖥️ 系统信息**：获取当前系统和桌面路径信息
- **🔄 异步处理**：使用Python异步编程提升性能
- **🌍 跨平台支持**：支持Windows、macOS、Linux

## 🛠️ 技术栈

- **Python 3.10+**
- **uv**：现代Python包管理器
- **MCP Framework 1.2.0+**
- **pathlib**：跨平台路径处理
- **asyncio**：异步编程支持

## 📦 快速开始

### 1. 安装uv（如果未安装）

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或者使用pip安装
pip install uv
```

### 2. 进入项目目录

```bash
cd mcp/demo/desktop-txt-stats
```

### 3. 安装依赖

```bash
# 使用uv安装依赖（推荐）
uv sync

# 或者手动安装MCP
uv add mcp>=1.2.0
```

### 4. 安装依赖

```bash
# 只安装核心依赖（推荐）
uv add mcp

# 或者完整同步（可能较慢）
uv sync
```

### 5. 测试服务器

```bash
# 方式1：使用简化启动脚本（推荐）
python run.py

# 方式2：直接运行
source .venv/bin/activate && python desktop_txt_server.py

# 方式3：使用uv（可能有依赖问题）
uv run desktop_txt_server.py
```

## 🚀 与Claude for Desktop集成

### 1. 配置Claude for Desktop

编辑Claude for Desktop配置文件：
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

### 2. 推荐配置（使用启动脚本）

```json
{
  "mcpServers": {
    "desktop-txt-stats": {
      "command": "python",
      "args": [
        "/绝对路径/到/mcp/demo/desktop-txt-stats/run.py"
      ]
    }
  }
}
```

### 3. 备用配置方式

```json
{
  "mcpServers": {
    "desktop-txt-stats": {
      "command": "python",
      "args": [
        "/绝对路径/到/mcp/demo/desktop-txt-stats/desktop_txt_server.py"
      ],
      "cwd": "/绝对路径/到/mcp/demo/desktop-txt-stats",
      "env": {
        "VIRTUAL_ENV": "/绝对路径/到/mcp/demo/desktop-txt-stats/.venv"
      }
    }
  }
}
```

### 4. 重启Claude for Desktop

保存配置文件后，重启Claude for Desktop应用。

## 🔧 可用工具

### 1. count_desktop_txt_files
统计桌面上txt文件的数量和总大小。

**示例使用**：
```
统计我桌面上有多少个txt文件
```

**返回信息**：
- 文件数量
- 总大小（KB）
- 平均文件大小

### 2. list_desktop_txt_files
获取桌面上所有txt文件的列表。

**参数**：
- `include_details` (可选): 是否包含文件大小等详细信息

**示例使用**：
```
列出我桌面上的所有txt文件
显示桌面txt文件的详细信息
```

### 3. find_txt_file
在桌面上查找匹配指定模式的txt文件。

**参数**：
- `filename_pattern` (必需): 文件名搜索模式

**示例使用**：
```
在桌面上找包含"笔记"的txt文件
查找名称包含"todo"的txt文件
```

### 4. get_system_info
获取当前系统的基本信息和桌面路径检测结果。

**示例使用**：
```
显示系统信息
检查桌面路径是否正确
```

## 📁 项目结构

```
desktop-txt-stats/
├── README.md                    # 项目说明
├── pyproject.toml              # uv项目配置
├── requirements.txt            # 依赖列表
├── desktop_txt_server.py       # MCP服务器主文件
├── run.py                      # 简化启动脚本
├── claude_config_example.json  # Claude配置示例
└── .venv/                      # 虚拟环境（uv创建）
```

## 💻 开发说明

### uv命令使用

```bash
# 安装新依赖
uv add package-name

# 安装开发依赖
uv add --dev pytest

# 运行脚本
uv run desktop_txt_server.py

# 运行测试
uv run pytest

# 格式化代码
uv run black .

# 代码检查
uv run ruff check .
```

### 代码结构详解

```python
# 1. MCP服务器初始化
mcp = FastMCP("desktop-txt-stats")

# 2. 工具注册
@mcp.tool()
async def count_desktop_txt_files() -> str:
    # 工具实现
    pass

# 3. 服务器启动
if __name__ == "__main__":
    mcp.run(transport='stdio')
```

## 🧪 测试和调试

### 本地测试

```bash
# 使用uv运行并查看调试信息
uv run desktop_txt_server.py

# 预期输出到stderr：
# 🚀 桌面txt文件管理MCP服务器启动中...
# 📁 检测到的桌面路径: /Users/username/Desktop
```

### 验证工具注册

启动服务器后，检查Claude for Desktop是否显示以下工具：
- count_desktop_txt_files
- list_desktop_txt_files  
- find_txt_file
- get_system_info

### 常见问题排查

1. **uv run 错误（build backend failed）**：
   ```bash
   # 解决方案：使用简化启动方式
   python run.py
   
   # 或者只安装核心依赖
   uv add mcp
   ```

2. **虚拟环境冲突**：
   ```bash
   # 清理环境变量
   unset VIRTUAL_ENV
   
   # 重新创建环境
   rm -rf .venv uv.lock
   uv add mcp
   ```

3. **工具未显示**：
   - 检查配置文件路径是否正确
   - 确认使用绝对路径
   - 推荐使用`run.py`启动脚本
   - 重启Claude for Desktop

4. **权限错误**：
   - 确保Python有权限访问桌面文件夹
   - 在macOS上可能需要授予"文件和文件夹"权限

5. **依赖下载慢**：
   - 使用`uv add mcp`而不是`uv sync`
   - 避免安装不必要的开发依赖

## 📚 学习要点

### 1. Python异步编程在MCP中的应用
- 所有工具函数使用`async def`定义
- 为未来的异步文件操作预留接口
- 保持与MCP协议的一致性

### 2. MCP工具设计模式
- **无参数工具**：`count_desktop_txt_files()`
- **可选参数**：`list_desktop_txt_files(include_details=False)`
- **必需参数**：`find_txt_file(filename_pattern)`
- **系统工具**：`get_system_info()`

### 3. uv项目管理
- 使用`pyproject.toml`配置项目
- `uv sync`安装依赖
- `uv run`执行脚本
- `[tool.uv]`部分配置开发依赖

## 🔮 扩展建议

1. **功能扩展**：
   - 添加文件内容搜索
   - 支持更多文件类型
   - 文件操作功能（重命名、删除）
   - 文件监控（检测变化）

2. **性能优化**：
   - 使用`aiofiles`实现真正的异步文件操作
   - 添加文件缓存机制
   - 支持大目录的分页处理

3. **安全增强**：
   - 添加文件访问权限检查
   - 限制可访问的目录范围
   - 添加操作日志记录

## 📄 许可证

MIT License - 可自由使用和修改。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！