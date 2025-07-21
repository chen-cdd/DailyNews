import re
import time
import requests
from bs4 import BeautifulSoup, Tag
from typing import Optional, Dict

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
HEADERS = {"User-Agent": USER_AGENT}

# 微信公众号文章选择器
WECHAT_TITLE_SELECTORS = [
    "#activity-name", "h1.rich_media_title",
    "h2.rich_media_title_text", "div.rich_media_title"
]
WECHAT_CONTENT_SELECTORS = ["#js_content", "div.rich_media_content"]

def get_article(url: str) -> Dict:
    """根据 URL 自动选择抓取逻辑，支持公众号和通用网页。"""
    if "mp.weixin.qq.com" in url:
        return _get_wechat_article(url)
    else:
        return _get_generic_article(url)

def _get_wechat_article(url: str) -> Dict:
    """抓取公众号文章纯文本（标题、正文）及发布时间戳。"""
    resp = requests.get(url, headers=HEADERS, timeout=(5, 20))
    resp.raise_for_status()
    html = resp.text
    soup = BeautifulSoup(html, "lxml")

    title = _pick_first(soup, WECHAT_TITLE_SELECTORS)
    content = _extract_content(soup)
    ts = _parse_timestamp(html)

    return {"url": url, "title": title, "content": content, "ts": ts}

def _get_generic_article(url: str) -> Dict:
    """抓取通用网页正文，返回标题和纯文本内容，没有时间戳。"""
    resp = requests.get(url, headers=HEADERS, timeout=(5, 20))
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    # 标题
    title = soup.title.string.strip() if soup.title and soup.title.string else url
    # 内容：提取所有 <p> 文本
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all('p')]
    content = "\n".join([p for p in paragraphs if p])

    return {"url": url, "title": title, "content": content, "ts": None}

def _pick_first(soup: BeautifulSoup, selectors) -> str:
    for sel in selectors:
        node = soup.select_one(sel)
        if node and node.get_text(strip=True):
            return node.get_text(strip=True)
    return "(未识别标题)"

def _extract_content(soup: BeautifulSoup) -> str:
    for sel in WECHAT_CONTENT_SELECTORS:
        ctn = soup.select_one(sel)
        if ctn:
            parts = []
            for tag in ctn.descendants:
                if not isinstance(tag, Tag):
                    continue
                if tag.name == "img":
                    src = tag.get("data-src") or tag.get("src")
                    parts.append(f"[图片: {src}]")
                elif tag.name in ("p", "li", "blockquote", "section"):
                    text = tag.get_text(" ", strip=True)
                    if text:
                        parts.append(text)
            return "\n".join(parts)
    return "(未识别正文)"

def _parse_timestamp(html: str) -> Optional[int]:
    m = re.search(r"(?:publish_time|ct)=([0-9]{10})", html)
    if m:
        return int(m.group(1))
    m2 = re.search(r'publish_time\s*[:=]\s*"([^\"]+)"', html)
    if m2:
        try:
            struct = time.strptime(m2.group(1), "%Y-%m-%d %H:%M:%S")
            return int(time.mktime(struct))
        except Exception:
            pass
    return None


def fetch_latest_news() -> list[str]:
    """
    抓取三花每日新闻页面，提取当天的文章链接。
    页面: https://sanhua.himrr.com/daily-news
    返回文章链接列表（只返回 href）
    """
    daily_url = "https://sanhua.himrr.com/daily-news"
    try:
        resp = requests.get(daily_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"[ERROR] 获取 daily-news 页面失败: {e}")
        return []

    soup = BeautifulSoup(resp.text, "lxml")

    # 解析所有文章链接，假设都放在 <a href="/news/..."></a>
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not href:
            continue
        # 只保留 /news/ 类型链接
        if href.startswith("/news/"):
            full_url = "https://sanhua.himrr.com" + href
            if full_url not in links:
                links.append(full_url)

    print(f"[INFO] 抓取到 {len(links)} 条今日新闻链接")
    return links
