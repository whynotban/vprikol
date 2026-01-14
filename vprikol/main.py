import datetime
import json
import aiohttp
from typing import List, Optional, Union, Literal, Dict, Any
from pydantic import TypeAdapter

from .models import (ServerStatusResponse, RatingResponse, CheckRpResponse, RpNickResponse, EstateResponse, MembersResponse,
                     FindPlayerResponse, OnlineResponse, TokenResponse, RequestLogResponse, RequestStatsResponse,
                     LeadersResponse, InterviewsResponse, PlayersResponse, MapResponse, RatingType, EstateType,
                     BotDetectionResponse, CheckRpManualOverridesListResponse, AIResponse, SSFont,
                     NicknameHistoryEntry, MoneyHistoryEntry, EstateHistoryResponse, EstateHistoryType, AdminsResponse,
                     PlayerViewsResponse, PlayerSessionsResponse, PlayerCalendarResponse, ServerOnlineHistoryResponse)
from .api import VprikolAPIError


class VprikolAPI:
    def __init__(self, token: Optional[str] = None, base_url: str = "https://api.szx.su/"):
        self.base_url = base_url
        self.headers = {"User-Agent": "vprikol-python-lib-6.0.0-release"}
        if token:
            self.headers["VP-API-Token"] = token
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    @staticmethod
    async def _make_request(session: aiohttp.ClientSession, method: str, url: str,
                            params: Optional[Dict[str, Any]], json_body: Optional[Dict[str, Any]], data: Any) -> Any:
        async with session.request(method, url, params=params, json=json_body, data=data) as response:
            if 200 <= response.status < 300:
                if response.status == 204:
                    return None
                if response.content_type == "application/json":
                    return await response.json()
                return await response.read()

            if response.content_type == "application/json":
                error_data = await response.json()
            else:
                error_data = {"detail": f"Необработанное исключение #{response.status}", "status_code": response.status}
            raise VprikolAPIError(status_code=response.status, error_data=error_data)

    async def _request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None,
                       json_body: Optional[Dict[str, Any]] = None, data: Any = None) -> Any:
        url = f"{self.base_url}{path}"

        cleaned_params = {}
        if params:
            for k, v in params.items():
                if v is not None:
                    cleaned_params[k] = v

        if self._session and not self._session.closed:
            return await self._make_request(self._session, method, url, cleaned_params, json_body, data)
        else:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                return await self._make_request(session, method, url, cleaned_params, json_body, data)

    async def get_token_information(self, token_id: Union[int, Literal["current", "all", "deactivated"]] = "current") -> Union[TokenResponse, List[TokenResponse]]:
        response = await self._request("GET", f"token/{token_id}")
        if isinstance(response, list):
            return TypeAdapter(List[TokenResponse]).validate_python(response)
        return TokenResponse.model_validate(response)

    async def get_server_status(self, server_id: int) -> ServerStatusResponse:
        response = await self._request("GET", "status", params={"server_id": str(server_id)})
        return ServerStatusResponse.model_validate(response)

    async def get_rating(self, server_id: int, rating_type: RatingType) -> RatingResponse:
        params = {"server_id": str(server_id), "rating_type": rating_type.value}
        response = await self._request("GET", "rating", params=params)
        return RatingResponse.model_validate(response)

    async def get_estate(self, server_id: int, estate_type: Optional[EstateType] = None, nickname: Optional[str] = None,
                         min_id: Optional[int] = None, max_id: Optional[int] = None) -> EstateResponse:
        params = {
            "server_id": str(server_id),
            "type": estate_type.value if estate_type else None,
            "nickname": nickname,
            "min_id": str(min_id) if min_id is not None else None,
            "max_id": str(max_id) if max_id is not None else None
        }
        response = await self._request("GET", "estate", params=params)
        return EstateResponse.model_validate(response)

    async def check_rp_nickname(self, first_name: Optional[str] = None, last_name: Optional[str] = None) -> CheckRpResponse:
        params = {"first_name": first_name, "last_name": last_name}
        response = await self._request("GET", "checkrp", params=params)
        return CheckRpResponse.model_validate(response)

    async def generate_rp_nickname(self, gender: str, nation: str) -> RpNickResponse:
        params = {"gender": gender, "nation": nation}
        response = await self._request("GET", "rpnick", params=params)
        return RpNickResponse.model_validate(response)

    async def generate_ss(self, screen: bytes, commands: List[str], text_top: bool = True, font: SSFont = SSFont.ARIAL_BOLD,
                          text_size: float = 0.95, commands_colors: Optional[Dict[str, str]] = None) -> bytes:
        form_data = aiohttp.FormData()
        form_data.add_field("screen", screen, filename="screen.png", content_type="image/png")
        for command in commands:
            form_data.add_field("commands", command)
        form_data.add_field("text_top", str(text_top).lower())
        form_data.add_field("font", font.value)
        form_data.add_field("text_size", str(text_size))
        form_data.add_field("commands_colors", json.dumps(commands_colors) if commands_colors else "{}")

        return await self._request("POST", "ss", data=form_data)

    async def generate_ai_situation(self, theme_prompt: str) -> AIResponse:
        response = await self._request("POST", "ai/situation", params={"theme_prompt": theme_prompt})
        return AIResponse.model_validate(response)

    async def get_leaders(self, server_id: int) -> LeadersResponse:
        response = await self._request("GET", "ingame/leaders", params={"server_id": str(server_id)})
        return LeadersResponse.model_validate(response)

    async def get_deputies(self, server_id: int) -> LeadersResponse:
        response = await self._request("GET", "ingame/deputies", params={"server_id": str(server_id)})
        return LeadersResponse.model_validate(response)

    async def get_interviews(self, server_id: int) -> InterviewsResponse:
        response = await self._request("GET", "ingame/interviews", params={"server_id": str(server_id)})
        return InterviewsResponse.model_validate(response)

    async def get_players(self, server_id: int) -> PlayersResponse:
        response = await self._request("GET", "ingame/players", params={"server_id": str(server_id)})
        return PlayersResponse.model_validate(response)

    async def get_server_map(self, server_id: int, only_ghetto: bool = False) -> MapResponse:
        params = {"server_id": str(server_id), "only_ghetto": str(only_ghetto).lower()}
        response = await self._request("GET", "ingame/map", params=params)
        return MapResponse.model_validate(response)

    async def get_token_requests_history(self, token_id: Union[int, Literal["current"]] = "current", limit: int = 50,
                                         request_start_id: Optional[int] = None, date_from: Optional[datetime.datetime] = None,
                                         date_to: Optional[datetime.datetime] = None, api_method: Optional[str] = None,
                                         ip_address: Optional[str] = None) -> RequestLogResponse:
        params = {
            "limit": str(limit),
            "request_start_id": str(request_start_id) if request_start_id is not None else None,
            "date_from": date_from.isoformat() if date_from else None,
            "date_to": date_to.isoformat() if date_to else None,
            "api_method": api_method,
            "ip_address": ip_address
        }
        response = await self._request("GET", f"token/{token_id}/requests", params=params)
        return RequestLogResponse.model_validate(response)

    async def get_token_requests_stats(self, token_id: Union[int, Literal["current"]] = "current",
                                       date_from: Optional[datetime.datetime] = None, date_to: Optional[datetime.datetime] = None,
                                       api_method: Optional[str] = None, ip_address: Optional[str] = None) -> RequestStatsResponse:
        params = {
            "date_from": date_from.isoformat() if date_from else None,
            "date_to": date_to.isoformat() if date_to else None,
            "api_method": api_method,
            "ip_address": ip_address
        }
        response = await self._request("GET", f"token/{token_id}/requests/stats", params=params)
        return RequestStatsResponse.model_validate(response)

    async def find_player(self, server_id: int, nickname: Optional[str] = None, account_id: Optional[int] = None,
                          is_premium: bool = False, bypass_privacy: bool = False, executor_id: Optional[int] = None,
                          platform: Optional[str] = None, is_incognito: bool = False) -> FindPlayerResponse:
        if not nickname and not account_id:
            raise ValueError("Необходимо указать nickname или account_id.")

        params = {
            "server_id": str(server_id),
            "is_premium": int(is_premium),
            "bypass_privacy": int(bypass_privacy),
            "is_incognito": int(is_incognito),
            "nickname": nickname,
            "account_id": str(account_id) if account_id is not None else None,
            "executor_id": str(executor_id) if executor_id is not None else None,
            "platform": platform
        }

        response = await self._request("GET", "player/find", params=params)
        return FindPlayerResponse.model_validate(response)

    async def get_player_online(self, server_id: int, nickname: str, date_from: Optional[datetime.datetime] = None,
                                date_to: Optional[datetime.datetime] = None) -> OnlineResponse:
        params = {
            "server_id": str(server_id),
            "nickname": nickname,
            "date_from": date_from.isoformat() if date_from else None,
            "date_to": date_to.isoformat() if date_to else None
        }
        response = await self._request("GET", "player/online", params=params)
        return OnlineResponse.model_validate(response)

    async def get_player_sessions(self, server_id: int, nickname: str,
                                  date_from: Optional[datetime.datetime] = None,
                                  date_to: Optional[datetime.datetime] = None,
                                  limit: int = 20, offset: int = 0) -> PlayerSessionsResponse:
        params = {
            "server_id": str(server_id),
            "nickname": nickname,
            "limit": str(limit),
            "offset": str(offset),
            "date_from": date_from.isoformat() if date_from else None,
            "date_to": date_to.isoformat() if date_to else None
        }
        response = await self._request("GET", "player/sessions", params=params)
        return PlayerSessionsResponse.model_validate(response)

    async def get_player_sessions_calendar(self, server_id: int, nickname: str, year: int, month: int) -> PlayerCalendarResponse:
        params = {"server_id": str(server_id), "nickname": nickname, "year": str(year), "month": str(month)}
        response = await self._request("GET", "player/sessions/calendar", params=params)
        return PlayerCalendarResponse.model_validate(response)

    async def get_player_history(self, server_id: int, history_type: Literal['nickname', 'total_money'],
                                 nickname: Optional[str] = None, account_id: Optional[int] = None,
                                 date_from: Optional[datetime.datetime] = None,
                                 date_to: Optional[datetime.datetime] = None) -> Union[List[NicknameHistoryEntry], List[MoneyHistoryEntry]]:
        if not nickname and not account_id:
            raise ValueError("Необходимо указать nickname или account_id.")

        params = {
            "server_id": str(server_id),
            "type": history_type,
            "nickname": nickname,
            "account_id": str(account_id) if account_id is not None else None,
            "date_from": date_from.isoformat() if date_from else None,
            "date_to": date_to.isoformat() if date_to else None
        }

        response = await self._request("GET", "player/history", params=params)
        if not response:
            return []
        if history_type == 'nickname':
            return TypeAdapter(List[NicknameHistoryEntry]).validate_python(response)
        else:
            return TypeAdapter(List[MoneyHistoryEntry]).validate_python(response)

    async def get_fraction_members(self, server_id: int, fraction_id: int) -> MembersResponse:
        params = {"server_id": str(server_id), "fraction_id": str(fraction_id)}
        response = await self._request("GET", "fraction/members", params=params)
        return MembersResponse.model_validate(response)

    async def get_admins_list(self, server_id: int) -> AdminsResponse:
        response = await self._request("GET", "admins/list", params={"server_id": str(server_id)})
        return AdminsResponse.model_validate(response)

    async def get_manual_checkrp_overrides(self) -> CheckRpManualOverridesListResponse:
        response = await self._request("GET", "internal/checkrp/overrides")
        return CheckRpManualOverridesListResponse.model_validate(response)

    async def confirm_rp_name(self, value_type: Literal["firstname", "surname"], value: str) -> None:
        params = {"type": value_type, "value": value}
        await self._request("POST", "internal/checkrp/confirm", params=params)

    async def deny_rp_name(self, value_type: Literal["firstname", "surname"], value: str) -> None:
        params = {"type": value_type, "value": value}
        await self._request("POST", "internal/checkrp/deny", params=params)

    async def reset_rp_name(self, value_type: Literal["firstname", "surname"], value: str) -> None:
        params = {"type": value_type, "value": value}
        await self._request("DELETE", "internal/checkrp/reset", params=params)

    async def get_current_ip(self) -> str:
        return await self._request("GET", "internal/ip")

    async def list_disabled_methods(self) -> List[str]:
        response = await self._request("GET", "internal/disabled-methods")
        return TypeAdapter(List[str]).validate_python(response)

    async def disable_method(self, method_name: str) -> None:
        await self._request("POST", "internal/disabled-methods", params={"method_name": method_name})

    async def enable_method(self, method_name: str) -> None:
        await self._request("DELETE", "internal/disabled-methods", params={"method_name": method_name})

    async def detect_bots(self, server_id: int, date_from: Optional[datetime.datetime] = None,
                          date_to: Optional[datetime.datetime] = None) -> BotDetectionResponse:
        params = {
            "server_id": str(server_id),
            "date_from": date_from.isoformat() if date_from else None,
            "date_to": date_to.isoformat() if date_to else None
        }
        response = await self._request("GET", "internal/detect-bots", params=params)
        return BotDetectionResponse.model_validate(response)

    async def create_token(self, project_label: str, service: bool = False, disabled_logs: bool = False,
                           subscription_days: Optional[int] = None) -> TokenResponse:
        body = {"project_label": project_label, "service": service, "disabled_logs": disabled_logs,
                "subscription_days": subscription_days}
        response = await self._request("POST", "internal/token", json_body=body)
        return TokenResponse.model_validate(response)

    async def update_token(self, token_id: int, project_label: Optional[str] = None, activated: Optional[bool] = None,
                           service: Optional[bool] = None, disabled_logs: Optional[bool] = None,
                           add_subscription_days: Optional[int] = None) -> TokenResponse:
        body = {}
        if project_label is not None:
            body["project_label"] = project_label
        if activated is not None:
            body["activated"] = activated
        if service is not None:
            body["service"] = service
        if disabled_logs is not None:
            body["disabled_logs"] = disabled_logs
        if add_subscription_days is not None:
            body["add_subscription_days"] = add_subscription_days
        response = await self._request("PUT", f"internal/token/{token_id}", json_body=body)
        return TokenResponse.model_validate(response)

    async def delete_token(self, token_id: int) -> None:
        await self._request("DELETE", f"internal/token/{token_id}")

    async def reissue_token(self, token_id: int) -> TokenResponse:
        response = await self._request("POST", f"internal/token/{token_id}/reissue")
        return TokenResponse.model_validate(response)

    async def find_tokens_by_ip(self, ip_address: str) -> List[TokenResponse]:
        response = await self._request("GET", f"internal/token/find-by-ip/{ip_address}")
        return TypeAdapter(List[TokenResponse]).validate_python(response)

    async def get_overall_requests_stats(self, date_from: Optional[datetime.datetime] = None,
                                         date_to: Optional[datetime.datetime] = None) -> RequestStatsResponse:
        params = {
            "date_from": date_from.isoformat() if date_from else None,
            "date_to": date_to.isoformat() if date_to else None
        }
        response = await self._request("GET", "internal/requests/stats", params=params)
        return RequestStatsResponse.model_validate(response)

    async def get_estate_history(self, server_id: int, estate_type: EstateHistoryType, estate_id: int, limit: int = 15,
                                 offset: int = 0) -> EstateHistoryResponse:
        params = {"server_id": str(server_id), "estate_type": estate_type.value, "estate_id": str(estate_id),
                  "limit": str(limit), "offset": str(offset)}
        response = await self._request("GET", "estate/history", params=params)
        return EstateHistoryResponse.model_validate(response)

    async def get_player_views(self, server_id: int, nickname: str, limit: int = 5) -> PlayerViewsResponse:
        params = {"server_id": str(server_id), "nickname": nickname, "limit": str(limit)}
        response = await self._request("GET", "player/views", params=params)
        return PlayerViewsResponse.model_validate(response)

    async def hide_profile(self, platform: Literal['vk', 'tg'], user_id: int, server_id: int, nickname: str,
                           is_superadmin: bool = False) -> None:
        body = {
            "platform": platform,
            "user_id": user_id,
            "server_id": server_id,
            "nickname": nickname,
            "is_superadmin": is_superadmin
        }
        await self._request("POST", "internal/privacy/hide", json_body=body)

    async def unhide_profile(self, platform: Literal['vk', 'tg'], user_id: int, server_id: int, nickname: str,
                             is_superadmin: bool = False) -> None:
        body = {
            "platform": platform,
            "user_id": user_id,
            "server_id": server_id,
            "nickname": nickname,
            "is_superadmin": is_superadmin
        }
        await self._request("DELETE", "internal/privacy/unhide", json_body=body)

    async def get_server_online_history(self, server_id: int, hours: int = 24) -> ServerOnlineHistoryResponse:
        params = {"server_id": str(server_id), "hours": str(hours)}
        response = await self._request("GET", "status/history", params=params)
        return ServerOnlineHistoryResponse.model_validate(response)
