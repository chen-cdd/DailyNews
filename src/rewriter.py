# rewriter.py
from openai import OpenAI
import math

def split_text(text: str, max_chars: int = 3000) -> list[str]:
    """简单按字符长度拆分文本，不直接按 token，但能避免超长。"""
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]


def rewrite_article(article: dict, client: OpenAI) -> str:
    """
    对文章 content 生成简短摘要。如果内容过长，会拆块分别摘要，再合并。
    返回最终合并的摘要文本。
    """
    content = article.get("content", "")
    # 拆块并摘要
    chunks = split_text(content, max_chars=3000)
    summaries = []
    for idx, chunk in enumerate(chunks, 1):
        prompt = (
            f"以下是第 {idx}/{len(chunks)} 段内容，请生成约80字的中文摘要：\n\n" + chunk
        )
        resp = client.chat.completions.create(
            model='gpt-4o',
            messages=[{'role':'user','content':prompt}],
            temperature=0.7,
        )
        summaries.append(resp.choices[0].message.content.strip())
    # 如果有多段摘要，合并并进一步精简
    if len(summaries) > 1:
        combined = '\n'.join(summaries)
        final_prompt = (
            "以下是多段本文摘要，请将它们整合为一段流畅的80字左右中文摘要：\n\n" + combined
        )
        resp2 = client.chat.completions.create(
            model='gpt-4o',
            messages=[{'role':'user','content':final_prompt}],
            temperature=0.7,
        )
        return resp2.choices[0].message.content.strip()
    else:
        return summaries[0] if summaries else ""


def expand_summary(summary: str, client: OpenAI, extra: str = "") -> str:
    """
    基于 summary（摘要）及可选 extra（外部资料或观点），生成约200~300字的连贯扩写。
    """
    prompt = (
        "下面是一段文章摘要：\n" + summary + "\n\n"
        "参考信息（可选）：\n" + extra + "\n\n"
        "请基于摘要和参考，输出一段200~300字的评论或分析："
    )
    resp = client.chat.completions.create(
        model='gpt-4-32k',
        messages=[{'role':'user','content':prompt}],
        temperature=0.8,
    )
    return resp.choices[0].message.content.strip()

