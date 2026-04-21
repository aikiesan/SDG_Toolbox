// js/assessment/ui_assessment.js
// Handles UI updates, interactions, and element references

// Note: DOM element references are defined in main_assessment.js after DOMContentLoaded

/**
 * Updates all elements in the DOM that have a data-translate-key attribute
 * using the currently selected language in the translations object.
 */
function updateUIForLanguage() {
    if (typeof translations === 'undefined' || !translations[currentLanguage]) {
        console.warn(`[i18n] Translations not loaded or language ${currentLanguage} not found`);
        return;
    }

    const langData = translations[currentLanguage];
    console.log(`[i18n] Updating UI for language: ${currentLanguage}`);

    // Update all elements with data-translate-key
    document.querySelectorAll('[data-translate-key]').forEach(el => {
        const key = el.getAttribute('data-translate-key');
        let translatedText = langData[key];

        // Fallback to English if key is missing in current language
        if (!translatedText && currentLanguage !== 'en') {
            translatedText = translations['en'][key];
        }

        if (translatedText) {
            // Special handling for different element types
            if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                if (el.placeholder !== undefined && el.hasAttribute('placeholder')) {
                    el.placeholder = translatedText;
                } else {
                    el.value = translatedText;
                }
            } else if (el.tagName === 'OPTGROUP' || el.tagName === 'OPTION') {
                el.label = translatedText;
                if (el.tagName === 'OPTION') el.textContent = translatedText;
            } else {
                // For standard elements (p, h2, span, etc.)
                // We use innerHTML to support potentially formatted text from the translations
                el.innerHTML = translatedText;
            }
        }
    });

    // Update dynamic navigation buttons that might have numbers in them
    updateNavigationButtonText();
    
    // Update progress text
    if (typeof updateProgress === 'function') updateProgress();

    // Update SDG Indicator buttons titles
    if (typeof updateIndicatorButtons === 'function') updateIndicatorButtons();
    
    console.log(`[i18n] UI update complete for ${currentLanguage}`);
}

function generateIndicatorButtons() {
    if (!indicatorContainer) return;
    indicatorContainer.innerHTML = ''; // Clear existing
    for (let i = 1; i <= TOTAL_SDGS; i++) {
        const btn = document.createElement('button');
        btn.type = 'button';
        const info = SDG_INFO[i] || {};
        const bgColor = info.color ? info.color + '33' : 'bg-gray-300';
        const borderColor = info.color || 'border-gray-400';
        btn.className = `sdg-indicator-btn w-8 h-8 rounded-full text-xs font-bold border-2 transition duration-150 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-1`;
        btn.style.backgroundColor = bgColor;
        btn.style.borderColor = borderColor;
        btn.style.color = info.color || 'black';
        btn.textContent = i;
        btn.dataset.sdg = `sdg-${i}`;
        // Update title using translated text - relies on translations being loaded
        const titleKey = `sdg${i}_title`;
        btn.title = (typeof translations !== 'undefined' && translations[currentLanguage])
                    ? translations[currentLanguage][titleKey]
                    : (info.name || `SDG ${i}`); // Fallback chain
        btn.addEventListener('click', () => {
            // Need access to saveCurrentSectionData & showSection (defined in main.js)
            if (typeof saveCurrentSectionData === 'function') saveCurrentSectionData();
            if (typeof showSection === 'function') showSection(`sdg-${i}`);
        });
        indicatorContainer.appendChild(btn);
    }
    updateIndicatorButtons(); // Set initial styles
}

function setupEventListeners() {
     if (!sectionsContainer) return;

    // Navigation Buttons (Next/Prev) - Event delegation on the container
    sectionsContainer.addEventListener('click', (event) => {
        const nextButton = event.target.closest('.next-btn');
        const prevButton = event.target.closest('.prev-btn');

        if (nextButton) {
            const nextId = nextButton.dataset.next;
            if (nextId) {
                // Need access to save/show functions from main.js
                if (typeof saveCurrentSectionData === 'function') saveCurrentSectionData();
                if (typeof showSection === 'function') showSection(nextId);
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        } else if (prevButton) {
            const prevId = prevButton.dataset.prev;
            if (prevId) {
                 if (typeof saveCurrentSectionData === 'function') saveCurrentSectionData();
                 if (typeof showSection === 'function') showSection(prevId);
                 window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        }
    });

    // Submit Button - Handled in main_assessment.js as it triggers core logic

    // Results Buttons
    const printButton = document.getElementById('print-results');
    if (printButton) printButton.addEventListener('click', () => window.print());

    const downloadButton = document.getElementById('download-results');
    if (downloadButton) downloadButton.addEventListener('click', generatePDF); // Call local PDF func

    const restartButton = document.getElementById('restart-assessment');
    if (restartButton) restartButton.addEventListener('click', () => location.reload());
}


function showSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (!section) {
        console.error(`Section with ID ${sectionId} not found.`);
        return;
    }

    // Get all sections
    const allSections = document.querySelectorAll('.sdg-section');
    if (!allSections || allSections.length === 0) {
        console.error("No sections found with class 'sdg-section'");
        return;
    }

    console.log(`Showing section: ${sectionId}`);
    
    // Update global state
    currentSectionId = sectionId;
    visitedSections.add(sectionId);

    // Hide all sections except the target one
    allSections.forEach(s => {
        if (s.id === sectionId) {
            s.classList.remove('hidden');
            // Ensure the section is visible
            s.style.display = '';
            // Scroll to top of section
            s.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            s.classList.add('hidden');
        }
    });

    // Update UI elements
    if (typeof updateProgress === 'function') {
        updateProgress();
    }
    if (typeof updateIndicatorButtons === 'function') {
        updateIndicatorButtons();
    }
    if (typeof updateNavigationButtonText === 'function') {
        updateNavigationButtonText();
    }
}


function updateProgress() {
    // Safety check: only update if the elements exist (Standard page uses different IDs)
    if (typeof progressBar === 'undefined' || !progressBar || typeof progressText === 'undefined' || !progressText) {
        // Log quietly so it doesn't clutter console if it's expected
        return;
    }
    
    // Ensure currentSectionId is defined
    const sectionId = (typeof currentSectionId !== 'undefined') ? currentSectionId : 'sdg-1';
    
    // Expert Assessment uses sdg-X IDs, Standard might use different logic
    const sectionMatch = sectionId.match(/sdg-(\d+)/);
    const currentSdgNumber = sectionMatch ? parseInt(sectionMatch[1]) : (parseInt(sectionId) || 1);
    
    // Check if TOTAL_SDGS exists (from main_assessment.js)
    const total = (typeof TOTAL_SDGS !== 'undefined') ? TOTAL_SDGS : 7; // Fallback to 7 for Standard
    const progressPercentage = (currentSdgNumber / total) * 100;

    progressBar.style.width = `${progressPercentage}%`;
    // Update progress text using translation key
    progressText.textContent = (typeof translations !== 'undefined' && translations[currentLanguage])
                                ? (translations[currentLanguage]['progress_status'] || 'SDG {current} of {total}')
                                    .replace('{current}', currentSdgNumber)
                                    .replace('{total}', total)
                                : `SDG ${currentSdgNumber} of ${total}`; // Fallback
}

function updateIndicatorButtons() {
     if (typeof indicatorContainer === 'undefined' || !indicatorContainer) return;
    const buttons = indicatorContainer.querySelectorAll('.sdg-indicator-btn');
    buttons.forEach(btn => {
        const sdgId = btn.dataset.sdg;
        btn.classList.remove('active', 'visited');
        const sdgNum = parseInt(sdgId.split('-')[1]);
        
        // Ensure SDG_INFO exists
        const info = (typeof SDG_INFO !== 'undefined' && SDG_INFO[sdgNum]) ? SDG_INFO[sdgNum] : {};
        const baseColor = info.color || '#9CA3AF';
        const lightBg = baseColor + '33';
        const darkText = baseColor;

        btn.style.backgroundColor = lightBg;
        btn.style.borderColor = baseColor;
        btn.style.color = darkText;
        // Update title using translated text
        const titleKey = `sdg${sdgNum}_title`;
        btn.title = (typeof translations !== 'undefined' && translations[currentLanguage])
                     ? translations[currentLanguage][titleKey]
                     : (info.name || `SDG ${sdgNum}`); // Fallback chain


        if (sdgId === currentSectionId) { // Assumes currentSectionId is accessible
            btn.classList.add('active');
            btn.style.backgroundColor = info.color || '#10B981';
            btn.style.borderColor = info.color || '#047857';
            btn.style.color = 'white';
            btn.style.fontWeight = 'bold';
            btn.classList.add('ring-2', 'ring-offset-1');
            btn.style.ringColor = info.color || '#10B981';
        } else if (visitedSections && visitedSections.has(sdgId)) { // Assumes visitedSections is accessible
            btn.classList.add('visited');
            const visitedBg = baseColor + '66';
            btn.style.backgroundColor = visitedBg;
            btn.style.borderColor = baseColor;
            btn.style.color = darkText;
            btn.style.fontWeight = 'normal';
            btn.classList.remove('ring-2', 'ring-offset-1');
        } else {
            btn.style.fontWeight = 'normal';
            btn.classList.remove('ring-2', 'ring-offset-1');
        }
    });
}

function updateNavigationButtonText() {
    document.querySelectorAll('.next-btn span[data-translate-key="continue_button"]').forEach(span => {
        const currentNum = parseInt(currentSectionId.split('-')[1] || '0');
        const nextNum = currentNum + 1;
        let text = '';
         if (nextNum <= TOTAL_SDGS && typeof translations !== 'undefined' && translations[currentLanguage]) {
            text = (translations[currentLanguage]['continue_button'] || 'Continue to SDG {next}').replace('{next}', nextNum);
         }
         span.textContent = text;
    });
    document.querySelectorAll('.prev-btn span[data-translate-key="back_button"]').forEach(span => {
        const currentNum = parseInt(currentSectionId.split('-')[1] || '0');
        const prevNum = currentNum - 1;
        let text = '';
         if (prevNum >= 1 && typeof translations !== 'undefined' && translations[currentLanguage]) {
            text = (translations[currentLanguage]['back_button'] || 'Back to SDG {prev}').replace('{prev}', prevNum);
         }
         span.textContent = text;
    });
}

function displayResults(scores) {
    // Hide form, show results
    if (form) form.classList.add('hidden');
    if (resultsSection) resultsSection.classList.remove('hidden');
    // Hide progress bar container
    document.querySelector('.sticky.top-\\[calc\\(4rem\\+1\\.25rem\\)\\]')?.classList.add('hidden');

    // --- Render Charts (call functions from charting_assessment.js) ---
    if (typeof renderRadarChart === 'function') renderRadarChart(scores);
    if (typeof renderBarChart === 'function') renderBarChart(scores);

    // --- Populate Detailed Breakdown ---
    populateDetailedBreakdown(scores);

     // Scroll to results
     if (resultsSection) resultsSection.scrollIntoView({ behavior: 'smooth' });
     console.log("Results displayed.");
}

function populateDetailedBreakdown(scores) {
    console.log('[ui] Entered populateDetailedBreakdown. Data:', scores);
    
    // Validate scores data
    if (!scores || !Array.isArray(scores)) {
        console.error('[ui] Invalid scores data:', scores);
        return;
    }
    
    if (scores.length === 0) {
        console.warn('[ui] No scores data provided');
        return;
    }
    
    // Get the container element *inside* the function
    const breakdownContainer = document.getElementById('sdg-breakdown-details'); // Use a local variable

    console.log('[ui] SDG Breakdown container:', breakdownContainer); // Log the local variable
    if (!breakdownContainer) { // Check the local variable
        console.error('[ui] SDG Breakdown container element with ID "sdg-breakdown-details" not found.');
        return;
    }
    breakdownContainer.innerHTML = ''; // Clear previous results

    console.log(`[ui] Processing ${scores.length} SDG scores`);
    scores.forEach((sdg, index) => {
        console.log(`[ui] Processing SDG ${index + 1}:`, sdg);
        const score = sdg.total_score;
        const performance = getPerformanceLevelDetails(score); // Assumes this helper is OK

        const item = document.createElement('div');
        // Apply consistent styling - using Tailwind classes from your example
        item.className = 'flex items-center justify-between p-3 md:p-4 border border-gray-200 rounded-lg bg-white hover:bg-gray-50 transition-colors duration-150';

        const sdgTitleKey = `sdg${sdg.number}_title`;
        // Ensure SDG_INFO is available globally (or passed as arg if refactored)
        const sdgName = (typeof translations !== 'undefined' && translations[currentLanguage])
                        ? (translations[currentLanguage][sdgTitleKey] || (typeof SDG_INFO !== 'undefined' && SDG_INFO[sdg.number]?.name) || `SDG ${sdg.number}`)
                        : (typeof SDG_INFO !== 'undefined' && SDG_INFO[sdg.number]?.name || `SDG ${sdg.number}`);

        // Refined innerHTML for better structure and responsiveness
        item.innerHTML = `
            <div class="flex items-center space-x-3 overflow-hidden mr-3 flex-grow min-w-0">
                <span class="w-8 h-8 rounded-full text-xs font-bold border-2 flex items-center justify-center text-white flex-shrink-0" style="background-color:${sdg.color_code}; border-color:${sdg.color_code};">
                   ${sdg.number}
                </span>
                <span class="font-medium text-gray-700 truncate" title="${sdgName}">${sdgName}</span>
            </div>
            <div class="flex items-center space-x-2 md:space-x-3 flex-shrink-0">
                 <div class="w-16 sm:w-20 md:w-24 lg:w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                     <div class="h-full rounded-full ${performance.bgColorClass}" style="width: ${Math.max(0, score) * 10}%"></div>
                 </div>
                 <span class="font-bold text-sm md:text-base lg:text-lg ${performance.textColorClass}" style="min-width: 35px; text-align: right;">${score.toFixed(1)}</span>
                 <span class="hidden sm:inline-block text-xs font-semibold px-2 py-0.5 rounded-full ${performance.bgColorClass} ${performance.textColorClass} whitespace-nowrap">${performance.levelText}</span>
            </div>
        `;
        breakdownContainer.appendChild(item); // Use the local variable
    });
    console.log('[ui] Finished populating breakdown.');
}


// Helper to get performance level translated text and Tailwind classes
function getPerformanceLevelDetails(score) {
    let levelKey, bgColorClass, textColorClass;
     if (score >= 8) { levelKey = 'perf_excellent'; bgColorClass = 'bg-green-500'; textColorClass = 'text-white'; }
     else if (score >= 6) { levelKey = 'perf_good'; bgColorClass = 'bg-blue-500'; textColorClass = 'text-white'; }
     else if (score >= 4) { levelKey = 'perf_fair'; bgColorClass = 'bg-yellow-400'; textColorClass = 'text-gray-800'; }
     else { levelKey = 'perf_needs_improvement'; bgColorClass = 'bg-red-500'; textColorClass = 'text-white'; }

     // Ensure translations and currentLanguage are accessible
     const levelText = (typeof translations !== 'undefined' && translations[currentLanguage])
                        ? (translations[currentLanguage][levelKey] || translations['en'][levelKey] || 'N/A')
                        : 'N/A'; // Fallback

     return {
         levelText: levelText,
         bgColorClass: bgColorClass,
         textColorClass: textColorClass
     };
 }

function generatePDF() {
    const alertKey = 'pdf_alert';
    const alertText = (typeof translations !== 'undefined' && translations[currentLanguage])
                    ? (translations[currentLanguage][alertKey] || translations['en'][alertKey])
                    : "PDF Generation is not fully implemented. Printing the page might be a temporary alternative.";
    alert(alertText);
}