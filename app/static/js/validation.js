/**
 * Form validation utilities
 */

// Main validation function
function validateForm(formId, validationRules) {
  const form = document.getElementById(formId);
  if (!form) return false;
  
  let isValid = true;
  const errors = {};
  
  // Clear previous error messages
  clearValidationErrors(form);
  
  // Validate each field
  for (const fieldName in validationRules) {
    const field = form.elements[fieldName];
    if (!field) continue;
    
    const rules = validationRules[fieldName];
    const fieldValue = field.value.trim();
    
    // Required validation
    if (rules.required && !fieldValue) {
      isValid = false;
      errors[fieldName] = 'This field is required';
      continue;
    }
    
    // Min length validation
    if (rules.minLength && fieldValue.length < rules.minLength) {
      isValid = false;
      errors[fieldName] = `Minimum length is ${rules.minLength} characters`;
      continue;
    }
    
    // Number validation
    if (rules.number && fieldValue && !/^-?\d*\.?\d+$/.test(fieldValue)) {
      isValid = false;
      errors[fieldName] = 'Please enter a valid number';
      continue;
    }
    
    // Min/max value validation for numbers
    if (rules.number && fieldValue) {
      const numValue = parseFloat(fieldValue);
      if (rules.min !== undefined && numValue < rules.min) {
        isValid = false;
        errors[fieldName] = `Minimum value is ${rules.min}`;
        continue;
      }
      if (rules.max !== undefined && numValue > rules.max) {
        isValid = false;
        errors[fieldName] = `Maximum value is ${rules.max}`;
        continue;
      }
    }
    
    // Custom validation
    if (rules.custom && !rules.custom.validator(fieldValue)) {
      isValid = false;
      errors[fieldName] = rules.custom.message;
      continue;
    }
  }
  
  // Display errors if any
  if (!isValid) {
    displayValidationErrors(form, errors);
  }
  
  return isValid;
}

// Display validation errors next to form fields
function displayValidationErrors(form, errors) {
  for (const fieldName in errors) {
    const field = form.elements[fieldName];
    const errorMessage = errors[fieldName];
    
    // Add error class to input
    field.classList.add('is-invalid');
    
    // Create error message element
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = errorMessage;
    
    // Insert after the field
    field.parentNode.insertBefore(errorDiv, field.nextSibling);
  }
}

// Clear all validation errors
function clearValidationErrors(form) {
  // Remove error classes
  const invalidFields = form.querySelectorAll('.is-invalid');
  invalidFields.forEach(field => field.classList.remove('is-invalid'));
  
  // Remove error messages
  const errorMessages = form.querySelectorAll('.invalid-feedback');
  errorMessages.forEach(el => el.remove());
}

// Auto-initialize validation on forms with data-validate attribute
document.addEventListener('DOMContentLoaded', function() {
  const forms = document.querySelectorAll('form[data-validate]');
  
  forms.forEach(form => {
    form.addEventListener('submit', function(event) {
      // Get validation rules from data attribute
      const rulesAttribute = form.getAttribute('data-validation-rules');
      if (!rulesAttribute) return;
      
      try {
        const validationRules = JSON.parse(rulesAttribute);
        if (!validateForm(form.id, validationRules)) {
          event.preventDefault();
        }
      } catch (e) {
        console.error('Error parsing validation rules:', e);
      }
    });
  });
});

// Project form validation
function validateProjectForm() {
  const validationRules = {
    'name': { required: true, minLength: 3 },
    'size_sqm': { number: true, min: 0 },
    'project_type': { required: true }
  };
  
  return validateForm('project-form', validationRules);
}

// Enhanced Assessment Section Validation
// Improved section validation for assessment form
function validateAssessmentSection(sectionNumber) {
    const section = document.querySelector(`.form-section[data-section="${sectionNumber}"]`);
    if (!section) return true; // Or false, depending on desired behavior if section not found

    let isValid = true;

    // Clear previous errors specifically within this section
    const errorMessages = section.querySelectorAll('.validation-error');
    errorMessages.forEach(el => el.remove()); // Remove old error messages

    const questions = section.querySelectorAll('.question');
    questions.forEach(question => question.classList.remove('invalid')); // Remove invalid styling

    // --- Begin validation logic ---
    questions.forEach(question => {
      const isRadioQuestion = question.querySelector('.radio-indicator') !== null;
      const isCheckboxQuestion = question.querySelector('.checkbox-indicator') !== null;
      
      if (isRadioQuestion) {
        // --- Radio validation logic (already fixed) ---
        const firstRadio = question.querySelector('input[type="radio"]');
        if (firstRadio) {
            const radioGroupName = firstRadio.name;
            const radiosInGroup = question.querySelectorAll(`input[type="radio"][name="${radioGroupName}"]`);
            const selected = Array.from(radiosInGroup).some(radio => radio.checked);
    
            if (!selected) {
                isValid = false;
                question.classList.add('invalid');
    
                if (!question.querySelector('.validation-error')) {
                     const errorMsg = document.createElement('div');
                     errorMsg.className = 'validation-error';
                     errorMsg.textContent = 'Please select one option';
                     const optionsDiv = question.querySelector('.options');
                     if (optionsDiv) {
                         optionsDiv.insertAdjacentElement('afterend', errorMsg);
                     } else {
                         question.appendChild(errorMsg);
                     }
                }
            }
        } else {
             console.warn("Could not find any radio buttons in question:", question);
        }
      }
      
      if (isCheckboxQuestion) {
        // --- Checkbox validation logic (already fixed) ---
        const firstCheckbox = question.querySelector('input[type="checkbox"]');
        if (firstCheckbox) {
            const checkboxGroupName = firstCheckbox.name;
            const checkboxesInGroup = question.querySelectorAll(`input[type="checkbox"][name="${checkboxGroupName}"]`);
            const selected = Array.from(checkboxesInGroup).some(checkbox => checkbox.checked);
    
            if (!selected) {
                isValid = false;
                question.classList.add('invalid');
    
                 if (!question.querySelector('.validation-error')) {
                    const errorMsg = document.createElement('div');
                    errorMsg.className = 'validation-error';
                    errorMsg.textContent = 'Please select at least one option';
                     const optionsDiv = question.querySelector('.options');
                     if (optionsDiv) {
                         optionsDiv.insertAdjacentElement('afterend', errorMsg);
                     } else {
                         question.appendChild(errorMsg);
                     }
                }
            }
        } else {
             console.warn("Could not find any checkboxes in question:", question);
        }
      }
    });
    // --- End validation logic ---

    // If validation failed, scroll to the first error
    if (!isValid) {
      const firstError = section.querySelector('.question.invalid');
      if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  
    return isValid;
}

// Export all functions
window.FormValidation = {
  validateForm,
  validateProjectForm,
  validateAssessmentSection,
  clearValidationErrors
};