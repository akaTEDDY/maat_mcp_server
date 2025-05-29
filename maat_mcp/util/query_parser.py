from typing import Dict, Optional

# 지역 정보 관련 상수
DETAILED_REGIONS = [
    # 광역시/도
    "서울", "부산", "인천", "대구", "대전", "광주", "울산", "세종",
    "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주",
    # 서울시 구
    "강남", "홍대", "이태원", "명동", "동대문", "신촌", "건대", "잠실",
    "송파", "마포", "용산", "종로", "중구", "서초", "강동", "강서"
]

# 기본 검색어
DEFAULT_SEARCH_SUFFIX = " 맛집"

# 기본 음식 종류
DEFAULT_FOOD_TYPES = [
    # 한식
    "한식", "국밥", "삼겹살", "치킨", "족발", "보쌈", "냉면", "비빔밥", 
    "김치찌개", "된장찌개",
    # 중식
    "중식", "짜장면", "짬뽕", "마라탕", "마라샹궈", "훠궈",
    # 일식
    "일식", "초밥", "라멘", "우동", "돈부리", "규동",
    # 양식
    "양식", "파스타", "피자", "햄버거", "스테이크",
    # 기타
    "분식", "떡볶이", "순대", "김밥", "샌드위치", "호프", "펍"
]

def has_region_info(query: str) -> bool:
    """검색어에 지역 정보가 포함되어 있는지 확인합니다.
    
    Args:
        query (str): 검색어
        
    Returns:
        bool: 지역 정보 포함 여부
    """
    return any(region in query for region in DETAILED_REGIONS)

def process_search_query(query: str, context: str = "") -> Dict[str, str]:
    """검색어를 처리하여 지역명과 검색어를 반환합니다.
    
    Args:
        query: 원본 검색어
        context: 이전 대화 맥락 (선택사항)
    
    Returns:
        Dict[str, str]: {
            "location": 지역명,
            "search_query": 검색어,
            "use_current_location": bool
        }
    """
    # 기본 검색어가 아닌 특수한 경우만 정의
    food_types = {
        # 중식 관련
        "중국음식": "중식",
        
        # 일식 관련
        "일본음식": "일식",
        "스시": "초밥",
        
        # 양식 관련
        "서양음식": "양식",
        
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
        "포차": "술집 바"
    }
    
    result = {
        "location": "",
        "search_query": "맛집",
        "use_current_location": False
    }
    
    nearby_keywords = ["내 주변", "근처", "주변", "여기", "현재 위치"]
    search_text = f"{query} {context}" if context else query
    
    for keyword in nearby_keywords:
        if keyword in search_text:
            result["use_current_location"] = True
            break
    
    if context:
        for location in DETAILED_REGIONS:
            if location in context:
                result["location"] = location
                break
        
        for food_type, search_term in food_types.items():
            if food_type in context:
                result["search_query"] = search_term + DEFAULT_SEARCH_SUFFIX
                break
        else:
            # 기본 음식 종류 확인
            for food_type in DEFAULT_FOOD_TYPES:
                if food_type in context:
                    result["search_query"] = food_type + DEFAULT_SEARCH_SUFFIX
                    break
    
    for location in DETAILED_REGIONS:
        if location in query:
            result["location"] = location
            break
    
    for food_type, search_term in food_types.items():
        if food_type in query:
            result["search_query"] = search_term + DEFAULT_SEARCH_SUFFIX
            break
    else:
        # 기본 음식 종류 확인
        for food_type in DEFAULT_FOOD_TYPES:
            if food_type in query:
                result["search_query"] = food_type + DEFAULT_SEARCH_SUFFIX
                break
    
    return result 