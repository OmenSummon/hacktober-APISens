import json
from typing import Any, Dict, List
from app.models.traffic import TrafficBatch, TrafficRequest


class TrafficService:
    """
    Manages in-memory ingestion and normalization of observed API traffic requests.
    """

    def __init__(self):
        self._traffic_store: List[TrafficRequest] = []

    def ingest(self, requests: List[TrafficRequest]) -> int:
        """Adds a list of requests to the traffic store."""
        self._traffic_store.extend(requests)
        return len(requests)

    def parse_from_json(self, raw_content: str | bytes | Dict[str, Any]) -> List[TrafficRequest]:
        """Parses traffic payload from JSON string, bytes, or dictionary."""
        if isinstance(raw_content, (bytes, str)):
            text = raw_content.decode("utf-8") if isinstance(raw_content, bytes) else raw_content
            data = json.loads(text)
        elif isinstance(raw_content, dict):
            data = raw_content
        elif isinstance(raw_content, list):
            data = {"requests": raw_content}
        else:
            raise ValueError("Unsupported traffic data format")

        if isinstance(data, dict) and "requests" in data:
            batch = TrafficBatch(**data)
            return batch.requests
        elif isinstance(data, list):
            return [TrafficRequest(**item) for item in data]
        else:
            raise ValueError("Expected JSON object with 'requests' array or raw array of requests")

    def get_all(self) -> List[TrafficRequest]:
        return list(self._traffic_store)

    def clear(self) -> None:
        self._traffic_store.clear()


traffic_service = TrafficService()
