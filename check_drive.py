
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('https://drive.google.com/drive/folders/166-dg2lNX8uUtMYuyEexHsiqS-OdYo8w?usp=drive_link')
    page.wait_for_timeout(5000)
    print('Title:', page.title())
    print('URL:', page.url)
    page.screenshot(path='d:/tool/2010/drive_check.png')
    text = page.inner_text('body')
    print('Text preview:', text[:300].replace('\n', ' '))
    browser.close()
