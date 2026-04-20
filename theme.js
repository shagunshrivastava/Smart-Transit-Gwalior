/**
 * Transport System - Theme Management
 * Handles dark/light mode switching and persistence
 */

(function() {
    const themeKey = 'transport-system-theme';
    const html = document.documentElement;

    /**
     * Apply the theme to the document
     * @param {string} theme - 'dark' or 'light'
     */
    function applyTheme(theme) {
        if (theme === 'light') {
            html.classList.add('light-mode');
        } else {
            html.classList.remove('light-mode');
        }
        localStorage.setItem(themeKey, theme);
    }

    /**
     * Initialize theme on page load
     */
    function initTheme() {
        const savedTheme = localStorage.getItem(themeKey);
        if (savedTheme) {
            applyTheme(savedTheme);
        } else {
            // Default to dark mode as per original design
            applyTheme('dark');
        }
    }

    /**
     * Toggle between themes
     */
    window.toggleTheme = function() {
        const currentTheme = html.classList.contains('light-mode') ? 'light' : 'dark';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        applyTheme(newTheme);
    };

    // Run initialization
    initTheme();
})();
