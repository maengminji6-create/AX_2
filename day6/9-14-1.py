import os
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

# Streamlit 기본 설정
st.set_page_config(page_title="카카오 지도 여행 대시보드", page_icon="🗺️", layout="wide")

# --- [.env 절대 경로 강제 탐색 로직] ---
# 현재 파일 위치를 기준으로 상위 폴더들을 차례대로 탐색
current_file_path = Path(__file__).resolve()
found_env_path = None

for parent in [current_file_path.parent] + list(current_file_path.parents):
    candidate = parent / ".env"
    if candidate.exists() and candidate.is_file():
        found_env_path = candidate
        break

if found_env_path:
    # override=True로 강제 덮어쓰기 로드
    load_dotenv(dotenv_path=found_env_path, override=True)

# 환경 변수 확인
KAKAO_API_KEY = os.getenv("KAKAO_MAP_API_KEY")

# 만약 키를 여전히 못 찾았다면 상세 진단 정보 출력
if not KAKAO_API_KEY:
    st.error("🚨 `.env` 파일에서 `KAKAO_MAP_API_KEY`를 읽어오지 못했습니다.")
    
    st.markdown("### 🔍 원인 진단")
    if found_env_path:
        st.warning(f"✅ `.env` 파일은 다음 위치에서 정상 발견되었습니다:\n`{found_env_path}`")
        st.write("👉 **하지만 파일 안에 `KAKAO_MAP_API_KEY` 변수명이 없거나 비어 있습니다.**")
        
        # 파일 내용 직접 읽어보기 (오타 확인용)
        try:
            with open(found_env_path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith("#")]
            st.info(f"현재 `.env`에 적힌 변수 목록: `{[line.split('=')[0] for line in lines]}`")
        except Exception as e:
            st.write(f"파일 읽기 오류: {e}")
    else:
        st.error("❌ 상위 폴더 어디에서도 `.env` 파일을 찾지 못했습니다.")
        st.write(f"현재 실행 중인 파일의 실제 위치: `{current_file_path}`")

    st.stop()

# --- 정상적으로 키가 로드된 경우 지도 화면 출력 ---
st.title("🗺️ 카카오 지도 여행 뷰어")

# 사이드바 설정
st.sidebar.header("📍 여행지 위치 설정")
lat = st.sidebar.number_input("위도 (Latitude)", value=37.5665, format="%.6f")
lng = st.sidebar.number_input("경도 (Longitude)", value=126.9780, format="%.6f")
level = st.sidebar.slider("지도 확대 레벨", min_value=1, max_value=14, value=3)

kakao_map_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>Kakao Map</title>
    <script type="text/javascript" src="https://dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_API_KEY}&autoload=false"></script>
    <style>
        html, body {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; font-family: sans-serif; }}
        #map {{ width: 100%; height: 100%; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.08); }}
        .custom-overlay {{ background: #fff; border: 1px solid #ccc; border-radius: 8px; padding: 6px 12px; font-size: 13px; font-weight: bold; }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        kakao.maps.load(function() {{
            var container = document.getElementById('map');
            var options = {{
                center: new kakao.maps.LatLng({lat}, {lng}),
                level: {level}
            }};
            var map = new kakao.maps.Map(container, options);

            var zoomControl = new kakao.maps.ZoomControl();
            map.addControl(zoomControl, kakao.maps.ControlPosition.RIGHT);

            var marker = new kakao.maps.Marker({{
                position: new kakao.maps.LatLng({lat}, {lng})
            }});
            marker.setMap(map);

            var customOverlay = new kakao.maps.CustomOverlay({{
                position: new kakao.maps.LatLng({lat}, {lng}),
                content: '<div class="custom-overlay">📍 선택된 위치</div>',
                yAnchor: 2.2
            }});
            customOverlay.setMap(map);
        }});
    </script>
</body>
</html>
"""

components.html(kakao_map_html, height=550)
st.success("✅ 카카오 지도가 정상적으로 연결되었습니다!")