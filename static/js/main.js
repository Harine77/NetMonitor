document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle functionality
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        // Check for saved theme preference or respect OS preference
        const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const savedTheme = localStorage.getItem('darkMode');
        
        // Apply theme based on saved preference or OS preference
        if (savedTheme === 'true' || (savedTheme === null && prefersDarkMode)) {
            document.body.classList.add('dark-mode');
        }
        
        // Toggle theme when button is clicked
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            // Save preference to localStorage
            const isDarkMode = document.body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDarkMode);
        });
    }
    
    // Initialize tooltips, dropdowns, etc. if using a framework
    // This is a placeholder for any additional initialization code
    
    // Make sidebar links active based on current page
    const currentPage = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    
    sidebarLinks.forEach(link => {
        if (link.getAttribute('href') === currentPage) {
            link.classList.add('active');
        }
    });
}); 