#!/usr/bin/env python3
"""
Playwright script to verify the interactive frontend demo of the Sphere Console
and capture a screenshot for visual inspection.
"""

import os
import sys
from playwright.sync_api import sync_playwright


def main():
    html_path = os.path.abspath("index.html")
    screenshot_path = os.path.abspath("demo_screenshot.png")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        page = browser.new_page(viewport={"width": 1200, "height": 900})
        page.goto(f"file://{html_path}")

        # Wait for device elements to render
        page.wait_for_selector("#sphereChassis")
        page.wait_for_selector("#beadsCanvas")
        page.wait_for_selector("#stylusCanvas")

        # Simulate actions: twist dial, rattle beads, pull ripcord, speak phonics, undock stylus and trace
        page.click("button:has-text('Auto-Twist to Target')")
        page.wait_for_timeout(300)

        page.click("#shakeBtn")
        page.wait_for_timeout(400)

        page.click("button:has-text('Quick Launch')")
        page.wait_for_timeout(500)

        page.click("button:has-text('Speak Phonics Sound')")
        page.wait_for_timeout(500)

        page.click("button:has-text('Auto-Trace Letter')")
        page.wait_for_timeout(500)

        # Capture high-resolution screenshot
        page.screenshot(path=screenshot_path, full_page=True)
        browser.close()

    print(f"Screenshot successfully captured at {screenshot_path}")


if __name__ == "__main__":
    main()
