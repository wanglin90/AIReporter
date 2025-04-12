import asyncio

import pandas as pd
import requests
from bs4 import BeautifulSoup
import plotly.express as px
from datetime import datetime
from googletrans import Translator

keywords = ["AI", "Machine Learning","LLM","NLP","LangChain","Agent","Digital Human","AI Agent","Rag"]

async def translate_to_chinese(text):
    """翻译为中文"""
    translator = Translator()
    translated = await translator.translate(text, src='en', dest='zh-cn')
    return translated.text

def format_stars(stars_str):
    return int(stars_str.replace(',',''))

def fetch_github_trending():
    """GitHub Trending AI项目"""
    #monthly weekly daily
    url = "https://github.com/trending/python?since=monthly"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    repos = []
    for article in soup.select('article'):
        #标题
        title = article.select_one('h2 a').text.strip()
        #url
        url = "https://github.com" + article.select_one('h2 a')['href']
        #描述
        desc = article.select_one('p').text.strip() if article.select_one('p') else ""
        if not any(kw.lower() in desc.lower() for kw in keywords):
            continue
        # Star数量
        # 新版Star数量解析
        stars_tag = article.find('a', href=lambda href: href and 'stargazers' in href)
        stars_str = stars_tag.text.strip() if stars_tag else "0"
        #结果
        repos.append({
            'title': title,
            'url': url,
            'desc': desc,
            'stars': format_stars(stars_str),
            'source': 'GitHub'
        })
    # 按Star数降序排序并取前10
    sorted_repos = sorted(repos, key=lambda x: x['stars'], reverse=True)
    return sorted_repos[:10]


# ================== NLP处理模块 ==================
def classify_content(items):
    """简单分类器"""
    # open_source_keywords = ['github', 'open source', 'library']
    # business_keywords = ['launch', 'enterprise', 'cloud']

    categorized = {'open_source': []}
    for item in items:
        categorized['open_source'].append(item)
    return categorized


# ================== Markdown生成 ==================
async def create_markdown(report_data):
    md_content = f"""
    # AI领域动态日报 ({datetime.now().strftime('%Y-%m-%d')})

    ## 开源项目
    {await format_section(report_data['open_source'])}
    
    """
    with open('ai_report.md', 'w',encoding='utf-8-sig') as f:
        f.write(md_content)


async def format_section(items):
    # return '\n'.join(
    #     f"### {i+1}. {item['title'].replace('\n', '')}\n"
    #     f"- ⭐ Stars: `{item['stars']:,}`\n"
    #     f"- 📝 描述: {await translate_to_chinese(item.get('desc', '暂无描述'))}\n"
    #     f"- 🔗 链接: {item['url']}"
    #     for i, item in enumerate(items)
    # )
    formatted_items = []
    for i, item in enumerate(items):
        title = item['title'].replace('\n', '')
        title = title.replace(' ', '')
        stars = item['stars']
        desc = await translate_to_chinese(item.get('desc', '暂无描述'))  # 使用 await 等待异步翻译
        url = item['url']

        formatted_items.append(
            f"### {i + 1}. {title}\n"
            f"- ⭐ Stars: `{stars:,}`\n"
            f"- 📝 描述: {desc}\n"
            f"- 🔗 链接: {url}"
        )
    return '\n'.join(formatted_items)


# ================== 主流程 ==================
if __name__ == "__main__":
    # 采集数据
    data = []
    # data += fetch_arxiv_ai()
    # print(data)
    data += fetch_github_trending()

    # # 分类处理
    categorized = classify_content(data)

    # 生成MD文件
    asyncio.run(create_markdown(categorized))

    # # 钉钉推送
    # if DING_WEBHOOK:
    #     send_dingding("AI日报已生成")