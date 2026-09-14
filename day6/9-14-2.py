import os
from pathlib import Path
import requests
import streamlit as st
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv

# 1. 레이아웃
st.set_page_config(page_title="스마트 여행 올인원 허브", page_icon="🌿", layout="wide")

# 2. .env 로드
current_file = Path(__file__).resolve()
for p in [current_file.parent] + list(current_file.parents):
    env_target = p / ".env"
    if env_target.exists():
        load_dotenv(env_target, override=True)
        break

# 3. 키 로드 (Secrets -> env)
def find_key(key_name):
    try:
        if key_name in st.secrets:
            return str(st.secrets[key_name]).strip()
    except Exception:
        pass
    return os.getenv(key_name, "").strip()

KAKAO_KEY = find_key("KAKAO_API_KEY")
WEATHER_KEY = find_key("OPENWEATHER_API_KEY")
EXCHANGE_KEY = find_key("EXCHANGE_RATE_API_KEY")

# 4. 스타일
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
        padding: 14px 20px;
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
    .rate-card {
        background: #FFFFFF;
        border: 1px solid #EAE5D9;
        border-radius: 12px;
        padding: 14px;
        text-align: center;
    }
    .calc-box {
        background: linear-gradient(135deg, #FFFDF2 0%, #F2F8F2 100%);
        border: 1px solid #DFE7DC;
        border-radius: 14px;
        padding: 24px;
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

# 5. 장소 검색 함수 (에러 명시 + 분할 검색 백업)
def search_places(keyword, api_key):
    keyword = keyword.strip()
    if not keyword:
        return []

    # 1순위: 카카오 로컬 키워드 검색
    if api_key:
        clean_key = api_key.replace("KakaoAK", "").strip()
        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
        headers = {"Authorization": f"KakaoAK {clean_key}"}
        try:
            res = requests.get(url, headers=headers, params={"query": keyword, "size": 10}, timeout=5)
            if res.status_code == 200:
                docs = res.json().get("documents", [])
                if docs:
                    return docs
            else:
                st.warning(f"카카오 API 응답 오류 [{res.status_code}]: REST API 키가 맞는지 확인해 주세요. ({res.text})")
        except Exception as e:
            st.warning(f"카카오 연결 오류: {e}")

    # 2순위: 오픈 무료 검색 (단어 분할 다중 검색)
    search_terms = [keyword]
    tokens = keyword.split()
    if len(tokens) > 1:
        search_terms.append(tokens[-1])  # 마지막 핵심 단어 (예: '두물머리')
        search_terms.append(" ".join(tokens[:-1]))

    headers = {"User-Agent": "SmartTravelHubApp/3.0"}
    for term in search_terms:
        try:
            url = "https://nominatim.openstreetmap.org/search"
            res = requests.get(url, params={"q": term, "format": "json", "limit": 7, "accept-language": "ko"}, headers=headers, timeout=4)
            if res.status_code == 200:
                data = res.json()
                if data:
                    fallback_docs = []
                    for item in data:
                        display = item.get("display_name", "")
                        fallback_docs.append({
                            "place_name": display.split(",")[0],
                            "address_name": display,
                            "road_address_name": display,
                            "category_name": "일반 > 명소",
                            "x": item.get("lon"),
                            "y": item.get("lat"),
                            "place_url": f"https://www.google.com/maps/search/?api=1&query={item.get('lat')},{item.get('lon')}"
                        })
                    return fallback_docs
        except Exception:
            continue

    return []

# 6. 날씨 조회
@st.cache_data(ttl=1200)
def get_weather(lat, lon, api_key):
    if api_key:
        try:
            url = "https://api.openweathermap.org/data/2.5/weather"
            res = requests.get(url, params={"lat": lat, "lon": lon, "appid": api_key, "units": "metric", "lang": "kr"}, timeout=4)
            if res.status_code == 200:
                data = res.json()
                return {
                    "temp": round(data["main"]["temp"], 1),
                    "feels_like": round(data["main"]["feels_like"], 1),
                    "humidity": data["main"]["humidity"],
                    "desc": data["weather"][0]["description"],
                    "icon_url": f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png"
                }
        except Exception:
            pass

    # 백업: Open-Meteo
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        res = requests.get(url, params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code"
        }, timeout=4)
        if res.status_code == 200:
            c = res.json().get("current", {})
            code = c.get("weather_code", 0)
            weather_map = {
                0: "맑음 ☀️", 1: "대체로 맑음 🌤️", 2: "구름 조금 ⛅", 3: "흐림 ☁️",
                45: "안개 🌫️", 48: "안개 🌫️", 51: "이슬비 🌦️", 61: "비 🌧️",
                71: "눈 ❄️", 95: "뇌우 ⛈️"
            }
            return {
                "temp": round(c.get("temperature_2m", 20.0), 1),
                "feels_like": round(c.get("apparent_temperature", 20.0), 1),
                "humidity": c.get("relative_humidity_2m", 50),
                "desc": weather_map.get(code, "온화함 🌤️"),
                "icon_url": "https://openweathermap.org/img/wn/02d@2x.png"
            }
    except Exception:
        pass
    return None

# 7. 환율 조회
@st.cache_data(ttl=1800)
def get_exchange_data(api_key):
    if api_key:
        try:
            url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
            res = requests.get(url, timeout=4)
            if res.status_code == 200:
                rates = res.json().get("conversion_rates", {})
                if rates:
                    return rates
        except Exception:
            pass

    try:
        res = requests.get("https://open.er-api.com/v6/latest/USD", timeout=4)
        if res.status_code == 200:
            return res.json().get("rates", {})
    except Exception:
        pass
    return {}

# --- 레이아웃 ---
st.markdown("""
<div class="hero-box">
    <h3 style="margin:0; color:#2F3E32; font-weight:800;">🌿 스마트 여행 올인원 허브</h3>
    <p style="margin:4px 0 0 0; color:#6C7A6F; font-size:14px;">실시간 지도·날씨 연동 & 다중 글로벌 환율 계산기</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📍 여행지 지도 & 날씨", "💱 글로벌 다중 환율 계산기", "🌐 여행 플랫폼 모음"])

# [TAB 1: 지도 & 날씨]
with tab1:
    with st.form(key="search_form"):
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            query = st.text_input("목적지 검색", value="경기도 양평 두물머리", label_visibility="collapsed")
        with col_btn:
            search_clicked = st.form_submit_button("장소 검색 🔍", use_container_width=True)

    # 검색어 변경 또는 검색 버튼 클릭 시 실행
    if "places_data" not in st.session_state or search_clicked or st.session_state.get("last_q") != query:
        st.session_state.places_data = search_places(query, KAKAO_KEY)
        st.session_state.last_q = query

    places = st.session_state.get("places_data", [])

    if places:
        c_lat, c_lng = float(places[0]["y"]), float(places[0]["x"])
        zoom_level = 14
    else:
        c_lat, c_lng = 37.5512, 126.9882
        zoom_level = 13

    # 날씨 박스
    w = get_weather(c_lat, c_lng, WEATHER_KEY)
    if w:
        st.markdown(f"""
        <div class="weather-box">
            <div style="display:flex; align-items:center; gap:14px;">
                <img src="{w['icon_url']}" width="50" height="50" style="object-fit:contain;"/>
                <div>
                    <b style="font-size:16px; color:#2A3C2D;">현지 기상 상태: {w['desc']}</b><br>
                    <small style="color:#6A776B;">체감온도 {w['feels_like']}°C · 상대습도 {w['humidity']}%</small>
                </div>
            </div>
            <div style="font-size:28px; font-weight:800; color:#3F6644;">{w['temp']}°C</div>
        </div>
        """, unsafe_allow_html=True)

    map_col, list_col = st.columns([6.5, 3.5])
    
    with map_col:
        m = folium.Map(location=[c_lat, c_lng], zoom_start=zoom_level, tiles="OpenStreetMap")
        if places:
            for idx, p in enumerate(places):
                lat, lng = float(p["y"]), float(p["x"])
                folium.Marker(
                    location=[lat, lng],
                    popup=f"<b>{p['place_name']}</b><br>{p.get('road_address_name') or p.get('address_name')}",
                    tooltip=p['place_name'],
                    icon=folium.Icon(color="red" if idx == 0 else "green", icon="star" if idx == 0 else "info-sign")
                ).add_to(m)
        else:
            folium.Marker([c_lat, c_lng], tooltip="선택 위치", icon=folium.Icon(color="red")).add_to(m)
            
        st_folium(m, width="100%", height=520, returned_objects=[], key=f"map_{c_lat}_{c_lng}")

    with list_col:
        st.markdown("<h4 style='margin:0 0 10px 0; color:#344837; font-size:15px;'>📍 검색된 장소 결과</h4>", unsafe_allow_html=True)
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
            st.info("검색된 장소가 없습니다. 검색어를 조금 더 간단히 입력해 보세요.")

# [TAB 2: 글로벌 다중 환율 계산기]
with tab2:
    rates = get_exchange_data(EXCHANGE_KEY)
    
    if rates:
        usd_krw = rates.get("KRW", 1350.0) / rates.get("USD", 1.0)
        jpy_krw = (rates.get("KRW", 1350.0) / rates.get("JPY", 150.0)) * 100
        eur_krw = rates.get("KRW", 1350.0) / rates.get("EUR", 0.92)
        cny_krw = rates.get("KRW", 1350.0) / rates.get("CNY", 7.2)
        
        st.markdown("**📊 주요 통화 실시간 환율 현황 (KRW 기준)**")
        rc1, rc2, rc3, rc4 = st.columns(4)
        with rc1:
            st.markdown(f"""<div class="rate-card"><small style="color:#718073;">🇺🇸 미국 USD</small><div style="font-size:19px; font-weight:800; color:#2A3C2D; margin-top:4px;">{usd_krw:,.1f} 원</div></div>""", unsafe_allow_html=True)
        with rc2:
            st.markdown(f"""<div class="rate-card"><small style="color:#718073;">🇯🇵 일본 JPY (100엔)</small><div style="font-size:19px; font-weight:800; color:#2A3C2D; margin-top:4px;">{jpy_krw:,.1f} 원</div></div>""", unsafe_allow_html=True)
        with rc3:
            st.markdown(f"""<div class="rate-card"><small style="color:#718073;">🇪🇺 유럽 EUR</small><div style="font-size:19px; font-weight:800; color:#2A3C2D; margin-top:4px;">{eur_krw:,.1f} 원</div></div>""", unsafe_allow_html=True)
        with rc4:
            st.markdown(f"""<div class="rate-card"><small style="color:#718073;">🇨🇳 중국 CNY</small><div style="font-size:19px; font-weight:800; color:#2A3C2D; margin-top:4px;">{cny_krw:,.1f} 원</div></div>""", unsafe_allow_html=True)

        st.markdown("---")
        
        curr_options = ["KRW", "USD", "JPY", "EUR", "CNY", "VND", "THB", "TWD", "AUD", "GBP", "SGD", "CAD", "CHF"]
        
        st.markdown("**🧮 양방향 통화 맞춤 계산기**")
        c1, c2, c3 = st.columns([2, 2, 3])
        
        with c1:
            from_curr = st.selectbox("보내는 통화 (From)", curr_options, index=1)
        with c2:
            to_curr = st.selectbox("받는 통화 (To)", curr_options, index=0)
        with c3:
            input_amt = st.number_input("환산할 금액", min_value=0.0, value=100.0, step=10.0)

        from_rate = rates.get(from_curr, 1.0)
        to_rate = rates.get(to_curr, 1.0)
        converted_result = (input_amt / from_rate) * to_rate

        st.markdown(f"""
        <div class="calc-box">
            <span style="font-size:24px; font-weight:700; color:#3A4A3C;">{input_amt:,.2f} {from_curr}</span>
            <span style="font-size:20px; color:#A4B4A6; margin:0 14px;">=</span>
            <span style="font-size:30px; font-weight:800; color:#305A36;">{converted_result:,.2f} {to_curr}</span>
            <div style="margin-top:8px; font-size:12px; color:#78887A;">(적용 기준 환율: 1 {from_curr} = {to_rate/from_rate:,.4f} {to_curr})</div>
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