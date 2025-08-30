# Claude Hook 完整讲解

## 📖 目录
1. [什么是Claude Hook](#什么是claude-hook)
2. [核心概念与原理](#核心概念与原理)
3. [Hook事件系统](#hook事件系统)
4. [配置与管理](#配置与管理)
5. [Hook输入输出机制](#hook输入输出机制)
6. [实际应用场景](#实际应用场景)
7. [安全机制与最佳实践](#安全机制与最佳实践)
8. [高级功能与技巧](#高级功能与技巧)
9. [故障排查与调试](#故障排查与调试)
10. [未来发展与扩展](#未来发展与扩展)

---

## 什么是Claude Hook

### 基本定义
Claude Hook是Claude Code中的事件驱动机制，允许用户在特定事件发生时自动执行shell命令。它为开发者提供了强大的自动化能力，可以在Claude Code的各种操作节点插入自定义逻辑。

### 核心特性
- **事件驱动**：基于Claude Code的各种操作事件触发
- **自动化执行**：无需手动干预的命令执行
- **灵活配置**：支持用户级和项目级配置
- **丰富的事件类型**：覆盖工具调用、会话管理、通知等多种场景
- **强大的控制能力**：可以阻止操作、提供反馈、添加上下文

### 设计理念
Hook系统的设计遵循了以下原则：
- **非侵入性**：不影响Claude Code的核心功能
- **可扩展性**：支持用户自定义的各种自动化需求
- **安全性**：提供必要的安全控制和隔离机制
- **易用性**：简单的配置和使用方式

---

## 核心概念与原理

### Hook工作原理

```
用户操作 → Claude Code处理 → Hook事件触发 → Shell命令执行 → 结果反馈
     ↑                                    ↓
     └─────────── 可能的操作阻止或修改 ←─────────┘
```

#### 执行流程
1. **事件检测**：Claude Code在特定操作点检测Hook配置
2. **匹配器检查**：根据工具名称或事件类型匹配相应的Hook
3. **并行执行**：所有匹配的Hook命令并行执行
4. **结果处理**：根据Hook输出决定后续操作
5. **反馈集成**：将Hook结果集成到Claude Code的工作流中

#### 关键组件

##### 1. 匹配器（Matcher）
- **作用**：确定哪些Hook应该在特定事件时执行
- **类型**：
  - 精确匹配：`"Write"` 只匹配Write工具
  - 正则表达式：`"Edit|Write"` 匹配Edit或Write工具
  - 通配符：`"*"` 匹配所有工具
  - 空匹配：`""` 或省略，匹配所有

##### 2. Hook命令
- **格式**：标准的bash命令
- **环境变量**：可以使用`$CLAUDE_PROJECT_DIR`等环境变量
- **超时控制**：支持单个命令的超时设置

##### 3. 事件上下文
- **输入数据**：通过stdin接收JSON格式的事件信息
- **输出处理**：通过stdout/stderr和退出码提供反馈

### Hook类型分类

#### 1. 工具生命周期Hook
- **PreToolUse**：工具调用前执行
- **PostToolUse**：工具调用后执行

#### 2. 会话管理Hook
- **SessionStart**：会话开始时执行
- **SessionEnd**：会话结束时执行

#### 3. 交互控制Hook
- **UserPromptSubmit**：用户提交prompt前执行
- **Notification**：发送通知时执行

#### 4. 系统操作Hook
- **Stop**：主agent停止时执行
- **SubagentStop**：子agent停止时执行
- **PreCompact**：压缩操作前执行

---

## Hook事件系统

### PreToolUse Hook

#### 功能特点
- **执行时机**：Claude创建工具参数后，但在处理工具调用之前
- **控制能力**：可以阻止工具调用、修改参数、请求用户确认
- **适用场景**：权限检查、参数验证、安全审核

#### 常用匹配器
```json
{
  "matcher": "Task",
  "hooks": [{
    "type": "command",
    "command": "echo 'Subagent task starting'",
    "timeout": 10
  }]
}
```

##### 主要工具类型
- **Task**：Subagent任务
- **Bash**：Shell命令
- **Read/Write/Edit**：文件操作
- **Glob/Grep**：搜索操作
- **WebFetch/WebSearch**：网络操作

#### 输入数据格式
```json
{
  "tool": "Write",
  "tool_input": {
    "file_path": "/path/to/file.txt",
    "content": "File content here"
  },
  "session_id": "session_123",
  "request_id": "req_456"
}
```

#### 控制选项
```json
{
  "permissionDecision": "allow" | "deny" | "ask",
  "permissionDecisionReason": "Reason for the decision",
  "continue": true | false,
  "stopReason": "Reason for stopping"
}
```

### PostToolUse Hook

#### 功能特点
- **执行时机**：工具成功完成后立即执行
- **信息获取**：可以访问工具的输入参数和输出结果
- **反馈能力**：可以向Claude提供额外的上下文或错误信息

#### 应用场景
```bash
# 文件写入后的自动格式化
{
  "matcher": "Write",
  "hooks": [{
    "type": "command", 
    "command": "prettier --write \"$CLAUDE_PROJECT_DIR/**/*.{js,ts,json}\""
  }]
}

# 代码提交后的自动测试
{
  "matcher": "Edit",
  "hooks": [{
    "type": "command",
    "command": "cd $CLAUDE_PROJECT_DIR && npm test"
  }]
}
```

#### 输入数据格式
```json
{
  "tool": "Write",
  "tool_input": {
    "file_path": "/path/to/file.txt", 
    "content": "File content"
  },
  "tool_response": {
    "success": true,
    "message": "File written successfully"
  },
  "session_id": "session_123",
  "request_id": "req_456"
}
```

### UserPromptSubmit Hook

#### 功能特点
- **执行时机**：用户提交prompt之前
- **控制能力**：可以阻止prompt处理、添加上下文、验证输入
- **适用场景**：内容过滤、上下文增强、工作流控制

#### 典型应用
```bash
# 添加项目上下文
{
  "hooks": [{
    "type": "command",
    "command": "$CLAUDE_PROJECT_DIR/scripts/add-context.sh"
  }]
}

# 敏感词检查
{
  "hooks": [{
    "type": "command", 
    "command": "python $CLAUDE_PROJECT_DIR/scripts/content-filter.py"
  }]
}
```

#### 输入数据格式
```json
{
  "prompt": "User's input prompt text",
  "session_id": "session_123",
  "conversation_history": [
    {
      "role": "user",
      "content": "Previous user message"
    },
    {
      "role": "assistant", 
      "content": "Previous assistant response"
    }
  ]
}
```

### Notification Hook

#### 功能特点
- **执行时机**：Claude Code发送通知时
- **通知类型**：
  - 权限请求：`"Claude需要使用Bash权限"`
  - 等待输入：`"Claude正在等待您的输入"`
  - 空闲超时：60秒无操作后触发

#### 应用场景
```bash
# 发送桌面通知
{
  "hooks": [{
    "type": "command",
    "command": "osascript -e 'display notification \"Claude需要注意\" with title \"Claude Code\"'"
  }]
}

# 记录通知日志
{
  "hooks": [{
    "type": "command",
    "command": "echo \"$(date): $notification\" >> $CLAUDE_PROJECT_DIR/notifications.log"
  }]
}
```

### SessionStart Hook

#### 功能特点
- **执行时机**：Claude Code启动新会话或恢复会话时
- **上下文加载**：可以为会话添加初始上下文信息
- **环境准备**：执行会话初始化相关的设置

#### 匹配器类型
- **startup**：从启动调用
- **resume**：从--resume、--continue或/resume调用
- **clear**：从/clear调用  
- **compact**：从自动或手动compact调用

#### 应用示例
```bash
# 加载项目状态
{
  "matcher": "startup",
  "hooks": [{
    "type": "command",
    "command": "$CLAUDE_PROJECT_DIR/scripts/load-project-context.sh"
  }]
}

# 恢复会话状态
{
  "matcher": "resume", 
  "hooks": [{
    "type": "command",
    "command": "cat $CLAUDE_PROJECT_DIR/.claude/last-session.md"
  }]
}
```

### SessionEnd Hook

#### 功能特点
- **执行时机**：Claude Code会话结束时
- **清理任务**：执行清理、保存状态、统计记录等操作
- **无阻止能力**：不能阻止会话终止

#### 结束原因
- **clear**：通过/clear命令清除会话
- **logout**：用户登出
- **prompt_input_exit**：用户在prompt输入时退出
- **other**：其他退出原因

#### 应用示例
```bash
# 保存会话统计
{
  "hooks": [{
    "type": "command",
    "command": "$CLAUDE_PROJECT_DIR/scripts/save-session-stats.sh"
  }]
}

# 清理临时文件
{
  "hooks": [{
    "type": "command",
    "command": "rm -rf $CLAUDE_PROJECT_DIR/tmp/*"
  }]
}
```

---

## 配置与管理

### 配置文件层次

Claude Code Hook采用分层配置系统：

```
~/.claude/settings.json          ← 用户全局设置
.claude/settings.json            ← 项目设置
.claude/settings.local.json      ← 本地项目设置（不提交）
Enterprise Policy Settings       ← 企业管理策略设置
```

#### 优先级顺序
1. Enterprise Policy Settings（最高优先级）
2. .claude/settings.local.json
3. .claude/settings.json
4. ~/.claude/settings.json（最低优先级）

### 基本配置结构

```json
{
  "hooks": [
    {
      "matcher": "工具名称或正则表达式",
      "hooks": [
        {
          "type": "command",
          "command": "要执行的bash命令",
          "timeout": 30
        }
      ]
    }
  ]
}
```

### 配置示例

#### 1. 文件操作监控
```json
{
  "hooks": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "command",
          "command": "echo \"File modified: $(date)\" >> $CLAUDE_PROJECT_DIR/file-changes.log"
        }
      ]
    }
  ]
}
```

#### 2. 代码质量检查
```json
{
  "hooks": [
    {
      "matcher": "Write",
      "hooks": [
        {
          "type": "command",
          "command": "if [[ \"$1\" == *.py ]]; then python -m flake8 \"$1\"; fi",
          "timeout": 60
        }
      ]
    }
  ]
}
```

#### 3. Git自动操作
```json
{
  "hooks": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "cd $CLAUDE_PROJECT_DIR && git add -A && git commit -m \"Auto-commit via Claude Hook: $(date)\""
        }
      ]
    }
  ]
}
```

#### 4. MCP工具集成
```json
{
  "hooks": [
    {
      "matcher": "mcp__filesystem__*",
      "hooks": [
        {
          "type": "command",
          "command": "echo \"MCP filesystem operation detected\" | logger"
        }
      ]
    },
    {
      "matcher": "mcp__github__*", 
      "hooks": [
        {
          "type": "command",
          "command": "$CLAUDE_PROJECT_DIR/scripts/github-webhook.sh"
        }
      ]
    }
  ]
}
```

### 环境变量

Claude Code为Hook执行提供了特殊的环境变量：

#### 核心环境变量
- **CLAUDE_PROJECT_DIR**：项目根目录的绝对路径
- **PATH**：继承Claude Code的环境PATH
- **其他系统环境变量**：完整的系统环境

#### 使用示例
```bash
# 使用项目相对路径
"$CLAUDE_PROJECT_DIR/scripts/my-script.sh"

# 访问项目配置
cat "$CLAUDE_PROJECT_DIR/.claude/config.json"

# 创建项目相关文件
echo "Log entry" >> "$CLAUDE_PROJECT_DIR/hook.log"
```

### 配置管理最佳实践

#### 1. 配置文件组织
```
.claude/
├── settings.json           # 团队共享配置
├── settings.local.json     # 个人本地配置
├── hooks/                  # Hook脚本目录
│   ├── pre-tool.sh
│   ├── post-tool.sh
│   └── validation.py
└── templates/              # 配置模板
    └── common-hooks.json
```

#### 2. 脚本路径管理
```json
{
  "hooks": [
    {
      "matcher": "Write",
      "hooks": [
        {
          "type": "command",
          "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/file-validator.sh"
        }
      ]
    }
  ]
}
```

#### 3. 条件执行
```bash
#!/bin/bash
# .claude/hooks/conditional-hook.sh

# 只在特定分支执行
current_branch=$(git branch --show-current)
if [[ "$current_branch" == "main" ]]; then
  echo "Running on main branch"
  # 执行主分支特定逻辑
fi

# 只在工作时间执行
hour=$(date +%H)
if (( hour >= 9 && hour <= 17 )); then
  echo "Working hours - running full validation"
else
  echo "Off hours - running quick validation"
fi
```

---

## Hook输入输出机制

### 输入机制

Hook通过stdin接收JSON格式的事件数据，包含以下信息：

#### 通用字段
```json
{
  "session_id": "唯一会话标识符",
  "request_id": "请求标识符", 
  "timestamp": "事件时间戳",
  "event_type": "事件类型"
}
```

#### 工具相关字段
```json
{
  "tool": "工具名称",
  "tool_input": "工具输入参数",
  "tool_response": "工具响应结果（仅PostToolUse）"
}
```

### 输出机制

Hook可以通过两种方式返回输出：

#### 1. 简单输出（退出码方式）
```bash
#!/bin/bash
# 简单的验证脚本

if [[ -f "$1" ]]; then
  echo "File exists and is valid"
  exit 0  # 成功
else
  echo "File not found" >&2
  exit 2  # 阻止操作
fi
```

##### 退出码含义
- **0**：成功，stdout在transcript模式下显示给用户
- **2**：阻止错误，stderr反馈给Claude处理
- **其他**：非阻止错误，stderr显示给用户，继续执行

#### 2. 高级输出（JSON方式）
```bash
#!/bin/bash
# 高级控制脚本

read -d '' input
tool_name=$(echo "$input" | jq -r '.tool')

if [[ "$tool_name" == "Bash" ]]; then
  # 返回JSON控制指令
  cat << EOF
{
  "permissionDecision": "ask",
  "permissionDecisionReason": "Bash command requires user confirmation",
  "hookSpecificOutput": {
    "additionalContext": "Security check: This command will execute shell operations"
  }
}
EOF
else
  # 允许执行
  cat << EOF
{
  "permissionDecision": "allow",
  "continue": true
}
EOF
fi
```

### 不同Hook类型的输出控制

#### PreToolUse输出控制
```json
{
  "permissionDecision": "allow|deny|ask",
  "permissionDecisionReason": "决策原因",
  "continue": true/false,
  "stopReason": "停止原因"
}
```

##### 权限决策
- **allow**：绕过权限系统，直接允许
- **deny**：阻止工具调用，原因显示给Claude
- **ask**：要求用户在UI中确认

#### PostToolUse输出控制
```json
{
  "decision": "block",
  "reason": "阻止原因",
  "hookSpecificOutput": {
    "additionalContext": "额外上下文信息"
  }
}
```

#### UserPromptSubmit输出控制
```json
{
  "decision": "block",
  "reason": "阻止原因（显示给用户）",
  "hookSpecificOutput": {
    "additionalContext": "添加到上下文的内容"
  }
}
```

#### Stop/SubagentStop输出控制
```json
{
  "decision": "block",
  "reason": "必须提供原因让Claude知道如何继续"
}
```

### 实际输出示例

#### 文件验证Hook
```bash
#!/bin/bash
# file-validator.sh

read -d '' input
file_path=$(echo "$input" | jq -r '.tool_input.file_path')

# 检查文件扩展名
if [[ "$file_path" == *.exe ]]; then
  cat << EOF
{
  "permissionDecision": "deny",
  "permissionDecisionReason": "Executable files are not allowed for security reasons"
}
EOF
  exit 0
fi

# 检查文件大小
if [[ -f "$file_path" ]] && [[ $(stat -f%z "$file_path" 2>/dev/null || stat -c%s "$file_path" 2>/dev/null) -gt 10485760 ]]; then
  cat << EOF
{
  "permissionDecision": "ask", 
  "permissionDecisionReason": "File is larger than 10MB, please confirm"
}
EOF
  exit 0
fi

# 允许操作
echo '{"permissionDecision": "allow"}'
```

#### 代码质量检查Hook
```bash
#!/bin/bash
# code-quality-check.sh

read -d '' input
file_content=$(echo "$input" | jq -r '.tool_input.content')
file_path=$(echo "$input" | jq -r '.tool_input.file_path')

# 对Python文件进行语法检查
if [[ "$file_path" == *.py ]]; then
  echo "$file_content" | python -m py_compile -
  if [[ $? -ne 0 ]]; then
    cat << EOF
{
  "decision": "block",
  "reason": "Python syntax error detected. Please fix the syntax before proceeding.",
  "hookSpecificOutput": {
    "additionalContext": "Automatic syntax validation failed for Python file: $file_path"
  }
}
EOF
    exit 0
  fi
fi

# 通过检查
echo '{"continue": true}'
```

---

## 实际应用场景

### 开发工作流自动化

#### 1. 代码质量保证
```json
{
  "hooks": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "command",
          "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/quality-check.sh",
          "timeout": 60
        }
      ]
    }
  ]
}
```

```bash
#!/bin/bash
# quality-check.sh
read -d '' input
file_path=$(echo "$input" | jq -r '.tool_input.file_path')

case "$file_path" in
  *.js|*.ts)
    # JavaScript/TypeScript检查
    npx eslint "$file_path"
    npx prettier --check "$file_path"
    ;;
  *.py)
    # Python检查
    python -m flake8 "$file_path"
    python -m black --check "$file_path"
    ;;
  *.go)
    # Go检查
    go fmt "$file_path"
    go vet "$file_path"
    ;;
esac
```

#### 2. 自动化测试触发
```json
{
  "hooks": [
    {
      "matcher": "Write",
      "hooks": [
        {
          "type": "command", 
          "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/auto-test.sh"
        }
      ]
    }
  ]
}
```

```bash
#!/bin/bash
# auto-test.sh
read -d '' input
file_path=$(echo "$input" | jq -r '.tool_input.file_path')

# 检查是否是测试相关文件
if [[ "$file_path" == *test* ]] || [[ "$file_path" == *spec* ]]; then
  echo "Test file modified, running tests..."
  cd "$CLAUDE_PROJECT_DIR"
  
  case "$file_path" in
    *.js|*.ts)
      npm test
      ;;
    *.py)
      python -m pytest "$file_path"
      ;;
    *.go)
      go test "./$(dirname "$file_path")"
      ;;
  esac
fi
```

#### 3. Git工作流集成
```json
{
  "hooks": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/git-workflow.sh"
        }
      ]
    }
  ]
}
```

```bash
#!/bin/bash
# git-workflow.sh
read -d '' input
tool=$(echo "$input" | jq -r '.tool')

if [[ "$tool" == "Write" || "$tool" == "Edit" ]]; then
  file_path=$(echo "$input" | jq -r '.tool_input.file_path')
  
  cd "$CLAUDE_PROJECT_DIR"
  
  # 自动添加到Git
  git add "$file_path"
  
  # 创建描述性提交信息
  commit_msg="Claude Code: Modified $(basename "$file_path")"
  git commit -m "$commit_msg" --quiet
  
  echo "File committed to Git: $(basename "$file_path")"
fi
```

### 安全与合规

#### 1. 敏感信息检测
```bash
#!/bin/bash
# sensitive-data-check.sh
read -d '' input
content=$(echo "$input" | jq -r '.tool_input.content')

# 检查敏感信息模式
sensitive_patterns=(
  "password\s*=\s*['\"].*['\"]"
  "api[_-]?key\s*=\s*['\"].*['\"]"
  "secret\s*=\s*['\"].*['\"]"
  "\b[A-Za-z0-9]{20,}\b"  # 可能的token
)

for pattern in "${sensitive_patterns[@]}"; do
  if echo "$content" | grep -iE "$pattern" > /dev/null; then
    cat << EOF
{
  "permissionDecision": "deny",
  "permissionDecisionReason": "Potential sensitive information detected. Please review and remove before proceeding."
}
EOF
    exit 0
  fi
done

echo '{"permissionDecision": "allow"}'
```

#### 2. 文件权限控制
```bash
#!/bin/bash
# file-permission-check.sh
read -d '' input
file_path=$(echo "$input" | jq -r '.tool_input.file_path')

# 限制只能修改项目目录下的文件
if [[ ! "$file_path" == "$CLAUDE_PROJECT_DIR"* ]]; then
  cat << EOF
{
  "permissionDecision": "deny", 
  "permissionDecisionReason": "File access restricted to project directory only"
}
EOF
  exit 0
fi

# 禁止修改关键系统文件
restricted_files=(
  ".env"
  ".env.local"
  "id_rsa"
  "id_dsa"
  "*.key"
  "*.pem"
)

for pattern in "${restricted_files[@]}"; do
  if [[ "$(basename "$file_path")" == $pattern ]]; then
    cat << EOF
{
  "permissionDecision": "ask",
  "permissionDecisionReason": "Attempting to modify sensitive file: $(basename "$file_path")"
}
EOF
    exit 0
  fi
done

echo '{"permissionDecision": "allow"}'
```

### 项目管理与监控

#### 1. 活动日志记录
```bash
#!/bin/bash
# activity-logger.sh
read -d '' input

session_id=$(echo "$input" | jq -r '.session_id')
tool=$(echo "$input" | jq -r '.tool')
timestamp=$(date '+%Y-%m-%d %H:%M:%S')

# 记录到活动日志
echo "[$timestamp] Session: $session_id, Tool: $tool" >> "$CLAUDE_PROJECT_DIR/.claude/activity.log"

# 如果是文件操作，记录更详细信息
if [[ "$tool" == "Write" || "$tool" == "Edit" ]]; then
  file_path=$(echo "$input" | jq -r '.tool_input.file_path')
  echo "  → File: $(basename "$file_path")" >> "$CLAUDE_PROJECT_DIR/.claude/activity.log"
fi
```

#### 2. 性能监控
```bash
#!/bin/bash
# performance-monitor.sh
read -d '' input

tool=$(echo "$input" | jq -r '.tool')
start_time=$(date +%s%N)

# 工具执行完成后记录耗时
echo "$input" | jq --arg start_time "$start_time" \
  '.performance = {start_time: $start_time}' \
  > /tmp/claude-perf-$$.json

# 在PostToolUse中计算实际耗时
if [[ -f "/tmp/claude-perf-$$.json" ]]; then
  end_time=$(date +%s%N)
  duration=$(( (end_time - start_time) / 1000000 )) # 转换为毫秒
  
  echo "Tool $tool executed in ${duration}ms" >> "$CLAUDE_PROJECT_DIR/.claude/performance.log"
  rm "/tmp/claude-perf-$$.json"
fi
```

### 团队协作增强

#### 1. 通知集成
```bash
#!/bin/bash
# team-notification.sh
read -d '' input

tool=$(echo "$input" | jq -r '.tool')
session_id=$(echo "$input" | jq -r '.session_id')

# 重要操作通知团队
if [[ "$tool" == "Write" ]]; then
  file_path=$(echo "$input" | jq -r '.tool_input.file_path')
  
  # 发送Slack通知
  curl -X POST -H 'Content-type: application/json' \
    --data "{\"text\":\"Claude Code modified: $(basename "$file_path")\"}" \
    "$SLACK_WEBHOOK_URL"
  
  # 发送邮件通知
  echo "Claude Code session $session_id modified $(basename "$file_path")" | \
    mail -s "Code Update Notification" team@company.com
fi
```

#### 2. 代码审查触发
```bash
#!/bin/bash
# code-review-trigger.sh
read -d '' input

tool=$(echo "$input" | jq -r '.tool')

if [[ "$tool" == "Write" || "$tool" == "Edit" ]]; then
  file_path=$(echo "$input" | jq -r '.tool_input.file_path')
  
  # 对关键文件触发代码审查
  critical_patterns=(
    "*/api/*"
    "*/security/*"
    "*/auth/*"
    "*database*"
  )
  
  for pattern in "${critical_patterns[@]}"; do
    if [[ "$file_path" == $pattern ]]; then
      # 创建审查请求
      echo "Critical file modified: $file_path" | \
        mail -s "Code Review Required" code-review@company.com
      
      # 标记文件需要审查
      echo "$(date): $file_path" >> "$CLAUDE_PROJECT_DIR/.claude/review-queue.txt"
      break
    fi
  done
fi
```

---

## 安全机制与最佳实践

### 安全风险与防护

#### ⚠️ 重要安全警告
**USE AT YOUR OWN RISK**：Claude Code Hook会在您的系统上自动执行任意shell命令。使用Hook时需要承担以下风险：
- Hook可以修改、删除或访问用户账户权限范围内的任何文件
- 恶意或错误的Hook可能导致数据丢失或系统损坏
- Anthropic不提供任何保证，不承担Hook使用造成的损失责任

#### 安全最佳实践

##### 1. 输入验证和清理
```bash
#!/bin/bash
# secure-hook-template.sh

# 设置严格模式
set -euo pipefail

# 验证输入
validate_input() {
  local input="$1"
  
  # 检查JSON格式
  if ! echo "$input" | jq . > /dev/null 2>&1; then
    echo "Invalid JSON input" >&2
    exit 1
  fi
  
  # 验证必需字段
  if ! echo "$input" | jq -e '.tool' > /dev/null; then
    echo "Missing required field: tool" >&2
    exit 1
  fi
}

# 清理文件路径
sanitize_path() {
  local path="$1"
  
  # 移除危险字符
  path=$(echo "$path" | sed 's/\.\.\///g')
  
  # 确保在项目目录内
  if [[ ! "$path" == "$CLAUDE_PROJECT_DIR"* ]]; then
    echo "Path outside project directory: $path" >&2
    exit 1
  fi
  
  echo "$path"
}

# 主要逻辑
read -d '' input
validate_input "$input"

file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')
if [[ -n "$file_path" ]]; then
  file_path=$(sanitize_path "$file_path")
fi

# 继续处理...
```

##### 2. 权限最小化
```bash
#!/bin/bash
# permission-limited-hook.sh

# 检查用户权限
check_permissions() {
  local operation="$1"
  local resource="$2"
  
  case "$operation" in
    "read")
      # 检查读取权限
      if [[ ! -r "$resource" ]]; then
        echo "No read permission for: $resource" >&2
        exit 1
      fi
      ;;
    "write")
      # 检查写入权限
      if [[ ! -w "$(dirname "$resource")" ]]; then
        echo "No write permission for: $(dirname "$resource")" >&2
        exit 1
      fi
      ;;
    "execute")
      # 严格限制执行权限
      echo "Execution not allowed via Hook" >&2
      exit 1
      ;;
  esac
}

# 使用权限检查
read -d '' input
file_path=$(echo "$input" | jq -r '.tool_input.file_path')
check_permissions "write" "$file_path"
```

##### 3. 敏感文件保护
```bash
#!/bin/bash
# sensitive-file-protection.sh

# 定义敏感文件模式
SENSITIVE_PATTERNS=(
  ".env*"
  "*.key"
  "*.pem"
  "id_rsa*"
  "*.p12"
  "*.pfx"
  "password*"
  "secret*"
  ".ssh/*"
  ".aws/*"
  ".docker/config.json"
)

# 检查是否为敏感文件
is_sensitive_file() {
  local file="$1"
  local basename_file="$(basename "$file")"
  
  for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    if [[ "$basename_file" == $pattern ]] || [[ "$file" == *$pattern ]]; then
      return 0
    fi
  done
  return 1
}

# 保护敏感文件
read -d '' input
file_path=$(echo "$input" | jq -r '.tool_input.file_path')

if is_sensitive_file "$file_path"; then
  cat << EOF
{
  "permissionDecision": "deny",
  "permissionDecisionReason": "Access to sensitive file '$(basename "$file_path")' is not allowed"
}
EOF
  exit 0
fi
```

### 配置安全

#### 1. 配置文件权限
```bash
# 设置正确的配置文件权限
chmod 600 ~/.claude/settings.json
chmod 600 .claude/settings.json
chmod 700 .claude/hooks/

# 防止意外提交敏感配置
echo ".claude/settings.local.json" >> .gitignore
echo ".claude/hooks/*.local.*" >> .gitignore
```

#### 2. Hook脚本安全
```bash
#!/bin/bash
# 安全的Hook脚本模板

# 设置安全环境
export PATH="/usr/local/bin:/usr/bin:/bin"
unset IFS
umask 077

# 验证环境变量
if [[ -z "$CLAUDE_PROJECT_DIR" ]]; then
  echo "CLAUDE_PROJECT_DIR not set" >&2
  exit 1
fi

# 验证项目目录存在且安全
if [[ ! -d "$CLAUDE_PROJECT_DIR" ]]; then
  echo "Project directory does not exist: $CLAUDE_PROJECT_DIR" >&2
  exit 1
fi

# 确保在正确的目录下工作
cd "$CLAUDE_PROJECT_DIR" || exit 1

# 日志记录
log_action() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') [$$] $*" >> .claude/hook.log
}

# 错误处理
error_exit() {
  log_action "ERROR: $*"
  echo "$*" >&2
  exit 1
}

# 主要逻辑开始
log_action "Hook started: $(basename "$0")"
```

#### 3. 审计和监控
```bash
#!/bin/bash
# hook-audit.sh - Hook执行审计

AUDIT_LOG="$CLAUDE_PROJECT_DIR/.claude/audit.log"

# 审计日志函数
audit_log() {
  local level="$1"
  local message="$2"
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  
  echo "[$timestamp] [$level] [$$] $message" >> "$AUDIT_LOG"
}

# Hook执行监控
monitor_hook_execution() {
  local hook_name="$1"
  local start_time=$(date +%s)
  
  audit_log "INFO" "Hook started: $hook_name"
  
  # 执行Hook逻辑
  execute_hook_logic "$@"
  local result=$?
  
  local end_time=$(date +%s)
  local duration=$((end_time - start_time))
  
  if [[ $result -eq 0 ]]; then
    audit_log "INFO" "Hook completed successfully: $hook_name (${duration}s)"
  else
    audit_log "ERROR" "Hook failed: $hook_name (${duration}s, exit code: $result)"
  fi
  
  return $result
}

# 使用监控
monitor_hook_execution "$(basename "$0")" "$@"
```

---

## 高级功能与技巧

### 高级JSON输出控制

#### 1. 多种决策组合
```bash
#!/bin/bash
# advanced-control.sh

read -d '' input
tool=$(echo "$input" | jq -r '.tool')
session_id=$(echo "$input" | jq -r '.session_id')

# 复杂的控制逻辑
case "$tool" in
  "Bash")
    # Bash命令需要特殊处理
    command=$(echo "$input" | jq -r '.tool_input.command')
    
    # 危险命令检查
    if echo "$command" | grep -E "(rm -rf|sudo|su -)" > /dev/null; then
      cat << EOF
{
  "permissionDecision": "deny",
  "permissionDecisionReason": "Dangerous command detected: $command",
  "continue": false,
  "stopReason": "Security policy violation"
}
EOF
      exit 0
    fi
    
    # 需要确认的命令
    if echo "$command" | grep -E "(git push|npm publish|docker run)" > /dev/null; then
      cat << EOF
{
  "permissionDecision": "ask", 
  "permissionDecisionReason": "Command requires confirmation: $command",
  "hookSpecificOutput": {
    "additionalContext": "This command may have external effects. Please review carefully."
  }
}
EOF
      exit 0
    fi
    ;;
    
  "Write")
    file_path=$(echo "$input" | jq -r '.tool_input.file_path')
    
    # 检查文件类型和大小
    if [[ "$file_path" == *.exe ]] || [[ "$file_path" == *.bin ]]; then
      cat << EOF
{
  "permissionDecision": "deny",
  "permissionDecisionReason": "Binary files are not allowed"
}
EOF
      exit 0
    fi
    ;;
esac

# 默认允许
echo '{"permissionDecision": "allow"}'
```

#### 2. 动态上下文添加
```bash
#!/bin/bash
# context-enhancer.sh

read -d '' input
prompt=$(echo "$input" | jq -r '.prompt')

# 分析prompt类型
context=""

# 如果询问项目相关问题，添加项目上下文
if echo "$prompt" | grep -iE "(project|codebase|structure)" > /dev/null; then
  context="Current project structure:\n$(tree -L 2 "$CLAUDE_PROJECT_DIR" 2>/dev/null | head -20)"
fi

# 如果询问Git相关问题，添加Git状态
if echo "$prompt" | grep -iE "(git|commit|branch)" > /dev/null; then
  cd "$CLAUDE_PROJECT_DIR"
  git_status=$(git status --porcelain 2>/dev/null | head -10)
  current_branch=$(git branch --show-current 2>/dev/null)
  context="$context\nCurrent branch: $current_branch\nGit status:\n$git_status"
fi

# 如果询问错误或调试，添加最近的日志
if echo "$prompt" | grep -iE "(error|debug|problem|issue)" > /dev/null; then
  recent_logs=$(tail -10 "$CLAUDE_PROJECT_DIR"/*.log 2>/dev/null | head -20)
  context="$context\nRecent logs:\n$recent_logs"
fi

# 返回增强的上下文
if [[ -n "$context" ]]; then
  cat << EOF
{
  "hookSpecificOutput": {
    "additionalContext": "$(echo -e "$context" | jq -R -s .)"
  }
}
EOF
else
  echo '{"continue": true}'
fi
```

### 条件执行与环境感知

#### 1. 环境条件检查
```bash
#!/bin/bash
# environment-aware-hook.sh

read -d '' input

# 检查当前环境
detect_environment() {
  if [[ -f "$CLAUDE_PROJECT_DIR/.env.production" ]] && grep -q "NODE_ENV=production" "$CLAUDE_PROJECT_DIR/.env.production"; then
    echo "production"
  elif [[ -f "$CLAUDE_PROJECT_DIR/.env.staging" ]] && grep -q "NODE_ENV=staging" "$CLAUDE_PROJECT_DIR/.env.staging"; then
    echo "staging"
  else
    echo "development"
  fi
}

# 检查Git分支
get_git_branch() {
  cd "$CLAUDE_PROJECT_DIR"
  git branch --show-current 2>/dev/null || echo "unknown"
}

# 根据环境调整行为
environment=$(detect_environment)
branch=$(get_git_branch)
tool=$(echo "$input" | jq -r '.tool')

case "$environment" in
  "production")
    # 生产环境严格控制
    if [[ "$tool" == "Write" || "$tool" == "Edit" ]]; then
      cat << EOF
{
  "permissionDecision": "ask",
  "permissionDecisionReason": "Production environment detected. Are you sure you want to modify files?"
}
EOF
      exit 0
    fi
    ;;
    
  "staging")
    # 测试环境记录操作
    echo "$(date): $tool operation in staging" >> "$CLAUDE_PROJECT_DIR/.claude/staging-operations.log"
    ;;
    
  "development")
    # 开发环境自由操作
    ;;
esac

# 分支保护
if [[ "$branch" == "main" || "$branch" == "master" ]]; then
  cat << EOF
{
  "permissionDecision": "ask",
  "permissionDecisionReason": "You are on the $branch branch. Consider creating a feature branch first."
}
EOF
  exit 0
fi

echo '{"permissionDecision": "allow"}'
```

#### 2. 时间条件控制
```bash
#!/bin/bash
# time-based-hook.sh

read -d '' input

# 获取当前时间信息
current_hour=$(date +%H)
current_day=$(date +%u)  # 1=Monday, 7=Sunday
current_date=$(date +%Y-%m-%d)

# 工作时间检查
is_working_hours() {
  # 工作日9点到18点
  if [[ $current_day -le 5 ]] && [[ $current_hour -ge 9 ]] && [[ $current_hour -lt 18 ]]; then
    return 0
  fi
  return 1
}

# 根据时间调整Hook行为
tool=$(echo "$input" | jq -r '.tool')

if [[ "$tool" == "Bash" ]]; then
  command=$(echo "$input" | jq -r '.tool_input.command')
  
  # 非工作时间限制某些命令
  if ! is_working_hours; then
    if echo "$command" | grep -E "(deploy|release|publish)" > /dev/null; then
      cat << EOF
{
  "permissionDecision": "ask",
  "permissionDecisionReason": "Deployment operations outside working hours require confirmation"
}
EOF
      exit 0
    fi
  fi
fi

# 周末限制
if [[ $current_day -gt 5 ]]; then
  echo "Weekend operation logged: $tool" >> "$CLAUDE_PROJECT_DIR/.claude/weekend-operations.log"
fi

echo '{"permissionDecision": "allow"}'
```

### 集成外部服务

#### 1. Slack集成
```bash
#!/bin/bash
# slack-integration.sh

SLACK_WEBHOOK="${SLACK_WEBHOOK_URL:-}"

send_slack_notification() {
  local message="$1"
  local channel="${2:-#general}"
  local username="${3:-Claude Code Hook}"
  
  if [[ -n "$SLACK_WEBHOOK" ]]; then
    curl -X POST -H 'Content-type: application/json' \
      --data "{
        \"channel\": \"$channel\",
        \"username\": \"$username\", 
        \"text\": \"$message\",
        \"icon_emoji\": \":robot_face:\"
      }" \
      "$SLACK_WEBHOOK" 2>/dev/null
  fi
}

read -d '' input
tool=$(echo "$input" | jq -r '.tool')
session_id=$(echo "$input" | jq -r '.session_id')

# 重要操作通知
case "$tool" in
  "Write"|"Edit")
    file_path=$(echo "$input" | jq -r '.tool_input.file_path')
    filename=$(basename "$file_path")
    
    # 关键文件修改通知
    if [[ "$filename" == "package.json" ]] || [[ "$filename" == "requirements.txt" ]] || [[ "$filename" == "Dockerfile" ]]; then
      send_slack_notification "🔧 Critical file modified: \`$filename\` in session \`$session_id\`" "#dev-alerts"
    fi
    ;;
    
  "Bash")
    command=$(echo "$input" | jq -r '.tool_input.command')
    
    # 部署命令通知
    if echo "$command" | grep -E "(deploy|build|release)" > /dev/null; then
      send_slack_notification "🚀 Deployment command executed: \`$command\`" "#deployments"
    fi
    ;;
esac
```

#### 2. 数据库记录
```bash
#!/bin/bash
# database-logger.sh

DB_HOST="${DB_HOST:-localhost}"
DB_NAME="${DB_NAME:-claude_hooks}"
DB_USER="${DB_USER:-claude}"

log_to_database() {
  local session_id="$1"
  local tool="$2"
  local action="$3"
  local metadata="$4"
  
  # 使用psql记录到PostgreSQL
  psql -h "$DB_HOST" -d "$DB_NAME" -U "$DB_USER" -c "
    INSERT INTO hook_logs (session_id, tool, action, metadata, timestamp)
    VALUES ('$session_id', '$tool', '$action', '$metadata', NOW());
  " 2>/dev/null
}

read -d '' input
session_id=$(echo "$input" | jq -r '.session_id')
tool=$(echo "$input" | jq -r '.tool')

# 记录Hook执行
if [[ "$tool" == "Write" || "$tool" == "Edit" ]]; then
  file_path=$(echo "$input" | jq -r '.tool_input.file_path')
  metadata="{\"file\": \"$(basename "$file_path")\", \"path\": \"$file_path\"}"
  log_to_database "$session_id" "$tool" "file_modified" "$metadata"
fi

echo '{"continue": true}'
```

### 性能优化技巧

#### 1. 缓存机制
```bash
#!/bin/bash
# cached-hook.sh

CACHE_DIR="$CLAUDE_PROJECT_DIR/.claude/cache"
CACHE_TTL=300  # 5分钟

# 创建缓存目录
mkdir -p "$CACHE_DIR"

# 计算缓存键
cache_key() {
  local input="$1"
  echo "$input" | sha256sum | cut -d' ' -f1
}

# 检查缓存
get_from_cache() {
  local key="$1"
  local cache_file="$CACHE_DIR/$key"
  
  if [[ -f "$cache_file" ]]; then
    local cache_age=$(($(date +%s) - $(stat -c %Y "$cache_file" 2>/dev/null || stat -f %m "$cache_file" 2>/dev/null)))
    if [[ $cache_age -lt $CACHE_TTL ]]; then
      cat "$cache_file"
      return 0
    fi
  fi
  return 1
}

# 保存到缓存
save_to_cache() {
  local key="$1"
  local data="$2"
  local cache_file="$CACHE_DIR/$key"
  
  echo "$data" > "$cache_file"
}

# 主要逻辑
read -d '' input
key=$(cache_key "$input")

# 尝试从缓存获取
if cached_result=$(get_from_cache "$key"); then
  echo "$cached_result"
  exit 0
fi

# 执行实际处理
result=$(process_hook_logic "$input")

# 保存到缓存
save_to_cache "$key" "$result"

echo "$result"
```

#### 2. 异步处理
```bash
#!/bin/bash
# async-hook.sh

ASYNC_DIR="$CLAUDE_PROJECT_DIR/.claude/async"
mkdir -p "$ASYNC_DIR"

# 异步执行长时间任务
execute_async() {
  local task_id="$1"
  local command="$2"
  
  # 后台执行
  (
    echo "$(date): Starting async task $task_id" >> "$ASYNC_DIR/async.log"
    eval "$command" >> "$ASYNC_DIR/$task_id.log" 2>&1
    echo "$(date): Completed async task $task_id" >> "$ASYNC_DIR/async.log"
  ) &
  
  echo $! > "$ASYNC_DIR/$task_id.pid"
}

read -d '' input
tool=$(echo "$input" | jq -r '.tool')

# 对于耗时操作，使用异步处理
if [[ "$tool" == "Write" ]]; then
  file_path=$(echo "$input" | jq -r '.tool_input.file_path')
  
  # 如果是大文件或特定类型，异步处理
  if [[ "$file_path" == *.md ]] && [[ -f "$file_path" ]] && [[ $(wc -l < "$file_path") -gt 1000 ]]; then
    task_id="index_$(date +%s)"
    execute_async "$task_id" "indexer.sh '$file_path'"
    
    echo '{"continue": true, "hookSpecificOutput": {"additionalContext": "Large file indexing started in background"}}'
    exit 0
  fi
fi

echo '{"continue": true}'
```

---

## 故障排查与调试

### 调试工具和方法

#### 1. Hook执行检查
```bash
# 检查Hook配置
claude --debug

# 查看当前Hook注册情况
/hooks

# 手动测试Hook命令
cd "$CLAUDE_PROJECT_DIR"
echo '{"tool":"Write","tool_input":{"file_path":"test.txt"}}' | .claude/hooks/my-hook.sh
```

#### 2. 详细日志记录
```bash
#!/bin/bash
# debug-hook.sh

DEBUG_LOG="$CLAUDE_PROJECT_DIR/.claude/debug.log"

debug_log() {
  local level="$1"
  local message="$2"
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S.%3N')
  
  echo "[$timestamp] [$level] [$$] $(basename "$0"): $message" >> "$DEBUG_LOG"
}

# 记录开始
debug_log "DEBUG" "Hook execution started"
debug_log "DEBUG" "Environment: CLAUDE_PROJECT_DIR=$CLAUDE_PROJECT_DIR"
debug_log "DEBUG" "Working directory: $(pwd)"

# 读取输入并记录
read -d '' input
debug_log "DEBUG" "Input received: $(echo "$input" | jq -c .)"

# 记录处理步骤
tool=$(echo "$input" | jq -r '.tool')
debug_log "INFO" "Processing tool: $tool"

# 错误处理
handle_error() {
  local error_code="$1"
  local error_message="$2"
  
  debug_log "ERROR" "Error $error_code: $error_message"
  echo "$error_message" >&2
  exit "$error_code"
}

# 主要逻辑
case "$tool" in
  "Write"|"Edit")
    file_path=$(echo "$input" | jq -r '.tool_input.file_path')
    debug_log "INFO" "File operation on: $file_path"
    
    # 文件检查
    if [[ ! -w "$(dirname "$file_path")" ]]; then
      handle_error 1 "No write permission for directory: $(dirname "$file_path")"
    fi
    ;;
esac

debug_log "DEBUG" "Hook execution completed successfully"
echo '{"continue": true}'
```

#### 3. 性能分析
```bash
#!/bin/bash
# performance-debug-hook.sh

PERF_LOG="$CLAUDE_PROJECT_DIR/.claude/performance.log"

# 记录性能指标
perf_start=$(date +%s%N)
memory_start=$(ps -o rss= -p $$)

# 性能记录函数
log_performance() {
  local operation="$1"
  local start_time="$2"
  local start_memory="$3"
  
  local end_time=$(date +%s%N)
  local end_memory=$(ps -o rss= -p $$)
  local duration=$(( (end_time - start_time) / 1000000 )) # 毫秒
  local memory_diff=$((end_memory - start_memory))
  
  echo "$(date '+%Y-%m-%d %H:%M:%S') Operation: $operation, Duration: ${duration}ms, Memory: ${memory_diff}KB" >> "$PERF_LOG"
}

# 主要逻辑
read -d '' input
tool=$(echo "$input" | jq -r '.tool')

# 执行Hook逻辑
process_hook "$input"

# 记录性能
log_performance "$tool" "$perf_start" "$memory_start"
```

### 常见问题诊断

#### 1. Hook不执行
```bash
#!/bin/bash
# hook-diagnostic.sh

echo "=== Claude Code Hook Diagnostic ==="

# 检查配置文件
check_config() {
  local config_file="$1"
  
  if [[ -f "$config_file" ]]; then
    echo "✓ Found config: $config_file"
    
    # 检查JSON语法
    if jq . "$config_file" > /dev/null 2>&1; then
      echo "✓ JSON syntax valid"
    else
      echo "✗ JSON syntax error in $config_file"
      jq . "$config_file"
    fi
    
    # 检查Hook配置
    if jq -e '.hooks' "$config_file" > /dev/null 2>&1; then
      local hook_count=$(jq '.hooks | length' "$config_file")
      echo "✓ Found $hook_count hook configurations"
    else
      echo "⚠ No hooks configured in $config_file"
    fi
  else
    echo "⚠ Config file not found: $config_file"
  fi
}

# 检查所有配置文件
check_config "$HOME/.claude/settings.json"
check_config ".claude/settings.json"
check_config ".claude/settings.local.json"

# 检查Hook脚本
echo -e "\n=== Hook Scripts ==="
if [[ -d ".claude/hooks" ]]; then
  echo "✓ Hook directory exists"
  
  for script in .claude/hooks/*; do
    if [[ -f "$script" ]]; then
      if [[ -x "$script" ]]; then
        echo "✓ Executable: $script"
      else
        echo "✗ Not executable: $script"
        echo "  Fix with: chmod +x $script"
      fi
    fi
  done
else
  echo "⚠ Hook directory not found: .claude/hooks"
fi

# 检查环境变量
echo -e "\n=== Environment ==="
echo "CLAUDE_PROJECT_DIR: ${CLAUDE_PROJECT_DIR:-'Not set'}"
echo "Working directory: $(pwd)"

# 检查权限
echo -e "\n=== Permissions ==="
if [[ -w "." ]]; then
  echo "✓ Write permission in current directory"
else
  echo "✗ No write permission in current directory"
fi

echo -e "\n=== Diagnostic Complete ==="
```

#### 2. 权限问题
```bash
#!/bin/bash
# permission-diagnostic.sh

echo "=== Permission Diagnostic ==="

# 检查文件权限
check_file_permissions() {
  local file="$1"
  
  if [[ -f "$file" ]]; then
    local perms=$(ls -l "$file" | cut -d' ' -f1)
    local owner=$(ls -l "$file" | cut -d' ' -f3)
    
    echo "File: $file"
    echo "  Permissions: $perms"
    echo "  Owner: $owner"
    echo "  Current user: $(whoami)"
    
    if [[ -r "$file" ]]; then
      echo "  ✓ Readable"
    else
      echo "  ✗ Not readable"
    fi
    
    if [[ -w "$file" ]]; then
      echo "  ✓ Writable"
    else
      echo "  ✗ Not writable"
    fi
    
    if [[ -x "$file" ]]; then
      echo "  ✓ Executable"
    else
      echo "  ✗ Not executable"
    fi
  else
    echo "File not found: $file"
  fi
  echo
}

# 检查关键文件权限
check_file_permissions ".claude/settings.json"
check_file_permissions ".claude/hooks/"

# 检查Hook脚本权限
if [[ -d ".claude/hooks" ]]; then
  for script in .claude/hooks/*; do
    if [[ -f "$script" ]]; then
      check_file_permissions "$script"
    fi
  done
fi
```

#### 3. 输出格式问题
```bash
#!/bin/bash
# output-diagnostic.sh

# 测试JSON输出格式
test_json_output() {
  local json_string="$1"
  
  echo "Testing JSON: $json_string"
  
  if echo "$json_string" | jq . > /dev/null 2>&1; then
    echo "✓ Valid JSON"
    
    # 检查必需字段
    if echo "$json_string" | jq -e '.permissionDecision' > /dev/null 2>&1; then
      local decision=$(echo "$json_string" | jq -r '.permissionDecision')
      echo "✓ Permission decision: $decision"
    fi
    
    if echo "$json_string" | jq -e '.continue' > /dev/null 2>&1; then
      local continue_flag=$(echo "$json_string" | jq -r '.continue')
      echo "✓ Continue flag: $continue_flag"
    fi
  else
    echo "✗ Invalid JSON"
    echo "$json_string" | jq . 2>&1
  fi
  echo
}

# 测试常见的JSON输出格式
echo "=== JSON Output Format Test ==="

test_json_output '{"permissionDecision": "allow"}'
test_json_output '{"permissionDecision": "deny", "permissionDecisionReason": "Test reason"}'
test_json_output '{"continue": true}'
test_json_output '{"decision": "block", "reason": "Test block"}'

# 测试错误的格式
echo "=== Common JSON Errors ==="
test_json_output '{"permissionDecision": allow}'  # 缺少引号
test_json_output '{"permissionDecision": "allow",}'  # 多余逗号
test_json_output '{permissionDecision: "allow"}'  # 缺少键引号
```

### 自动化诊断脚本

#### 完整诊断工具
```bash
#!/bin/bash
# complete-hook-diagnostic.sh

set -euo pipefail

echo "🔍 Claude Code Hook Complete Diagnostic Tool"
echo "=============================================="

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

success() { echo -e "${GREEN}✓${NC} $1"; }
warning() { echo -e "${YELLOW}⚠${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; }

# 1. 环境检查
echo -e "\n📊 Environment Check"
echo "-------------------"

if [[ -n "${CLAUDE_PROJECT_DIR:-}" ]]; then
  success "CLAUDE_PROJECT_DIR is set: $CLAUDE_PROJECT_DIR"
else
  error "CLAUDE_PROJECT_DIR is not set"
fi

echo "Current directory: $(pwd)"
echo "Current user: $(whoami)"

# 2. 配置文件检查
echo -e "\n📄 Configuration Files"
echo "---------------------"

CONFIG_FILES=(
  "$HOME/.claude/settings.json"
  ".claude/settings.json" 
  ".claude/settings.local.json"
)

for config in "${CONFIG_FILES[@]}"; do
  if [[ -f "$config" ]]; then
    success "Found: $config"
    
    # JSON语法检查
    if jq . "$config" > /dev/null 2>&1; then
      success "  Valid JSON syntax"
      
      # Hook配置检查
      if jq -e '.hooks' "$config" > /dev/null 2>&1; then
        local hook_count=$(jq '.hooks | length' "$config")
        success "  $hook_count hook(s) configured"
      else
        warning "  No hooks configured"
      fi
    else
      error "  Invalid JSON syntax"
    fi
  else
    warning "Not found: $config"
  fi
done

# 3. Hook脚本检查
echo -e "\n🔧 Hook Scripts"
echo "--------------"

if [[ -d ".claude/hooks" ]]; then
  success "Hook directory exists: .claude/hooks"
  
  script_count=0
  for script in .claude/hooks/*; do
    if [[ -f "$script" ]]; then
      ((script_count++))
      
      if [[ -x "$script" ]]; then
        success "Executable: $(basename "$script")"
      else
        error "Not executable: $(basename "$script")"
        echo "  Fix with: chmod +x $script"
      fi
      
      # 检查shebang
      if head -1 "$script" | grep -q "^#!"; then
        success "  Has shebang"
      else
        warning "  Missing shebang"
      fi
    fi
  done
  
  if [[ $script_count -eq 0 ]]; then
    warning "No scripts found in .claude/hooks/"
  fi
else
  warning "Hook directory not found: .claude/hooks"
fi

# 4. 权限检查
echo -e "\n🔐 Permissions"
echo "-------------"

if [[ -w "." ]]; then
  success "Write permission in current directory"
else
  error "No write permission in current directory"
fi

if [[ -d ".claude" ]]; then
  if [[ -w ".claude" ]]; then
    success "Write permission in .claude directory"
  else
    error "No write permission in .claude directory"
  fi
fi

# 5. Hook测试
echo -e "\n🧪 Hook Test"
echo "-----------"

# 创建测试Hook
TEST_HOOK=".claude/hooks/diagnostic-test.sh"

if [[ ! -d ".claude/hooks" ]]; then
  mkdir -p ".claude/hooks"
fi

cat > "$TEST_HOOK" << 'EOF'
#!/bin/bash
read -d '' input
echo "Hook test successful"
echo '{"continue": true}'
EOF

chmod +x "$TEST_HOOK"

# 测试Hook执行
if echo '{"tool":"Write","tool_input":{"file_path":"test.txt"}}' | "$TEST_HOOK" > /dev/null 2>&1; then
  success "Hook execution test passed"
else
  error "Hook execution test failed"
fi

# 清理测试Hook
rm -f "$TEST_HOOK"

# 6. 常见问题建议
echo -e "\n💡 Common Issues & Solutions"
echo "----------------------------"

echo "1. Hook not executing:"
echo "   - Check JSON syntax in settings files"
echo "   - Ensure hook scripts are executable (chmod +x)"
echo "   - Verify matcher patterns match tool names exactly"

echo -e "\n2. Permission denied errors:"
echo "   - Check file/directory permissions"
echo "   - Ensure Claude Code has access to project directory"

echo -e "\n3. JSON output errors:"
echo "   - Validate JSON with: echo '{...}' | jq ."
echo "   - Check for trailing commas, missing quotes"

echo -e "\n4. Environment issues:"
echo "   - Verify CLAUDE_PROJECT_DIR is set correctly"
echo "   - Check working directory is correct"

echo -e "\n✅ Diagnostic Complete"
echo "====================="
```

---

## 未来发展与扩展

### Hook系统演进方向

#### 1. 更丰富的事件类型
随着Claude Code功能的扩展，Hook系统将支持更多事件类型：

```typescript
// 未来可能的事件类型
interface FutureHookEvents {
  // 模型交互事件
  PreModelCall: "模型调用前";
  PostModelCall: "模型调用后";
  
  // 数据流事件
  DataStream: "数据流处理";
  CacheHit: "缓存命中";
  CacheMiss: "缓存未命中";
  
  // 协作事件
  UserJoin: "用户加入会话";
  UserLeave: "用户离开会话";
  SessionShare: "会话共享";
  
  // 集成事件
  MCPServerConnect: "MCP服务器连接";
  MCPServerDisconnect: "MCP服务器断开";
  ExternalAPICall: "外部API调用";
}
```

#### 2. 增强的控制能力
```json
{
  "advancedControl": {
    "async": true,
    "priority": "high",
    "retryPolicy": {
      "maxRetries": 3,
      "backoffStrategy": "exponential"
    },
    "conditions": {
      "timeRange": "09:00-18:00",
      "userRole": ["admin", "developer"],
      "environment": ["development", "staging"]
    }
  }
}
```

#### 3. 智能化Hook管理
```javascript
// AI驱动的Hook推荐
const intelligentHookManager = {
  // 基于使用模式推荐Hook
  recommendHooks(userActivity, projectType) {
    return aiModel.analyze(userActivity, projectType)
      .then(suggestions => suggestions.map(createHookTemplate));
  },
  
  // 自动优化Hook性能
  optimizeHookPerformance(hookMetrics) {
    return aiModel.optimizeConfiguration(hookMetrics);
  },
  
  // 智能错误诊断
  diagnoseHookIssues(errorLogs, configuration) {
    return aiModel.diagnoseProblem(errorLogs, configuration);
  }
};
```

### 生态系统集成

#### 1. 预置Hook库
```bash
# Hook包管理器概念
claude-hooks install security-suite
claude-hooks install git-workflow
claude-hooks install code-quality

# 社区Hook分享
claude-hooks search file-validation
claude-hooks publish my-custom-hook
```

#### 2. 企业级功能
```json
{
  "enterpriseFeatures": {
    "centralManagement": {
      "policyServer": "https://company.com/claude-policies",
      "auditLogging": true,
      "complianceChecks": ["SOX", "GDPR", "HIPAA"]
    },
    "teamCollaboration": {
      "sharedHooks": true,
      "roleBasedAccess": true,
      "approvalWorkflows": true
    }
  }
}
```

#### 3. 云服务集成
```javascript
// 云原生Hook执行
const cloudHookService = {
  // 在云端执行计算密集型Hook
  executeInCloud(hookCode, eventData) {
    return cloudFunction.invoke({
      runtime: 'nodejs18',
      code: hookCode,
      input: eventData,
      timeout: 300
    });
  },
  
  // 分布式Hook执行
  executeDistributed(hooks, eventData) {
    return Promise.all(
      hooks.map(hook => 
        cloudService.execute(hook, eventData)
      )
    );
  }
};
```

### 技术发展趋势

#### 1. 性能优化
- **并行执行优化**：更高效的Hook并行处理
- **资源管理**：智能的资源分配和限制
- **缓存策略**：多层次的缓存优化

#### 2. 安全增强
- **沙箱执行**：隔离的Hook执行环境
- **代码审计**：自动化的Hook代码安全扫描
- **权限细化**：更精细的权限控制机制

#### 3. 开发体验
- **可视化配置**：图形化的Hook配置界面
- **实时调试**：Hook执行的实时调试功能
- **模板生成**：基于AI的Hook模板自动生成

### 社区生态

#### 1. Hook市场
- **官方Hook库**：Anthropic维护的官方Hook集合
- **社区贡献**：开发者贡献的Hook分享平台
- **企业级Hook**：商业化的高级Hook解决方案

#### 2. 开发工具
- **Hook IDE插件**：VS Code、JetBrains等IDE的Hook开发插件
- **测试框架**：专门的Hook测试和验证框架
- **文档生成**：自动化的Hook文档生成工具

#### 3. 标准化
- **Hook规范**：社区驱动的Hook开发规范
- **安全标准**：Hook安全的最佳实践标准
- **互操作性**：与其他AI工具的Hook兼容性

### 长期愿景

#### 1. 智能化自动化
Hook系统将发展为智能化的自动化平台：
- **自学习Hook**：能够学习用户行为并自动调整的Hook
- **预测性执行**：基于模式识别预先执行的Hook
- **自愈系统**：能够自动修复和优化的Hook生态

#### 2. 无缝集成
- **零配置集成**：新项目自动配置适合的Hook
- **智能推荐**：基于项目类型和团队习惯的Hook推荐
- **自动化工作流**：完全自动化的开发和部署流程

#### 3. 生态互联
- **跨工具协作**：Hook在不同AI工具间的共享和协作
- **行业解决方案**：针对特定行业的Hook解决方案包
- **全球化部署**：支持全球分布式的Hook执行网络

Claude Code Hook系统作为AI驱动开发的重要组成部分，将继续演进以满足日益复杂的开发需求，为开发者提供更强大、更智能、更安全的自动化能力。

---

**文档版本**：v1.0  
**创建时间**：2025年8月30日  
**适用范围**：Claude Code用户、开发者、系统管理员  
**更新说明**：基于Claude Code官方文档和最新Hook功能整理