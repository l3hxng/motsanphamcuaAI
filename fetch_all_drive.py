import json
import os
import requests
from playwright.sync_api import sync_playwright

with open('d:/tool/2010/files_info.json', 'r', encoding='utf-8') as f:
    files = json.load(f)

out_dir = 'd:/tool/2010/images/drive'
os.makedirs(out_dir, exist_ok=True)

# Use Playwright page.request or requests with browser cookies to download high-res images
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://drive.google.com/drive/folders/166-dg2lNX8uUtMYuyEexHsiqS-OdYo8w')
    page.wait_for_timeout(2000)
    
    for fid, fname in files.items():
        if fname.lower().endswith('.heic'):
            continue  # Skip HEIC if not directly web-compatible
            
        clean_name = fname.replace(' ', '_')
        save_path = os.path.join(out_dir, clean_name)
        
        # Method 1: thumbnail API at high resolution (sz=w1000)
        thumb_url = f"https://drive.google.com/thumbnail?id={fid}&sz=w1000"
        try:
            resp = page.request.get(thumb_url)
            if resp.status == 200 and len(resp.body()) > 2000:
                with open(save_path, 'wb') as img_f:
                    img_f.write(resp.body())
                print(f"Downloaded (thumbnail): {clean_name} ({len(resp.body())} bytes)")
                continue
        except Exception as e:
            print(f"Thumb failed for {clean_name}: {e}")
            
        # Method 2: direct export download
        try:
            uc_url = f"https://drive.google.com/uc?export=download&id={fid}"
            resp2 = page.request.get(uc_url)
            if resp2.status == 200 and len(resp2.body()) > 2000:
                with open(save_path, 'wb') as img_f:
                    img_f.write(resp2.body())
                print(f"Downloaded (uc): {clean_name} ({len(resp2.body())} bytes)")
        except Exception as e:
            print(f"UC failed for {clean_name}: {e}")
            
    browser.close()
print("All downloads finished!")
