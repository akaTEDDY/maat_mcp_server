import logging
from typing import Dict, Any
from maat_mcp.api.http import HttpClient
from maat_mcp.config import Config

logger = logging.getLogger(__name__)

class GoogleMapsApi:
    """Google Maps API 요청을 처리하는 클라이언트 클래스입니다."""
    
    @staticmethod
    async def get_location_by_name(location_name: str) -> Dict[str, Any]:
        """위치 이름으로 좌표 정보를 조회합니다."""
        url = f"{Config.get_google_maps_base_url()}/geocode/json"
        params = {
            "address": location_name,
            "key": Config.get_google_api_key()
        }
        logger.debug(f"위치 정보 조회 요청: {location_name}")
        response = await HttpClient.get(url, params)
        logger.debug(f"위치 정보 조회 응답: {response}")
        return response
    
    @staticmethod
    async def get_restaurants(latitude: float, longitude: float, search_query: str = None) -> Dict[str, Any]:
        """위치 기반으로 맛집 정보를 조회합니다."""
        search_query = search_query or Config.DEFAULT_SEARCH_QUERY
        url = f"{Config.get_google_maps_base_url()}/place/nearbysearch/json"
        params = {
            "location": f"{latitude},{longitude}",
            "radius": Config.SEARCH_RADIUS,
            "type": "restaurant",
            "keyword": search_query,
            "key": Config.get_google_api_key()
        }
        logger.debug(f"맛집 정보 조회 요청: {search_query} ({latitude}, {longitude})")
        response = await HttpClient.get(url, params)
        logger.debug(f"맛집 정보 조회 응답: {response}")
        return response 