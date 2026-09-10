# 날씨: API 실습
# Openweather 현재 날씨 API로 특정 도시의 날씨를 가져와 출력한다.
# 사전준비 = Openweather회원 가입 후 API 발급
# API는 Github에 올리면 안됨. 노출되면 절대 안되는 키 => 그래서 env파일 따로 만들어서 여기에API 보관하고, 이걸 끌어오도록 명령 설정
# pip install requests python-dotenv
# .env 파일을 생성하고 이곳에 OPENWEATHER_API_KEY=발급받은_API_KEY로 변수명 설정
# .env.example OPENWEATHER_API_KEY=your_key
# .env.example 받아서 .env로 이름 바꾸고 자기 API를 채운다.


# import os
# import requests
# import streamlit
# from dotenv import load_dotenv



# load_dotenv() #.env 파일을 읽어 환경 변수로 등록한다.

# API_KEY = os.getenv("OPENWEATHER_API_KEY")

import os
from pathlib import Path
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from dotenv import load_dotenv
import requests

# --------------------------------------------------
# 1. 환경 변수 및 설정
# --------------------------------------------------
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

# .env 파일을 읽어 환경 변수로 등록한다.
load_dotenv(dotenv_path=ENV_PATH)

# 환경 변수에서 API 키 불러오기
API_KEY = os.getenv("OPENWEATHER_API_KEY")
EXCHANGE_KEY = os.getenv("EXCHANGE_RATE_API_KEY")

st.set_page_config(
    page_title="기상청 종합기상관측 & 외환 통보 포털",
    page_icon="🛰️",
    layout="wide"
)

# --------------------------------------------------
# 2. 통합 프리미엄 UI CSS
# --------------------------------------------------
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    html, body, [class*="css"] {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    }
    
    .stApp {
        background-color: #f1f5f9;
    }
    
    .kma-header {
        background: linear-gradient(135deg, #091e3a 0%, #173d6d 100%);
        border-radius: 16px;
        padding: 22px 30px;
        color: #ffffff;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.2);
        border-bottom: 4px solid #38bdf8;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .kma-header h1 {
        font-size: 25px;
        font-weight: 800;
        margin: 0;
        color: #ffffff !important;
        letter-spacing: -0.5px;
    }
    .kma-header p {
        font-size: 13px;
        color: #93c5fd;
        margin: 6px 0 0 0;
        font-weight: 500;
    }

    .glass-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 22px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 18px;
    }

    .fx-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 4px 10px rgba(15, 23, 42, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .fx-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.08);
        border-color: #cbd5e1;
    }
    .fx-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    .fx-country {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 13.5px;
        font-weight: 700;
        color: #334155;
    }
    .fx-badge {
        font-size: 11px;
        font-weight: 800;
        padding: 2px 7px;
        border-radius: 6px;
        background: #f1f5f9;
        color: #475569;
        letter-spacing: 0.5px;
    }
    .fx-rate {
        font-size: 24px;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.5px;
    }
    .fx-rate span {
        font-size: 14px;
        font-weight: 600;
        color: #64748b;
        margin-left: 2px;
    }
    .fx-sub {
        font-size: 11.5px;
        color: #94a3b8;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

if not API_KEY or API_KEY == "your_key":
    st.error("⚠️ 상위 디렉터리 `.env`에 `OPENWEATHER_API_KEY` 설정이 필요합니다.")
    st.stop()

# --------------------------------------------------
# 3. 권역 정의 (울릉도/독도 명확 분리 및 신규 한반도 정밀 좌표)
# --------------------------------------------------
REGION_SPECS = {
    "서해5도": {"en": "Incheon", "top": "24%", "left": "12%"},
    "서울":     {"en": "Seoul", "top": "20%", "left": "33%"},
    "경기":     {"en": "Suwon", "top": "27%", "left": "36%"},
    "영서":     {"en": "Chuncheon", "top": "17%", "left": "51%"},
    "영동":     {"en": "Gangneung", "top": "21%", "left": "70%"},
    "울릉도":   {"en": "Ulleungdo", "top": "25%", "left": "83%"},
    "독도":     {"en": "Dokdo", "top": "30%", "left": "93%"},
    "충남":     {"en": "Daejeon", "top": "41%", "left": "31%"},
    "충북":     {"en": "Cheongju", "top": "36%", "left": "49%"},
    "경북":     {"en": "Andong", "top": "42%", "left": "68%"},
    "전북":     {"en": "Jeonju", "top": "54%", "left": "37%"},
    "경남":     {"en": "Changwon", "top": "62%", "left": "62%"},
    "부산":     {"en": "Busan", "top": "65%", "left": "76%"},
    "전남":     {"en": "Gwangju", "top": "69%", "left": "32%"},
    "제주도":   {"en": "Jeju", "top": "89%", "left": "32%"}
}

def get_kma_emoji(icon_code: str) -> str:
    mapping = {
        "01d": "☀️", "01n": "🌙",
        "02d": "⛅", "02n": "⛅",
        "03d": "☁️", "03n": "☁️",
        "04d": "☁️", "04n": "☁️",
        "09d": "🌧️", "09n": "🌧️",
        "10d": "🌦️", "10n": "🌧️",
        "11d": "⛈️", "11n": "⛈️",
        "13d": "❄️", "13n": "❄️",
        "50d": "🌫️", "50n": "🌫️",
    }
    return mapping.get(icon_code, "⛅")

# --------------------------------------------------
# 4. API 수신 캐싱 함수
# --------------------------------------------------
@st.cache_data(ttl=600)
def fetch_weather_by_city(city_en: str):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city_en, "appid": API_KEY, "units": "metric", "lang": "kr"}
    try:
        res = requests.get(url, params=params, timeout=5)
        # 독도(Dokdo) 영문 쿼리가 매핑되지 않을 경우 울릉도 기상으로 안전 보정
        if res.status_code != 200 and city_en.lower() == "dokdo":
            params["q"] = "Ulleungdo"
            res = requests.get(url, params=params, timeout=5)
        return res.json() if res.status_code == 200 else None
    except:
        return None

@st.cache_data(ttl=600)
def fetch_forecast_by_city(city_en: str, unit: str):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"q": city_en, "appid": API_KEY, "units": unit, "lang": "kr"}
    try:
        res = requests.get(url, params=params, timeout=5)
        if res.status_code != 200 and city_en.lower() == "dokdo":
            params["q"] = "Ulleungdo"
            res = requests.get(url, params=params, timeout=5)
        return res.json() if res.status_code == 200 else None
    except:
        return None

@st.cache_data(ttl=1800)
def fetch_exchange_data(api_val: str):
    if not api_val:
        return None
    try:
        if api_val.startswith("http"):
            res = requests.get(api_val, timeout=5)
            if res.status_code == 200:
                return res.json()
        url = f"https://v6.exchangerate-api.com/v6/{api_val}/latest/USD"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()
        return None
    except:
        return None

# --------------------------------------------------
# 5. 헤더 배너
# --------------------------------------------------
now = datetime.now()
now_time_str = now.strftime('%m.%d. %H:%M')

st.markdown(f"""
<div class="kma-header">
    <div>
        <h1>🛰️ 국가종합기상정보 관측 포털</h1>
        <p>OpenWeather 관측망 연동 · 지상수치예보 & 외환 통합 모니터링</p>
    </div>
    <div style="text-align: right;">
        <span style="background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.4); color: #7dd3fc; font-size: 13px; padding: 6px 14px; border-radius: 30px; font-weight: 600;">
            ● LIVE 통보문 ({now_time_str} 기준)
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 6. 본문 2열 레이아웃 (좌: 정밀 한반도도, 우: 브리핑)
# --------------------------------------------------
col_map, col_detail = st.columns([11, 13], gap="large")

with col_map:
    with st.spinner("전국 기상 감시판 렌더링 중..."):
        badges_elements = []
        for name, meta in REGION_SPECS.items():
            data = fetch_weather_by_city(meta["en"])
            if data:
                temp = data["main"]["temp"]
                icon = data["weather"][0]["icon"]
                emoji = get_kma_emoji(icon)
                rain_mm = data.get("rain", {}).get("1h", data.get("rain", {}).get("3h", 0.0))
                rain_str = f"{rain_mm:.1f}" if rain_mm > 0 else "0"
                temp_str = f"{temp:.1f}"
            else:
                emoji = "⛅"
                temp_str = "--"
                rain_str = "0"

            badge = (
                f'<div class="region-card" style="top:{meta["top"]};left:{meta["left"]};">'
                f'<div class="region-title">{name}</div>'
                f'<div class="region-icon">{emoji}</div>'
                f'<div class="region-badge">'
                f'<span class="temp-val">{temp_str}</span><span class="divider">/</span><span class="rain-val">{rain_str}</span>'
                f'</div>'
                f'</div>'
            )
            badges_elements.append(badge)

        badges_html = "".join(badges_elements)

        # 기상청 실시간 지상관측도용 한반도 정밀 벡터
        map_board_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif; }}
            body {{ background: transparent; display: flex; justify-content: center; }}
            .kma-container {{
                width: 100%;
                border-radius: 18px;
                overflow: hidden;
                box-shadow: 0 12px 30px -8px rgba(14, 116, 144, 0.25);
                border: 1px solid #bfdbfe;
            }}
            .kma-top-bar {{
                background: #0f2744;
                color: #f8fafc;
                padding: 13px 20px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                font-size: 13px;
                font-weight: 600;
            }}
            .weather-map-board {{
                position: relative;
                width: 100%;
                height: 640px;
                background: linear-gradient(180deg, #93c5fd 0%, #60a5fa 100%);
                overflow: hidden;
            }}
            .korea-svg-bg {{
                position: absolute;
                width: 100%;
                height: 100%;
                top: 0;
                left: 0;
            }}
            .region-card {{
                position: absolute;
                transform: translate(-50%, -50%);
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
                user-select: none;
                cursor: default;
                transition: transform 0.15s ease-in-out;
            }}
            .region-card:hover {{
                transform: translate(-50%, -55%) scale(1.06);
                z-index: 10;
            }}
            .region-title {{
                font-size: 11.5px;
                font-weight: 800;
                color: #0f172a;
                margin-bottom: 2px;
                text-shadow: 0 1px 3px rgba(255,255,255,0.9);
                letter-spacing: -0.3px;
            }}
            .region-icon {{
                font-size: 24px;
                line-height: 1.1;
                filter: drop-shadow(0 2px 4px rgba(0,0,0,0.15));
            }}
            .region-badge {{
                background: rgba(255, 255, 255, 0.95);
                padding: 2px 6px;
                border-radius: 12px;
                box-shadow: 0 2px 5px rgba(15, 23, 42, 0.12);
                border: 1px solid rgba(226, 232, 240, 0.8);
                display: flex;
                align-items: center;
                gap: 2px;
                font-size: 10.5px;
                font-weight: 800;
                margin-top: 2px;
                white-space: nowrap;
            }}
            .temp-val {{ color: #0f172a; }}
            .divider {{ color: #94a3b8; font-size: 9px; }}
            .rain-val {{ color: #0284c7; }}
            .map-legend {{
                position: absolute;
                bottom: 14px;
                right: 14px;
                font-size: 11.5px;
                font-weight: 700;
                color: #0f172a;
                background: rgba(255,255,255,0.85);
                padding: 4px 10px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.08);
            }}
        </style>
        </head>
        <body>
            <div class="kma-container">
                <div class="kma-top-bar">
                    <span>🕒 {now_time_str} 현재 기상도</span>
                    <span style="color: #38bdf8; font-size: 12px;">기상청 지상관측 통보문</span>
                </div>
                <div class="weather-map-board">
                    <svg class="korea-svg-bg" viewBox="0 0 520 560" preserveAspectRatio="none">
                        <defs>
                            <filter id="kma-shadow" x="-20%" y="-20%" width="140%" height="140%">
                                <feDropShadow dx="8" dy="12" stdDeviation="5" flood-color="#0f2b5c" flood-opacity="0.25"/>
                            </filter>
                        </defs>
                        
                        <!-- 서해5도 (백령도) -->
                        <ellipse cx="65" cy="135" rx="14" ry="7" fill="#ffffff" filter="url(#kma-shadow)"/>
                        
                        <!-- 한반도 남한 본토 정밀 지형 (동해안, 호미곶, 부산포, 남해안 다도해, 태안반도 재현) -->
                        <path d="M 160,50 
                                 L 230,48 
                                 L 255,60 
                                 L 285,75 
                                 L 330,105 
                                 C 350,125 365,165 360,200 
                                 C 358,225 368,245 378,265
                                 L 395,305 
                                 C 405,325 410,335 412,350
                                 C 415,365 415,375 400,388
                                 L 390,398 
                                 C 382,410 375,418 360,422
                                 L 335,426 
                                 C 310,428 295,432 270,428
                                 L 235,430 
                                 C 200,432 175,438 150,430
                                 L 140,410 
                                 L 148,380 
                                 L 155,340 
                                 L 150,300 
                                 L 128,270 
                                 L 115,245 
                                 L 125,225 
                                 L 142,210 
                                 L 148,175 
                                 L 138,150 
                                 L 148,110 
                                 L 155,80 Z" 
                              fill="#ffffff" filter="url(#kma-shadow)"/>
                        
                        <!-- 제주도 -->
                        <ellipse cx="165" cy="495" rx="38" ry="18" fill="#ffffff" filter="url(#kma-shadow)"/>
                        
                        <!-- 울릉도 본섬 -->
                        <path d="M 425,140 C 428,135 438,133 442,138 C 445,142 443,148 438,150 C 432,152 423,148 425,140 Z" fill="#ffffff" filter="url(#kma-shadow)"/>
                        
                        <!-- 독도 (동도/서도 분리 형태) -->
                        <circle cx="482" cy="168" r="4.5" fill="#ffffff" filter="url(#kma-shadow)"/>
                        <circle cx="489" cy="172" r="3.5" fill="#ffffff" filter="url(#kma-shadow)"/>
                    </svg>
                    {badges_html}
                    <div class="map-legend">기온℃ / 강수량mm</div>
                </div>
            </div>
        </body>
        </html>
        """
        components.html(map_board_html, height=700)

with col_detail:
    c_sub1, c_sub2, c_sub3 = st.columns([1.5, 1, 1.2])
    with c_sub1:
        # 울릉도, 독도를 포함한 전 지역 개별 선택 가능
        selected_region = st.selectbox("🎯 관측 지점 선택", options=list(REGION_SPECS.keys()), index=12)
        target_en = REGION_SPECS[selected_region]["en"]
    with c_sub2:
        unit_label = st.selectbox("온도 단위", ["섭씨 (°C)", "화씨 (°F)"])
        unit_param = "metric" if "섭씨" in unit_label else "imperial"
        unit_symbol = "°C" if "섭씨" in unit_label else "°F"
    with c_sub3:
        view_mode = st.selectbox("예보 조회 방식", ["시간대별 (3시간)", "요일별 (5일)", "상세 제원"])

    detail_curr = fetch_weather_by_city(target_en)
    detail_fore = fetch_forecast_by_city(target_en, unit_param)

    if detail_curr and detail_fore:
        temp = detail_curr["main"]["temp"]
        feels = detail_curr["main"]["feels_like"]
        if unit_param == "imperial":
            temp = (temp * 9/5) + 32
            feels = (feels * 9/5) + 32

        cur_emoji = get_kma_emoji(detail_curr["weather"][0]["icon"])
        cur_desc = detail_curr["weather"][0]["description"]

        st.markdown(f"""
        <div class="glass-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <span style="background:#e0f2fe; color:#0369a1; font-weight:800; padding:4px 10px; border-radius:6px; font-size:12.5px;">
                    기상특보 브리핑
                </span>
                <span style="color:#64748b; font-size:13px; font-weight:600;">{detail_curr['name']} ({selected_region}) 관측소</span>
            </div>
            <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px;">
                <div style="font-size: 38px; font-weight: 800; color:#0f172a; letter-spacing:-1px;">
                    {cur_emoji} {temp:.1f}{unit_symbol} 
                    <span style="font-size: 19px; font-weight: 600; color: #475569; margin-left: 6px;">{cur_desc}</span>
                </div>
                <div style="font-size: 13.5px; color: #334155; font-weight: 500;">
                    체감 <b>{feels:.1f}{unit_symbol}</b> &nbsp;|&nbsp; 
                    최저 <b>{detail_curr['main']['temp_min']:.1f}{unit_symbol}</b> / 
                    최고 <b>{detail_curr['main']['temp_max']:.1f}{unit_symbol}</b>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("상대습도", f"{detail_curr['main']['humidity']}%")
        m2.metric("지상풍속", f"{detail_curr['wind']['speed']} m/s")
        m3.metric("해면기압", f"{detail_curr['main']['pressure']} hPa")
        m4.metric("가시거리", f"{detail_curr.get('visibility', 0) / 1000:.1f} km")

        st.write("")

        forecast_items = detail_fore.get("list", [])
        df_raw = []
        days = ["월", "화", "수", "목", "금", "토", "일"]
        for it in forecast_items:
            dt = datetime.fromtimestamp(it["dt"])
            df_raw.append({
                "날짜": f"{dt.strftime('%m/%d')}({days[dt.weekday()]})",
                "시간": dt.strftime("%H시"),
                "기온": it["main"]["temp"],
                "이모지": get_kma_emoji(it["weather"][0]["icon"]),
                "강수": int(it.get("pop", 0) * 100)
            })
        df = pd.DataFrame(df_raw)

        if view_mode == "시간대별 (3시간)":
            st.caption("📈 향후 24시간 기온 추이 선도")
            chart_data = df.head(8).set_index("시간")[["기온"]]
            st.line_chart(chart_data, height=180)
            
            sub_cols = st.columns(8)
            for idx, row in df.head(8).iterrows():
                with sub_cols[idx]:
                    st.markdown(f"<div style='text-align:center; font-size:12px; font-weight:700;'>{row['시간']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align:center; font-size:22px; margin:2px 0;'>{row['이모지']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align:center; font-size:13px; font-weight:700;'>{row['기온']:.0f}°</div>", unsafe_allow_html=True)
                    st.caption(f"☔{row['강수']}%")

        elif view_mode == "요일별 (5일)":
            st.caption("📅 주간 중기예보 통보")
            daily = df.groupby("날짜", sort=False)
            d_cols = st.columns(min(5, len(daily)))
            for idx, (day_label, grp) in enumerate(daily):
                if idx >= 5: break
                with d_cols[idx]:
                    st.markdown(f"<div style='font-weight:700; font-size:13px;'>{day_label}</div>", unsafe_allow_html=True)
                    mid = grp.iloc[len(grp)//2]
                    st.markdown(f"<div style='font-size:32px; margin:4px 0;'>{mid['이모지']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<span style='font-size:12px;'>최저 <b>{grp['기온'].min():.0f}°</b></span><br><span style='font-size:12px;'>최고 <b>{grp['기온'].max():.0f}°</b></span>", unsafe_allow_html=True)
                    st.caption(f"강수 {grp['강수'].max()}%")
        else:
            st.markdown(f"""
            - **관측소 좌표**: 위도 `{detail_curr['coord']['lat']}` / 경도 `{detail_curr['coord']['lon']}`
            - **일출/일몰**: 🌅 {datetime.fromtimestamp(detail_curr['sys']['sunrise']).strftime('%H:%M')} / 🌇 {datetime.fromtimestamp(detail_curr['sys']['sunset']).strftime('%H:%M')}
            - **데이터 갱신 주기**: 10분 자동 캐싱 동기화
            """)

# --------------------------------------------------
# 7. 실시간 주요국 외환 시황 섹션
# --------------------------------------------------
st.divider()

st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px;">
    <div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <h3 style="margin: 0; color: #0f172a; font-size: 21px; font-weight: 800; letter-spacing: -0.5px;">
                💱 국가금융외환 실시간 시황
            </h3>
            <span style="background: #e0f2fe; color: #0369a1; font-size: 12px; font-weight: 700; padding: 3px 8px; border-radius: 6px;">
                한국은행·외환망 고시
            </span>
        </div>
        <p style="margin: 5px 0 0 0; color: #64748b; font-size: 13.5px;">
            원화(KRW) 매매기준율 환산 실시간 시황 통보문
        </p>
    </div>
    <div style="text-align: right; color: #94a3b8; font-size: 12.5px; font-weight: 500;">
        기준: 1 USD / 100 JPY / 1 EUR / 1 CNY
    </div>
</div>
""", unsafe_allow_html=True)

rates_display = {
    "USD": {"val": "--", "name": "미국 달러", "flag": "🇺🇸", "code": "USD/KRW", "sub": "1달러 기준"},
    "JPY": {"val": "--", "name": "일본 엔", "flag": "🇯🇵", "code": "JPY/KRW", "sub": "100엔 기준"},
    "EUR": {"val": "--", "name": "유럽 유로", "flag": "🇪🇺", "code": "EUR/KRW", "sub": "1유로 기준"},
    "CNY": {"val": "--", "name": "중국 위안", "flag": "🇨🇳", "code": "CNY/KRW", "sub": "1위안 기준"}
}

if EXCHANGE_KEY:
    rate_res = fetch_exchange_data(EXCHANGE_KEY)
    
    if rate_res and "conversion_rates" in rate_res:
        rates = rate_res["conversion_rates"]
        usd_krw = rates.get("KRW", 0)
        jpy_rate = rates.get("JPY", 1)
        eur_rate = rates.get("EUR", 1)
        cny_rate = rates.get("CNY", 1)

        jpy_krw = (usd_krw / jpy_rate) * 100 if jpy_rate else 0
        eur_krw = (usd_krw / eur_rate) if eur_rate else 0
        cny_krw = (usd_krw / cny_rate) if cny_rate else 0

        rates_display["USD"]["val"] = f"{usd_krw:,.2f}"
        rates_display["JPY"]["val"] = f"{jpy_krw:,.2f}"
        rates_display["EUR"]["val"] = f"{eur_krw:,.2f}"
        rates_display["CNY"]["val"] = f"{cny_krw:,.2f}"

    elif isinstance(rate_res, list) and len(rate_res) > 0:
        rate_dict = {item.get("cur_unit", ""): item.get("deal_bas_r", "0") for item in rate_res}
        rates_display["USD"]["val"] = f"{rate_dict.get('USD', '--')}"
        rates_display["JPY"]["val"] = f"{rate_dict.get('JPY(100)', '--')}"
        rates_display["EUR"]["val"] = f"{rate_dict.get('EUR', '--')}"
        rates_display["CNY"]["val"] = f"{rate_dict.get('CNH', rate_dict.get('CNY', '--'))}"

fx_cols = st.columns(4)
for idx, (curr_key, info) in enumerate(rates_display.items()):
    with fx_cols[idx]:
        st.markdown(f"""
        <div class="fx-card">
            <div class="fx-header">
                <span class="fx-country">{info['flag']} {info['name']}</span>
                <span class="fx-badge">{info['code']}</span>
            </div>
            <div class="fx-rate">
                {info['val']} <span>원</span>
            </div>
            <div class="fx-sub">
                {info['sub']}
            </div>
        </div>
        """, unsafe_allow_html=True)

if not EXCHANGE_KEY:
    st.caption("💡 상위 폴더의 `.env` 파일에 `EXCHANGE_RATE_API_KEY`를 설정하시면 실시간 환율이 연동됩니다.")