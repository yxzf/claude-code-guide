#!/usr/bin/env python3
"""
简化的MCP服务器启动脚本
直接运行服务器，避免uv的复杂性
"""

import sys
import subprocess
import os
from pathlib import Path

def main():
    # 获取脚本所在目录
    script_dir = Path(__file__).parent
    server_script = script_dir / "desktop_txt_server.py"
    venv_python = script_dir / ".venv" / "bin" / "python"
    
    # 检查虚拟环境是否存在
    if venv_python.exists():
        # 使用虚拟环境中的Python
        cmd = [str(venv_python), str(server_script)]
    else:
        # 使用系统Python
        cmd = [sys.executable, str(server_script)]
    
    try:
        # 运行服务器
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"服务器启动失败: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("服务器已停止", file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    main()