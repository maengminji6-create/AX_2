import os
from pathlib import Path
import requests
import streamlit as st
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv

# Streamlit 기본 설정
st.set_page_config(page_title="카카오 REST API 여행 지도", page_icon="🗺️", layout="wide")

# .env 자동 탐색 및 로드
current_file_path = Path(__file__).resolve()
for parent in [current_file_path.parent] + list(current_file_path.parents):
    candidate = parent / ".env"
    if candidate.exists() and candidate.is_file():
        load_dotenv(dotenv_path=candidate, override=True)
        break

# REST API 키 가져오기
KAKAO_REST_KEY = os.getenv("KAKAO_API_KEY") or os.getenv("KAKAO_MAP_API_KEY")

if not KAKAO_REST_KEY:
    st.error("🚨 `.env` 파일에서 카카오 키를 찾을 수 없습니다.")
    st.stop()

st.title("🗺️ 카카오 로컬 검색 & 여행 지도")

# 카카오 REST API 키워드 장소 검색 함수
def search_kakao_place(keyword, api_key):
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": keyword, "size": 5}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("documents", [])
    else:
        st.error(f"API 요청 실패 (코드 {response.status_code}): {response.text}")
        return []

# 사이드바 검색창
st.sidebar.header("🔍 카카오 장소 검색")
query = st.sidebar.text_input("검색할 장소나 주소를 입력하세요", value="경복궁")
search_btn = st.sidebar.button("검색")

# 세션 상태에 검색 결과 저장
if "place_results" not in st.session_state or search_btn:
    if query:
        st.session_state.place_results = search_kakao_place(query, KAKAO_REST_KEY)

# 기본 중심 좌표 (서울 시청)
center_lat, center_lng = 37.5665, 126.9780

# 지도 생성
if st.session_state.get("place_results"):
    first_place = st.session_state.place_results[0]
    center_lat = float(first_place["y"])
    center_lng = float(first_place["x"])

m = folium.Map(location=[center_lat, center_lng], zoom_start=14)

# 검색된 장소 마커 찍기
results = st.session_state.get("place_results", [])
if results:
    for idx, place in enumerate(results):
        lat = float(place["y"])
        lng = float(place["x"])
        name = place.get("place_name", "장소")
        address = place.get("road_address_name") or place.get("address_name")
        
        # 마커 및 팝업 추가
        popup_html = f"<b>{name}</b><br><small>{address}</small>"
        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=name,
            icon=folium.Icon(color="red" if idx == 0 else "blue", icon="info-sign")
        ).add_to(m)

# 지도 렌더링
st_folium(m, width=900, height=520)

# 검색 결과 리스트 출력
if results:
    st.subheader(f"📍 '{query}' 검색 결과")
    for place in results:
        addr = place.get("road_address_name") or place.get("address_name")
        st.markdown(f"- **{place['place_name']}** : {addr} (위도: `{place['y']}`, 경도: `{place['x']}`)")