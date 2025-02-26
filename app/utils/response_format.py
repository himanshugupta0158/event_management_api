from typing import Any, Dict

from pydantic import BaseModel


class APIResponse(BaseModel):
    message: str = ""
    data: Dict[str, Any] | list[Dict[str, Any]] | Any = {}
