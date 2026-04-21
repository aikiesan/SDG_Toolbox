// /app/static/js/assessment/results_display.js
// Initializes the display of the expert assessment results page.

(function() {
    'use strict';

    // Function to check if required dependencies are loaded
    function checkDependencies() {
        const requiredFunctions = {
            'renderRadarChart': window.renderRadarChart,
            'renderBarChart': window.renderBarChart,
            'populateDetailedBreakdown': window.populateDetailedBreakdown
        };

        for (const [name, func] of Object.entries(requiredFunctions)) {
            if (typeof func !== 'function') {
                console.error(`Required function ${name} is not available. Make sure all necessary script files are included.`);
                return false;
            }
        }
        return true;
    }

    // Function to validate scores data
    function validateScoresData() {
        if (!window.sdgScoresData) {
            console.error('SDG scores data is not available');
            return false;
        }

        if (!Array.isArray(window.sdgScoresData)) {
            console.error('SDG scores data is not in the expected array format');
            return false;
        }

        if (window.sdgScoresData.length === 0) {
            console.warn('SDG scores data array is empty');
            return false;
        }

        return true;
    }

    // Main initialization function
    function initializeResultsDisplay() {
        console.log('Initializing results display...');
        console.log('Available global data:', {
            sdgScoresData: window.sdgScoresData,
            SDG_INFO: window.SDG_INFO,
            translations: window.translations,
            currentLanguage: window.currentLanguage
        });

        try {
            // Check dependencies first
            if (!checkDependencies()) {
                console.error('Required functions not found. Check script loading order.');
                return;
            }

            // Validate data
            if (!validateScoresData()) {
                console.error('Invalid or missing scores data');
                return;
            }

            console.log('Starting chart and breakdown rendering...');
            
            // Render the charts
            console.log('Rendering radar chart...');
            renderRadarChart(window.sdgScoresData);
            
            console.log('Rendering bar chart...');
            renderBarChart(window.sdgScoresData);

            // Update detailed breakdown
            console.log('Populating detailed breakdown...');
            populateDetailedBreakdown(window.sdgScoresData);

            // Set up print button if it exists
            const printButton = document.getElementById('print-results');
            if (printButton) {
                printButton.addEventListener('click', function() {
                    try {
                        window.print();
                    } catch (error) {
                        console.error('Error during print:', error);
                    }
                });
            }

            // Set up download button if it exists
            const downloadButton = document.getElementById('download-results');
            if (downloadButton) {
                downloadButton.addEventListener('click', function() {
                    try {
                        if (typeof generatePDF === 'function') {
                            generatePDF();
                        } else {
                            console.error('PDF generation function not available');
                        }
                    } catch (error) {
                        console.error('Error during PDF generation:', error);
                    }
                });
            }

            console.log('Results display initialization complete');
        } catch (error) {
            console.error('Error during results display initialization:', error);
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeResultsDisplay);
    } else {
        initializeResultsDisplay();
    }
})();