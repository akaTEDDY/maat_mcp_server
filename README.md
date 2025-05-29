# MAAT MCP Restaurant Finder

맛집 검색 및 추천 서비스를 제공하는 remote MCP(Model Context Protocol) server입니다.

## 주요 기능

- **맛집 검색**: 사용자의 위치 기반으로 주변 맛집을 검색합니다.
- **랜덤 추천**: 현재 위치 기반으로 랜덤 맛집을 추천합니다.
- **카테고리별 검색**: 한식, 중식, 일식, 양식 등 카테고리별 맛집 검색을 지원합니다.

## 기술 스택

- Python 3.8+
- FastMCP 0.4.1+
- Google Maps API

## 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/akateddy/maat_mcp_server.git
cd maat_mcp_server
```

2. 의존성 설치
```bash
pip install -r requirements.txt
```

3. 환경 변수 설정
`.env` 파일을 생성하고 다음 변수들을 설정합니다:
```
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
IPLOCATION_API_KEY=your_iplocation_api_key
```

## 실행 방법

```bash
python main.py
```

## API 엔드포인트

### 리소스
- `maat://restaurant_results`: 맛집 검색 결과 리소스

### 프롬프트
- `맛집 검색`: 맛집 검색 프롬프트

### 도구
- `find_restaurants`: 맛집 검색 도구
- `recommend_random_restaurant`: 랜덤 맛집 추천 도구

## 프로젝트 구조

```
maat_mcp_server/
├── main.py              # 메인 애플리케이션
├── requirements.txt     # 의존성 목록
└── maat_mcp/           # 핵심 패키지
    ├── api/            # API 클라이언트
    ├── handlers/       # 비즈니스 로직
    └── util/           # 유틸리티 함수
```

## 라이선스

MIT License 

## claude_desktop_config 설정 방법
```
"restaurants_finder": {
	"command": "npx",
	"args": [
		"mcp-remote",
	"http://localhost:8000/sse"
	],
  	"env": {
		"GOOGLE_MAPS_API_KEY": "{YOUR_GOOGLE_MAPS_API_KEY}"
  	}
}
```
