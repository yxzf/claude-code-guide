# desktop_txt_server_full.py - 完整版MCP服务器（包含Tools、Resources、Prompts）

# =============================================================================
# 导入模块
# =============================================================================
import os
import json
import platform
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# =============================================================================
# 初始化MCP服务器
# =============================================================================
# 创建FastMCP服务器实例，名称为"desktop-txt-manager-full"
mcp = FastMCP("desktop-txt-manager-full")

# =============================================================================
# 辅助函数 - 获取桌面路径
# =============================================================================
def get_desktop_path() -> Path:
    """
    跨平台获取用户桌面路径
    
    Returns:
        Path: 桌面文件夹的路径对象
    """
    home = Path.home()
    desktop_path = home / "Desktop"
    
    if not desktop_path.exists():
        alt_desktop = home / "桌面"
        if alt_desktop.exists():
            return alt_desktop
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
    """
    txt_files = []
    
    try:
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() == '.txt':
                stat_info = file_path.stat()
                file_info = {
                    'name': file_path.name,
                    'stem': file_path.stem,
                    'full_path': str(file_path),
                    'size_bytes': stat_info.st_size,
                    'size_kb': round(stat_info.st_size / 1024, 2),
                    'modified_time': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                    'created_time': datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                }
                txt_files.append(file_info)
                
    except (PermissionError, Exception):
        pass
    
    # 按文件名排序
    txt_files.sort(key=lambda x: x['name'].lower())
    
    return txt_files

# =============================================================================
# RESOURCES - 提供可读取的数据源
# =============================================================================

@mcp.resource("desktop://txt-files")
async def get_txt_files_resource() -> str:
    """
    作为资源提供桌面txt文件列表
    
    Resources特点：
    - 类似文件系统的只读数据
    - 客户端可以订阅和读取
    - 支持URI标识
    - 适合提供静态或半静态数据
    """
    desktop_path = get_desktop_path()
    txt_files = await scan_txt_files(desktop_path)
    
    resource_data = {
        "type": "file_list",
        "path": str(desktop_path),
        "scan_time": datetime.now().isoformat(),
        "file_count": len(txt_files),
        "total_size_kb": sum(file_info['size_kb'] for file_info in txt_files),
        "files": txt_files
    }
    
    return json.dumps(resource_data, indent=2, ensure_ascii=False)

@mcp.resource("desktop://system-info")
async def get_system_info_resource() -> str:
    """
    作为资源提供系统信息
    """
    desktop_path = get_desktop_path()
    desktop_exists = desktop_path.exists()
    desktop_accessible = os.access(desktop_path, os.R_OK) if desktop_exists else False
    
    system_data = {
        "type": "system_info",
        "scan_time": datetime.now().isoformat(),
        "system": {
            "platform": platform.system(),
            "release": platform.release(),
            "python_version": platform.python_version(),
        },
        "paths": {
            "home_directory": str(Path.home()),
            "desktop_path": str(desktop_path),
            "desktop_exists": desktop_exists,
            "desktop_accessible": desktop_accessible
        }
    }
    
    return json.dumps(system_data, indent=2, ensure_ascii=False)

@mcp.resource("desktop://file-stats")
async def get_file_stats_resource() -> str:
    """
    作为资源提供文件统计信息
    """
    desktop_path = get_desktop_path()
    txt_files = await scan_txt_files(desktop_path)
    
    if not txt_files:
        stats_data = {
            "type": "file_statistics",
            "scan_time": datetime.now().isoformat(),
            "has_files": False,
            "message": "未找到txt文件"
        }
    else:
        # 计算统计信息
        total_size = sum(f['size_kb'] for f in txt_files)
        avg_size = total_size / len(txt_files) if txt_files else 0
        
        # 分析文件名模式
        naming_patterns = {
            "has_dates": any("20" in f['name'] for f in txt_files),
            "has_numbers": any(any(c.isdigit() for c in f['name']) for f in txt_files),
            "has_underscores": any("_" in f['name'] for f in txt_files),
            "has_chinese": any(any('\u4e00' <= c <= '\u9fff' for c in f['name']) for f in txt_files),
            "untitled_count": sum(1 for f in txt_files if 'untitled' in f['name'].lower())
        }
        
        stats_data = {
            "type": "file_statistics",
            "scan_time": datetime.now().isoformat(),
            "has_files": True,
            "summary": {
                "file_count": len(txt_files),
                "total_size_kb": round(total_size, 2),
                "average_size_kb": round(avg_size, 2),
                "largest_file": max(txt_files, key=lambda x: x['size_kb'])['name'],
                "smallest_file": min(txt_files, key=lambda x: x['size_kb'])['name']
            },
            "naming_analysis": naming_patterns,
            "recommendations": {
                "needs_renaming": naming_patterns["untitled_count"] > 0,
                "suggest_date_format": not naming_patterns["has_dates"],
                "suggest_categorization": len(txt_files) > 5
            }
        }
    
    return json.dumps(stats_data, indent=2, ensure_ascii=False)

# =============================================================================
# PROMPTS - 预定义的提示模板
# =============================================================================

@mcp.prompt()
async def desktop_organization_wizard() -> str:
    """
    桌面整理向导 - 基于实际文件数据的个性化建议
    
    Prompts特点：
    - 预定义的提示模板
    - 帮助用户快速开始特定任务
    - 可以包含动态数据
    - 引导用户进行特定类型的对话
    """
    desktop_path = get_desktop_path()
    txt_files = await scan_txt_files(desktop_path)
    
    if not txt_files:
        return """
我的桌面目前没有txt文件，但我想建立良好的文件管理习惯。

请为我提供：
1. 桌面文件管理的最佳实践
2. txt文件的命名规范建议
3. 如何建立有效的文件夹分类体系
4. 定期维护和清理的建议

我希望从零开始建立一个高效的文件管理系统。
"""
    
    # 分析当前文件情况
    total_size = sum(f['size_kb'] for f in txt_files)
    has_untitled = any('untitled' in f['name'].lower() for f in txt_files)
    has_single_char = any(len(f['stem']) == 1 for f in txt_files)
    
    file_list = "\n".join([
        f"  • {f['name']} ({f['size_kb']} KB) - 修改于 {f['modified_time'][:10]}"
        for f in txt_files[:10]  # 只显示前10个文件
    ])
    
    if len(txt_files) > 10:
        file_list += f"\n  ... 还有 {len(txt_files) - 10} 个文件"
    
    return f"""
我的桌面有 {len(txt_files)} 个txt文件需要整理：

📁 桌面路径：{desktop_path}
📊 总大小：{total_size:.2f} KB
📝 文件清单：
{file_list}

🔍 当前问题分析：
{'• 存在默认命名文件（如untitled.txt），需要重新命名' if has_untitled else ''}
{'• 存在单字符命名文件，建议使用更描述性的名称' if has_single_char else ''}
{'• 文件数量较多，建议进行分类整理' if len(txt_files) > 5 else ''}

请为我制定专属的整理方案：
1. 分析当前文件的命名模式和特点
2. 建议个性化的文件夹分类体系
3. 提供具体的重命名建议和命名规范
4. 制定定期维护和备份计划
5. 给出step-by-step的整理步骤

请考虑我的实际使用情况，提供最实用和可操作的建议。
"""

@mcp.prompt()
async def file_naming_consultant() -> str:
    """
    文件命名顾问 - 专业的命名规范建议
    """
    desktop_path = get_desktop_path()
    txt_files = await scan_txt_files(desktop_path)
    
    if not txt_files:
        return """
我需要学习专业的txt文件命名规范。

请教我：
1. 通用的文件命名最佳实践
2. 不同类型txt文件的命名方案（笔记、清单、草稿等）
3. 日期和版本号的标准格式
4. 如何避免文件名冲突
5. 跨平台兼容的命名规则

我希望建立一套标准化的命名体系。
"""
    
    # 分析命名问题
    naming_issues = []
    good_examples = []
    bad_examples = []
    
    for file in txt_files:
        name = file['name']
        stem = file['stem']
        
        if 'untitled' in name.lower() or len(stem) <= 2:
            bad_examples.append(f"❌ {name}")
        elif '_' in name and len(stem) > 5:
            good_examples.append(f"✅ {name}")
        elif any(char in name for char in ['日期', '笔记', '清单', '2024', '2025']):
            good_examples.append(f"✅ {name}")
        else:
            naming_issues.append(name)
    
    examples_text = ""
    if good_examples:
        examples_text += f"\n✅ 命名较好的文件：\n" + "\n".join(good_examples[:3])
    if bad_examples:
        examples_text += f"\n❌ 需要改进的文件：\n" + "\n".join(bad_examples[:3])
    
    return f"""
我有 {len(txt_files)} 个txt文件，想要规范化命名：
{examples_text}

🎯 我的命名规范需求：
1. 为不同类型的txt文件建立命名标准（工作文档、学习笔记、个人记录）
2. 设计包含时间信息的命名格式
3. 确保文件名具有良好的可读性和搜索性
4. 支持版本控制和更新迭代
5. 考虑文件的优先级和重要性标识

请为我设计一套完整的txt文件命名规范体系，包括：
- 具体的命名模板和示例
- 各种使用场景的应用方法
- 迁移现有文件的重命名建议
- 长期维护的注意事项

让我的文件命名既专业又实用！
"""

@mcp.prompt()
async def file_cleanup_assistant() -> str:
    """
    文件清理助手 - 识别和清理不需要的文件
    """
    desktop_path = get_desktop_path()
    txt_files = await scan_txt_files(desktop_path)
    
    if not txt_files:
        return """
我的桌面很干净，没有txt文件。

请教我建立文件清理的良好习惯：
1. 如何定期检查和清理桌面文件
2. 识别不再需要的文件的方法
3. 安全删除文件的最佳实践
4. 建立自动化清理流程
5. 文件备份和归档策略

我想要保持桌面的整洁和高效。
"""
    
    # 分析可能需要清理的文件
    cleanup_candidates = []
    small_files = []
    old_files = []
    duplicate_names = []
    
    now = datetime.now()
    name_counts = {}
    
    for file in txt_files:
        # 统计文件名（不含扩展名）
        stem = file['stem'].lower()
        name_counts[stem] = name_counts.get(stem, 0) + 1
        
        # 检查小文件
        if file['size_kb'] < 0.5:
            small_files.append(file['name'])
        
        # 检查修改时间（超过30天）
        modified = datetime.fromisoformat(file['modified_time'])
        days_old = (now - modified).days
        if days_old > 30:
            old_files.append(f"{file['name']} (修改于 {days_old} 天前)")
        
        # 检查可能的临时文件
        if any(word in file['name'].lower() for word in ['untitled', 'temp', '临时', 'test', '测试']):
            cleanup_candidates.append(file['name'])
    
    # 查找可能的重复文件
    for name, count in name_counts.items():
        if count > 1:
            duplicate_names.extend([f['name'] for f in txt_files if f['stem'].lower() == name])
    
    analysis_text = f"""
📊 清理分析报告：
• 总文件数：{len(txt_files)}
• 小文件（<0.5KB）：{len(small_files)} 个
• 老文件（>30天未修改）：{len(old_files)} 个  
• 可能的临时文件：{len(cleanup_candidates)} 个
• 可能的重复命名：{len(set(duplicate_names))} 个
"""
    
    if small_files:
        analysis_text += f"\n🔍 小文件清单：\n" + "\n".join([f"  • {name}" for name in small_files[:5]])
    
    if cleanup_candidates:
        analysis_text += f"\n🗑️ 可能的临时文件：\n" + "\n".join([f"  • {name}" for name in cleanup_candidates[:5]])
    
    return f"""
我需要清理桌面上的txt文件：
{analysis_text}

请帮我制定清理策略：
1. 分析哪些文件可能不再需要
2. 如何安全地识别重复或过时的文件
3. 清理前的备份建议
4. step-by-step的清理流程
5. 建立定期清理的自动化方案

我希望在保证重要文件安全的前提下，让桌面更加整洁高效。
"""

@mcp.prompt()
async def productivity_file_organizer() -> str:
    """
    效率文件管理器 - 提升工作效率的文件整理方案
    """
    desktop_path = get_desktop_path()
    txt_files = await scan_txt_files(desktop_path)
    
    base_prompt = """
我想要建立一个高效的txt文件管理系统来提升工作效率。

请为我设计：
1. 基于工作流程的文件分类体系
2. 快速查找和访问文件的方法
3. 文件优先级和状态管理系统
4. 与其他工具（如日历、任务管理）的集成方案
5. 移动端和多设备同步的最佳实践

我的目标是建立一个既专业又高效的文件管理工作流。
"""
    
    if not txt_files:
        return base_prompt + "\n\n目前我的桌面没有txt文件，可以从零开始设计最佳方案。"
    
    # 分析工作模式
    work_indicators = {
        "has_meeting_files": any(word in f['name'].lower() for f in txt_files 
                               for word in ['会议', 'meeting', '讨论']),
        "has_project_files": any(word in f['name'].lower() for f in txt_files 
                               for word in ['项目', 'project', '计划']),
        "has_notes": any(word in f['name'].lower() for f in txt_files 
                        for word in ['笔记', 'note', '记录']),
        "has_todos": any(word in f['name'].lower() for f in txt_files 
                        for word in ['todo', '待办', '任务']),
    }
    
    work_analysis = "🔍 当前工作模式分析：\n"
    if work_indicators["has_meeting_files"]:
        work_analysis += "• 包含会议相关文件，建议建立会议文档管理体系\n"
    if work_indicators["has_project_files"]:
        work_analysis += "• 包含项目文件，建议按项目分类管理\n"
    if work_indicators["has_notes"]:
        work_analysis += "• 包含笔记文件，建议建立知识管理系统\n"
    if work_indicators["has_todos"]:
        work_analysis += "• 包含待办文件，建议与任务管理工具集成\n"
    
    recent_files = [f for f in txt_files 
                   if (datetime.now() - datetime.fromisoformat(f['modified_time'])).days <= 7]
    
    return f"""
我有 {len(txt_files)} 个txt文件，想要优化工作效率：

{work_analysis}

📈 活跃度分析：
• 最近7天内修改的文件：{len(recent_files)} 个
• 文件平均大小：{sum(f['size_kb'] for f in txt_files)/len(txt_files):.1f} KB

{base_prompt}

请特别针对我当前的文件使用模式，提供个性化的效率提升方案。
"""

# =============================================================================
# TOOLS - 原有的工具函数（保持不变）
# =============================================================================

@mcp.tool()
async def count_desktop_txt_files() -> str:
    """统计当前用户桌面上的txt文件数量"""
    desktop_path = get_desktop_path()
    txt_files = await scan_txt_files(desktop_path)
    
    count = len(txt_files)
    
    if count == 0:
        return f"桌面路径: {desktop_path}\n📁 未找到任何txt文件"
    
    total_size_kb = sum(file_info['size_kb'] for file_info in txt_files)
    
    result = f"""
📁 桌面路径: {desktop_path}
📊 txt文件统计结果:
   • 文件数量: {count} 个
   • 总大小: {total_size_kb:.2f} KB
   • 平均大小: {total_size_kb/count:.2f} KB
"""
    return result.strip()

@mcp.tool()
async def list_desktop_txt_files(include_details: bool = False) -> str:
    """获取桌面上所有txt文件的名称列表"""
    desktop_path = get_desktop_path()
    txt_files = await scan_txt_files(desktop_path)
    
    if not txt_files:
        return f"📁 桌面路径: {desktop_path}\n❌ 未找到任何txt文件"
    
    result = [f"📁 桌面路径: {desktop_path}"]
    result.append(f"📋 找到 {len(txt_files)} 个txt文件:\n")
    
    if include_details:
        result.append("📄 详细信息:")
        for i, file_info in enumerate(txt_files, 1):
            file_line = f"   {i:2d}. {file_info['name']}"
            file_line += f" ({file_info['size_kb']} KB)"
            result.append(file_line)
    else:
        result.append("📝 文件列表:")
        for i, file_info in enumerate(txt_files, 1):
            result.append(f"   {i:2d}. {file_info['name']}")
    
    return "\n".join(result)

@mcp.tool()
async def find_txt_file(filename_pattern: str) -> str:
    """在桌面上查找匹配指定模式的txt文件"""
    desktop_path = get_desktop_path()
    txt_files = await scan_txt_files(desktop_path)
    
    if not txt_files:
        return f"📁 桌面路径: {desktop_path}\n❌ 桌面上没有txt文件"
    
    pattern_lower = filename_pattern.lower()
    matched_files = [
        file_info for file_info in txt_files 
        if pattern_lower in file_info['name'].lower()
    ]
    
    if not matched_files:
        return f"📁 桌面路径: {desktop_path}\n🔍 未找到包含 '{filename_pattern}' 的txt文件"
    
    result = [f"📁 桌面路径: {desktop_path}"]
    result.append(f"🔍 搜索模式: '{filename_pattern}'")
    result.append(f"✅ 找到 {len(matched_files)} 个匹配的文件:\n")
    
    for i, file_info in enumerate(matched_files, 1):
        file_line = f"   {i}. {file_info['name']}"
        file_line += f" ({file_info['size_kb']} KB)"
        file_line += f"\n      路径: {file_info['full_path']}"
        result.append(file_line)
    
    return "\n".join(result)

@mcp.tool()
async def get_system_info() -> str:
    """获取当前系统的基本信息"""
    desktop_path = get_desktop_path()
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
    启动完整版MCP服务器
    
    本服务器提供：
    1. Tools（4个）：执行具体操作
    2. Resources（3个）：提供可读取的数据源
    3. Prompts（4个）：预定义的专业提示模板
    """
    print("🚀 完整版桌面txt文件管理MCP服务器启动中...", file=__import__('sys').stderr)
    print(f"📁 检测到的桌面路径: {get_desktop_path()}", file=__import__('sys').stderr)
    print("🔧 提供功能：", file=__import__('sys').stderr)
    print("   • 4个Tools：文件统计、列表、搜索、系统信息", file=__import__('sys').stderr)
    print("   • 3个Resources：文件数据、系统信息、统计分析", file=__import__('sys').stderr)
    print("   • 4个Prompts：整理向导、命名顾问、清理助手、效率管理", file=__import__('sys').stderr)
    
    # 启动MCP服务器
    mcp.run(transport='stdio')