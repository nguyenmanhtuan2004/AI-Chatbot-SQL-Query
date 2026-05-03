from typing import Any
from decimal import Decimal
from datetime import date, datetime

def serialize_to_json(obj: Any) -> Any:
    """Chuyển Decimal / date / datetime sang kiểu JSON-safe."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
