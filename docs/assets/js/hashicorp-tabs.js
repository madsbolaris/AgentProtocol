/**
 * HashiCorp Tabs - Tab switching functionality
 */

(function() {
  'use strict';

  function initializeTabs() {
    // Find all tab button lists
    const tabLists = document.querySelectorAll('.tab-button-controls_tabList__ueYEe');

    tabLists.forEach(tabList => {
      const buttons = tabList.querySelectorAll('button[role="tab"]');

      buttons.forEach(button => {
        button.addEventListener('click', handleTabClick);
        button.addEventListener('keydown', handleTabKeydown);
      });
    });

    // Restore saved language preference
    const savedLanguage = localStorage.getItem('preferred-code-language');
    if (savedLanguage) {
      const firstMatchingButton = document.querySelector(`button[role="tab"]`);
      if (firstMatchingButton) {
        const allButtons = document.querySelectorAll('button[role="tab"]');
        allButtons.forEach(button => {
          if (button.textContent.trim() === savedLanguage) {
            selectTab(button);
          }
        });
      }
    }
  }

  function handleTabClick(event) {
    const button = event.currentTarget;
    selectTab(button);
  }

  function handleTabKeydown(event) {
    const button = event.currentTarget;
    const tabList = button.closest('.tab-button-controls_tabList__ueYEe');
    const buttons = Array.from(tabList.querySelectorAll('button[role="tab"]'));
    const currentIndex = buttons.indexOf(button);

    let newIndex = currentIndex;

    switch(event.key) {
      case 'ArrowLeft':
        newIndex = currentIndex > 0 ? currentIndex - 1 : buttons.length - 1;
        event.preventDefault();
        break;
      case 'ArrowRight':
        newIndex = currentIndex < buttons.length - 1 ? currentIndex + 1 : 0;
        event.preventDefault();
        break;
      case 'Home':
        newIndex = 0;
        event.preventDefault();
        break;
      case 'End':
        newIndex = buttons.length - 1;
        event.preventDefault();
        break;
      default:
        return;
    }

    buttons[newIndex].focus();
    selectTab(buttons[newIndex]);
  }

  function selectTab(selectedButton) {
    const tabList = selectedButton.closest('.tab-button-controls_tabList__ueYEe');
    const buttons = tabList.querySelectorAll('button[role="tab"]');
    const panelId = selectedButton.getAttribute('aria-controls');
    const tabsWrapper = selectedButton.closest('.mdx-tabs_tabsWrapper__eBd6p');
    const panels = tabsWrapper.querySelectorAll('[role="tabpanel"]');

    // Get the selected tab label for syncing
    const selectedLabel = selectedButton.textContent.trim();

    // Update all buttons in this tab group
    buttons.forEach(button => {
      const isSelected = button === selectedButton;
      button.setAttribute('aria-selected', isSelected);
      button.setAttribute('tabindex', isSelected ? '0' : '-1');
    });

    // Update all panels in this tab group
    panels.forEach(panel => {
      const isVisible = panel.id === panelId;
      panel.setAttribute('aria-hidden', !isVisible);
    });

    // Sync all other tab groups on the page with the same label
    syncAllTabsWithLabel(selectedLabel, selectedButton);
  }

  function syncAllTabsWithLabel(label, excludeButton) {
    // Find all tab buttons on the page
    const allTabButtons = document.querySelectorAll('button[role="tab"]');

    allTabButtons.forEach(button => {
      // Skip the button that was clicked
      if (button === excludeButton) return;

      // Check if this button has the same label
      if (button.textContent.trim() === label) {
        // Get the tab group and panel
        const tabList = button.closest('.tab-button-controls_tabList__ueYEe');
        const buttons = tabList.querySelectorAll('button[role="tab"]');
        const panelId = button.getAttribute('aria-controls');
        const tabsWrapper = button.closest('.mdx-tabs_tabsWrapper__eBd6p');
        const panels = tabsWrapper.querySelectorAll('[role="tabpanel"]');

        // Update buttons in this tab group
        buttons.forEach(btn => {
          const isSelected = btn === button;
          btn.setAttribute('aria-selected', isSelected);
          btn.setAttribute('tabindex', isSelected ? '0' : '-1');
        });

        // Update panels in this tab group
        panels.forEach(panel => {
          const isVisible = panel.id === panelId;
          panel.setAttribute('aria-hidden', !isVisible);
        });
      }
    });

    // Save preference
    localStorage.setItem('preferred-code-language', label);
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeTabs);
  } else {
    initializeTabs();
  }

  // Re-initialize after instant navigation (if using Material's instant feature)
  document.addEventListener('DOMContentSwapped', initializeTabs);
})();
