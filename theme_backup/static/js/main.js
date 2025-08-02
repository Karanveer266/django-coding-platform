// Main JavaScript for CodePlatform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeNavigation();
    initializeToasts();
    initializeModals();
    initializeCodeEditor();
    initializeSearch();
    initializeTheme();
});

// Navigation functionality
function initializeNavigation() {
    // User menu toggle
    const userMenuButton = document.getElementById('user-menu-button');
    const userMenu = document.getElementById('user-menu');
    
    if (userMenuButton && userMenu) {
        userMenuButton.addEventListener('click', function(e) {
            e.stopPropagation();
            userMenu.classList.toggle('hidden');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!userMenuButton.contains(e.target) && !userMenu.contains(e.target)) {
                userMenu.classList.add('hidden');
            }
        });
    }
    
    // Mobile menu toggle
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
            
            // Update button icon
            const icon = mobileMenuButton.querySelector('i');
            if (mobileMenu.classList.contains('hidden')) {
                icon.className = 'fas fa-bars text-lg';
            } else {
                icon.className = 'fas fa-times text-lg';
            }
        });
    }
    
    // Notifications toggle
    const notificationsButton = document.getElementById('notifications-button');
    if (notificationsButton) {
        notificationsButton.addEventListener('click', function() {
            // TODO: Implement notifications panel
            showToast('Notifications panel coming soon!', 'info');
        });
    }
}

// Toast notifications
function initializeToasts() {
    // Auto-hide existing toasts after 5 seconds
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        setTimeout(() => {
            hideToast(toast);
        }, 5000);
    });
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type} slide-in`;
    
    const icon = getToastIcon(type);
    const color = getToastColor(type);
    
    toast.innerHTML = `
        <div class="flex items-center">
            <div class="flex-shrink-0">
                <i class="fas ${icon} ${color}"></i>
            </div>
            <div class="ml-3">
                <p class="text-sm ${color}">${message}</p>
            </div>
            <div class="ml-auto pl-3">
                <button type="button" class="text-gray-400 hover:text-gray-600" onclick="hideToast(this.closest('.toast'))">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        hideToast(toast);
    }, 5000);
}

function hideToast(toast) {
    if (toast) {
        toast.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }
}

function getToastIcon(type) {
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    return icons[type] || icons.info;
}

function getToastColor(type) {
    const colors = {
        success: 'text-green-600',
        error: 'text-red-600',
        warning: 'text-yellow-600',
        info: 'text-blue-600'
    };
    return colors[type] || colors.info;
}

// Modal functionality
function initializeModals() {
    // Close modal when clicking on backdrop
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal-backdrop')) {
            closeModal(e.target.closest('.modal'));
        }
    });
    
    // Close modal with escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal:not(.hidden)');
            if (openModal) {
                closeModal(openModal);
            }
        }
    });
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        
        // Focus on first focusable element
        const firstInput = modal.querySelector('input, textarea, select, button');
        if (firstInput) {
            firstInput.focus();
        }
    }
}

function closeModal(modal) {
    if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = 'auto';
    }
}

// Code Editor functionality
function initializeCodeEditor() {
    const codeEditors = document.querySelectorAll('.code-editor');
    
    codeEditors.forEach(editor => {
        const textarea = editor.querySelector('textarea');
        if (textarea) {
            // Add line numbers
            addLineNumbers(editor, textarea);
            
            // Handle tab key
            textarea.addEventListener('keydown', function(e) {
                if (e.key === 'Tab') {
                    e.preventDefault();
                    const start = this.selectionStart;
                    const end = this.selectionEnd;
                    
                    this.value = this.value.substring(0, start) + '    ' + this.value.substring(end);
                    this.selectionStart = this.selectionEnd = start + 4;
                    
                    updateLineNumbers(editor, this);
                }
            });
            
            // Update line numbers on input
            textarea.addEventListener('input', function() {
                updateLineNumbers(editor, this);
            });
        }
    });
}

function addLineNumbers(editor, textarea) {
    const lineNumbers = document.createElement('div');
    lineNumbers.className = 'line-numbers absolute left-0 top-0 w-12 h-full bg-gray-800 text-gray-400 text-sm font-mono text-right pr-2 py-4 select-none';
    
    editor.style.position = 'relative';
    textarea.style.paddingLeft = '3rem';
    
    editor.insertBefore(lineNumbers, textarea);
    updateLineNumbers(editor, textarea);
}

function updateLineNumbers(editor, textarea) {
    const lineNumbers = editor.querySelector('.line-numbers');
    if (lineNumbers) {
        const lines = textarea.value.split('\n').length;
        let numbersHTML = '';
        
        for (let i = 1; i <= lines; i++) {
            numbersHTML += i + '\n';
        }
        
        lineNumbers.textContent = numbersHTML;
    }
}

// Search functionality
function initializeSearch() {
    const searchInputs = document.querySelectorAll('#global-search, input[placeholder*="Search"]');
    
    searchInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    performSearch(query);
                }, 300);
            }
        });
        
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                performSearch(this.value.trim());
            }
        });
    });
}

function performSearch(query) {
    if (query.length < 2) return;
    
    // TODO: Implement actual search functionality
    console.log('Searching for:', query);
    
    // For now, just show a toast
    showToast(`Searching for "${query}"...`, 'info');
}

// Theme functionality
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);
    
    // Theme toggle button (if exists)
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = localStorage.getItem('theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            applyTheme(newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
}

function applyTheme(theme) {
    if (theme === 'dark') {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }
}

// Utility functions
function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) {
        return 'Yesterday';
    } else if (diffDays < 7) {
        return `${diffDays} days ago`;
    } else {
        return date.toLocaleDateString();
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy to clipboard', 'error');
    });
}

// Form validation
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    return isValid;
}

function showFieldError(field, message) {
    const errorElement = field.parentNode.querySelector('.field-error');
    if (errorElement) {
        errorElement.textContent = message;
    } else {
        const error = document.createElement('div');
        error.className = 'field-error text-red-500 text-sm mt-1';
        error.textContent = message;
        field.parentNode.appendChild(error);
    }
    
    field.classList.add('border-red-500', 'focus:ring-red-500');
    field.classList.remove('border-gray-300', 'focus:ring-blue-500');
}

function clearFieldError(field) {
    const errorElement = field.parentNode.querySelector('.field-error');
    if (errorElement) {
        errorElement.remove();
    }
    
    field.classList.remove('border-red-500', 'focus:ring-red-500');
    field.classList.add('border-gray-300', 'focus:ring-blue-500');
}

// AJAX helpers
function makeRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    return fetch(url, mergedOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

// Export functions for global use
window.CodePlatform = {
    showToast,
    hideToast,
    openModal,
    closeModal,
    formatTime,
    formatDate,
    copyToClipboard,
    validateForm,
    makeRequest
};