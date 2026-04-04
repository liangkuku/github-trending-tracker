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
