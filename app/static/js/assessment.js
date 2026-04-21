/**
 * Assessment-specific JavaScript functionality
 * Wrapped in IIFE to avoid global scope pollution
 */
(function() {
    // Store event handler references for potential cleanup
    const eventHandlers = {
        evidenceFields: [],
        tooltips: [],
        evidenceQualityMeter: []
    };

    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        // Initialize character counters for evidence fields
        initEvidenceFields();
        
        // Initialize tooltips
        initTooltips();
        
        // Initialize evidence quality meter
        initEvidenceQualityMeter();
    });

    /**
     * Initialize evidence text fields with character counting
     */
    function initEvidenceFields() {
        const evidenceFields = document.querySelectorAll('.evidence-field');
        
        evidenceFields.forEach(field => {
            const id = field.getAttribute('data-id');
            const charCount = document.getElementById(`charCount_${id}`);
            const qualityMeter = document.getElementById(`quality_${id}`);
            
            // Create handler function
            const handleInput = function() {
                const count = this.value.length;
                const maxLength = this.getAttribute('maxlength');
                
                // Update character counter
                if (charCount) {
                    charCount.textContent = count;
                }
                
                // Update evidence quality meter
                if (qualityMeter) {
                    updateEvidenceQualityMeter(qualityMeter, count, maxLength);
                }
            };
            
            // Store handler reference
            eventHandlers.evidenceFields.push({
                field: field,
                handler: handleInput
            });
            
            // Add event listener
            field.addEventListener('input', handleInput);
            
            // Trigger input event to initialize counters
            field.dispatchEvent(new Event('input'));
        });
    }

    /**
     * Update the evidence quality meter based on character count
     */
    function updateEvidenceQualityMeter(meterElement, count, maxLength) {
        const percentage = Math.min(100, (count / maxLength) * 100);
        const levelElement = meterElement.querySelector('.evidence-level');
        const textElement = meterElement.querySelector('.evidence-text');
        
        if (levelElement) {
            levelElement.style.width = `${percentage}%`;
        }
        
        if (textElement) {
            let qualityText = 'Not started';
            
            if (count > 0) {
                if (count < 50) {
                    qualityText = 'Minimal evidence';
                } else if (count < 150) {
                    qualityText = 'Basic evidence';
                } else if (count < 300) {
                    qualityText = 'Good evidence';
                } else if (count < 450) {
                    qualityText = 'Strong evidence';
                } else {
                    qualityText = 'Comprehensive evidence';
                }
            }
            
            textElement.textContent = `Evidence strength: ${qualityText}`;
        }
    }

    /**
     * Initialize Bootstrap tooltips
     */
    function initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.forEach(function (tooltipTriggerEl) {
            const tooltip = new bootstrap.Tooltip(tooltipTriggerEl);
            eventHandlers.tooltips.push(tooltip);
        });
    }

    /**
     * Initialize evidence quality meter
     */
    function initEvidenceQualityMeter() {
        const meters = document.querySelectorAll('.evidence-quality');
        
        meters.forEach(meter => {
            const id = meter.getAttribute('id').split('_')[1];
            const field = document.getElementById(`notes_${id}`);
            
            if (field) {
                const count = field.value.length;
                const maxLength = field.getAttribute('maxlength');
                
                updateEvidenceQualityMeter(meter, count, maxLength);
                
                // Create handler function
                const handleInput = function() {
                    const count = this.value.length;
                    const maxLength = this.getAttribute('maxlength');
                    updateEvidenceQualityMeter(meter, count, maxLength);
                };
                
                // Store handler reference
                eventHandlers.evidenceQualityMeter.push({
                    field: field,
                    handler: handleInput
                });
                
                // Add event listener
                field.addEventListener('input', handleInput);
            }
        });
    }

    /**
     * Handle form submission validation
     */
    function validateAssessmentForm() {
        // Use the validation function from main.js if available
        if (window.SDGAssessment && typeof window.SDGAssessment.validateForm === 'function') {
            return window.SDGAssessment.validateForm();
        }
        
        // Fallback validation if main.js is not loaded
        const form = document.getElementById('sdg-assessment-form');
        if (!form) return true;
        
        let isValid = true;
        const requiredFields = document.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value) {
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
     * Toggle accordion sections
     */
    function toggleAccordion(id) {
        const accordion = document.getElementById(id);
        if (accordion) {
            const bsAccordion = new bootstrap.Collapse(accordion, {
                toggle: true
            });
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
    
    // Expose necessary functions to window for potential use by other scripts
    window.SDGAssessmentUtils = {
        validateAssessmentForm: validateAssessmentForm,
        toggleAccordion: toggleAccordion
    };
})(); 