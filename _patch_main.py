import os

base = r'D:\codex\MediaCrawler\MediaCrawler'

# Read current main.py
with open(os.path.join(base, 'main.py'), 'r', encoding='utf-8') as f:
    content = f.read()

# Check if cctv_news import already exists
if 'cctv_news' not in content:
    # Add imports
    old_imports = 'from media_platform.zhihu import ZhihuCrawler'
    new_imports = old_imports + '\nfrom media_platform.cctv_news import CctvNewsCrawler\nfrom media_platform.cctv_people import CctvPeopleCrawler'
    content = content.replace(old_imports, new_imports)

    # Add to CRAWLERS dict
    old_dict = '"zhihu": ZhihuCrawler,'
    new_dict = old_dict + '\n        "cctv_news": CctvNewsCrawler,\n        "cctv_people": CctvPeopleCrawler,'
    content = content.replace(old_dict, new_dict)

    with open(os.path.join(base, 'main.py'), 'w', encoding='utf-8') as f:
        f.write(content)
    print('main.py updated')
else:
    print('main.py already has cctv_news')
