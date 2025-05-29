import asyncio
import random
import logging
from typing import Dict, Any, Optional

from maat_mcp.handlers.ip_location_api_handler import get_ip_location_info
from maat_mcp.handlers.google_maps_api_handler import get_restaurants_from_google_maps
from maat_mcp.util import process_search_query, has_region_info

logger = logging.getLogger(__name__)

async def find_restaurants(query: str, context: str = "") -> Dict[str, Any]:
    """맛집 검색의 내부 구현 함수입니다."""
    try:
        parsed_query = process_search_query(query, context)
        location_info = await get_ip_location_info()
        restaurants = await get_restaurants_from_google_maps(
            location_info["latitude"],
            location_info["longitude"],
            parsed_query["search_query"]
        )
        return {
            "location": location_info,
            "restaurants": restaurants,
            "search_query": parsed_query["search_query"],
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        logger.error(f"맛집 검색 중 에러 발생: {str(e)}")
        raise

async def find_random_restaurant(category: Optional[str] = None) -> Dict[str, Any]:
    """랜덤 맛집 추천의 내부 구현 함수입니다."""
    try:
        # 카테고리가 있는 경우와 없는 경우 모두 process_search_query를 통해 처리
        parsed_query = process_search_query(category if category else "맛집")
        
        # 카테고리에 지역 정보가 없는 경우에만 현재 위치 사용
        if not has_region_info(parsed_query["search_query"]):
            location_info = await get_ip_location_info()
            restaurants = await get_restaurants_from_google_maps(
                location_info["latitude"],
                location_info["longitude"],
                parsed_query["search_query"]
            )
        else:
            # 지역 정보가 있는 경우 위치 정보 없이 검색
            location_info = {"latitude": None, "longitude": None}
            restaurants = await get_restaurants_from_google_maps(
                None,
                None,
                parsed_query["search_query"]
            )
        
        if not restaurants:
            raise Exception("추천할 맛집이 없습니다.")
            
        restaurant = random.choice(restaurants)
        return {
            "location": location_info,
            "restaurant": restaurant,
            "search_query": parsed_query["search_query"],
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        logger.error(f"랜덤 맛집 추천 중 에러 발생: {str(e)}")
        raise 