from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch()
    # Accept downloads
    page = browser.new_page(accept_downloads=True)
    page.goto('https://drive.google.com/drive/folders/166-dg2lNX8uUtMYuyEexHsiqS-OdYo8w')
    page.wait_for_timeout(3000)
    
    dl_btn = page.query_selector("button:has-text('Tải xuống tất cả'), [aria-label*='Tải xuống'], div:has-text('Tải xuống tất cả')")
    print('Found dl_btn:', dl_btn is not None)
    
    if dl_btn:
        print('Clicking dl_btn...')
        # Note: Google Drive compresses first, so download may take 5-15 seconds to start
        dl_btn.click()
        
        # Wait for either download or progress toast
        print('Waiting for download event (up to 45s)...')
        try:
            with page.expect_download(timeout=45000) as download_info:
                # Sometimes a confirmation or toast appears
                page.wait_for_timeout(2000)
            download = download_info.value
            zip_path = 'd:/tool/2010/drive_files.zip'
            download.save_as(zip_path)
            print('SUCCESS: Saved zip to:', zip_path)
        except Exception as e:
            print('Download wait failed:', e)
            page.screenshot(path='d:/tool/2010/dl_fail.png')
            
    browser.close()
