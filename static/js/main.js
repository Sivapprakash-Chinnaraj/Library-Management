document.addEventListener("DOMContentLoaded", function() {
    
    // 1. Auto-dismiss Flash Messages after 4 seconds
    setTimeout(function() {
        let alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            // Check if bootstrap is defined to prevent errors
            if (typeof bootstrap !== 'undefined') {
                let bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } else {
                alert.style.display = 'none';
            }
        });
    }, 4000);

    // 2. Client-side Table Search Filter
    // To use this, add <input type="text" id="tableSearch" placeholder="Search..."> to any page with a table
    let searchInput = document.getElementById('tableSearch');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            let filter = searchInput.value.toLowerCase();
            let rows = document.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                // Get all text content from the row
                let text = row.textContent.toLowerCase();
                // Toggle display based on match
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    }
    // 3. 3D Book Flip Page Transition
    const pageWrapper = document.getElementById('page-wrapper');
    const links = document.querySelectorAll('a');

    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetUrl = this.getAttribute('href');
            const targetAttr = this.getAttribute('target');
            
            // Ignore links that don't route anywhere, or open in new tabs
            if (!targetUrl || targetUrl === '#' || targetAttr === '_blank') return;
            
            // Prevent instant navigation
            e.preventDefault();
            
            // Apply the flip-out animation
            pageWrapper.classList.add('flip-page-out');
            
            // Wait 500ms for the animation to finish before navigating
            setTimeout(() => {
                window.location.href = targetUrl;
            }, 500); 
        });
    });
    
});