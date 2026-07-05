from __future__ import annotations

import asyncio
import aiohttp
import orjson
from collections.abc import Mapping
from typing import Any, Optional, Union
from .api import VprikolAPIError, create_api_error

RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})
RETRY_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


def dumps_json(value: Any) -> str:
    return orjson.dumps(value).decode()


TimeoutConfig = Optional[Union[aiohttp.ClientTimeout, int, float]]


def clean_params(params: Optional[Mapping[str, Any]]) -> dict[str, Any]:
    return {key: value for key, value in (params or {}).items() if value is not None}


def normalize_base_url(base_url: str) -> str:
    return f"{base_url.rstrip('/')}/"


def normalize_timeout(timeout: TimeoutConfig) -> Optional[aiohttp.ClientTimeout]:
    if timeout is None or isinstance(timeout, aiohttp.ClientTimeout):
        return timeout
    return aiohttp.ClientTimeout(total=float(timeout))


def is_json_content_type(content_type: Optional[str]) -> bool:
    if not content_type:
        return False
    return content_type == "application/json" or content_type.endswith("+json")


async def read_json_response(response: aiohttp.ClientResponse) -> Any:
    return await response.json(loads=orjson.loads, content_type=None)


async def read_error_data(response: aiohttp.ClientResponse) -> dict[str, Any]:
    if is_json_content_type(response.content_type):
        try:
            data = await read_json_response(response)
        except (aiohttp.ContentTypeError, orjson.JSONDecodeError):
            data = None
        if isinstance(data, dict):
            return data
        if data is not None:
            return {"detail": data, "status_code": response.status}

    text = await response.text()
    return {"detail": text or f"HTTP {response.status}", "status_code": response.status}


class VprikolHTTPClient:
    def __init__(self, base_url: str, headers: dict[str, str], *, session: Optional[aiohttp.ClientSession] = None,
                 timeout: TimeoutConfig = None, connector: Optional[aiohttp.BaseConnector] = None,
                 retry_count: int = 0, retry_backoff: float = 0.25):
        self.base_url = normalize_base_url(base_url)
        self._headers = headers
        self._session = session
        self._session_owner = session is None
        self._timeout = normalize_timeout(timeout)
        self._connector = connector
        self._retry_count = max(retry_count, 0)
        self._retry_backoff = max(retry_backoff, 0.0)

    async def __aenter__(self):
        await self.create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def create_session(self):
        if self._session and not self._session.closed:
            return
        if not self._session_owner:
            raise RuntimeError("Переданная aiohttp-сессия закрыта.")

        self._session = aiohttp.ClientSession(**self._session_kwargs())

    async def close(self):
        if self._session_owner and self._session and not self._session.closed:
            await self._session.close()

    def _session_kwargs(self) -> dict[str, Any]:
        kwargs: dict[str, Any] = {"headers": self._headers, "json_serialize": dumps_json}
        if self._timeout is not None:
            kwargs["timeout"] = self._timeout
        if self._connector is not None:
            kwargs["connector"] = self._connector
            kwargs["connector_owner"] = False
        return kwargs

    def _request_kwargs(self, params: dict[str, Any], json_body: Any, data: Any) -> dict[str, Any]:
        kwargs: dict[str, Any] = {"params": params, "json": json_body, "data": data}
        if self._timeout is not None:
            kwargs["timeout"] = self._timeout
        if not self._session_owner:
            kwargs["headers"] = self._headers
        return kwargs

    def _build_url(self, path: str) -> str:
        return f"{self.base_url}{path.lstrip('/')}"

    async def _make_request(self, session: aiohttp.ClientSession, method: str, url: str,
                            params: dict[str, Any], json_body: Any, data: Any = None) -> Any:
        async with session.request(method, url, **self._request_kwargs(params, json_body, data)) as response:
            if 200 <= response.status < 300:
                if response.status == 204:
                    return None
                if is_json_content_type(response.content_type):
                    return await read_json_response(response)
                return await response.read()

            raise create_api_error(response.status, await read_error_data(response))

    async def _request(self, method: str, path: str, params: Optional[Mapping[str, Any]] = None,
                       json_body: Any = None, data: Any = None) -> Any:
        url = self._build_url(path)
        cleaned_params = clean_params(params)
        if self._session and self._session.closed and not self._session_owner:
            raise RuntimeError("Переданная aiohttp-сессия закрыта.")

        for attempt in range(self._retry_count + 1):
            try:
                if self._session and not self._session.closed:
                    return await self._make_request(self._session, method, url, cleaned_params, json_body, data)

                async with aiohttp.ClientSession(**self._session_kwargs()) as session:
                    return await self._make_request(session, method, url, cleaned_params, json_body, data)
            except (aiohttp.ClientError, asyncio.TimeoutError, VprikolAPIError) as exc:
                if not self._should_retry(method, attempt, exc):
                    raise
                await self._wait_before_retry(attempt)

        raise RuntimeError("Не удалось выполнить запрос.")

    def _should_retry(self, method: str, attempt: int, exc: Exception) -> bool:
        if attempt >= self._retry_count or method.upper() not in RETRY_METHODS:
            return False
        if isinstance(exc, VprikolAPIError):
            return exc.status_code in RETRY_STATUSES
        return isinstance(exc, (aiohttp.ClientError, asyncio.TimeoutError))

    async def _wait_before_retry(self, attempt: int) -> None:
        if self._retry_backoff <= 0:
            return
        await asyncio.sleep(self._retry_backoff * (2 ** attempt))
