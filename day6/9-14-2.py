import os
from pathlib import Path
import requests
import streamlit as st
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv

# 1. 페이지 레이아웃 설정
st.set_page_config(
    page_title="TripPalette - 스마트 트래블 허브",
    page_icon="🌿",
    layout="wide"
)

# 2. 로컬 실행 대비 .env 파일 로드 (상위 폴더 전수 조사)
current_file_path = Path(__file__).resolve()
for parent in [current_file_path.parent] + list(current_file_path.parents):
    candidate = parent / ".env"
    if candidate.exists() and candidate.is_file():
        load_dotenv(dotenv_path=candidate, override=True)
        break

# 3. [핵심] Streamlit Secrets + OS 환경 변수 + .env 통합 탐색 함수
def get_secret(key_name):
    # 1) Streamlit Cloud st.secrets 직접 조회 (대소문자 무관 탐색)
    try:
        if hasattr(st, "secrets"):
            if key_name in st.secrets:
                return str(st.secrets[key_name]).strip()
            # 소문자로 저장된 경우 대비
            if key_name.lower() in st.secrets:
                return str(st.secrets[key_name.lower()]).strip()
    except Exception:
        pass

    # 2) OS 환경 변수 및 .env 조회
    val = os.getenv(key_name) or os.getenv(key_name.lower())
    if val:
        return str(val).strip()

    return ""

# 변수명 KAKAO_API_KEY 명시적 추출
KAKAO_KEY = get_secret("KAKAO_API_KEY")
WEATHER_KEY = get_secret("OPENWEATHER_API_KEY")
EXCHANGE_KEY = get_secret("EXCHANGE_RATE_API_KEY")

# 4. 세련된 크림 옐로우 & 소프트 세이지 그린 스타일링
custom_ui_css = """
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    * {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    }

    .stApp {
        background-color: #FAF8F5 !important;
    }

    /* 상단 배너 */
    .hero-banner {
        background: linear-gradient(135deg, #FFFDF0 0%, #F3F7F2 100%);
        border: 1px solid #ECE7DE;
        border-radius: 18px;
        padding: 24px 28px;
        margin-bottom: 20px;
        box-shadow: 0 4px 16px rgba(160, 150, 130, 0.06);
    }
    .hero-title {
        font-size: 22px;
        font-weight: 800;
        color: #2F3E32;
        margin-bottom: 6px;
    }
    .hero-desc {
        font-size: 13.5px;
        color: #6C7A6F;
    }

    /* 탭 디자인 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        border-bottom: 2px solid #EBE5DB;
        padding-bottom: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #FFFFFF;
        border: 1px solid #ECE5DA;
        border-radius: 10px 10px 0 0;
        padding: 8px 18px;
        font-size: 14px;
        font-weight: 600;
        color: #687569;
    }
    .stTabs [aria-selected="true"] {
        background: #F4F8F3 !important;
        border-color: #608A64 !important;
        color: #2E4B33 !important;
        border-bottom: 2.5px solid #608A64 !important;
    }

    /* 날씨 위젯 */
    .weather-card {
        background: #FFFFFF;
        border: 1px solid #EAE3D5;
        border-left: 5px solid #608A64;
        border-radius: 12px;
        padding: 12px 20px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    }

    /* 장소 카드 */
    .spot-card {
        background: #FFFFFF;
        border: 1px solid #ECE7DE;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 10px;
        transition: all 0.2s ease;
    }
    .spot-card:hover {
        border-color: #8EAE92;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(96, 138, 100, 0.08);
    }

    /* 환율 카드 */
    .exchange-card {
        background: linear-gradient(135deg, #FFFDF2 0%, #F2F8F2 100%);
        border: 1px solid #DFE7DC;
        border-radius: 14px;
        padding: 22px;
        margin: 16px 0;
        text-align: center;
    }

    .service-card {
        background: #FFFFFF;
        border: 1px solid #ECE7DE;
        border-radius: 12px;
        padding: 18px;
    }
    .service-card-title {
        font-size: 15px;
        font-weight: 700;
        color: #344837;
        margin-bottom: 12px;
    }

    .stButton>button {
        background: linear-gradient(135deg, #608A64 0%, #46674A 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
</style>
"""
st.markdown(custom_ui_css, unsafe_allow_html=True)

# 5. 만약 키가 아직 서버 Secrets에 안 들어간 경우를 위한 사이드바 비상 입력기
if not KAKAO_KEY:
    with st.sidebar:
        st.warning("🔑 KAKAO_API_KEY 미감지")
        manual_key = st.text_input("카카오 REST API 키 직접 입력 (테스트용)", type="password")
        if manual_key:
            KAKAO_KEY = manual_key.strip()
            st.success("임시 키가 적용되었습니다!")

# 6. API 함수군
def search_kakao_places(keyword, api_key):
    if not api_key or not keyword:
        return []
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": keyword, "size": 8}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=6)
        if res.status_code == 200:
            return res.json().get("documents", [])
        elif res.status_code == 401:
            st.warning("⚠️ 카카오 인증 실패(401): `KAKAO_API_KEY`가 REST API 키인지 확인해 주세요.")
        else:
            st.warning(f"⚠️ 요청 응답 코드: {res.status_code}")
    except Exception as e:
        st.error(f"장소 검색 통신 에러: {e}")
    return []

@st.cache_data(ttl=1800)
def get_current_weather(lat, lon, api_key):
    if not api_key:
        return None
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",
        "lang": "kr"
    }
    try:
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

@st.cache_data(ttl=3600)
def get_exchange_rates(api_key, base_currency="USD"):
    if api_key:
        try:
            url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                if data.get("result") == "success":
                    return data.get("conversion_rates", {})
        except Exception:
            pass
    try:
        fallback_res = requests.get(f"https://open.er-api.com/v6/latest/{base_currency}", timeout=5)
        if fallback_res.status_code == 200:
            return fallback_res.json().get("rates", {})
    except Exception:
        pass
    return {}

# 7. 상단 헤더
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🌿 스마트 여행 올인원 허브</div>
    <div class="hero-desc">카카오 장소 검색, OpenWeather 현지 기상정보, 실시간 환율 계산기 및 여행 사이트 포털</div>
</div>
""", unsafe_allow_html=True)

# 8. 상단 탭 구성
tab_map, tab_exchange, tab_links = st.tabs([
    "📍 여행지 지도 & 날씨", 
    "💱 실시간 환율 계산기", 
    "🌐 여행 플랫폼 모음"
])

# ----------------- TAB 1: 지도 & 날씨 -----------------
with tab_map:
    with st.form("search_form"):
        col_search, col_btn = st.columns([5, 1])
        with col_search:
            search_query = st.text_input(
                "목적지 검색", 
                value="서울 남산타워", 
                placeholder="명소, 카페, 맛집, 주소를 검색해 보세요...",
                label_visibility="collapsed"
            )
        with col_btn:
            submitted = st.form_submit_button("장소 검색 🔍", use_container_width=True)

    # 검색 실행 조건
    if "places" not in st.session_state or submitted:
        if KAKAO_KEY:
            st.session_state.places = search_kakao_places(search_query, KAKAO_KEY)
        else:
            st.session_state.places = []
            st.info("💡 카카오 키가 감지되지 않았습니다. Streamlit Cloud의 Secrets에 등록하거나 사이드바에 키를 입력하면 바로 연동됩니다.")

    places = st.session_state.get("places", [])

    # 좌표 세팅 (기본: 서울 N서울타워)
    if places:
        center_lat = float(places[0]["y"])
        center_lng = float(places[0]["x"])
        zoom = 15
    else:
        center_lat, center_lng = 37.5512, 126.9882
        zoom = 14

    # 날씨 위젯 표시
    weather_data = get_current_weather(center_lat, center_lng, WEATHER_KEY)
    if weather_data:
        w_main = weather_data["main"]
        w_weather = weather_data["weather"][0]
        icon_code = w_weather["icon"]
        icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
        
        st.markdown(f"""
        <div class="weather-card">
            <div style="display: flex; align-items: center; gap: 14px;">
                <img src="{icon_url}" width="48" height="48" style="margin: -6px 0;"/>
                <div>
                    <div style="font-size: 15px; font-weight: 700; color: #2C3E2D;">
                        현지 날씨: {w_weather['description']}
                    </div>
                    <div style="font-size: 13px; color: #728074;">
                        체감 {w_main['feels_like']}°C · 습도 {w_main['humidity']}% · 풍속 {weather_data['wind']['speed']}m/s
                    </div>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 24px; font-weight: 800; color: #446849;">
                    {w_main['temp']}°C
                </div>
                <div style="font-size: 12px; color: #9AA79C;">
                    최저 {w_main['temp_min']}°C / 최고 {w_main['temp_max']}°C
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 2열 분할: 지도 + 장소 목록
    map_col, list_col = st.columns([6.5, 3.5])

    with map_col:
        m = folium.Map(location=[center_lat, center_lng], zoom_start=zoom, tiles="OpenStreetMap")

        if places:
            for idx, p in enumerate(places):
                lat = float(p["y"])
                lng = float(p["x"])
                name = p.get("place_name")
                addr = p.get("road_address_name") or p.get("address_name")
                phone = p.get("phone", "전화번호 미등록")
                place_url = p.get("place_url", "#")

                popup_html = f"""
                <div style="font-family: sans-serif; min-width: 160px; padding: 4px;">
                    <span style="background: #EAF3EC; color: #325838; font-size: 10px; font-weight: bold; padding: 2px 5px; border-radius: 3px;">#{idx+1}</span>
                    <h5 style="margin: 4px 0; color: #2A3C2D; font-size: 13px; font-weight: bold;">{name}</h5>
                    <p style="margin: 0; font-size: 11px; color: #5B6A5E;">{addr}</p>
                    <p style="margin: 2px 0 6px 0; font-size: 10px; color: #8F9E92;">📞 {phone}</p>
                    <a href="{place_url}" target="_blank" style="display: inline-block; background: #608A64; color: #FFF; font-size: 11px; text-decoration: none; padding: 3px 8px; border-radius: 4px; font-weight: bold;">카카오맵 상세 ↗</a>
                </div>
                """
                folium.Marker(
                    location=[lat, lng],
                    popup=folium.Popup(popup_html, max_width=260),
                    tooltip=name,
                    icon=folium.Icon(color="red" if idx == 0 else "green", icon="star" if idx == 0 else "info-sign")
                ).add_to(m)
        else:
            folium.Marker(
                location=[center_lat, center_lng],
                popup="위치: 서울 N서울타워",
                tooltip="서울 N서울타워",
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(m)

        st_folium(m, width="100%", height=530, returned_objects=[])

    with list_col:
        st.markdown("<h4 style='font-size: 15px; font-weight: 700; color: #344837; margin-bottom: 10px;'>📍 검색된 장소</h4>", unsafe_allow_html=True)
        if places:
            for idx, p in enumerate(places):
                category = p.get('category_name', '').split('>')[-1].strip() or "명소"
                st.markdown(f"""
                <div class="spot-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <b style="font-size: 13px; color: #2A3C2D;">{idx+1}. {p['place_name']}</b>
                        <span style="font-size: 10px; background: #FFF9E0; color: #7B6816; padding: 2px 5px; border-radius: 4px; font-weight: 600;">{category}</span>
                    </div>
                    <div style="font-size: 11.5px; color: #718073; margin-top: 4px;">
                        {p.get('road_address_name') or p.get('address_name')}
                    </div>
                    <div style="margin-top: 6px;">
                        <a href="{p['place_url']}" target="_blank" style="font-size: 11.5px; color: #4A734E; font-weight: 600; text-decoration: none;">상세 안내 보기 ↗</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("검색창에 원하는 장소를 입력하고 검색 버튼을 눌러주세요.")

# ----------------- TAB 2: 실시간 환율 계산기 -----------------
with tab_exchange:
    rates = get_exchange_rates(EXCHANGE_KEY, "USD")
    
    if rates:
        krw_per_usd = rates.get("KRW", 1350.0)
        currency_info = {
            "USD": "미국 달러 ($)",
            "JPY": "일본 엔 (¥)",
            "EUR": "유럽 유로 (€)",
            "CNY": "중국 위안 (¥)",
            "VND": "베트남 동 (₫)",
            "THB": "태국 바트 (฿)",
            "TWD": "대만 달러 (NT$)",
            "AUD": "호주 달러 (A$)"
        }
        
        c1, c2, c3 = st.columns([2, 2.5, 2.5])
        with c1:
            base_curr = st.selectbox("기준 외화 선택", list(currency_info.keys()), format_func=lambda x: f"{x} - {currency_info[x]}")
        with c2:
            amount = st.number_input(f"{base_curr} 환전 금액", min_value=0.0, value=100.0, step=10.0)
        
        curr_rate_to_usd = rates.get(base_curr, 1.0)
        krw_value = (amount / curr_rate_to_usd) * krw_per_usd
        unit_rate = (1.0 / curr_rate_to_usd) * krw_per_usd

        with c3:
            st.metric(
                label=f"1 {base_curr} 당 매매기준율",
                value=f"{unit_rate:,.2f} 원"
            )

        st.markdown(f"""
        <div class="exchange-card">
            <div style="font-size: 13px; font-weight: 600; color: #6E7E70; margin-bottom: 6px;">실시간 환산 결과</div>
            <span style="font-size: 22px; font-weight: 800; color: #2A3C2D;">{amount:,.2f} {base_curr}</span>
            <span style="font-size: 18px; color: #9EB0A1; margin: 0 8px;">≈</span>
            <span style="font-size: 26px; font-weight: 800; color: #325838;">{krw_value:,.0f} KRW (원)</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<h5 style='font-size: 14px; font-weight: 700; color: #344837; margin-top: 20px;'>📊 주요 통화 기준 환율</h5>", unsafe_allow_html=True)
        grid = st.columns(4)
        for i, c in enumerate(["USD", "JPY", "EUR", "CNY"]):
            rate_val = (1.0 / rates.get(c, 1.0)) * krw_per_usd
            grid[i].metric(label=f"{c} / KRW", value=f"{rate_val:,.2f} 원")
    else:
        st.warning("환율 데이터를 불러오는 중입니다.")

# ----------------- TAB 3: 여행 플랫폼 링크 -----------------
with tab_links:
    col_air, col_hotel, col_act = st.columns(3)

    with col_air:
        st.markdown("""
        <div class="service-card">
            <div class="service-card-title">✈️ 항공권 예약</div>
        """, unsafe_allow_html=True)
        st.link_button("스카이스캐너 (Skyscanner)", "https://www.skyscanner.co.kr", use_container_width=True)
        st.write("")
        st.link_button("네이버 항공권", "https://flight.naver.com", use_container_width=True)
        st.write("")
        st.link_button("구글 플라이트 (Google Flights)", "https://www.google.com/travel/flights", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_hotel:
        st.markdown("""
        <div class="service-card">
            <div class="service-card-title">🏨 숙소 & 호텔</div>
        """, unsafe_allow_html=True)
        st.link_button("아고다 (Agoda)", "https://www.agoda.com", use_container_width=True)
        st.write("")
        st.link_button("부킹닷컴 (Booking.com)", "https://www.booking.com", use_container_width=True)
        st.write("")
        st.link_button("에어비앤비 (Airbnb)", "https://www.airbnb.co.kr", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_act:
        st.markdown("""
        <div class="service-card">
            <div class="service-card-title">🎟️ 투어 & 티켓</div>
        """, unsafe_allow_html=True)
        st.link_button("클룩 (Klook)", "https://www.klook.com/ko/", use_container_width=True)
        st.write("")
        st.link_button("마이리얼트립 (MyRealTrip)", "https://www.myrealtrip.com", use_container_width=True)
        st.write("")
        st.link_button("트리플 (Triple)", "https://triple.guide", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)