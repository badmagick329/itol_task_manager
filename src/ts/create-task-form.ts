import { FormListener, ValidationHelpers } from './form-listener';

/**
 * setupCreateTaskForm sets up the create task form with validation and submission handling.
 *
 * @returns {void}
 */
export function setupCreateTaskForm() {
  const formId = 'create-task-form';
  if (!FormListener.formExists(formId)) return;

  const formListener = new FormListener({
    formId,
    errorBoxId: 'create-task-error',
    errorMessageId: 'create-task-error-message',
    endpoint: '/task',
  });

  formListener.addValidator(ValidationHelpers.required('title'));
  formListener.addValidator(ValidationHelpers.required('due_date'));
  formListener.addValidator(ValidationHelpers.required('status'));

  formListener.tryAttach();
}
