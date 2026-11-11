#!/usr/bin/env python3
"""
Record video walkthrough of the Sphere Console Alphabet Adventure demo.
Uses Playwright's native record_video_dir to record a video file (.webm).
"""

import os
import shutil
import sys
import time
from playwright.sync_api import sync_playwright


def main():
    html_path = os.path.abspath("index.html")
    temp_video_dir = "/tmp/sphere_video_temp"
    final_video_path = os.path.abspath("demo_video.webm")
    verification_img_path = "/home/jules/verification/video_verification.png"

    os.makedirs(temp_video_dir, exist_ok=True)
    os.makedirs("/home/jules/verification", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = browser.new_context(
            viewport={"width": 1200, "height": 900},
            record_video_dir=temp_video_dir,
            record_video_size={"width": 1200, "height": 900}
        )
        page = context.new_page()
        page.goto(f"file://{html_path}")

        page.wait_for_selector("#sphereChassis")
        page.wait_for_timeout(1000)

        # 1. MicroSD Cartridge Eject and Re-insert
        page.click("button:has-text('Eject / Insert')")
        page.wait_for_timeout(800)
        page.click("button:has-text('Eject / Insert')")
        page.wait_for_timeout(1000)

        # 2. Twist Mechanic: Rotate outer bezel to 45 degrees
        page.click("button:has-text('Auto-Twist to Target')")
        page.wait_for_timeout(1200)

        # 3. Shake Mechanic: Rattle the sphere and beads
        page.click("#shakeBtn")
        page.wait_for_timeout(1500)

        # 4. Pull Mechanic: Ripcord spring tension & launch
        page.click("button:has-text('Quick Launch')")
        page.wait_for_timeout(1500)

        # 5. Talk Mechanic: Microphone phonics sound
        page.click("button:has-text('Speak Phonics Sound')")
        page.wait_for_timeout(1500)

        # 6. Stylus Mechanic: Un-dock stylus and trace letter A
        page.click("button:has-text('Dock/Undock')")
        page.wait_for_timeout(800)
        page.click("button:has-text('Auto-Trace Letter')")
        page.wait_for_timeout(2000)

        # Capture verification screenshot during video recording
        page.screenshot(path=verification_img_path, full_page=True)

        video_path = page.video.path()
        page.close()
        context.close()
        browser.close()

        # Copy recorded video to root demo_video.webm
        if video_path and os.path.exists(video_path):
            shutil.copy(video_path, final_video_path)
            print(f"Video recorded successfully: {final_video_path} (from {video_path})")
        else:
            print(f"Could not locate recorded video at {video_path}")


if __name__ == "__main__":
    main()
