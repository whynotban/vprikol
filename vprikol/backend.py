import aiohttp
from typing import List, Optional, Literal, Union
from pydantic import TypeAdapter

from ._http import VprikolHTTPClient
from .models.backend import (AnalyticsEventEntry, BackendMeResponse, MarketAlertSubscriptionEntry, NotificationSubscriptionEntry, TgAuthConfirmResponse, DndSettings,
                             ForumThreadEntry, BroadcastAudienceResponse, PromoActivationResponse, PromoCodeEntry,
                             TelegramStarsPaymentResponse, TelegramStarsConfirmResponse, TelegramStarsPreCheckoutResponse)
from .models.items import MarketDealsResponse


NOTIFICATION_SUBSCRIPTIONS_ADAPTER = TypeAdapter(List[NotificationSubscriptionEntry])
MARKET_ALERTS_ADAPTER = TypeAdapter(List[MarketAlertSubscriptionEntry])
FORUM_THREADS_ADAPTER = TypeAdapter(List[ForumThreadEntry])


class VprikolBackend(VprikolHTTPClient):
    def __init__(self, bot_token: str, platform: Literal["tg", "vk", "ds"], base_url: str = "https://backend.szx.su/",
                 timeout: Optional[Union[aiohttp.ClientTimeout, int, float]] = None, session: Optional[aiohttp.ClientSession] = None,
                 connector: Optional[aiohttp.BaseConnector] = None, retry_count: int = 0, retry_backoff: float = 0.25):
        self.platform = platform
        self._headers = {
            "X-Bot-Token": bot_token,
            "User-Agent": "vprikol-python-lib-backend",
        }
        super().__init__(base_url, self._headers, session=session, timeout=timeout, connector=connector,
                         retry_count=retry_count, retry_backoff=retry_backoff)

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

    async def track_events(self, events: List[AnalyticsEventEntry]) -> None:
        if not events:
            return
        await self._request(
            "POST", "analytics/bot/events",
            json_body={
                "platform": self.platform,
                "events": [event.model_dump(mode="json") for event in events],
            }
        )

    async def get_subscriptions(self, platform_user_id: int) -> List[NotificationSubscriptionEntry]:
        response = await self._request(
            "GET", "notifications/bot/subscriptions",
            params={"platform": self.platform, "platform_user_id": platform_user_id}
        )
        return NOTIFICATION_SUBSCRIPTIONS_ADAPTER.validate_python(response)

    async def get_market_alerts(self, platform_user_id: int) -> List[MarketAlertSubscriptionEntry]:
        response = await self._request(
            "GET", "notifications/bot/market-alerts",
            params={"platform": self.platform, "platform_user_id": platform_user_id}
        )
        return MARKET_ALERTS_ADAPTER.validate_python(response)

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

    async def create_telegram_stars_payment(self, platform_user_id: int, tariff_id: int, target_site_user_id: int = None, promo_code: str = None, username: str = None,
                                            first_name: str = None, last_name: str = None) -> TelegramStarsPaymentResponse:
        response = await self._request(
            "POST", "payment/telegram-stars/create",
            json_body={
                "platform_user_id": platform_user_id,
                "tariff_id": tariff_id,
                "target_site_user_id": target_site_user_id,
                "promo_code": promo_code,
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
        return FORUM_THREADS_ADAPTER.validate_python(response)

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

    async def confirm_ds_auth(self, code: str, ds_id: int, username: str, photo_url: str = None) -> TgAuthConfirmResponse:
        response = await self._request(
            "POST", "auth/ds/bot/confirm",
            json_body={
                "code": code,
                "ds_id": ds_id,
                "username": username,
                "photo_url": photo_url
            }
        )
        return TgAuthConfirmResponse.model_validate(response)
