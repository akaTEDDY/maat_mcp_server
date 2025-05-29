import logging
from typing import Dict, Any, Optional
from maat_mcp.api.http import HttpClient
from maat_mcp.config import Config

logger = logging.getLogger(__name__)

class IpLocationApi:
    """IP 기반 위치 정보를 조회하는 클라이언트"""
    
    @staticmethod
    async def get_location_info(client_ip: Optional[str] = None) -> Dict[str, Any]:
        """IP 기반으로 위치 정보를 조회합니다.
        
        Args:
            client_ip (str, optional): 클라이언트 IP 주소
            
        Returns:
            Dict[str, Any]: 위치 정보
            
        Raises:
            Exception: API 호출 실패 시
        """
        try:
            # IP 주소가 없는 경우 현재 IP 사용
            if not client_ip:
                client_ip = (await HttpClient.get("https://api.ipify.org?format=json"))["ip"]

            # IP2Location.io API 호출
            response = await HttpClient.get(f"https://api.ip2location.io/?ip={client_ip}")
            
            if not response:
                # IP2Location API 실패 시 ip-api.com으로 폴백
                location_data = await HttpClient.get(f"http://ip-api.com/json/{client_ip}")
                
                if location_data["status"] != "success":
                    raise Exception("위치 정보를 가져올 수 없습니다.")
                
                return {
                    "latitude": location_data["lat"],
                    "longitude": location_data["lon"],
                    "city": location_data["city"],
                    "country": location_data["country"]
                }
            
            return {
                "latitude": float(response["latitude"]),
                "longitude": float(response["longitude"]),
                "city": response["city_name"],
                "country": response["country_name"]
            }
        except Exception as e:
            logger.error(f"IP 위치 정보 조회 중 에러 발생: {str(e)}")
            raise