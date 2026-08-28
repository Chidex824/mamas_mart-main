// JavaScript to handle AJAX loading of sidebar content into main content wrapper

document.addEventListener('DOMContentLoaded', function () {
  const sidebarLinks = document.querySelectorAll('.sidebar-link');
  const mainContentWrapper = document.querySelector('.body-wrapper');

  function loadContent(url) {
    if (!url) return;
    mainContentWrapper.innerHTML = '<p>Loading...</p>';
    fetch(url, {
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.text();
      })
      .then(html => {
        mainContentWrapper.innerHTML = html;
        // Optionally update browser history
        history.pushState(null, '', url);
      })
      .catch(error => {
        mainContentWrapper.innerHTML = '<p>Error loading content.</p>';
        console.error('Error loading content:', error);
      });
  }

  sidebarLinks.forEach(link => {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      const url = this.getAttribute('data-url');
      loadContent(url);
    });
  });

  // Load default content on page load (first sidebar link)
  if (sidebarLinks.length > 0) {
    const defaultUrl = sidebarLinks[0].getAttribute('data-url');
    loadContent(defaultUrl);
  }
});
