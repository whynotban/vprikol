from typing import Optional, List
from pydantic import BaseModel, Field


class HostStatsLoadAvg(BaseModel):
    one: float = Field(alias="1")
    five: float = Field(alias="5")
    fifteen: float = Field(alias="15")

    model_config = {"populate_by_name": True}


class HostStatsCPU(BaseModel):
    model: str
    cores_physical: int
    cores_logical: int
    usage_percent_total: float
    usage_percent_per_core: List[float]
    freq_current_mhz: Optional[float] = None
    freq_min_mhz: Optional[float] = None
    freq_max_mhz: Optional[float] = None
    temperature_package_c: Optional[float] = None
    temperature_per_core_c: List[float] = []


class HostStatsMemory(BaseModel):
    total_bytes: int
    used_bytes: int
    available_bytes: int
    free_bytes: int
    cached_bytes: int = 0
    buffers_bytes: int = 0
    percent: float
    swap_total_bytes: int
    swap_used_bytes: int
    swap_percent: float


class HostStatsFilesystem(BaseModel):
    device: str
    mountpoint: str
    fstype: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
    percent: float


class HostStatsDiskIO(BaseModel):
    name: str
    model: str = ""
    size_bytes: int = 0
    read_bytes_per_sec: int
    write_bytes_per_sec: int
    read_iops: float
    write_iops: float


class HostStatsSMART(BaseModel):
    name: str
    model: str = ""
    serial: str = ""
    size_bytes: int = 0
    health_ok: Optional[bool] = None
    temperature_c: Optional[float] = None
    power_on_hours: Optional[int] = None
    power_cycles: Optional[int] = None
    percentage_used: Optional[int] = None
    data_units_read: Optional[int] = None
    data_units_written: Optional[int] = None
    unsafe_shutdowns: Optional[int] = None
    media_errors: Optional[int] = None
    reallocated_sectors: Optional[int] = None
    wear_leveling_count: Optional[int] = None


class HostStatsDisks(BaseModel):
    filesystems: List[HostStatsFilesystem]
    io: List[HostStatsDiskIO]
    smart: List[HostStatsSMART]


class HostStatsNetIface(BaseModel):
    name: str
    is_up: bool
    speed_mbps: Optional[int] = None
    rx_bytes_per_sec: int
    tx_bytes_per_sec: int
    rx_packets_per_sec: float
    tx_packets_per_sec: float
    rx_total_bytes: int
    tx_total_bytes: int
    rx_errors: int
    tx_errors: int
    rx_dropped: int
    tx_dropped: int


class HostStatsSensor(BaseModel):
    chip: str
    label: str
    kind: str
    value: float
    unit: str


class HostStatsResponse(BaseModel):
    uptime_seconds: int
    load_avg: HostStatsLoadAvg
    cpu: HostStatsCPU
    memory: HostStatsMemory
    disks: HostStatsDisks
    network: List[HostStatsNetIface]
    sensors: List[HostStatsSensor]
    collected_at: float
