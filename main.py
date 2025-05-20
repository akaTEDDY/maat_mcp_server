from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import requests
import os
import json
import asyncio
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="MCP Restaurant Finder")

# CORS 설정
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

class Restaurant(BaseModel):
    name: str
    address: str
    category: str
    distance: float
    rating: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "address": self.address,
            "category": self.category,
            "distance": self.distance,
            "rating": self.rating
        }

class MCPRequest(BaseModel):
    query: str
    location: Optional[Dict[str, float]] = None
    context: Optional[str] = None  # LLM 대화 컨텍스트 추가

async def get_location_info(client_ip: str = None) -> Dict[str, Any]:
    try:
        # 클라이언트 IP가 있으면 그 IP로 위치 확인
        if client_ip:
            location_response = requests.get(f"http://ip-api.com/json/{client_ip}", timeout=5)
        else:
            location_response = requests.get("http://ip-api.com/json/", timeout=5)
            
        location_data = location_response.json()
        
        if location_data["status"] != "success":
            raise HTTPException(status_code=400, detail="위치 정보를 가져올 수 없습니다.")
        
        return {
            "latitude": location_data["lat"],
            "longitude": location_data["lon"],
            "city": location_data["city"],
            "country": location_data["country"]
        }
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="위치 정보 서버 응답 시간 초과")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"위치 정보 요청 실패: {str(e)}")

async def get_restaurants(latitude: float, longitude: float, search_query: str = "맛집") -> List[Restaurant]:
    try:
        # 위도/경도 값 검증
        if not latitude or not longitude:
            raise HTTPException(status_code=400, detail="위도/경도 값이 유효하지 않습니다.")
        
        # 위도/경도 범위 검증
        if not (-90 <= latitude <= 90):
            raise HTTPException(status_code=400, detail="위도는 -90에서 90 사이여야 합니다.")
        if not (-180 <= longitude <= 180):
            raise HTTPException(status_code=400, detail="경도는 -180에서 180 사이여야 합니다.")

        kakao_api_key = os.getenv("KAKAO_API_KEY")
        if not kakao_api_key:
            raise HTTPException(status_code=500, detail="KAKAO_API_KEY가 설정되지 않았습니다.")

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
            raise HTTPException(status_code=400, detail="맛집 정보를 가져올 수 없습니다.")
            
        restaurants = []
        for place in restaurant_data["documents"]:
            try:
                restaurant = Restaurant(
                    name=place["place_name"],
                    address=place["address_name"],
                    category=place["category_name"],
                    distance=float(place["distance"]),
                    rating=float(place.get("rating", 0))
                )
                restaurants.append(restaurant)
            except (ValueError, KeyError) as e:
                logger.warning(f"맛집 데이터 처리 중 오류 발생: {str(e)}")
                continue
        
        if not restaurants:
            raise HTTPException(status_code=404, detail="주변에 맛집을 찾을 수 없습니다.")
            
        return restaurants
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="카카오 API 응답 시간 초과")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"카카오 API 요청 실패: {str(e)}")
    except Exception as e:
        logger.error(f"맛집 정보 조회 중 에러 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"맛집 정보 조회 실패: {str(e)}")

@app.get("/")
async def root():
    return {"message": "MCP Restaurant Finder API"}

@app.get("/sse")
async def sse_endpoint(request: Request, query: str = "주변 맛집 추천해줘", context: Optional[str] = None):
    async def event_generator():
        try:
            # 클라이언트 IP 가져오기 (X-Forwarded-For 또는 X-Real-IP 헤더 확인)
            client_ip = request.headers.get("X-Forwarded-For", request.headers.get("X-Real-IP", request.client.host))
            if "," in client_ip:
                client_ip = client_ip.split(",")[0].strip()
            
            logger.info(f"클라이언트 IP: {client_ip}")
            logger.info(f"대화 컨텍스트: {context}")
            
            # 위치 정보 가져오기
            location = await get_location_info(client_ip)
            yield f"data: {json.dumps({'type': 'location', 'data': location})}\n\n"
            
            # 맛집 정보 가져오기 (컨텍스트에 따라 검색어 수정)
            search_query = "맛집"
            if context:
                # 컨텍스트에서 음식 종류나 선호도를 추출하여 검색어 수정
                if "한식" in context:
                    search_query = "한식 맛집"
                elif "중식" in context:
                    search_query = "중식 맛집"
                elif "일식" in context:
                    search_query = "일식 맛집"
                # 추가적인 컨텍스트 기반 검색어 수정 가능
            
            restaurants = await get_restaurants(location["latitude"], location["longitude"], search_query)
            
            # 맛집 정보를 하나씩 스트리밍
            for restaurant in restaurants:
                yield f"data: {json.dumps({'type': 'restaurant', 'data': restaurant.to_dict()})}\n\n"
                await asyncio.sleep(0.5)
            
            yield f"data: {json.dumps({'type': 'complete', 'message': '스트리밍이 완료되었습니다.'})}\n\n"
            
        except Exception as e:
            logger.error(f"SSE 에러: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        timeout_keep_alive=75  # keep-alive 타임아웃 증가
    ) 