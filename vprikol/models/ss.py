from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .base import SSFont


class SSTextAlign(str, Enum):
    LEFT = 'left'
    CENTER = 'center'
    RIGHT = 'right'


class SSOutputFormat(str, Enum):
    AUTO = 'auto'
    JPEG = 'jpeg'
    PNG = 'png'


class SSIssueLevel(str, Enum):
    ERROR = 'error'
    WARNING = 'warning'


class SSLineIssue(BaseModel):
    level: SSIssueLevel
    code: str
    message: str


class SSLineReport(BaseModel):
    index: int
    source: str
    accepted: bool
    normalized: Optional[str] = None
    command: Optional[str] = None
    nickname: Optional[str] = None
    issues: List[SSLineIssue] = Field(default_factory=list)


class SSValidateResponse(BaseModel):
    lines: List[SSLineReport]
    accepted_lines: List[str]
    errors_count: int
    warnings_count: int


FONT_LABELS: Dict[SSFont, str] = {
    SSFont.ARIAL_BOLD: 'Arial',
    SSFont.ARIAL_BOLD_ITALIC: 'Arial (курсив)',
    SSFont.BITTER_BOLD: 'Bitter',
    SSFont.BITTER_BOLD_ITALIC: 'Bitter (курсив)',
    SSFont.MONTSERRAT_BOLD: 'Montserrat',
    SSFont.MONTSERRAT_BOLD_ITALIC: 'Montserrat (курсив)',
    SSFont.NUNITO_BOLD: 'Nunito',
    SSFont.NUNITO_BOLD_ITALIC: 'Nunito (курсив)',
    SSFont.OPENSANS_BOLD: 'Open Sans',
    SSFont.OPENSANS_BOLD_ITALIC: 'Open Sans (курсив)',
    SSFont.UBUNTU_BOLD: 'Ubuntu',
    SSFont.UBUNTU_BOLD_ITALIC: 'Ubuntu (курсив)',
    SSFont.ROBOTO_BOLD: 'Roboto',
    SSFont.ROBOTO_BOLD_ITALIC: 'Roboto (курсив)',
    SSFont.SF_PRO_DISPLAY_BOLD: 'SF Pro Display',
}

FONTS_ORDER: List[SSFont] = list(FONT_LABELS)

DEFAULT_COMMAND_COLORS: Dict[str, str] = {'/me': '#F58BF5', '/do': '#3182b4', '/todo': '#ffffff', '/say': '#ffffff',
                                          '/phone': '#32a852', '/d': '#2f7bf5', '/m': '#ffe62b', '/r': '#2f994c',
                                          '/f': '#2f994c', '/s': '#ecdd88'}

COMMAND_LABELS: Dict[str, str] = {'/me': 'Действия', '/do': 'Окружение', '/todo': 'Речь с действием', '/say': 'Речь',
                                  '/phone': 'Телефон', '/d': 'Departament', '/m': 'Мегафон', '/r': 'Рация',
                                  '/f': 'Семья', '/s': 'Крик'}


class SSSettings(BaseModel):
    font: SSFont = SSFont.ARIAL_BOLD
    text_top: bool = True
    text_size: float = 0.95
    line_spacing: float = 1.0
    align: SSTextAlign = SSTextAlign.LEFT
    offset_x: Optional[int] = None
    offset_y: Optional[int] = None
    wrap: bool = True
    outline_width: int = 1
    outline_color: str = '#000000'
    shadow_offset: int = 0
    shadow_color: str = '#000000'
    shadow_opacity: float = 0.6
    backdrop_blur: int = 0
    backdrop_opacity: float = 0.0
    backdrop_color: str = '#000000'
    timestamps: bool = False
    timestamp_color: str = '#ffffff'
    output_format: SSOutputFormat = SSOutputFormat.AUTO
    quality: int = 95
    commands_colors: Dict[str, str] = Field(default_factory=dict)

    @classmethod
    def from_storage(cls, raw: Optional[Dict[str, Any]]) -> 'SSSettings':
        data = dict(raw or {})

        legacy_font = data.pop('font', None)
        if isinstance(legacy_font, int):
            data['font'] = FONTS_ORDER[legacy_font] if 0 <= legacy_font < len(FONTS_ORDER) else SSFont.ARIAL_BOLD
        elif legacy_font is not None:
            data['font'] = legacy_font

        if 'position' in data:
            data['text_top'] = data.pop('position') == 0
        if 'ss_colors' in data:
            colors = data.pop('ss_colors') or {}
            data['commands_colors'] = {key if key.startswith('/') else f'/{key}': value for key, value in colors.items()}

        known = set(cls.model_fields)
        return cls.model_validate({key: value for key, value in data.items() if key in known and value is not None})

    def to_storage(self) -> Dict[str, Any]:
        return self.model_dump(mode='json')

    def to_api_kwargs(self) -> Dict[str, Any]:
        return self.model_dump(mode='python', exclude={'commands_colors'}) | {'commands_colors': self.commands_colors or None}

    def color_for(self, command: str) -> str:
        return self.commands_colors.get(command, DEFAULT_COMMAND_COLORS[command])

    def reset(self, field_name: str) -> None:
        default = type(self).model_fields[field_name].get_default(call_default_factory=True)
        setattr(self, field_name, default)
