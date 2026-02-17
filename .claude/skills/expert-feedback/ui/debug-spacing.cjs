/**
 * Debug script to inspect the conversation view spacing issue
 */

const { chromium } = require('playwright');
const path = require('path');

async function debugSpacing() {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    // Load the prototype HTML file
    const htmlPath = path.join(__dirname, '../../../.workspace/2026/02/16/expert-feedback-ui/prototype.html');
    await page.goto(`file://${htmlPath}`);

    // Switch to conversation view
    await page.click('[data-view="conversation"]');
    await page.waitForTimeout(500);

    console.log('\n=== Conversation View Spacing Debug ===\n');

    // Check if conversation view is active
    const isActive = await page.evaluate(() => {
        const conv = document.querySelector('.conversation-view');
        return conv ? conv.classList.contains('active') : false;
    });
    console.log('Conversation view active:', isActive);

    // Get all messages
    const messages = await page.evaluate(() => {
        const conv = document.querySelector('.conversation-view');
        if (!conv) return [];

        const msgs = Array.from(conv.querySelectorAll('.message'));
        return msgs.map((msg, idx) => {
            const computed = window.getComputedStyle(msg);
            const isLastOfType = msg === conv.querySelector('.message:last-of-type');
            const isLastChild = msg === conv.lastElementChild;

            return {
                index: idx,
                isLastOfType,
                isLastChild,
                marginBottom: computed.marginBottom,
                classes: Array.from(msg.classList),
            };
        });
    });

    console.log('\nMessages found:', messages.length);
    messages.forEach(msg => {
        console.log(`  Message ${msg.index}:`, {
            marginBottom: msg.marginBottom,
            isLastOfType: msg.isLastOfType,
            isLastChild: msg.isLastChild,
            classes: msg.classes
        });
    });

    // Check message input container
    const inputInfo = await page.evaluate(() => {
        const input = document.querySelector('.message-input-container');
        if (!input) return null;

        const computed = window.getComputedStyle(input);
        const conv = document.querySelector('.conversation-view');
        const isLastChild = conv && input === conv.lastElementChild;

        return {
            position: computed.position,
            bottom: computed.bottom,
            zIndex: computed.zIndex,
            background: computed.background,
            isLastChild,
            isInsideConversationView: !!input.closest('.conversation-view')
        };
    });

    console.log('\nMessage Input Container:', inputInfo);

    // Check the applied CSS rules
    const cssRules = await page.evaluate(() => {
        const conv = document.querySelector('.conversation-view');
        if (!conv) return [];

        const lastMessage = conv.querySelector('.message:last-of-type');
        if (!lastMessage) return [];

        // Get all matching CSS rules
        const rules = [];
        const sheets = Array.from(document.styleSheets);

        for (const sheet of sheets) {
            try {
                const cssRules = Array.from(sheet.cssRules || []);
                for (const rule of cssRules) {
                    if (rule.selectorText && lastMessage.matches(rule.selectorText)) {
                        const marginBottom = rule.style.marginBottom;
                        if (marginBottom) {
                            rules.push({
                                selector: rule.selectorText,
                                marginBottom: marginBottom
                            });
                        }
                    }
                }
            } catch (e) {
                // Skip sheets we can't access
            }
        }

        return rules;
    });

    console.log('\nCSS rules affecting last message margin-bottom:');
    cssRules.forEach(rule => {
        console.log(`  ${rule.selector} { margin-bottom: ${rule.marginBottom} }`);
    });

    // Check the detailed structure
    const structure = await page.evaluate(() => {
        const conv = document.querySelector('.conversation-view');
        if (!conv) return null;

        return {
            childCount: conv.children.length,
            lastChild: conv.lastElementChild?.className || null,
            children: Array.from(conv.children).map(child => ({
                tag: child.tagName,
                class: child.className,
                isMessage: child.classList.contains('message'),
                isInput: child.classList.contains('message-input-container')
            }))
        };
    });

    console.log('\nConversation view structure:', JSON.stringify(structure, null, 2));

    await browser.close();
}

debugSpacing().catch(console.error);
