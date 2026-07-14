import os, json

base = r'D:\codex\MediaCrawler\MediaCrawler'

# Read data.py
with open(os.path.join(base, 'api', 'routers', 'data.py'), 'r', encoding='utf-8') as f:
    data_content = f.read()

# Add CCTV data endpoints before the last line
cctv_endpoint = '''

# ---- CCTV Data Endpoints ----

def _load_jsonl_data(platform_name: str):
    data_dir = Path(__file__).parent.parent.parent / "data" / platform_name
    rows = []
    if data_dir.exists():
        for root, dirs, files in os.walk(str(data_dir)):
            for file in files:
                if file.endswith('.jsonl'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            for line in f:
                                line = line.strip()
                                if line:
                                    try:
                                        rows.append(json.loads(line))
                                    except json.JSONDecodeError:
                                        pass
                    except Exception:
                        pass
                elif file.endswith('.json'):
                    filepath = os.path.join(root, file)
                    try:
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

# Add to patches
patch_file = os.path.join(base, '_apply_patches.json')
with open(patch_file, 'r', encoding='utf-8') as f:
    patches = json.load(f)

patches[os.path.join(base, 'api', 'routers', 'data.py')] = data_content

with open(patch_file, 'w', encoding='utf-8') as f:
    json.dump(patches, f, ensure_ascii=False)

print(f"Added data.py to patches. Total: {len(patches)} files")
