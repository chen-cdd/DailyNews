def render_markdown(records: list) -> str:
    # 板块分类标签
    labels = ['新闻', '技术', '案例']
    
    # 将文章循环分配到板块
    sections = {label: [] for label in labels}
    for idx, art in enumerate(records):
        sections[labels[idx % len(labels)]].append(art)

    md_lines = []
    
    # 顶部主标题
    md_lines.append('# 每日AI精选资讯')
    md_lines.append('')

    # 输出各板块内容
    for label in labels:
        articles = sections[label]
        if not articles:
            continue
        md_lines.append(f'## {label}')
        md_lines.append('')
        for art in articles:
            md_lines.append(f"### {art['title']}")
            md_lines.append('')
            if label == '技术':
                tech = art.get('tech', '（未提供技术信息）')
                case = art.get('case', '（未提供案例信息）')
                md_lines.append(f"**技术：** {tech}")
                md_lines.append('')
                md_lines.append(f"**案例：** {case}")
                md_lines.append('')
                md_lines.append(art.get('commentary', art.get('summary', '')))
            elif label == '案例':
                md_lines.append(art.get('commentary', art.get('summary', '')))
            else:
                md_lines.append(art.get('commentary', art.get('summary', '')))
            md_lines.append('')

    return '\n'.join(md_lines)
