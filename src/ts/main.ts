import { setupCreateTaskForm } from './create-task-form';
import { setupDashboard } from './dashboard';
import { setupDeleteTaskHandler } from './delete-task-handler';
import { setupEditTaskForm } from './edit-task-form';
import { setupLoginForm } from './login-form';
import { setupRegistrationForm } from './registration-form';

async function main() {
  console.log('🤓');
  setupLoginForm();
  setupRegistrationForm();
  setupCreateTaskForm();
  setupEditTaskForm();
  setupDeleteTaskHandler();
  setupDashboard();
}

main();
