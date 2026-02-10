# CSS Fix Checklist - If Alignment Issues Exist

## Quick Reference: Key CSS Properties

If you need to adjust sidebar navigation alignment, here are the exact CSS properties and values to check/modify:

### 1. Navigation List Container
```css
.sidebar_navList__4Rg4g {
  list-style: none;
  margin: 0;           /* Must be 0 - no margin */
  padding: 0;          /* Must be 0 - no padding */
}
```

### 2. Navigation Items (Links/Buttons)
```css
.sidebar-nav-menu-item_sidebarNavMenuItem__PiyI8 {
  padding: 8px;                    /* CRITICAL: Exactly 8px all sides */
  margin-bottom: 2px;
  width: 100%;
  box-sizing: border-box;          /* Ensure padding doesn't add to width */
  text-indent: 0;                  /* CRITICAL: No text indentation */
  display: flex;
  align-items: center;
}
```

### 3. Nested Lists
```css
.sidebar_sidebar___fTlC ul ul {
  list-style: none;
  padding: 0;
  margin: 0 0 0 .5em;             /* CRITICAL: Only 0.5em left margin */
}
```

### 4. Item Labels
```css
.sidebar-nav-menu-item_navMenuItemLabel__tJHwX {
  margin-right: 8px;
  width: 100%;
  text-indent: 0;                  /* Ensure no text indentation */
}
```

## Common Alignment Issues and Fixes

### Issue 1: Items Not Left-Aligned

**Symptoms:**
- Navigation items don't line up on the left edge
- Inconsistent left margins

**Fix:**
```css
/* Ensure list has no padding */
.sidebar_navList__4Rg4g {
  padding-left: 0 !important;
  margin-left: 0 !important;
}

/* Ensure items have consistent padding */
.sidebar-nav-menu-item_sidebarNavMenuItem__PiyI8 {
  padding: 8px !important;
  text-indent: 0 !important;
}
```

### Issue 2: Nested Items Too Far Indented

**Symptoms:**
- Second-level items have excessive left indent
- Visual hierarchy too pronounced

**Fix:**
```css
/* Reduce nested list margin */
.sidebar_sidebar___fTlC ul ul,
.sidebar_navList__4Rg4g .sidebar_navList__4Rg4g {
  margin-left: 0.5em !important;  /* Only half an em */
  padding-left: 0 !important;
}
```

### Issue 3: Text Not Aligned Within Items

**Symptoms:**
- Text appears offset within the button/link
- Inconsistent text positioning

**Fix:**
```css
/* Remove any text indentation */
.sidebar-nav-menu-item_sidebarNavMenuItem__PiyI8,
.sidebar-nav-menu-item_navMenuItemLabel__tJHwX {
  text-indent: 0 !important;
}

/* Ensure proper flex alignment */
.sidebar-nav-menu-item_sidebarNavMenuItem__PiyI8 {
  display: flex !important;
  align-items: center !important;
}
```

### Issue 4: Items Different Widths

**Symptoms:**
- Some items appear narrower than others
- Right edges don't align

**Fix:**
```css
/* Ensure all items full width */
.sidebar-nav-menu-item_sidebarNavMenuItem__PiyI8 {
  width: 100% !important;
  box-sizing: border-box !important;
}

/* Ensure parent container doesn't restrict width */
.sidebar_navList__4Rg4g {
  width: 100%;
}
```

### Issue 5: Spacing Inconsistent

**Symptoms:**
- Gaps between items vary
- Some items too close together

**Fix:**
```css
/* Consistent spacing */
.sidebar-nav-menu-item_sidebarNavMenuItem__PiyI8 {
  margin-bottom: 2px !important;
  margin-top: 0 !important;
  margin-left: 0 !important;
  margin-right: 0 !important;
}
```

## Where to Add Fixes

### Option 1: Custom CSS File
Add to `/Users/mabolan/AgentProtocol/docs/assets/css/extra.css` or create a new file:

```css
/* Sidebar Navigation Alignment Fixes */

/* Reset list containers */
.sidebar_navList__4Rg4g {
  list-style: none !important;
  margin: 0 !important;
  padding: 0 !important;
}

/* Uniform padding on all items */
.sidebar-nav-menu-item_sidebarNavMenuItem__PiyI8 {
  padding: 8px !important;
  margin-bottom: 2px !important;
  width: 100% !important;
  box-sizing: border-box !important;
  text-indent: 0 !important;
}

/* Minimal nested indentation */
.sidebar_sidebar___fTlC ul ul {
  margin: 0 0 0 0.5em !important;
  padding: 0 !important;
}

/* No text indent on labels */
.sidebar-nav-menu-item_navMenuItemLabel__tJHwX {
  text-indent: 0 !important;
}
```

### Option 2: Inline Styles Override
Add to `/Users/mabolan/AgentProtocol/docs/overrides/base.html`:

```html
<style>
/* Sidebar Navigation Alignment Overrides */
.sidebar_navList__4Rg4g {
  padding: 0;
  margin: 0;
}

.sidebar-nav-menu-item_sidebarNavMenuItem__PiyI8 {
  padding: 8px;
  text-indent: 0;
}

.sidebar_sidebar___fTlC ul ul {
  margin: 0 0 0 0.5em;
}
</style>
```

## Verification Steps

After applying fixes:

1. **Clear Browser Cache**
   ```bash
   # Force reload with Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
   ```

2. **Check Computed Styles**
   - Open DevTools (F12)
   - Select a navigation item
   - Go to "Computed" tab
   - Verify:
     - `padding: 8px` (or `8px 8px 8px 8px`)
     - `padding-left: 8px`
     - `margin-left: 0px` (for top-level items)
     - `text-indent: 0px`

3. **Visual Inspection**
   - All items should have same left edge position
   - Nested items should be only slightly indented (≈8px)
   - Items should have consistent vertical spacing
   - Hover states should work uniformly

4. **Test Responsiveness**
   - Resize browser window
   - Check mobile breakpoints
   - Verify alignment holds at all sizes

## Debugging Commands

### Check Current CSS
```bash
# View loaded CSS
curl -s http://127.0.0.1:8001/assets/css/inline-styles-2.css | grep -A 10 "sidebar-nav-menu-item"

# Check for overrides
grep -r "sidebar-nav\|padding.*8px" /Users/mabolan/AgentProtocol/docs/assets/css/
```

### Check HTML Structure
```bash
# View navigation HTML
curl -s http://127.0.0.1:8001/products/client-sdk/ | grep -A 20 "sidebar_navList__4Rg4g" | head -30
```

### Check File Modifications
```bash
# See what CSS files have been modified
git status /Users/mabolan/AgentProtocol/docs/assets/css/
git diff /Users/mabolan/AgentProtocol/docs/assets/css/
```

## CSS Property Priority (Importance)

1. **CRITICAL** - These must be correct:
   - `padding: 8px` on all nav items
   - `padding: 0` on list containers
   - `text-indent: 0` everywhere

2. **Important** - These should match:
   - `margin-bottom: 2px` for spacing
   - `width: 100%` on all items
   - `box-sizing: border-box` on all items

3. **Nice to have** - These enhance UX:
   - `border-radius: 5px` for rounded corners
   - `background-color` for hover states
   - `transition` for smooth animations

## Testing Checklist

- [ ] Top-level items all start at same left position
- [ ] Nested items indented by exactly 0.5em (≈8px)
- [ ] No unwanted text-indent applied anywhere
- [ ] Items have 8px padding on all sides
- [ ] Vertical spacing is 2px between items
- [ ] Items span full width of sidebar
- [ ] Hover states work correctly
- [ ] Active/current page highlighting works
- [ ] Expandable sections toggle properly
- [ ] Looks correct on mobile viewports
- [ ] Print preview shows correct alignment

## Still Having Issues?

If alignment problems persist after applying these fixes:

1. **Share specifics:**
   - Which item(s) are misaligned
   - Expected vs actual position (in pixels)
   - Browser DevTools screenshot showing computed styles

2. **Check for conflicts:**
   ```bash
   # Search for CSS that might override
   grep -r "!important" /Users/mabolan/AgentProtocol/docs/assets/css/
   ```

3. **Verify CSS load order:**
   - View page source
   - Check `<link>` tags in `<head>`
   - Ensure custom CSS loads after inline-styles-2.css

4. **Test in isolation:**
   - Disable all CSS except inline-styles-2.css
   - Add fixes one at a time
   - Identify conflicting rule

## Quick Test Template

Use this in browser console to test alignment:

```javascript
// Check all nav items
document.querySelectorAll('.sidebar-nav-menu-item_sidebarNavMenuItem__PiyI8').forEach((el, i) => {
  const styles = window.getComputedStyle(el);
  console.log(`Item ${i}:`, {
    padding: styles.padding,
    paddingLeft: styles.paddingLeft,
    marginLeft: styles.marginLeft,
    textIndent: styles.textIndent,
    left: el.getBoundingClientRect().left
  });
});
```

Expected output: All items should show `paddingLeft: "8px"`, `marginLeft: "0px"` (top-level), `textIndent: "0px"`.
