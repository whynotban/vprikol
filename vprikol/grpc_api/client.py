import datetime
import os
from __future__ import annotations
from enum import Enum
from typing import Any, Literal
from google.protobuf.json_format import MessageToDict
from google.protobuf.timestamp_pb2 import Timestamp

try:
    import grpc
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("Для gRPC клиента установите пакет с extra-зависимостями: vprikol[grpc].") from exc

from ._generated import vprikol_pb2 as pb
from ._generated import vprikol_pb2_grpc as pb_grpc
from ..api import create_api_error
from ..models import (AllServersStatusResponse, EstateResponse, EstateType, FindPlayerResponse, InterviewsResponse, LeadersResponse, MapResponse,
                      MapZonesResponse, MembersResponse, MoneyHistoryEntry, NicknameHistoryEntry, OnlineResponse, PlayersResponse, PunishHistoryResponse,
                      RatingResponse, RatingType, RequestLogResponse, RequestStatsResponse, ServerStatusResponse, TokenResponse)


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
                           date_to: datetime.datetime | None = None, limit: int = 100, offset: int = 0) -> PunishHistoryResponse:
        request = pb.GetPunishesRequest(server_id=server_id, limit=limit, offset=offset)
        if player_nickname:
            request.player_nickname = player_nickname
        if admin_nickname:
            request.admin_nickname = admin_nickname
        if punish_type:
            request.punish_type = punish_type
        _set_timestamp(request.date_from, date_from)
        _set_timestamp(request.date_to, date_to)
        data = _message_to_dict(await self._call(self._ensure_stub().GetPunishes, request))
        for entry in data.setdefault("data", []):
            entry.setdefault("expires_at", None)
        return PunishHistoryResponse.model_validate(data)

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
