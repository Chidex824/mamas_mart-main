document.addEventListener('DOMContentLoaded', function() {
    const dynamicContent = document.getElementById('dynamic-content');
    const sidebarLinks = document.querySelectorAll('.sidebar-link[data-url]');

    sidebarLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.getAttribute('data-url');

            // Add active class to clicked link and remove from others
            sidebarLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');

            // Fetch content from the URL
            fetch(url)
                .then(response => response.text())
                .then(html => {
                    // Create a temporary element to parse the HTML
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    
                    // Find the dynamic content in the response
                    const newContent = doc.querySelector('#dynamic-content');
                    if (newContent) {
                        dynamicContent.innerHTML = newContent.innerHTML;
                    } else {
                        // If no specific dynamic content found, load the main content
                        const mainContent = doc.querySelector('.container-fluid');
                        if (mainContent) {
                            dynamicContent.innerHTML = mainContent.innerHTML;
                        }
                    }
                })
                .catch(error => {
                    console.error('Error loading content:', error);
                });
        });
    });

    // Trigger click on the current page's link if it exists
    const currentPath = window.location.pathname;
    const currentLink = document.querySelector(`.sidebar-link[data-url="${currentPath}"]`);
    if (currentLink) {
        currentLink.classList.add('active');
    }
});
