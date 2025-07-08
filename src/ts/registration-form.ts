import { FormListener, ValidationHelpers } from './form-listener';

/**
 * setupRegistrationForm sets up the registration form with validation and submission handling.
 *
 * @returns {void}
 */
export function setupRegistrationForm() {
  const formId = 'registration-form';
  if (!FormListener.formExists(formId)) return;

  const formListener = new FormListener({
    formId,
    errorBoxId: 'register-error',
    errorMessageId: 'register-error-message',
    endpoint: '/register',
  });

  formListener.addValidator(ValidationHelpers.required('username'));
  formListener.addValidator(ValidationHelpers.required('email'));
  formListener.addValidator(ValidationHelpers.required('password'));
  formListener.addValidator(ValidationHelpers.required('password2'));

  formListener.addValidator(ValidationHelpers.minLength('password', 8));
  formListener.addValidator(
    ValidationHelpers.pattern(
      'username',
      /^[a-zA-Z0-9_-]+$/,
      'Username can only contain letters, numbers, hyphens, and underscores'
    )
  );
  formListener.addValidator(
    ValidationHelpers.pattern(
      'email',
      /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      'Please enter a valid email address'
    )
  );
  formListener.addValidator(
    ValidationHelpers.passwordMatch('password', 'password2')
  );

  formListener.tryAttach();
}
