import os
from typing import Dict, Any

class Config:
    """환경 변수 설정을 관리하는 클래스입니다."""
    
    # API 키
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
    IPLOCATION_API_KEY = os.getenv("IPLOCATION_API_KEY", "")
    
    # 기본 설정
    DEFAULT_SEARCH_QUERY = "맛집"
    MAX_CACHE_SIZE = 1000
    REQUEST_TIMEOUT = 10
    
    # 평점 기준
    RATING_THRESHOLDS = [4.5, 4.0, 3.8]
    
    # API 기본 URL
    GOOGLE_MAPS_BASE_URL = "https://maps.googleapis.com/maps/api"
    IPLOCATION_BASE_URL = "https://api.ip2location.io/?ip="

    # 검색 설정
    SEARCH_RADIUS = "1000"  # 미터 단위
    
    # HTTP 설정
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # 초
    
    # 캐시 설정
    CACHE_TTL = 3600  # 초 (1시간)
    
    @classmethod
    def get_google_maps_base_url(cls) -> str:
        """Google Maps API 기본 URL을 반환합니다."""
        return cls.GOOGLE_MAPS_BASE_URL
    
    @classmethod
    def get_iplocation_base_url(cls) -> str:
        """IPLocation API 기본 URL을 반환합니다."""
        return cls.IPLOCATION_BASE_URL
    
    @classmethod
    def get_google_api_key(cls) -> str:
        """Google Maps API 키를 반환합니다."""
        if not cls.GOOGLE_MAPS_API_KEY:
            raise ValueError("Google Maps API 키가 설정되지 않았습니다.")
        return cls.GOOGLE_MAPS_API_KEY