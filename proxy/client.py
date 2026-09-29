"""Stream one reply from BUILD LLM Proxy.

Never retries: the proxy docs forbid retrying after partial output, and a
repeated request could be billed twice. Errors are classified by whether the
request could have produced billable output.
"""

import logging
import time
from collections.abc import Callable, Iterator

import httpx
from django.conf import settings

from .adapters import adapter_for
from .sse import iter_sse
from .types import Cancelled, Done, Message, ProxyError, TextDelta

log = logging.getLogger("litechat.proxy")

TIMEOUT = httpx.Timeout(connect=10.0, read=90.0, write=10.0, pool=10.0)
MAX_DURATION = 300.0  # seconds for a whole reply

# Status codes returned before generation starts, so nothing was billed.
REJECTIONS = {
    400: ("bad_request", "The model service rejected the request."),
    401: ("auth", "The model service did not accept this app's key."),
    403: ("auth", "The model service did not accept this app's key."),
    404: ("bad_request", "The model service does not offer this model."),
    413: ("too_large", "This conversation is too long for the model."),
    422: ("bad_request", "The model service rejected the request."),
    429: ("rate_limited", "The model service is busy. Wait a moment and try again."),
}

_transport: httpx.BaseTransport | None = None  # tests install a MockTransport here


def set_transport(transport: httpx.BaseTransport | None) -> None:
    global _transport
    _transport = transport


def stream_reply(
    *,
    provider: str,
    model: str,
    messages: list[Message],
    max_output_tokens: int,
    system: str = "",
    should_cancel: Callable[[], bool] = lambda: False,
) -> Iterator[TextDelta | Done]:
    key = settings.PROXY_KEYS.get(provider)
    if not key:
        raise ProxyError("not_configured", "This model is not configured.", nothing_generated=True)
    adapter = adapter_for(provider)
    req = adapter.build(model=model, messages=messages, max_output_tokens=max_output_tokens, key=key, system=system)
    started = time.monotonic()

    with httpx.Client(base_url=settings.PROXY_BASE_URL, timeout=TIMEOUT, transport=_transport) as http:
        try:
            with http.stream("POST", req.path, headers=req.headers, json=req.body) as response:
                if response.status_code != 200:
                    raise _status_error(response)
                for item in adapter.parse(iter_sse(response.iter_lines())):
                    yield item
                    if isinstance(item, Done):
                        return
                    if should_cancel():
                        raise Cancelled()
                    if time.monotonic() - started > MAX_DURATION:
                        raise ProxyError("timeout", "The reply took too long and was stopped.")
        except (httpx.ConnectError, httpx.ConnectTimeout) as exc:
            # The request never reached the service: nothing to bill.
            raise ProxyError("unreachable", "Could not reach the model service.", nothing_generated=True) from exc
        except httpx.TimeoutException as exc:
            raise ProxyError("timeout", "The model service stopped responding.") from exc
        except httpx.TransportError as exc:
            raise ProxyError("interrupted", "The connection to the model service broke.") from exc


def _status_error(response: httpx.Response) -> ProxyError:
    status = response.status_code
    response.read()
    log.info("proxy status %s for %s", status, response.request.url.path)
    if status in REJECTIONS:
        kind, message = REJECTIONS[status]
        return ProxyError(kind, message, status=status, nothing_generated=True)
    if 400 <= status < 500:
        return ProxyError("bad_request", "The model service rejected the request.", status=status, nothing_generated=True)
    # 5xx: the docs say usage can be unknown after an upstream failure.
    return ProxyError("upstream", "The model service failed to answer.", status=status)
