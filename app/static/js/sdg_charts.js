/**
 * SDG Assessment Charts - Enhanced Version
 * 
 * This script provides improved visualizations for SDG assessment data using Chart.js.
 * It implements radar charts, bar charts, and other visualizations with better
 * accessibility, responsiveness, and visual clarity.
 */

// Define official SDG colors with a more accessible color palette
// These colors maintain the SDG brand identity but with slight modifications for better contrast
const SDG_COLORS = {
    1: '#E5243B',  // No Poverty - Red
    2: '#DDA63A',  // Zero Hunger - Yellow
    3: '#4C9F38',  // Good Health - Green
    4: '#C5192D',  // Quality Education - Red
    5: '#FF3A21',  // Gender Equality - Orange-Red
    6: '#26BDE2',  // Clean Water - Blue
    7: '#FCC30B',  // Affordable Energy - Yellow
    8: '#A21942',  // Decent Work - Burgundy
    9: '#FD6925',  // Industry & Innovation - Orange
    10: '#DD1367', // Reduced Inequalities - Magenta
    11: '#FD9D24', // Sustainable Cities - Orange
    12: '#BF8B2E', // Responsible Consumption - Brown
    13: '#3F7E44', // Climate Action - Green
    14: '#0A97D9', // Life Below Water - Blue
    15: '#56C02B', // Life on Land - Green
    16: '#00689D', // Peace & Justice - Blue
    17: '#19486A'  // Partnerships - Navy Blue
};

// SDG groups with full names for better readability
const SDG_GROUPS = {
    people: {
        ids: [1, 2, 3, 4, 5],
        name: "People",
        description: "End poverty and hunger in all forms and ensure dignity and equality"
    },
    planet: {
        ids: [6, 12, 13, 14, 15],
        name: "Planet", 
        description: "Protect our planet's natural resources and climate for future generations"
    },
    prosperity: {
        ids: [7, 8, 9, 10, 11],
        name: "Prosperity",
        description: "Ensure prosperous and fulfilling lives in harmony with nature"
    },
    peace: {
        ids: [16],
        name: "Peace",
        description: "Foster peaceful, just and inclusive societies"
    },
    partnership: {
        ids: [17],
        name: "Partnership",
        description: "Implement the agenda through global partnership"
    }
};

// Group colors with improved alpha values for better contrast
const GROUP_COLORS = {
    people: 'rgba(0, 123, 255, 0.8)',      // Blue (primary)
    planet: 'rgba(40, 167, 69, 0.8)',      // Green (success)
    prosperity: 'rgba(255, 193, 7, 0.8)',  // Yellow (warning)
    peace: 'rgba(23, 162, 184, 0.8)',      // Cyan (info)
    partnership: 'rgba(25, 72, 106, 0.8)'  // Navy Blue (partnership)
};

// Chart configuration defaults for consistency
const CHART_DEFAULTS = {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    titleFontSize: 16,
    labelFontSize: 12,
    tooltipFontSize: 13,
    animation: {
        duration: 1200,
        easing: 'easeOutQuart'
    }
};

// Initialize storage API with fallback
window.storageAPI = window.storageAPI || {
    getWithTTL: function(key) {
        try {
            const item = localStorage.getItem(key);
            if (!item) return null;
            const data = JSON.parse(item);
            if (Date.now() < data.expiry) return data.value;
            localStorage.removeItem(key);
            return null;
        } catch (e) {
            console.error('Storage error:', e);
            return null;
        }
    },
    setWithTTL: function(key, value, ttlSeconds) {
        const expiry = Date.now() + ttlSeconds * 1000;
        localStorage.setItem(key, JSON.stringify({ value, expiry }));
    }
};

// Modified storage read function
function readRenderPromptFromStorage() {
    try {
        if (window.storageAPI && typeof window.storageAPI.getWithTTL === 'function') {
            const result = window.storageAPI.getWithTTL('renderPrompt');
            console.debug('Storage read:', result);
            return result || null;
        }
        return null;
    } catch (e) {
        console.error('Storage read failed:', e);
        return null;
    }
}

// Initialize all charts on the assessment results page
function initializeCharts(sdgScores, sdgNames) {
    try {
        // Validate inputs
        if (!sdgScores || !sdgNames) {
            throw new Error('SDG data not provided');
        }

        // Ensure Chart.js is loaded
        if (typeof Chart === 'undefined') {
            throw new Error('Chart.js library not loaded');
        }

        // Set defaults safely
        try {
            setChartDefaults();
        } catch (err) {
            console.error('Failed to set chart defaults:', err);
        }

        // Chart creation with fallbacks
        const charts = [
            { id: 'sdgRadarChart', creator: createRadarChart },
            { id: 'sdgBarChart', creator: createBarChart },
            { id: 'dimensionsChart', creator: createDimensionsChart },
            { id: 'strengthsGapsChart', creator: createStrengthsGapsChart },
            { id: 'categoriesPolarChart', creator: createCategoriesPolarChart }
        ];

        charts.forEach(({id, creator}) => {
            const canvas = document.getElementById(id);
            if (!canvas) {
                console.warn(`Canvas element not found: ${id}`);
                return;
            }
            
            try {
                creator(sdgScores, sdgNames);
            } catch (err) {
                console.error(`Chart creation failed for ${id}:`, err);
                canvas.innerHTML = `
                    <div class="chart-error p-3 text-center text-danger">
                        <i class="fas fa-exclamation-triangle"></i>
                        Chart failed to load
                    </div>
                `;
            }
        });

        // Benchmark comparison with null checks
        if (window.benchmarkScores?.length > 0) {
            try {
                createBenchmarkChart(
                    sdgScores, 
                    window.benchmarkScores, 
                    sdgNames
                );
            } catch (err) {
                console.error('Benchmark chart failed:', err);
            }
        }

        // Setup event handlers
        try {
            addResizeHandler();
            setupInteractiveLegends();
        } catch (err) {
            console.error('Event setup failed:', err);
        }

    } catch (err) {
        console.error('SDG Charts initialization failed:', err);
        // Fallback UI for complete failure
        document.querySelectorAll('.chart-container').forEach(container => {
            container.innerHTML = `
                <div class="chart-error p-4 text-center">
                    <h5>Data Visualization Failed to Load</h5>
                    <p class="text-muted">Please refresh the page or contact support</p>
                </div>
            `;
        });
    }
}

// Add safe data access helper
function safeAccess(obj, ...props) {
    return props.reduce((acc, prop) => {
        try {
            return acc?.[prop];
        } catch {
            return undefined;
        }
    }, obj);
}

/**
 * Normalize SDG scores data to handle different formats
 * @param {Array|Object} sdgScores - SDG scores in array or object format
 * @returns {Array} - Normalized array of SDG score objects
 */
function normalizeSDGData(sdgScores) {
    if (!sdgScores) return [];
    
    // If already array format, return copy
    if (Array.isArray(sdgScores)) {
        return JSON.parse(JSON.stringify(sdgScores));
    }
    
    // Convert object format to array
    const normalizedData = [];
    Object.keys(sdgScores).forEach(key => {
        const num = parseInt(key);
        if (!isNaN(num)) {
            const score = sdgScores[key];
            if (typeof score === 'object') {
                normalizedData.push({
                    number: num,
                    ...score
                });
            } else if (typeof score === 'number') {
                normalizedData.push({
                    number: num,
                    total_score: score
                });
            }
        }
    });
    
    return normalizedData.sort((a, b) => a.number - b.number);
}

/**
 * Calculate the average score for a dimension (group of SDGs)
 * @param {Object|Array} sdgScores - Object or Array containing the scores for each SDG
 * @param {Array} sdgIds - Array of SDG IDs to include in this dimension
 * @returns {number} - Average score for the dimension (0-10)
 */
function calculateDimensionScore(sdgScores, sdgIds) {
    let validScores = [];
    
    // Collect valid scores with proper type conversion
    sdgIds.forEach(num => {
        let score;
        if (Array.isArray(sdgScores)) {
            // Find score in array format
            const sdg = sdgScores.find(s => parseInt(s.number) === parseInt(num));
            score = sdg ? parseFloat(sdg.total_score) : null;
        } else {
            // Find score in object format
            score = sdgScores[num] ? parseFloat(sdgScores[num].total_score) : null;
        }
        
        if (score !== null && !isNaN(score)) {
            validScores.push(score);
        }
    });
    
    // Calculate average
    if (validScores.length === 0) return 0;
    const sum = validScores.reduce((total, score) => total + score, 0);
    return parseFloat((sum / validScores.length).toFixed(1));
}

/**
 * Set global Chart.js defaults for consistent styling
 */
function setChartDefaults() {
    Chart.defaults.font.family = CHART_DEFAULTS.fontFamily;
    Chart.defaults.color = '#333333';
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(0, 0, 0, 0.8)';
    Chart.defaults.plugins.tooltip.titleFont = { weight: 'bold', size: CHART_DEFAULTS.tooltipFontSize };
    Chart.defaults.plugins.tooltip.bodyFont = { size: CHART_DEFAULTS.tooltipFontSize };
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.plugins.tooltip.cornerRadius = 6;
    Chart.defaults.plugins.tooltip.displayColors = true;
    Chart.defaults.plugins.tooltip.boxPadding = 4;
    
    // Ensure charts are accessible
    Chart.defaults.plugins.tooltip.titleAlign = 'left';
    Chart.defaults.plugins.tooltip.bodyAlign = 'left';
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
}

/**
 * Initialize all SDG charts with comprehensive error handling
 * @param {Object|Array} sdgScores - Object or Array containing the scores for each SDG
 * @param {Object} sdgNames - Object containing the names of each SDG
 */
function initializeCharts(sdgScores, sdgNames) {
    try {
        // Add debugging info
        console.log("SDG scores data:", sdgScores);
        console.log("SDG names lookup:", sdgNames);
        
        // Validate inputs with better error messages
        if (!sdgScores) {
            console.error("SDG scores data is missing or invalid");
            throw new Error('SDG data not provided');
        }

        // Ensure Chart.js is loaded with explicit check
        if (typeof Chart === 'undefined') {
            console.error("Chart.js library not found in global scope");
            document.querySelectorAll('.chart-container').forEach(container => {
                container.innerHTML = `
                    <div class="alert alert-warning p-3">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Chart.js library not loaded. Please refresh the page or check console for errors.
                    </div>
                `;
            });
            throw new Error('Chart.js library not loaded');
        }

        // Set defaults safely
        try {
            setChartDefaults();
            console.log("Chart defaults set successfully");
        } catch (err) {
            console.error('Failed to set chart defaults:', err);
        }

        // Chart creation with explicit canvas checks
        console.log("Attempting to create charts...");
        
        // List all expected canvas elements
        const chartCanvases = [
            'sdgRadarChart',
            'sdgBarChart',
            'dimensionsChart',
            'strengthsGapsChart',
            'categoriesPolarChart'
        ];
        
        // Check if canvases exist
        const missingCanvases = chartCanvases.filter(id => !document.getElementById(id));
        if (missingCanvases.length > 0) {
            console.warn(`Missing chart canvases: ${missingCanvases.join(', ')}`);
        }
        
        // Add loading indicators to all chart containers
        document.querySelectorAll('.chart-container').forEach(container => {
            container.classList.add('loading');
        });
        
        // Create radar chart (always try this first)
        if (document.getElementById('sdgRadarChart')) {
            console.log("Creating radar chart...");
            try {
                createRadarChart(sdgScores, sdgNames);
                console.log("Radar chart created successfully");
                // Remove loading indicator
                const container = document.getElementById('sdgRadarChart').closest('.chart-container');
                if (container) {
                    container.classList.remove('loading');
                }
            } catch (err) {
                console.error("Error creating radar chart:", err);
                const container = document.getElementById('sdgRadarChart').closest('.chart-container');
                if (container) {
                    container.classList.remove('loading');
                    container.innerHTML = `
                        <div class="alert alert-warning">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Radar chart could not be created. Please refresh the page.
                        </div>
                    `;
                }
            }
        }
        
        // Create bar chart
        if (document.getElementById('sdgBarChart')) {
            console.log("Creating bar chart...");
            try {
                createBarChart(sdgScores, sdgNames);
                console.log("Bar chart created successfully");
                // Remove loading indicator
                const container = document.getElementById('sdgBarChart').closest('.chart-container');
                if (container) {
                    container.classList.remove('loading');
                }
            } catch (err) {
                console.error("Error creating bar chart:", err);
                const container = document.getElementById('sdgBarChart').closest('.chart-container');
                if (container) {
                    container.classList.remove('loading');
                    container.innerHTML = `
                        <div class="alert alert-warning">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Score breakdown chart could not be created. Please refresh the page.
                        </div>
                    `;
                }
            }
        }
        
        // Create dimensions chart
        if (document.getElementById('dimensionsChart')) {
            console.log("Creating dimensions chart...");
            try {
                createDimensionsChart(sdgScores);
                console.log("Dimensions chart created successfully");
                // Remove loading indicator
                const container = document.getElementById('dimensionsChart').closest('.chart-container');
                if (container) {
                    container.classList.remove('loading');
                }
            } catch (err) {
                console.error("Error creating dimensions chart:", err);
                const container = document.getElementById('dimensionsChart').closest('.chart-container');
                if (container) {
                    container.classList.remove('loading');
                    container.innerHTML = `
                        <div class="alert alert-warning">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Dimensions chart could not be created. Please refresh the page.
                        </div>
                    `;
                }
            }
        }
        
        // Create strengths and gaps chart
        if (document.getElementById('strengthsGapsChart')) {
            console.log("Creating strengths/gaps chart...");
            try {
                createStrengthsGapsChart(sdgScores, sdgNames);
                console.log("Strengths/gaps chart created successfully");
                // Remove loading indicator
                const container = document.getElementById('strengthsGapsChart').closest('.chart-container');
                if (container) {
                    container.classList.remove('loading');
                }
            } catch (err) {
                console.error("Error creating strengths/gaps chart:", err);
                const container = document.getElementById('strengthsGapsChart').closest('.chart-container');
                if (container) {
                    container.classList.remove('loading');
                    container.innerHTML = `
                        <div class="alert alert-warning">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Strengths and improvement areas chart could not be created. Please refresh the page.
                        </div>
                    `;
                }
            }
        }
        
        // Create categories polar chart
        if (document.getElementById('categoriesPolarChart')) {
            console.log("Creating categories polar chart...");
            try {
                createCategoriesPolarChart(sdgScores);
                console.log("Categories polar chart created successfully");
                // Remove loading indicator
                const container = document.getElementById('categoriesPolarChart').closest('.chart-container');
                if (container) {
                    container.classList.remove('loading');
                }
            } catch (err) {
                console.error("Error creating categories polar chart:", err);
                const container = document.getElementById('categoriesPolarChart').closest('.chart-container');
                if (container) {
                    container.classList.remove('loading');
                    container.innerHTML = `
                        <div class="alert alert-warning">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Categories chart could not be created. Please refresh the page.
                        </div>
                    `;
                }
            }
        }

        // Benchmark comparison with null checks
        if (document.getElementById('comparisonChart')) {
            console.log("Creating benchmark comparison chart...");
            if (window.benchmarkScores?.length > 0) {
                try {
                    createBenchmarkChart(
                        sdgScores, 
                        window.benchmarkScores, 
                        sdgNames
                    );
                    console.log("Benchmark chart created successfully");
                    // Remove loading indicator
                    const container = document.getElementById('comparisonChart').closest('.chart-container');
                    if (container) {
                        container.classList.remove('loading');
                    }
                } catch (err) {
                    console.error('Benchmark chart failed:', err);
                    const container = document.getElementById('comparisonChart').closest('.chart-container');
                    if (container) {
                        container.classList.remove('loading');
                        container.innerHTML = `
                            <div class="alert alert-warning">
                                <i class="fas fa-exclamation-triangle me-2"></i>
                                Benchmark comparison chart could not be created. Please refresh the page.
                            </div>
                        `;
                    }
                }
            } else {
                console.warn("No benchmark data available for comparison chart");
                const container = document.getElementById('comparisonChart').closest('.chart-container');
                if (container) {
                    container.classList.remove('loading');
                    container.innerHTML = `
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle me-2"></i>
                            No benchmark data available for comparison at this time.
                        </div>
                    `;
                }
            }
        }

        // Setup event handlers
        try {
            console.log("Setting up event handlers...");
            if (typeof addResizeHandler === 'function') {
                addResizeHandler();
            }
            if (typeof setupInteractiveLegends === 'function') {
                setupInteractiveLegends();
            }
            console.log("Event handlers set up successfully");
        } catch (err) {
            console.error('Event setup failed:', err);
        }

    } catch (err) {
        console.error('SDG Charts initialization failed:', err);
        // Fallback UI for complete failure
        document.querySelectorAll('.chart-container').forEach(container => {
            container.innerHTML = `
                <div class="chart-error p-4 text-center">
                    <h5>Data Visualization Failed to Load</h5>
                    <p class="text-muted">Please refresh the page or contact support</p>
                </div>
            `;
        });
    }
}

/**
 * Create an enhanced SDG radar chart with better tooltips and accessibility
 * @param {Object|Array} sdgScores - Object or Array containing the scores for each SDG
 * @param {Object} sdgNames - Object containing the names of each SDG
 */
function createRadarChart(sdgScores, sdgNames) {
    try {
        const ctx = document.getElementById('sdgRadarChart');
        if (!ctx) {
            console.warn("Radar chart container not found in the DOM");
            return;
        }
        
        // Process data for radar chart - handle array format coming from Flask
        const sdgNumbers = Array.isArray(sdgScores) 
            ? sdgScores.map(s => s.number).sort((a, b) => a - b)
            : Object.keys(SDG_COLORS).sort((a, b) => a - b);
            
        const labels = sdgNumbers.map(num => `SDG ${num}`);
        
        // Access data correctly based on format
        const data = sdgNumbers.map(num => {
            if (Array.isArray(sdgScores)) {
                const sdg = sdgScores.find(s => s.number == num);
                return sdg && sdg.total_score !== undefined ? sdg.total_score : 0;
            } else {
                return sdgScores[num]?.total_score || 0;
            }
        });
        
        const pointBackgroundColors = sdgNumbers.map(num => SDG_COLORS[num] || '#cccccc');
    
    const radarData = {
        labels: labels,
        datasets: [{
            label: 'Impact Score',
            data: data,
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgb(54, 162, 235)',
            borderWidth: 2,
            pointBackgroundColor: pointBackgroundColors,
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: pointBackgroundColors,
            pointRadius: 5,
            pointHoverRadius: 7
        }]
    };

    // Chart configuration with enhanced options
    const config = {
        type: 'radar',
        data: radarData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: false,
                    text: 'SDG Performance Overview',
                    font: {
                        size: CHART_DEFAULTS.titleFontSize,
                        weight: 'bold'
                    },
                    padding: {
                        top: 10,
                        bottom: 20
                    }
                },
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        title: function(tooltipItems) {
                            const idx = tooltipItems[0].dataIndex;
                            const sdgNum = sdgNumbers[idx];
                            const sdgName = sdgNames[sdgNum] || `SDG ${sdgNum}`;
                            return `${sdgName}`;
                        },
                        label: function(context) {
                            return `Score: ${context.raw.toFixed(1)}/10`;
                        }
                    }
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 10,
                    ticks: {
                        stepSize: 2,
                        font: {
                            size: 11
                        }
                    },
                    pointLabels: {
                        font: {
                            size: CHART_DEFAULTS.labelFontSize
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            },
            layout: {
                padding: {
                    top: 20,
                    bottom: 30,
                    left: 20,
                    right: 20
                }
            },
            animation: CHART_DEFAULTS.animation
        }
    };

    // Create and store chart instance
    window.radarChart = new Chart(ctx, config);
    // Log chart creation
    console.log('SDG Radar chart created successfully');
    return window.radarChart;
    } catch (error) {
        console.error("Error creating radar chart:", error);
        const container = document.getElementById('sdgRadarChart')?.closest('.chart-container');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Chart could not be created. Please refresh the page or try again later.
                </div>
            `;
        }
    }
}

/**
 * Create an enhanced bar chart for SDG score comparison
 * @param {Object|Array} sdgScores - Object or Array containing the scores for each SDG
 * @param {Object} sdgNames - Object containing the names of each SDG
 */
function createBarChart(sdgScores, sdgNames) {
    try {
        const ctx = document.getElementById('sdgBarChart');
        if (!ctx) {
            console.warn("Bar chart container not found in the DOM");
            return;
        }
    
    // Process data for bar chart - handle array format coming from Flask
    const sdgNumbers = Array.isArray(sdgScores) 
        ? sdgScores.map(s => s.number).sort((a, b) => a - b)
        : Object.keys(SDG_COLORS).sort((a, b) => a - b);
    
    const labels = sdgNumbers.map(num => `SDG ${num}`);
    
    // Get direct scores based on data format
    const directScores = sdgNumbers.map(num => {
        if (Array.isArray(sdgScores)) {
            const sdg = sdgScores.find(s => s.number == num);
            return sdg && sdg.direct_score !== undefined ? sdg.direct_score : 0;
        } else {
            return sdgScores[num]?.direct_score || 0;
        }
    });
    
    // Get bonus scores based on data format
    const bonusScores = sdgNumbers.map(num => {
        if (Array.isArray(sdgScores)) {
            const sdg = sdgScores.find(s => s.number == num);
            return sdg && sdg.bonus_score !== undefined ? sdg.bonus_score : 0;
        } else {
            return sdgScores[num]?.bonus_score || 0;
        }
    });
    
    const backgroundColor = sdgNumbers.map(num => SDG_COLORS[num] || '#cccccc');
    
    const barData = {
        labels: labels,
        datasets: [
            {
                label: 'Direct Score',
                data: directScores,
                backgroundColor: sdgNumbers.map(num => `${SDG_COLORS[num]}CC`), // More opacity for better visibility
                borderColor: sdgNumbers.map(num => SDG_COLORS[num]),
                borderWidth: 1,
                barPercentage: 0.8,
                categoryPercentage: 0.9
            },
            {
                label: 'Bonus Score',
                data: bonusScores,
                backgroundColor: sdgNumbers.map(num => `${SDG_COLORS[num]}77`), // Less opacity for visual distinction
                borderColor: sdgNumbers.map(num => SDG_COLORS[num]),
                borderWidth: 1,
                barPercentage: 0.8,
                categoryPercentage: 0.9
            }
        ]
    };

    // Enhanced chart configuration
    const config = {
        type: 'bar',
        data: barData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: false,
                    text: 'SDG Score Breakdown',
                    font: {
                        size: CHART_DEFAULTS.titleFontSize,
                        weight: 'bold'
                    },
                    padding: {
                        top: 10,
                        bottom: 20
                    }
                },
                legend: {
                    position: 'top',
                    labels: {
                        font: {
                            size: CHART_DEFAULTS.labelFontSize
                        },
                        padding: 15,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            const sdgNum = context[0].label.replace('SDG ', '');
                            return `${context[0].label}: ${sdgNames[sdgNum] || ''}`;
                        },
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += context.parsed.y.toFixed(1);
                            return label;
                        },
                        footer: function(tooltipItems) {
                            let sum = 0;
                            tooltipItems.forEach(function(tooltipItem) {
                                sum += tooltipItem.parsed.y;
                            });
                            return 'Total: ' + sum.toFixed(1);
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Sustainable Development Goals',
                        font: {
                            size: CHART_DEFAULTS.labelFontSize,
                            weight: '600'
                        },
                        padding: {top: 10, bottom: 0}
                    },
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    },
                    stacked: true
                },
                y: {
                    beginAtZero: true,
                    max: 10,
                    title: {
                        display: true,
                        text: 'Score (out of 10)',
                        font: {
                            size: CHART_DEFAULTS.labelFontSize,
                            weight: '600'
                        },
                        padding: {bottom: 10}
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        stepSize: 2,
                        font: {
                            size: 11
                        }
                    },
                    stacked: true
                }
            },
            layout: {
                padding: {
                    top: 20,
                    bottom: 30,
                    left: 20,
                    right: 20
                }
            },
            animation: CHART_DEFAULTS.animation
        },
        layout: {
            padding: {
                top: 5,
                bottom: 15, // Increased bottom padding to further prevent cut-off
                left: 5,
                right: 5
            }
        }
    };

    // Create and store chart instance
    window.barChart = new Chart(ctx, config);
    // Log chart creation
    console.log('SDG Bar chart created successfully');
    return window.barChart;
    } catch (error) {
        console.error("Error creating bar chart:", error);
        const container = document.getElementById('sdgBarChart')?.closest('.chart-container');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Chart could not be created. Please refresh the page or try again later.
                </div>
            `;
        }
    }
}

/**
 * Create a categories polar chart with enhanced visualization
 * @param {Object|Array} sdgScores - Object or Array containing the scores for each SDG
 */
function createCategoriesPolarChart(sdgScores) {
    try {
        const ctx = document.getElementById('categoriesPolarChart');
        if (!ctx) {
            console.warn("Categories polar chart container not found in the DOM");
            return;
        }
        
        // Calculate category averages
        const categories = {
            'People (SDGs 1-5)': calculateDimensionScore(sdgScores, SDG_GROUPS.people.ids),
            'Planet (SDGs 6, 12-15)': calculateDimensionScore(sdgScores, SDG_GROUPS.planet.ids),
            'Prosperity (SDGs 7-11)': calculateDimensionScore(sdgScores, SDG_GROUPS.prosperity.ids),
            'Peace (SDGs 16-17)': calculateDimensionScore(sdgScores, SDG_GROUPS.peace.ids)
        };
        
        // Prepare data for chart
        const data = {
            labels: Object.keys(categories),
            datasets: [{
                data: Object.values(categories),
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)',  // Red for People
                    'rgba(75, 192, 192, 0.7)',  // Green for Planet
                    'rgba(255, 159, 64, 0.7)',  // Orange for Prosperity
                    'rgba(54, 162, 235, 0.7)'   // Blue for Peace & Partnership
                ],
                borderColor: [
                    'rgb(255, 99, 132)',
                    'rgb(75, 192, 192)',
                    'rgb(255, 159, 64)',
                    'rgb(54, 162, 235)'
                ],
                borderWidth: 1
            }]
        };
        
        // Enhanced chart configuration
        const config = {
            type: 'polarArea',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 10,
                        ticks: {
                            stepSize: 2,
                            font: {
                                size: 11
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: {
                                size: CHART_DEFAULTS.legendFontSize
                            },
                            padding: 15
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw.toFixed(1);
                                return `${label}: ${value}/10`;
                            }
                        }
                    }
                },
                layout: {
                    padding: {
                        top: 5,
                        bottom: 15,
                        left: 5,
                        right: 5
                    }
                },
                layout: {
                padding: {
                    top: 20,
                    bottom: 30,
                    left: 20,
                    right: 20
                }
            },
            animation: CHART_DEFAULTS.animation
            }
        };
        
        // Create and store chart instance
        window.categoriesPolarChart = new Chart(ctx, config);
        
        // Log chart creation
        console.log('Categories polar chart created successfully');
        
    } catch (error) {
        console.error("Error creating categories polar chart:", error);
        const container = document.getElementById('categoriesPolarChart')?.closest('.chart-container');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Chart could not be created. Please refresh the page or try again later.
                </div>
            `;
        }
    }
}

/**
 * Create a dimensions doughnut chart with enhanced interactivity
 * @param {Object|Array} sdgScores - Object or Array containing the scores for each SDG
 */
function createDimensionsChart(sdgScores) {
    const ctx = document.getElementById('dimensionsChart');
    if (!ctx) {
        console.warn("Dimensions chart container not found in the DOM");
        return;
    }
    
    // Calculate scores for each dimension
    const dimensions = {
        people: calculateDimensionScore(sdgScores, SDG_GROUPS.people.ids),
        planet: calculateDimensionScore(sdgScores, SDG_GROUPS.planet.ids),
        prosperity: calculateDimensionScore(sdgScores, SDG_GROUPS.prosperity.ids),
        peace: calculateDimensionScore(sdgScores, SDG_GROUPS.peace.ids),
        partnership: calculateDimensionScore(sdgScores, SDG_GROUPS.partnership.ids)
    };
    
    // Prepare data for chart
    const labels = [
        SDG_GROUPS.people.name, 
        SDG_GROUPS.planet.name, 
        SDG_GROUPS.prosperity.name, 
        SDG_GROUPS.peace.name,
        SDG_GROUPS.partnership.name
    ];
    
    const data = [
        dimensions.people,
        dimensions.planet,
        dimensions.prosperity,
        dimensions.peace,
        dimensions.partnership
    ];
    
    const backgroundColors = [
        GROUP_COLORS.people,
        GROUP_COLORS.planet,
        GROUP_COLORS.prosperity,
        GROUP_COLORS.peace,
        GROUP_COLORS.partnership
    ];
    
    const borderColors = backgroundColors.map(color => color.replace('0.8', '1'));
    
    const dimensionsData = {
        labels: labels,
        datasets: [{
            data: data,
            backgroundColor: backgroundColors,
            borderColor: borderColors,
            borderWidth: 1,
            hoverOffset: 15
        }]
    };

    // Enhanced chart configuration
    const config = {
        type: 'doughnut',
        data: dimensionsData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '50%',
            plugins: {
                title: {
                    display: false,
                    text: 'SDG Dimensions Overview',
                    font: {
                        size: CHART_DEFAULTS.titleFontSize,
                        weight: 'bold'
                    },
                    padding: {
                        top: 10,
                        bottom: 20
                    }
                },
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 15,
                        padding: 15,
                        font: {
                            size: CHART_DEFAULTS.labelFontSize
                        },
                        generateLabels: function(chart) {
                            const chartData = chart.data;
                            if (chartData.labels.length && chartData.datasets.length) {
                                const dataset = chartData.datasets[0]; // Assuming one dataset
                                return chartData.labels.map((label, i) => {
                                    const meta = chart.getDatasetMeta(0); // Assuming one dataset
                                    const style = meta.controller.getStyle(i);
                                    const score = dataset.data[i]; // Get score from dataset data

                                    return {
                                        text: `${label} (${score !== undefined ? score.toFixed(1) : 'N/A'})`,
                                        fillStyle: style.backgroundColor,
                                        strokeStyle: style.borderColor,
                                        lineWidth: style.borderWidth,
                                        hidden: !chart.isDatasetVisible(0) || isNaN(dataset.data[i]), // Hide if dataset hidden or data invalid
                                        index: i
                                    };
                                });
                            }
                            return []; // Return empty array if data is missing
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return context[0].label;
                        },
                        label: function(context) {
                            const dimensionKey = context.label ? context.label.toLowerCase().split(' ')[0].replace('&', '').trim() : '';
                            const description = SDG_GROUPS[dimensionKey]?.description || '';
                            const scoreText = (typeof context.raw === 'number' && !isNaN(context.raw)) ? `Score: ${context.raw.toFixed(1)}/10` : 'Score: N/A';
                            return [scoreText, description];
                        }
                    }
                }
            },
            layout: {
                padding: {
                    top: 20,
                    bottom: 30,
                    left: 20,
                    right: 20
                }
            },
            animation: CHART_DEFAULTS.animation
        },
        layout: {
            padding: {
                top: 5,
                bottom: 15, // Increased bottom padding to further prevent cut-off
                left: 5,
                right: 5
            }
        }
    };

    // Create and store chart instance
    window.dimensionsChart = new Chart(ctx, config);
    // Log chart creation
    console.log('SDG Dimensions chart created successfully');
    return window.dimensionsChart;
}

/**
 * Create a horizontal bar chart showing strengths and improvement areas
 * @param {Object} sdgScores - Object containing the scores for each SDG
 * @param {Object} sdgNames - Object containing the names of each SDG
 */
function createStrengthsGapsChart(sdgScores, sdgNames) {
    const ctx = document.getElementById('strengthsGapsChart');
    if (!ctx) {
        console.warn("Strengths/Gaps chart container not found in the DOM");
        return;
    }
    
    // Sort SDGs by score
    const sortedSDGs = Object.keys(SDG_COLORS)
        .map(num => {
            const score = getScoreWithFallback(sdgScores, num);
            const name = sdgNames[num] || `SDG ${num}`;
            // Validate score and name
            if (score === undefined || score === null || isNaN(score)) {
                console.error('Invalid score for SDG', num, score);
            }
            if (!name) {
                console.error('Invalid name for SDG', num, name);
            }
            return {
                number: parseInt(num),
                score: (score === undefined || score === null || isNaN(score)) ? 0 : score,
                name: name || `SDG ${num}`
            };
        })
        .sort((a, b) => b.score - a.score);
    
    // Take top 5 and bottom 5
    const topSDGs = sortedSDGs.slice(0, 5);
    const bottomSDGs = sortedSDGs.slice(-5).reverse();
    
    // Prepare data for chart
    const strengthsGapsData = {
        labels: [
            ...topSDGs.map((item, idx) => {
                if (!item || typeof item.number === 'undefined' || typeof item.name === 'undefined') {
                    console.error('Invalid topSDGs item at index', idx, item);
                    return 'N/A';
                }
                // Defensive: handle weird/undefined data
                if (item.number === null || item.name === null) return 'N/A';
                return `SDG ${item.number}: ${item.name}`;
            }),
            ...bottomSDGs.map((item, idx) => {
                if (!item || typeof item.number === 'undefined' || typeof item.name === 'undefined') {
                    console.error('Invalid bottomSDGs item at index', idx, item);
                    return 'N/A';
                }
                if (item.number === null || item.name === null) return 'N/A';
                return `SDG ${item.number}: ${item.name}`;
            })
        ],
        datasets: [{
            label: 'Strengths',
            data: [
                ...topSDGs.map((item, idx) => {
                    if (!item || typeof item.score === 'undefined' || item.score === null || isNaN(item.score)) {
                        console.error('Invalid score in topSDGs at index', idx, item);
                        return null;
                    }
                    return item.score;
                }),
                ...Array(5).fill(null)
            ],
            backgroundColor: topSDGs.map(item => SDG_COLORS[item.number]),
            borderColor: 'rgba(0, 0, 0, 0.1)',
            borderWidth: 1,
            barThickness: 20
        }, {
            label: 'Improvement Areas',
            data: [
                ...Array(5).fill(null),
                ...bottomSDGs.map((item, idx) => {
                    if (!item || typeof item.score === 'undefined' || item.score === null || isNaN(item.score)) {
                        console.error('Invalid score in bottomSDGs at index', idx, item);
                        return null;
                    }
                    return item.score;
                })
            ],
            backgroundColor: bottomSDGs.map(item => SDG_COLORS[item.number]),
            borderColor: 'rgba(0, 0, 0, 0.1)',
            borderWidth: 1,
            barThickness: 20
        }]
    };

    // Enhanced chart configuration
    const config = {
        type: 'bar',
        data: strengthsGapsData,
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Strengths & Areas for Improvement',
                    font: {
                        size: CHART_DEFAULTS.titleFontSize,
                        weight: 'bold'
                    },
                    padding: {
                        top: 10,
                        bottom: 20
                    }
                },
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: {
                            size: CHART_DEFAULTS.labelFontSize
                        },
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            if (context.raw === null) return '';
                            return `Score: ${context.raw.toFixed(1)}/10`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 10,
                    title: {
                        display: true,
                        text: 'Impact Score',
                        font: {
                            size: CHART_DEFAULTS.labelFontSize,
                            weight: '600'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        stepSize: 2
                    }
                },
                y: {
                    grid: {
                        display: false
                    }
                }
            },
            layout: {
                padding: {
                    top: 20,
                    bottom: 30,
                    left: 20,
                    right: 20
                }
            },
            animation: CHART_DEFAULTS.animation
        }
    };

    // Create and store chart instance
    window.strengthsGapsChart = new Chart(ctx, config);
    // Log chart creation
    console.log('SDG Strengths/Gaps chart created successfully');
    return window.strengthsGapsChart;
}

/**
 * Create a polar area chart for SDG category comparison
 * @param {Object} sdgScores - Object containing the scores for each SDG
 */
function createCategoriesPolarChart(sdgScores) {
    const ctx = document.getElementById('categoriesPolarChart');
    if (!ctx) {
        console.warn("Categories polar chart container not found in the DOM");
        return;
    }
    
    // Calculate category averages
    const categories = {
        'People (SDGs 1-5)': calculateDimensionScore(sdgScores, SDG_GROUPS.people.ids),
        'Planet (SDGs 6, 12-15)': calculateDimensionScore(sdgScores, SDG_GROUPS.planet.ids),
        'Prosperity (SDGs 7-11)': calculateDimensionScore(sdgScores, SDG_GROUPS.prosperity.ids),
        'Peace (SDGs 16-17)': calculateDimensionScore(sdgScores, SDG_GROUPS.peace.ids)
    };
    
    const categoriesData = {
        labels: Object.keys(categories),
        datasets: [{
            data: Object.values(categories),
            backgroundColor: [
                GROUP_COLORS.people,
                GROUP_COLORS.planet,
                GROUP_COLORS.prosperity,
                GROUP_COLORS.peace
            ],
            borderColor: [
                GROUP_COLORS.people.replace('0.8', '1'),
                GROUP_COLORS.planet.replace('0.8', '1'),
                GROUP_COLORS.prosperity.replace('0.8', '1'),
                GROUP_COLORS.peace.replace('0.8', '1')
            ],
            borderWidth: 1
        }]
    };

    // Enhanced chart configuration
    const config = {
        type: 'polarArea',
        data: categoriesData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: false,
                    text: 'SDG Categories Performance',
                    font: {
                        size: CHART_DEFAULTS.titleFontSize,
                        weight: 'bold'
                    },
                    padding: {
                        top: 10,
                        bottom: 20
                    }
                },
                legend: {
                    position: 'right',
                    labels: {
                        font: {
                            size: CHART_DEFAULTS.labelFontSize
                        },
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.raw.toFixed(1)}/10`;
                        }
                    }
                },
                datalabels: {
                    display: true,
                    color: '#fff',
                    font: {
                        weight: 'bold'
                    },
                    formatter: function(value) {
                        return value.toFixed(1);
                    }
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 10,
                    ticks: {
                        stepSize: 2,
                        backdropColor: 'rgba(255, 255, 255, 0.75)'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    angleLines: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            },
            layout: {
                padding: {
                    top: 20,
                    bottom: 30,
                    left: 20,
                    right: 20
                }
            },
            animation: CHART_DEFAULTS.animation
        }
    };

    // Create and store chart instance
    window.categoriesPolarChart = new Chart(ctx, config);
    // Log chart creation
    console.log('SDG Categories polar chart created successfully');
    return window.categoriesPolarChart;
}

/**
 * Create benchmark comparison chart
 * @param {Array} userScores - User's SDG scores
 * @param {Array} benchmarkScores - Benchmark SDG scores
 * @param {String} chartId - ID of the chart container for comparison
 */
function createBenchmarkChart(userScores, benchmarkScores, sdgNames) {
    const ctx = document.getElementById('comparisonChart');
    if (!ctx) {
        console.warn("Comparison chart container not found");
        return;
    }

    // Prepare data for comparison
    const labels = [];
    const userData = [];
    const benchmarkData = [];
    
    Object.keys(SDG_COLORS).sort((a, b) => a - b).forEach(num => {
        const userScore = userScores.find(s => s.number == num)?.total_score || 0;
        const benchmarkScore = benchmarkScores.find(s => s.number == num)?.total_score || 0;
        
        if (userScore > 0 || benchmarkScore > 0) {
            labels.push(`SDG ${num}: ${sdgNames[num] || num}`);
            userData.push(userScore);
            benchmarkData.push(benchmarkScore);
        }
    });

    // Chart configuration
    const config = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Your Scores',
                    data: userData,
                    backgroundColor: SDG_COLORS['17'], // Use primary SDG color
                    borderColor: 'rgba(37, 99, 235, 1)',
                    borderWidth: 1,
                    borderRadius: 4,
                    barPercentage: 0.8
                },
                {
                    label: 'Industry Benchmark',
                    data: benchmarkData,
                    backgroundColor: 'rgba(100, 100, 100, 0.7)',
                    borderColor: 'rgba(70, 70, 70, 1)',
                    borderWidth: 1,
                    borderRadius: 4,
                    barPercentage: 0.8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Your Scores vs Industry Benchmark',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            return `${context.dataset.label}: ${context.raw.toFixed(1)}/10`;
                        },
                        footer: (context) => {
                            const diff = (context[0].raw - context[1].raw).toFixed(1);
                            return `Difference: ${diff > 0 ? '+' : ''}${diff}`;
                        }
                    }
                },
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10,
                    title: {
                        display: true,
                        text: 'Score (out of 10)'
                    }
                },
                x: {
                    ticks: {
                        callback: function(value) {
                            return this.getLabelForValue(value).split(':')[0];
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    };

    // Create and store chart instance
    window.comparisonChart = new Chart(ctx, config);
    console.log('Benchmark comparison chart created');
}

/**
 * Generate PDF report of the assessment with custom styling
 * @param {String} projectName - Name of the project
 * @param {Object} sdgScores - Object containing the scores for each SDG
 * @param {Object} sdgNotes - Object containing the notes for each SDG
 */
function generatePDFReport(projectName, sdgScores, sdgNotes) {
    console.log('Preparing to generate PDF report');
    
    // Notify user that the feature is in development
    alert('PDF generation is in progress. This feature will be available in the next update.');
    
    // This would implement a PDF generation library like jsPDF
    // For now, we'll just log what this function would do
    console.log('PDF report would include:');
    console.log('- Project name:', projectName);
    console.log('- Number of SDGs with data:', Object.keys(sdgScores).length);
    console.log('- Number of SDGs with notes:', Object.keys(sdgNotes || {}).length);
    
    // In full implementation, we would:
    // 1. Create PDF document
    // 2. Add project details and summary
    // 3. Convert charts to images
    // 4. Add SDG scores and notes
    // 5. Format and style consistently
    // 6. Generate for download
}

/**
 * Calculate the average score for a dimension
 * @param {Object} sdgScores - Object containing the scores for each SDG
 * @param {Array} sdgNumbers - Array of SDG numbers in this dimension
 * @returns {Number} - Average score for the dimension
 */
function calculateDimensionScore(sdgScores, sdgNumbers) {
    let validScores = [];
    
    // Collect valid scores
    sdgNumbers.forEach(num => {
        const score = getScoreWithFallback(sdgScores, num);
        if (score !== null && score !== undefined && !isNaN(score)) {
            validScores.push(score);
        }
    });
    
    // If no valid scores, return 0
    if (validScores.length === 0) {
        return 0;
    }
    
    // Calculate average
    const sum = validScores.reduce((total, score) => total + score, 0);
    return parseFloat((sum / validScores.length).toFixed(1));
}

/**
 * Get score with fallback for missing values
 * @param {Object} sdgScores - Object containing the scores for each SDG
 * @param {Number|String} sdgNumber - SDG number to get score for
 * @returns {Number} - Score value or 0 if not available
 */
function getScoreWithFallback(sdgScores, sdgNumber) {
    if (!sdgScores) return 0;
    
    const num = typeof sdgNumber === 'string' ? parseInt(sdgNumber) : sdgNumber;
    if (isNaN(num)) return 0;

    if (Array.isArray(sdgScores)) {
        const sdg = sdgScores.find(s => s?.number === num);
        return sdg?.total_score ?? 0;
    }
    
    const score = sdgScores[num];
    return score?.total_score ?? (typeof score === 'number' ? score : 0);
}

/**
 * Add window resize handler for responsive charts
 */
function addResizeHandler() {
    let resizeTimeout;
    const resizeDelay = 250; // ms
    
    function handleResize() {
        if (window.radarChart) window.radarChart.resize();
        if (window.barChart) window.barChart.resize();
        if (window.dimensionsChart) window.dimensionsChart.resize();
        if (window.strengthsGapsChart) window.strengthsGapsChart.resize();
        if (window.categoriesPolarChart) window.categoriesPolarChart.resize();
    }

    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(handleResize, resizeDelay);
    });
}

/**
 * Setup interactive legends for all charts
 */
function setupInteractiveLegends() {
    document.querySelectorAll('.chart-container').forEach(container => {
        const chartId = container.querySelector('canvas')?.id;
        if (!chartId) return;
        
        const chartInstance = Chart.getChart(chartId);
        if (!chartInstance) return;
        
        // Create custom legend if needed
        if (chartInstance.options.plugins?.legend?.display === false) {
            createCustomLegend(container, chartInstance);
        }
    });
}

/**
 * Create accessible custom legend
 */
function createCustomLegend(container, chartInstance) {
    const legendContainer = document.createElement('div');
    legendContainer.className = 'chart-legend';
    legendContainer.setAttribute('role', 'list');
    
    chartInstance.data.datasets.forEach((dataset, i) => {
        const legendItem = document.createElement('div');
        legendItem.className = 'legend-item';
        legendItem.setAttribute('role', 'listitem');
        
        const legendButton = document.createElement('button');
        legendButton.className = 'legend-btn';
        legendButton.setAttribute('aria-pressed', 'true');
        legendButton.setAttribute('aria-label', `Toggle ${dataset.label} visibility`);
        
        const legendColor = document.createElement('span');
        legendColor.className = 'legend-color';
        legendColor.style.backgroundColor = dataset.backgroundColor;
        
        const legendLabel = document.createElement('span');
        legendLabel.className = 'legend-label';
        legendLabel.textContent = dataset.label;
        
        legendButton.append(legendColor, legendLabel);
        legendItem.append(legendButton);
        legendContainer.append(legendItem);
        
        // Toggle dataset visibility on click
        legendButton.addEventListener('click', () => {
            const meta = chartInstance.getDatasetMeta(i);
            meta.hidden = !meta.hidden;
            chartInstance.update();
            legendButton.setAttribute('aria-pressed', !meta.hidden);
        });
    });
    
    // Insert legend after chart header
    const header = container.querySelector('.chart-header');
    if (header) {
        header.insertAdjacentElement('afterend', legendContainer);
    }
}

/**
 * Helper function to get score label text
 * @param {Number} score - Score value
 * @returns {String} - Label describing score
 */
function getScoreLabel(score) {
    if (score === null || score === undefined) return 'N/A';
    if (score >= 8) return 'Excellent';
    if (score >= 6) return 'Good';
    if (score >= 4) return 'Fair';
    return 'Needs Improvement';
}

/**
 * Helper function to get Bootstrap background class for badges
 * @param {Number} score - Score value
 * @returns {String} - CSS class name
 */
function getBadgeClass(score) {
    if (score === null || score === undefined) return 'bg-secondary';
    if (score >= 8) return 'bg-success';
    if (score >= 6) return 'bg-primary';
    if (score >= 4) return 'bg-warning text-dark';
    return 'bg-danger';
}

/**
* Export chart images for download
 * @param {String} chartId - ID of the chart to export
 * @param {String} fileName - File name for the downloaded image
 */
function exportChartImage(chartId, fileName = null) {
    const canvas = document.getElementById(chartId);
    if (!canvas) {
        console.error(`Canvas with ID ${chartId} not found for export`);
        alert('Chart export failed: Could not find chart element');
        return;
    }

    const chartInstance = Chart.getChart(canvas);
    if (!chartInstance) {
        console.error(`No Chart.js instance found for canvas ${chartId}`);
        alert('Chart export failed: Chart not initialized');
        return;
    }

    let chartTitle = document.querySelector(`[data-chart="${chartId}"]`)?.ariaLabel ||
                   chartInstance.options.plugins.title?.text ||
                   'chart';

    chartTitle = chartTitle.replace('Download ', '').replace(' as image', '');

    try {
        // Create larger canvas with metadata footer
        const originalWidth = canvas.width;
        const originalHeight = canvas.height;
        const footerHeight = 80;  // Space for metadata

        const exportCanvas = document.createElement('canvas');
        exportCanvas.width = originalWidth;
        exportCanvas.height = originalHeight + footerHeight;
        const ctx = exportCanvas.getContext('2d');

        // White background
        ctx.fillStyle = '#FFFFFF';
        ctx.fillRect(0, 0, exportCanvas.width, exportCanvas.height);

        // Draw original chart
        ctx.drawImage(canvas, 0, 0);

        // Add metadata footer
        ctx.fillStyle = '#F7F6F6';
        ctx.fillRect(0, originalHeight, originalWidth, footerHeight);

        // Add metadata text
        ctx.fillStyle = '#000000';
        ctx.font = 'bold 14px Arial';
        ctx.fillText(`SDG Assessment: ${window.projectName || 'Project'}`, 20, originalHeight + 25);

        ctx.font = '12px Arial';
        ctx.fillStyle = '#6C6B69';
        ctx.fillText(`Assessment ID: ${window.assessmentId || 'N/A'}`, 20, originalHeight + 45);
        ctx.fillText(`Generated: ${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()}`, 20, originalHeight + 65);

        ctx.textAlign = 'right';
        ctx.fillText('SDG Assessment Tool - UIA', originalWidth - 20, originalHeight + 55);

        // Generate filename with context
        const safeName = chartTitle.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/-$/, '');
        const safeProjectName = (window.projectName || 'project').replace(/[^a-z0-9]/gi, '_').toLowerCase();
        fileName = `sdg-${safeName}-${safeProjectName}-${window.assessmentId}-${new Date().toISOString().split('T')[0]}.png`;

        // Download
        const link = document.createElement('a');
        link.download = fileName;
        link.href = exportCanvas.toDataURL('image/png', 1.0);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        console.log(`Chart exported with metadata: ${fileName}`);
    } catch (error) {
        console.error('Error exporting chart:', error);
        alert('Error exporting chart. Please try again.');
    }
}

function exportToCSV(sdgScores, sdgNames, projectName = 'sdg-assessment') {
    if (!sdgScores || Object.keys(sdgScores).length === 0) {
        console.error('No SDG scores data available for CSV export');
        alert('No data available to export.');
        return;
    }
    
    try {
        // Prepare CSV content
        const headers = ['SDG Number', 'SDG Name', 'Direct Score', 'Bonus Score', 'Total Score'];
        let csvContent = headers.join(',') + '\n';
        
        // Format project name for filename
        const safeProjectName = projectName.replace(/[^a-z0-9]/gi, '-').toLowerCase();
        const filename = `${safeProjectName}-sdg-scores-${new Date().toISOString().split('T')[0]}.csv`;
        
        // Add data rows
        Object.keys(SDG_COLORS).sort((a, b) => parseInt(a) - parseInt(b)).forEach(num => {
            const sdg = sdgScores.find(s => s.number == num) || {};
            const row = [
                num,
                `"${sdgNames[num] || `SDG ${num}`}"`,
                sdg.direct_score ?? '',
                sdg.bonus_score ?? '',
                sdg.total_score ?? ''
            ];
            csvContent += row.join(',') + '\n';
        });
        
        // Create accessible download link
        const link = document.createElement('a');
        link.download = filename;
        link.href = URL.createObjectURL(new Blob([csvContent], { type: 'text/csv' }));
        link.ariaLabel = `Download SDG scores as CSV`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        console.log(`CSV exported as ${filename}`);
    } catch (error) {
        console.error('Error exporting CSV:', error);
        alert('Error exporting data. Please try again.');
    }
}

/**
 * Compare assessment results with benchmark data
 * @param {Object} sdgScores - Object containing the scores for each SDG
 * @param {Object} benchmarkData - Object containing benchmark data for comparison
 * @param {String} chartId - ID of the chart container for comparison
 */
function compareWithBenchmark(sdgScores, benchmarkData, chartId = 'comparisonChart') {
    const ctx = document.getElementById(chartId);
    if (!ctx) {
        console.warn(`Comparison chart container with ID ${chartId} not found`);
        return;
    }
    
    if (!benchmarkData || Object.keys(benchmarkData).length === 0) {
        console.warn('No benchmark data available for comparison');
        ctx.innerHTML = '<div class="text-center p-4 text-muted"><i class="fas fa-info-circle me-2"></i>No benchmark data available for comparison.</div>';
        return;
    }
    
    // Prepare data for chart
    const sdgNumbers = Object.keys(SDG_COLORS);
    const labels = sdgNumbers.map(num => `SDG ${num}`);
    
    const projectScores = sdgNumbers.map(num => getScoreWithFallback(sdgScores, num));
    const benchmarkScores = sdgNumbers.map(num => {
        return benchmarkData[num] !== undefined ? benchmarkData[num] : null;
    });
    
    const comparisonData = {
        labels: labels,
        datasets: [
            {
                label: 'Your Project',
                data: projectScores,
                backgroundColor: 'rgba(54, 162, 235, 0.7)',
                borderColor: 'rgb(54, 162, 235)',
                borderWidth: 2,
                order: 1
            },
            {
                label: 'Industry Benchmark',
                data: benchmarkScores,
                backgroundColor: 'rgba(255, 159, 64, 0.7)',
                borderColor: 'rgb(255, 159, 64)',
                borderWidth: 2,
                order: 2
            }
        ]
    };

    // Enhanced chart configuration
    const config = {
        type: 'bar',
        data: comparisonData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Comparison with Industry Benchmark',
                    font: {
                        size: CHART_DEFAULTS.titleFontSize,
                        weight: 'bold'
                    },
                    padding: {
                        top: 10,
                        bottom: 20
                    }
                },
                legend: {
                    position: 'top',
                    labels: {
                        font: {
                            size: CHART_DEFAULTS.labelFontSize
                        },
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.raw !== null ? context.raw.toFixed(1) : 'N/A';
                            return `${label}: ${value}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10,
                    title: {
                        display: true,
                        text: 'Score (out of 10)'
                    }
                }
            }
        }
    };

    // Create and store chart instance
    window.comparisonChart = new Chart(ctx, config);
    
    // Log chart creation
    console.log('Benchmark comparison chart created successfully');
}

// Initialize all charts on the assessment results page
function initializeCharts(sdgScores, sdgNames) {
    // Debug print: log the received SDG scores
    console.log('Raw sdgScores data:', sdgScores);
    const normalizedScores = normalizeSdgScores(sdgScores);
    console.log('Normalized sdgScores data:', normalizedScores);
    // ... rest of the chart rendering logic using normalizedScores instead of sdgScores ...
    // For example:
    createRadarChart(normalizedScores, sdgNames);
    createBarChart(normalizedScores, sdgNames);
    createCategoriesPolarChart(normalizedScores);
    createDimensionsChart(normalizedScores);
    createStrengthsGapsChart(normalizedScores, sdgNames);
}

// Utility function to determine performance level as text
// @param {Number} score - Score value
// @returns {Object} - Performance level and class
function getPerformanceLevel(score) {
    if (score >= 8) return { level: 'Excellent', class: 'success' };
    if (score >= 6) return { level: 'Good', class: 'primary' };
    if (score >= 4) return { level: 'Fair', class: 'warning' };
    return { level: 'Needs Improvement', class: 'danger' };
}

// Export functions for use in the main application
// Returns the Chart.js config for a given chartId, or null if not found
function getChartData(chartId) {
    const chartInstance = Chart.getChart(chartId);
    if (chartInstance) {
        return {
            type: chartInstance.config.type,
            data: chartInstance.data,
            options: chartInstance.options // Note: may need adjustment for modal
        };
    }
    return null;
}

/**
 * Create a bar chart showing performance across the 5 P categories.
 * @param {Object} categoryScores - Object with calculated scores { People: {score, color}, Planet: {...}, ... }
 */
function createCategoryBarChart(categoryScores) {
    const ctx = document.getElementById('categoryBarChart');
    if (!ctx) { /* ... */ return null; }
    if (!categoryScores || Object.keys(categoryScores).length === 0) { /* ... */ return null; }

    // Define reliable RGBA colors matching the category themes
    const CATEGORY_RGBA_COLORS = {
        'People':      'rgba(239, 68, 68, 0.7)',   // Red (danger)
        'Planet':      'rgba(16, 185, 129, 0.7)',  // Green (success)
        'Prosperity':  'rgba(245, 158, 11, 0.7)',  // Orange (warning)
        'Peace':       'rgba(37, 99, 235, 0.7)',   // Blue (primary)
        'Partnership': 'rgba(14, 165, 233, 0.7)'   // Cyan (info)
    };
    // Define the SDG ranges for labels
    const CATEGORY_SDG_RANGES = {
        'People': '(1-5)',
        'Planet': '(6, 12-15)',
        'Prosperity': '(7-11)',
        'Peace': '(16)',
        'Partnership': '(17)'
    };

    // Generate labels including SDG numbers
    const labels = Object.keys(categoryScores).map(label =>
        `${label} ${CATEGORY_SDG_RANGES[label] || ''}` // Add range like "(1-5)"
    );
    const data = Object.values(categoryScores).map(cat => cat.score.toFixed(1)); // Extract scores
    // Use the hardcoded RGBA colors
    const backgroundColors = Object.keys(categoryScores).map(label => CATEGORY_RGBA_COLORS[label] || 'rgba(128,128,128, 0.7)'); // Default gray
    const borderColors = backgroundColors.map(color => color.replace('0.7', '1')); // Make border solid

    const chartData = {
        labels: labels, // Use the updated labels
        datasets: [{
            label: 'Average Score',
            data: data,
            backgroundColor: backgroundColors, // Use hardcoded RGBA
            borderColor: borderColors,         // Use solid version of RGBA
            borderWidth: 1,
            barPercentage: 0.6,
            categoryPercentage: 0.7
        }]
    };

    const config = {
        type: 'bar',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                title: {
                    display: false
                },
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Avg Score: ${context.raw}/10`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 10,
                    title: {
                        display: true,
                        text: 'Average Score (0-10)',
                        font: { size: CHART_DEFAULTS.labelFontSize, weight: '600' }
                    },
                    grid: { color: 'rgba(0, 0, 0, 0.05)' }
                },
                y: {
                    grid: { display: false },
                    ticks: {
                        font: { size: 11 },
                        autoSkip: false
                    }
                }
            },
            layout: {
                padding: {
                    top: 20,
                    bottom: 30,
                    left: 20,
                    right: 20
                }
            },
            animation: CHART_DEFAULTS.animation
        },
        layout: {
            padding: {
                top: 5,
                bottom: 15, // Increased bottom padding to further prevent cut-off
                left: 5,
                right: 5
            }
        }
    };

    // ... (destroy and create chart instance) ...
    if (window.categoryBarChartInstance) {
        window.categoryBarChartInstance.destroy();
    }
    window.categoryBarChartInstance = new Chart(ctx, config); // Recreate with new data/options
    console.log("Category Bar chart created/updated successfully.");
    return window.categoryBarChartInstance;
}

window.SDGCharts = {
    initializeCharts,
    createRadarChart,
    createBarChart,
    createCategoriesPolarChart,
    createDimensionsChart,
    createStrengthsGapsChart,
    createCategoryBarChart,
    createBenchmarkChart,
    generatePDFReport,
    exportChartImage,
    exportToCSV,
    compareWithBenchmark,
    getScoreLabel,
    getBadgeClass,
    getPerformanceLevel,
    getChartData // <--- Now exported
};

console.log("sdg_charts.js script executed and SDGCharts object defined."); // <-- ADDED