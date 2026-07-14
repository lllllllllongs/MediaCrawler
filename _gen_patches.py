import os
base = r'D:\codex\MediaCrawler\MediaCrawler'

# Read all original files
with open(os.path.join(base, 'cmd_arg', 'arg.py'), 'r', encoding='utf-8') as f:
    arg_content = f.read()
with open(os.path.join(base, 'api', 'schemas', 'crawler.py'), 'r', encoding='utf-8') as f:
    schema_content = f.read()
with open(os.path.join(base, 'api', 'main.py'), 'r', encoding='utf-8') as f:
    api_content = f.read()
with open(os.path.join(base, 'config', '__init__.py'), 'r', encoding='utf-8') as f:
    config_content = f.read()
with open(os.path.join(base, 'api', 'webui', 'main.html'), 'r', encoding='utf-8') as f:
    html_content = f.read()
with open(os.path.join(base, 'main.py'), 'r', encoding='utf-8') as f:
    main_content = f.read()

# 1. Patch cmd_arg/arg.py - add CCTV_NEWS and CCTV_PEOPLE to PlatformEnum
arg_content = arg_content.replace(
    'ZHIHU = "zhihu"',
    'ZHIHU = "zhihu"\n    CCTV_NEWS = "cctv_news"\n    CCTV_PEOPLE = "cctv_people"'
)

# 2. Patch api/schemas/crawler.py - add to PlatformEnum
schema_content = schema_content.replace(
    'ZHIHU = "zhihu"',
    'ZHIHU = "zhihu"\n    CCTV_NEWS = "cctv_news"\n    CCTV_PEOPLE = "cctv_people"'
)

# 3. Patch api/main.py - add platforms and skip login for CCTV
old_platforms = '{"value": "zhihu", "label": "Zhihu", "icon": "help-circle"},'
new_platforms = old_platforms + '\n            {"value": "cctv_news", "label": "社会新闻_央视网", "icon": "newspaper"},\n            {"value": "cctv_people", "label": "人物频道_央视网", "icon": "users"},'
api_content = api_content.replace(old_platforms, new_platforms)

# 4. Patch config/__init__.py - import new configs
old_config_import = 'from .base_config import *'
new_config_import = old_config_import + '\nfrom .cctv_news_config import *\nfrom .cctv_people_config import *'
config_content = config_content.replace(old_config_import, new_config_import)

# 5. Patch api/webui/main.html - add dashboard links
old_links = 'zhihu: "/static/zhihu-dashboard.html"'
new_links = old_links + ',\n      cctv_news: "/static/cctv_news-dashboard.html",\n      cctv_people: "/static/cctv_people-dashboard.html"'
html_content = html_content.replace(old_links, new_links)

old_nav = '<a href="/static/zhihu-dashboard.html">知乎</a>'
new_nav = old_nav + '\n      <a href="/static/cctv_news-dashboard.html">央视社会新闻</a>\n      <a href="/static/cctv_people-dashboard.html">央视人物</a>'
html_content = html_content.replace(old_nav, new_nav)

# 6. Patch main.py
main_content = main_content.replace(
    'from media_platform.zhihu import ZhihuCrawler',
    'from media_platform.zhihu import ZhihuCrawler\nfrom media_platform.cctv_news import CctvNewsCrawler\nfrom media_platform.cctv_people import CctvPeopleCrawler'
)
main_content = main_content.replace(
    '"zhihu": ZhihuCrawler,',
    '"zhihu": ZhihuCrawler,\n        "cctv_news": CctvNewsCrawler,\n        "cctv_people": CctvPeopleCrawler,'
)

# Write all patched files
patches = {
    os.path.join(base, 'cmd_arg', 'arg.py'): arg_content,
    os.path.join(base, 'api', 'schemas', 'crawler.py'): schema_content,
    os.path.join(base, 'api', 'main.py'): api_content,
    os.path.join(base, 'config', '__init__.py'): config_content,
    os.path.join(base, 'api', 'webui', 'main.html'): html_content,
    os.path.join(base, 'main.py'): main_content,
}

# Save patches as JSON for later application
import json
patch_data = {}
for path, content in patches.items():
    patch_data[path] = content

with open(os.path.join(base, '_apply_patches.json'), 'w', encoding='utf-8') as f:
    json.dump(patch_data, f, ensure_ascii=False)

print("Patch data saved to _apply_patches.json")
