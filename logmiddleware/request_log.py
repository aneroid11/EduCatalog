"""
Middleware to log requests and responses.
"""
import socket
import time
import json
import logging
import types

from django.http.request import HttpRequest
from django.http.response import HttpResponse

logging.basicConfig(filename="logs.txt", level=logging.INFO)
logger = logging.getLogger(__name__)


class RequestLogMiddleware:
    """Request logging middleware."""

    def __init__(self, get_response: types.FunctionType):
        """Init self.get_response with a function to get the response"""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Log requests and responses."""

        start_time = time.time()
        log_data = {
            "remote_address": request.META["REMOTE_ADDR"],
            "server_hostname": socket.gethostname(),
            "request_method": request.method,
            "request_path": request.get_full_path(),
        }

        req_body = json.loads(request.body.decode("utf-8")) if request.body else {}
        log_data["request_body"] = req_body

        response = self.get_response(request)

        if response and response["content-type"] == "application/json":
            response_body = json.loads(response.content.decode("utf-8"))
            log_data["response_body"] = response_body
        log_data["run_time"] = time.time() - start_time

        logger.info(msg=log_data)

        return response


    def process_exception(self, request: HttpRequest, exception: Exception) -> Exception:
        """Process unhandled exceptions"""
        try:
            raise exception
        except Exception as e:
            logger.exception("Unhandled Exception: " + str(e))
        return exception
