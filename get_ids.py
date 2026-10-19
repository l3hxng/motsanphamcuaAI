from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://drive.google.com/drive/folders/166-dg2lNX8uUtMYuyEexHsiqS-OdYo8w')
    page.wait_for_timeout(4000)
    
    # Find all elements with data-id or role="row"
    elements = page.query_selector_all("[data-id]")
    print(f"Total elements with data-id: {len(elements)}")
    
    file_map = {}
    for el in elements:
        did = el.get_attribute("data-id")
        try:
            txt = el.inner_text().strip().split("\n")[0]
            if did and len(did) > 15 and did != "166-dg2lNX8uUtMYuyEexHsiqS-OdYo8w":
                file_map[did] = txt
        except Exception:
            pass
            
    for fid, fname in file_map.items():
        print(f"FILE: {fid} -> {fname}")
        
    browser.close()
