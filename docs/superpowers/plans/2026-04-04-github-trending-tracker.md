# GitHub Trending Tracker 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个自动化工具，每天定时获取 GitHub Trending 热门项目并通过邮件通知

**Architecture:** Python 爬虫获取 GitHub Trending 数据 → 生成 Markdown/JSON 报告 → GitHub Actions 定时运行 → QQ 邮箱发送通知

**Tech Stack:** Python 3.11+, requests, beautifulsoup4, GitHub Actions

---

## 文件结构

```
github-trending-tracker/
├── .github/workflows/daily-trending.yml   # GitHub Actions 工作流
├── src/
│   ├── __init__.py                        # 包初始化
│   ├── trending.py                        # 爬取 GitHub Trending
│   ├── output.py                          # 生成 Markdown/JSON
│   └── email_sender.py                    # QQ 邮箱发送
├── main.py                                # 主入口
├── data/
│   ├── daily/                             # 每日存档目录
│   └── .gitkeep                           # 保持目录存在
├── requirements.txt                       # 依赖清单
└── README.md                              # 项目说明
```

---

## Task 1: 项目初始化

**Files:**
- Create: `requirements.txt`
- Create: `src/__init__.py`
- Create: `data/.gitkeep`
- Create: `data/daily/.gitkeep`

- [ ] **Step 1: 创建 requirements.txt**

```
requests>=2.28.0
beautifulsoup4>=4.11.0
```

- [ ] **Step 2: 创建 src/__init__.py**

```python
"""GitHub Trending Tracker - 每日热门项目追踪器"""
```

- [ ] **Step 3: 创建数据目录占位文件**

创建 `data/.gitkeep` 和 `data/daily/.gitkeep`（空文件）

- [ ] **Step 4: 验证目录结构**

Run: `ls -la && ls -la src/ && ls -la data/`

Expected: 目录结构正确

- [ ] **Step 5: Commit**

```bash
git add requirements.txt src/__init__.py data/
git commit -m "chore: initialize project structure"
```

---

## Task 2: 实现 Trending 爬虫

**Files:**
- Create: `src/trending.py`

- [ ] **Step 1: 创建 trending.py 基础结构**

```python
"""爬取 GitHub Trending 页面"""

import time
from dataclasses import dataclass
from typing import Optional

import requests
from bs4 import BeautifulSoup


@dataclass
class Repository:
    """仓库信息"""
    rank: int
    name: str  # owner/repo
    url: str
    description: str
    language: Optional[str]
    stars: int
    forks: int
    growth: int  # 今日/本周增长


GITHUB_TRENDING_URL = "https://github.com/trending"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}
MAX_RETRIES = 3
RETRY_DELAY = 5


def fetch_trending(since: str = "daily", limit: int = 5) -> list[Repository]:
    """
    获取 GitHub Trending 项目
    
    Args:
        since: "daily" 或 "weekly"
        limit: 返回项目数量
    
    Returns:
        Repository 列表
    """
    url = f"{GITHUB_TRENDING_URL}?since={since}"
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            return _parse_trending_page(response.text, limit)
        except requests.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                print(f"请求失败，{RETRY_DELAY}秒后重试: {e}")
                time.sleep(RETRY_DELAY)
            else:
                raise RuntimeError(f"获取 Trending 失败: {e}") from e
    
    return []


def _parse_trending_page(html: str, limit: int) -> list[Repository]:
    """解析 Trending 页面 HTML"""
    soup = BeautifulSoup(html, "html.parser")
    repos = []
    
    articles = soup.select("article.Box-row")[:limit]
    
    for rank, article in enumerate(articles, start=1):
        repo = _parse_repo_article(article, rank)
        if repo:
            repos.append(repo)
    
    return repos


def _parse_repo_article(article, rank: int) -> Optional[Repository]:
    """解析单个仓库的 HTML 元素"""
    try:
        # 仓库名称 (owner/repo)
        name_elem = article.select_one("h2 a")
        if not name_elem:
            return None
        
        name = name_elem.get_text(strip=True).replace(" ", "").replace("\n", "")
        url = f"https://github.com{name_elem['href']}"
        
        # 描述
        desc_elem = article.select_one("p")
        description = desc_elem.get_text(strip=True) if desc_elem else ""
        
        # 编程语言
        lang_elem = article.select_one("[itemprop='programmingLanguage']")
        language = lang_elem.get_text(strip=True) if lang_elem else None
        
        # Star 和 Fork 数量
        stats = article.select("a.Link--muted")
        stars = _parse_number(stats[0].get_text(strip=True)) if len(stats) > 0 else 0
        forks = _parse_number(stats[1].get_text(strip=True)) if len(stats) > 1 else 0
        
        # 今日/本周增长
        growth_elem = article.select_one("span.d-inline-block.float-sm-right")
        growth = 0
        if growth_elem:
            growth_text = growth_elem.get_text(strip=True)
            growth = _parse_number(growth_text.split()[0])
        
        return Repository(
            rank=rank,
            name=name,
            url=url,
            description=description,
            language=language,
            stars=stars,
            forks=forks,
            growth=growth
        )
    except Exception as e:
        print(f"解析仓库失败: {e}")
        return None


def _parse_number(text: str) -> int:
    """解析数字字符串，支持 k 后缀"""
    text = text.strip().replace(",", "")
    if text.endswith("k"):
        return int(float(text[:-1]) * 1000)
    try:
        return int(text)
    except ValueError:
        return 0
```

- [ ] **Step 2: 测试爬虫功能**

Run: `python -c "from src.trending import fetch_trending; repos = fetch_trending('daily', 5); print(f'获取到 {len(repos)} 个项目'); [print(f'{r.rank}. {r.name} - {r.stars} stars') for r in repos]"`

Expected: 输出 5 个项目信息

- [ ] **Step 3: Commit**

```bash
git add src/trending.py
git commit -m "feat: implement GitHub Trending scraper"
```

---

## Task 3: 实现输出模块

**Files:**
- Create: `src/output.py`

- [ ] **Step 1: 创建 output.py**

```python
"""生成 Markdown 和 JSON 输出"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.trending import Repository


def generate_markdown(
    daily: list[Repository],
    weekly: list[Repository],
    date: str
) -> str:
    """
    生成 Markdown 格式报告
    
    Args:
        daily: 今日热门项目列表
        weekly: 本周热门项目列表
        date: 日期字符串 (YYYY-MM-DD)
    
    Returns:
        Markdown 格式字符串
    """
    lines = [
        "# GitHub 热门项目日报",
        "",
        f"> 📅 {date} | 自动生成",
        "",
        "## 🔥 今日热门 (Daily Top 5)",
        "",
        _generate_table(daily, "今日"),
        "",
        "## 📊 本周热门 (Weekly Top 5)",
        "",
        _generate_table(weekly, "本周"),
        "",
        "---",
        "*由 GitHub Actions 自动生成*",
    ]
    
    return "\n".join(lines)


def _generate_table(repos: list[Repository], period: str) -> str:
    """生成 Markdown 表格"""
    if not repos:
        return "*暂无数据*"
    
    lines = [
        f"| 排名 | 项目 | 描述 | 语言 | ⭐ Star | 📈 {period} |",
        "|:---:|------|------|:----:|-------:|-------:|",
    ]
    
    for repo in repos:
        desc = repo.description[:50] + "..." if len(repo.description) > 50 else repo.description
        desc = desc.replace("|", "\\|")  # 转义表格分隔符
        lang = repo.language or "-"
        stars = _format_number(repo.stars)
        growth = f"+{_format_number(repo.growth)}"
        
        line = f"| {repo.rank} | [{repo.name}]({repo.url}) | {desc} | {lang} | {stars} | {growth} |"
        lines.append(line)
    
    return "\n".join(lines)


def _format_number(num: int) -> str:
    """格式化数字，大于 1000 显示为 k"""
    if num >= 1000:
        return f"{num / 1000:.1f}k"
    return str(num)


def generate_json(
    daily: list[Repository],
    weekly: list[Repository],
    date: str
) -> dict[str, Any]:
    """
    生成 JSON 格式数据
    
    Args:
        daily: 今日热门项目列表
        weekly: 本周热门项目列表
        date: 日期字符串 (YYYY-MM-DD)
    
    Returns:
        JSON 可序列化的字典
    """
    return {
        "date": date,
        "generated_at": datetime.now().astimezone().isoformat(),
        "daily": [_repo_to_dict(r) for r in daily],
        "weekly": [_repo_to_dict(r) for r in weekly],
    }


def _repo_to_dict(repo: Repository) -> dict[str, Any]:
    """将 Repository 转换为字典"""
    return {
        "rank": repo.rank,
        "name": repo.name,
        "url": repo.url,
        "description": repo.description,
        "language": repo.language,
        "stars": repo.stars,
        "forks": repo.forks,
        "growth": repo.growth,
    }


def save_outputs(
    daily: list[Repository],
    weekly: list[Repository],
    date: str,
    data_dir: str = "data"
) -> tuple[Path, Path, Path]:
    """
    保存 Markdown 和 JSON 文件
    
    Args:
        daily: 今日热门项目列表
        weekly: 本周热门项目列表
        date: 日期字符串 (YYYY-MM-DD)
        data_dir: 数据目录路径
    
    Returns:
        (markdown_path, json_path, latest_path) 元组
    """
    data_path = Path(data_dir)
    daily_path = data_path / "daily"
    daily_path.mkdir(parents=True, exist_ok=True)
    
    # 生成内容
    markdown_content = generate_markdown(daily, weekly, date)
    json_content = generate_json(daily, weekly, date)
    
    # 保存每日存档
    md_file = daily_path / f"{date}.md"
    json_file = daily_path / f"{date}.json"
    
    md_file.write_text(markdown_content, encoding="utf-8")
    json_file.write_text(
        json.dumps(json_content, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    # 保存 latest.md
    latest_file = data_path / "latest.md"
    latest_file.write_text(markdown_content, encoding="utf-8")
    
    return md_file, json_file, latest_file
```

- [ ] **Step 2: 验证输出模块**

Run: `python -c "from src.trending import Repository; from src.output import generate_markdown; r = Repository(1, 'test/repo', 'https://github.com/test/repo', 'Test desc', 'Python', 1234, 100, 50); print(generate_markdown([r], [r], '2026-04-04'))"`

Expected: 输出格式正确的 Markdown

- [ ] **Step 3: Commit**

```bash
git add src/output.py
git commit -m "feat: implement Markdown and JSON output generation"
```

---

## Task 4: 实现邮件发送模块

**Files:**
- Create: `src/email_sender.py`

- [ ] **Step 1: 创建 email_sender.py**

```python
"""QQ 邮箱发送模块"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465


def send_email(
    subject: str,
    html_content: str,
    to_email: str | None = None,
    from_email: str | None = None,
    password: str | None = None,
) -> bool:
    """
    通过 QQ 邮箱发送邮件
    
    Args:
        subject: 邮件标题
        html_content: HTML 格式的邮件正文
        to_email: 收件人地址（默认从环境变量读取）
        from_email: 发件人地址（默认从环境变量读取）
        password: QQ 邮箱授权码（默认从环境变量读取）
    
    Returns:
        是否发送成功
    """
    # 从环境变量读取配置
    from_email = from_email or os.environ.get("QQ_EMAIL")
    password = password or os.environ.get("QQ_EMAIL_PASSWORD")
    to_email = to_email or os.environ.get("TO_EMAIL")
    
    if not all([from_email, password, to_email]):
        print("邮件配置不完整，跳过发送")
        return False
    
    try:
        # 创建邮件
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email
        
        # 添加 HTML 内容
        html_part = MIMEText(html_content, "html", "utf-8")
        msg.attach(html_part)
        
        # 发送邮件
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
        
        print(f"邮件发送成功: {to_email}")
        return True
        
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False


def markdown_to_html(markdown: str) -> str:
    """
    将 Markdown 转换为简单 HTML
    
    注意：这是简化版转换，只处理表格和基本格式
    """
    lines = markdown.split("\n")
    html_lines = []
    in_table = False
    
    for line in lines:
        # 标题
        if line.startswith("# "):
            html_lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("> "):
            html_lines.append(f"<blockquote>{line[2:]}</blockquote>")
        # 表格
        elif line.startswith("|"):
            if not in_table:
                html_lines.append("<table border='1' cellpadding='8' cellspacing='0' style='border-collapse: collapse;'>")
                in_table = True
            
            if "|:---" in line or "|---" in line:
                continue  # 跳过分隔行
            
            cells = [c.strip() for c in line.split("|")[1:-1]]
            row = "".join(f"<td>{cell}</td>" for cell in cells)
            html_lines.append(f"<tr>{row}</tr>")
        else:
            if in_table:
                html_lines.append("</table>")
                in_table = False
            if line.strip():
                html_lines.append(f"<p>{line}</p>")
    
    if in_table:
        html_lines.append("</table>")
    
    # 包装完整 HTML
    body = "\n".join(html_lines)
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; }}
            h1 {{ color: #333; }}
            h2 {{ color: #555; margin-top: 30px; }}
            table {{ width: 100%; margin: 10px 0; }}
            td {{ padding: 8px; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            a {{ color: #0366d6; text-decoration: none; }}
            blockquote {{ color: #666; border-left: 3px solid #ddd; padding-left: 10px; margin: 10px 0; }}
        </style>
    </head>
    <body>
    {body}
    </body>
    </html>
    """
```

- [ ] **Step 2: 验证模块导入**

Run: `python -c "from src.email_sender import send_email, markdown_to_html; print('模块导入成功')"`

Expected: 输出 "模块导入成功"

- [ ] **Step 3: Commit**

```bash
git add src/email_sender.py
git commit -m "feat: implement QQ email sender module"
```

---

## Task 5: 实现主入口

**Files:**
- Create: `main.py`

- [ ] **Step 1: 创建 main.py**

```python
#!/usr/bin/env python3
"""GitHub Trending Tracker 主入口"""

import sys
from datetime import datetime

from src.trending import fetch_trending
from src.output import save_outputs, generate_markdown
from src.email_sender import send_email, markdown_to_html


def main() -> int:
    """主函数"""
    print("=" * 50)
    print("GitHub Trending Tracker")
    print("=" * 50)
    
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n📅 日期: {today}")
    
    # 获取 Trending 数据
    print("\n🔍 正在获取 Daily Trending...")
    try:
        daily = fetch_trending("daily", limit=5)
        print(f"   ✓ 获取到 {len(daily)} 个项目")
    except Exception as e:
        print(f"   ✗ 获取失败: {e}")
        daily = []
    
    print("\n🔍 正在获取 Weekly Trending...")
    try:
        weekly = fetch_trending("weekly", limit=5)
        print(f"   ✓ 获取到 {len(weekly)} 个项目")
    except Exception as e:
        print(f"   ✗ 获取失败: {e}")
        weekly = []
    
    if not daily and not weekly:
        print("\n❌ 未获取到任何数据，退出")
        return 1
    
    # 保存输出文件
    print("\n💾 正在保存文件...")
    try:
        md_file, json_file, latest_file = save_outputs(daily, weekly, today)
        print(f"   ✓ Markdown: {md_file}")
        print(f"   ✓ JSON: {json_file}")
        print(f"   ✓ Latest: {latest_file}")
    except Exception as e:
        print(f"   ✗ 保存失败: {e}")
        return 1
    
    # 发送邮件
    print("\n📧 正在发送邮件...")
    markdown_content = generate_markdown(daily, weekly, today)
    html_content = markdown_to_html(markdown_content)
    subject = f"📊 GitHub 热门项目日报 - {today}"
    
    if send_email(subject, html_content):
        print("   ✓ 邮件发送成功")
    else:
        print("   ⚠ 邮件发送跳过或失败（不影响数据存档）")
    
    print("\n✅ 完成!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: 本地测试运行**

Run: `python main.py`

Expected: 输出运行日志，生成 data/daily/ 下的文件

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat: implement main entry point"
```

---

## Task 6: 创建 GitHub Actions 工作流

**Files:**
- Create: `.github/workflows/daily-trending.yml`

- [ ] **Step 1: 创建工作流文件**

```yaml
name: Daily GitHub Trending

on:
  schedule:
    # 北京时间早上 7:00 = UTC 23:00（前一天）
    - cron: '0 23 * * *'
  workflow_dispatch:  # 支持手动触发

permissions:
  contents: write

jobs:
  fetch-trending:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run trending tracker
        env:
          QQ_EMAIL: ${{ secrets.QQ_EMAIL }}
          QQ_EMAIL_PASSWORD: ${{ secrets.QQ_EMAIL_PASSWORD }}
          TO_EMAIL: ${{ secrets.TO_EMAIL }}
        run: python main.py
      
      - name: Commit and push data
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add data/
          git diff --staged --quiet || git commit -m "📊 Update trending data - $(date +'%Y-%m-%d')"
          git push
```

- [ ] **Step 2: 验证 YAML 语法**

Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/daily-trending.yml')); print('YAML 语法正确')"`

Expected: 输出 "YAML 语法正确"

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/daily-trending.yml
git commit -m "ci: add GitHub Actions workflow for daily trending"
```

---

## Task 7: 创建 README

**Files:**
- Create: `README.md`

- [ ] **Step 1: 创建 README.md**

```markdown
# GitHub Trending Tracker

每天自动获取 GitHub Trending 热门项目，生成报告并发送邮件通知。

## 功能

- 🔥 获取 GitHub Trending Daily Top 5
- 📊 获取 GitHub Trending Weekly Top 5
- 📄 生成 Markdown 和 JSON 格式报告
- 📧 通过 QQ 邮箱发送每日通知
- ⏰ GitHub Actions 定时自动运行

## 配置

### 1. Fork 本仓库

### 2. 配置 Secrets

在仓库的 Settings → Secrets and variables → Actions 中添加：

| Secret 名称 | 说明 |
|------------|------|
| `QQ_EMAIL` | 发送方 QQ 邮箱地址 |
| `QQ_EMAIL_PASSWORD` | QQ 邮箱授权码（非登录密码） |
| `TO_EMAIL` | 接收方邮箱地址 |

**获取 QQ 邮箱授权码：**
1. 登录 QQ 邮箱网页版
2. 设置 → 账户 → POP3/SMTP 服务
3. 开启服务并获取授权码

### 3. 启用 Actions

仓库的 Actions 默认启用，每天北京时间早上 7:00 自动运行。

也可以手动触发：Actions → Daily GitHub Trending → Run workflow

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行（不发送邮件）
python main.py

# 运行（发送邮件）
export QQ_EMAIL="your@qq.com"
export QQ_EMAIL_PASSWORD="your_auth_code"
export TO_EMAIL="receiver@example.com"
python main.py
```

## 数据存储

- `data/daily/YYYY-MM-DD.md` - 每日 Markdown 报告
- `data/daily/YYYY-MM-DD.json` - 每日 JSON 数据
- `data/latest.md` - 最新一期报告

## License

MIT
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with setup instructions"
```

---

## Task 8: 最终验证

- [ ] **Step 1: 完整运行测试**

Run: `python main.py`

Expected: 成功获取数据，生成文件

- [ ] **Step 2: 检查生成的文件**

Run: `cat data/latest.md`

Expected: 显示格式正确的 Markdown 报告

- [ ] **Step 3: 检查 JSON 文件**

Run: `cat data/daily/*.json | head -50`

Expected: 显示格式正确的 JSON 数据

- [ ] **Step 4: 最终 Commit（如有遗漏）**

```bash
git status
git add -A
git diff --staged --quiet || git commit -m "chore: final cleanup"
```

---

## 部署清单

完成以上任务后，你需要：

1. **创建 GitHub 仓库** - 将代码推送到 GitHub
2. **配置 Secrets** - 在仓库设置中添加 QQ_EMAIL、QQ_EMAIL_PASSWORD、TO_EMAIL
3. **手动触发测试** - 在 Actions 页面手动运行一次验证
4. **等待定时运行** - 北京时间每天早上 7:00 自动运行
