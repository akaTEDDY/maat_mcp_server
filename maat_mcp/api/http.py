import logging
import aiohttp
from typing import Dict, Any
from maat_mcp.config import Config

logger = logging.getLogger(__name__)

class HttpClient:
    """HTTP 요청을 처리하는 클라이언트 클래스"""
    
    @staticmethod
    async def get(url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """GET 요청을 수행합니다.
        
        Args:
            url (str): 요청 URL
            params (Dict[str, Any], optional): 쿼리 파라미터
            
        Returns:
            Dict[str, Any]: 응답 데이터
            
        Raises:
            Exception: 요청 실패 시
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    timeout=Config.REQUEST_TIMEOUT
                ) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP 요청 실패: {response.status}")
                    return await response.json()
        except Exception as e:
            logger.error(f"HTTP 요청 중 에러 발생: {str(e)}")
            raise 