import orjson
import aiohttp
from typing import List, Optional, Literal

from .api import VprikolAPIError
from .models.backend import (BackendMeResponse, MarketAlertSubscriptionEntry, NotificationSubscriptionEntry, TgAuthConfirmResponse, DndSettings,
                             ForumThreadEntry, BroadcastAudienceResponse, PromoActivationResponse, PromoCodeEntry,
                             TelegramStarsPaymentResponse, TelegramStarsConfirmResponse, TelegramStarsPreCheckoutResponse)
from .models.items import MarketDealsResponse


class VprikolBackend:
    def __init__(self, bot_token: str, platform: Literal["tg", "vk"], base_url: str = "https://backend.szx.su/"):
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

    async def get_market_deals(self, platform_user_id: int, server_id: int, item_id: Optional[int] = None,
                               include_modded: bool = True, allow_vc_routes: bool = True, min_profit: int = 0, min_discount: int = 0,
                               sort: Literal["profit", "discount", "price"] = "profit",
                               limit: int = 20, offset: int = 0) -> MarketDealsResponse:
        response = await self._request(
            "GET", "notifications/bot/market/deals",
            params={
                "platform": self.platform,
                "platform_user_id": platform_user_id,
                "server_id": server_id,
                "item_id": item_id,
                "include_modded": str(include_modded).lower(),
                "allow_vc_routes": str(allow_vc_routes).lower(),
                "min_profit": min_profit,
                "min_discount": min_discount,
                "sort": sort,
                "limit": limit,
                "offset": offset,
            }
        )
        return MarketDealsResponse.model_validate(response)

    async def get_subscriptions(self, platform_user_id: int) -> List[NotificationSubscriptionEntry]:
        response = await self._request(
            "GET", "notifications/bot/subscriptions",
            params={"platform": self.platform, "platform_user_id": platform_user_id}
        )
        from pydantic import TypeAdapter
        return TypeAdapter(List[NotificationSubscriptionEntry]).validate_python(response)

    async def get_market_alerts(self, platform_user_id: int) -> List[MarketAlertSubscriptionEntry]:
        response = await self._request(
            "GET", "notifications/bot/market-alerts",
            params={"platform": self.platform, "platform_user_id": platform_user_id}
        )
        from pydantic import TypeAdapter
        return TypeAdapter(List[MarketAlertSubscriptionEntry]).validate_python(response)

    async def add_subscription(self, platform_user_id: int, server_id: Optional[int],
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

    async def get_dnd_settings(self, platform_user_id: int) -> DndSettings:
        response = await self._request(
            "GET", "notifications/bot/dnd",
            params={"platform": self.platform, "platform_user_id": platform_user_id}
        )
        return DndSettings.model_validate(response)

    async def set_dnd_settings(self, platform_user_id: int, dnd_start_hour: Optional[int], dnd_end_hour: Optional[int]) -> None:
        await self._request(
            "PATCH", "notifications/bot/dnd",
            params={"platform": self.platform, "platform_user_id": platform_user_id},
            json_body={"dnd_start_hour": dnd_start_hour, "dnd_end_hour": dnd_end_hour}
        )

    async def get_broadcast_audience(self, ref_levels: List[int], active_paid_subscription: bool = False,) -> List[int]:
        response = await self._request(
            "POST", "notifications/bot/broadcast/audience",
            json_body={
                "platform": self.platform,
                "ref_levels": ref_levels,
                "active_paid_subscription": active_paid_subscription,
            }
        )
        return BroadcastAudienceResponse.model_validate(response).user_ids

    async def activate_promo(self, platform_user_id: int, code: str) -> PromoActivationResponse:
        response = await self._request(
            "POST", "notifications/bot/promos/activate",
            json_body={
                "platform": self.platform,
                "platform_user_id": platform_user_id,
                "code": code,
            },
        )
        return PromoActivationResponse.model_validate(response)

    async def create_telegram_stars_payment(self, platform_user_id: int, tariff_id: int, target_site_user_id: int = None, username: str = None,
                                            first_name: str = None, last_name: str = None) -> TelegramStarsPaymentResponse:
        response = await self._request(
            "POST", "payment/telegram-stars/create",
            json_body={
                "platform_user_id": platform_user_id,
                "tariff_id": tariff_id,
                "target_site_user_id": target_site_user_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
            },
        )
        return TelegramStarsPaymentResponse.model_validate(response)

    async def confirm_telegram_stars_payment(self, platform_user_id: int, payment_id: str, total_amount: int,
                                             telegram_payment_charge_id: str) -> TelegramStarsConfirmResponse:
        response = await self._request(
            "POST", "payment/telegram-stars/confirm",
            json_body={
                "platform_user_id": platform_user_id,
                "payment_id": payment_id,
                "total_amount": total_amount,
                "telegram_payment_charge_id": telegram_payment_charge_id,
            },
        )
        return TelegramStarsConfirmResponse.model_validate(response)

    async def pre_checkout_telegram_stars_payment(self, payment_id: str, total_amount: int) -> TelegramStarsPreCheckoutResponse:
        response = await self._request(
            "POST", "payment/telegram-stars/pre-checkout",
            json_body={
                "payment_id": payment_id,
                "total_amount": total_amount,
            },
        )
        return TelegramStarsPreCheckoutResponse.model_validate(response)

    async def create_promo(self, platform_user_id: int, code: str, reward_type: str, reward_value: int = 3,
                           duration_seconds: int = None, duration_hours: int = None, duration_days: int = None,
                           title: str = None, max_activations: int = None, per_user_limit: int = 1,
                           starts_at: str = None, expires_at: str = None, allowed_platforms: List[str] = None,
                           allowed_user_ids: List[int] = None, require_site_account: bool = True) -> PromoCodeEntry:
        response = await self._request(
            "POST", "notifications/bot/promos",
            json_body={
                "platform": self.platform,
                "platform_user_id": platform_user_id,
                "code": code,
                "reward_type": reward_type,
                "reward_value": reward_value,
                "duration_seconds": duration_seconds,
                "duration_hours": duration_hours,
                "duration_days": duration_days,
                "title": title,
                "max_activations": max_activations,
                "per_user_limit": per_user_limit,
                "starts_at": starts_at,
                "expires_at": expires_at,
                "allowed_platforms": allowed_platforms or [],
                "allowed_user_ids": allowed_user_ids or [],
                "require_site_account": require_site_account,
            },
        )
        return PromoCodeEntry.model_validate(response)

    async def delete_promo(self, code: str) -> None:
        await self._request("DELETE", f"notifications/bot/promos/{code}")

    async def list_forum_threads(self, platform_user_id: int) -> List[ForumThreadEntry]:
        response = await self._request(
            "GET", "forum/bot/threads",
            params={"platform": self.platform, "platform_user_id": platform_user_id}
        )
        from pydantic import TypeAdapter
        return TypeAdapter(List[ForumThreadEntry]).validate_python(response)

    async def add_forum_thread(self, platform_user_id: int, raw_input: str, subscription_platform_user_id: Optional[int] = None) -> ForumThreadEntry:
        response = await self._request(
            "POST", "forum/bot/threads",
            json_body={
                "platform": self.platform,
                "platform_user_id": platform_user_id,
                "subscription_platform_user_id": subscription_platform_user_id,
                "raw_input": raw_input,
            }
        )
        return ForumThreadEntry.model_validate(response)

    async def delete_forum_thread(self, platform_user_id: int, thread_id: int) -> None:
        await self._request(
            "DELETE", f"forum/bot/threads/{thread_id}",
            params={"platform": self.platform, "platform_user_id": platform_user_id}
        )

    async def confirm_tg_auth(self, code: str, tg_id: int, first_name: str,
                               last_name: str = None, username: str = None,
                               photo_url: str = None) -> TgAuthConfirmResponse:
        response = await self._request(
            "POST", "auth/tg/bot/confirm",
            json_body={
                "code": code,
                "tg_id": tg_id,
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "photo_url": photo_url
            }
        )
        return TgAuthConfirmResponse.model_validate(response)
