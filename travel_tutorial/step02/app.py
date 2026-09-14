import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="세계 여행 포털",
    page_icon="🌎",
    layout="wide"
)

# 사이드바 메뉴
st.sidebar.title("🧭 여행지 안내")
menu = st.sidebar.radio("국가를 선택하세요", ["홈 (대한민국)", "미국", "중국", "일본"])

# 메뉴별 화면 구성
if menu == "홈 (대한민국)":
    st.title("🇰🇷 대한민국 (Republic of Korea)")
    st.markdown("---")
    st.subheader("사계절의 아름다움과 전통, 현대가 공존하는 곳")
    st.write(
        """
        대한민국은 유구한 역사 속의 고궁과 현대적인 도심이 공존하는 매력적인 여행지입니다.
        다채로운 사계절 풍경, 풍부한 문화유산, 세계적인 K-컬처와 먹거리를 경험해보세요.
        """
    )
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="수도", value="서울")
    col2.metric(label="언어", value="한국어")
    col3.metric(label="통화", value="KRW (₩)")
    
    st.markdown("### 📍 추천 명소")
    st.markdown("- **경복궁 & 북촌한옥마을**: 고즈넉한 한국 전통의 멋")
    st.markdown("- **제주도**: 유네스코 세계자연유산의 화산섬")
    st.markdown("- **부산 해운대 & 광안리**: 역동적인 해변과 야경")
    
    st.write("")
    st.link_button("🌐 대한민국 구석구석 (한국관광공사)", "https://korean.visitkorea.or.kr")

elif menu == "미국":
    st.title("🇺🇸 미국 (United States of America)")
    st.markdown("---")
    st.subheader("광활한 대자연과 세계적인 대도시의 만남")
    st.write(
        """
        북아메리카 대륙을 아우르는 광활한 영토에 웅장한 국립공원부터 세계 경제와 문화의 중심지까지,
        끝없는 다양성을 품고 있는 기회의 땅입니다.
        """
    )
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="수도", value="워싱턴 D.C.")
    col2.metric(label="언어", value="영어")
    col3.metric(label="통화", value="USD ($)")
    
    st.markdown("### 📍 추천 명소")
    st.markdown("- **뉴욕 타임스퀘어 & 센트럴파크**: 세계의 교차로")
    st.markdown("- **그랜드 캐니언**: 대자연의 경이로움을 담은 협곡")
    st.markdown("- **하와이 와이키키**: 최고의 휴양과 서핑 파라다이스")
    
    st.write("")
    st.link_button("🌐 GoUSA 공식 관광청 바로가기", "https://www.gousa.or.kr")

elif menu == "중국":
    st.title("🇨🇳 중국 (People's Republic of China)")
    st.markdown("---")
    st.subheader("수천 년의 찬란한 역사와 거대한 풍경")
    st.write(
        """
        장구한 역사 속 문화유산과 눈부시게 발전한 메가시티가 공존합니다. 
        세계 7대 불가사의인 만리장성부터 이색적인 자연 풍광까지 풍부한 여행 경험을 선사합니다.
        """
    )
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="수도", value="베이징")
    col2.metric(label="언어", value="중국어 (표준어)")
    col3.metric(label="통화", value="CNY (¥)")
    
    st.markdown("### 📍 추천 명소")
    st.markdown("- **만리장성 & 자금성**: 중국 제국의 장엄한 흔적")
    st.markdown("- **상하이 와이탄**: 근현대 건축과 현대식 스카이라인의 조화")
    st.markdown("- **장가계(장자제)**: 영화 아바타의 모티브가 된 기암괴석")
    
    st.write("")
    st.link_button("🌐 중국문화관광부 공식 포털", "http://zwgk.mct.gov.cn")

elif menu == "일본":
    st.title("🇯🇵 일본 (Japan)")
    st.markdown("---")
    st.subheader("정갈한 문화와 사계절의 낭만이 머무는 섬나라")
    st.write(
        """
        고유의 온천 문화, 풍부한 미식, 고즈넉한 신사와 최첨단 도심 문화가 어우러져 있습니다.
        지역마다 뚜렷한 개성과 사계절의 섬세한 정취를 만끽할 수 있습니다.
        """
    )
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="수도", value="도쿄")
    col2.metric(label="언어", value="일본어")
    col3.metric(label="통화", value="JPY (¥)")
    
    st.markdown("### 📍 추천 명소")
    st.markdown("- **도쿄 시부야 & 신주쿠**: 현대 대도시 트렌드의 중심")
    st.markdown("- **교토 청수사(기요미즈데라)**: 전통 목조 건축과 붉은 단풍")
    st.markdown("- **홋카이도 삿포로 & 비에이**: 순백의 설경과 계절별 꽃밭")
    
    st.write("")
    st.link_button("🌐 일본정부관광국 (JNTO) 바로가기", "https://www.japan.travel/ko/kr/")