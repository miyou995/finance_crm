import logging
import json
from django.contrib.messages import get_messages
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest, HttpResponse

from django.contrib.auth.middleware import (
    LoginRequiredMiddleware as DjangoLoginRequiredMiddleware,
)

logger = logging.getLogger(__name__)

LOGIN_NOT_REQUIRED_APPS = []


class LoginRequiredMiddleware(DjangoLoginRequiredMiddleware):
    def process_view(self, request, view_func, view_args, view_kwargs):
        match = request.resolver_match

        if request.user.is_authenticated:
            return None

        if match.app_name in LOGIN_NOT_REQUIRED_APPS:
            return None

        if not getattr(view_func, "login_required", True):
            return None

        return self.handle_no_permission(request, view_func)


class HtmxMessageMiddleware(MiddlewareMixin):
    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        if "HX-Request" not in request.headers or 300 <= response.status_code < 400:
            return response

        messages = [
            {"message": str(message.message), "tags": message.tags}
            for message in get_messages(request)
        ]
        if not messages:
            return response

        try:
            hx_trigger = json.loads(response.headers.get("HX-Trigger", "{}"))
        except json.JSONDecodeError:
            logger.error("Invalid JSON format in HX-Trigger header")
            hx_trigger = {}

        hx_trigger["messages"] = messages
        response.headers["HX-Trigger"] = json.dumps(hx_trigger)
        return response
