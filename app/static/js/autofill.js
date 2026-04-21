// Autofill the questionnaire randomly for testing
(function() {
    function randomInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    function autofillQuestions() {
        // Handle radio buttons
        document.querySelectorAll('.question').forEach(question => {
            // Radio
            const radios = question.querySelectorAll('input[type="radio"]');
            if (radios.length > 0) {
                const group = {};
                radios.forEach(radio => {
                    group[radio.name] = group[radio.name] || [];
                    group[radio.name].push(radio);
                });
                Object.values(group).forEach(radioGroup => {
                    // Uncheck all first
                    radioGroup.forEach(r => r.checked = false);
                    // Randomly select one
                    const idx = randomInt(0, radioGroup.length - 1);
                    radioGroup[idx].checked = true;
                });
            }
            // Checkbox
            const checkboxes = question.querySelectorAll('input[type="checkbox"]');
            if (checkboxes.length > 0) {
                // For each group of checkboxes with the same name, randomly check 1 or more
                const group = {};
                checkboxes.forEach(checkbox => {
                    group[checkbox.name] = group[checkbox.name] || [];
                    group[checkbox.name].push(checkbox);
                });
                Object.values(group).forEach(cbGroup => {
                    // Uncheck all first
                    cbGroup.forEach(cb => cb.checked = false);
                    // Randomly decide how many to check (at least 1)
                    const numToCheck = randomInt(1, cbGroup.length);
                    const shuffled = cbGroup.sort(() => 0.5 - Math.random());
                    for (let i = 0; i < numToCheck; i++) {
                        shuffled[i].checked = true;
                    }
                });
            }
            // Select dropdowns
            const selects = question.querySelectorAll('select');
            selects.forEach(select => {
                if (select.options.length > 1) {
                    // Avoid the first option if it's a placeholder
                    const startIdx = select.options[0].value ? 0 : 1;
                    const idx = randomInt(startIdx, select.options.length - 1);
                    select.selectedIndex = idx;
                }
            });
            // Textareas (optional, fill with 'Test' or random string)
            const textareas = question.querySelectorAll('textarea');
            textareas.forEach(textarea => {
                textarea.value = 'Test ' + randomInt(1, 1000);
            });
            // Text inputs (optional, fill with 'Test' or random string)
            const textinputs = question.querySelectorAll('input[type="text"]');
            textinputs.forEach(input => {
                input.value = 'Test ' + randomInt(1, 1000);
            });
        });
    }

    window.autofillQuestions = autofillQuestions;
})();
