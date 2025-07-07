import { ApiResponse } from './types';

type FormListenerArgs = {
  formId: string;
  errorBoxId: string;
  errorMessageId: string;
  endpoint: string;
  method?: string;
};

export class FormListener {
  private formId: string;
  private validators: ((data: Record<string, string>) => string)[] = [];
  private errorBox: HTMLElement;
  private errorMessage: HTMLElement;

  private endpoint: string;
  private method: string = 'POST';

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
    this.endpoint = endpoint;
    if (method) {
      this.method = method;
    }
  }

  static formExists(formId: string) {
    const form = document.getElementById(formId);
    return form !== null && form instanceof HTMLFormElement;
  }

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

  addValidator(validator: (data: Record<string, string>) => string) {
    this.validators.push(validator);
  }

  private showError(message: string) {
    if (!this.errorBox.classList.contains('flex')) {
      this.errorBox.classList.remove('hidden');
      this.errorBox.classList.add('flex');
    }

    this.errorMessage.textContent = message;
  }

  private hideError() {
    if (this.errorBox.classList.contains('hidden')) return;

    this.errorBox.classList.add('hidden');
    this.errorBox.classList.remove('flex');
  }
}

export const ValidationHelpers = {
  required: (fieldName: string) => (data: Record<string, string>) => {
    if (!data[fieldName]) {
      return `${fieldName} cannot be empty`;
    }
    return '';
  },

  minLength:
    (fieldName: string, minLen: number) => (data: Record<string, string>) => {
      if (data[fieldName] && data[fieldName].length < minLen) {
        return `${fieldName} must be at least ${minLen} characters long`;
      }
      return '';
    },

  pattern:
    (fieldName: string, regex: RegExp, message: string) =>
    (data: Record<string, string>) => {
      if (data[fieldName] && !regex.test(data[fieldName])) {
        return message;
      }
      return '';
    },

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

  custom: (validator: (data: Record<string, string>) => string) => validator,
};
