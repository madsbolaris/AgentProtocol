// Synchronized tab selection across all tabbed code examples
document.addEventListener('DOMContentLoaded', function() {
  // Get all tab inputs
  const allTabs = document.querySelectorAll('.tabbed-set > input[type="radio"]');

  // Create a map to track which language is selected
  const selectedLanguage = localStorage.getItem('preferred-language') || null;

  // Function to sync all tabs to a specific language
  function syncTabs(language) {
    allTabs.forEach(input => {
      const label = input.nextElementSibling;
      if (label && label.textContent.trim() === language) {
        input.checked = true;
      }
    });
    localStorage.setItem('preferred-language', language);
  }

  // Apply saved preference on load
  if (selectedLanguage) {
    syncTabs(selectedLanguage);
  }

  // Listen for tab changes
  allTabs.forEach(input => {
    input.addEventListener('change', function() {
      if (this.checked) {
        const label = this.nextElementSibling;
        if (label) {
          const language = label.textContent.trim();
          syncTabs(language);
        }
      }
    });
  });
});
