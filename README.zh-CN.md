# name-skill

[English](README.md) | 中文

一个 Claude Code 技能，通过自然对话帮你给产品起名字，并检查域名是否可注册。

## 功能

1. **引导式对话** — 了解你的产品、命名偏好、域名要求
2. **名字生成** — 一次生成 8-12 个候选名，覆盖不同风格
3. **域名查询** — 通过 RDAP + DNS + WHOIS 三层验证 `.com` / `.io` / `.ai` 可用性
4. **结果表格** — 展示名字、域名状态（可注册 / 已注册 / 待确认）和命名理由

## 安装

将 `nameskill/` 文件夹复制到 Claude Code 的 skills 目录：

```bash
cp -r nameskill/ ~/.claude/skills/nameskill/
```

然后开启一个新的 Claude Code 对话，技能会自动加载。

## 使用

直接说：

- "帮我起个名字"
- "给产品命名"
- "帮我想个域名"
- "I'm building an AI writing assistant, help me name it"

技能会引导你完成后续流程。

## 域名查询工具

域名查询脚本也可以独立使用：

```bash
python nameskill/scripts/check_domain.py notion.com example.io myapp.ai
```

输出（每行一个 JSON）：

```json
{"domain": "notion.com", "status": "TAKEN", "source": "rdap"}
{"domain": "myapp.ai", "status": "AVAILABLE", "source": "rdap+dns"}
```

### 三层查询链

| 层级 | 方法 | 用途 |
|------|------|------|
| 1 | RDAP | 通过 `rdap.org` 进行主查询 |
| 2 | DNS NS | 验证 RDAP 的否定结果，防止误判 |
| 3 | WHOIS | 兜底方案，用于 RDAP 不支持的后缀 |

### 环境要求

- Python 3.9+
- `dig` 命令（macOS/Linux 自带）
- `whois` 命令（macOS 自带，Linux 需 `apt install whois`）
- 无需 API key

## 许可证

MIT
