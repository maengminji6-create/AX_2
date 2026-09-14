import os
from pathlib import Path
import requests
import streamlit as st
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv

# 1. 기본 레이아웃
st.set_page_config(page_title="스마트 여행 허브", page_icon="🌿", layout="wide")

# 2. 로컬 .env 탐색
current_file = Path(__file__).resolve()
for p in [current_file.parent] + list(current_file.parents):
    env_target = p / ".env"
    if env_target.exists():
        load_dotenv(env_target, override=True)
        break

# 3. 키 추출 함수 (Secrets -> env -> 빈값)
def find_key(key_name):
    # Streamlit Cloud 환경
    try:
        if key_name in st.secrets:
            return str(st.secrets[key_name]).strip()
    except Exception:
        pass
    # 로컬 .env 환경
    return os.getenv(key_name, "").strip()

KAKAO_KEY = find_key("KAKAO_API_KEY")
WEATHER_KEY = find_key("OPENWEATHER_API_KEY")

# 4. 부드러운 UI 스타일
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    * { font-family: 'Pretendard', sans-serif; }
    .stApp { background-color: #FAF8F5; }
    .hero-box {
        background: linear-gradient(135deg, #FFFDF0 0%, #F3F7F2 100%);
        border: 1px solid #ECE7DE;
        border-radius: 16px;
        padding: 22px 26px;
        margin-bottom: 20px;
    }
    .weather-box {
        background: #FFFFFF;
        border: 1px solid #EAE3D5;
        border-left: 5px solid #608A64;
        border-radius: 12px;
        padding: 12px 20px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .spot-box {
        background: #FFFFFF;
        border: 1px solid #ECE7DE;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 8px;
    }
    .exchange-box {
        background: linear-gradient(135deg, #FFFDF2 0%, #F2F8F2 100%);
        border: 1px solid #DFE7DC;
        border-radius: 14px;
        padding: 22px;
        text-align: center;
        margin: 16px 0;
    }
    .stButton>button {
        background: linear-gradient(135deg, #608A64 0%, #46674A 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# 5. 장소 검색 함수 (카카오 API 우선 -> 키 없거나 실패 시 OSM 오픈 API 자동 백업)
def search_places(keyword, api_key):
    # 1순위: 카카오 로컬 API 시도
    if api_key:
        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
        headers = {"Authorization": f"KakaoAK {api_key}"}
        try:
            res = requests.get(url, headers=headers, params={"query": keyword, "size": 7}, timeout=5)
            if res.status_code == 200:
                docs = res.json().get("documents", [])
                if docs:
                    return docs
        except Exception:
            pass

    # 2순위: 오픈 무료 검색 (Nominatim - 키 필요 없음)
    try:
        url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent": "TravelHubApp/1.0"}
        res = requests.get(url, params={"q": keyword, "format": "json", "limit": 5}, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            fallback_docs = []
            for item in data:
                fallback_docs.append({
                    "place_name": item.get("display_name", "").split(",")[0],
                    "address_name": item.get("display_name", ""),
                    "road_address_name": item.get("display_name", ""),
                    "category_name": "일반 > 명소",
                    "x": item.get("lon"),
                    "y": item.get("lat"),
                    "place_url": f"https://www.google.com/maps/search/?api=1&query={item.get('lat')},{item.get('lon')}"
                })
            return fallback_docs
    except Exception:
        pass

    return []

# 6. 오픈웨더 날씨 조회
@st.cache_data(ttl=1800)
def get_weather(lat, lon, api_key):
    if not api_key:
        return None
    url = "https://api.openweathermap.org/data/2.5/weather"
    try:
        res = requests.get(url, params={"lat": lat, "lon": lon, "appid": api_key, "units": "metric", "lang": "kr"}, timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

# 7. 환율 조회
@st.cache_data(ttl=3600)
def get_exchange():
    try:
        res = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5)
        if res.status_code == 200:
            return res.json().get("rates", {})
    except Exception:
        pass
    return {}

# --- 화면 출력부 ---
st.markdown("""
<div class="hero-box">
    <h3 style="margin:0; color:#2F3E32; font-weight:800;">🌿 스마트 여행 올인원 허브</h3>
    <p style="margin:4px 0 0 0; color:#6C7A6F; font-size:14px;">카카오 & 오픈 지도 탐색, 실시간 날씨, 환율 계산기 및 여행 포털</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📍 여행지 지도 & 날씨", "💱 실시간 환율 계산기", "🌐 여행 플랫폼 모음"])

# [TAB 1: 지도 & 날씨]
with tab1:
    with st.form(key="search_form"):
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            query = st.text_input("목적지 검색", value="경기도 양평 두물머리", label_visibility="collapsed")
        with col_btn:
            search_clicked = st.form_submit_button("장소 검색 🔍", use_container_width=True)

    # 검색 실행 및 세션 저장
    if "places_data" not in st.session_state or search_clicked or st.session_state.get("last_q") != query:
        st.session_state.places_data = search_places(query, KAKAO_KEY)
        st.session_state.last_q = query

    places = st.session_state.get("places_data", [])

    # 좌표 추출
    if places:
        c_lat, c_lng = float(places[0]["y"]), float(places[0]["x"])
        zoom_level = 14
    else:
        c_lat, c_lng = 37.5512, 126.9882  # 기본값
        zoom_level = 13

    # 날씨 박스
    w_info = get_weather(c_lat, c_lng, WEATHER_KEY)
    if w_info:
        temp = w_info["main"]["temp"]
        desc = w_info["weather"][0]["description"]
        icon = w_info["weather"][0]["icon"]
        st.markdown(f"""
        <div class="weather-box">
            <div style="display:flex; align-items:center; gap:12px;">
                <img src="https://openweathermap.org/img/wn/{icon}@2x.png" width="46"/>
                <div>
                    <b>현지 기상: {desc}</b><br>
                    <small style="color:#728074;">체감 {w_info['main']['feels_like']}°C · 습도 {w_info['main']['humidity']}%</small>
                </div>
            </div>
            <div style="font-size:24px; font-weight:800; color:#446849;">{temp}°C</div>
        </div>
        """, unsafe_allow_html=True)

    map_col, list_col = st.columns([6.5, 3.5])
    
    with map_col:
        # 지도 생성
        m = folium.Map(location=[c_lat, c_lng], zoom_start=zoom_level, tiles="OpenStreetMap")
        
        if places:
            for idx, p in enumerate(places):
                lat, lng = float(p["y"]), float(p["x"])
                name = p["place_name"]
                addr = p.get("road_address_name") or p.get("address_name")
                folium.Marker(
                    location=[lat, lng],
                    popup=f"<b>{name}</b><br>{addr}",
                    tooltip=name,
                    icon=folium.Icon(color="red" if idx == 0 else "green", icon="star" if idx == 0 else "info-sign")
                ).add_to(m)
        else:
            folium.Marker([c_lat, c_lng], tooltip="선택 위치", icon=folium.Icon(color="red")).add_to(m)
            
        # key에 좌표를 바인딩하여 목적지 검색 시 지도 화면이 즉시 전환되도록 설정
        st_folium(m, width="100%", height=520, returned_objects=[], key=f"map_{c_lat}_{c_lng}")

    with list_col:
        st.markdown("<h4 style='margin:0 0 10px 0; color:#344837; font-size:15px;'>📍 검색된 장소</h4>", unsafe_allow_html=True)
        if places:
            for idx, p in enumerate(places):
                cat = p.get('category_name', '').split('>')[-1].strip() or "명소"
                link_text = "카카오맵 보기 ↗" if "kakao" in p.get('place_url', '') else "상세 위치 보기 ↗"
                st.markdown(f"""
                <div class="spot-box">
                    <div style="display:flex; justify-content:space-between;">
                        <b style="font-size:13px; color:#2A3C2D;">{idx+1}. {p['place_name']}</b>
                        <span style="font-size:10px; background:#FFF9E0; color:#7B6816; padding:2px 4px; border-radius:3px;">{cat}</span>
                    </div>
                    <div style="font-size:11px; color:#718073; margin:3px 0;">{p.get('road_address_name') or p.get('address_name')}</div>
                    <a href="{p['place_url']}" target="_blank" style="font-size:11px; color:#4A734E; font-weight:600; text-decoration:none;">{link_text}</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("검색 결과가 없습니다.")

# [TAB 2: 환율]
with tab2:
    rates = get_exchange()
    if rates:
        krw_rate = rates.get("KRW", 1350.0)
        curr_list = ["USD", "JPY", "EUR", "CNY", "VND", "THB", "TWD", "AUD"]
        c1, c2 = st.columns(2)
        with c1:
            base = st.selectbox("기준 통화", curr_list)
        with c2:
            amt = st.number_input(f"{base} 금액", min_value=0.0, value=100.0, step=10.0)
        
        calc_krw = (amt / rates.get(base, 1.0)) * krw_rate
        st.markdown(f"""
        <div class="exchange-box">
            <span style="font-size:22px; font-weight:800; color:#2A3C2D;">{amt:,.2f} {base}</span>
            <span style="font-size:18px; color:#9EB0A1; margin:0 10px;">≈</span>
            <span style="font-size:26px; font-weight:800; color:#325838;">{calc_krw:,.0f} KRW (원)</span>
        </div>
        """, unsafe_allow_html=True)

# [TAB 3: 사이트 모음]
with tab3:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("##### ✈️ 항공권")
        st.link_button("스카이스캐너", "https://www.skyscanner.co.kr", use_container_width=True)
        st.write("")
        st.link_button("네이버 항공권", "https://flight.naver.com", use_container_width=True)
    with c2:
        st.markdown("##### 🏨 숙소")
        st.link_button("아고다", "https://www.agoda.com", use_container_width=True)
        st.write("")
        st.link_button("에어비앤비", "https://www.airbnb.co.kr", use_container_width=True)
    with c3:
        st.markdown("##### 🎟️ 액티비티")
        st.link_button("클룩", "https://www.klook.com/ko/", use_container_width=True)
        st.write("")
        st.link_button("마이리얼트립", "https://www.myrealtrip.com", use_container_width=True)