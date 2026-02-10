#!/usr/bin/env python3
"""
Extract sidebar navigation HTML and CSS from both pages for comparison.
"""
import asyncio
from playwright.async_api import async_playwright
import json

async def extract_sidebar_info():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})

        results = {}

        # Analyze current implementation
        print("Analyzing current implementation...")
        page1 = await context.new_page()
        try:
            await page1.goto('http://127.0.0.1:8001/products/client-sdk/', wait_until='networkidle', timeout=15000)
            await page1.wait_for_timeout(1500)

            # Extract sidebar HTML and CSS
            sidebar_data = await page1.evaluate('''() => {
                // Find the main sidebar
                const sidebar = document.querySelector('[data-md-component="sidebar"]') ||
                               document.querySelector('.md-sidebar--primary') ||
                               document.querySelector('.md-sidebar');

                if (!sidebar) return {error: 'Sidebar not found'};

                // Get the navigation list
                const navList = sidebar.querySelector('.md-nav__list') ||
                               sidebar.querySelector('ul');

                const result = {
                    sidebar_html: sidebar.innerHTML.substring(0, 5000),
                    nav_items: [],
                    css_classes: new Set()
                };

                // Analyze navigation items
                if (navList) {
                    const items = navList.querySelectorAll('li, a, .md-nav__item, .md-nav__link');

                    items.forEach((item, idx) => {
                        if (idx < 15) { // First 15 items
                            const styles = window.getComputedStyle(item);
                            const rect = item.getBoundingClientRect();

                            result.nav_items.push({
                                index: idx,
                                tag: item.tagName,
                                class: item.className,
                                text: item.textContent.trim().substring(0, 40),
                                styles: {
                                    padding: styles.padding,
                                    paddingLeft: styles.paddingLeft,
                                    paddingRight: styles.paddingRight,
                                    margin: styles.margin,
                                    marginLeft: styles.marginLeft,
                                    marginRight: styles.marginRight,
                                    textIndent: styles.textIndent,
                                    position: styles.position,
                                    display: styles.display,
                                    fontSize: styles.fontSize,
                                    lineHeight: styles.lineHeight
                                },
                                position: {
                                    left: rect.left,
                                    width: rect.width,
                                    top: rect.top
                                }
                            });

                            // Collect unique classes
                            if (item.className) {
                                item.className.split(' ').forEach(cls => {
                                    if (cls) result.css_classes.add(cls);
                                });
                            }
                        }
                    });
                }

                result.css_classes = Array.from(result.css_classes);
                return result;
            }''')

            results['current'] = sidebar_data

            # Take sidebar screenshot
            sidebar_elem = await page1.query_selector('[data-md-component="sidebar"]')
            if not sidebar_elem:
                sidebar_elem = await page1.query_selector('.md-sidebar--primary')
            if sidebar_elem:
                await sidebar_elem.screenshot(path='/Users/mabolan/AgentProtocol/current_sidebar.png')

        except Exception as e:
            print(f"Error analyzing current page: {e}")
            results['current'] = {'error': str(e)}
        finally:
            await page1.close()

        # Now analyze the reference page from the local file
        print("\nAnalyzing reference page (complete-page.html)...")
        page2 = await context.new_page()
        try:
            file_path = 'file:///Users/mabolan/AgentProtocol/.workspace/hashicorp-complete/complete-page.html'
            await page2.goto(file_path, wait_until='networkidle', timeout=15000)
            await page2.wait_for_timeout(1500)

            # Extract sidebar HTML and CSS
            sidebar_data = await page2.evaluate('''() => {
                // Find the main sidebar - try multiple selectors
                const sidebar = document.querySelector('[data-md-component="sidebar"]') ||
                               document.querySelector('.md-sidebar--primary') ||
                               document.querySelector('.md-sidebar') ||
                               document.querySelector('aside') ||
                               document.querySelector('nav');

                if (!sidebar) return {error: 'Sidebar not found', tried: 'multiple selectors'};

                // Get the navigation list
                const navList = sidebar.querySelector('.md-nav__list') ||
                               sidebar.querySelector('ul') ||
                               sidebar.querySelector('.docs-sidenav');

                const result = {
                    sidebar_html: sidebar.innerHTML.substring(0, 5000),
                    nav_items: [],
                    css_classes: new Set()
                };

                // Analyze navigation items
                if (navList) {
                    const items = navList.querySelectorAll('li, a, .md-nav__item, .md-nav__link');

                    items.forEach((item, idx) => {
                        if (idx < 15) { // First 15 items
                            const styles = window.getComputedStyle(item);
                            const rect = item.getBoundingClientRect();

                            result.nav_items.push({
                                index: idx,
                                tag: item.tagName,
                                class: item.className,
                                text: item.textContent.trim().substring(0, 40),
                                styles: {
                                    padding: styles.padding,
                                    paddingLeft: styles.paddingLeft,
                                    paddingRight: styles.paddingRight,
                                    margin: styles.margin,
                                    marginLeft: styles.marginLeft,
                                    marginRight: styles.marginRight,
                                    textIndent: styles.textIndent,
                                    position: styles.position,
                                    display: styles.display,
                                    fontSize: styles.fontSize,
                                    lineHeight: styles.lineHeight
                                },
                                position: {
                                    left: rect.left,
                                    width: rect.width,
                                    top: rect.top
                                }
                            });

                            // Collect unique classes
                            if (item.className) {
                                item.className.split(' ').forEach(cls => {
                                    if (cls) result.css_classes.add(cls);
                                });
                            }
                        }
                    });
                }

                result.css_classes = Array.from(result.css_classes);
                return result;
            }''')

            results['reference'] = sidebar_data

            # Take sidebar screenshot
            sidebar_elem = await page2.query_selector('[data-md-component="sidebar"]')
            if not sidebar_elem:
                sidebar_elem = await page2.query_selector('.md-sidebar--primary')
            if not sidebar_elem:
                sidebar_elem = await page2.query_selector('.md-sidebar')
            if not sidebar_elem:
                sidebar_elem = await page2.query_selector('aside')
            if sidebar_elem:
                await sidebar_elem.screenshot(path='/Users/mabolan/AgentProtocol/reference_sidebar.png')

        except Exception as e:
            print(f"Error analyzing reference page: {e}")
            results['reference'] = {'error': str(e)}
        finally:
            await page2.close()

        await browser.close()

        # Save results
        with open('/Users/mabolan/AgentProtocol/sidebar_css_comparison.json', 'w') as f:
            json.dump(results, f, indent=2)

        print("\n=== ANALYSIS COMPLETE ===")
        print("Files saved:")
        print("  - current_sidebar.png")
        print("  - reference_sidebar.png")
        print("  - sidebar_css_comparison.json")

        # Print comparison summary
        if 'current' in results and 'reference' in results:
            print("\n=== COMPARISON SUMMARY ===")

            if 'nav_items' in results['current'] and 'nav_items' in results['reference']:
                print(f"\nCurrent implementation: {len(results['current']['nav_items'])} items analyzed")
                print(f"Reference implementation: {len(results['reference']['nav_items'])} items analyzed")

                # Compare first item styles
                if results['current']['nav_items'] and results['reference']['nav_items']:
                    curr_item = results['current']['nav_items'][0]
                    ref_item = results['reference']['nav_items'][0]

                    print("\n--- First Navigation Item Comparison ---")
                    print(f"Current: '{curr_item['text']}'")
                    print(f"  Padding-left: {curr_item['styles']['paddingLeft']}")
                    print(f"  Margin-left: {curr_item['styles']['marginLeft']}")
                    print(f"  Text-indent: {curr_item['styles']['textIndent']}")
                    print(f"  Position left: {curr_item['position']['left']}px")

                    print(f"\nReference: '{ref_item['text']}'")
                    print(f"  Padding-left: {ref_item['styles']['paddingLeft']}")
                    print(f"  Margin-left: {ref_item['styles']['marginLeft']}")
                    print(f"  Text-indent: {ref_item['styles']['textIndent']}")
                    print(f"  Position left: {ref_item['position']['left']}px")

        return results

if __name__ == '__main__':
    asyncio.run(extract_sidebar_info())
