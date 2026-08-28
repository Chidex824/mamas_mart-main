// Custom sidebar toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    const mainWrapper = document.getElementById('main-wrapper');
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const body = document.querySelector('body');
    
    // Set initial state
    mainWrapper.setAttribute('data-sidebartype', 'full');
    
    // Function to handle sidebar toggle
    function toggleSidebar(event) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }
        
        const currentType = mainWrapper.getAttribute('data-sidebartype');
        const newType = currentType === 'mini-sidebar' ? 'full' : 'mini-sidebar';
        
        // Add transition class
        body.classList.add('sidebar-transitioning');
        
        // Set new sidebar type
        mainWrapper.setAttribute('data-sidebartype', newType);
        
        // Remove transition class after animation
        setTimeout(() => {
            body.classList.remove('sidebar-transitioning');
        }, 300);
    }

    // Add click event listener to toggle button
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }

    // Check local storage for saved sidebar state
    const savedSidebarType = localStorage.getItem('sidebarType');
    if (savedSidebarType) {
        mainWrapper.setAttribute('data-sidebartype', savedSidebarType);
    }
});
