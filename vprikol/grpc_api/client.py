from __future__ import annotations

import datetime
import os
from enum import Enum
from typing import Any, Literal
from google.protobuf.empty_pb2 import Empty
from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf.struct_pb2 import Struct
from google.protobuf.timestamp_pb2 import Timestamp

try:
    import grpc
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("Для gRPC клиента установите пакет с extra-зависимостями: vprikol[grpc].") from exc

from ._generated import vprikol_pb2 as pb
from ._generated import vprikol_pb2_grpc as pb_grpc
from ..api import create_api_error
from ..models import (AdminsResponse, AllCommentsResponse, AllServersStatusResponse, CheckRpManualOverridesListResponse, CheckRpResponse, CommentComplaintCreateRequest,
                      CommentComplaintResponse, CurrencyResponse, EstateHistoryResponse, EstateHistoryType, EstateResponse, EstateType, EXPCalcResponse,
                      FamilyCapturesResponse, FamilyTopResponse, FindPlayerResponse, FractionMemberHistoryResponse, GhettoCapturesResponse, GhettoRatingResponse,
                      HiddenProfilesListResponse, HostStatsResponse, ItemMarketStatsResponse, ItemsHistoryResponse, ItemsResponse, InterviewsResponse,
                      LeadersResponse, MapResponse, MapZonesResponse, MarketplaceAuthorContext, MarketplaceAuthorRequest, MarketplaceContactClickRequest,
                      MarketplaceFavoriteRequest, MarketplaceListingActionRequest, MarketplaceListingDeleteRequest, MarketplaceListingResponse,
                      MarketplaceListingsResponse, MarketplaceModerationListResponse, MarketplaceModerationRequest, MarketplaceMyListingsResponse,
                      MarketplacePromoteRequest, MarketplacePromoteResponse, MarketplaceSimilarResponse, MarketplaceUserListingCreateRequest,
                      MarketplaceUserListingPatchRequest, MembersResponse, MoneyHistoryEntry, NicknameHistoryEntry, OnlineResponse, PendingCommentsResponse,
                      PendingComplaintsResponse, PlayerCalendarResponse, PlayerCommentCreateRequest, PlayerCommentDeleteRequest, PlayerCommentResponse,
                      PlayerCommentsListResponse, PlayerSessionsResponse, PlayersResponse, PunishHistoryResponse, PunishType, RateLimitStatusResponse,
                      RatingResponse, RatingType, RequestLogResponse, RequestStatsResponse, RpNickResponse, ServerOnlineHistoryResponse, ServerStatusResponse,
                      ShopsResponse, TokenResponse)


class VprikolGrpcAPI:
    def __init__(self, token: str, endpoint: str = "dev-api.szx.su:443", grpc_token: str | None = None, timeout: float | None = 15,
                 secure: bool = True) -> None:
        self.token = token
        self.endpoint = endpoint
        self.grpc_token = grpc_token or os.getenv("VPRIKOL_GRPC_TOKEN")
        if not self.grpc_token:
            raise ValueError("Передайте grpc_token=... или задайте переменную окружения VPRIKOL_GRPC_TOKEN.")
        self.timeout = timeout
        self.secure = secure
        self._channel: grpc.aio.Channel | None = None
        self._stub: pb_grpc.VprikolAPIStub | None = None

    async def __aenter__(self) -> "VprikolGrpcAPI":
        self._ensure_stub()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    async def close(self) -> None:
        if self._channel is not None:
            await self._channel.close()
            self._channel = None
            self._stub = None

    async def create_session(self) -> None:
        self._ensure_stub()

    async def get_token_info(self, token_id: int | None = None) -> TokenResponse:
        request = pb.GetTokenInfoRequest()
        if token_id is not None:
            request.token_id = token_id
        data = _message_to_dict(await self._call(self._ensure_stub().GetTokenInfo, request))
        _set_missing(data, "daily_limit", "subscription_until")
        data.setdefault("allowed_ips", [])
        data.setdefault("allowed_methods", [])
        data.setdefault("rate_limits", {})
        return TokenResponse.model_validate(data)

    async def get_token_list(self, status: Literal["active", "deactivated"] | None = None, ip_address: str | None = None) -> list[TokenResponse]:
        request = pb.GetTokenListRequest()
        if status:
            request.status = status
        if ip_address:
            request.ip_address = ip_address
        return [TokenResponse.model_validate(entry) for entry in _json_data(await self._call(self._ensure_stub().GetTokenList, request)) or []]

    async def reissue_token(self, token_id: int | None = None) -> TokenResponse:
        request = pb.ReissueTokenRequest()
        if token_id is not None:
            request.token_id = token_id
        data = _message_to_dict(await self._call(self._ensure_stub().ReissueToken, request))
        _set_missing(data, "daily_limit", "subscription_until")
        data.setdefault("allowed_ips", [])
        data.setdefault("allowed_methods", [])
        data.setdefault("rate_limits", {})
        return TokenResponse.model_validate(data)

    async def get_token_limits(self, token_id: int | None = None) -> RateLimitStatusResponse:
        request = pb.GetTokenInfoRequest()
        if token_id is not None:
            request.token_id = token_id
        return RateLimitStatusResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetTokenLimits, request)) or {})

    async def create_token(self, project_label: str, service: bool = False, disabled_logs: bool = False, subscription_days: int | None = None,
                           allowed_ips: list[str] | None = None, bypass_antifloods: bool = False, allowed_methods: list[str] | None = None,
                           rate_limits: dict[str, Any] | None = None, daily_limit: int | None = None) -> TokenResponse:
        request = pb.CreateTokenRequest(project_label=project_label, service=service, disabled_logs=disabled_logs, allowed_ips=allowed_ips or [],
                                        bypass_antifloods=bypass_antifloods, allowed_methods=allowed_methods or [], rate_limits=_struct(rate_limits))
        if subscription_days is not None:
            request.subscription_days = subscription_days
        if daily_limit is not None:
            request.daily_limit = daily_limit
        return TokenResponse.model_validate(_message_to_dict(await self._call(self._ensure_stub().CreateToken, request)))

    async def update_token(self, token_id: int, project_label: str | None = None, activated: bool | None = None, service: bool | None = None,
                           disabled_logs: bool | None = None, add_subscription_days: int | None = None, allowed_ips: list[str] | None = None,
                           bypass_antifloods: bool | None = None, allowed_methods: list[str] | None = None, rate_limits: dict[str, Any] | None = None,
                           daily_limit: int | None = None) -> TokenResponse:
        request = pb.UpdateTokenRequest(token_id=token_id)
        if project_label is not None:
            request.project_label = project_label
        if activated is not None:
            request.activated = activated
        if service is not None:
            request.service = service
        if disabled_logs is not None:
            request.disabled_logs = disabled_logs
        if add_subscription_days is not None:
            request.add_subscription_days = add_subscription_days
        if allowed_ips is not None:
            request.allowed_ips.extend(allowed_ips)
        if bypass_antifloods is not None:
            request.bypass_antifloods = bypass_antifloods
        if allowed_methods is not None:
            request.allowed_methods.extend(allowed_methods)
        if rate_limits is not None:
            request.rate_limits.CopyFrom(_struct(rate_limits))
        if daily_limit is not None:
            request.daily_limit = daily_limit
        return TokenResponse.model_validate(_message_to_dict(await self._call(self._ensure_stub().UpdateToken, request)))

    async def delete_token(self, token_id: int) -> None:
        await self._call(self._ensure_stub().DeleteToken, pb.DeleteTokenRequest(token_id=token_id))

    async def update_fraction_record(self, server_id: int, fraction_id: int, online_players: int, leader_nickname: str | None = None,
                                     modified_by: str | None = "admin") -> dict[str, Any]:
        request = pb.UpdateFractionRecordRequest(server_id=server_id, fraction_id=fraction_id, online_players=online_players)
        if leader_nickname is not None:
            request.leader_nickname = leader_nickname
        if modified_by is not None:
            request.modified_by = modified_by
        return dict(_json_data(await self._call(self._ensure_stub().UpdateFractionRecord, request)) or {})

    async def get_available_methods(self) -> dict[str, Any]:
        return dict(_json_data(await self._call(self._ensure_stub().GetAvailableMethods, Empty())) or {})

    async def check_rp_nickname(self, first_name: str | None = None, last_name: str | None = None) -> CheckRpResponse:
        request = pb.CheckRpNicknameRequest()
        if first_name is not None:
            request.first_name = first_name
        if last_name is not None:
            request.last_name = last_name
        return CheckRpResponse.model_validate(_json_data(await self._call(self._ensure_stub().CheckRpNickname, request)))

    async def generate_rp_nickname(self, gender: str, nation: str) -> RpNickResponse:
        return RpNickResponse.model_validate(_json_data(await self._call(self._ensure_stub().GenerateRpNickname, pb.GenerateRpNicknameRequest(gender=gender, nation=nation))))

    async def get_token_requests_history(self, token_id: int | None = None, limit: int = 50, request_start_id: int | None = None,
                                         date_from: datetime.datetime | None = None, date_to: datetime.datetime | None = None,
                                         api_method: str | None = None, ip_address: str | None = None) -> RequestLogResponse:
        request = pb.GetTokenRequestsRequest(limit=limit)
        if token_id is not None:
            request.token_id = token_id
        if request_start_id is not None:
            request.request_start_id = request_start_id
        _set_timestamp(request.date_from, date_from)
        _set_timestamp(request.date_to, date_to)
        if api_method:
            request.api_method = api_method
        if ip_address:
            request.ip_address = ip_address
        data = _message_to_dict(await self._call(self._ensure_stub().GetTokenRequests, request))
        data.setdefault("next_request_start_id", None)
        for entry in data.setdefault("data", []):
            entry.setdefault("api_method", None)
            entry.setdefault("request_id", None)
            entry.setdefault("params", {})
        return RequestLogResponse.model_validate(data)

    async def get_token_requests_stats(self, token_id: int | None = None, date_from: datetime.datetime | None = None,
                                       date_to: datetime.datetime | None = None, api_method: str | None = None,
                                       ip_address: str | None = None) -> RequestStatsResponse:
        request = pb.GetTokenRequestsStatsRequest()
        if token_id is not None:
            request.token_id = token_id
        _set_timestamp(request.date_from, date_from)
        _set_timestamp(request.date_to, date_to)
        if api_method:
            request.api_method = api_method
        if ip_address:
            request.ip_address = ip_address
        data = _message_to_dict(await self._call(self._ensure_stub().GetTokenRequestsStats, request))
        data.setdefault("methods", {})
        return RequestStatsResponse.model_validate(data)

    async def get_server_status(self, server_id: int | None = None) -> ServerStatusResponse | AllServersStatusResponse:
        request = pb.GetStatusRequest()
        if server_id is not None:
            request.server_id = server_id
        data = _message_to_dict(await self._call(self._ensure_stub().GetStatus, request))
        if "server" in data:
            return ServerStatusResponse.model_validate(_normalize_status(data["server"]))
        all_servers = data.get("all_servers", {"data": []})
        for entry in all_servers.get("data", []):
            _normalize_status(entry)
        return AllServersStatusResponse.model_validate(all_servers)

    async def get_rating(self, server_id: int, rating_type: RatingType | str) -> RatingResponse:
        data = _message_to_dict(await self._call(self._ensure_stub().GetRating, pb.GetRatingRequest(server_id=server_id, rating_type=_enum_value(rating_type))))
        for player in data.setdefault("players", []):
            _set_missing(player, "server_id", "server_label", "additional_value", "az_coins", "family")
        return RatingResponse.model_validate(data)

    async def get_estate(self, server_id: int, estate_type: EstateType | str | None = None, nickname: str | None = None,
                         min_id: int | None = None, max_id: int | None = None) -> EstateResponse:
        request = pb.GetEstateRequest(server_id=server_id)
        if estate_type is not None:
            request.estate_type = _enum_value(estate_type)
        if nickname is not None:
            request.nickname = nickname
        if min_id is not None:
            request.min_id = min_id
        if max_id is not None:
            request.max_id = max_id
        data = _message_to_dict(await self._call(self._ensure_stub().GetEstate, request))
        for house in data.setdefault("houses", []):
            _set_missing(house, "owner", "name")
            house.setdefault("auction", {}).setdefault("time_end", None)
        for business in data.setdefault("businesses", []):
            business.setdefault("owner", None)
            business.setdefault("auction", {}).setdefault("time_end", None)
        return EstateResponse.model_validate(data)

    async def get_leaders(self, server_id: int) -> LeadersResponse:
        data = _message_to_dict(await self._call(self._ensure_stub().GetLeaders, pb.ServerRequest(server_id=server_id)))
        for entry in data.setdefault("data", []):
            _set_missing(entry, "phone_number", "afk")
        return LeadersResponse.model_validate(data)

    async def get_deputies(self, server_id: int) -> LeadersResponse:
        data = _message_to_dict(await self._call(self._ensure_stub().GetDeputies, pb.ServerRequest(server_id=server_id)))
        for entry in data.setdefault("data", []):
            _set_missing(entry, "phone_number", "afk")
        return LeadersResponse.model_validate(data)

    async def get_interviews(self, server_id: int) -> InterviewsResponse:
        data = _message_to_dict(await self._call(self._ensure_stub().GetInterviews, pb.ServerRequest(server_id=server_id)))
        for entry in data.setdefault("data", []):
            _set_missing(entry, "place", "time")
        return InterviewsResponse.model_validate(data)

    async def get_players(self, server_id: int) -> PlayersResponse:
        return PlayersResponse.model_validate(_message_to_dict(await self._call(self._ensure_stub().GetPlayers, pb.ServerRequest(server_id=server_id))))

    async def get_server_map(self, server_id: int, only_ghetto: bool = False) -> MapResponse:
        return MapResponse.model_validate(_message_to_dict(await self._call(self._ensure_stub().GetMap, pb.GetMapRequest(server_id=server_id, only_ghetto=only_ghetto))))

    async def get_map_zones(self, server_id: int) -> MapZonesResponse:
        return MapZonesResponse.model_validate(_message_to_dict(await self._call(self._ensure_stub().GetMapZones, pb.ServerRequest(server_id=server_id))))

    async def get_fraction_members(self, server_id: int, fraction_id: int) -> MembersResponse:
        data = _message_to_dict(await self._call(self._ensure_stub().GetFractionMembers, pb.GetFractionMembersRequest(server_id=server_id, fraction_id=fraction_id)))
        data.setdefault("leader_nickname", None)
        data.setdefault("online_record", {})
        _set_missing(data["online_record"], "leader_nickname", "modified_at")
        for player in data.setdefault("players", []):
            _set_missing(player, "account_id", "ingame_id", "nickname_color")
        return MembersResponse.model_validate(data)

    async def find_player(self, server_id: int, nickname: str | None = None, account_id: int | None = None) -> FindPlayerResponse:
        request = pb.FindPlayerRequest(server_id=server_id)
        if nickname is not None:
            request.nickname = nickname
        if account_id is not None:
            request.account_id = account_id
        data = _message_to_dict(await self._call(self._ensure_stub().FindPlayer, request))
        data.setdefault("admin_info", {"is_admin": None, "post": None, "vk_tag": None})
        _set_missing(data.setdefault("general", {}), "phone_number", "marriage", "job_label")
        _set_missing(data.setdefault("fraction", {}), "fraction_id", "fraction_label", "rank_number", "rank_label")
        data.setdefault("money", {}).setdefault("phone_balance", None)
        data["money"].setdefault("deposit", None)
        data["money"]["individual_accounts"] = _normalize_individual_accounts(data["money"].get("individual_accounts", {}))
        _set_missing(data.setdefault("vip_info", {}), "vip_lvl", "vip_label", "vip_expiration_date", "addition_vip_expiration_date")
        return FindPlayerResponse.model_validate(data)

    async def get_player_online(self, server_id: int, nickname: str, date_from: datetime.datetime | None = None,
                                date_to: datetime.datetime | None = None) -> OnlineResponse:
        request = pb.GetPlayerOnlineRequest(server_id=server_id, nickname=nickname)
        _set_timestamp(request.date_from, date_from)
        _set_timestamp(request.date_to, date_to)
        data = _message_to_dict(await self._call(self._ensure_stub().GetPlayerOnline, request))
        _set_missing(data, "active_session_login_at", "last_login_at", "last_logout_at")
        return OnlineResponse.model_validate(data)

    async def get_player_history(self, server_id: int, history_type: Literal["nickname", "total_money"], nickname: str | None = None,
                                 account_id: int | None = None, date_from: datetime.datetime | None = None,
                                 date_to: datetime.datetime | None = None) -> list[NicknameHistoryEntry] | list[MoneyHistoryEntry]:
        request = pb.GetPlayerHistoryRequest(server_id=server_id, history_type=history_type)
        if nickname is not None:
            request.nickname = nickname
        if account_id is not None:
            request.account_id = account_id
        _set_timestamp(request.date_from, date_from)
        _set_timestamp(request.date_to, date_to)
        data = _message_to_dict(await self._call(self._ensure_stub().GetPlayerHistory, request))
        if "money_history" in data:
            return [MoneyHistoryEntry.model_validate(entry) for entry in data["money_history"].get("data", [])]
        return [NicknameHistoryEntry.model_validate(entry) for entry in data.get("nickname_history", {}).get("data", [])]

    async def get_punishes(self, server_id: int, player_nickname: str | None = None, admin_nickname: str | None = None,
                           punish_type: str | None = None, date_from: datetime.datetime | None = None,
                           date_to: datetime.datetime | None = None, limit: int = 100, offset: int = 0, include_cross_server: bool = False) -> PunishHistoryResponse:
        request = pb.GetPunishesRequest(server_id=server_id, limit=limit, offset=offset, include_cross_server=include_cross_server)
        if player_nickname:
            request.player_nickname = player_nickname
        if admin_nickname:
            request.admin_nickname = admin_nickname
        if punish_type:
            request.punish_type = _enum_value(punish_type)
        _set_timestamp(request.date_from, date_from)
        _set_timestamp(request.date_to, date_to)
        data = _message_to_dict(await self._call(self._ensure_stub().GetPunishes, request))
        for entry in data.setdefault("data", []):
            entry.setdefault("expires_at", None)
        return PunishHistoryResponse.model_validate(data)

    async def get_server_online_history(self, server_id: int, hours: int = 24) -> ServerOnlineHistoryResponse:
        data = _json_data(await self._call(self._ensure_stub().GetServerOnlineHistory, pb.GetServerOnlineHistoryRequest(server_id=server_id, hours=hours)))
        return ServerOnlineHistoryResponse.model_validate(data)

    async def get_player_sessions(self, server_id: int, nickname: str, date_from: datetime.datetime | None = None,
                                  date_to: datetime.datetime | None = None, limit: int = 20, offset: int = 0) -> PlayerSessionsResponse:
        request = pb.GetPlayerSessionsRequest(server_id=server_id, nickname=nickname, limit=limit, offset=offset)
        _set_timestamp(request.date_from, date_from)
        _set_timestamp(request.date_to, date_to)
        return PlayerSessionsResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetPlayerSessions, request)))

    async def get_player_sessions_calendar(self, server_id: int, nickname: str, year: int, month: int) -> PlayerCalendarResponse:
        request = pb.GetPlayerSessionsCalendarRequest(server_id=server_id, nickname=nickname, year=year, month=month)
        return PlayerCalendarResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetPlayerSessionsCalendar, request)))

    async def get_fraction_member_history(self, server_id: int, fraction_id: int | None = None, nickname: str | None = None,
                                          date_from: datetime.datetime | None = None, date_to: datetime.datetime | None = None,
                                          limit: int = 50, offset: int = 0) -> FractionMemberHistoryResponse:
        request = pb.GetFractionMemberHistoryRequest(server_id=server_id, limit=limit, offset=offset)
        if fraction_id is not None:
            request.fraction_id = fraction_id
        if nickname is not None:
            request.nickname = nickname
        _set_timestamp(request.date_from, date_from)
        _set_timestamp(request.date_to, date_to)
        return FractionMemberHistoryResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetFractionMemberHistory, request)))

    async def get_admins_list(self, server_id: int) -> Any:
        return _json_data(await self._call(self._ensure_stub().GetAdminsList, pb.ServerRequest(server_id=server_id)))

    async def get_manual_checkrp_overrides(self) -> CheckRpManualOverridesListResponse:
        return CheckRpManualOverridesListResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetManualCheckRpOverrides, Empty())))

    async def confirm_rp_name(self, value_type: Literal["firstname", "surname"], value: str) -> None:
        await self._call(self._ensure_stub().ConfirmRpName, pb.RpNameOverrideRequest(value_type=value_type, value=value))

    async def deny_rp_name(self, value_type: Literal["firstname", "surname"], value: str) -> None:
        await self._call(self._ensure_stub().DenyRpName, pb.RpNameOverrideRequest(value_type=value_type, value=value))

    async def reset_rp_name(self, value_type: Literal["firstname", "surname"], value: str) -> None:
        await self._call(self._ensure_stub().ResetRpName, pb.RpNameOverrideRequest(value_type=value_type, value=value))

    async def get_estate_history(self, server_id: int, estate_type: EstateHistoryType | str, estate_id: int, limit: int = 15,
                                 offset: int = 0) -> EstateHistoryResponse:
        request = pb.GetEstateHistoryRequest(server_id=server_id, estate_type=_enum_value(estate_type), estate_id=estate_id, limit=limit, offset=offset)
        return EstateHistoryResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetEstateHistory, request)))

    async def calculate_exp(self, current_lvl: int, target_lvl: int, current_exp: int) -> EXPCalcResponse:
        request = pb.CalculateExpRequest(current_lvl=current_lvl, target_lvl=target_lvl, current_exp=current_exp)
        return EXPCalcResponse.model_validate(_json_data(await self._call(self._ensure_stub().CalculateExp, request)))

    async def get_currency(self, server_id: int) -> CurrencyResponse:
        return CurrencyResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetCurrency, pb.ServerRequest(server_id=server_id))))

    async def get_all_currencies(self) -> list[CurrencyResponse]:
        return [CurrencyResponse.model_validate(entry) for entry in _json_data(await self._call(self._ensure_stub().GetAllCurrencies, Empty())) or []]

    async def get_items(self, item_type: int | None = None, name: str | None = None, skin_id: int | None = None,
                        availability: Literal["tradeable", "rentable"] | None = None, server_id: int | None = None,
                        period: Literal["1d", "1w", "1m", "3m", "6m", "1y"] = "1m", limit: int = 50, offset: int = 0) -> ItemsResponse:
        request = pb.GetItemsRequest(period=period, limit=limit, offset=offset)
        if item_type is not None:
            request.item_type = item_type
        if name is not None:
            request.name = name
        if skin_id is not None:
            request.skin_id = skin_id
        if availability is not None:
            request.availability = availability
        if server_id is not None:
            request.server_id = server_id
        return ItemsResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetItems, request)))

    async def get_vehicles(self, name: str | None = None, limit: int = 6, offset: int = 0) -> ItemsResponse:
        request = pb.GetVehiclesRequest(limit=limit, offset=offset)
        if name is not None:
            request.name = name
        return ItemsResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetVehicles, request)))

    async def get_shops(self, server_id: int | None = None, nickname: str | None = None, item_id: int | None = None,
                        min_price: int | None = None, max_price: int | None = None, type: str | None = None,
                        limit: int = 50, offset: int = 0) -> ShopsResponse:
        request = pb.GetShopsRequest(limit=limit, offset=offset)
        if server_id is not None:
            request.server_id = server_id
        if nickname is not None:
            request.nickname = nickname
        if item_id is not None:
            request.item_id = item_id
        if min_price is not None:
            request.min_price = min_price
        if max_price is not None:
            request.max_price = max_price
        if type is not None:
            request.type = type
        return ShopsResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetShops, request)))

    async def report_client_shop_snapshot(self, payload: dict[str, Any]) -> dict[str, Any]:
        return dict(_json_data(await self._call(self._ensure_stub().ReportClientShopSnapshot, _json_body_request(payload))) or {})

    async def get_client_shop_snapshots(self, params: dict[str, Any]) -> dict[str, Any]:
        return dict(_json_data(await self._call(self._ensure_stub().GetClientShopSnapshots, _json_query_request(params))) or {})

    async def get_shop_deals(self, server_id: int, item_id: int | None = None, mod_level: int | None = None, include_modded: bool = True,
                             min_profit: int = 0, min_discount: int = 0, sort: Literal["profit", "discount", "price"] = "profit",
                             limit: int = 20, offset: int = 0, all_deals: bool = False) -> MarketDealsResponse:
        request = pb.GetShopDealsRequest(server_id=server_id, include_modded=include_modded, min_profit=min_profit, min_discount=min_discount,
                                         sort=sort, limit=limit, offset=offset, all_deals=all_deals)
        if item_id is not None:
            request.item_id = item_id
        if mod_level is not None:
            request.mod_level = mod_level
        return MarketDealsResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetShopDeals, request)))

    async def get_item_market_details(self, item_id: int, server_id: int = 1000,
                                      period: Literal["1d", "1w", "1m", "3m", "6m", "1y"] = "1m") -> ItemMarketStatsResponse:
        request = pb.GetItemMarketDetailsRequest(item_id=item_id, server_id=server_id, period=period)
        return ItemMarketStatsResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetItemMarketDetails, request)))

    async def get_items_history(self, item_id: int | None = None, limit: int = 100, offset: int = 0) -> ItemsHistoryResponse:
        request = pb.GetItemsHistoryRequest(limit=limit, offset=offset)
        if item_id is not None:
            request.item_id = item_id
        return ItemsHistoryResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetItemsHistory, request)))

    async def get_ghetto_rating(self, server_id: int) -> GhettoRatingResponse:
        return GhettoRatingResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetGhettoRating, pb.ServerRequest(server_id=server_id))))

    async def get_ghetto_captures(self, server_id: int) -> GhettoCapturesResponse:
        return GhettoCapturesResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetGhettoCaptures, pb.ServerRequest(server_id=server_id))))

    async def get_family_top(self, server_id: int) -> FamilyTopResponse:
        return FamilyTopResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetFamilyTop, pb.ServerRequest(server_id=server_id))))

    async def get_family_captures(self, server_id: int) -> FamilyCapturesResponse:
        return FamilyCapturesResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetFamilyCaptures, pb.ServerRequest(server_id=server_id))))

    async def hide_profile(self, platform: Literal["vk", "tg", "ds"], user_id: int, server_id: int, nickname: str, is_superadmin: bool = False) -> None:
        await self._call(self._ensure_stub().HideProfile, pb.PrivacyToggleRequest(platform=platform, user_id=user_id, server_id=server_id, nickname=nickname, is_superadmin=is_superadmin))

    async def unhide_profile(self, platform: Literal["vk", "tg", "ds"], user_id: int, server_id: int, nickname: str, is_superadmin: bool = False) -> None:
        await self._call(self._ensure_stub().UnhideProfile, pb.PrivacyToggleRequest(platform=platform, user_id=user_id, server_id=server_id, nickname=nickname, is_superadmin=is_superadmin))

    async def get_hidden_players(self, user_id: int) -> HiddenProfilesListResponse:
        return HiddenProfilesListResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetHiddenPlayers, pb.GetHiddenPlayersRequest(user_id=user_id))))

    async def clear_hidden_profiles(self, user_id: int) -> None:
        await self._call(self._ensure_stub().ClearHiddenProfiles, pb.ClearHiddenProfilesRequest(user_id=user_id))

    async def create_player_comment(self, data: PlayerCommentCreateRequest) -> PlayerCommentResponse:
        return PlayerCommentResponse.model_validate(_json_data(await self._call(self._ensure_stub().CreatePlayerComment, _json_body_request(data.model_dump(mode="json")))))

    async def get_player_comments(self, server_id: int, account_id: int, executor_id: int | None = None, platform: str | None = None,
                                  limit: int = 20, offset: int = 0) -> PlayerCommentsListResponse:
        request = pb.GetPlayerCommentsRequest(server_id=server_id, account_id=account_id, limit=limit, offset=offset)
        if executor_id is not None:
            request.executor_id = executor_id
        if platform is not None:
            request.platform = platform
        return PlayerCommentsListResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetPlayerComments, request)))

    async def get_my_player_comment(self, server_id: int, account_id: int, executor_id: int, platform: str) -> PlayerCommentResponse | None:
        request = pb.GetMyPlayerCommentRequest(server_id=server_id, account_id=account_id, executor_id=executor_id, platform=platform)
        data = _json_data(await self._call(self._ensure_stub().GetMyPlayerComment, request))
        return PlayerCommentResponse.model_validate(data) if data is not None else None

    async def delete_player_comment(self, data: PlayerCommentDeleteRequest) -> None:
        await self._call(self._ensure_stub().DeletePlayerComment, _json_body_request(data.model_dump(mode="json")))

    async def create_comment_complaint(self, data: CommentComplaintCreateRequest) -> CommentComplaintResponse:
        return CommentComplaintResponse.model_validate(_json_data(await self._call(self._ensure_stub().CreateCommentComplaint, _json_body_request(data.model_dump(mode="json")))))

    async def get_pending_comments(self, limit: int = 20, offset: int = 0) -> PendingCommentsResponse:
        return PendingCommentsResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetPendingComments, pb.PagingRequest(limit=limit, offset=offset))))

    async def moderate_comment(self, comment_id: int, action: str, moderator_id: int, moderator_comment: str | None = None) -> PlayerCommentResponse:
        request = pb.ModerateCommentRequest(comment_id=comment_id, action=action, moderator_id=moderator_id)
        if moderator_comment is not None:
            request.reason = moderator_comment
        return PlayerCommentResponse.model_validate(_json_data(await self._call(self._ensure_stub().ModerateComment, request)))

    async def get_all_comments(self, limit: int = 20, offset: int = 0, status: int | None = None) -> AllCommentsResponse:
        request = pb.GetAllCommentsRequest(limit=limit, offset=offset)
        if status is not None:
            request.status = status
        return AllCommentsResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetAllComments, request)))

    async def get_pending_complaints(self, limit: int = 20, offset: int = 0) -> PendingComplaintsResponse:
        return PendingComplaintsResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetPendingComplaints, pb.PagingRequest(limit=limit, offset=offset))))

    async def moderate_complaint(self, complaint_id: int, action: str, moderator_id: int) -> CommentComplaintResponse:
        request = pb.ModerateComplaintRequest(complaint_id=complaint_id, action=action, moderator_id=moderator_id)
        return CommentComplaintResponse.model_validate(_json_data(await self._call(self._ensure_stub().ModerateComplaint, request)))

    async def get_marketplace_listings(self, server_id: int | None = None, source: Literal["external", "user"] | None = None,
                                       q: str | None = None, object_type: str | None = None, deal_type: str | None = None,
                                       category_id: int | None = None, min_price: int | None = None, max_price: int | None = None,
                                       sort: Literal["smart", "new", "price", "price_desc", "bumped"] = "smart",
                                       limit: int = 50, offset: int = 0, author: MarketplaceAuthorContext | None = None) -> MarketplaceListingsResponse:
        request = pb.GetMarketplaceListingsRequest(sort=sort, limit=limit, offset=offset)
        if server_id is not None:
            request.server_id = server_id
        if source is not None:
            request.source = source
        if q is not None:
            request.q = q
        if object_type is not None:
            request.object_type = object_type
        if deal_type is not None:
            request.deal_type = deal_type
        if category_id is not None:
            request.category_id = category_id
        if min_price is not None:
            request.min_price = min_price
        if max_price is not None:
            request.max_price = max_price
        if author is not None:
            request.author.CopyFrom(_struct(author.model_dump(mode="json")))
        return MarketplaceListingsResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetMarketplaceListings, request)))

    async def get_marketplace_listing(self, target_key: str, author: MarketplaceAuthorContext | None = None) -> MarketplaceListingResponse:
        request = pb.GetMarketplaceListingRequest(target_key=target_key)
        if author is not None:
            request.author.CopyFrom(_struct(author.model_dump(mode="json")))
        return MarketplaceListingResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetMarketplaceListing, request)))

    async def get_marketplace_similar(self, server_id: int, q: str | None = None, item_id: int | None = None,
                                      category_id: int | None = None, limit: int = 8) -> MarketplaceSimilarResponse:
        request = pb.GetMarketplaceSimilarRequest(server_id=server_id, limit=limit)
        if q is not None:
            request.q = q
        if item_id is not None:
            request.item_id = item_id
        if category_id is not None:
            request.category_id = category_id
        return MarketplaceSimilarResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetMarketplaceSimilar, request)))

    async def create_marketplace_listing(self, request: MarketplaceUserListingCreateRequest) -> MarketplaceListingResponse:
        data = _json_data(await self._call(self._ensure_stub().CreateMarketplaceListing, _json_body_request(request.model_dump(mode="json"))))
        return MarketplaceListingResponse.model_validate(data)

    async def patch_marketplace_listing(self, listing_id: int, request: MarketplaceUserListingPatchRequest) -> MarketplaceListingResponse:
        grpc_request = pb.ListingBodyRequest(listing_id=listing_id, body=_struct(request.model_dump(mode="json", exclude_unset=True)))
        return MarketplaceListingResponse.model_validate(_json_data(await self._call(self._ensure_stub().PatchMarketplaceListing, grpc_request)))

    async def update_marketplace_listing_status(self, listing_id: int, request: MarketplaceListingActionRequest) -> MarketplaceListingResponse:
        grpc_request = pb.ListingBodyRequest(listing_id=listing_id, body=_struct(request.model_dump(mode="json")))
        return MarketplaceListingResponse.model_validate(_json_data(await self._call(self._ensure_stub().UpdateMarketplaceListingStatus, grpc_request)))

    async def get_my_marketplace_listings(self, author: MarketplaceAuthorContext) -> MarketplaceMyListingsResponse:
        body = MarketplaceAuthorRequest(author=author).model_dump(mode="json")
        return MarketplaceMyListingsResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetMyMarketplaceListings, _json_body_request(body))))

    async def get_marketplace_moderation(self, status: str = "moderation", limit: int = 50, offset: int = 0) -> MarketplaceModerationListResponse:
        request = pb.GetMarketplaceModerationRequest(status=status, limit=limit, offset=offset)
        return MarketplaceModerationListResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetMarketplaceModeration, request)))

    async def moderate_marketplace_listing(self, listing_id: int, request: MarketplaceModerationRequest) -> MarketplaceListingResponse:
        grpc_request = pb.ListingBodyRequest(listing_id=listing_id, body=_struct(request.model_dump(mode="json")))
        return MarketplaceListingResponse.model_validate(_json_data(await self._call(self._ensure_stub().ModerateMarketplaceListing, grpc_request)))

    async def delete_marketplace_listing(self, listing_id: int, request: MarketplaceListingDeleteRequest) -> MarketplaceListingResponse:
        grpc_request = pb.ListingBodyRequest(listing_id=listing_id, body=_struct(request.model_dump(mode="json")))
        return MarketplaceListingResponse.model_validate(_json_data(await self._call(self._ensure_stub().DeleteMarketplaceListing, grpc_request)))

    async def promote_marketplace_listing(self, request: MarketplacePromoteRequest) -> MarketplacePromoteResponse:
        return MarketplacePromoteResponse.model_validate(_json_data(await self._call(self._ensure_stub().PromoteMarketplaceListing, _json_body_request(request.model_dump(mode="json")))))

    async def set_marketplace_favorite(self, request: MarketplaceFavoriteRequest) -> None:
        await self._call(self._ensure_stub().SetMarketplaceFavorite, _json_body_request(request.model_dump(mode="json")))

    async def track_marketplace_view(self, target_key: str) -> None:
        await self._call(self._ensure_stub().TrackMarketplaceView, pb.TrackMarketplaceViewRequest(target_key=target_key))

    async def track_marketplace_contact_click(self, request: MarketplaceContactClickRequest) -> None:
        await self._call(self._ensure_stub().TrackMarketplaceContactClick, _json_body_request(request.model_dump(mode="json")))

    async def get_host_stats(self) -> HostStatsResponse:
        return HostStatsResponse.model_validate(_json_data(await self._call(self._ensure_stub().GetHostStats, Empty())))

    def _ensure_stub(self) -> pb_grpc.VprikolAPIStub:
        if self._stub is not None:
            return self._stub
        options = [("grpc.max_receive_message_length", 32 * 1024 * 1024), ("grpc.max_send_message_length", 1024 * 1024)]
        self._channel = grpc.aio.secure_channel(self.endpoint, grpc.ssl_channel_credentials(), options=options) if self.secure else grpc.aio.insecure_channel(self.endpoint, options=options)
        self._stub = pb_grpc.VprikolAPIStub(self._channel)
        return self._stub

    async def _call(self, method: Any, request: Any) -> Any:
        try:
            return await method(request, metadata=(("vp-api-token", self.token), ("vp-grpc-token", self.grpc_token)), timeout=self.timeout)
        except grpc.aio.AioRpcError as exc:
            raise _grpc_error_to_api_error(exc) from exc


def _message_to_dict(message: Any) -> dict[str, Any]:
    try:
        return MessageToDict(message, preserving_proto_field_name=True, always_print_fields_with_no_presence=True)
    except TypeError:
        return MessageToDict(message, preserving_proto_field_name=True, including_default_value_fields=True)


def _json_data(message: Any) -> Any:
    return _message_to_dict(message).get("data")


def _struct(data: dict[str, Any] | None) -> Struct:
    return ParseDict(data or {}, Struct())


def _json_body_request(data: dict[str, Any] | None) -> Any:
    return pb.JsonBodyRequest(body=_struct(data))


def _json_query_request(data: dict[str, Any] | None) -> Any:
    clean_data = {key: value for key, value in (data or {}).items() if value is not None}
    return pb.JsonQueryRequest(params=_struct(clean_data))


def _grpc_error_to_api_error(exc: grpc.aio.AioRpcError) -> Exception:
    status_code = {
        grpc.StatusCode.INVALID_ARGUMENT: 400,
        grpc.StatusCode.UNAUTHENTICATED: 401,
        grpc.StatusCode.PERMISSION_DENIED: 403,
        grpc.StatusCode.NOT_FOUND: 404,
        grpc.StatusCode.RESOURCE_EXHAUSTED: 429,
        grpc.StatusCode.UNIMPLEMENTED: 501,
        grpc.StatusCode.UNAVAILABLE: 503,
        grpc.StatusCode.DEADLINE_EXCEEDED: 504,
    }.get(exc.code(), 500)
    return create_api_error(status_code, {"detail": exc.details()})


def _set_timestamp(target: Timestamp, value: datetime.datetime | None) -> None:
    if value is not None:
        target.FromDatetime(value)


def _set_missing(data: dict[str, Any], *keys: str) -> None:
    for key in keys:
        data.setdefault(key, None)


def _enum_value(value: Enum | str) -> str:
    return value.value if isinstance(value, Enum) else value


def _normalize_status(data: dict[str, Any]) -> dict[str, Any]:
    _set_missing(data, "server_icon", "server_vk", "server_discord", "main_admin_vk", "deputy_main_admin_vk")
    if "queue_eta" not in data:
        data["queue_eta"] = None
    return data


def _normalize_individual_accounts(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "1": data.get("account_1"),
        "2": data.get("account_2"),
        "3": data.get("account_3"),
        "4": data.get("account_4"),
        "5": data.get("account_5"),
        "6": data.get("account_6"),
    }
