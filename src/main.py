from pathlib import Path
from typing import List
import argparse
import os
import time
import schedule

from utils import load_settings, load_seen, save_seen, logger, OUTPUT_DIR, ROOT_DIR
from fetcher import get_article, fetch_latest_news
from openai import OpenAI
from rewriter import rewrite_article, expand_summary
from renderer import render_markdown
from md2html import md_to_html
from publisher import publish

CONFIG_URLS_PATH = ROOT_DIR / 'config' / 'urls.txt'

def load_urls_from_file() -> List[str]:
    if not CONFIG_URLS_PATH.exists():
        logger.error(f"未找到 URL 列表文件: {CONFIG_URLS_PATH}")
        return []
    with open(CONFIG_URLS_PATH, 'r', encoding='utf-8') as f:
        return [ln.strip() for ln in f if ln.strip() and not ln.startswith('#')]

def process_articles(urls: List[str], client: OpenAI):
    cfg = load_settings()
    seen = load_seen()
    records = []

    for url in urls:
        if url in seen:
            logger.info(f"跳过已处理 URL: {url}")
            continue

        logger.info(f"抓取文章: {url}")
        try:
            art = get_article(url)
        except Exception:
            logger.exception(f"抓取失败: {url}")
            continue

        logger.info(f"摘要文章: {url}")
        try:
            summary = rewrite_article(art, client)
        except Exception:
            logger.exception(f"摘要失败: {url}")
            continue
        art['summary'] = summary

        logger.info(f"扩写文章: {url}")
        extra_info = cfg.get('extra_info', '我认为该技术的关键在于...')
        try:
            commentary = expand_summary(summary, client, extra=extra_info)
        except Exception:
            commentary = summary
        art['commentary'] = commentary

        records.append(art)
        seen.add(url)
        save_seen(seen)

    if not records:
        logger.info('没有成功处理的文章，结束。')
        return

    md = render_markdown(records)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    out_md = OUTPUT_DIR / 'digest_latest.md'
    out_md.write_text(md, encoding='utf-8')
    logger.info(f"Markdown 已写入 {out_md}")

    html = md_to_html(md)
    out_html = OUTPUT_DIR / 'digest_latest.html'
    out_html.write_text(html, encoding='utf-8')
    logger.info(f"HTML 已写入 {out_html}")

    if cfg.get('wechat_app_id') and cfg.get('wechat_app_secret'):
        status, media_id = publish(
            markdown=md,
            html=html,
            app_id=cfg['wechat_app_id'],
            app_secret=cfg['wechat_app_secret'],
            publish_mode="draft_only",
            thumb_path=cfg.get('thumb_path', 'config/thumb.jpg'),
        )
        logger.info(f"发布状态: {status}, media_id={media_id}")
    else:
        logger.warning('未配置公众号凭证：跳过发布。')

def run(mode='auto'):
    cfg = load_settings()
    api_key = cfg.get('openai_api_key')
    if not api_key:
        raise RuntimeError('OpenAI API Key 未配置 (openai_api_key)')

    os.environ['OPENAI_API_KEY'] = api_key
    client = OpenAI()
    
    if mode == 'manual':
        urls = load_urls_from_file()
        if not urls:
            logger.warning('urls.txt 为空，退出。')
            return
    else:
        logger.info("自动模式下尝试获取新闻源链接...")
        urls = fetch_latest_news()
        if not urls:
            logger.warning("未获取到任何新闻链接，跳过处理。")
            return

    process_articles(urls, client)

def schedule_job():
    logger.info("定时任务触发中...")
    run(mode='auto')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="忽略已处理记录，强制重跑所有 URL")
    parser.add_argument("--manual", action="store_true", help="使用 urls.txt 作为输入（旧逻辑）")
    parser.add_argument("--once", action="store_true", help="只执行一次，不启用定时器")
    args = parser.parse_args()

    if args.manual or args.once:
        run(mode='manual' if args.manual else 'auto')
    else:
        # 每天早上 8:00 定时执行
        schedule.every().day.at("8:00").do(schedule_job)
        logger.info("已启动定时调度，每天 8:00 自动爬取发布")
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == '__main__':
    main()
