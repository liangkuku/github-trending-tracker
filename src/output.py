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
