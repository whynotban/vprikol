import orjson
import aiohttp
from typing import List, Optional, Literal

from .api import VprikolAPIError
from .models.backend import BackendMeResponse, NotificationSubscriptionEntry


class VprikolBackend:
    def __init__(self, bot_token: str, platform: Literal["tg", "vk"],
                 base_url: str = "https://backend.szx.su/"):
        self.base_url = base_url
        self.platform = platform
        self._headers = {
            "X-Bot-Token": bot_token,
            "User-Agent": "vprikol-python-lib-backend",
        }
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        await self.create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def create_session(self):
        if self._session and not self._session.closed:
            return
        self._session = aiohttp.ClientSession(
            headers=self._headers,
            json_serialize=lambda x: orjson.dumps(x).decode()
        )

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    @staticmethod
    async def _make_request(session: aiohttp.ClientSession, method: str, url: str,
                            params: dict, json_body):
        async with session.request(method, url, params=params, json=json_body) as response:
            if 200 <= response.status < 300:
                if response.status == 204:
                    return None
                if response.content_type == "application/json":
                    return await response.json(loads=orjson.loads)
                return await response.read()
            if response.content_type == "application/json":
                error_data = await response.json(loads=orjson.loads)
            else:
                error_data = {"detail": f"HTTP {response.status}", "status_code": response.status}
            raise VprikolAPIError(status_code=response.status, error_data=error_data)

    async def _request(self, method: str, path: str, params: dict = None, json_body=None):
        url = f"{self.base_url}{path}"
        cleaned_params = {k: v for k, v in (params or {}).items() if v is not None}

        if self._session and not self._session.closed:
            return await self._make_request(self._session, method, url, cleaned_params, json_body)
        else:
            async with aiohttp.ClientSession(
                headers=self._headers,
                json_serialize=lambda x: orjson.dumps(x).decode()
            ) as session:
                return await self._make_request(session, method, url, cleaned_params, json_body)

    async def get_me(self, platform_user_id: int) -> BackendMeResponse:
        response = await self._request(
            "GET", "notifications/bot/me",
            params={"platform": self.platform, "platform_user_id": platform_user_id}
        )
        return BackendMeResponse.model_validate(response)

    async def get_subscriptions(self, platform_user_id: int) -> List[NotificationSubscriptionEntry]:
        response = await self._request(
            "GET", "notifications/bot/subscriptions",
            params={"platform": self.platform, "platform_user_id": platform_user_id}
        )
        from pydantic import TypeAdapter
        return TypeAdapter(List[NotificationSubscriptionEntry]).validate_python(response)

    async def add_subscription(self, platform_user_id: int, server_id: int,
                               event_type: str, target_value: str = "*") -> NotificationSubscriptionEntry:
        response = await self._request(
            "POST", "notifications/bot/subscriptions",
            json_body={
                "platform": self.platform,
                "platform_user_id": platform_user_id,
                "server_id": server_id,
                "event_type": event_type,
                "target_value": target_value
            }
        )
        return NotificationSubscriptionEntry.model_validate(response)

    async def delete_subscription(self, platform_user_id: int, sub_id: int) -> None:
        await self._request(
            "DELETE", f"notifications/bot/subscriptions/{sub_id}",
            params={"platform": self.platform, "platform_user_id": platform_user_id}
        )

    async def set_notify_platform(self, platform_user_id: int, notify_platform: str) -> None:
        await self._request(
            "PATCH", "notifications/bot/platform",
            params={"platform": self.platform, "platform_user_id": platform_user_id},
            json_body={"notify_platform": notify_platform}
        )
