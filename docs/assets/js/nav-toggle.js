/**
 * Navigation expand/collapse functionality
 */

(function() {
  'use strict';

  function initializeNavToggle() {
    const toggleButtons = document.querySelectorAll('[data-nav-toggle]');

    toggleButtons.forEach(button => {
      // Set initial state based on whether it has active class
      const isActive = button.classList.contains('sidebar-nav-item--active');
      if (isActive) {
        button.classList.add('nav-expanded');
      }

      button.addEventListener('click', function(e) {
        e.preventDefault();
        toggleNavSection(this);
      });
    });
  }

  function toggleNavSection(button) {
    const isExpanded = button.classList.contains('nav-expanded');
    const submenu = button.nextElementSibling;

    if (!submenu || !submenu.classList.contains('nav-submenu')) {
      return;
    }

    if (isExpanded) {
      // Collapse
      button.classList.remove('nav-expanded');
      submenu.classList.add('nav-collapsed');
    } else {
      // Expand
      button.classList.add('nav-expanded');
      submenu.classList.remove('nav-collapsed');
    }
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeNavToggle);
  } else {
    initializeNavToggle();
  }

  // Re-initialize after instant navigation
  document.addEventListener('DOMContentSwapped', initializeNavToggle);
})();
