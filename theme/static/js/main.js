/**
 * MyCodePlatform Main JavaScript
 */

const MyCodePlatform = {
    // Toast notification system
    showToast: function(message, type = 'info') {
        // Remove any existing toasts
        const existingToasts = document.querySelectorAll('.toast-notification');
        existingToasts.forEach(toast => toast.remove());
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = 'toast-notification fixed bottom-4 right-4 px-4 py-2 rounded-lg shadow-lg z-50 transition-opacity duration-300';
        
        // Set style based on type
        switch(type) {
            case 'success':
                toast.classList.add('bg-green-600', 'text-white');
                message = `<i class="fas fa-check-circle mr-2"></i>${message}`;
                break;
            case 'error':
                toast.classList.add('bg-red-600', 'text-white');
                message = `<i class="fas fa-exclamation-circle mr-2"></i>${message}`;
                break;
            case 'warning':
                toast.classList.add('bg-yellow-500', 'text-white');
                message = `<i class="fas fa-exclamation-triangle mr-2"></i>${message}`;
                break;
            default: // info
                toast.classList.add('bg-gray-800', 'text-white');
                message = `<i class="fas fa-info-circle mr-2"></i>${message}`;
        }
        
        toast.innerHTML = message;
        document.body.appendChild(toast);
        
        // Remove toast after 3 seconds
        setTimeout(() => {
            toast.classList.add('opacity-0');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 3000);
    },
    
    // Initialize common functionality
    init: function() {
        // Add any global initialization here
        this.initDropdowns();
        this.initMobileMenu();
    },
    
    // Initialize dropdown menus
    initDropdowns: function() {
        const dropdownButtons = document.querySelectorAll('[data-dropdown-toggle]');
        
        dropdownButtons.forEach(button => {
            const targetId = button.getAttribute('data-dropdown-toggle');
            const target = document.getElementById(targetId);
            
            if (target) {
                button.addEventListener('click', (e) => {
                    e.stopPropagation();
                    target.classList.toggle('hidden');
                });
                
                // Close when clicking outside
                document.addEventListener('click', (e) => {
                    if (!button.contains(e.target) && !target.contains(e.target)) {
                        target.classList.add('hidden');
                    }
                });
            }
        });
    },
    
    // Initialize mobile menu
    initMobileMenu: function() {
        const mobileMenuButton = document.getElementById('mobile-menu-button');
        const mobileMenu = document.getElementById('mobile-menu');
        
        if (mobileMenuButton && mobileMenu) {
            mobileMenuButton.addEventListener('click', () => {
                mobileMenu.classList.toggle('hidden');
            });
        }
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    MyCodePlatform.init();
});