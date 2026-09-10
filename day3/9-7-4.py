# 인코딩 자동 감지 + 한글 폰트 막대그래프
# 여러 인코딩("utf-8-sig","cp949", "euc-kr") 순서대로 시도
# 내가 쓸 폰트 같은 경로에 있어야 함
# 객실 등급별 생존율 막대 그래프 생성후 그림으로 저장  chart.png
# 실행 streamlit run 9-7-4.py

import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib import font_manager

st.title("인코딩 자동 감지 + 한글 폰트 막대 그래프(Taitanic 연습)")
st.caption("여러 인코딩을 순서대로 시도해서 파일을 읽고,객실등급별 생존율을 그래프로 그립니다.")

csv_path = os.path.join(os.path.dirname(__file__),"Titanic_cleaned.csv")
font_path = os.path.join(os.path.dirname(__file__),"ongle.ttf")

def read_csv_with_auto(file_path):
    encodings = ["utf-8-sig", "cp949", "euc-kr"]
    
    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            st.success(f"✅ '{encoding}' 인코딩으로 파일을 성공적으로 읽었습니다.")
            return df
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            st.error("파일을 찾을 수 없습니다. 경로와 파일명을 다시 확인해주세요.")
            return None
        except Exception as e:
            st.error(f"알 수 없는 오류가 발생했습니다: {e}")
            return None
            
    st.error("모든 인코딩 시도에 실패했습니다. 파일의 인코딩을 확인해주세요.")
    return None

df = read_csv_with_auto(csv_path)

if df is not None:
    st.subheader("데이터 미리보기")
    st.dataframe(df.head())


# 인코딩 자동 감지로 csv읽기
st.subheader("1) 인코딩 자동 감지")
df= read_csv_with_auto(csv_path)

st.markdown("---")
# 객실 등급(pclass) 별 생존율집계
# Survived 사망0/ 생존1 등급별 평균을 내면
# 그대로가 등급의 생존 비율이 된다
# 10명 남 3 여자 7
# 100 생존300 300/100 30%

Pclass_survival_rate = df.groupby("Pclass")["Survived"].mean().sort_index()
st.dataframe((Pclass_survival_rate * 100).round(1).rename("생존율(%)"))

# df_df = st.dataframe((Pclass_survival_rate * 100).round(1).rename("생존율(%)"))
# st.write(df_df)

# 차트 그리기

st.markdown("---")
st.subheader("3) 객실등급별 생존율 막대그래프")
try :
    # 폰트 파일이 없으면 FileNotFoundError가 발생
    font_prop = font_manager.FontProperties(fname=font_path)
    # matplotlib font_manager에 폰트를 등록하고, 전역 폰트로 설정
    font_manager.fontManager.addfont(font_path)
    plt.rcParams["font.family"]=font_prop.get_name()
    plt.rcParams['axes.unicode_minus'] = False
    st.write("ComicRelief-Regular 폰트를 적용했습니다")
except FileNotFoundError:
    st.warning("폰트파일을 찾을 수가 없습니다")

fig, ax = plt.subplots(figsize=(8,5))
(Pclass_survival_rate * 100).plot(kind="bar",color="blue",ax=ax)
ax.set_title("객실 등급별 생존율")
ax.set_xlabel("객실등급(Pclass)")
ax.set_ylabel("생존율(%)")

st.pyplot(fig)

output_png = os.path.join(os.path.dirname(__file__),"chart.png")
fig.savefig(output_png)