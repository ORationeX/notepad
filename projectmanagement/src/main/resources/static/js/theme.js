(function() {
    // 1. Immediately apply the stored theme before the DOM loads to prevent flashing
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);

    // 2. Set up the toggle button when DOM is ready
    document.addEventListener('DOMContentLoaded', () => {
        // Create the button element
        const toggleBtn = document.createElement('button');
        toggleBtn.id = 'themeToggleBtn';
        toggleBtn.className = 'theme-toggle-btn';
        toggleBtn.setAttribute('aria-label', 'Toggle Theme');
        
        // Icon depends on the current theme
        const icon = document.createElement('i');
        icon.className = savedTheme === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
        toggleBtn.appendChild(icon);
        
        // Append to body
        document.body.appendChild(toggleBtn);
        
        // Add event listener
        toggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Toggle icon class
            icon.className = newTheme === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
        });
    });
})();
