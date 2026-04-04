# GitHub Trending Tracker 设计文档

> 📅 创建日期: 2026-04-04

## 1. 项目概述

### 1.1 项目目标
构建一个自动化工具，每天定时获取 GitHub Trending 热门项目（Daily Top 5 + Weekly Top 5），生成报告并通过邮件通知。

### 1.2 核心功能
- 爬取 GitHub Trending Daily 和 Weekly 榜单
- 生成 Markdown 和 JSON 格式的报告
- 自动存档到 Git 仓库
- 通过 QQ 邮箱发送每日通知

## 2. 需求规格

| 项目 | 选择 |
|------|------|
| **数据来源** | GitHub Trending Daily Top 5 + Weekly Top 5 |
| **运行环境** | GitHub Actions |
| **运行时间** | 北京时间每天早上 7:00（UTC 23:00） |
| **实现语言** | Python |
| **语言范围** | 所有编程语言 |
| **输出方式** | Markdown + JSON + QQ邮箱通知 |
| **存储位置** | 同一仓库的 `data/` 目录 |

## 3. 系统架构

### 3.1 项目结构

```
github-trending-tracker/
├── .github/
│   └── workflows/
│       └── daily-trending.yml    # GitHub Actions 工作流
├── src/
│   ├── __init__.py
│   ├── trending.py               # 爬取 GitHub Trending
│   ├── output.py                 # 生成 Markdown/JSON 输出
│   └── email_sender.py           # QQ 邮箱发送
├── data/
│   ├── daily/                    # 每日存档
│   │   ├── YYYY-MM-DD.json
│   │   └── YYYY-MM-DD.md
│   └── latest.md                 # 最新一期（方便快速查看）
├── requirements.txt
└── README.md
```

### 3.2 模块职责

| 模块 | 职责 |
|------|------|
| `trending.py` | 爬取 GitHub Trending 页面，解析项目信息 |
| `output.py` | 将数据格式化为 Markdown 和 JSON |
| `email_sender.py` | 通过 QQ 邮箱 SMTP 发送邮件 |
| `daily-trending.yml` | 定义 GitHub Actions 工作流 |

## 4. 数据获取

### 4.1 数据源

| 榜单 | URL |
|------|-----|
| Daily Top 5 | `https://github.com/trending?since=daily` |
| Weekly Top 5 | `https://github.com/trending?since=weekly` |

### 4.2 解析字段

每个项目需要解析以下信息：

| 字段 | 说明 | 示例 |
|------|------|------|
| `name` | 仓库全名 | `microsoft/vscode` |
| `url` | 项目链接 | `https://github.com/microsoft/vscode` |
| `description` | 项目描述 | `Visual Studio Code` |
| `language` | 编程语言 | `TypeScript` |
| `stars` | Star 总数 | `150000` |
| `growth` | 近期增长 | `1234`（今日/本周） |
| `forks` | Fork 数 | `25000` |

### 4.3 爬虫实现

使用 `requests` + `BeautifulSoup` 解析 HTML：
- 设置合理的 User-Agent
- 处理网络超时和重试
- 解析 Trending 页面的 DOM 结构

## 5. 输出格式

### 5.1 Markdown 格式

```markdown
# GitHub 热门项目日报

> 📅 2026-04-04 | 自动生成

## 🔥 今日热门 (Daily Top 5)

| 排名 | 项目 | 描述 | 语言 | ⭐ Star | 📈 今日 |
|:---:|------|------|:----:|-------:|-------:|
| 1 | [owner/repo](链接) | 项目描述... | Python | 12.3k | +1,234 |
| 2 | ... | ... | ... | ... | ... |

## 📊 本周热门 (Weekly Top 5)

| 排名 | 项目 | 描述 | 语言 | ⭐ Star | 📈 本周 |
|:---:|------|------|:----:|-------:|-------:|
| 1 | [owner/repo](链接) | 项目描述... | Go | 45.6k | +3,456 |
| 2 | ... | ... | ... | ... | ... |

---
*由 GitHub Actions 自动生成*
```

### 5.2 JSON 格式

```json
{
  "date": "2026-04-04",
  "generated_at": "2026-04-04T07:00:00+08:00",
  "daily": [
    {
      "rank": 1,
      "name": "owner/repo",
      "url": "https://github.com/owner/repo",
      "description": "项目描述",
      "language": "Python",
      "stars": 12300,
      "growth": 1234,
      "forks": 500
    }
  ],
  "weekly": [
    {
      "rank": 1,
      "name": "owner/repo",
      "url": "https://github.com/owner/repo",
      "description": "项目描述",
      "language": "Go",
      "stars": 45600,
      "growth": 3456,
      "forks": 2000
    }
  ]
}
```

### 5.3 邮件格式

- **标题**: `📊 GitHub 热门项目日报 - 2026-04-04`
- **正文**: HTML 格式，内容与 Markdown 一致，但渲染为美观的表格

## 6. 邮件配置

### 6.1 QQ 邮箱 SMTP 设置

| 配置项 | 值 |
|--------|-----|
| SMTP 服务器 | `smtp.qq.com` |
| 端口 | `465`（SSL） |
| 认证方式 | 邮箱地址 + 授权码 |

### 6.2 GitHub Secrets

需要在仓库设置中配置以下密钥：

| Secret 名称 | 说明 |
|------------|------|
| `QQ_EMAIL` | 发送方 QQ 邮箱地址 |
| `QQ_EMAIL_PASSWORD` | QQ 邮箱授权码（非登录密码） |
| `TO_EMAIL` | 接收方邮箱地址 |

> ⚠️ **获取授权码**: QQ 邮箱 → 设置 → 账户 → POP3/SMTP 服务 → 开启并获取授权码

## 7. GitHub Actions 工作流

### 7.1 触发条件

```yaml
on:
  schedule:
    # 北京时间早上 7:00 = UTC 23:00（前一天）
    - cron: '0 23 * * *'
  workflow_dispatch:  # 支持手动触发
```

### 7.2 工作流步骤

1. **检出代码** - `actions/checkout@v4`
2. **设置 Python** - `actions/setup-python@v5`
3. **安装依赖** - `pip install -r requirements.txt`
4. **运行爬虫** - 执行主脚本，生成报告
5. **提交数据** - 将 Markdown/JSON 提交到仓库
6. **发送邮件** - 通过 QQ 邮箱发送通知

### 7.3 权限配置

```yaml
permissions:
  contents: write  # 允许提交到仓库
```

## 8. 错误处理

| 场景 | 处理方式 |
|------|----------|
| 网络请求失败 | 重试 3 次，间隔 5 秒 |
| 页面解析失败 | 记录错误日志，跳过当前项目 |
| 邮件发送失败 | 记录错误，不影响数据存档 |
| 数据为空 | 不生成文件，发送告警邮件 |

## 9. 依赖清单

```
requests>=2.28.0
beautifulsoup4>=4.11.0
```

## 10. 后续扩展（可选）

- [ ] 支持按编程语言筛选
- [ ] 添加更多数据源（Hacker News、Reddit）
- [ ] 生成静态网页（GitHub Pages）
- [ ] 数据可视化（Star 增长趋势图）
