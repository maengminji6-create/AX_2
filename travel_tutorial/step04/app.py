import streamlit as st

# 1. set_page_config로 함수명 수정
st.set_page_config(page_title="세계 여행 포털", page_icon="🌎", layout="wide")

# 2. st.Page(대문자) 사용, 유효한 국기 이모지 적용, 파일 경로 오타(.japan.py) 수정
home_page = st.Page("view/home.py", title="홈", icon="🏠", default=True)
usa_page = st.Page("view/usa.py", title="미국", icon="🇺🇸")
jp_page = st.Page("view/japan.py", title="일본", icon="🇯🇵")
cn_page = st.Page("view/china.py", title="중국", icon="🇨🇳")

# 3. 네비게이션 등록 및 실행
pg = st.navigation([home_page, usa_page, jp_page, cn_page])
pg.run()