from flask import jsonify
from flask.wrappers import Response


# This service is used to create a standardized API response format. This has to match what the frontend expects.
class ApiResponseService:
    @classmethod
    def to_response(
        cls,
        ok: bool,
        status: int,
        redirect: str | None = None,
        message: str | None = None,
        data: dict | None = None,
        error: str | None = None,
    ) -> Response:
        return jsonify(
            ok=ok,
            status=status,
            redirect=redirect,
            message=message,
            data=data,
            error=error,
        )
