# Sidebar Navigation CSS Analysis

## Reference Page (complete-page.html) - Correct Alignment

### HTML Structure
The reference page uses the following structure:
```html
<ul class="sidebar_navList__4Rg4g">
  <li>
    <a class="sidebar-nav-highlight-item_root___pPhp">...</a>
  </li>
  <li>
    <button class="sidebar-nav-menu-item_sidebarNavMenuItem__PiyI8">...</button>
  </li>
</ul>
```

### Key CSS Properties for Correct Alignment

#### 1. `.sidebar_navList__4Rg4g` (Main Navigation List)
```css
.sidebar_navList__4Rg4g {
  list-style: none;
  margin: 0;
  padding: 0;
}
```

#### 2. `.sidebar-nav-menu-item_sidebarNavMenuItem__PiyI8` (Menu Items)
```css
.sidebar-nav-menu-item_sidebarNavMenuItem__PiyI8 {
  align-items: center;
  background-color: var(--mds-color-surface-primary);
  border-radius: 5px;
  border: none;
  color: var(--mds-color-foreground-faint);
  display: flex;
  justify-content: space-between;
  margin-bottom: 2px;
  padding: 8px;                    /* KEY PROPERTY */
  position: relative;
  text-align: left;
  width: 100%;
  z-index: 0;
}
```

**Key padding value: `padding: 8px;`**

#### 3. `.sidebar-nav-highlight-item_root___pPhp` (Highlight Items)
```css
.sidebar-nav-highlight-item_root___pPhp {
  align-items: center;
  background: var(--mds-color-surface-primary);
  border-radius: 5px;
  color: var(--mds-color-foreground-primary);
  display: flex;
  grid-gap: 8px;
  gap: 8px;
  margin-bottom: 2px;
  padding: 8px;                    /* KEY PROPERTY */
  position: relative;
  width: 100%;
  z-index: 0;
}
```

**Key padding value: `padding: 8px;`**

#### 4. Nested List Indentation
```css
.sidebar_sidebar___fTlC ul ul {
  list-style: none;
  padding: 0;
  margin: 0 0 0 .5em;             /* KEY PROPERTY - Left margin for nested items */
}
```

**Key margin value: `margin: 0 0 0 .5em;` (0.5em left margin for nesting)**

#### 5. Navigation Label
```css
.sidebar-nav-menu-item_navMenuItemLabel__tJHwX {
  margin-right: 8px;
  width: 100%;
}
```

### Container CSS

#### `.sidebar_sidebar___fTlC` (Sidebar Container)
No specific padding/margin on the container itself - alignment comes from the individual items.

#### `.sidebar_nav__IworY` (Nav Wrapper)
```css
.sidebar_nav__IworY {
  position: relative;
}

.sidebar_nav__IworY:first-child {
  margin-top: 8px;
}
```

### Interactive States

#### Hover State
```css
.sidebar-nav-menu-item_sidebarNavMenuItem__PiyI8:hover {
  background-color: var(--mds-color-palette-neutral-100);
}
```

#### Active/Current Page
```css
.sidebar-nav-menu-item_sidebarNavMenuItem__PiyI8[aria-current=page] {
  background-color: var(--mds-color-palette-neutral-200);
}
```

#### Expanded State
```css
.sidebar-nav-menu-item_sidebarNavMenuItem__PiyI8[aria-expanded=true] {
  margin-bottom: 0;
}
```

## Summary of Key Properties for Alignment

### Essential Properties:
1. **Uniform padding**: `padding: 8px;` on all navigation items (both links and buttons)
2. **No left/right padding or margin on the list**: `padding: 0;` and `margin: 0;` on `ul.sidebar_navList__4Rg4g`
3. **Consistent spacing**: `margin-bottom: 2px;` between items
4. **Nested indentation**: `margin: 0 0 0 .5em;` for nested `ul ul` (0.5em left margin)
5. **Full width items**: `width: 100%;` on all navigation items
6. **Flex alignment**: `display: flex; align-items: center;` for proper vertical alignment

### Common Alignment Issues to Check:
- **Uneven left padding/margin** on navigation items
- **Text-indent** being applied incorrectly
- **Different padding** between different item types (links vs buttons)
- **Container padding** pushing items to the right
- **List-style markers** not being removed

## Comparison Checklist

To fix alignment issues in the current implementation, verify:
1. [ ] All `<li>` items have `padding: 8px;` (or consistent padding)
2. [ ] Parent `<ul>` has `padding: 0; margin: 0;`
3. [ ] No extra `text-indent` is applied
4. [ ] All navigation links/buttons have `width: 100%;`
5. [ ] Nested lists have only `margin-left: 0.5em;`
6. [ ] No extra padding on sidebar container is shifting content
