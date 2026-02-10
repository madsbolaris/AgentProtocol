/**
 * Copy button functionality for code blocks
 * Matches HashiCorp's copy button behavior
 */
document.addEventListener('DOMContentLoaded', function() {
  // Find all copy buttons
  const copyButtons = document.querySelectorAll('.copy-button__nMsTD, button[aria-label="Copy code to clipboard"]');

  copyButtons.forEach(button => {
    button.addEventListener('click', async function(e) {
      e.preventDefault();

      // Find the associated code block
      const codeBlock = this.closest('.highlight, .code-block__dOm6M, div[class*="highlight"]');
      if (!codeBlock) return;

      // Get the code content - try multiple selectors
      let code = '';
      const pre = codeBlock.querySelector('pre code, pre.code__J06se code, pre');
      if (pre) {
        code = pre.textContent || pre.innerText;
      }

      if (!code) return;

      try {
        // Copy to clipboard
        await navigator.clipboard.writeText(code);

        // Visual feedback
        const originalHTML = this.innerHTML;
        const originalAriaLabel = this.getAttribute('aria-label');

        // Show success state
        this.innerHTML = `<svg class="flight-icon__f6lPO flight-icon-check display-inline__ItStG" aria-hidden="true" fill="currentColor" width="12" height="12" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg"><path d="M13.78 4.22a.75.75 0 010 1.06l-7.25 7.25a.75.75 0 01-1.06 0L2.22 9.28a.75.75 0 011.06-1.06L6 10.94l6.72-6.72a.75.75 0 011.06 0z"/></svg>`;
        this.setAttribute('aria-label', 'Copied!');
        this.classList.remove('idle__1ofXr');
        this.classList.add('success__2Kpjx');

        // Reset after 2 seconds
        setTimeout(() => {
          this.innerHTML = originalHTML;
          this.setAttribute('aria-label', originalAriaLabel || 'Copy');
          this.classList.remove('success__2Kpjx');
          this.classList.add('idle__1ofXr');
        }, 2000);

      } catch (err) {
        console.error('Failed to copy code:', err);

        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = code;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        document.body.appendChild(textArea);
        textArea.select();

        try {
          document.execCommand('copy');
          // Show success feedback
          const originalAriaLabel = this.getAttribute('aria-label');
          this.setAttribute('aria-label', 'Copied!');
          setTimeout(() => {
            this.setAttribute('aria-label', originalAriaLabel || 'Copy');
          }, 2000);
        } catch (err2) {
          console.error('Fallback copy failed:', err2);
        }

        document.body.removeChild(textArea);
      }
    });
  });
});
