// Chart.js implementation for Tesla Stock Analysis Dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Set global Chart.js defaults
    Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
    Chart.defaults.color = '#34495e';
    Chart.defaults.responsive = true;
    Chart.defaults.maintainAspectRatio = false;

    // 1. Revenue Chart
    const revenueCtx = document.getElementById('revenueChart').getContext('2d');
    const revenueChart = new Chart(revenueCtx, {
        type: 'bar',
        data: {
            labels: ['2019', '2020', '2021', '2022', '2023'],
            datasets: [
                {
                    label: 'Revenue ($ Billions)',
                    data: [24.58, 31.54, 53.82, 81.46, 96.77],
                    backgroundColor: 'rgba(52, 152, 219, 0.7)',
                    borderColor: 'rgba(52, 152, 219, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Net Income ($ Billions)',
                    data: [-0.86, 0.72, 5.52, 12.56, 7.93],
                    backgroundColor: 'rgba(46, 204, 113, 0.7)',
                    borderColor: 'rgba(46, 204, 113, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Tesla Revenue & Net Income (2019-2023)'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': $' + context.raw + 'B';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '$ Billions'
                    }
                }
            }
        }
    });

    // 2. Valuation Chart
    const valuationCtx = document.getElementById('valuationChart').getContext('2d');
    const valuationChart = new Chart(valuationCtx, {
        type: 'bar',
        data: {
            labels: ['Bull Case', 'Base Case', 'Bear Case', 'Current Price'],
            datasets: [{
                label: 'Price per Share ($)',
                data: [240.53, 76.05, 33.16, 284.65],
                backgroundColor: [
                    'rgba(46, 204, 113, 0.7)',  // Bull - Green
                    'rgba(52, 152, 219, 0.7)',  // Base - Blue
                    'rgba(231, 76, 60, 0.7)',   // Bear - Red
                    'rgba(243, 156, 18, 0.7)'   // Current - Orange
                ],
                borderColor: [
                    'rgba(46, 204, 113, 1)',
                    'rgba(52, 152, 219, 1)',
                    'rgba(231, 76, 60, 1)',
                    'rgba(243, 156, 18, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'DCF Valuation Scenarios vs. Current Price'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': $' + context.raw;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Price per Share ($)'
                    }
                }
            }
        }
    });

    // 3. Technical Analysis Chart
    const technicalCtx = document.getElementById('technicalChart').getContext('2d');
    const technicalChart = new Chart(technicalCtx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [
                {
                    label: 'Stock Price',
                    data: [220, 235, 250, 210, 230, 255, 270, 290, 260, 275, 280, 284.65],
                    borderColor: 'rgba(52, 152, 219, 1)',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: '50-day SMA',
                    data: [null, null, 235, 232, 230, 232, 241, 261, 270, 275, 276, 278],
                    borderColor: 'rgba(243, 156, 18, 1)',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0
                },
                {
                    label: '200-day SMA',
                    data: [210, 215, 220, 225, 228, 230, 232, 235, 238, 240, 242, 245],
                    borderColor: 'rgba(231, 76, 60, 1)',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0
                }
            ]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Tesla Price & Moving Averages (2024)'
                }
            },
            scales: {
                y: {
                    title: {
                        display: true,
                        text: 'Price ($)'
                    }
                }
            }
        }
    });

    // 4. Market Share Chart
    const marketShareCtx = document.getElementById('marketShareChart').getContext('2d');
    const marketShareChart = new Chart(marketShareCtx, {
        type: 'pie',
        data: {
            labels: ['Tesla', 'BYD', 'Volkswagen Group', 'GM', 'Ford', 'Others'],
            datasets: [{
                data: [18.4, 15.5, 14.6, 8.1, 7.5, 35.9],
                backgroundColor: [
                    'rgba(52, 152, 219, 0.7)',  // Tesla - Blue
                    'rgba(155, 89, 182, 0.7)',  // BYD - Purple
                    'rgba(52, 73, 94, 0.7)',    // VW - Dark Blue
                    'rgba(241, 196, 15, 0.7)',  // GM - Yellow
                    'rgba(46, 204, 113, 0.7)',  // Ford - Green
                    'rgba(189, 195, 199, 0.7)'  // Others - Gray
                ],
                borderColor: [
                    'rgba(52, 152, 219, 1)',
                    'rgba(155, 89, 182, 1)',
                    'rgba(52, 73, 94, 1)',
                    'rgba(241, 196, 15, 1)',
                    'rgba(46, 204, 113, 1)',
                    'rgba(189, 195, 199, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Global EV Market Share (%)'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.raw + '%';
                        }
                    }
                }
            }
        }
    });

    // 5. Price Target Chart
    const priceTargetCtx = document.getElementById('priceTargetChart').getContext('2d');
    const priceTargetChart = new Chart(priceTargetCtx, {
        type: 'bar',
        data: {
            labels: ['Bull Case', 'Base Case', 'Bear Case', 'Current Price'],
            datasets: [{
                label: 'Price Target',
                data: [500, 250, 100, 284.65],
                backgroundColor: [
                    'rgba(46, 204, 113, 0.7)',  // Bull - Green
                    'rgba(52, 152, 219, 0.7)',  // Base - Blue
                    'rgba(231, 76, 60, 0.7)',   // Bear - Red
                    'rgba(243, 156, 18, 0.7)'   // Current - Orange
                ],
                borderColor: [
                    'rgba(46, 204, 113, 1)',
                    'rgba(52, 152, 219, 1)',
                    'rgba(231, 76, 60, 1)',
                    'rgba(243, 156, 18, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Price Targets by Scenario'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': $';
                            }
                            if (context.parsed.y !== null) {
                                label += context.parsed.y;
                            }
                            return label;
                        },
                        afterLabel: function(context) {
                            const upside = ['+75.7%', '-12.2%', '-64.9%', '0%'];
                            const probability = ['25%', '50%', '25%', '100%'];
                            return [
                                'Upside/Downside: ' + upside[context.dataIndex],
                                'Probability: ' + probability[context.dataIndex]
                            ];
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Price ($)'
                    }
                }
            }
        }
    });
});
