from typing import Dict, Any

class VprikolAPIError(Exception):
    def __init__(self, status_code: int, error_data: Dict[str, Any]):
        self.status_code = status_code
        self.detail = error_data.get("detail", error_data)
        self.error_data = error_data
        super().__init__(f"API веселого прикола вернуло ошибку {self.status_code}: {self.detail}")
