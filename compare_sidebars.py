#!/usr/bin/env python3
"""
Compare navigation sidebar alignment between two pages.
"""
import asyncio
import json
from playwright.async_api import async_playwright
from pathlib import Path

async def capture_and_analyze():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})

        results = {}

        # Page 1: Current implementation
        print("Analyzing page 1: http://127.0.0.1:8001/products/client-sdk/")
        page1 = await context.new_page()
        try:
            await page1.goto('http://127.0.0.1:8001/products/client-sdk/', wait_until='networkidle', timeout=10000)
            await page1.wait_for_timeout(1000)

            # Take full page screenshot
            await page1.screenshot(path='/Users/mabolan/AgentProtocol/sidebar_current.png', full_page=True)

            # Find navigation sidebar
            nav_selectors = [
                '.md-sidebar--primary',
                '.md-sidebar',
                'nav.md-nav',
                '[data-md-component="sidebar"]',
                '.md-nav--primary'
            ]

            nav_element = None
            for selector in nav_selectors:
                try:
                    nav_element = await page1.query_selector(selector)
                    if nav_element:
                        print(f"Found nav with selector: {selector}")
                        break
                except:
                    continue

            if nav_element:
                # Take screenshot of sidebar only
                await nav_element.screenshot(path='/Users/mabolan/AgentProtocol/sidebar_current_only.png')

                # Extract CSS properties for navigation items
                nav_css = await page1.evaluate('''() => {
                    const nav = document.querySelector('.md-sidebar--primary') ||
                                document.querySelector('.md-sidebar') ||
                                document.querySelector('nav.md-nav');
                    if (!nav) return null;

                    const navItems = nav.querySelectorAll('.md-nav__item, .md-nav__link, li, a');
                    const results = {
                        nav_container: {},
                        items: []
                    };

                    // Get nav container styles
                    const navStyles = window.getComputedStyle(nav);
                    results.nav_container = {
                        padding: navStyles.padding,
                        paddingLeft: navStyles.paddingLeft,
                        paddingRight: navStyles.paddingRight,
                        margin: navStyles.margin,
                        marginLeft: navStyles.marginLeft,
                        marginRight: navStyles.marginRight,
                        position: navStyles.position,
                        width: navStyles.width
                    };

                    // Get styles for first few nav items
                    for (let i = 0; i < Math.min(10, navItems.length); i++) {
                        const item = navItems[i];
                        const styles = window.getComputedStyle(item);
                        const rect = item.getBoundingClientRect();
                        results.items.push({
                            tag: item.tagName,
                            class: item.className,
                            text: item.textContent.trim().substring(0, 50),
                            padding: styles.padding,
                            paddingLeft: styles.paddingLeft,
                            paddingRight: styles.paddingRight,
                            margin: styles.margin,
                            marginLeft: styles.marginLeft,
                            marginRight: styles.marginRight,
                            textIndent: styles.textIndent,
                            position: styles.position,
                            left: rect.left,
                            width: rect.width
                        });
                    }

                    return results;
                }''')

                results['page1'] = nav_css
            else:
                print("Could not find navigation element on page 1")
                results['page1'] = None

        except Exception as e:
            print(f"Error with page 1: {e}")
            results['page1'] = {'error': str(e)}
        finally:
            await page1.close()

        # Page 2: Reference with correct alignment
        print("\nAnalyzing page 2: http://localhost:8001/complete-page.html")
        page2 = await context.new_page()
        try:
            await page2.goto('http://localhost:8001/complete-page.html', wait_until='networkidle', timeout=10000)
            await page2.wait_for_timeout(1000)

            # Take full page screenshot
            await page2.screenshot(path='/Users/mabolan/AgentProtocol/sidebar_reference.png', full_page=True)

            # Find navigation sidebar
            nav_element = None
            for selector in nav_selectors:
                try:
                    nav_element = await page2.query_selector(selector)
                    if nav_element:
                        print(f"Found nav with selector: {selector}")
                        break
                except:
                    continue

            if nav_element:
                # Take screenshot of sidebar only
                await nav_element.screenshot(path='/Users/mabolan/AgentProtocol/sidebar_reference_only.png')

                # Extract CSS properties for navigation items
                nav_css = await page2.evaluate('''() => {
                    const nav = document.querySelector('.md-sidebar--primary') ||
                                document.querySelector('.md-sidebar') ||
                                document.querySelector('nav.md-nav');
                    if (!nav) return null;

                    const navItems = nav.querySelectorAll('.md-nav__item, .md-nav__link, li, a');
                    const results = {
                        nav_container: {},
                        items: []
                    };

                    // Get nav container styles
                    const navStyles = window.getComputedStyle(nav);
                    results.nav_container = {
                        padding: navStyles.padding,
                        paddingLeft: navStyles.paddingLeft,
                        paddingRight: navStyles.paddingRight,
                        margin: navStyles.margin,
                        marginLeft: navStyles.marginLeft,
                        marginRight: navStyles.marginRight,
                        position: navStyles.position,
                        width: navStyles.width
                    };

                    // Get styles for first few nav items
                    for (let i = 0; i < Math.min(10, navItems.length); i++) {
                        const item = navItems[i];
                        const styles = window.getComputedStyle(item);
                        const rect = item.getBoundingClientRect();
                        results.items.push({
                            tag: item.tagName,
                            class: item.className,
                            text: item.textContent.trim().substring(0, 50),
                            padding: styles.padding,
                            paddingLeft: styles.paddingLeft,
                            paddingRight: styles.paddingRight,
                            margin: styles.margin,
                            marginLeft: styles.marginLeft,
                            marginRight: styles.marginRight,
                            textIndent: styles.textIndent,
                            position: styles.position,
                            left: rect.left,
                            width: rect.width
                        });
                    }

                    return results;
                }''')

                results['page2'] = nav_css
            else:
                print("Could not find navigation element on page 2")
                results['page2'] = None

        except Exception as e:
            print(f"Error with page 2: {e}")
            results['page2'] = {'error': str(e)}
        finally:
            await page2.close()

        await browser.close()

        # Save results to JSON
        with open('/Users/mabolan/AgentProtocol/sidebar_comparison.json', 'w') as f:
            json.dump(results, f, indent=2)

        print("\nScreenshots saved:")
        print("  - sidebar_current.png (full page)")
        print("  - sidebar_current_only.png (sidebar only)")
        print("  - sidebar_reference.png (full page)")
        print("  - sidebar_reference_only.png (sidebar only)")
        print("  - sidebar_comparison.json (CSS data)")

        return results

if __name__ == '__main__':
    asyncio.run(capture_and_analyze())
