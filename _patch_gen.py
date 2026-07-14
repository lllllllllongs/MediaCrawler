import os

# Read original main.py to create patched version
base = r'D:\codex\MediaCrawler\MediaCrawler'
with open(os.path.join(base, 'main.py'), 'r', encoding='utf-8') as f:
    content = f.read()

imports_old = 'from media_platform.zhihu import ZhihuCrawler'
imports_new = imports_old + '\nfrom media_platform.cctv_news import CctvNewsCrawler\nfrom media_platform.cctv_people import CctvPeopleCrawler'

dict_old = '"zhihu": ZhihuCrawler,'
dict_new = dict_old + '\n        "cctv_news": CctvNewsCrawler,\n        "cctv_people": CctvPeopleCrawler,'

content = content.replace(imports_old, imports_new)
content = content.replace(dict_old, dict_new)

with open(os.path.join(base, 'main_patched.py'), 'w', encoding='utf-8') as f:
    f.write(content)
print('main_patched.py created')
