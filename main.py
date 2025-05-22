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
)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

load_dotenv()

@mcp.resource("maat://restaurant_results")
async def get_restaurant_results() -> Dict[str, Any]:
    """맛집 검색 결과를 리소스로 제공합니다.
    
    Returns:
        Dict[str, Any]: 검색된 맛집 정보
    """
    try:
        # 위치 정보 가져오기
        location = await get_location_info()
        
        # 맛집 정보 가져오기
        search_query = "맛집"
        restaurants = await get_restaurants(location["latitude"], location["longitude"], search_query)
        
        return {
            "location": location,
            "restaurants": restaurants,
            "query": search_query,
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        logger.error(f"맛집 검색 결과 조회 중 에러 발생: {str(e)}")
        raise

def process_search_query(query: str, context: Optional[str] = None) -> Dict[str, str]:
    """검색어를 처리하여 지역명과 음식 종류를 반환합니다.
    
    Args:
        query: 원본 검색어
        context: 이전 대화 맥락 (선택사항)
    
    Returns:
        Dict[str, str]: {"location": 지역명, "food_type": 음식 종류, "use_current_location": bool}
    """
    # 지역명 목록 (예시)
    locations = [
        "서울", "부산", "인천", "대구", "대전", "광주", "울산", "세종",
        "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주",
        "강남", "홍대", "이태원", "명동", "동대문", "신촌", "건대", "잠실",
        "송파", "마포", "용산", "종로", "중구", "서초", "강동", "강서"
    ]
    
    food_types = {
        # 한식 관련
        "한식": "한식 맛집",
        "한국음식": "한식 맛집",
        "국밥": "국밥 맛집",
        "삼겹살": "삼겹살 맛집",
        "치킨": "치킨 맛집",
        "족발": "족발 맛집",
        "보쌈": "보쌈 맛집",
        "냉면": "냉면 맛집",
        "비빔밥": "비빔밥 맛집",
        "김치찌개": "김치찌개 맛집",
        "된장찌개": "된장찌개 맛집",
        
        # 중식 관련
        "중식": "중식 맛집",
        "중국음식": "중식 맛집",
        "짜장면": "짜장면 맛집",
        "짬뽕": "짬뽕 맛집",
        "마라탕": "마라탕 맛집",
        "마라샹궈": "마라샹궈 맛집",
        "훠궈": "훠궈 맛집",
        
        # 일식 관련
        "일식": "일식 맛집",
        "일본음식": "일식 맛집",
        "초밥": "초밥 맛집",
        "스시": "초밥 맛집",
        "라멘": "라멘 맛집",
        "우동": "우동 맛집",
        "돈부리": "돈부리 맛집",
        "규동": "규동 맛집",
        
        # 양식 관련
        "양식": "양식 맛집",
        "서양음식": "양식 맛집",
        "파스타": "파스타 맛집",
        "피자": "피자 맛집",
        "햄버거": "햄버거 맛집",
        "스테이크": "스테이크 맛집",
        
        # 기타 음식
        "분식": "분식 맛집",
        "떡볶이": "떡볶이 맛집",
        "순대": "순대 맛집",
        "김밥": "김밥 맛집",
        "샌드위치": "샌드위치 맛집",
        
        # 카페/디저트
        "카페": "카페 디저트",
        "커피": "카페 디저트",
        "디저트": "카페 디저트",
        "빵집": "카페 디저트",
        "베이커리": "카페 디저트",
        "아이스크림": "카페 디저트",
        
        # 술집/바
        "술집": "술집 바",
        "바": "술집 바",
        "이자카야": "술집 바",
        "포차": "술집 바",
        "호프": "술집 바",
        "펍": "술집 바"
    }
    
    result = {
        "location": "",
        "food_type": "맛집",
        "use_current_location": False
    }
    
    # "내 주변" 키워드 확인
    nearby_keywords = ["내 주변", "근처", "주변", "여기", "현재 위치"]
    search_text = f"{query} {context}" if context else query
    
    for keyword in nearby_keywords:
        if keyword in search_text:
            result["use_current_location"] = True
            break
    
    # context에서 검색
    if context:
        # 지역명 검색
        for location in locations:
            if location in context:
                result["location"] = location
                break
        
        # 음식 종류 검색
        for food_type, search_term in food_types.items():
            if food_type in context:
                result["food_type"] = search_term
                break
    
    # query에서 검색
    # 지역명 검색
    for location in locations:
        if location in query:
            result["location"] = location
            break
    
    # 음식 종류 검색
    for food_type, search_term in food_types.items():
        if food_type in query:
            result["food_type"] = search_term
            break
    
    return result

@mcp.prompt("맛집 검색")
async def search_restaurants(query: str, context: Optional[str] = None) -> Dict[str, Any]:
    """사용자의 위치 기반으로 맛집을 검색합니다.
    
    Args:
        query: 검색어 (예: '맛집', '한식 맛집', '강남 맛집', '내 주변 맛집')
        context: 이전 대화 맥락 (선택사항)
    
    Returns:
        Dict[str, Any]: 검색된 맛집 정보
    """
    try:
        # 검색어 처리
        search_info = process_search_query(query, context)
        
        # 위치 정보 가져오기
        if search_info["use_current_location"]:
            location = await get_location_info()
        else:
            # 지역명이 있는 경우 해당 지역의 좌표를 가져오기
            if search_info["location"]:
                location = await get_location_by_name(search_info["location"])
            else:
                location = await get_location_info()
        
        # 검색어 조합
        search_query = f"{search_info['location']} {search_info['food_type']}" if search_info['location'] else search_info['food_type']
        
        # 맛집 정보 가져오기
        restaurants = await get_restaurants(location["latitude"], location["longitude"], search_query)
        
        return {
            "location": location,
            "restaurants": restaurants,
            "search_query": search_query
        }
    except Exception as e:
        logger.error(f"맛집 검색 중 에러 발생: {str(e)}")
        raise

@mcp.tool("find_restaurants")
async def find_restaurants(query: str, context: Optional[str] = None) -> Dict[str, Any]:
    """사용자의 위치 기반으로 맛집을 검색하고 결과를 스트리밍합니다.
    
    Args:
        query: 검색어 (예: '맛집', '한식 맛집', '강남 맛집', '내 주변 맛집')
        context: 이전 대화 맥락 (선택사항)
    
    Returns:
        Dict[str, Any]: 검색된 맛집 정보
    """
    try:
        # 검색어 처리
        search_info = process_search_query(query, context)
        
        # 위치 정보 가져오기
        if search_info["use_current_location"]:
            location = await get_location_info()
        else:
            # 지역명이 있는 경우 해당 지역의 좌표를 가져오기
            if search_info["location"]:
                location = await get_location_by_name(search_info["location"])
            else:
                location = await get_location_info()
        
        # 검색어 조합
        search_query = f"{search_info['location']} {search_info['food_type']}" if search_info['location'] else search_info['food_type']
        
        # 맛집 정보 가져오기
        restaurants = await get_restaurants(location["latitude"], location["longitude"], search_query)
        
        return {
            "location": location,
            "restaurants": restaurants,
            "search_query": search_query
        }
    except Exception as e:
        logger.error(f"맛집 검색 중 에러 발생: {str(e)}")
        raise

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
            # 현재 검색어가 기본 검색어인 경우
            if search_query == "맛집":
                raise Exception("주변에 맛집을 찾을 수 없습니다. 지역명이나 음식 종류를 구체적으로 말씀해 주세요. (예: 강남 한식, 홍대 카페)")
            
            # 특정 음식 종류로 검색했는데 결과가 없는 경우
            food_type = search_query.split()[-2] if len(search_query.split()) > 1 else search_query.split()[0]  # "강남 한식 맛집" -> "한식"
            raise Exception(f"주변에 {search_query}를 찾을 수 없습니다. 다른 지역이나 음식 종류를 시도해보시겠어요?")
            
        return restaurants
    except Exception as e:
        logger.error(f"맛집 정보 조회 중 에러 발생: {str(e)}")
        raise

async def get_location_by_name(location_name: str) -> Dict[str, Any]:
    """지역명으로 좌표 정보를 가져옵니다.
    
    Args:
        location_name: 지역명
    
    Returns:
        Dict[str, Any]: 위치 정보 (위도, 경도, 도시, 국가)
    """
    try:
        kakao_api_key = os.getenv("KAKAO_API_KEY")
        if not kakao_api_key:
            raise Exception("KAKAO_API_KEY가 설정되지 않았습니다.")

        headers = {"Authorization": f"KakaoAK {kakao_api_key}"}
        params = {"query": location_name}
        
        response = requests.get(
            "https://dapi.kakao.com/v2/local/search/keyword.json",
            headers=headers,
            params=params,
            timeout=5
        )
        
        data = response.json()
        
        if "documents" not in data or not data["documents"]:
            raise Exception(f"'{location_name}' 지역을 찾을 수 없습니다.")
        
        # 첫 번째 검색 결과 사용
        place = data["documents"][0]
        
        return {
            "latitude": float(place["y"]),
            "longitude": float(place["x"]),
            "city": place["address_name"].split()[0],
            "country": "대한민국"
        }
    except Exception as e:
        logger.error(f"지역 정보 조회 중 에러 발생: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        # 서버 실행
        mcp.run(transport="sse")
    except Exception as e:
        logger.error(f"서버 실행 중 에러 발생: {str(e)}")