/**
 * Main JavaScript functionality for the SDG Assessment Tool
 * Wrapped in IIFE to avoid global scope pollution
 */
(function() {
    // Store event handler references for potential cleanup
    const eventHandlers = {
        autoSave: null,
        formValidation: null
    };

    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        // Initialize CSRF token handling
        initCSRFTokenHandling();
        
        // Initialize auto-save functionality for assessment forms
        initAutoSave();
        
        // Initialize form validation
        initFormValidation();
        
        // Initialize Bootstrap tooltips
        initTooltips();
        
        // Initialize Bootstrap popovers
        initPopovers();
        
        // Mobile navigation improvements
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');
        const body = document.body;
        
        // Add class to body when mobile menu is open
        if (navbarToggler && navbarCollapse) {
            navbarToggler.addEventListener('click', function() {
                // Use a small delay to allow Bootstrap's collapse to process
                setTimeout(() => {
                    if (navbarCollapse.classList.contains('show')) {
                        body.classList.add('navbar-open');
                    } else {
                        body.classList.remove('navbar-open');
                    }
                }, 50);
            });
            
            // Listen for Bootstrap collapse events
            navbarCollapse.addEventListener('shown.bs.collapse', function() {
                body.classList.add('navbar-open');
            });
            
            navbarCollapse.addEventListener('hidden.bs.collapse', function() {
                body.classList.remove('navbar-open');
            });
        }
        
        // Close mobile menu when clicking on a nav link (better UX)
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link:not(.dropdown-toggle)');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth < 992 && navbarCollapse.classList.contains('show')) {
                    navbarToggler.click();
                }
            });
        });
        
        // Improve dropdown behavior on mobile
        const dropdownToggles = document.querySelectorAll('.navbar-nav .dropdown-toggle');
        dropdownToggles.forEach(toggle => {
            toggle.addEventListener('click', function(e) {
                if (window.innerWidth < 992) {
                    e.preventDefault();
                    const dropdownMenu = this.nextElementSibling;
                    if (dropdownMenu) {
                        dropdownMenu.classList.toggle('show');
                        this.setAttribute('aria-expanded', 
                            dropdownMenu.classList.contains('show') ? 'true' : 'false'
                        );
                    }
                }
            });
        });
    });

    /**
     * Initialize CSRF token handling
     */
    function initCSRFTokenHandling() {
        // Extract CSRF token from meta tag or form input
        refreshCSRFToken();
        
        // Set up periodic token refresh (every 15 minutes)
        setInterval(refreshCSRFToken, 15 * 60 * 1000);
        
        // Also refresh token when tabs become visible
        document.addEventListener('visibilitychange', function() {
            if (!document.hidden) {
                refreshCSRFToken();
            }
        });
    }
    
    /**
     * Refresh CSRF token from meta tag or existing form field
     * @returns {String} - Current CSRF token
     */
    function refreshCSRFToken() {
        // Try to get token from meta tag first
        let token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        
        // If no meta tag, try form input
        if (!token) {
            token = document.querySelector('input[name="csrf_token"]')?.value;
        }
        
        // If token found, update all forms with it
        if (token) {
            document.querySelectorAll('form').forEach(form => {
                let tokenInput = form.querySelector('input[name="csrf_token"]');
                if (!tokenInput) {
                    tokenInput = document.createElement('input');
                    tokenInput.type = 'hidden';
                    tokenInput.name = 'csrf_token';
                    form.appendChild(tokenInput);
                }
                tokenInput.value = token;
            });
        } else {
            console.warn('CSRF token not found in document');
        }
        
        return token;
    }

    /**
     * Initialize auto-save functionality for assessment forms
     */
    function initAutoSave() {
        const form = document.getElementById('sdg-assessment-form');
        if (!form) return;
        
        const formInputs = form.querySelectorAll('input, textarea, select');
        
        // Save form data to localStorage
        function saveFormData() {
            try {
                const formData = {};
                
                // Include CSRF token in saved data
                const csrfToken = refreshCSRFToken();
                if (csrfToken) {
                    formData.csrf_token = csrfToken;
                }
                
                formInputs.forEach(input => {
                    // Skip the csrf_token field - we already handled it
                    if (input.name === 'csrf_token') return;
                    
                    if (input.type === 'radio') {
                        if (input.checked) {
                            formData[input.name] = input.value;
                        }
                    } else if (input.type === 'checkbox') {
                        formData[input.name] = input.checked;
                    } else {
                        formData[input.name] = input.value;
                    }
                });
                
                // Save to localStorage with a unique key for this assessment page
                const pageKey = window.location.pathname;
                localStorage.setItem('sdg_assessment_' + pageKey, JSON.stringify({
                    timestamp: new Date().toISOString(),
                    data: formData
                }));
                
                // Show subtle save indicator
                showSaveIndicator();
            } catch (e) {
                console.error('LocalStorage write failed:', e);
                // Consider fallback to sessionStorage or warning the user
                showStorageError();
            }
        }
        
        // Store the handler reference for potential cleanup
        eventHandlers.autoSave = saveFormData;
        
        // Auto-save when inputs change
        formInputs.forEach(input => {
            input.addEventListener('change', eventHandlers.autoSave);
            if (input.tagName === 'TEXTAREA') {
                input.addEventListener('blur', eventHandlers.autoSave);
            }
        });
        
        // Load saved data if available
        function loadSavedData() {
            try {
                const pageKey = window.location.pathname;
                const savedData = localStorage.getItem('sdg_assessment_' + pageKey);
                
                if (savedData) {
                    const parsedData = JSON.parse(savedData);
                    
                    // Check if saved data is recent enough (within 24 hours)
                    const savedTime = new Date(parsedData.timestamp || new Date()).getTime();
                    const currentTime = new Date().getTime();
                    const maxAge = 24 * 60 * 60 * 1000; // 24 hours in milliseconds
                    
                    if (currentTime - savedTime <= maxAge) {
                        const formData = parsedData.data || parsedData; // Handle both formats
                        
                        // Populate form fields
                        Object.keys(formData).forEach(key => {
                            // Skip the CSRF token field - we'll refresh it separately
                            if (key === 'csrf_token') return;
                            
                            const inputs = form.querySelectorAll(`[name="${key}"]`);
                            
                            inputs.forEach(input => {
                                if (input.type === 'radio') {
                                    input.checked = (input.value === formData[key]);
                                } else if (input.type === 'checkbox') {
                                    input.checked = formData[key];
                                } else {
                                    input.value = formData[key];
                                }
                            });
                        });
                        
                        // Always refresh the CSRF token after loading data
                        refreshCSRFToken();
                        
                        // Show loaded indicator
                        showLoadedIndicator();
                    } else {
                        // Data is too old, remove it
                        localStorage.removeItem(pageKey);
                    }
                }
            } catch (e) {
                console.error('LocalStorage read failed:', e);
                showStorageError();
            }
        }
        
        // Load saved data when page loads
        loadSavedData();
        
        // Clear storage on successful form submission
        form.addEventListener('submit', function(event) {
            // Make sure CSRF token is fresh before submission
            refreshCSRFToken();
            
            // Only clear if form validation passes
            if (validateForm()) {
                try {
                    const pageKey = window.location.pathname;
                    localStorage.removeItem('sdg_assessment_' + pageKey);
                } catch (e) {
                    console.error('LocalStorage clear failed:', e);
                }
            } else {
                event.preventDefault();
            }
        });
    }

    /**
     * Initialize form validation
     */
    function initFormValidation() {
        const form = document.getElementById('sdg-assessment-form');
        if (!form) return;
        
        // Store the handler reference for potential cleanup
        eventHandlers.formValidation = function(event) {
            // Ensure CSRF token is present before validation
            const csrfToken = refreshCSRFToken();
            if (!csrfToken) {
                event.preventDefault();
                showCSRFError();
                return false;
            }
            
            let isValid = true;
            const requiredRadioGroups = new Set();
            
            // Collect all required radio button groups
            form.querySelectorAll('input[required]').forEach(input => {
                if (input.type === 'radio') {
                    requiredRadioGroups.add(input.name);
                }
            });
            
            // Check if all required radio groups have a selection
            requiredRadioGroups.forEach(groupName => {
                const checkedInGroup = form.querySelector(`input[name="${groupName}"]:checked`);
                if (!checkedInGroup) {
                    isValid = false;
                    // Find the group container and add error indication
                    const groupContainer = form.querySelector(`input[name="${groupName}"]`).closest('.rating-options');
                    if (groupContainer) {
                        groupContainer.classList.add('is-invalid');
                        groupContainer.classList.remove('is-valid');
                    }
                } else {
                    // Mark as valid
                    const groupContainer = form.querySelector(`input[name="${groupName}"]`).closest('.rating-options');
                    if (groupContainer) {
                        groupContainer.classList.remove('is-invalid');
                        groupContainer.classList.add('is-valid');
                    }
                }
            });
            
            // Check other required fields
            form.querySelectorAll('textarea[required], input[type="text"][required]').forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');
                    field.classList.remove('is-valid');
                } else {
                    field.classList.remove('is-invalid');
                    field.classList.add('is-valid');
                }
            });
            
            if (!isValid) {
                event.preventDefault();
                showValidationError();
            }
            
            return isValid;
        };
        
        form.addEventListener('submit', eventHandlers.formValidation);
        
        // Add real-time validation feedback
        form.querySelectorAll('input, textarea, select').forEach(field => {
            field.addEventListener('blur', function() {
                validateField(this);
            });
        });
    }
    
    /**
     * Validate a single field and update its visual state
     */
    function validateField(field) {
        if (field.hasAttribute('required')) {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                field.classList.remove('is-valid');
            } else {
                field.classList.remove('is-invalid');
                field.classList.add('is-valid');
            }
        }
    }
    
    /**
     * Validate the entire form
     */
    function validateForm() {
        const form = document.getElementById('sdg-assessment-form');
        if (!form) return true;
        
        // Ensure CSRF token is present before validation
        const csrfToken = refreshCSRFToken();
        if (!csrfToken) {
            showCSRFError();
            return false;
        }
        
        let isValid = true;
        const requiredRadioGroups = new Set();
        
        // Collect all required radio button groups
        form.querySelectorAll('input[required]').forEach(input => {
            if (input.type === 'radio') {
                requiredRadioGroups.add(input.name);
            }
        });
        
        // Check if all required radio groups have a selection
        requiredRadioGroups.forEach(groupName => {
            const checkedInGroup = form.querySelector(`input[name="${groupName}"]:checked`);
            if (!checkedInGroup) {
                isValid = false;
                // Find the group container and add error indication
                const groupContainer = form.querySelector(`input[name="${groupName}"]`).closest('.rating-options');
                if (groupContainer) {
                    groupContainer.classList.add('is-invalid');
                    groupContainer.classList.remove('is-valid');
                }
            } else {
                // Mark as valid
                const groupContainer = form.querySelector(`input[name="${groupName}"]`).closest('.rating-options');
                if (groupContainer) {
                    groupContainer.classList.remove('is-invalid');
                    groupContainer.classList.add('is-valid');
                }
            }
        });
        
        // Check other required fields
        form.querySelectorAll('textarea[required], input[type="text"][required]').forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('is-invalid');
                field.classList.remove('is-valid');
            } else {
                field.classList.remove('is-invalid');
                field.classList.add('is-valid');
            }
        });
        
        if (!isValid) {
            showValidationError();
        }
        
        return isValid;
    }
    
    /**
     * Initialize Bootstrap tooltips
     */
    function initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    /**
     * Initialize Bootstrap popovers
     */
    function initPopovers() {
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
    
    /**
     * Show a subtle save indicator
     */
    function showSaveIndicator() {
        // Create or get the indicator element
        let indicator = document.getElementById('save-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'save-indicator';
            indicator.className = 'save-indicator';
            indicator.innerHTML = '<i class="bi bi-check-circle-fill"></i> Saved';
            document.body.appendChild(indicator);
        }
        
        // Show the indicator
        indicator.classList.add('show');
        
        // Hide after 2 seconds
        setTimeout(() => {
            indicator.classList.remove('show');
        }, 2000);
    }
    
    /**
     * Show a loaded indicator
     */
    function showLoadedIndicator() {
        // Create or get the indicator element
        let indicator = document.getElementById('load-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'load-indicator';
            indicator.className = 'load-indicator';
            indicator.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Loaded saved data';
            document.body.appendChild(indicator);
        }
        
        // Show the indicator
        indicator.classList.add('show');
        
        // Hide after 2 seconds
        setTimeout(() => {
            indicator.classList.remove('show');
        }, 2000);
    }
    
    /**
     * Show a storage error message
     */
    function showStorageError() {
        // Create or get the error element
        let error = document.getElementById('storage-error');
        if (!error) {
            error = document.createElement('div');
            error.id = 'storage-error';
            error.className = 'alert alert-warning alert-dismissible fade show';
            error.innerHTML = `
                <strong>Storage Error:</strong> Unable to save form data locally. Your progress may not be saved if you leave the page.
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            document.querySelector('.container').prepend(error);
        }
    }
    
    /**
     * Show a validation error message
     */
    function showValidationError() {
        // Create or get the error element
        let error = document.getElementById('validation-error');
        if (!error) {
            error = document.createElement('div');
            error.id = 'validation-error';
            error.className = 'alert alert-danger alert-dismissible fade show';
            error.innerHTML = `
                <strong>Validation Error:</strong> Please complete all required fields before proceeding.
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            document.querySelector('.container').prepend(error);
        } else {
            error.classList.add('show');
        }
    }
    
    /**
     * Show a CSRF token error message
     */
    function showCSRFError() {
        // Create or get the error element
        let error = document.getElementById('csrf-error');
        if (!error) {
            error = document.createElement('div');
            error.id = 'csrf-error';
            error.className = 'alert alert-danger alert-dismissible fade show';
            error.innerHTML = `
                <strong>Security Error:</strong> CSRF token missing or invalid. Please refresh the page and try again.
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            document.querySelector('.container').prepend(error);
        } else {
            error.classList.add('show');
        }
    }
    
    // Add CSS for indicators
    const style = document.createElement('style');
    style.textContent = `
        .save-indicator, .load-indicator {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: rgba(40, 167, 69, 0.9);
            color: white;
            padding: 10px 15px;
            border-radius: 4px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            z-index: 9999;
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.3s, transform 0.3s;
        }
        
        .save-indicator.show, .load-indicator.show {
            opacity: 1;
            transform: translateY(0);
        }
        
        .load-indicator {
            background-color: rgba(13, 110, 253, 0.9);
        }
    `;
    document.head.appendChild(style);
    
    // Expose necessary functions to window for potential use by other scripts
    window.SDGAssessment = {
        validateForm: validateForm,
        validateField: validateField,
        refreshCSRFToken: refreshCSRFToken
    };

    // Utility function for responsive navigation
    function handleResponsiveNav() {
        const navbarCollapse = document.querySelector('.navbar-collapse');
        const body = document.body;
        
        // Close mobile menu when resizing to desktop
        if (window.innerWidth >= 992) {
            if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                navbarCollapse.classList.remove('show');
            }
            body.classList.remove('navbar-open');
        }
    }

    // Handle window resize
    window.addEventListener('resize', handleResponsiveNav);
})();
