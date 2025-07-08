from flask import (
    Blueprint,
    Response,
    current_app,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from src.core.errors import TaskNotFoundError
from src.infra.repositories.sql_task_repository import SQLTaskRepository
from src.infra.repositories.sql_user_repository import SQLUserRepository
from src.services.api_response_service import ApiResponseService

task_bp = Blueprint("task", __name__)


@task_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    user_id = current_user.id if current_user.is_authenticated else None
    if not user_id:
        return redirect(url_for("auth.login"))

    from flask import current_app

    task_repository: SQLTaskRepository = current_app.extensions["task_repo"]
    user_repository: SQLUserRepository = current_app.extensions["user_repo"]
    user = user_repository.get_by_id(user_id)

    if not user:
        return redirect(url_for("auth.login"))

    tasks = task_repository.list_by_user(user.id)

    return render_template("tasks/dashboard.html", tasks=tasks)


@task_bp.route("/task", methods=["GET", "POST"])
@login_required
def task_create():
    task_repository: SQLTaskRepository = current_app.extensions["task_repo"]
    api_response_service: ApiResponseService = current_app.extensions[
        "api_response_service"
    ]
    user_id = current_user.id if current_user.is_authenticated else None

    if not user_id:
        return redirect(url_for("auth.login"))

    if request.method == "GET":
        return render_template("tasks/create_task.html")

    # POST /task
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    due_date = request.form.get("due_date", "").strip()
    status = request.form.get("status", "").strip()
    result = task_repository.create(
        title=title,
        description=description,
        due_date=due_date,
        status=status,
        user_id=user_id,
    )
    if result.is_err:
        return api_response_service.to_response(
            ok=False,
            status=400,
            message="Task creation failed",
            error=str(result.unwrap_err()),
        )

    created = result.unwrap()
    return api_response_service.to_response(
        ok=True,
        status=201,
        redirect=url_for("task.dashboard"),
        message="Task created successfully",
        data={"task_id": created.id},
    )


@task_bp.route("/task/<int:task_id>", methods=["GET"])
@login_required
def task_edit(task_id: int):
    task_repository: SQLTaskRepository = current_app.extensions["task_repo"]
    user_id = current_user.id
    task = task_repository.get_by_id(task_id)
    if not task or task.user_id != user_id:
        return redirect(url_for("task.dashboard"))
    return render_template("tasks/edit_task.html", task=task)


@task_bp.route("/task/<int:task_id>", methods=["PUT"])
@login_required
def task_update(task_id: int):
    task_repository: SQLTaskRepository = current_app.extensions["task_repo"]
    api_response_service: ApiResponseService = current_app.extensions[
        "api_response_service"
    ]
    user_id = current_user.id if current_user.is_authenticated else None
    if not user_id:
        return redirect(url_for("auth.login"))

    title = request.form.get("title", "")
    description = request.form.get("description", "")
    due_date = request.form.get("due_date", "")
    status = request.form.get("status", "")
    result = task_repository.update(
        task_id=task_id,
        title=title,
        description=description,
        due_date=due_date,
        status=status,
        user_id=user_id,
    )
    if result.is_err:
        return api_response_service.to_response(
            ok=False,
            status=400,
            message="Task update failed",
            error=str(result.unwrap_err()),
        )
    updated = result.unwrap()
    return api_response_service.to_response(
        ok=True,
        status=200,
        redirect=url_for("task.dashboard"),
        message="Task updated successfully",
        data={"task_id": updated.id},
    )


@task_bp.route("/task/<int:task_id>", methods=["DELETE"])
@login_required
def task_delete(task_id: int):
    task_repository: SQLTaskRepository = current_app.extensions["task_repo"]
    api_response_service: ApiResponseService = current_app.extensions[
        "api_response_service"
    ]
    user_id = current_user.id if current_user.is_authenticated else None
    if not user_id:
        return redirect(url_for("auth.login"))
    error = task_repository.delete(task_id)
    if isinstance(error, TaskNotFoundError):
        return api_response_service.to_response(
            ok=False,
            status=404,
            error=str(error),
        )
    return api_response_service.to_response(
        ok=True,
        status=200,
        redirect=url_for("task.dashboard"),
        message="Task deleted successfully",
    )


@task_bp.route("/task/export", methods=["GET"])
@login_required
def export_tasks():
    """
    Export the current user's tasks as a downloadable CSV file.
    """
    user_id = current_user.id if current_user.is_authenticated else None
    if not user_id:
        return redirect(url_for("auth.login"))

    export_service = current_app.extensions["task_export_service"]
    api_response_service: ApiResponseService = current_app.extensions[
        "api_response_service"
    ]
    result = export_service.export_user_tasks(user_id)
    if result.is_err:
        return api_response_service.to_response(
            ok=False,
            status=500,
            message="Task export failed",
            error=str(result.unwrap_err()),
        )

    csv_content = result.unwrap()
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=tasks.csv"},
    )
