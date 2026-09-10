# import io
#import pandas as pd
#import streamlit as st

#st.title("K-pop idol 팔로워 수")

#csv_path = "kpop_idol_followers.csv"
#upload_file = st.file_uploader("kpop_idol_followers.csv 파일을 직접 업로드 할 수 있습니다(선택사항)", type="csv")
#if upload_file is not None:
#    df = pd.read_csv(upload_file)
#else:
#    try:

import io
import pandas as pd
import streamlit as st

st.title("🎤 K-pop 아이돌 팔로워 분석 대시보드")
st.caption("pandas를 활용한 기초 탐색부터 영향력 분석까지")

# 1. 파일 업로더 생성 (수정된 부분)
upload_file = st.file_uploader("K-pop 팔로워 데이터(CSV)를 업로드하세요", type="csv")

# 2. 업로드된 파일이 있으면 pandas로 읽어서 df 변수에 저장 (추가된 부분)
if upload_file is not None:
    df = pd.read_csv(upload_file)
else:
    df = None

# 3. df가 존재할 때만 아래 분석 코드 실행
if df is not None:
    st.divider()
    st.header("📊 2차 데이터 가공: 아이돌 영향력 분석")

    st.subheader("1) 결측치 처리 및 '총 팔로워 수' 계산")
    df_clean = df.fillna(0)
    
    st.write("결측치를 0으로 처리한 데이터 미리보기:")
    st.dataframe(df_clean.head(), use_container_width=True)

    st.subheader("2) 팔로워 수 순위 (Top 10)")
    st.caption("특정 기준(예: 인스타그램 팔로워)으로 데이터를 내림차순 정렬합니다.")
    
    numeric_cols = df_clean.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        sort_target = numeric_cols[0]
        top_10_df = df_clean.sort_values(by=sort_target, ascending=False).head(20)
        st.dataframe(top_10_df, use_container_width=True)
    else:
        st.warning("정렬할 숫자형 데이터가 없습니다.")

    st.subheader("3) 성별 또는 소속사별 필터링")
    st.caption("사용자가 원하는 그룹만 골라서 볼 수 있게 가공합니다.")
    
    if 'Gender' in df_clean.columns:
        selected_gender = st.selectbox("성별을 선택하세요", df_clean['Gender'].unique())
        filtered_df = df_clean[df_clean['Gender'] == selected_gender]
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("💡 성별이나 소속사 컬럼을 활용해 selectbox 필터를 만들어보세요!")

    st.success("데이터 가공 완료! 이제 이 데이터를 바탕으로 차트를 그릴 준비가 되었습니다.")