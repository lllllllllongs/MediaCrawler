import os, json

base = r'D:\codex\MediaCrawler\MediaCrawler'

with open(os.path.join(base, 'cmd_arg', 'arg.py'), 'r', encoding='utf-8') as f:
    arg_content = f.read()
with open(os.path.join(base, 'api', 'schemas', 'crawler.py'), 'r', encoding='utf-8') as f:
    schema_content = f.read()
with open(os.path.join(base, 'api', 'main.py'), 'r', encoding='utf-8') as f:
    api_content = f.read()
with open(os.path.join(base, 'config', '__init__.py'), 'r', encoding='utf-8') as f:
    config_init = f.read()
with open(os.path.join(base, 'api', 'webui', 'main.html'), 'r', encoding='utf-8') as f:
    html_content = f.read()
with open(os.path.join(base, 'main.py'), 'r', encoding='utf-8') as f:
    main_content = f.read()
with open(os.path.join(base, 'api', 'routers', 'data.py'), 'r', encoding='utf-8') as f:
    data_content = f.read()
with open(os.path.join(base, 'cctv_news-dashboard.html'), 'r', encoding='utf-8') as f:
    news_dash = f.read()
with open(os.path.join(base, 'cctv_people-dashboard.html'), 'r', encoding='utf-8') as f:
    people_dash = f.read()

# Config files
news_cfg = '# -*- coding: utf-8 -*-\n# CCTV News config\nCCTV_NEWS_LIST_URL = "https://news.cctv.com/society/"\nCCTV_NEWS_MAX_ARTICLES = 40\nCCTV_NEWS_CRAWL_INTERVAL = 0.5\n'
people_cfg = '# -*- coding: utf-8 -*-\n# CCTV People config\nCCTV_PEOPLE_LIST_URL = "https://people.cctv.com/"\nCCTV_PEOPLE_MAX_ARTICLES = 40\nCCTV_PEOPLE_CRAWL_INTERVAL = 0.5\n'

# 1. cmd_arg/arg.py
arg_content = arg_content.replace(
    'ZHIHU = "zhihu"',
    'ZHIHU = "zhihu"\n    CCTV_NEWS = "cctv_news"\n    CCTV_PEOPLE = "cctv_people"'
)

# 2. api/schemas/crawler.py
schema_content = schema_content.replace(
    'ZHIHU = "zhihu"',
    'ZHIHU = "zhihu"\n    CCTV_NEWS = "cctv_news"\n    CCTV_PEOPLE = "cctv_people"'
)

# 3. api/main.py
old_platforms = '{"value": "zhihu", "label": "Zhihu", "icon": "help-circle"},'
new_platforms = old_platforms + '\n            {"value": "cctv_news", "label": "\u793e\u4f1a\u65b0\u95fb_\u592e\u89c6\u7f51", "icon": "newspaper"},\n            {"value": "cctv_people", "label": "\u4eba\u7269\u9891\u9053_\u592e\u89c6\u7f51", "icon": "users"},'
api_content = api_content.replace(old_platforms, new_platforms)

# 4. config/__init__.py
config_init = config_init.replace(
    'from .base_config import *',
    'from .base_config import *\nfrom .cctv_news_config import *\nfrom .cctv_people_config import *'
)

# 5. api/webui/main.html
old_links = 'zhihu: "/static/zhihu-dashboard.html"'
new_links = old_links + ',\n      cctv_news: "/static/cctv_news-dashboard.html",\n      cctv_people: "/static/cctv_people-dashboard.html"'
html_content = html_content.replace(old_links, new_links)

old_nav = '<a href="/static/zhihu-dashboard.html">\u77e5\u4e4e</a>'
new_nav = old_nav + '\n      <a href="/static/cctv_news-dashboard.html">\u592e\u89c6\u793e\u4f1a\u65b0\u95fb</a>\n      <a href="/static/cctv_people-dashboard.html">\u592e\u89c6\u4eba\u7269</a>'
html_content = html_content.replace(old_nav, new_nav)

# 6. main.py
main_content = main_content.replace(
    'from media_platform.zhihu import ZhihuCrawler',
    'from media_platform.zhihu import ZhihuCrawler\nfrom media_platform.cctv_news import CctvNewsCrawler\nfrom media_platform.cctv_people import CctvPeopleCrawler'
)
main_content = main_content.replace(
    '"zhihu": ZhihuCrawler,',
    '"zhihu": ZhihuCrawler,\n        "cctv_news": CctvNewsCrawler,\n        "cctv_people": CctvPeopleCrawler,'
)

# 7. api/routers/data.py - add CCTV endpoints
cctv_endpoint = '''

# ---- CCTV Data Endpoints ----

def _load_jsonl_data(platform_name: str):
    """Load data from JSONL/JSON files for a platform"""
    data_dir = Path(__file__).parent.parent.parent / "data" / platform_name
    rows = []
    if data_dir.exists():
        for root, dirs, files in os.walk(str(data_dir)):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    if file.endswith('.jsonl'):
                        with open(filepath, 'r', encoding='utf-8') as f:
                            for line in f:
                                line = line.strip()
                                if line:
                                    try:
                                        rows.append(json.loads(line))
                                    except json.JSONDecodeError:
                                        pass
                    elif file.endswith('.json'):
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                rows.extend(data)
                            elif isinstance(data, dict):
                                rows.append(data)
                except Exception:
                    pass
    return rows


@router.get("/cctv_news")
async def get_cctv_news_data():
    rows = _load_jsonl_data("cctv_news")
    return {"platform": "cctv_news", "rows": rows}


@router.get("/cctv_people")
async def get_cctv_people_data():
    rows = _load_jsonl_data("cctv_people")
    return {"platform": "cctv_people", "rows": rows}
'''

data_content = data_content + cctv_endpoint

patches = {
    os.path.join(base, 'cmd_arg', 'arg.py'): arg_content,
    os.path.join(base, 'api', 'schemas', 'crawler.py'): schema_content,
    os.path.join(base, 'api', 'main.py'): api_content,
    os.path.join(base, 'config', '__init__.py'): config_init,
    os.path.join(base, 'api', 'webui', 'main.html'): html_content,
    os.path.join(base, 'main.py'): main_content,
    os.path.join(base, 'api', 'routers', 'data.py'): data_content,
    os.path.join(base, 'config', 'cctv_news_config.py'): news_cfg,
    os.path.join(base, 'config', 'cctv_people_config.py'): people_cfg,
    os.path.join(base, 'api', 'webui', 'cctv_news-dashboard.html'): news_dash,
    os.path.join(base, 'api', 'webui', 'cctv_people-dashboard.html'): people_dash,
}

with open(os.path.join(base, '_apply_patches.json'), 'w', encoding='utf-8') as f:
    json.dump(patches, f, ensure_ascii=False)

print(f"Patches regenerated: {len(patches)} files")
for p in sorted(patches.keys()):
    print(f"  {os.path.relpath(p, base)}")
