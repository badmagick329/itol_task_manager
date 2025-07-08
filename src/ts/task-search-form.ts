/**
 * setupTaskSearchForm sets up the task search form with submit and reset handlers.
 * On submit, it reads title and description inputs, builds a URL-encoded query string, and navigates to it.
 * On reset, it clears the form and removes any query parameters from the URL.
 *
 * @returns {void}
 */
export function setupTaskSearchForm() {
  const form = document.getElementById(
    'task-search-form'
  ) as HTMLFormElement | null;
  if (!form) return;

  console.log(form);
  form.addEventListener('submit', (event) => {
    event.preventDefault();

    const formData = new FormData(form);
    const title = (formData.get('title') || '') as string;
    const description = (formData.get('description') || '') as string;
    const searchParams = new URLSearchParams();
    if (title) {
      searchParams.append('title', title);
    }
    if (description) {
      searchParams.append('description', description);
    }

    window.location.search = searchParams.toString();
  });

  // If task search form is present then reset search button should be present too
  const resetTaskSearchButton = document.getElementById(
    'reset-task-search-button'
  ) as HTMLButtonElement | null;
  if (!resetTaskSearchButton) return;

  resetTaskSearchButton.addEventListener('click', () => {
    form.reset();
    window.location.href = window.location.pathname;
  });
}
