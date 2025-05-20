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

async def get_location_info() -> Dict[str, Any]:
    try:
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

async def get_restaurants(latitude: float, longitude: float) -> List[Restaurant]:
    try:
        kakao_api_key = os.getenv("KAKAO_API_KEY")
        if not kakao_api_key:
            raise HTTPException(status_code=500, detail="KAKAO_API_KEY가 설정되지 않았습니다.")

        headers = {"Authorization": f"KakaoAK {kakao_api_key}"}
        params = {
            "query": "맛집",
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
            restaurant = Restaurant(
                name=place["place_name"],
                address=place["address_name"],
                category=place["category_name"],
                distance=float(place["distance"]),
                rating=float(place.get("rating", 0))
            )
            restaurants.append(restaurant)
        
        return restaurants
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="카카오 API 응답 시간 초과")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"카카오 API 요청 실패: {str(e)}")

@app.get("/")
async def root():
    return {"message": "MCP Restaurant Finder API"}

@app.get("/sse")
async def sse_endpoint(query: str = "주변 맛집 추천해줘"):
    async def event_generator():
        try:
            # 위치 정보 가져오기
            location = await get_location_info()
            yield f"data: {json.dumps({'type': 'location', 'data': location})}\n\n"
            
            # 맛집 정보 가져오기
            restaurants = await get_restaurants(location["latitude"], location["longitude"])
            
            # 맛집 정보를 하나씩 스트리밍
            for restaurant in restaurants:
                yield f"data: {json.dumps({'type': 'restaurant', 'data': restaurant.to_dict()})}\n\n"
                await asyncio.sleep(0.5)  # 각 맛집 정보 사이에 0.5초 딜레이
            
            # 스트리밍 완료 메시지
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