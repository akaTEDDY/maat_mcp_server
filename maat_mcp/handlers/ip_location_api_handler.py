import logging
from typing import Dict, Any, Optional
from maat_mcp.api.ip_location_api import IpLocationApi

logger = logging.getLogger(__name__)

async def get_ip_location_info(client_ip: Optional[str] = None) -> Dict[str, Any]:
    """IP 기반으로 위치 정보를 조회합니다.
    
    Args:
        client_ip (str, optional): 클라이언트 IP 주소
        
    Returns:
        Dict[str, Any]: 위치 정보 (위도, 경도, 도시, 국가)
        
    Raises:
        Exception: API 호출 실패 시
    """ 
    try:
        response = await IpLocationApi.get_location_info(client_ip)
        
        # 응답이 필요한 필드를 포함하는지 확인
        required_fields = ["latitude", "longitude", "city", "country"]
        if not all(field in response for field in required_fields):
            raise Exception("위치 정보가 올바르지 않습니다.")
            
        return response
    except Exception as e:
        logger.error(f"IP 위치 정보 조회 중 에러 발생: {str(e)}")
        raise 