/**
 * EXTRACTED FROM: 6722-08dd1931f158b3d6.js
 *
 * HashiCorp's scroll container logic that adds/removes scrim classes
 */

// The key function that calculates scroll state
function calculateScrollState(element) {
    const { scrollTop, scrollHeight, clientHeight } = element;
    const scrollableHeight = scrollHeight - clientHeight;
    const isScrollable = scrollableHeight > 0;
    const scrollPercentage = Math.round((100 * scrollTop) / scrollableHeight);

    if (Number.isNaN(scrollPercentage)) {
        return { isScrollable };
    }

    return {
        isScrollable,
        isAtStart: isScrollable && scrollPercentage === 0,
        isAtEnd: isScrollable && scrollPercentage === 100
    };
}

// Apply scrim classes based on scroll state
function updateScrollScrims(rootElement, scrollContainer) {
    const state = calculateScrollState(scrollContainer);

    // CSS classes from HashiCorp
    const showTopScrimClass = 'sidecar-scroll-container_showTopScrim__Cvl7n';
    const showBottomScrimClass = 'sidecar-scroll-container_showBottomScrim__yucsk';

    // Add/remove top scrim (shown when not at start)
    if (state.isScrollable && !state.isAtStart) {
        rootElement.classList.add(showTopScrimClass);
    } else {
        rootElement.classList.remove(showTopScrimClass);
    }

    // Add/remove bottom scrim (shown when not at end)
    if (state.isScrollable && !state.isAtEnd) {
        rootElement.classList.add(showBottomScrimClass);
    } else {
        rootElement.classList.remove(showBottomScrimClass);
    }
}

// Initialize scroll container
function initScrollContainer(rootSelector = '.sidecar-scroll-container_root__a8nIj') {
    const rootElement = document.querySelector(rootSelector);
    if (!rootElement) {
        console.warn('Scroll container root not found:', rootSelector);
        return;
    }

    const scrollContainer = rootElement.querySelector('.sidecar-scroll-container_scrollContainer__Dw9id');
    if (!scrollContainer) {
        console.warn('Scroll container not found inside root');
        return;
    }

    // Update on scroll
    scrollContainer.addEventListener('scroll', () => {
        updateScrollScrims(rootElement, scrollContainer);
    });

    // Update on resize (content height might change)
    const resizeObserver = new ResizeObserver(() => {
        updateScrollScrims(rootElement, scrollContainer);
    });
    resizeObserver.observe(scrollContainer);

    // Initial update
    updateScrollScrims(rootElement, scrollContainer);

    console.log('✅ Scroll container initialized');
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => initScrollContainer());
} else {
    initScrollContainer();
}
