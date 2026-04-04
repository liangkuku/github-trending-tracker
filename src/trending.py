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
