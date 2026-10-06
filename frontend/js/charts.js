/**
 * GARMENT TRACKER - CHARTS INITIALIZER
 * Provides pre-styled Chart.js configurations aligned with the brand design system.
 */

const ChartManager = {
  // Production Trend Bar Chart
  createProductionTrendChart(canvasId) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'],
        datasets: [
          {
            label: 'Garments Produced',
            data: [4200, 5100, 6800, 7400, 8900, 9500],
            backgroundColor: '#f95721',
            borderRadius: 6,
            barThickness: 24
          },
          {
            label: 'Target Goal',
            data: [4500, 5000, 6500, 7000, 8500, 9000],
            backgroundColor: '#e2e8f0',
            borderRadius: 6,
            barThickness: 24
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: { boxWidth: 12, font: { family: "'Plus Jakarta Sans', sans-serif", weight: '600', size: 12 } }
          },
          tooltip: {
            backgroundColor: '#1e293b',
            titleFont: { family: "'Plus Jakarta Sans', sans-serif", size: 13 },
            bodyFont: { family: "'Plus Jakarta Sans', sans-serif", size: 12 },
            padding: 10,
            cornerRadius: 8
          }
        },
        scales: {
          x: {
            grid: { display: false }
          },
          y: {
            grid: { color: '#f1f5f9' },
            beginAtZero: true
          }
        }
      }
    });
  },

  // Order Status Doughnut Chart
  createOrderStatusChart(canvasId) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['In Progress', 'Completed', 'Pending', 'Delayed'],
        datasets: [{
          data: [11, 8, 5, 2],
          backgroundColor: ['#2563eb', '#10b981', '#f59e0b', '#ef4444'],
          borderWidth: 3,
          borderColor: '#ffffff',
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '72%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: { boxWidth: 10, padding: 14, font: { family: "'Plus Jakarta Sans', sans-serif", size: 12, weight: '600' } }
          }
        }
      }
    });
  },

  // Quality Inspection Pass vs Rework Chart
  createQualityRateChart(canvasId) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
      type: 'pie',
      data: {
        labels: ['First Time Pass (94%)', 'Rework Required (5%)', 'Scrap/Rejected (1%)'],
        datasets: [{
          data: [94, 5, 1],
          backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { boxWidth: 12, font: { family: "'Plus Jakarta Sans', sans-serif", size: 12, weight: '600' } }
          }
        }
      }
    });
  },

  // Department Efficiency Horizontal Bar
  createDeptEfficiencyChart(canvasId) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Cutting', 'Stitching', 'Finishing', 'Quality Control', 'Packaging', 'Logistics'],
        datasets: [{
          label: 'Efficiency Rate (%)',
          data: [96, 92, 88, 97, 95, 94],
          backgroundColor: ['#10b981', '#2563eb', '#f59e0b', '#8b5cf6', '#06b6d4', '#64748b'],
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            min: 50,
            max: 100,
            grid: { color: '#f1f5f9' }
          },
          y: {
            grid: { display: false }
          }
        }
      }
    });
  }
};
