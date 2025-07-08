from flask import jsonify
from flask.wrappers import Response


class ApiResponseService:
    """
    Service for creating consistent JSON responses for API endpoints. This response format has to match what the frontend expects
    """

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
        """Jsonify the values

        Args:
            ok (bool): Indicates whether the operation was successful.
            status (int): HTTP status code for the response.
            redirect (str | None, optional): URL to redirect the client to. Defaults to None.
            message (str | None, optional): Informational message to include. Defaults to None.
            data (dict | None, optional): Payload data for the response. Defaults to None.
            error (str | None, optional): Error message if the operation failed. Defaults to None.

        Returns:
            Response: Flask Response object containing the standardized JSON payload.
        """
        return jsonify(
            ok=ok,
            status=status,
            redirect=redirect,
            message=message,
            data=data,
            error=error,
        )
