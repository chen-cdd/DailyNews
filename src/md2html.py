# md2html.py

import markdown as mdlib

# 自定义 CSS 样式
CUSTOM_CSS = """
<style>
  /* 标题样式 */
  h1 { color: #2c3e50; font-size: 2.2em; margin-bottom: 0.5em; }
  h2 { color: #34495e; border-bottom: 2px solid #ecf0f1; padding-bottom: 0.3em; margin-top: 1.2em; }
  h3 { color: #2c3e50; margin-top: 1em; }
  /* 引用样式 */
  blockquote {
    border-left: 4px solid #95a5a6;
    color: #7f8c8d;
    padding-left: 1em;
    margin: 1em 0;
    font-style: italic;
    background: #f9f9f9;
  }
  /* 段落与列表 */
  p, ul, ol {
    line-height: 1.6;
    margin: 0.8em 0;
  }
  /* 技术板块高亮 */
  .tech {
    background: #ecf0f1;
    padding: 0.5em;
    border-radius: 4px;
    margin-bottom: 0.8em;
  }
  /* 链接样式 */
  a {
    color: #1e90ff;
    text-decoration: none;
  }
  a:hover {
    text-decoration: underline;
  }
</style>
"""

def md_to_html(md_text: str) -> str:
    """
    将 Markdown 转成 HTML，并注入自定义 CSS（适配公众号草稿箱）。
    """
    html_body = mdlib.markdown(
        md_text,
        extensions=['tables', 'fenced_code', 'attr_list']
    )
    return CUSTOM_CSS + html_body
