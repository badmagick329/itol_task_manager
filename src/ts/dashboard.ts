/**
 * setupDashboard sets up the dashboard to sort and filter tasks
 *
 * @returns {void}
 */
export function setupDashboard() {
  const taskCards = document.querySelectorAll('[data-task-status]');
  if (taskCards.length === 0) return;

  const taskStatusFilter = document.getElementById('task-status-filter');
  if (taskStatusFilter) {
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

  const taskSorter = document.getElementById('task-sorter');
  if (!taskSorter) return;

  taskSorter.addEventListener('change', (event) => {
    const selectedKey = (event.target as HTMLSelectElement).value;
    if (!selectedKey) return;

    const container = taskCards[0].parentElement;
    if (!container) return;

    const cardsArray = Array.from(taskCards) as HTMLElement[];
    cardsArray.sort((a, b) => {
      let valA: string = '';
      let valB: string = '';
      switch (selectedKey) {
        case 'title':
          valA = a.dataset.taskTitle || '';
          valB = b.dataset.taskTitle || '';
          return valA.localeCompare(valB);
        case 'status':
          valA = a.dataset.taskStatus || '';
          valB = b.dataset.taskStatus || '';
          return valA.localeCompare(valB);
        case 'due_date':
          valA = a.dataset.taskDueDate || '';
          valB = b.dataset.taskDueDate || '';

          return new Date(valA).getTime() - new Date(valB).getTime();
        default:
          return 0;
      }
    });

    cardsArray.forEach((card) => container.appendChild(card));
  });
}

/**
 * tryHide hides the task card by removing the 'flex' class and adding the 'hidden' class.
 *
 * @param {Element} card - The task card element to hide.
 */
function tryHide(card: Element) {
  if (card.classList.contains('flex')) {
    card.classList.add('hidden');
    card.classList.remove('flex');
  }
}

/**
 * tryShow shows the task card by removing the 'hidden' class and adding the 'flex' class.
 *
 * @param {Element} card - The task card element to show.
 */
function tryShow(card: Element) {
  if (card.classList.contains('hidden')) {
    card.classList.remove('hidden');
    card.classList.add('flex');
  }
}
