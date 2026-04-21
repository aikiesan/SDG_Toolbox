/**
 * SDG Assessment Questionnaire JavaScript functionality
 * Handles form interactions, validation, auto-save and scoring calculations
 */

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize auto-save
    initAutoSave();
    
    // Update progress bar
    updateProgress();
    
    // Set up form submission
    setupFormSubmission();
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});

/**
 * Initialize auto-save functionality
 */
function initAutoSave() {
    // Auto-save on input changes
    const formInputs = document.querySelectorAll('input, textarea, select');
    
    formInputs.forEach(input => {
        input.addEventListener('change', debounce(saveFormData, 2000));
        
        // For text inputs, also listen for input events
        if (input.tagName === 'TEXTAREA') {
            input.addEventListener('input', debounce(saveFormData, 3000));
        }
    });
    
    // Manual save button
    const saveButton = document.getElementById('save-draft');
    if (saveButton) {
        saveButton.addEventListener('click', function() {
            saveFormData(true);
        });
    }
}

/**
 * Create a debounce function to prevent excessive calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} - Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

/**
 * Save form data to the server
 * @param {boolean} showMessage - Whether to show a success message
 */
function saveFormData(showMessage = false) {
    const form = document.getElementById('sdg-assessment-form');
    if (!form) return;
    
    const formData = new FormData(form);
    
    // Add specific action
    formData.append('action', 'save_draft');
    
    // Get the URL for saving drafts
    const url = form.action.replace('save_assessment', 'save_draft');
    
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (showMessage) {
                showSaveIndicator('Draft saved successfully');
            }
            updateProgress();
        } else {
            showSaveIndicator('Error saving draft', 'error');
            console.error('Server error:', data.message || 'Unknown error');
        }
    })
    .catch(error => {
        console.error('Error saving form data:', error);
        showSaveIndicator('Error saving draft', 'error');
    });
}

/**
 * Update progress indicator based on completed questions
 */
function updateProgress() {
    // Count completed questions
    const totalQuestions = document.querySelectorAll('.question-card').length;
    let completedQuestions = 0;
    
    // Radio button questions
    const radioGroups = document.querySelectorAll('input[type="radio"]:checked');
    const radioGroupNames = new Set();
    radioGroups.forEach(radio => {
        radioGroupNames.add(radio.name);
    });
    completedQuestions += radioGroupNames.size;
    
    // Text inputs
    const textInputs = document.querySelectorAll('textarea[required]');
    textInputs.forEach(input => {
        if (input.value.trim().length > 0) {
            completedQuestions++;
        }
    });
    
    // Checklist questions (count if at least one option is checked)
    const checklistGroups = document.querySelectorAll('input[type="checkbox"]');
    const checklistNames = new Set();
    checklistGroups.forEach(checkbox => {
        if (checkbox.checked) {
            const questionId = checkbox.name.split('_')[1];
            checklistNames.add(questionId);
        }
    });
    completedQuestions += checklistNames.size;
    
    // Update progress bar
    const percentage = Math.round((completedQuestions / totalQuestions) * 100);
    const progressBar = document.querySelector('.progress-bar');
    if (!progressBar) return;
    
    progressBar.style.width = `${percentage}%`;
    progressBar.setAttribute('aria-valuenow', percentage);
    progressBar.textContent = `${percentage}%`;
    
    // Update completion text
    const completionText = document.getElementById('completion-text');
    if (completionText) {
        completionText.textContent = `${completedQuestions} of ${totalQuestions} questions completed`;
    }
    
    // Update progress bar color based on completion
    if (percentage < 25) {
        progressBar.className = 'progress-bar bg-danger';
    } else if (percentage < 50) {
        progressBar.className = 'progress-bar bg-warning';
    } else if (percentage < 100) {
        progressBar.className = 'progress-bar bg-info';
    } else {
        progressBar.className = 'progress-bar bg-success';
    }
}

/**
 * Set up form submission handler
 */
function setupFormSubmission() {
    const form = document.getElementById('sdg-assessment-form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate the form
        if (validateForm()) {
            // Show loading indicator
            showSaveIndicator('Submitting assessment...', 'info');
            
            // Submit the form
            const formData = new FormData(form);
            formData.append('action', 'submit');
            
            // Get CSRF token from meta tag or hidden input
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || 
                            document.querySelector('input[name="csrf_token"]')?.value;
            
            // Use the form's action URL instead of constructing it
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                },
                credentials: 'same-origin'  // Include cookies
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = data.redirect_url;
                } else {
                    showSaveIndicator('Error submitting assessment', 'error');
                    console.error('Server error:', data.message || 'Unknown error');
                }
            })
            .catch(error => {
                console.error('Error submitting form:', error);
                showSaveIndicator('Error submitting assessment', 'error');
            });
        } else {
            showValidationError();
        }
    });
}

/**
 * Validate the form before submission
 * @returns {boolean} - Whether the form is valid
 */
function validateForm() {
    const form = document.getElementById('sdg-assessment-form');
    let isValid = true;
    
    // Reset previous validation indicators
    document.querySelectorAll('.card.border-danger').forEach(card => {
        card.classList.remove('border-danger');
    });
    document.querySelectorAll('.is-invalid').forEach(field => {
        field.classList.remove('is-invalid');
    });
    
    // Validate required fields
    const requiredFields = form.querySelectorAll('[required]');
    const validatedGroups = new Set();
    
    requiredFields.forEach(field => {
        if (field.type === 'radio') {
            const name = field.name;
            // Only validate each radio group once
            if (!validatedGroups.has(name)) {
                validatedGroups.add(name);
                const checked = form.querySelector(`input[name="${name}"]:checked`);
                if (!checked) {
                    isValid = false;
                    field.closest('.card').classList.add('border-danger');
                }
            }
        } else if (!field.value.trim()) {
            isValid = false;
            field.classList.add('is-invalid');
            field.closest('.card').classList.add('border-danger');
        }
    });
    
    return isValid;
}

/**
 * Show validation error message
 */
function showValidationError() {
    // Remove any existing error messages
    document.querySelectorAll('.validation-error').forEach(el => el.remove());
    
    // Create new error message
    const errorElement = document.createElement('div');
    errorElement.className = 'alert alert-danger alert-dismissible fade show validation-error';
    errorElement.innerHTML = `
        <strong>Error:</strong> Please complete all required questions before submitting.
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Find first incomplete question
    const firstIncomplete = document.querySelector('.card.border-danger');
    if (firstIncomplete) {
        firstIncomplete.querySelector('.card-body').prepend(errorElement);
        firstIncomplete.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else {
        document.querySelector('.container').prepend(errorElement);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

/**
 * Show a save/error indicator message
 * @param {string} message - Message to display
 * @param {string} type - Indicator type (success, error, info)
 */
function showSaveIndicator(message = 'Saved', type = 'success') {
    // Create or get the indicator element
    let indicator = document.getElementById('save-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'save-indicator';
        indicator.className = 'save-indicator';
        document.body.appendChild(indicator);
        
        // Add styles for the indicator
        if (!document.getElementById('save-indicator-style')) {
            const style = document.createElement('style');
            style.id = 'save-indicator-style';
            style.textContent = `
                .save-indicator {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    padding: 10px 15px;
                    border-radius: 4px;
                    color: white;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                    z-index: 9999;
                    opacity: 0;
                    transform: translateY(20px);
                    transition: opacity 0.3s, transform 0.3s;
                }
                
                .save-indicator.show {
                    opacity: 1;
                    transform: translateY(0);
                }
                
                .save-indicator.success {
                    background-color: rgba(40, 167, 69, 0.9);
                }
                
                .save-indicator.error {
                    background-color: rgba(220, 53, 69, 0.9);
                }
                
                .save-indicator.info {
                    background-color: rgba(13, 110, 253, 0.9);
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    // Set appropriate styling based on type
    indicator.className = 'save-indicator';
    indicator.classList.add(type);
    
    // Set message
    indicator.textContent = message;
    
    // Show indicator
    indicator.classList.add('show');
    
    // Hide after 3 seconds
    setTimeout(() => {
        indicator.classList.remove('show');
    }, 3000);
}
