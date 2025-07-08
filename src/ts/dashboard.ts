export function setupDashboard() {
  const taskStatusFilter = document.getElementById('task-status-filter');
  if (!taskStatusFilter) return;

  const taskCards = document.querySelectorAll('[data-task-status]');
  if (taskCards.length === 0) return;

  taskStatusFilter.addEventListener('change', (event) => {
    const selectedStatus = (event.target as HTMLSelectElement).value;
    taskCards.forEach((card) => {
      const cardStatus = (card as HTMLElement).dataset.taskStatus;
      if (selectedStatus === 'All' || cardStatus === selectedStatus) {
        tryShow(card);
      } else {
        tryHide(card);
      }
    });
  });
}

function tryHide(card: Element) {
  if (card.classList.contains('flex')) {
    card.classList.add('hidden');
    card.classList.remove('flex');
  }
}

function tryShow(card: Element) {
  if (card.classList.contains('hidden')) {
    card.classList.remove('hidden');
    card.classList.add('flex');
  }
}
