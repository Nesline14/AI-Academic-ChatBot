/* CampusConnect Main JavaScript */
document.addEventListener('DOMContentLoaded', () => {
  // Mobile Sidebar Toggle
  const sidebarToggle = document.getElementById('sidebar-toggle');
  const sidebar = document.querySelector('.app-sidebar');

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('show');
    });
  }

  // Auto-dismiss Flash Alerts after 6 seconds
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach((alert) => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 6000);
  });

  // Enable Bootstrap Tooltips & Popovers
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl));
});
