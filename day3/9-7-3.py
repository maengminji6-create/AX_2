"""
타이타닉 데이터 필터링, 결측치 정리
age(나이)가 35살 이상인 승객 필터링
성별별로 필터링
titanic_cleaned.csv로 저장
실행방법 streamlit run 9-7-3.py
"""

import pandas as pd
import streamlit as st


st.title("타이타닉 데이터 필터링 & 결측치 정리")

csv_path = "Titanic.csv"


try:
    df = pd.read_csv(csv_path)

except FileNotFoundError:
    st.error("❌ Titanic.csv 파일을 찾을 수가 없습니다")

else: 
    st.metric("원본 데이터 행 개수", f"{len(df)}행")

    st.markdown("---")

    #age 35세 이상 필터링
    st.subheader("1) 나이 35세 이상 승객")

    over_35 = df[df["Age"]>=35]
    st.write(f"나이 35세 이상 승객수 : **{len(over_35)}명**")
    st.dataframe(over_35[["Name","Sex","Age"]].head())

    # 성별 여자 남자 필터링 2컬럼 사용
    st.subheader("2) 성별 필터링 결과")
    female_df = df[df["Sex"] == "female"]
    male_df = df[df["Sex"] == "male"]

    col1,col2 = st.columns(2)
    with col1:
        st.metric("여성승객수",f"{len(female_df)}명") 
    with col2:
        st.metric("남성승객수",f"{len(male_df)}명")

    st.markdown("---")

    st.subheader("3) 35세 이상 & 여성 승객")
    over_35_female = df[(df["Age"] >= 35) & (df["Sex"] == "female")]
    st.write(f"35세 이상 여성 수 : **{len(over_35_female)}명**")

    st.markdown("---")


    # 결측치(NaN) 확인 및 dropna 처리
    st.subheader("4) Age 결측치 처리")
    missing_age_count = df["Age"].isna().sum() #isna()는 결측치면 True를 반환한다
    st.write(f"Age의 열의 결측치 개수: **{missing_age_count}개**")

    df_clean = df.dropna(subset=["Age"])
    col1,col2 = st.columns(2)
    with col1:
        st.metric("제거 전", f"{len(df)}행")
    with col2:
        st.metric("제거 후", f"{len(df_clean)}행")

    # 정리된 데이터를 csv 파일로 저장
    output_path = "titanic_cleaned.csv"
    df_clean.to_csv(output_path, index=False)
    st.success("파일을 저장했습니다")
    st.dataframe(df_clean.head(), use_container_width=True)
    