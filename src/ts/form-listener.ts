import { ApiResponse } from './types';

type FormListenerArgs = {
  formId: string;
  errorBoxId: string;
  errorMessageId: string;
  endpoint: string;
  method?: 'POST' | 'PUT';
};

/**
 * FormListener handles form submission, validation, and error display.
 * It can be used for both POST and PUT requests.
 */
export class FormListener {
  private formId: string;
  private validators: ((data: Record<string, string>) => string)[] = [];
  private errorBox: HTMLElement;
  private errorMessage: HTMLElement;

  private _endpoint: string;
  private method: 'POST' | 'PUT' = 'POST';

  /**
   * Constructs a FormListener instance.
   *
   * @param {FormListenerArgs} args - The arguments for the FormListener.
   */
  constructor({
    formId,
    errorBoxId,
    errorMessageId,
    endpoint,
    method,
  }: FormListenerArgs) {
    const errorBox = document.getElementById(errorBoxId);
    const errorMessage = document.getElementById(errorMessageId);
    if (!errorBox || !errorMessage) {
      throw new Error(
        `Error box or message element not found. ${errorBoxId}, ${errorMessageId}`
      );
    }

    this.formId = formId;
    this.errorBox = errorBox;
    this.errorMessage = errorMessage;
    this._endpoint = endpoint;
    if (method) {
      this.method = method;
    }
  }

  /**
   * Checks if a form exists in the DOM.
   *
   * @param {string} formId - The ID of the form to check.
   * @returns {boolean} - True if the form exists, false otherwise.
   */
  static formExists(formId: string) {
    const form = document.getElementById(formId);
    return form !== null && form instanceof HTMLFormElement;
  }

  /**
   * Tries to attach the form submission handler. If the form does not exist, it does nothing.
   *
   * This method adds a listener which listens for the form's submit event,
   * validates the input data, sends the data to the server, and handles the
   * response.
   *
   * @returns {void}
   */
  tryAttach() {
    const form = document.getElementById(this.formId) as HTMLFormElement | null;

    if (!form) {
      return;
    }

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const formData = new FormData(form);
      const data: Record<string, string> = {};
      formData.forEach((value, key) => {
        if (typeof value === 'string') {
          data[key] = value.trim();
        }
      });

      for (const validator of this.validators) {
        const error = validator(data);
        if (error) {
          this.showError(error);
          return;
        }
      }

      this.hideError();

      try {
        const response = await fetch(this.endpoint, {
          method: this.method,
          body: formData,
        });

        // No validation. Backend is expected to return responses in this shape
        const json: ApiResponse = await response.json();
        if (json.error) {
          this.showError(json.error);
          return;
        }

        if (json.redirect) {
          window.location.href = json.redirect;
        }
      } catch (error) {
        this.showError('Something went wrong 😕');
      }
    });
  }

  /**
   * Adds a validation function to the list of validators.
   *
   * @param {function} validator - A function that takes data and returns an
   * error message if validation fails.
   *
   * @returns {void}
   */
  addValidator(validator: (data: Record<string, string>) => string) {
    this.validators.push(validator);
  }

  /**
   * Gets the endpoint URL based on the method.
   * If the method is POST, it returns the base endpoint.
   * If the method is PUT, it appends the last part of the current URL, which is
   * assumed to be an ID, to the endpoint.
   *
   * @returns {string} - The endpoint URL.
   */
  get endpoint(): string {
    if (this.method === 'POST') {
      return this._endpoint;
    }
    const parts = window.location.href.split('/');
    return `${this._endpoint}/${parts[parts.length - 1]}`;
  }

  /**
   * Displays an error message in the error box.
   *
   * @returns {void}
   */
  private showError(message: string) {
    if (!this.errorBox.classList.contains('flex')) {
      this.errorBox.classList.remove('hidden');
      this.errorBox.classList.add('flex');
    }

    this.errorMessage.textContent = message;
  }

  /**
   * Hides the error box if it is currently visible.
   *
   * @returns {void}
   */
  private hideError() {
    if (this.errorBox.classList.contains('hidden')) return;

    this.errorBox.classList.add('hidden');
    this.errorBox.classList.remove('flex');
  }
}

/**
 * ValidationHelpers provides a set of common validation functions that can be used with FormListener.
 */
export const ValidationHelpers = {
  /**
   * Creates a validation function that checks if a field is required.
   *
   * @param {string} fieldName - The name of the field to validate.
   * @returns {function} - A validation function that returns an error message if the field is empty.
   */
  required: (fieldName: string) => (data: Record<string, string>) => {
    if (!data[fieldName]) {
      return `${fieldName} cannot be empty`;
    }
    return '';
  },

  /**
   * Creates a validation function that checks if a field's value is at least a minimum length.
   *
   * @param {string} fieldName - The name of the field to validate.
   * @param {number} minLen - The minimum length required.
   *
   * @returns {function} - A validation function that returns an error message if the field's value is too short.
   */
  minLength:
    (fieldName: string, minLen: number) => (data: Record<string, string>) => {
      if (data[fieldName] && data[fieldName].length < minLen) {
        return `${fieldName} must be at least ${minLen} characters long`;
      }
      return '';
    },

  /**
   * Creates a validation function that checks if a field's value matches a specific pattern.
   * @param {string} fieldName - The name of the field to validate.
   * @param {RegExp} regex - The regular expression to test against the field's value.
   * @param {string} message - The error message to return if the validation fails.
   *
   * @return {function} - A validation function that returns an error message if the field's value does not match the pattern.
   */
  pattern:
    (fieldName: string, regex: RegExp, message: string) =>
    (data: Record<string, string>) => {
      if (data[fieldName] && !regex.test(data[fieldName])) {
        return message;
      }
      return '';
    },

  /**
   * Creates a validation function that checks if two password fields match.
   * @param {string} password1 - The name of the first password field.
   * @param {string} password2 - The name of the second password field.
   *
   * @return {function} - A validation function that returns an error message if the passwords do not match.
   */
  passwordMatch:
    (password1: string, password2: string) =>
    (data: Record<string, string>) => {
      if (
        data[password1] &&
        data[password2] &&
        data[password1] !== data[password2]
      ) {
        return 'Passwords do not match';
      }
      return '';
    },

  /**
   * Creates a custom validation function.
   * This function allows you to define your own validation logic.
   * @param {function} validator - A function that takes data and returns an error message if validation fails.
   * @return {function} - A validation function that can be added to the FormListener.
   */
  custom: (validator: (data: Record<string, string>) => string) => validator,
};
