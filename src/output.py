"""生成 Markdown 输出"""

from pathlib import Path

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
        f"| 排名 | 项目 | 语言 | ⭐ Star | 📈 {period} |",
        "|:---:|------|:----:|-------:|-------:|",
    ]
    
    for repo in repos:
        lang = repo.language or "-"
        stars = _format_number(repo.stars)
        growth = f"+{_format_number(repo.growth)}"
        
        # 项目行
        line = f"| {repo.rank} | [{repo.name}]({repo.url}) | {lang} | {stars} | {growth} |"
        lines.append(line)
        
        # 描述单独一行（完整显示）
        if repo.description:
            desc = repo.description.replace("|", "\\|")
            lines.append(f"| | ↳ {desc} | | | |")
    
    return "\n".join(lines)


def _format_number(num: int) -> str:
    """格式化数字，大于 1000 显示为 k"""
    if num >= 1000:
        return f"{num / 1000:.1f}k"
    return str(num)


def save_outputs(
    daily: list[Repository],
    weekly: list[Repository],
    date: str,
    data_dir: str = "data"
) -> tuple[Path, Path]:
    """
    保存 Markdown 文件
    
    目录结构: 
    - data/daily/YYYY/MM/YYYY-MM-DD.md
    - data/daily/README.md (倒序索引)
    - data/latest.md
    
    Args:
        daily: 今日热门项目列表
        weekly: 本周热门项目列表
        date: 日期字符串 (YYYY-MM-DD)
        data_dir: 数据目录路径
    
    Returns:
        (markdown_path, latest_path) 元组
    """
    # 解析日期
    year, month, day = date.split("-")
    
    # 创建目录结构: data/daily/YYYY/MM/
    data_path = Path(data_dir)
    month_path = data_path / "daily" / year / month
    month_path.mkdir(parents=True, exist_ok=True)
    
    # 生成内容
    markdown_content = generate_markdown(daily, weekly, date)
    
    # 保存每日存档: data/daily/YYYY/MM/YYYY-MM-DD.md
    md_file = month_path / f"{date}.md"
    md_file.write_text(markdown_content, encoding="utf-8")
    
    # 保存 latest.md
    latest_file = data_path / "latest.md"
    latest_file.write_text(markdown_content, encoding="utf-8")
    
    # 更新 README 索引
    _update_readme_index(data_path / "daily")
    
    return md_file, latest_file


def _update_readme_index(daily_path: Path) -> None:
    """
    更新 data/daily/README.md 索引文件
    扫描所有 .md 文件，按日期倒序生成索引
    """
    # 收集所有日期文件
    entries = []
    
    for year_dir in sorted(daily_path.iterdir(), reverse=True):
        if not year_dir.is_dir() or year_dir.name.startswith("."):
            continue
        
        year = year_dir.name
        
        for month_dir in sorted(year_dir.iterdir(), reverse=True):
            if not month_dir.is_dir():
                continue
            
            month = month_dir.name
            
            for md_file in sorted(month_dir.glob("*.md"), reverse=True):
                # 文件名格式: YYYY-MM-DD.md
                date_str = md_file.stem  # e.g., "2026-04-04"
                relative_path = f"{year}/{month}/{md_file.name}"
                entries.append((date_str, relative_path))
    
    # 生成 README 内容
    lines = [
        "# 📊 GitHub Trending 历史记录",
        "",
        "> 最新数据请查看 [latest.md](../latest.md)",
        "",
        "## 历史归档",
        "",
        "| 日期 | 报告 |",
        "|------|------|",
    ]
    
    for date_str, path in entries:
        lines.append(f"| {date_str} | [📄 查看]({path}) |")
    
    if not entries:
        lines.append("| - | 暂无数据 |")
    
    lines.append("")
    lines.append("---")
    lines.append("*由 GitHub Actions 自动更新*")
    
    # 写入 README.md
    readme_file = daily_path / "README.md"
    readme_file.write_text("\n".join(lines), encoding="utf-8")
