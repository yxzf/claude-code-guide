# desktop_txt_server.py - 桌面txt文件统计MCP服务器

# =============================================================================
# 导入模块
# =============================================================================
import os
import platform
from pathlib import Path
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP

# =============================================================================
# 初始化MCP服务器
# =============================================================================
# 创建FastMCP服务器实例，名称为"desktop-txt-manager"
mcp = FastMCP("desktop-txt-manager")

# =============================================================================
# 辅助函数 - 获取桌面路径
# =============================================================================
def get_desktop_path() -> Path:
    """
    跨平台获取用户桌面路径
    
    Returns:
        Path: 桌面文件夹的路径对象
        
    支持的操作系统：
    - Windows: ~/Desktop
    - macOS: ~/Desktop  
    - Linux: ~/Desktop
    """
    # 获取用户主目录
    home = Path.home()
    
    # 拼接桌面路径（在大多数系统中桌面文件夹都叫"Desktop"）
    desktop_path = home / "Desktop"
    
    # 如果Desktop文件夹不存在，尝试其他可能的名称
    if not desktop_path.exists():
        # 某些中文系统可能使用"桌面"
        alt_desktop = home / "桌面"
        if alt_desktop.exists():
            return alt_desktop
        
        # 如果都不存在，返回主目录作为fallback
        return home
    
    return desktop_path

# =============================================================================
# 辅助函数 - 文件扫描和过滤
# =============================================================================
async def scan_txt_files(directory: Path) -> List[Dict[str, Any]]:
    """
    异步扫描指定目录下的所有txt文件
    
    Args:
        directory: 要扫描的目录路径
        
    Returns:
        List[Dict]: 包含文件信息的字典列表
        
    异步编程说明：
    - 虽然文件系统操作通常是同步的，但我们使用async来保持一致性
    - 在实际项目中，可以使用aiofiles等库进行真正的异步文件操作
    - 这里演示如何在MCP中正确使用异步函数
    """
    txt_files = []
    
    try:
        # 遍历目录中的所有文件
        for file_path in directory.iterdir():
            # 检查是否为文件（排除文件夹）且扩展名为.txt
            if file_path.is_file() and file_path.suffix.lower() == '.txt':
                # 获取文件详细信息
                file_info = {
                    'name': file_path.name,           # 文件名（包含扩展名）
                    'stem': file_path.stem,           # 文件名（不包含扩展名）
                    'full_path': str(file_path),      # 完整路径
                    'size_bytes': file_path.stat().st_size,  # 文件大小（字节）
                    'size_kb': round(file_path.stat().st_size / 1024, 2),  # 文件大小（KB）
                }
                txt_files.append(file_info)
                
    except PermissionError:
        # 处理权限错误（某些系统文件夹可能无法访问）
        pass
    except Exception as e:
        # 处理其他可能的文件系统错误
        pass
    
    # 按文件名排序，提供一致的输出
    txt_files.sort(key=lambda x: x['name'].lower())
    
    return txt_files

# =============================================================================
# MCP工具 1: 统计txt文件数量
# =============================================================================
@mcp.tool()
async def count_desktop_txt_files() -> str:
    """
    统计当前用户桌面上的txt文件数量
    
    Returns:
        str: 包含文件数量统计的字符串
        
    MCP工具特点：
    1. @mcp.tool() 装饰器自动注册为可调用工具
    2. 函数名会成为工具名称 
    3. docstring会成为工具描述
    4. 无需参数的简单工具
    """
    # 获取桌面路径
    desktop_path = get_desktop_path()
    
    # 异步扫描txt文件
    txt_files = await scan_txt_files(desktop_path)
    
    # 格式化输出结果
    count = len(txt_files)
    
    if count == 0:
        return f"桌面路径: {desktop_path}\n📁 未找到任何txt文件"
    
    # 计算总文件大小
    total_size_kb = sum(file_info['size_kb'] for file_info in txt_files)
    
    result = f"""
📁 桌面路径: {desktop_path}
📊 txt文件统计结果:
   • 文件数量: {count} 个
   • 总大小: {total_size_kb:.2f} KB
   • 平均大小: {total_size_kb/count:.2f} KB
"""
    return result.strip()

# =============================================================================
# MCP工具 2: 获取txt文件列表
# =============================================================================
@mcp.tool()
async def list_desktop_txt_files(include_details: bool = False) -> str:
    """
    获取桌面上所有txt文件的名称列表
    
    Args:
        include_details: 是否包含详细信息（文件大小等），默认为False
        
    Returns:
        str: 格式化的文件列表字符串
        
    参数说明：
    - include_details参数演示了如何在MCP工具中使用可选参数
    - 类型提示bool告诉MCP这是一个布尔值参数
    - 默认值False使该参数可选
    """
    # 获取桌面路径
    desktop_path = get_desktop_path()
    
    # 异步扫描txt文件
    txt_files = await scan_txt_files(desktop_path)
    
    if not txt_files:
        return f"📁 桌面路径: {desktop_path}\n❌ 未找到任何txt文件"
    
    # 构建结果字符串
    result = [f"📁 桌面路径: {desktop_path}"]
    result.append(f"📋 找到 {len(txt_files)} 个txt文件:\n")
    
    # 根据include_details参数决定输出格式
    if include_details:
        # 详细模式：显示文件名、大小等信息
        result.append("📄 详细信息:")
        for i, file_info in enumerate(txt_files, 1):
            file_line = f"   {i:2d}. {file_info['name']}"
            file_line += f" ({file_info['size_kb']} KB)"
            result.append(file_line)
    else:
        # 简单模式：只显示文件名
        result.append("📝 文件列表:")
        for i, file_info in enumerate(txt_files, 1):
            result.append(f"   {i:2d}. {file_info['name']}")
    
    return "\n".join(result)

# =============================================================================
# MCP工具 3: 查找特定txt文件
# =============================================================================
@mcp.tool()
async def find_txt_file(filename_pattern: str) -> str:
    """
    在桌面上查找匹配指定模式的txt文件
    
    Args:
        filename_pattern: 文件名搜索模式（支持部分匹配，不区分大小写）
        
    Returns:
        str: 匹配的文件信息
        
    搜索功能：
    - 不区分大小写的部分匹配
    - 支持搜索文件名的任意部分
    - 返回详细的匹配结果
    """
    # 获取桌面路径
    desktop_path = get_desktop_path()
    
    # 异步扫描txt文件
    txt_files = await scan_txt_files(desktop_path)
    
    if not txt_files:
        return f"📁 桌面路径: {desktop_path}\n❌ 桌面上没有txt文件"
    
    # 搜索匹配的文件（不区分大小写）
    pattern_lower = filename_pattern.lower()
    matched_files = [
        file_info for file_info in txt_files 
        if pattern_lower in file_info['name'].lower()
    ]
    
    if not matched_files:
        return f"📁 桌面路径: {desktop_path}\n🔍 未找到包含 '{filename_pattern}' 的txt文件"
    
    # 构建搜索结果
    result = [f"📁 桌面路径: {desktop_path}"]
    result.append(f"🔍 搜索模式: '{filename_pattern}'")
    result.append(f"✅ 找到 {len(matched_files)} 个匹配的文件:\n")
    
    for i, file_info in enumerate(matched_files, 1):
        file_line = f"   {i}. {file_info['name']}"
        file_line += f" ({file_info['size_kb']} KB)"
        file_line += f"\n      路径: {file_info['full_path']}"
        result.append(file_line)
    
    return "\n".join(result)

# =============================================================================
# MCP工具 4: 获取系统信息
# =============================================================================
@mcp.tool()
async def get_system_info() -> str:
    """
    获取当前系统的基本信息
    
    Returns:
        str: 系统信息字符串
        
    用途：
    - 帮助调试不同操作系统的兼容性问题
    - 提供系统环境上下文
    - 验证桌面路径检测是否正确
    """
    desktop_path = get_desktop_path()
    
    # 检查桌面路径是否存在
    desktop_exists = desktop_path.exists()
    desktop_accessible = os.access(desktop_path, os.R_OK) if desktop_exists else False
    
    system_info = f"""
🖥️  系统信息:
   • 操作系统: {platform.system()}
   • 系统版本: {platform.release()}
   • Python版本: {platform.python_version()}
   • 用户主目录: {Path.home()}
   • 桌面路径: {desktop_path}
   • 桌面存在: {'✅ 是' if desktop_exists else '❌ 否'}
   • 桌面可读: {'✅ 是' if desktop_accessible else '❌ 否'}
"""
    
    return system_info.strip()

# =============================================================================
# 服务器启动
# =============================================================================
if __name__ == "__main__":
    """
    启动MCP服务器
    
    启动说明：
    1. 使用stdio传输协议与MCP客户端通信
    2. 服务器会注册4个工具：
       - count_desktop_txt_files: 统计txt文件数量
       - list_desktop_txt_files: 列出txt文件
       - find_txt_file: 查找特定txt文件
       - get_system_info: 获取系统信息
    3. 客户端可以通过MCP协议调用这些工具
    
    调试注意事项：
    - 不要使用print()输出调试信息！
    - 使用logging模块将调试信息输出到stderr
    - stdout专用于MCP协议通信
    """
    print("🚀 桌面txt文件管理MCP服务器启动中...", file=__import__('sys').stderr)
    print(f"📁 检测到的桌面路径: {get_desktop_path()}", file=__import__('sys').stderr)
    
    # 启动MCP服务器
    mcp.run(transport='stdio')

# =============================================================================
# 使用示例和扩展说明
# =============================================================================
"""
这个MCP服务器演示了以下概念：

1. 异步编程应用：
   - 所有工具函数都是异步的
   - 为未来的异步文件操作预留接口
   - 保持与MCP协议的一致性

2. MCP工具设计模式：
   - 简单工具：count_desktop_txt_files（无参数）
   - 带可选参数：list_desktop_txt_files
   - 带必需参数：find_txt_file
   - 系统工具：get_system_info

3. 错误处理：
   - 文件权限错误处理
   - 路径不存在的fallback机制
   - 空结果的友好提示

4. 跨平台兼容性：
   - 使用pathlib处理路径
   - 支持不同操作系统的桌面路径
   - 处理中文路径名

5. 用户体验优化：
   - 使用emoji使输出更友好
   - 提供详细的文件信息
   - 支持搜索和过滤功能

扩展建议：
- 添加文件内容搜索功能
- 支持其他文件类型
- 添加文件操作功能（重命名、删除等）
- 集成文件监控（检测文件变化）
"""