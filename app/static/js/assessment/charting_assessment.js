// js/assessment/charting_assessment.js
// Handles rendering charts using Chart.js

let radarChartInstance = null;
let barChartInstance = null;

function renderRadarChart(scores) {
    const radarCtx = document.getElementById('radar-chart')?.getContext('2d');
    if (!radarCtx) {
        console.error("Radar chart canvas not found");
        return;
    }

    if (radarChartInstance) {
        radarChartInstance.destroy(); // Destroy previous instance if exists
    }

    // Check if SDG_INFO is available (should be defined globally in main_assessment.js)
    if (typeof SDG_INFO === 'undefined') {
         console.error("SDG_INFO not available for charting.");
         return;
    }

    const labels = scores.map(s => `SDG ${s.number}`); // Keep labels simple for chart data
    const data = scores.map(s => s.total_score);
    const pointColors = scores.map(s => s.color_code || s.color || '#CCCCCC');

    radarChartInstance = new Chart(radarCtx, {
         type: 'radar',
         data: {
             labels: labels,
             datasets: [{
                 label: 'SDG Score', // This label might need translation if shown
                 data: data,
                 backgroundColor: 'rgba(16, 185, 129, 0.2)', // Emerald-500 with alpha
                 borderColor: 'rgb(5, 150, 105)', // Emerald-600
                 pointBackgroundColor: pointColors,
                 pointBorderColor: '#fff',
                 pointHoverBackgroundColor: '#fff',
                 pointHoverBorderColor: pointColors,
                 borderWidth: 2,
                 pointRadius: 4,
                 pointHoverRadius: 6
             }]
         },
         options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 10,
                    ticks: { stepSize: 2, backdropColor: 'rgba(255,255,255,0.7)' },
                    pointLabels: { font: { size: 10 } },
                    grid: { color: 'rgba(0, 0, 0, 0.05)'},
                    angleLines: { color: 'rgba(0, 0, 0, 0.05)'}
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        // Use translated SDG title for tooltip
                        title: (tooltipItems) => {
                            const sdgNum = scores[tooltipItems[0].dataIndex].number;
                            const titleKey = `sdg${sdgNum}_title`;
                            // Ensure translations object is accessible
                            const name = (typeof translations !== 'undefined' && translations[currentLanguage])
                                        ? translations[currentLanguage][titleKey]
                                        : null;
                            return name || SDG_INFO[sdgNum]?.name || tooltipItems[0].label; // Fallback chain
                        },
                        label: (context) => {
                             // Ensure translations object is accessible
                             const labelKey = 'score_label';
                             const scoreText = (typeof translations !== 'undefined' && translations[currentLanguage])
                                                ? translations[currentLanguage][labelKey]
                                                : 'Score';
                             return `${scoreText}: ${context.raw.toFixed(1)} / 10`;
                        }
                    }
                }
            }
         }
    });
    console.log("Radar chart rendered.");
}

function renderBarChart(scores) {
    const barCtx = document.getElementById('bar-chart')?.getContext('2d');
     if (!barCtx) {
        console.error("Bar chart canvas not found");
        return;
    }

    if (barChartInstance) {
        barChartInstance.destroy();
    }

     // Check if SDG_INFO is available (should be defined globally in main_assessment.js)
    if (typeof SDG_INFO === 'undefined') {
         console.error("SDG_INFO not available for charting.");
         return;
    }

    const labels = scores.map(s => `SDG ${s.number}`);
    const data = scores.map(s => s.total_score);
    const backgroundColors = scores.map(s => s.color_code || s.color || '#CCCCCC');

    barChartInstance = new Chart(barCtx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Total Score', // Might need translation if shown
                data: data,
                backgroundColor: backgroundColors,
                borderColor: backgroundColors.map(c => c + 'CC'), // Add alpha for border
                borderWidth: 1,
                borderRadius: 4,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'x', // Default bar chart orientation
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10,
                     title: { display: true, text: 'Score (0-10)', font: { weight: 'bold'} } // Consider translating axis title
                },
                x: {
                     ticks: { font: { size: 10 }}
                }
            },
            plugins: {
                legend: { display: false },
                 tooltip: {
                    callbacks: {
                        // Use translated SDG title for tooltip
                        title: (tooltipItems) => {
                             const sdgNum = scores[tooltipItems[0].dataIndex].number;
                             const titleKey = `sdg${sdgNum}_title`;
                             const name = (typeof translations !== 'undefined' && translations[currentLanguage])
                                         ? translations[currentLanguage][titleKey]
                                         : null;
                             return name || SDG_INFO[sdgNum]?.name || tooltipItems[0].label; // Fallback chain
                         },
                        label: (context) => {
                             const labelKey = 'score_label';
                             const scoreText = (typeof translations !== 'undefined' && translations[currentLanguage])
                                                 ? translations[currentLanguage][labelKey]
                                                 : 'Score';
                             return `${scoreText}: ${context.raw.toFixed(1)} / 10`;
                        }
                    }
                }
            }
        }
    });
    console.log("Bar chart rendered.");
}