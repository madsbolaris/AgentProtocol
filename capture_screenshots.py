#!/usr/bin/env python3
"""
Capture screenshots of both sidebars for comparison.
"""
import asyncio
from playwright.async_api import async_playwright

async def capture_screenshots():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1200})

        # Capture current implementation
        print("Capturing current implementation...")
        page1 = await context.new_page()
        try:
            await page1.goto('http://127.0.0.1:8001/products/client-sdk/', timeout=15000)
            await page1.wait_for_timeout(2000)

            # Take full page screenshot
            await page1.screenshot(
                path='/Users/mabolan/AgentProtocol/screenshot_current_full.png',
                full_page=True
            )

            # Try to capture just the sidebar area
            await page1.screenshot(
                path='/Users/mabolan/AgentProtocol/screenshot_current_sidebar.png',
                clip={'x': 0, 'y': 100, 'width': 350, 'height': 800}
            )

            print("✓ Current implementation captured")
        except Exception as e:
            print(f"✗ Error capturing current: {e}")
        finally:
            await page1.close()

        # Capture reference implementation
        print("\nCapturing reference implementation...")
        page2 = await context.new_page()
        try:
            file_path = 'file:///Users/mabolan/AgentProtocol/.workspace/hashicorp-complete/complete-page.html'
            await page2.goto(file_path, timeout=15000)
            await page2.wait_for_timeout(2000)

            # Take full page screenshot
            await page2.screenshot(
                path='/Users/mabolan/AgentProtocol/screenshot_reference_full.png',
                full_page=True
            )

            # Try to capture just the sidebar area
            await page2.screenshot(
                path='/Users/mabolan/AgentProtocol/screenshot_reference_sidebar.png',
                clip={'x': 0, 'y': 100, 'width': 350, 'height': 800}
            )

            print("✓ Reference implementation captured")
        except Exception as e:
            print(f"✗ Error capturing reference: {e}")
        finally:
            await page2.close()

        await browser.close()

        print("\n=== Screenshots saved: ===")
        print("  - screenshot_current_full.png")
        print("  - screenshot_current_sidebar.png")
        print("  - screenshot_reference_full.png")
        print("  - screenshot_reference_sidebar.png")

if __name__ == '__main__':
    asyncio.run(capture_screenshots())
