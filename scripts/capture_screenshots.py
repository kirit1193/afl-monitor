#!/usr/bin/env python3
"""
Capture screenshots of AFL Overseer TUI and WebUI for documentation.

This script should be run locally on a machine with display capabilities.
Requires: playwright, pillow

Install dependencies:
    pip install playwright pillow
    python -m playwright install chromium

Usage:
    python scripts/capture_screenshots.py
"""

import asyncio
import subprocess
import time
import sys
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Error: playwright not installed")
    print("Install with: pip install playwright && python -m playwright install chromium")
    sys.exit(1)


async def capture_webui_screenshots():
    """Capture screenshots of all WebUI tabs."""

    # Ensure assets directory exists
    Path('assets').mkdir(exist_ok=True)

    # Start web server in background
    print("Starting web server on port 8899...")
    proc = subprocess.Popen(
        ['python3', '-m', 'src.cli', '-w', '--headless', '-p', '8899', 'testing/mock_sync'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    time.sleep(4)

    try:
        # Verify server is running
        import requests
        for i in range(10):
            try:
                resp = requests.get('http://localhost:8899/api/stats', timeout=1)
                if resp.status_code == 200:
                    print("✓ Server is ready!")
                    break
            except:
                if i == 9:
                    raise Exception("Server failed to start")
                time.sleep(1)

        async with async_playwright() as p:
            # Launch browser
            print("Launching browser...")
            browser = await p.chromium.launch(headless=False)  # Use headful for better rendering
            page = await browser.new_page(viewport={'width': 1600, 'height': 1000})

            # Navigate to dashboard
            print("Loading dashboard...")
            await page.goto('http://localhost:8899')

            # Wait for data to load
            await page.wait_for_timeout(3000)

            # Capture Overview tab
            print("📸 Capturing Overview tab...")
            await page.screenshot(path='assets/webui-overview.png', full_page=False)

            # Switch to Fuzzers tab
            print("📸 Capturing Fuzzers tab...")
            await page.click('text=Fuzzers')
            await page.wait_for_timeout(500)
            await page.screenshot(path='assets/webui-fuzzers.png', full_page=False)

            # Switch to Graphs tab
            print("📸 Capturing Graphs tab...")
            await page.click('text=Graphs')
            await page.wait_for_timeout(2000)  # Let graphs render
            await page.screenshot(path='assets/webui-graphs.png', full_page=False)

            await browser.close()

        print("\n✓ WebUI screenshots captured successfully!")
        print("  - assets/webui-overview.png")
        print("  - assets/webui-fuzzers.png")
        print("  - assets/webui-graphs.png")

    finally:
        proc.terminate()
        proc.wait()


def capture_tui_screenshot():
    """Capture TUI screenshot using terminal recording."""
    print("\n📸 Capturing TUI...")
    print("Note: For TUI recording, consider using:")
    print("  - asciinema: asciinema rec assets/tui-demo.cast")
    print("  - termtosvg: termtosvg assets/tui-demo.svg")
    print("  - Manual screenshot of: afl-overseer testing/mock_sync")


if __name__ == '__main__':
    print("AFL Overseer Screenshot Capture Tool")
    print("=" * 50)
    print()

    # Capture WebUI
    try:
        asyncio.run(capture_webui_screenshots())
    except Exception as e:
        print(f"Error capturing WebUI: {e}")
        print("Make sure you're running this on a machine with display support")

    # TUI instructions
    capture_tui_screenshot()

    print("\n✓ Done! Screenshots saved to assets/")
