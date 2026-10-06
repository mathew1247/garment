/**
 * GARMENT TRACKER - REPORTS & ANALYTICS JAVASCRIPT
 * Handles report charts rendering, filter controls, and CSV export / print functions.
 */

document.addEventListener('DOMContentLoaded', () => {
  initReports();
});

function initReports() {
  if (typeof ChartManager !== 'undefined') {
    ChartManager.createProductionTrendChart('chart-production-trend');
    ChartManager.createOrderStatusChart('chart-order-status');
    ChartManager.createQualityRateChart('chart-quality-rate');
    ChartManager.createDeptEfficiencyChart('chart-dept-efficiency');
  }

  // Bind Export Button
  const exportBtn = document.getElementById('btn-export-report');
  if (exportBtn) {
    exportBtn.addEventListener('click', handleExportCSV);
  }

  // Bind Print Button
  const printBtn = document.getElementById('btn-print-report');
  if (printBtn) {
    printBtn.addEventListener('click', () => {
      window.print();
    });
  }

  // Filter apply button
  const filterForm = document.getElementById('reports-filter-form');
  if (filterForm) {
    filterForm.addEventListener('submit', (e) => {
      e.preventDefault();
      showToast('Report metrics updated for selected criteria', 'info');
    });
  }
}

function handleExportCSV() {
  const orders = DataStore.getOrders();
  let csvContent = 'data:text/csv;charset=utf-8,';
  csvContent += 'Order ID,Customer,Product,Quantity,Stage,Status,Deadline,Progress\r\n';

  orders.forEach(o => {
    const row = [
      `"${o.id}"`,
      `"${o.customer}"`,
      `"${o.product}"`,
      o.quantity,
      `"${o.currentStage}"`,
      `"${o.status}"`,
      `"${o.deadline}"`,
      `"${o.progress}%"`
    ].join(',');
    csvContent += row + '\r\n';
  });

  const encodedUri = encodeURI(csvContent);
  const link = document.createElement('a');
  link.setAttribute('href', encodedUri);
  link.setAttribute('download', `Garment_Production_Report_${new Date().toISOString().slice(0,10)}.csv`);
  document.body.appendChild(link);
  link.click();
  link.remove();

  showToast('Production Report exported successfully as CSV', 'success');
}
