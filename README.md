# Claude-Codex Bridge

[English](#english) | [中文](#中文)

---

## English

### Overview

**Claude-Codex Bridge** integrates OpenAI Codex CLI into Claude Code, enabling multi-model collaboration. This allows Claude to consult Codex for code reviews, brainstorming, architecture analysis, and structured debates.

**Key Features:**
- 🔌 **MCP Server Integration** - Codex runs as an MCP server, accessible via native tools
- 🤖 **Custom Agent** - Dedicated agent for autonomous Codex interactions
- 📝 **Code Review Skill** - Specialized skill for git-based code review
- 🔄 **Multi-turn Discussions** - Support for structured debates between Claude and Codex

### The Bootstrap Story

> This entire project was **created by Claude Code itself** through a self-bootstrap process:
>
> 1. User asked Claude to integrate Codex as a tool
> 2. Claude explored `codex --help` and discovered MCP server mode
> 3. Claude created the skill, agent, and MCP configuration
> 4. Claude tested the integration and iterated based on Codex's feedback
> 5. Claude packaged everything into this repository
>
> This demonstrates how AI assistants can extend their own capabilities through tool integration.

### Prerequisites

- [Claude Code](https://claude.ai/code) installed and configured
- [OpenAI Codex CLI](https://github.com/openai/codex) installed and authenticated
- Git (for code review features)

### Installation

#### 1. Clone the repository

```bash
git clone https://github.com/yourusername/claude-codex-bridge.git
cd claude-codex-bridge
```

#### 2. Copy configuration files to your project

```bash
# Copy MCP configuration
cp .mcp.json /path/to/your/project/

# Copy agent and skill
cp -r .claude /path/to/your/project/
```

Or install globally:

```bash
# Global MCP config (available in all projects)
claude mcp add --transport stdio codex-server -- codex mcp-server

# Global agent (user-level)
mkdir -p ~/.claude/agents
cp .claude/agents/codex-integration.md ~/.claude/agents/

# Global skill (user-level)
mkdir -p ~/.claude/skills/codex-review
cp .claude/skills/codex-review/SKILL.md ~/.claude/skills/codex-review/
```

#### 3. Restart Claude Code

Restart Claude Code to load the MCP server.

### Usage

#### MCP Tools (via Agent or directly)

Two MCP tools are available after configuration:

| Tool | Purpose |
|------|---------|
| `codex` | Start a new Codex session |
| `codex-reply` | Continue an existing conversation |

**Example - Direct MCP call:**
```
Use the codex MCP tool to analyze the pros and cons of microservices vs monolith
```

**Example - Via Agent:**
```
Ask the codex agent to review my current code changes
```

#### Sandbox Permissions

| Mode | Use Case |
|------|----------|
| `read-only` | Conversations, brainstorming (default) |
| `workspace-write` | Running tests, shell commands |
| `danger-full-access` | Full file system access |

#### Code Review Skill

For git-based code review:

```bash
# Review uncommitted changes
codex review --uncommitted "Focus on security issues"

# Review against a branch
codex review --base main "Check for breaking changes"

# Review a specific commit
codex review --commit HEAD~1 "Analyze this change"
```

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Claude Code                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Main Agent                                          │    │
│  │  ├── Uses Skills (codex-review)                     │    │
│  │  └── Delegates to Subagents (codex-integration)     │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                    │
│                         ▼                                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  MCP Server (codex mcp-server)                       │    │
│  │  ├── Tool: codex (start session)                    │    │
│  │  └── Tool: codex-reply (continue conversation)      │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                    │
└─────────────────────────┼────────────────────────────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │ Codex CLI   │
                   └─────────────┘
```

### Security Notes

- **Never send secrets** (API keys, passwords) to Codex
- **Default to `read-only`** sandbox unless more access is needed
- **Review large diffs carefully** - prefer focused reviews over full codebase scans
- The `danger-full-access` mode should only be used when necessary

### Troubleshooting

| Issue | Solution |
|-------|----------|
| MCP server not found | Restart Claude Code after adding `.mcp.json` |
| Codex authentication error | Run `codex login` to authenticate |
| Sandbox restrictions | Try `read-only` mode first, escalate if needed |
| Tool name mismatch | Check `.mcp.json` server name matches tool calls |

### License

MIT License - see [LICENSE](LICENSE)

---

## 中文

### 概述

**Claude-Codex Bridge** 将 OpenAI Codex CLI 集成到 Claude Code 中，实现多模型协作。这使得 Claude 可以咨询 Codex 进行代码审查、头脑风暴、架构分析和结构化辩论。

**核心特性：**
- 🔌 **MCP Server 集成** - Codex 作为 MCP 服务器运行，通过原生工具访问
- 🤖 **自定义 Agent** - 专用 agent 处理自主的 Codex 交互
- 📝 **代码审查 Skill** - 专门用于 git 变更审查的技能
- 🔄 **多轮对话** - 支持 Claude 和 Codex 之间的结构化辩论

### 自举故事

> 这个项目完全由 **Claude Code 自己创建**，通过自举过程：
>
> 1. 用户要求 Claude 将 Codex 集成为工具
> 2. Claude 探索 `codex --help` 并发现了 MCP 服务器模式
> 3. Claude 创建了 skill、agent 和 MCP 配置
> 4. Claude 测试集成并根据 Codex 的反馈迭代改进
> 5. Claude 将所有内容打包成这个仓库
>
> 这展示了 AI 助手如何通过工具集成来扩展自己的能力。

### 前置要求

- 已安装并配置 [Claude Code](https://claude.ai/code)
- 已安装并认证 [OpenAI Codex CLI](https://github.com/openai/codex)
- Git（用于代码审查功能）

### 安装

#### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/claude-codex-bridge.git
cd claude-codex-bridge
```

#### 2. 复制配置文件到你的项目

```bash
# 复制 MCP 配置
cp .mcp.json /path/to/your/project/

# 复制 agent 和 skill
cp -r .claude /path/to/your/project/
```

或者全局安装：

```bash
# 全局 MCP 配置（所有项目可用）
claude mcp add --transport stdio codex-server -- codex mcp-server

# 全局 agent（用户级别）
mkdir -p ~/.claude/agents
cp .claude/agents/codex-integration.md ~/.claude/agents/

# 全局 skill（用户级别）
mkdir -p ~/.claude/skills/codex-review
cp .claude/skills/codex-review/SKILL.md ~/.claude/skills/codex-review/
```

#### 3. 重启 Claude Code

重启 Claude Code 以加载 MCP 服务器。

### 使用方法

#### MCP 工具（通过 Agent 或直接调用）

配置后有两个 MCP 工具可用：

| 工具 | 用途 |
|------|------|
| `codex` | 启动新的 Codex 会话 |
| `codex-reply` | 继续现有对话 |

**示例 - 直接 MCP 调用：**
```
使用 codex MCP 工具分析微服务和单体架构的优缺点
```

**示例 - 通过 Agent：**
```
让 codex agent 审查我当前的代码更改
```

#### 沙盒权限

| 模式 | 使用场景 |
|------|----------|
| `read-only` | 对话、头脑风暴（默认） |
| `workspace-write` | 运行测试、shell 命令 |
| `danger-full-access` | 完全文件系统访问 |

#### 代码审查 Skill

用于 git 变更审查：

```bash
# 审查未提交的更改
codex review --uncommitted "关注安全问题"

# 与分支对比审查
codex review --base main "检查破坏性更改"

# 审查特定提交
codex review --commit HEAD~1 "分析这个更改"
```

### 架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Claude Code                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  主 Agent                                                ││
│  │  ├── 使用 Skills (codex-review)                         ││
│  │  └── 委托给 Subagents (codex-integration)               ││
│  └──────────────────────┬──────────────────────────────────┘│
│                         │                                    │
│                         ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  MCP Server (codex mcp-server)                          ││
│  │  ├── 工具: codex (启动会话)                              ││
│  │  └── 工具: codex-reply (继续对话)                        ││
│  └──────────────────────┬──────────────────────────────────┘│
│                         │                                    │
└─────────────────────────┼────────────────────────────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │ Codex CLI   │
                   └─────────────┘
```

### 安全注意事项

- **永远不要发送密钥**（API keys、密码）给 Codex
- **默认使用 `read-only`** 沙盒，除非需要更多访问权限
- **谨慎审查大型 diff** - 优先进行专注的审查而非全代码库扫描
- `danger-full-access` 模式仅在必要时使用

### 故障排查

| 问题 | 解决方案 |
|------|----------|
| MCP 服务器未找到 | 添加 `.mcp.json` 后重启 Claude Code |
| Codex 认证错误 | 运行 `codex login` 进行认证 |
| 沙盒限制 | 先尝试 `read-only` 模式，必要时升级 |
| 工具名称不匹配 | 检查 `.mcp.json` 服务器名称与工具调用是否匹配 |

### 许可证

MIT 许可证 - 见 [LICENSE](LICENSE)
