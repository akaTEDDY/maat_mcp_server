from mcp.server.fastmcp import FastMCP
import asyncio
import logging
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import os

# Create MCP server
mcp = FastMCP(
    name="Restaurant Finder",
    instructions="You are a restaurant finder. You can find restaurants around the user's location.",
    capabilities={
        "tools": {
            "listChanged": True,
            "tools": [
                {
                    "name": "find_restaurants",
                    "description": "Find restaurants around the user's location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query (e.g., '맛집', '한식 맛집')"
                            },
                            "context": {
                                "type": "string",
                                "description": "Previous conversation context (optional)"
                            }
                        },
                        "required": ["query"]
                    }
                }
            ]
        },
        "resources": {
            "subscribe": True,
            "listChanged": True
        }
    }
)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

load_dotenv()

async def get_location_info(client_ip: str = None) -> Dict[str, Any]:
    try:
        if client_ip:
            location_response = requests.get(f"http://ip-api.com/json/{client_ip}", timeout=5)
        else:
            location_response = requests.get("http://ip-api.com/json/", timeout=5)
            
        location_data = location_response.json()
        
        if location_data["status"] != "success":
            raise Exception("위치 정보를 가져올 수 없습니다.")
        
        return {
            "latitude": location_data["lat"],
            "longitude": location_data["lon"],
            "city": location_data["city"],
            "country": location_data["country"]
        }
    except requests.exceptions.Timeout:
        raise Exception("위치 정보 서버 응답 시간 초과")
    except requests.exceptions.RequestException as e:
        raise Exception(f"위치 정보 요청 실패: {str(e)}")

async def get_restaurants(latitude: float, longitude: float, search_query: str = "맛집"):
    try:
        if not latitude or not longitude:
            raise Exception("위도/경도 값이 유효하지 않습니다.")
        
        if not (-90 <= latitude <= 90):
            raise Exception("위도는 -90에서 90 사이여야 합니다.")
        if not (-180 <= longitude <= 180):
            raise Exception("경도는 -180에서 180 사이여야 합니다.")

        kakao_api_key = os.getenv("KAKAO_API_KEY")
        if not kakao_api_key:
            raise Exception("KAKAO_API_KEY가 설정되지 않았습니다.")

        headers = {"Authorization": f"KakaoAK {kakao_api_key}"}
        params = {
            "query": search_query,
            "x": str(longitude),
            "y": str(latitude),
            "radius": "1000",
            "sort": "distance"
        }
        
        restaurant_response = requests.get(
            "https://dapi.kakao.com/v2/local/search/keyword.json",
            headers=headers,
            params=params,
            timeout=5
        )
        
        restaurant_data = restaurant_response.json()
        
        if "documents" not in restaurant_data:
            raise Exception("맛집 정보를 가져올 수 없습니다.")
            
        restaurants = []
        for place in restaurant_data["documents"]:
            try:
                restaurant = {
                    "name": place["place_name"],
                    "address": place["address_name"],
                    "category": place["category_name"],
                    "distance": float(place["distance"]),
                    "rating": float(place.get("rating", 0))
                }
                restaurants.append(restaurant)
            except (ValueError, KeyError) as e:
                logger.warning(f"맛집 데이터 처리 중 오류 발생: {str(e)}")
                continue
        
        if not restaurants:
            raise Exception("주변에 맛집을 찾을 수 없습니다.")
            
        return restaurants
    except Exception as e:
        logger.error(f"맛집 정보 조회 중 에러 발생: {str(e)}")
        raise

async def handle_request(request) -> None:
    try:
        # 클라이언트 IP 가져오기
        client_ip = request.headers.get("X-Forwarded-For", request.headers.get("X-Real-IP", request.remote_addr))
        if "," in client_ip:
            client_ip = client_ip.split(",")[0].strip()
        
        logger.info(f"클라이언트 IP: {client_ip}")
        
        # 위치 정보 가져오기
        location = await get_location_info(client_ip)
        await request.send_data({"location": location})
        
        # 맛집 정보 가져오기
        search_query = "맛집"
        if request.context:
            if "한식" in request.context:
                search_query = "한식 맛집"
            elif "중식" in request.context:
                search_query = "중식 맛집"
            elif "일식" in request.context:
                search_query = "일식 맛집"
        
        restaurants = await get_restaurants(location["latitude"], location["longitude"], search_query)
        
        # 맛집 정보를 스트리밍
        for restaurant in restaurants:
            await request.send_data({"restaurant": restaurant})
            await asyncio.sleep(0.5)
            
    except Exception as e:
        logger.error(f"요청 처리 중 에러 발생: {str(e)}")
        await request.send_error(str(e))

if __name__ == "__main__":
    mcp.run(transport="sse")