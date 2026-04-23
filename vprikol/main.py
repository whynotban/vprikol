import datetime
import orjson
import aiohttp
from typing import List, Optional, Union, Literal, Dict, Any
from pydantic import TypeAdapter

from .models import (ServerStatusResponse, RatingResponse, CheckRpResponse, RpNickResponse, EstateResponse, MembersResponse,
                     FindPlayerResponse, OnlineResponse, TokenResponse, RequestLogResponse, RequestStatsResponse,
                     LeadersResponse, InterviewsResponse, PlayersResponse, MapResponse, RatingType, EstateType,
                     BotDetectionResponse, CheckRpManualOverridesListResponse, AIResponse, SSFont,
                     NicknameHistoryEntry, MoneyHistoryEntry, EstateHistoryResponse, EstateHistoryType, AdminsResponse,
                     PlayerViewsResponse, PlayerSessionsResponse, PlayerCalendarResponse, ServerOnlineHistoryResponse,
                     EXPCalcResponse, MapZonesResponse, CurrencyResponse, PunishType, PunishHistoryResponse,
                     FindStatsResponse, PlayersRequest, PlayerExtendedEntry, IngameAdminData, IngameLeaderData,
                     IngameJudgeData, IngameMapData, IngameInterviewData, FractionSalariesRequest, IngameMemberEntry,
                     PunishRequest, CurrencyRequest, RankSalaryEntry, ItemsResponse, ItemsHistoryResponse,
                     AllServersStatusResponse, GhettoRatingResponse, GhettoCapturesResponse, FamilyTopResponse,
                     FamilyCapturesResponse, ShopsResponse, ItemMarketStatsResponse, MarketDealsResponse, RateLimitStatusResponse,
                     VoteType, PlayerVoteResponse, HiddenProfilesListResponse,
                     PlayerCommentCreateRequest, PlayerCommentDeleteRequest, PlayerCommentResponse,
                     PlayerCommentsListResponse, CommentComplaintCreateRequest, CommentComplaintResponse,
                     PendingCommentsResponse, PendingComplaintsResponse, AllCommentsResponse, CommentsCountResponse)
from .api import VprikolAPIError


class VprikolAPI:
    def __init__(self, token: Optional[str] = None, base_url: str = "https://api.szx.su/"):
        self.base_url = base_url
        self.headers = {"User-Agent": "vprikol-python-lib-6.3.19-release"}
        if token:
            self.headers["VP-API-Token"] = token
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        await self.create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def create_session(self):
        if self._session and not self._session.closed:
            return

        self._session = aiohttp.ClientSession(headers=self.headers, json_serialize=lambda x: orjson.dumps(x).decode())

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    @staticmethod
    async def _make_request(session: aiohttp.ClientSession, method: str, url: str,
                            params: Optional[Dict[str, Any]], json_body: Any, data: Any) -> Any:
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
                       json_body: Any = None, data: Any = None) -> Any:
        url = f"{self.base_url}{path}"

        cleaned_params = {}
        if params:
            for k, v in params.items():
                if v is not None:
                    cleaned_params[k] = v

        if self._session and not self._session.closed:
            return await self._make_request(self._session, method, url, cleaned_params, json_body, data)
        else:
            async with aiohttp.ClientSession(headers=self.headers, json_serialize=lambda x: orjson.dumps(x).decode()) as session:
                return await self._make_request(session, method, url, cleaned_params, json_body, data)

    async def get_token_info(self, token_id: Optional[int] = None) -> TokenResponse:
        params = {"token_id": str(token_id)} if token_id else None
        response = await self._request("GET", "token/info", params=params)
        return TokenResponse.model_validate(response)

    async def get_token_list(self, status: Optional[Literal["active", "deactivated"]] = None, ip_address: Optional[str] = None) -> List[TokenResponse]:
        params = {}
        if status:
            params["status"] = status
        if ip_address:
            params["ip_address"] = ip_address
        response = await self._request("GET", "token/list", params=params)
        return TypeAdapter(List[TokenResponse]).validate_python(response)

    async def reissue_token(self, token_id: Optional[int] = None) -> TokenResponse:
        params = {"token_id": str(token_id)} if token_id else None
        response = await self._request("POST", "token/reissue", params=params)
        return TokenResponse.model_validate(response)

    async def update_token_settings(self, allowed_ips: Optional[List[str]] = None, token_id: Optional[int] = None) -> TokenResponse:
        params = {"token_id": str(token_id)} if token_id else None
        response = await self._request("PATCH", "token/settings", json_body={"allowed_ips": allowed_ips}, params=params)
        return TokenResponse.model_validate(response)

    async def get_token_limits(self, token_id: Optional[int] = None) -> RateLimitStatusResponse:
        params = {"token_id": str(token_id)} if token_id else None
        response = await self._request("GET", "token/limits", params=params)
        return RateLimitStatusResponse.model_validate(response)

    async def get_token_requests_history(self, token_id: Optional[int] = None, limit: int = 50,
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
        if token_id is not None:
            params["token_id"] = str(token_id)
        response = await self._request("GET", "token/requests", params=params)
        return RequestLogResponse.model_validate(response)

    async def get_token_requests_stats(self, token_id: Optional[int] = None,
                                       date_from: Optional[datetime.datetime] = None, date_to: Optional[datetime.datetime] = None,
                                       api_method: Optional[str] = None, ip_address: Optional[str] = None) -> RequestStatsResponse:
        params = {
            "date_from": date_from.isoformat() if date_from else None,
            "date_to": date_to.isoformat() if date_to else None,
            "api_method": api_method,
            "ip_address": ip_address
        }
        if token_id is not None:
            params["token_id"] = str(token_id)
        response = await self._request("GET", "token/requests/stats", params=params)
        return RequestStatsResponse.model_validate(response)

    async def create_token(self, project_label: str, service: bool = False, disabled_logs: bool = False,
                           subscription_days: Optional[int] = None, allowed_ips: Optional[List[str]] = None,
                           bypass_antifloods: bool = False, allowed_methods: Optional[List[str]] = None,
                           rate_limits: Optional[Dict[str, Any]] = None, daily_limit: Optional[int] = None) -> TokenResponse:
        body = {"project_label": project_label, "service": service, "disabled_logs": disabled_logs,
                "subscription_days": subscription_days, "allowed_ips": allowed_ips,
                "bypass_antifloods": bypass_antifloods, "allowed_methods": allowed_methods,
                "rate_limits": rate_limits, "daily_limit": daily_limit}
        response = await self._request("POST", "token", json_body=body)
        return TokenResponse.model_validate(response)

    async def update_token(self, token_id: int, project_label: Optional[str] = None, activated: Optional[bool] = None,
                           service: Optional[bool] = None, disabled_logs: Optional[bool] = None,
                           add_subscription_days: Optional[int] = None, allowed_ips: Optional[List[str]] = None,
                           bypass_antifloods: Optional[bool] = None, allowed_methods: Optional[List[str]] = None,
                           rate_limits: Optional[Dict[str, Any]] = None, daily_limit: Optional[int] = None) -> TokenResponse:
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
        if allowed_ips is not None:
            body["allowed_ips"] = allowed_ips
        if bypass_antifloods is not None:
            body["bypass_antifloods"] = bypass_antifloods
        if allowed_methods is not None:
            body["allowed_methods"] = allowed_methods
        if rate_limits is not None:
            body["rate_limits"] = rate_limits
        if daily_limit is not None:
            body["daily_limit"] = daily_limit
        response = await self._request("PUT", "token", params={"token_id": str(token_id)}, json_body=body)
        return TokenResponse.model_validate(response)

    async def delete_token(self, token_id: int) -> None:
        await self._request("DELETE", "token", params={"token_id": str(token_id)})

    async def update_fraction_record(self, server_id: int, fraction_id: int, online_players: int,
                                      leader_nickname: Optional[str] = None, modified_by: Optional[str] = 'admin') -> dict:
        body = {"server_id": server_id, "fraction_id": fraction_id, "online_players": online_players,
                "leader_nickname": leader_nickname, "modified_by": modified_by}
        return await self._request("PUT", "internal/fraction-record", json_body=body)

    async def get_available_methods(self) -> dict:
        return await self._request("GET", "internal/methods")

    async def get_server_status(self, server_id: Optional[int] = None) -> Union[ServerStatusResponse, AllServersStatusResponse]:
        params = {"server_id": str(server_id)} if server_id else None
        response = await self._request("GET", "status", params=params)
        if server_id is None:
            return AllServersStatusResponse.model_validate(response)
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
        form_data.add_field("commands_colors", orjson.dumps(commands_colors).decode() if commands_colors else "{}")

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

    async def find_player(self, server_id: int, nickname: Optional[str] = None, account_id: Optional[int] = None,
                          is_premium: bool = False, bypass_privacy: bool = False, executor_id: Optional[int] = None,
                          executor_site_id: Optional[int] = None,
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
            "executor_site_id": str(executor_site_id) if executor_site_id is not None else None,
            "platform": platform
        }

        response = await self._request("GET", "player/find", params=params)
        return FindPlayerResponse.model_validate(response)

    async def vote_player(self, server_id: int, account_id: int, executor_id: int, platform: str,
                          vote: Optional[VoteType] = None) -> PlayerVoteResponse:
        body = {
            "server_id": server_id,
            "account_id": account_id,
            "executor_id": executor_id,
            "platform": platform,
            "vote": vote.value if vote is not None else None
        }
        response = await self._request("POST", "player/vote", json_body=body)
        return PlayerVoteResponse.model_validate(response)

    async def create_player_comment(self, data: PlayerCommentCreateRequest) -> PlayerCommentResponse:
        response = await self._request("POST", "player/comments", json_body=data.model_dump())
        return PlayerCommentResponse.model_validate(response)

    async def get_player_comments(self, server_id: int, account_id: int,
                                  executor_id: Optional[int] = None, platform: Optional[str] = None,
                                  limit: int = 20, offset: int = 0) -> PlayerCommentsListResponse:
        params = {"server_id": str(server_id), "account_id": str(account_id),
                  "limit": str(limit), "offset": str(offset)}
        if executor_id is not None:
            params["executor_id"] = str(executor_id)
        if platform is not None:
            params["platform"] = platform
        response = await self._request("GET", "player/comments", params=params)
        return PlayerCommentsListResponse.model_validate(response)

    async def get_my_player_comment(self, server_id: int, account_id: int,
                                    executor_id: int, platform: str) -> Optional[PlayerCommentResponse]:
        params = {"server_id": str(server_id), "account_id": str(account_id),
                  "executor_id": str(executor_id), "platform": platform}
        response = await self._request("GET", "player/comments/mine", params=params)
        if response is None:
            return None
        return PlayerCommentResponse.model_validate(response)

    async def delete_player_comment(self, data: PlayerCommentDeleteRequest) -> None:
        await self._request("DELETE", "player/comments", json_body=data.model_dump())

    async def get_player_comments_count(self, server_id: int, account_id: int) -> int:
        params = {"server_id": str(server_id), "account_id": str(account_id)}
        response = await self._request("GET", "player/comments/count", params=params)
        return CommentsCountResponse.model_validate(response).count

    async def create_comment_complaint(self, data: CommentComplaintCreateRequest) -> CommentComplaintResponse:
        response = await self._request("POST", "player/comments/complaint", json_body=data.model_dump())
        return CommentComplaintResponse.model_validate(response)

    async def get_pending_comments(self, limit: int = 20, offset: int = 0) -> PendingCommentsResponse:
        params = {"limit": str(limit), "offset": str(offset)}
        response = await self._request("GET", "player/comments/pending", params=params)
        return PendingCommentsResponse.model_validate(response)

    async def get_all_comments(self, limit: int = 20, offset: int = 0,
                               status: Optional[int] = None) -> AllCommentsResponse:
        params = {"limit": str(limit), "offset": str(offset)}
        if status is not None:
            params["status"] = str(status)
        response = await self._request("GET", "player/comments/all", params=params)
        return AllCommentsResponse.model_validate(response)

    async def moderate_comment(self, comment_id: int, action: str, moderator_id: int,
                               moderator_comment: Optional[str] = None) -> PlayerCommentResponse:
        body = {"action": action, "moderator_id": moderator_id, "moderator_comment": moderator_comment}
        response = await self._request("POST", f"player/comments/{comment_id}/moderate", json_body=body)
        return PlayerCommentResponse.model_validate(response)

    async def get_pending_complaints(self, limit: int = 20, offset: int = 0) -> PendingComplaintsResponse:
        params = {"limit": str(limit), "offset": str(offset)}
        response = await self._request("GET", "player/comments/complaints/pending", params=params)
        return PendingComplaintsResponse.model_validate(response)

    async def moderate_complaint(self, complaint_id: int, action: str, moderator_id: int) -> CommentComplaintResponse:
        body = {"action": action, "moderator_id": moderator_id}
        response = await self._request("POST", f"player/comments/complaints/{complaint_id}/moderate", json_body=body)
        return CommentComplaintResponse.model_validate(response)

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

    async def get_hidden_players(self, user_id: int) -> HiddenProfilesListResponse:
        response = await self._request("GET", "internal/privacy/list",
                                       params={"user_id": str(user_id)})
        return HiddenProfilesListResponse.model_validate(response)

    async def get_server_online_history(self, server_id: int, hours: int = 24) -> ServerOnlineHistoryResponse:
        params = {"server_id": str(server_id), "hours": str(hours)}
        response = await self._request("GET", "status/history", params=params)
        return ServerOnlineHistoryResponse.model_validate(response)

    async def calculate_exp(self, current_lvl: int, target_lvl: int, current_exp: int) -> EXPCalcResponse:
        params = {"current_lvl": str(current_lvl), "target_lvl": str(target_lvl), "current_exp": str(current_exp)}
        response = await self._request("GET", "exp_calc", params=params)
        return EXPCalcResponse.model_validate(response)

    async def get_map_zones(self, server_id: int) -> MapZonesResponse:
        response = await self._request("GET", "ingame/map/zones", params={"server_id": str(server_id)})
        return MapZonesResponse.model_validate(response)

    async def get_currency(self, server_id: int) -> CurrencyResponse:
        response = await self._request("GET", "ingame/currency", params={"server_id": str(server_id)})
        return CurrencyResponse.model_validate(response)

    async def get_all_currencies(self) -> List[CurrencyResponse]:
        response = await self._request("GET", "ingame/currency/all")
        return [CurrencyResponse.model_validate(item) for item in response]

    async def get_punishes(self, server_id: int, player_nickname: Optional[str] = None,
                           admin_nickname: Optional[str] = None, punish_type: Optional[PunishType] = None,
                           date_from: Optional[datetime.datetime] = None, date_to: Optional[datetime.datetime] = None,
                           limit: int = 100, offset: int = 0) -> PunishHistoryResponse:
        params = {
            "server_id": str(server_id),
            "player_nickname": player_nickname,
            "admin_nickname": admin_nickname,
            "punish_type": punish_type.value if punish_type else None,
            "date_from": date_from.isoformat() if date_from else None,
            "date_to": date_to.isoformat() if date_to else None,
            "limit": str(limit),
            "offset": str(offset)
        }
        response = await self._request("GET", "player/punishes", params=params)
        return PunishHistoryResponse.model_validate(response)

    async def get_find_stats(self) -> FindStatsResponse:
        response = await self._request("GET", "internal/stats/find")
        return FindStatsResponse.model_validate(response)

    async def post_turnstile(self, captcha_token: str) -> None:
        await self._request("POST", "internal/turnstile", params={"captcha_token": captcha_token})

    async def get_account_token(self) -> Optional[str]:
        return await self._request("GET", "internal/account-token")

    async def update_players(self, server_id: int, players: List[dict]) -> List[str]:
        req = PlayersRequest(server_id=server_id, players=players)
        response = await self._request("POST", "internal/players", json_body=req.model_dump())
        return TypeAdapter(List[str]).validate_python(response)

    async def update_players_extended(self, server_id: int, players: List[PlayerExtendedEntry]) -> None:
        body = [p.model_dump() for p in players]
        await self._request("POST", "internal/players/extended", params={"server_id": str(server_id)}, json_body=body)

    async def update_admins(self, server_id: int, admins: List[IngameAdminData]) -> None:
        body = [a.model_dump() for a in admins]
        await self._request("POST", "internal/admins", params={"server_id": str(server_id)}, json_body=body)

    async def update_leaders(self, server_id: int, leaders: List[IngameLeaderData]) -> None:
        body = [l.model_dump() for l in leaders]
        await self._request("POST", "internal/leaders", params={"server_id": str(server_id)}, json_body=body)

    async def update_deputies(self, server_id: int, deputies: List[IngameLeaderData]) -> None:
        body = [d.model_dump() for d in deputies]
        await self._request("POST", "internal/deputies", params={"server_id": str(server_id)}, json_body=body)

    async def update_judges(self, server_id: int, judges: List[IngameJudgeData]) -> None:
        body = [j.model_dump() for j in judges]
        await self._request("POST", "internal/judges", params={"server_id": str(server_id)}, json_body=body)

    async def update_map(self, server_id: int, zones: List[IngameMapData]) -> None:
        body = [z.model_dump() for z in zones]
        await self._request("POST", "internal/map", params={"server_id": str(server_id)}, json_body=body)

    async def update_interviews(self, server_id: int, interviews: List[IngameInterviewData]) -> None:
        body = [i.model_dump() for i in interviews]
        await self._request("POST", "internal/interviews", params={"server_id": str(server_id)}, json_body=body)

    async def update_salaries(self, server_id: int, salaries: Dict[str, List[RankSalaryEntry]]) -> None:
        req = FractionSalariesRequest(server_id=server_id, data=salaries)
        await self._request("POST", "internal/salaries", json_body=req.model_dump())

    async def update_members(self, server_id: int, members: Dict[str, List[IngameMemberEntry]]) -> None:
        body = {k: [m.model_dump() for m in v] for k, v in members.items()}
        await self._request("POST", "internal/members", params={"server_id": str(server_id)}, json_body=body)

    async def update_auth_token(self, server_id: int, token: str) -> None:
        await self._request("POST", "internal/auth", params={"server_id": str(server_id), "token": token})

    async def get_server_ip(self, host: str) -> str:
        return await self._request("GET", "internal/server-ip", params={"host": host})

    async def save_punish(self, punish_request: PunishRequest) -> None:
        await self._request("POST", "internal/punish", json_body=punish_request.model_dump())

    async def update_currency(self, server_id: int, currency: CurrencyRequest) -> None:
        await self._request("POST", "internal/currency", params={"server_id": str(server_id)}, json_body=currency.model_dump())

    async def get_items(self, item_type: Optional[int] = None, name: Optional[str] = None,
                        skin_id: Optional[int] = None, limit: int = 50, offset: int = 0) -> ItemsResponse:
        params = {
            "item_type": str(item_type) if item_type is not None else None,
            "name": name,
            "skin_id": str(skin_id) if skin_id is not None else None,
            "limit": str(limit),
            "offset": str(offset)
        }
        response = await self._request("GET", "items/list", params=params)
        return ItemsResponse.model_validate(response)

    async def get_ghetto_rating(self, server_id: int) -> GhettoRatingResponse:
        response = await self._request("GET", "ingame/ghetto/rating", params={"server_id": str(server_id)})
        return GhettoRatingResponse.model_validate(response)

    async def get_ghetto_captures(self, server_id: int) -> GhettoCapturesResponse:
        response = await self._request("GET", "ingame/ghetto/captures", params={"server_id": str(server_id)})
        return GhettoCapturesResponse.model_validate(response)

    async def get_family_top(self, server_id: int) -> FamilyTopResponse:
        response = await self._request("GET", "ingame/family/top", params={"server_id": str(server_id)})
        return FamilyTopResponse.model_validate(response)

    async def get_family_captures(self, server_id: int) -> FamilyCapturesResponse:
        response = await self._request("GET", "ingame/family/captures", params={"server_id": str(server_id)})
        return FamilyCapturesResponse.model_validate(response)

    async def get_shops(self, server_id: Optional[int] = None, nickname: Optional[str] = None,
                        item_id: Optional[int] = None, min_price: Optional[int] = None,
                        max_price: Optional[int] = None, type: Optional[str] = None,
                        limit: int = 50, offset: int = 0) -> ShopsResponse:
        params = {
            "server_id": str(server_id) if server_id is not None else None,
            "nickname": nickname,
            "item_id": str(item_id) if item_id is not None else None,
            "min_price": str(min_price) if min_price is not None else None,
            "max_price": str(max_price) if max_price is not None else None,
            "type": type,
            "limit": str(limit),
            "offset": str(offset)
        }
        response = await self._request("GET", "items/shops", params=params)
        return ShopsResponse.model_validate(response)

    async def get_shop_deals(self, server_id: int, item_id: Optional[int] = None,
                             mod_level: Optional[int] = None, include_modded: bool = True,
                             min_profit: int = 0,
                             sort: Literal['profit', 'discount', 'price'] = 'profit',
                             limit: int = 20, offset: int = 0) -> MarketDealsResponse:
        params = {
            "server_id": str(server_id),
            "item_id": str(item_id) if item_id is not None else None,
            "mod_level": str(mod_level) if mod_level is not None else None,
            "include_modded": str(include_modded).lower(),
            "min_profit": str(min_profit),
            "sort": sort,
            "limit": str(limit),
            "offset": str(offset)
        }
        response = await self._request("GET", "shops/deals", params=params)
        return MarketDealsResponse.model_validate(response)

    async def get_item_market_details(self, item_id: int, server_id: int = 1000,
                                      period: Literal['1d', '1w', '1m', '3m', '6m', '1y'] = '1m') -> ItemMarketStatsResponse:
        params = {"item_id": str(item_id), "server_id": str(server_id), "period": period}
        response = await self._request("GET", "items/market", params=params)
        return ItemMarketStatsResponse.model_validate(response)

    async def get_items_history(self, item_id: Optional[int] = None, limit: int = 100, offset: int = 0) -> ItemsHistoryResponse:
        params = {
            "item_id": str(item_id) if item_id is not None else None,
            "limit": str(limit),
            "offset": str(offset)
        }
        response = await self._request("GET", "items/history", params=params)
        return ItemsHistoryResponse.model_validate(response)
