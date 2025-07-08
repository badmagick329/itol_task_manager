import { FormListener, ValidationHelpers } from './form-listener';

export function setupEditTaskForm() {
  const formId = 'edit-task-form';
  if (!FormListener.formExists(formId)) return;

  const formListener = new FormListener({
    formId,
    errorBoxId: 'edit-task-error',
    errorMessageId: 'edit-task-error-message',
    endpoint: '/task',
    method: 'PUT',
  });

  formListener.addValidator(ValidationHelpers.required('title'));
  formListener.addValidator(ValidationHelpers.required('due_date'));
  formListener.addValidator(ValidationHelpers.required('status'));

  formListener.tryAttach();
}
