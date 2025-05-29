import logging
from typing import Dict, Any, List
from maat_mcp.api.google_maps_api import GoogleMapsApi
from maat_mcp.config import Config

logger = logging.getLogger(__name__)

async def get_restaurants_from_google_maps(latitude: float, longitude: float, search_query: str = None) -> List[Dict[str, Any]]:
    """Google Maps API를 통해 위치 기반으로 맛집 정보를 조회합니다.
    
    Args:
        latitude (float): 위도
        longitude (float): 경도
        search_query (str, optional): 검색어
        
    Returns:
        List[Dict[str, Any]]: 맛집 정보 목록
        
    Raises:
        Exception: API 호출 실패 시
    """
    try:
        response = await GoogleMapsApi.get_restaurants(latitude, longitude, search_query)
        if response["status"] != "OK":
            raise Exception(f"맛집 정보 조회 실패: {response['status']}")
            
        restaurants = []
        for place in response["results"]:
            restaurants.append({
                "name": place["name"],
                "address": place["vicinity"],
                "rating": place.get("rating", 0),
                "total_ratings": place.get("user_ratings_total", 0),
                "types": place.get("types", []),
                "place_id": place["place_id"]
            })
        
        # 평점 기준을 순차적으로 하향 조정
        filtered_restaurants = []
        
        for threshold in Config.RATING_THRESHOLDS:
            filtered_restaurants = [r for r in restaurants if r["rating"] >= threshold]
            if filtered_restaurants:
                logger.info(f"평점 {threshold} 이상의 맛집 {len(filtered_restaurants)}개 발견")
                break
        
        if not filtered_restaurants:
            if search_query == Config.DEFAULT_SEARCH_QUERY:
                raise Exception("주변에 맛집을 찾을 수 없습니다. 지역명이나 음식 종류를 구체적으로 말씀해 주세요. (예: 강남 한식, 홍대 카페)")
            
            food_type = search_query.split()[-2] if len(search_query.split()) > 1 else search_query.split()[0]
            raise Exception(f"주변에 {search_query}를 찾을 수 없습니다. 다른 지역이나 음식 종류를 시도해보시겠어요?")
        
        return filtered_restaurants
    except Exception as e:
        logger.error(f"맛집 정보 조회 중 에러 발생: {str(e)}")
        raise 