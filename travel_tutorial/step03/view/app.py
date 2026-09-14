import streamlit as st

st.set_page_config(page_title="세계 여행 포털", page_icon="🌎")

# view/ 를 제거하고 파일명만 입력
home_page = st.Page("home.py", title="홈", icon="🏠", default=True)
usa = st.Page("usa.py", title="미국", icon="🇺🇸")
china = st.Page("china.py", title="중국", icon="🇨🇳")
japan = st.Page("japan.py", title="일본", icon="🇯🇵")

# 네비게이션
pg = st.navigation([home_page, usa, china, japan])
pg.run()