import urllib.request
import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://drive.google.com/drive/folders/166-dg2lNX8uUtMYuyEexHsiqS-OdYo8w')
    page.wait_for_timeout(4000)
    
    elements = page.query_selector_all("[data-id]")
    file_map = {}
    for el in elements:
        did = el.get_attribute("data-id")
        try:
            txt = el.inner_text().strip().split("\n")[0]
            if did and len(did) > 15 and did != "166-dg2lNX8uUtMYuyEexHsiqS-OdYo8w":
                file_map[did] = txt
        except Exception:
            pass
            
    with open('d:/tool/2010/files_info.json', 'w', encoding='utf-8') as f:
        json.dump(file_map, f, ensure_ascii=False, indent=2)
        
    print(f"Extracted {len(file_map)} files into files_info.json")
    browser.close()
