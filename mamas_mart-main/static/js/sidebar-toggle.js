// Custom sidebar toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    const mainWrapper = document.getElementById('main-wrapper');
    if (!mainWrapper) return;

    function applySidebarType(type) {
        const targetType = type === 'mini-sidebar' ? 'mini-sidebar' : 'full';
        mainWrapper.setAttribute('data-sidebartype', targetType);
        if (targetType === 'mini-sidebar') {
            mainWrapper.classList.add('mini-sidebar');
        } else {
            mainWrapper.classList.remove('mini-sidebar');
        }
        try {
            localStorage.setItem('sidebarType', targetType);
        } catch (e) {}
    }

    function toggleSidebar(event) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }
        const currentType = mainWrapper.getAttribute('data-sidebartype') || 'full';
        const nextType = currentType === 'mini-sidebar' ? 'full' : 'mini-sidebar';
        applySidebarType(nextType);
    }

    // Use event delegation so ANY toggle button in header or sidebar works reliably
    document.addEventListener('click', function(event) {
        const toggleBtn = event.target.closest('.sidebar-toggle, .sidebartoggler');
        if (toggleBtn) {
            toggleSidebar(event);
        }
    });

    // Restore saved sidebar preference
    try {
        const savedType = localStorage.getItem('sidebarType');
        if (savedType === 'mini-sidebar' || savedType === 'full') {
            applySidebarType(savedType);
        } else {
            applySidebarType('full');
        }
    } catch (e) {
        applySidebarType('full');
    }
});
