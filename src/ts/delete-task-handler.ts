export function setupDeleteTaskHandler() {
  const deleteButtons = document.querySelectorAll('[data-delete-task-id]');
  if (deleteButtons.length === 0) return;

  deleteButtons.forEach((button) => {
    button.addEventListener('click', async (event) => {
      event.preventDefault();
      const taskId = (button as HTMLElement).dataset.deleteTaskId;
      if (!taskId) return;
      const confirm = window.confirm(
        'Are you sure you want to delete this task?'
      );
      if (!confirm) return;

      const response = await fetch(`/task/${taskId}`, {
        method: 'DELETE',
      });

      const json = await response.json();
      if (json.error) {
        alert(`Error deleting task: ${json.error}`);
        return;
      }

      window.location.reload();
    });
  });
}
