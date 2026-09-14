import streamlit as st
from src.data.country_info import COUNTRIES
from src.components.card import display_country_details

# 페이지 설정
st.set_page_config(
    page_title="Wanderlust | 글로벌 여행 가이드",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사이드바 감성 브랜딩 및 내비게이션
with st.sidebar:
    st.markdown("## 🧭 Wanderlust")
    st.markdown("##### 프리미엄 글로벌 여행 가이드")
    st.caption("가고 싶은 여행지를 선택해 보세요.")
    st.markdown("---")
    
    country_list = list(COUNTRIES.keys())
    
    # 윈도우 폰트 깨짐 방지를 위해 깔끔한 한글 레이블과 심플 불릿 스타일 적용
    selected_country = st.radio(
        "목적지 선택",
        options=country_list,
        index=0,
        format_func=lambda c: f"•  {c}"
    )
    
    st.markdown("---")
    st.caption("© 2026 Wanderlust Travel Guide. All rights reserved.")

# 메인 콘텐츠 출력
info = COUNTRIES[selected_country]
display_country_details(info, selected_country)