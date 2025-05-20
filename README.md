# MCP Restaurant Finder

FastAPI를 사용한 위치 기반 맛집 검색 서비스입니다.

## 기능

- IP 기반 현재 위치 확인
- 카카오 맵 API를 활용한 주변 맛집 검색
- 거리 기반 정렬
- 맛집 상세 정보 제공

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. 환경 변수 설정:
- `.env` 파일을 생성하고 카카오 API 키를 설정합니다:
```
KAKAO_API_KEY=your_kakao_api_key_here
```

## 실행 방법

```bash
uvicorn main:app --reload
```

## API 엔드포인트

- `GET /`: API 상태 확인
- `GET /location`: 현재 위치 정보 조회
- `GET /restaurants?latitude={lat}&longitude={lon}`: 주변 맛집 검색

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc 