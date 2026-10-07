# -*- coding: utf-8 -*-
"""
Script chụp ảnh màn hình giao diện thực tế của Dashboard sau khi đã sửa lỗi dữ liệu.
"""

import os
import sys
import time
import threading
from playwright.sync_api import sync_playwright

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from dashboard.app import app

def run_flask(port):
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)

def main():
    port = 8070
    server_thread = threading.Thread(target=run_flask, args=(port,), daemon=True)
    server_thread.start()
    print(f"[*] Started Flask server on http://127.0.0.1:{port}")
    time.sleep(2.5)

    os.makedirs(os.path.join(ROOT_DIR, "extracted_images"), exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 920})
        page = context.new_page()

        print("[*] Navigating to Dashboard...")
        page.goto(f"http://127.0.0.1:{port}", wait_until="networkidle")
        time.sleep(3.5) # Chờ API nạp và Chart.js render xong

        # 1. Chụp Tab Tổng quan (Overview)
        p1 = os.path.join(ROOT_DIR, "extracted_images", "ui_overview.png")
        page.screenshot(path=p1, full_page=False)
        print(f"[+] Captured Overview: {p1}")

        # 2. Chụp Tab Phân tích Điện năng (Energy)
        page.click("#btn-tab-energy")
        page.wait_for_selector("#tableFullHomeRanking tr", timeout=5000)
        time.sleep(2.0) # Chờ bar chart và pie chart resize
        p2 = os.path.join(ROOT_DIR, "extracted_images", "ui_energy.png")
        page.screenshot(path=p2, full_page=False)
        print(f"[+] Captured Energy: {p2}")

        # 3. Chụp Tab Giám sát An toàn & Bất thường (Anomaly)
        page.click("#btn-tab-anomaly")
        page.wait_for_selector("#tableFullAnomalies tr", timeout=5000)
        time.sleep(2.0)
        p3 = os.path.join(ROOT_DIR, "extracted_images", "ui_anomaly.png")
        page.screenshot(path=p3, full_page=False)
        print(f"[+] Captured Anomaly: {p3}")

        # 4. Chụp Tab Dữ liệu RDBMS & Quản trị CSDL lớn (7 Triệu bản ghi)
        page.click("#btn-tab-rdbms")
        page.wait_for_selector("#rdbmsGridBody tr", timeout=5000)
        time.sleep(2.0)
        p5 = os.path.join(ROOT_DIR, "extracted_images", "ui_rdbms.png")
        page.screenshot(path=p5, full_page=False)
        print(f"[+] Captured RDBMS: {p5}")

        # 5. Chụp Tab Luồng NoSQL / Hadoop (Pipeline)
        page.click("#btn-tab-pipeline")
        time.sleep(2.0)
        p4 = os.path.join(ROOT_DIR, "extracted_images", "ui_pipeline.png")
        page.screenshot(path=p4, full_page=False)
        print(f"[+] Captured Pipeline: {p4}")

        # 6. Chụp Tab Kinh doanh & Gói cước (Business)
        page.click("#btn-tab-business")
        time.sleep(2.0)
        p6 = os.path.join(ROOT_DIR, "extracted_images", "ui_business.png")
        page.screenshot(path=p6, full_page=False)
        print(f"[+] Captured Business: {p6}")

        browser.close()
        print("[*] All screenshots recaptured with full live data successfully!")

if __name__ == "__main__":
    main()
