import { FormListener, ValidationHelpers } from './form-listener';

/**
 * setupLoginForm sets up the login form with validation and submission handling.
 *
 * @returns {void}
 */
export function setupLoginForm() {
  const formId = 'login-form';
  if (!FormListener.formExists(formId)) return;

  const formListener = new FormListener({
    formId,
    errorBoxId: 'login-error',
    errorMessageId: 'login-error-message',
    endpoint: '/login',
  });

  formListener.addValidator(ValidationHelpers.required('username'));
  formListener.addValidator(ValidationHelpers.required('password'));
  formListener.addValidator(ValidationHelpers.minLength('password', 8));
  formListener.addValidator(
    ValidationHelpers.pattern(
      'username',
      /^[a-zA-Z0-9_-]+$/,
      'Username can only contain letters, numbers, hyphens, and underscores'
    )
  );

  formListener.tryAttach();
}
