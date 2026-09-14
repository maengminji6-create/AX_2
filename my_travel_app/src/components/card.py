import streamlit as st

# 국가별 감성 테마 스타일 정의
THEMES = {
    "대한민국": {
        "gradient": "linear-gradient(135deg, #ffe4e6 0%, #ffffff 50%, #dbeafe 100%)",
        "title_color": "#1e3a8a",
        "desc_color": "#334155",
        "badge_bg": "#ffffff",
        "badge_border": "#cbd5e1",
        "badge_text": "#e11d48",
        "tagline": "HARMONY & VIBRANT CULTURE",
        "shadow": "rgba(225, 29, 72, 0.12)"
    },
    "일본": {
        "gradient": "linear-gradient(120deg, #fdf2f8 0%, #fce7f3 50%, #fff1f2 100%)",
        "title_color": "#be185d",
        "desc_color": "#475569",
        "badge_bg": "#ffffff",
        "badge_border": "#f472b6",
        "badge_text": "#db2777",
        "tagline": "TRADITION MEETS FUTURE",
        "shadow": "rgba(236, 72, 153, 0.15)"
    },
    "중국": {
        "gradient": "linear-gradient(135deg, #ffe4e6 0%, #fecdd3 45%, #fed7aa 100%)",
        "title_color": "#9f1239",
        "desc_color": "#475569",
        "badge_bg": "#ffffff",
        "badge_border": "#fb7185",
        "badge_text": "#be123c",
        "tagline": "GREAT DYNASTY & HERITAGE",
        "shadow": "rgba(225, 29, 72, 0.16)"
    },
    "미국": {
        "gradient": "linear-gradient(120deg, #ecfeff 0%, #cffafe 50%, #e0e7ff 100%)",
        "title_color": "#0e7490",
        "desc_color": "#334155",
        "badge_bg": "#ffffff",
        "badge_border": "#67e8f9",
        "badge_text": "#0891b2",
        "tagline": "ENDLESS ROAD & NATURE",
        "shadow": "rgba(6, 182, 212, 0.15)"
    }
}

# 고화질 국기 SVG 매핑 (Windows 폰트 깨짐 완벽 방지)
FLAG_SVGS = {
    "대한민국": "https://flagcdn.com/w40/kr.png",
    "일본": "https://flagcdn.com/w40/jp.png",
    "중국": "https://flagcdn.com/w40/cn.png",
    "미국": "https://flagcdn.com/w40/us.png"
}

def inject_custom_styles():
    st.markdown(
        """
        <style>
        /* Pretendard 폰트 및 Google Material Symbols 폰트 강제 로드 */
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

        * {
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif !important;
        }

        /* 1. 사이드바 접기/열기 버튼 아이콘 정상화 (keyboard_double... 텍스트 깨짐 해결) */
        [data-testid="stSidebarCollapseButton"] span,
        [data-testid="collapsedControl"] span {
            font-family: 'Material Symbols Rounded' !important;
            font-size: 1.3rem !important;
            line-height: 1 !important;
        }

        /* 2. 상단 히어로 배너 */
        .hero-banner {
            border-radius: 24px;
            padding: 38px 36px;
            margin-bottom: 28px;
            border: 1px solid rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            position: relative;
        }

        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.8px;
            border-width: 1px;
            border-style: solid;
            box-shadow: 0 2px 6px rgba(0,0,0,0.03);
            margin-bottom: 14px;
        }

        .hero-badge img {
            border-radius: 3px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.15);
        }

        .hero-title {
            font-size: 2.6rem;
            font-weight: 800;
            letter-spacing: -0.8px;
            margin: 0 0 10px 0;
            line-height: 1.2;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .hero-title img {
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.12);
        }

        .hero-desc {
            font-size: 1.05rem;
            line-height: 1.65;
            font-weight: 500;
            margin: 0;
            max-width: 800px;
        }

        /* 3. 3단 카드 */
        .info-card {
            background: #ffffff;
            border-radius: 18px;
            padding: 22px 24px;
            border: 1px solid #f1f5f9;
            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.03);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .info-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
        }
        .card-label {
            font-size: 0.82rem;
            color: #64748b;
            font-weight: 600;
            margin-bottom: 6px;
        }
        .card-value {
            font-size: 1.18rem;
            font-weight: 700;
            color: #0f172a;
        }

        /* 4. 이미지 갤러리 */
        div[data-testid="stImage"] img {
            border-radius: 16px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
            transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }
        div[data-testid="stImage"] img:hover {
            transform: scale(1.02);
        }

        /* 5. 사이드바 배경 */
        section[data-testid="stSidebar"] {
            background-color: #fafaf9;
            border-right: 1px solid #e7e5e4;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def display_country_details(info, country_name):
    inject_custom_styles()
    
    theme = THEMES.get(country_name, THEMES["대한민국"])
    flag_url = FLAG_SVGS.get(country_name, "")
    
    # 1. 상단 그라디언트 헤더 (배지와 제목 옆에 선명한 국기 이미지 노출)
    st.markdown(
        f"""
        <div class="hero-banner" style="background: {theme['gradient']}; box-shadow: 0 14px 35px {theme['shadow']};">
            <div class="hero-badge" style="background: {theme['badge_bg']}; border-color: {theme['badge_border']}; color: {theme['badge_text']};">
                <img src="{flag_url}" width="18" height="13" alt="{country_name} 국기" />
                <span>{theme['tagline']}</span>
            </div>
            <div class="hero-title" style="color: {theme['title_color']};">
                <img src="{flag_url}" width="42" height="28" alt="{country_name} 국기" />
                <span>{country_name}</span>
            </div>
            <p class="hero-desc" style="color: {theme['desc_color']};">{info['description']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 2. 3단 정보 카드 그리드
    st.markdown("### 🏛️ 핵심 국가 여행 정보")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="card-label">📍 수도</div>
                <div class="card-value">{info['capital']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="card-label">💵 공식 통화</div>
                <div class="card-value">{info['currency']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="card-label">🗣️ 사용 언어</div>
                <div class="card-value">{info['language']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. 공식 관광청 웹사이트 바로가기
    st.markdown("### 🌐 공식 여행 정보 포털")
    st.caption("비자 요건, 관광 명소 코스 및 공식 여행 가이드를 확인하세요.")
    st.link_button(
        label=f"✈️ {info['site_name']} 공식 사이트 방문하기 ↗",
        url=info["official_site"],
        use_container_width=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. 3단 명소 사진 갤러리
    st.markdown(f"### 📸 {country_name} 대표 명소 갤러리")
    st.caption("현지의 대표적인 랜드마크와 분위기를 미리 둘러보세요.")
    
    images = info.get("images", [])
    if images:
        cols = st.columns(len(images), gap="medium")
        for idx, img_data in enumerate(images):
            with cols[idx]:
                st.image(
                    img_data["url"],
                    caption=img_data["caption"],
                    use_container_width=True
                )