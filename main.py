import logging
from mcp.server.fastmcp import FastMCP
from maat_mcp.handlers.service_implementation import (
    find_restaurants,
    find_random_restaurant
)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# MCP 서버 생성
mcp = FastMCP(
    name="Restaurant Finder",
    instructions="You are a restaurant finder. You can find restaurants around the user's location and recommend random restaurants based on their preferences."
)

# 리소스 등록
@mcp.resource("maat://restaurant_results")
async def get_restaurant_results_resource():
    """맛집 검색 결과를 리소스로 제공합니다."""
    return await find_restaurants("맛집")  # 기본 검색어 명시

# 프롬프트 등록
@mcp.prompt("맛집 검색")
async def search_restaurants_prompt(query: str, context: str = None):
    """맛집을 검색합니다.
    
    Args:
        query (str): 검색어 (예: '맛집', '한식 맛집', '강남 맛집', '내 주변 맛집')
        context (str, optional): 이전 대화 내용
    
    Returns:
        Dict[str, Any]: 검색된 맛집 정보
    """
    return await find_restaurants(query, context)

# 도구 등록
@mcp.tool("find_restaurants")
async def find_restaurants_tool(query: str, context: str = ""):
    """맛집을 검색합니다.
    
    Args:
        query (str): 검색어 (예: '맛집', '한식 맛집', '강남 맛집', '내 주변 맛집')
        context (str, optional): 이전 대화 내용
    
    Returns:
        Dict[str, Any]: 검색된 맛집 정보
    """
    return await find_restaurants(query, context)

@mcp.tool("recommend_random_restaurant")
async def recommend_random_restaurant_tool(category: str = None):
    """현재 위치 기반으로 랜덤 맛집을 추천합니다.
    
    Args:
        category (str, optional): 음식 종류 (예: '한식', '중식', '일식', '양식')
    
    Returns:
        Dict[str, Any]: 추천된 맛집 정보
    """
    return await find_random_restaurant(category)

if __name__ == "__main__":
    try:
        mcp.run(transport="sse")
    except Exception as e:
        logging.error(f"서버 실행 중 에러 발생: {str(e)}")
        raise