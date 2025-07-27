// players/static/players/js/player_detail.js

document.addEventListener('DOMContentLoaded', function() {
    // Check if personality engine is enabled
    const personalitySection = document.getElementById('personalitySection');
    if (!personalitySection) return;

    // Initialize personality radar chart
    const radarCanvas = document.getElementById('personalityRadarChart');
    if (radarCanvas) {
        initializeRadarChart(radarCanvas);
    }

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add animation to evolution events on scroll
    observeEvolutionEvents();
});

function initializeRadarChart(canvas) {
    const ctx = canvas.getContext('2d');
    const personalityDataEl = document.getElementById('personality-data-json');
    const personalityData = personalityDataEl ? JSON.parse(personalityDataEl.textContent) : {};
    
    // Define trait labels and extract values
    const traits = [
        { key: 'aggression', label: 'Aggression' },
        { key: 'confidence', label: 'Confidence' },
        { key: 'risk_taking', label: 'Risk Taking' },
        { key: 'patience', label: 'Patience' },
        { key: 'teamwork', label: 'Teamwork' },
        { key: 'leadership', label: 'Leadership' },
        { key: 'ambition', label: 'Ambition' },
        { key: 'charisma', label: 'Charisma' },
        { key: 'endurance', label: 'Endurance' },
        { key: 'adaptability', label: 'Adaptability' }
    ];

    const labels = traits.map(t => t.label);
    const data = traits.map(t => personalityData[t.key] || 10);

    // Check for dark mode
    const isDarkMode = document.body.classList.contains('dark-mode') || 
                      document.documentElement.getAttribute('data-bs-theme') === 'dark';
    
    const chart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Personality Traits',
                data: data,
                fill: true,
                backgroundColor: isDarkMode ? 'rgba(110, 168, 254, 0.2)' : 'rgba(13, 110, 253, 0.2)',
                borderColor: isDarkMode ? 'rgb(110, 168, 254)' : 'rgb(13, 110, 253)',
                pointBackgroundColor: isDarkMode ? 'rgb(110, 168, 254)' : 'rgb(13, 110, 253)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: isDarkMode ? 'rgb(110, 168, 254)' : 'rgb(13, 110, 253)',
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: {
                        display: true,
                        color: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
                    },
                    suggestedMin: 0,
                    suggestedMax: 20,
                    ticks: {
                        stepSize: 5,
                        color: isDarkMode ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)',
                        backdropColor: 'transparent'
                    },
                    grid: {
                        color: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'
                    },
                    pointLabels: {
                        color: isDarkMode ? 'rgba(255, 255, 255, 0.9)' : 'rgba(0, 0, 0, 0.9)',
                        font: {
                            size: 12,
                            weight: '500'
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.parsed.r + '/20';
                        }
                    },
                    backgroundColor: isDarkMode ? 'rgba(33, 37, 41, 0.9)' : 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
                    borderWidth: 1
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });

    // Store chart instance for potential updates
    window.personalityRadarChart = chart;
}

function observeEvolutionEvents() {
    const options = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                observer.unobserve(entry.target);
            }
        });
    }, options);

    // Observe all evolution events
    document.querySelectorAll('.evolution-event').forEach(event => {
        observer.observe(event);
    });

    // Observe narrative events
    document.querySelectorAll('.narrative-event').forEach(event => {
        observer.observe(event);
    });
}

// Function to format trait changes
function formatTraitChange(trait, oldValue, newValue) {
    const change = newValue - oldValue;
    const changeClass = change > 0 ? 'text-success' : 'text-danger';
    const changeSymbol = change > 0 ? '+' : '';
    
    return `
        <span class="trait-change">
            ${trait}: 
            <span class="old-value">${oldValue}</span> 
            → 
            <span class="new-value">${newValue}</span>
            <span class="${changeClass}">(${changeSymbol}${change})</span>
        </span>
    `;
}

// Function to get event icon based on type
function getEventIcon(eventType) {
    const iconMap = {
        'rivalry_clash': 'fas fa-fire',
        'chemistry_moment': 'fas fa-handshake',
        'memorable_goal': 'fas fa-futbol',
        'crucial_save': 'fas fa-hand-paper',
        'team_victory': 'fas fa-trophy',
        'personal_milestone': 'fas fa-star',
        'dramatic_moment': 'fas fa-bolt',
        'leadership_moment': 'fas fa-crown'
    };
    
    return iconMap[eventType] || 'fas fa-circle';
}

// Function to get importance color
function getImportanceColor(importance) {
    switch(importance) {
        case 'high':
            return 'danger';
        case 'medium':
            return 'warning';
        case 'low':
            return 'info';
        default:
            return 'secondary';
    }
}

// Dark mode support
document.addEventListener('DarkModeToggled', function() {
    // Recreate radar chart with new colors
    const radarCanvas = document.getElementById('personalityRadarChart');
    if (radarCanvas && window.personalityRadarChart) {
        window.personalityRadarChart.destroy();
        initializeRadarChart(radarCanvas);
    }
});