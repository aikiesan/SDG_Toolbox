'use strict';
// results_page.js
// Main JS logic for SDG Assessment Results page

// --- Global Variables ---
// --- SDG to 5P Category Mapping and Colors ---
const SDG_TO_CATEGORY_MAP = {
    1: 'People', 2: 'People', 3: 'People', 4: 'People', 5: 'People',
    6: 'Planet', 12: 'Planet', 13: 'Planet', 14: 'Planet', 15: 'Planet',
    7: 'Prosperity', 8: 'Prosperity', 9: 'Prosperity', 10: 'Prosperity', 11: 'Prosperity',
    16: 'Peace',
    17: 'Partnership'
};
const CATEGORY_COLORS = {
    'People': 'var(--danger)',
    'Planet': 'var(--success)',
    'Prosperity': 'var(--warning)',
    'Peace': 'var(--primary)',
    'Partnership': 'var(--info)'
};

// (Accessed by multiple functions)
let currentExpandedChartId = null; // Track which chart is in the modal
let modalChartInstance = null;     // Instance of the chart in the modal

// --- Main Initialization ---
// Wait for the DOM to be fully loaded before executing JS
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM Content Loaded. Starting results page initialization.");

    // --- Dependency Checks ---
    if (typeof Chart === 'undefined') {
        console.error("Chart.js library not loaded. Cannot render charts.");
        displayInitializationError("Chart library (Chart.js) is missing. Please reload the page.");
        return; // Stop execution if Chart.js is missing
    }
     if (typeof window.SDGCharts === 'undefined') {
        console.error("SDGCharts module not loaded. Cannot render charts.");
        // Display error but continue to initialize UI/Handlers that don't depend on SDGCharts
        displayInitializationError("Custom chart functions (SDGCharts) are missing. Charts may not display correctly.");
    }
     if (typeof bootstrap === 'undefined' || typeof bootstrap.Modal === 'undefined') {
        console.error("Bootstrap JavaScript components (Modal) not loaded.");
        displayInitializationError("UI components (Bootstrap Modals) are missing. Some features might not work.");
        // Continue if possible, modals might just fail
    }
     if (!window.sdgScoresData) {
         console.error("SDG Score Data (window.sdgScoresData) not found. Check template.");
         displayInitializationError("Assessment score data is missing. Results cannot be displayed.");
         // Hide loading overlay even on error, but show data error
         hideLoadingOverlay();
         return; // Stop if core data is missing
     }

    // --- Initialization Sequence ---
    try {
        initializeCharts(); // Create all charts
        initializeUIComponents(); // Populate score cards, strengths, recommendations, etc.
        setupEventHandlers(); // Attach listeners to buttons, etc.
        hideLoadingOverlay(); // Hide loading spinner *after* essential setup
        console.log("Results page initialization sequence complete.");
    } catch (error) {
        console.error("Critical error during page initialization:", error);
        displayInitializationError(`An unexpected error occurred: ${error.message}. Please check the console.`);
        hideLoadingOverlay(); // Ensure overlay is hidden even if errors occur later
    }
}); // End DOMContentLoaded

// --- Helper Functions ---

/**
 * Hides the loading overlay smoothly.
 */
function hideLoadingOverlay() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.style.opacity = '0';
        // Use setTimeout to allow the transition to complete before setting display: none
        setTimeout(() => {
            loadingOverlay.classList.add('hidden'); // Add class that sets display: none !important
            loadingOverlay.style.display = 'none'; // Fallback just in case
        }, 300); // Should match the CSS transition duration
    }
}

/**
 * Displays a general error message on the page.
 * @param {string} message - The error message to display.
 */
function displayInitializationError(message) {
    // Try to add the error message prominently, e.g., below the header
    const headerSection = document.querySelector('#results-report .section-container:first-child');
    if (headerSection && !headerSection.querySelector('.alert-danger.init-error')) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger init-error mt-3';
        errorDiv.setAttribute('role', 'alert');
        errorDiv.textContent = `Initialization Error: ${message}`;
        headerSection.appendChild(errorDiv);
    }
    // Also ensure loading overlay is hidden if an error occurs
    hideLoadingOverlay();
}

/**
 * Initializes all charts on the page.
 */
function initializeCharts() {
    console.log("Initializing charts...");
    let chartInitializationError = false;

    // Check again for dependencies within this function
    if (typeof Chart === 'undefined' || typeof window.SDGCharts === 'undefined') {
        console.error("initializeCharts: Chart.js or SDGCharts not available.");
         document.querySelectorAll('.chart-container').forEach(container => {
            if (!container.querySelector('.alert')) {
                 container.innerHTML = '<div class="alert alert-warning">Chart library or functions missing.</div>';
             }
         });
        return; // Don't proceed if libraries are missing
    }

    // Prepare necessary data (already available globally)
    const sdgScoresData = window.sdgScoresData;
    // Create a simple SDG Name Lookup if not provided by SDGCharts
    const sdgNameLookup = window.sdgNameLookup || sdgScoresData.reduce((acc, sdg) => {
        if (sdg && sdg.number && sdg.name) {
            acc[sdg.number] = sdg.name;
        }
        return acc;
    }, {});

    // Calculate 5P category scores once
    const calculatedCategoryScores = calculate5PCategoryData();

    const chartConfigs = [
        { id: 'sdgRadarChart', creator: window.SDGCharts.createRadarChart, data: sdgScoresData, lookup: sdgNameLookup },
        { id: 'sdgBarChart', creator: window.SDGCharts.createBarChart, data: sdgScoresData, lookup: sdgNameLookup },
        // --- MODIFIED ENTRY ---
        { id: 'categoryBarChart', creator: window.SDGCharts.createCategoryBarChart, data: calculatedCategoryScores }, // Pass calculated scores
        // --- END MODIFIED ENTRY ---
        { id: 'dimensionsChart', creator: window.SDGCharts.createDimensionsChart, data: sdgScoresData }, // Pass original scores
        { id: 'strengthsGapsChart', creator: window.SDGCharts.createStrengthsGapsChart, data: sdgScoresData, lookup: sdgNameLookup }
    ];

    chartConfigs.forEach(config => {
        try {
            console.log(`Attempting to create chart: ${config.id}`);
            const canvas = document.getElementById(config.id);
            if (!canvas) {
                console.warn(`Canvas element not found for chart: ${config.id}`);
                return; // Skip
            }
            const ctx = canvas.getContext('2d');
            if (!ctx) {
                 console.error(`Could not get 2D context for canvas: ${config.id}`);
                 canvas.closest('.chart-container').innerHTML = `<div class="alert alert-danger">Error preparing chart canvas.</div>`;
                 return; // Skip
            }

            if (typeof config.creator !== 'function') {
                throw new Error(`Chart creator function for ${config.id} is not defined in SDGCharts.`);
            }

            // Call the creator function, passing appropriate data
            const chartInstance = config.creator(config.data, config.lookup); // Pass data and lookup if needed

            if (!(chartInstance instanceof Chart)) {
                // The creator function might have logged its own success message but didn't return a Chart object
                console.error(`Chart creator for ${config.id} did not return a valid Chart instance. Function might have failed internally or has wrong return type.`);
                 // Avoid overwriting potential error messages from the creator itself if possible
                 if (!canvas.closest('.chart-container').querySelector('.alert')) {
                    canvas.closest('.chart-container').innerHTML = `<div class="alert alert-danger">Error creating chart instance.</div>`;
                 }
                chartInitializationError = true;
            } else {
                console.log(`${config.id} chart instance created successfully by results_page.js.`);
                // Optional: Store instances globally if needed for complex interactions later
                 // window[config.id + 'Instance'] = chartInstance;
            }
        } catch (chartError) {
            console.error(`Error creating chart ${config.id}:`, chartError);
            const canvas = document.getElementById(config.id);
            if (canvas && canvas.closest('.chart-container') && !canvas.closest('.chart-container').querySelector('.alert')) {
               canvas.closest('.chart-container').innerHTML = `<div class="alert alert-danger">Error creating chart: ${chartError.message}</div>`;
            }
            chartInitializationError = true;
        }
    });

    console.log("Chart initialization phase complete. Errors encountered:", chartInitializationError);
}


/**
 * Initialize UI components like tooltips, populate score cards, etc.
 */
function initializeUIComponents() {
    console.log("Initializing UI components...");

     // Initialize Custom Tooltips (using hover listeners)
    try {
        const tooltipTriggerList = document.querySelectorAll('.custom-tooltip'); // Target the container
        tooltipTriggerList.forEach(tooltipContainer => {
            const icon = tooltipContainer.querySelector('.tooltip-icon');
            const tooltipText = tooltipContainer.querySelector('.tooltiptext');
             if (icon && tooltipText) {
                 tooltipContainer.addEventListener('mouseenter', () => {
                     tooltipText.style.visibility = 'visible';
                     tooltipText.style.opacity = '1';
                 });
                 tooltipContainer.addEventListener('mouseleave', () => {
                    tooltipText.style.visibility = 'hidden';
                    tooltipText.style.opacity = '0';
                 });
             }
        });
        console.log("Custom tooltips initialized via event listeners.");
    } catch (e) { console.error("Error initializing custom tooltips:", e); }

    // Pre-initialize Bootstrap Modals (ensure instance exists)
    try {
        document.querySelectorAll('.modal').forEach(modalElement => {
            if (window.bootstrap && !bootstrap.Modal.getInstance(modalElement)) {
                new bootstrap.Modal(modalElement);
            }
        });
        console.log("Modals pre-initialized.");
    } catch(e) { console.error("Error initializing Bootstrap modals:", e); }

    // Populate dynamic UI elements
    populateCategoryData();
    populateSdgsEvaluated();
    populateStrengthsAndImprovement();
    generateRecommendations();
    console.log("Dynamic UI components populated.");
}

/**
 * Set up event listeners for buttons and interactive elements.
 */
function setupEventHandlers() {
    console.log("Setting up event handlers...");

    // Print report button
    document.getElementById('printReport')?.addEventListener('click', () => window.print());

    // Download PDF button
    document.getElementById('downloadPDF')?.addEventListener('click', generatePDF);

    // Share results button
    document.getElementById('shareResults')?.addEventListener('click', shareResults);

    // Export CSV button
    document.getElementById('exportCSV')?.addEventListener('click', () => {
        // Use global function, passing required data
        exportToCSV(window.sdgScoresData, window.projectName);
    });

    // Expand chart buttons
    document.querySelectorAll('.expand-chart').forEach(button => {
        button.addEventListener('click', function() {
            const chartId = this.getAttribute('data-chart');
            expandChart(chartId); // Calls the expandChart function
        });
    });

    // Download chart buttons (in each chart container)
    document.querySelectorAll('.download-chart').forEach(button => {
        button.addEventListener('click', function() {
            const chartId = this.getAttribute('data-chart');
             if (window.SDGCharts && typeof window.SDGCharts.exportChartImage === 'function') {
                 // Use the dedicated function if available
                 window.SDGCharts.exportChartImage(chartId);
             } else {
                 // Basic fallback
                 console.warn('SDGCharts.exportChartImage not available. Using basic canvas export.');
                 const canvas = document.getElementById(chartId);
                 if (canvas) {
                     try {
                         const link = document.createElement('a');
                         link.download = `${chartId}.png`;
                         link.href = canvas.toDataURL('image/png');
                         link.click();
                     } catch (e) {
                         console.error(`Error exporting basic chart ${chartId}:`, e);
                         alert("Could not export chart image.");
                     }
                 } else {
                     console.error(`Canvas not found for basic export: ${chartId}`);
                 }
             }
        });
    });

    // Download button within the chart modal
    document.getElementById('downloadModalChart')?.addEventListener('click', function() {
        const canvas = document.getElementById('modalChartCanvas');
        if (!canvas) {
            console.error("Modal canvas not found for download.");
            alert("Cannot download: Modal chart canvas not found.");
            return;
        }
        const currentChartId = window.currentExpandedChartId || 'expanded-chart'; // Use stored ID
        const link = document.createElement('a');
        link.download = `${currentChartId}_expanded.png`; // More descriptive name
        try {
            link.href = canvas.toDataURL('image/png', 1.0); // Quality argument
            document.body.appendChild(link); // Required for Firefox
            link.click();
            document.body.removeChild(link); // Clean up
        } catch (e) {
            console.error("Error generating modal chart image for download:", e);
            alert("Could not download chart image due to an error.");
        }
    });

    // Share modal confirmation button
    document.getElementById('confirmShare')?.addEventListener('click', function() {
        const emailInput = document.getElementById('shareEmail');
        const messageInput = document.getElementById('shareMessage');
        const includeRecsInput = document.getElementById('includeRecommendations');
        const email = emailInput?.value;
        const message = messageInput?.value;
        const includeRecs = includeRecsInput?.checked;
        const button = this;

        if (!email || !/^\S+@\S+\.\S+$/.test(email)) { // Basic validation
            alert('Please enter a valid email address.');
            emailInput?.focus();
            return;
        }

        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Sending...';
        button.disabled = true;

        // --- AJAX Call Placeholder ---
        // Replace with your actual fetch() call to the backend sharing endpoint
        console.log("Simulating share request:", { email, message, includeRecs, assessmentId: window.assessmentId });
        setTimeout(() => { // Simulate network delay
            // On success/failure from backend:
            const shareModalEl = document.getElementById('shareModal');
            if (shareModalEl && window.bootstrap) {
                const shareModal = bootstrap.Modal.getInstance(shareModalEl);
                shareModal?.hide();
            }
            alert('Assessment results shared successfully! (Simulation)'); // Replace with actual feedback

            // Reset button
            button.innerHTML = 'Share';
            button.disabled = false;
            // Optionally clear form fields
            // emailInput.value = '';
            // messageInput.value = '';
        }, 1500);
        // --- End AJAX Placeholder ---
    });

    // Chart Modal event listeners for rendering/cleanup
    const chartModalEl = document.getElementById('chartModal');
    if (chartModalEl && window.bootstrap) {
        chartModalEl.addEventListener('shown.bs.modal', handleChartModalShow);
        chartModalEl.addEventListener('hidden.bs.modal', handleChartModalHide);
    }
    console.log("Event handlers attached.");
}


// --- Chart Modal Handling ---

/**
 * Renders the selected chart in the modal when it's shown.
 */
function handleChartModalShow() {
    console.log(`Modal shown. Attempting to render chart: ${window.currentExpandedChartId}`);
    if (!window.currentExpandedChartId) {
        console.error("Cannot expand chart: No chart ID stored.");
        renderModalError("Could not load chart. No chart selected.");
        return;
    }
     // Check dependencies again just before use
     if (typeof Chart === 'undefined' || !window.SDGCharts || typeof window.SDGCharts.getChartData !== 'function') {
        console.error("Cannot expand chart: Chart.js, SDGCharts module, or getChartData function not available.");
        renderModalError("Failed to load chart data function or library.");
        return;
    }

    const chartCanvas = document.getElementById('modalChartCanvas');
    if (!chartCanvas){
        console.error("Modal canvas element not found.");
        return; // Should not happen if modal HTML is correct
    }
    const ctx = chartCanvas.getContext('2d');
    if (!ctx) {
         console.error("Could not get 2D context for modal canvas.");
         renderModalError("Failed to prepare modal chart canvas.");
         return;
    }


    // Destroy previous chart instance if it exists to prevent conflicts
    if (window.modalChartInstance) {
        window.modalChartInstance.destroy();
        window.modalChartInstance = null;
         console.log("Destroyed previous modal chart instance.");
    }

    try {
        // Get the configuration object for the specific chart
        const chartConfig = window.SDGCharts.getChartData(window.currentExpandedChartId);

        if (!chartConfig || !chartConfig.type || !chartConfig.data || !chartConfig.options) {
            throw new Error(`Chart configuration not found or invalid for ID: ${window.currentExpandedChartId}`);
        }

        // Update modal title dynamically
         const modalTitleEl = document.getElementById('chartModalLabel');
          if (modalTitleEl) {
              // Try to get a meaningful title from the config, otherwise generate one
               const chartTitle = chartConfig.options?.plugins?.title?.text ||
                                  window.currentExpandedChartId.replace(/([A-Z])/g, ' $1') // Add spaces before caps
                                                              .replace(/^./, str => str.toUpperCase()); // Capitalize first letter
               modalTitleEl.textContent = `${chartTitle} - Expanded View`;
           }


        // Create the new chart instance on the modal canvas
        window.modalChartInstance = new Chart(ctx, {
            type: chartConfig.type,
            data: chartConfig.data,
            // Merge original options with overrides for modal display
            options: {
                ...chartConfig.options,
                responsive: true,          // Ensure responsiveness within modal
                maintainAspectRatio: false, // Allow modal size to dictate aspect ratio
                 // Potentially increase font size or adjust legend for larger view
                 plugins: {
                    ...chartConfig.options.plugins,
                    legend: {
                         ...chartConfig.options.plugins?.legend,
                         position: 'top', // Example: Ensure legend is visible
                    }
                 }
            }
        });
        console.log(`Expanded chart ${window.currentExpandedChartId} rendered in modal.`);

    } catch (error) {
        console.error("Error creating modal chart:", error);
        renderModalError(`Error rendering chart: ${error.message}`);
    }
}

/**
 * Cleans up the chart instance when the modal is hidden.
 */
function handleChartModalHide() {
    if (window.modalChartInstance) {
        window.modalChartInstance.destroy();
        window.modalChartInstance = null;
        console.log("Destroyed modal chart instance on hide.");
    }
    // Reset the stored ID and modal title
    window.currentExpandedChartId = null;
    const modalTitleEl = document.getElementById('chartModalLabel');
    if (modalTitleEl) modalTitleEl.textContent = 'Chart View';

    // Restore original canvas container if it was replaced by an error message
     const modalBody = document.querySelector('#chartModal .modal-body div[style*="height: 500px"]');
     if (modalBody && !modalBody.querySelector('canvas#modalChartCanvas')) {
         console.log("Restoring modal canvas container.");
         modalBody.innerHTML = '<canvas id="modalChartCanvas"></canvas>'; // Add the canvas back
     }
}

/**
 * Displays an error message within the chart modal body.
 * @param {string} message - The error message.
 */
function renderModalError(message) {
     const modalBody = document.querySelector('#chartModal .modal-body div[style*="height: 500px"]');
     if (modalBody) {
         modalBody.innerHTML = `<div class="alert alert-danger text-center p-5">${message}</div>`;
     }
 }

// (These functions update specific parts of the page with data)

/**
 * Calculates average scores for the 5 P categories.
 * Returns an object with category data.
 */
function calculate5PCategoryData() {
    if (!window.sdgScoresData || !Array.isArray(window.sdgScoresData) || window.sdgScoresData.length === 0) {
        console.warn("Category data calculation skipped: No sdgScoresData.");
        return {};
    }
    console.log("Calculating 5 P category data...");

    // Define the standard 5 P categories
    const categories5P = {
        'People':      { sdgs: [1, 2, 3, 4, 5], color: 'var(--danger)', icon: 'fa-users' },
        'Planet':      { sdgs: [6, 12, 13, 14, 15], color: 'var(--success)', icon: 'fa-leaf' },
        'Prosperity':  { sdgs: [7, 8, 9, 10, 11], color: 'var(--warning)', icon: 'fa-chart-line' },
        'Peace':       { sdgs: [16], color: 'var(--primary)', icon: 'fa-hands-helping' },
        'Partnership': { sdgs: [17], color: 'var(--info)', icon: 'fa-handshake' }
    };

    let categoryScores = {};
    Object.entries(categories5P).forEach(([categoryName, categoryData]) => {
        let total = 0;
        let count = 0;
        categoryData.sdgs.forEach(num => {
            const sdg = window.sdgScoresData.find(s => s && parseInt(s.number) === num);
            if (sdg && sdg.total_score !== null && typeof sdg.total_score !== 'undefined') {
                total += parseFloat(sdg.total_score);
                count++;
            }
        });

        categoryScores[categoryName] = {
            score: (count > 0) ? (total / count) : 0, // Calculate average or default to 0
            count: count,
            color: categoryData.color,
            icon: categoryData.icon
        };
        console.log(`Category ${categoryName}: Score=${categoryScores[categoryName].score.toFixed(1)}, Count=${count}`);
    });

    return categoryScores; // Return the calculated scores object
}

/**
 * Populates the 'Top Performing Category' card using 5P data.
 */
function populateCategoryData() { // Keep original name for consistency if called elsewhere
    const element = document.getElementById('topCategory');
    if (!element) return;

    const categoryScores = calculate5PCategoryData(); // Use the 5P calculation

    if (Object.keys(categoryScores).length === 0) {
        element.innerHTML = '<p class="text-muted fst-italic small">No score data available.</p>';
        return;
    }

    // Find the category with the highest average score (and at least one scored SDG)
    let topCategoryName = '';
    let topCategoryScore = -1;
    let topCategoryColor = 'var(--gray)';

    Object.entries(categoryScores).forEach(([name, data]) => {
        // Ensure category had scored SDGs before considering it 'top'
        if (data.count > 0 && data.score > topCategoryScore) {
            topCategoryName = name;
            topCategoryScore = data.score;
            topCategoryColor = data.color;
        }
    });

    // Update UI
    if (topCategoryName) {
        element.innerHTML = `
            <div class="d-flex align-items-center mb-1">
                <span class="category-pill me-2" style="background-color: ${topCategoryColor};">
                    ${topCategoryName}
                </span>
                <div class="score-value mb-0">${topCategoryScore.toFixed(1)}<span class="fs-6">/10</span></div>
            </div>
            <div class="score-progress mb-1" title="Average score: ${topCategoryScore.toFixed(1)}/10">
                <div class="score-progress-bar"
                     style="width: ${Math.max(0, topCategoryScore / 10 * 100)}%; background-color: ${topCategoryColor};">
                </div>
            </div>
            <div class="small text-muted mt-1">
                Highest scoring category average (5 P's)
            </div>
        `;
    } else {
        element.innerHTML = '<p class="text-muted fst-italic small">No category scores calculated yet.</p>';
    }
}

/**
 * Populates the 'SDGs Evaluated' card.
 */
function populateSdgsEvaluated() {
    const element = document.getElementById('sdgsEvaluated');
    if (!element) return;
     if (!window.sdgScoresData || !Array.isArray(window.sdgScoresData)) {
         element.innerHTML = '<p class="text-muted fst-italic small">Score data unavailable.</p>';
         return;
     }
    console.log("Populating SDGs evaluated count...");

    // Count SDGs that have a defined total_score (not null/undefined)
    const evaluatedCount = window.sdgScoresData.filter(sdg => sdg && typeof sdg.total_score === 'number').length;
    const totalSDGs = 17; // Total possible SDGs
    const percentage = totalSDGs > 0 ? (evaluatedCount / totalSDGs) * 100 : 0;

    element.innerHTML = `
        <div class="score-value">${evaluatedCount}<span class="fs-6">/${totalSDGs}</span></div>
        <div class="score-label mb-1">SDGs with Scores</div>
        <div class="score-progress" title="${evaluatedCount} out of ${totalSDGs} SDGs scored">
            <div class="score-progress-bar"
                 style="width: ${percentage}%; background-color: var(--primary);">
            </div>
        </div>
        <div class="small text-muted mt-1">
            ${percentage.toFixed(0)}% of SDGs have calculated scores
        </div>
    `;
}

/**
 * Populates the 'Top Strengths' and 'Areas for Improvement' sections.
 */
function populateStrengthsAndImprovement() {
    const strengthsElement = document.getElementById('topStrengths');
    const improvementElement = document.getElementById('improvementAreas');

    if (!strengthsElement || !improvementElement) return;
     if (!window.sdgScoresData || !Array.isArray(window.sdgScoresData)) {
         strengthsElement.innerHTML = '<p class="text-muted fst-italic small">Score data unavailable.</p>';
         improvementElement.innerHTML = '<p class="text-muted fst-italic small">Score data unavailable.</p>';
         return;
     }
    console.log("Populating strengths and improvement areas...");


    // Filter for SDGs with valid scores, number, and name
    const assessedSDGs = window.sdgScoresData.filter(sdg =>
        sdg && typeof sdg.total_score === 'number' && sdg.number && sdg.name
    );

    if (assessedSDGs.length === 0) {
        strengthsElement.innerHTML = '<p class="text-muted fst-italic small">No scored SDGs found.</p>';
        improvementElement.innerHTML = '<p class="text-muted fst-italic small">No scored SDGs found.</p>';
        return;
    }

    // Sort and take top/bottom 3
    const sortedSDGs = [...assessedSDGs].sort((a, b) => b.total_score - a.total_score); // Descending for strengths
    const topStrengths = sortedSDGs.slice(0, 3);
    const improvementAreas = sortedSDGs.slice(-3).reverse(); // Take last 3 and reverse to show lowest first

    // --- Helper functions for display ---
    const getScoreLabel = (score) => {
        if (score >= 8) return 'Excellent';
        if (score >= 6) return 'Good';
        if (score >= 4) return 'Fair';
        return 'Needs Improvement';
    };
    const getBadgeClass = (score) => {
        if (score >= 8) return 'bg-success';
        if (score >= 6) return 'bg-primary';
        if (score >= 4) return 'bg-warning';
        return 'bg-danger';
    };
    const createItemHTML = (sdg, itemClass) => {
        const categoryName = SDG_TO_CATEGORY_MAP[sdg.number] || 'Unknown';
        const categoryColor = CATEGORY_COLORS[categoryName] || 'var(--gray)';
        return `
            <div class="${itemClass}">
                <span class="sdg-badge sdg-badge-sm me-2" style="background-color: ${sdg.color_code || '#cccccc'};">
                    ${sdg.number}
                </span>
                <div class="flex-grow-1">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="fw-bold small">${sdg.name}</span>
                        <span class="badge rounded-pill ms-2" style="background-color:${categoryColor}; font-size: 0.7rem;">${categoryName}</span>
                    </div>
                    <div class="d-flex align-items-center mt-1" style="font-size: 0.8rem;">
                        <div class="me-2">Score: <strong>${sdg.total_score.toFixed(1)}</strong></div>
                        <div class="badge ${getBadgeClass(sdg.total_score)} ms-auto">
                            ${getScoreLabel(sdg.total_score)}
                        </div>
                    </div>
                </div>
            </div>
        `;
    };

    // Generate HTML for strengths (only if score >= 6, for example)
    const strengthsHTML = topStrengths
        .filter(sdg => sdg.total_score >= 6) // Optionally filter strengths
        .map(sdg => createItemHTML(sdg, 'strength-item'))
        .join('');

    // Generate HTML for improvement areas (only if score < 6)
    const improvementHTML = improvementAreas
         .filter(sdg => sdg.total_score < 6) // Filter for actual improvement areas
         .map(sdg => createItemHTML(sdg, 'improve-item'))
         .join('');

    // Update DOM
    strengthsElement.innerHTML = strengthsHTML || '<p class="text-muted fst-italic small">No significant strengths (score >= 6) identified.</p>';
    improvementElement.innerHTML = improvementHTML || '<p class="text-muted fst-italic small">No specific areas for improvement (score < 6) identified.</p>';
}

/**
 * Generates tailored recommendations based on lowest scoring SDGs.
 */
function generateRecommendations() {
    const container = document.getElementById('recommendationsContainer');
    if (!container) return;
     if (!window.sdgScoresData || !Array.isArray(window.sdgScoresData)) {
         container.innerHTML = '<p class="text-muted fst-italic small">Score data unavailable.</p>';
         return;
     }
    console.log("Generating recommendations...");


    // Filter, sort by lowest score, take top 3 needing improvement
    const improvementSDGs = window.sdgScoresData
        .filter(sdg => sdg && typeof sdg.total_score === 'number' && sdg.total_score < 6 && sdg.number && sdg.name)
        .sort((a, b) => a.total_score - b.total_score)
        .slice(0, 3); // Max 3 recommendations

    if (improvementSDGs.length === 0) {
        container.innerHTML = '<p class="text-success fst-italic small"><i class="fas fa-check-circle me-1"></i>Good performance! No SDGs found scoring below 6.</p>';
        return;
    }

    // Simplified map (expand significantly for real application)
     const recommendationsMap = {
         1: ['Enhance local employment opportunities through project phases.', 'Integrate affordable material choices or housing components.', 'Design flexible spaces for potential community enterprise.'],
         2: ['Incorporate urban farming elements (gardens, green roofs).', 'Specify locally sourced, sustainable food options if applicable (e.g., cafe).', 'Implement composting and food waste reduction strategies.'],
         3: ['Prioritize indoor air quality through material selection and ventilation.', 'Maximize access to natural light and views.', 'Include spaces promoting physical activity and mental well-being.'],
         4: ['Integrate educational signage about sustainable features.', 'Ensure universal design principles for inclusive access.', 'Design adaptable spaces for learning or community workshops.'],
         5: ['Ensure gender-neutral or appropriate facilities.', 'Conduct safety audits focusing on vulnerable users.', 'Promote equitable access to all project amenities.'],
         6: ['Implement high-efficiency water fixtures and appliances.', 'Explore rainwater harvesting and greywater recycling systems.', 'Design drought-tolerant landscaping (xeriscaping).'],
         7: ['Maximize on-site renewable energy generation (solar PV).', 'Optimize building envelope insulation and airtightness.', 'Specify energy-efficient lighting and HVAC systems.'],
         8: ['Prioritize local and ethical sourcing for materials and labor.', 'Design for durability and low maintenance.', 'Support local economy through design choices (e.g., spaces for local businesses).'],
         9: ['Incorporate resilient infrastructure design (against climate impacts, etc.).', 'Specify innovative and sustainable materials/technologies.', 'Design for future adaptability and technological upgrades.'],
        10: ['Exceed basic accessibility standards (universal design).', 'Design inclusive spaces catering to diverse needs (age, ability, culture).', 'Consider socio-economic diversity in project impact and access.'],
        11: ['Enhance connections to public transport and active mobility (walking, cycling).', 'Create safe, accessible, and engaging public spaces.', 'Promote mixed-use development to reduce travel needs.'],
        12: ['Specify materials with high recycled content and low environmental impact (EPDs).', 'Design for deconstruction and material reuse.', 'Implement robust construction and operational waste management plans.'],
        13: ['Conduct climate risk assessment and incorporate adaptation measures.', 'Prioritize low-embodied carbon materials.', 'Utilize passive design strategies to reduce energy demand and enhance thermal comfort.'],
        14: ['Implement advanced stormwater management (LID/SuDS).', 'Prevent water pollution during construction and operation.', 'Protect marine/aquatic ecosystems if project is near water bodies.'],
        15: ['Enhance on-site biodiversity with native planting and habitat creation.', 'Protect existing ecosystems and trees.', 'Specify sustainably harvested timber and bio-based materials.'],
        16: ['Ensure transparent project communication and stakeholder engagement.', 'Promote inclusive design processes.', 'Implement fair labor practices and ethical procurement.'],
        17: ['Collaborate with local communities and sustainability experts.', 'Share project performance data and lessons learned.', 'Seek partnerships to enhance sustainability outcomes.']
    };


    // Helper functions for labels/badges (could be shared)
    const getScoreLabel = (score) => { /* ... copy from populateStrengths ... */ return score >= 8 ? 'Excellent': score >= 6 ? 'Good' : score >= 4 ? 'Fair' : 'Needs Improvement'; };
    const getBadgeClass = (score) => { /* ... copy from populateStrengths ... */ return score >= 8 ? 'bg-success': score >= 6 ? 'bg-primary' : score >= 4 ? 'bg-warning' : 'bg-danger'; };

    let recommendationsHTML = '<p class="mb-3">Focusing on these areas could improve the project\'s SDG alignment:</p>';
    improvementSDGs.forEach(sdg => {
        const sdgNumber = parseInt(sdg.number);
        const recList = recommendationsMap[sdgNumber] || ['Review official SDG targets and consult specific resources for improvement strategies.'];
        // Construct the official UN SDG goal link
        const unSdgLink = `https://sdgs.un.org/goals/goal${sdgNumber}`;

        recommendationsHTML += `
            <div class="recommendation-card mb-3 animate-in" style="animation-delay: ${improvementSDGs.indexOf(sdg) * 0.1}s">
                <div class="recommendation-header">
                    <span class="sdg-badge me-2" style="background-color: ${sdg.color_code || '#cccccc'};">
                        ${sdg.number}
                    </span>
                    <h5 class="mb-0 flex-grow-1 h6">${sdg.name}</h5>
                     <span class="badge ${getBadgeClass(sdg.total_score)} ms-auto me-2">${getScoreLabel(sdg.total_score)}</span>
                     <span class="small text-muted">(Score: ${sdg.total_score.toFixed(1)})</span>
                </div>
                <div class="recommendation-content">
                    <p class="mb-2 small text-muted">Suggested actions:</p>
                    <ul class="recommendation-list small mb-0">
                        ${recList.map(rec => `<li>${rec}</li>`).join('')}
                         <li><a href="${unSdgLink}" target="_blank" class="text-decoration-none small link-primary">Learn more about SDG ${sdg.number} (UN Site)... <i class="fas fa-external-link-alt fa-xs"></i></a></li>
                    </ul>
                </div>
            </div>
        `;
    });

    container.innerHTML = recommendationsHTML;
}


// --- Action Functions ---
// (Called by event handlers)

/**
 * Triggers the browser's print dialog.
 */
// Note: Print logic is simple, handled directly in event handler: () => window.print()


/**
 * Generates a PDF report using html2canvas and jsPDF.
 */
async function generatePDF() {
    const downloadButton = document.getElementById('downloadPDF');
    if (!downloadButton) return;

    // Check for required libraries
    if (typeof jspdf === 'undefined' || typeof jspdf.jsPDF === 'undefined' || typeof html2canvas === 'undefined') {
        console.error("PDF Generation libraries (jsPDF or html2canvas) not loaded.");
        alert("PDF generation components are missing. Please reload the page.");
        return;
    }

    const originalHtml = downloadButton.innerHTML;
    downloadButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Generating PDF...';
    downloadButton.disabled = true;

    const elementToPrint = document.getElementById('results-report');
    if (!elementToPrint) {
        console.error("#results-report element not found for PDF generation.");
        alert("Report content not found. Cannot generate PDF.");
        downloadButton.innerHTML = originalHtml;
        downloadButton.disabled = false;
        return;
    }

    try {
        // CRITICAL: Wait for all charts to fully render
        console.log("Waiting for charts to render...");
        await new Promise(resolve => setTimeout(resolve, 500));  // Increased from 200ms

        // Force chart redraw to ensure canvas is populated
        const chartsToUpdate = [
            window.radarChart,
            window.barChart,
            window.categoriesPolarChart,
            window.dimensionsChart,
            window.strengthsGapsChart,
            window.comparisonChart,
            window.categoryBarChartInstance
        ];

        chartsToUpdate.forEach(chart => {
            if (chart && typeof chart.update === 'function') {
                chart.update('none');  // Update without animation
            }
        });

        // Wait for chart updates
        await new Promise(resolve => setTimeout(resolve, 300));

        // Temporarily hide non-print elements
        const noPrintElements = document.querySelectorAll('.no-print');
        noPrintElements.forEach(el => {
            el.style.display = 'none';  // Use display instead of visibility
        });

        // Ensure all canvases are visible
        const canvases = elementToPrint.querySelectorAll('canvas');
        console.log(`Found ${canvases.length} canvas elements`);

        canvases.forEach((canvas, idx) => {
            canvas.style.display = 'block';
            canvas.style.visibility = 'visible';
            console.log(`Canvas ${idx}: ${canvas.width}x${canvas.height}`);
        });

        console.log("Starting html2canvas...");
        const canvas = await html2canvas(elementToPrint, {
            scale: 1.5,  // Avoid hitting browser canvas size limits on long pages
            useCORS: true,
            allowTaint: false,
            backgroundColor: '#ffffff',
            scrollY: -window.scrollY, // Fix for scroll-related offsets causing blank/black spaces
            onclone: (clonedDoc) => {
                // Ensure charts are visible in cloned document
                const clonedCanvases = clonedDoc.querySelectorAll('canvas');
                clonedCanvases.forEach(c => {
                    c.style.display = 'block';
                    c.style.visibility = 'visible';
                });
            }
        });

        console.log(`Canvas generated: ${canvas.width}x${canvas.height}`);

        // Use JPEG instead of PNG to significantly reduce memory/payload size
        // and avoid "corrupted data" issues with massive base64 strings in jsPDF
        const imgData = canvas.toDataURL('image/jpeg', 0.95);
        const { jsPDF } = jspdf;
        const pdf = new jsPDF({
            orientation: 'p',
            unit: 'mm',
            format: 'a4',
            compress: true
        });

        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = pdf.internal.pageSize.getHeight();
        const margin = 10;  // 10mm margins
        const contentWidth = pdfWidth - (margin * 2);
        const contentHeight = pdfHeight - (margin * 2); // Height of printable area

        const imgProps = pdf.getImageProperties(imgData);
        const imgWidth = contentWidth;
        const imgHeight = (imgProps.height * imgWidth) / imgProps.width;

        let heightLeft = imgHeight;
        let position = 0; // Cumulative vertical offset

        // First page
        pdf.addImage(imgData, 'JPEG', margin, margin, imgWidth, imgHeight);
        heightLeft -= contentHeight;

        // Remaining pages
        while (heightLeft > 0) {
            pdf.addPage();
            position -= contentHeight; // Shift image UP for the next slice
            pdf.addImage(imgData, 'JPEG', margin, position + margin, imgWidth, imgHeight);
            heightLeft -= contentHeight;
        }

        const safeProjectName = (window.projectName || 'project').replace(/[^a-z0-9]/gi, '_').toLowerCase();
        const filename = `SDG_Assessment_${safeProjectName}_${window.assessmentId}_${new Date().toISOString().split('T')[0]}.pdf`;

        pdf.save(filename);
        console.log(`PDF saved: ${filename}`);

    } catch (error) {
        console.error("PDF generation failed:", error);
        alert(`Failed to generate PDF. Error: ${error.message}`);
    } finally {
        // Restore hidden elements
        const noPrintElements = document.querySelectorAll('.no-print');
        noPrintElements.forEach(el => {
            el.style.display = '';
        });

        downloadButton.innerHTML = originalHtml;
        downloadButton.disabled = false;
    }
}


/**
 * Opens the Share modal and generates a shareable link.
 */
async function shareResults() {
    const shareModalEl = document.getElementById('shareModal');
    if (!shareModalEl || !window.bootstrap) {
        console.error("Share modal element or Bootstrap Modal not found.");
        alert("Could not open the share dialog.");
        return;
    }

    const shareModal = bootstrap.Modal.getInstance(shareModalEl) || new bootstrap.Modal(shareModalEl);

    // Generate share link via API
    try {
        const response = await fetch(`/assessments/projects/${window.projectId}/assessments/${window.assessmentId}/share`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.success) {
            // Display share URL in modal
            const shareUrlInput = document.getElementById('shareUrl');
            if (shareUrlInput) {
                shareUrlInput.value = data.share_url;
                shareUrlInput.select();  // Auto-select for easy copying
            }

            shareModal.show();
        } else {
            alert(`Failed to generate share link: ${data.message}`);
        }
    } catch (error) {
        console.error("Error generating share link:", error);
        alert("Failed to generate share link. Please try again.");
    }
}

/**
 * Exports the SDG score data to a CSV file.
 * @param {Array} data - The array of SDG score objects.
 * @param {string} filenamePrefix - Prefix for the downloaded file name.
 */
function exportToCSV(data, filenamePrefix = 'sdg-assessment') {
     if (!data || !Array.isArray(data) || data.length === 0) {
         alert("No score data available to export.");
         console.warn("ExportToCSV called with invalid data:", data);
         return;
     }
    console.log("Exporting data to CSV...");

     // Define desired headers and order
     const desiredHeaders = ["number", "name", "direct_score", "bonus_score", "total_score", "notes"];
     // Get actual headers from the first object to ensure keys exist
     const actualHeaders = data.length > 0 ? Object.keys(data[0]) : [];
     const headers = desiredHeaders.filter(h => actualHeaders.includes(h)); // Use only headers present in data

     // Format headers for display (Capitalize, replace underscores)
     const formattedHeaders = headers.map(h => `"${h.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}"`);
     let csvContent = "data:text/csv;charset=utf-8," + formattedHeaders.join(",") + "\n";

     // Add data rows
     data.forEach(sdg => {
         const row = headers.map(header => {
             let value = sdg[header];
             // Handle null/undefined
             if (value === null || typeof value === 'undefined') {
                 return '"N/A"'; // Enclose N/A in quotes
             }
             // Format numbers (specifically scores)
             if (typeof value === 'number' && header.includes('score')) {
                 value = value.toFixed(1);
             }
             // Escape double quotes within the value and enclose the whole value in quotes
             value = `"${String(value).replace(/"/g, '""')}"`;
             return value;
         });
         csvContent += row.join(",") + "\n";
     });

     // Create and trigger download link
     const encodedUri = encodeURI(csvContent);
     const link = document.createElement("a");
     link.setAttribute("href", encodedUri);
     const safeFilename = filenamePrefix.replace(/[^a-z0-9]/gi, '_').toLowerCase();
     link.setAttribute("download", `${safeFilename}_sdg_scores_${window.assessmentId}.csv`);
     document.body.appendChild(link); // Required for Firefox
     link.click();
     document.body.removeChild(link); // Clean up
     console.log("CSV export triggered.");
 }


/**
 * Stores the ID of the chart to be expanded and shows the modal.
 * @param {string} chartId - The HTML ID of the chart canvas to expand.
 */
function expandChart(chartId) {
    console.log(`Request to expand chart: ${chartId}`);
    window.currentExpandedChartId = chartId; // Store the ID globally
    const chartModalEl = document.getElementById('chartModal');
    if (chartModalEl && window.bootstrap) {
        const chartModal = bootstrap.Modal.getInstance(chartModalEl) || new bootstrap.Modal(chartModalEl);
        chartModal.show(); // Trigger the 'shown.bs.modal' event
    } else {
        console.error("Chart modal element or Bootstrap Modal not found.");
        alert("Could not open the chart expansion dialog.");
    }
}

// --- Fallback Chart Creation (If SDGCharts fails) ---
/**
 * Creates basic fallback charts if the main SDGCharts module fails.
 * @param {Array} sdgScoresData - Array of SDG score objects.
 */
function createBasicCharts(sdgScoresData) {
    console.warn("Creating basic fallback charts.");
    if (!sdgScoresData || sdgScoresData.length === 0) {
        console.warn("No data for basic charts.");
        return;
    }

    const labels = sdgScoresData.map(score => `SDG ${score.number || '?'}`);
    const scores = sdgScoresData.map(score => parseFloat(score.total_score || 0));
    const colors = sdgScoresData.map(score => score.color_code || '#cccccc');

    // Basic Radar Chart
    try {
        const radarCanvas = document.getElementById('sdgRadarChart');
        if (radarCanvas) {
            const radarCtx = radarCanvas.getContext('2d');
            new Chart(radarCtx, {
                type: 'radar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'SDG Scores (Fallback)',
                        data: scores,
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgb(54, 162, 235)',
                        pointBackgroundColor: colors,
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false, scales: { r: { beginAtZero: true, max: 10 } } }
            });
             radarCanvas.closest('.chart-container')?.insertAdjacentHTML('afterbegin', '<div class="alert alert-warning alert-sm mb-2">Using fallback chart view.</div>');
        }
    } catch (e) { console.error("Failed to create basic radar chart:", e); }

    // Basic Bar Chart
    try {
        const barCanvas = document.getElementById('sdgBarChart');
        if (barCanvas) {
            const barCtx = barCanvas.getContext('2d');
            new Chart(barCtx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'SDG Scores (Fallback)',
                        data: scores,
                        backgroundColor: colors
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, max: 10 } } }
            });
            barCanvas.closest('.chart-container')?.insertAdjacentHTML('afterbegin', '<div class="alert alert-warning alert-sm mb-2">Using fallback chart view.</div>');
        }
    } catch (e) { console.error("Failed to create basic bar chart:", e); }

     // Mark other charts as unavailable
     ['categoriesPolarChart', 'dimensionsChart', 'strengthsGapsChart'].forEach(id => {
         const container = document.getElementById(id)?.closest('.chart-container');
         if (container && !container.querySelector('.alert')) {
             container.innerHTML = '<div class="alert alert-warning">Advanced chart view unavailable.</div>';
         }
     });
}

// Copy share URL to clipboard
document.addEventListener('DOMContentLoaded', function() {
    const copyShareUrlBtn = document.getElementById('copyShareUrl');
    if (copyShareUrlBtn) {
        copyShareUrlBtn.addEventListener('click', async function() {
            const shareUrlInput = document.getElementById('shareUrl');
            if (!shareUrlInput) return;

            try {
                await navigator.clipboard.writeText(shareUrlInput.value);
                this.innerHTML = '<i class="fas fa-check me-2"></i>Copied!';
                setTimeout(() => {
                    this.innerHTML = '<i class="fas fa-copy me-2"></i>Copy Link';
                }, 2000);
            } catch (error) {
                // Fallback for older browsers
                shareUrlInput.select();
                document.execCommand('copy');
                this.innerHTML = '<i class="fas fa-check me-2"></i>Copied!';
                setTimeout(() => {
                    this.innerHTML = '<i class="fas fa-copy me-2"></i>Copy Link';
                }, 2000);
            }
        });
    }
});