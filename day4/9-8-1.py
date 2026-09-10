"""
raw_trade_data.csv 무역 데이터 분석 및 시각화 대시보드
실행방법: streamlit run day4/9-8-1.py
"""
# 수정 ver.1

import os
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime

# 1. 페이지 설정 및 제목
st.set_page_config(
    page_title="글로벌 무역 데이터 분석 대시보드",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 한글 폰트 설정 (Windows 환경 대응)
try:
    plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams['axes.unicode_minus'] = False
except Exception:
    pass

st.title("🚢 글로벌 무역 데이터 분석 대시보드")
st.caption("common/raw_trade_data.csv 파일을 분석하여 국가별/품목별 무역 흐름과 트렌드를 시각화합니다.")

# 2. 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
    # 경로 찾기 (스크립트 위치 기준 및 실행 경로 기준 둘 다 지원)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(current_dir, "..", "common", "raw_trade_data.csv"),
        os.path.join("common", "raw_trade_data.csv"),
        "raw_trade_data.csv"
    ]
    
    csv_path = None
    for path in possible_paths:
        if os.path.exists(path):
            csv_path = path
            break
            
    if csv_path is None:
        return None
        
    df = pd.read_csv(csv_path)
    # 날짜 컬럼을 datetime형으로 변환
    df['날짜'] = pd.to_datetime(df['날짜'])
    return df

raw_df = load_data()

if raw_df is None:
    st.error("❌ 'raw_trade_data.csv' 파일을 찾을 수 없습니다.")
    st.info("파일이 'common/raw_trade_data.csv' 경로에 존재하는지 확인해주세요.")
    st.stop()

# 3. 사이드바 - 전처리 설정 및 필터
st.sidebar.header("🛠️ 대시보드 설정")

# 결측치 처리 선택
st.sidebar.subheader("1. 데이터 전처리")
missing_method = st.sidebar.selectbox(
    "중량(중량) 결측치 처리 방식",
    ["중위값(Median) 대체 (권장)", "평균값(Mean) 대체", "0으로 대체", "결측치 행 제거"]
)

# 데이터 복사본 생성 후 결측치 처리
df = raw_df.copy()
nan_count = df['중량'].isnull().sum()

if nan_count > 0:
    if missing_method == "중위값(Median) 대체 (권장)":
        median_val = df['중량'].median()
        df['중량'] = df['중량'].fillna(median_val)
    elif missing_method == "평균값(Mean) 대체":
        mean_val = df['중량'].mean()
        df['중량'] = df['중량'].fillna(mean_val)
    elif missing_method == "0으로 대체":
        df['중량'] = df['중량'].fillna(0)
    elif missing_method == "결측치 행 제거":
        df = df.dropna(subset=['중량'])

st.sidebar.subheader("2. 데이터 필터링")

# 날짜 필터
min_date = df['날짜'].min().to_pydatetime()
max_date = df['날짜'].max().to_pydatetime()
selected_date_range = st.sidebar.slider(
    "조회 기간 설정",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)

# 국가 필터 (다중 선택)
all_countries = sorted(df['국가명'].unique().tolist())
selected_countries = st.sidebar.multiselect(
    "국가 선택 (선택 안 하면 전체)",
    all_countries,
    default=[]
)

# 품목 필터 (다중 선택)
all_items = sorted(df['품목명'].unique().tolist())
selected_items = st.sidebar.multiselect(
    "품목 선택 (선택 안 하면 전체)",
    all_items,
    default=[]
)

# 수출입 구분 필터 (라디오 버튼)
trade_type = st.sidebar.radio(
    "수출입 구분",
    ["전체", "Export (수출)", "Import (수입)"]
)

# --- 필터 적용 ---
filtered_df = df.copy()

# 날짜 필터 적용
filtered_df = filtered_df[
    (filtered_df['날짜'] >= selected_date_range[0]) & 
    (filtered_df['날짜'] <= selected_date_range[1])
]

# 국가 필터 적용
if selected_countries:
    filtered_df = filtered_df[filtered_df['국가명'].isin(selected_countries)]

# 품목 필터 적용
if selected_items:
    filtered_df = filtered_df[filtered_df['품목명'].isin(selected_items)]

# 수출입 구분 필터 적용
if trade_type == "Export (수출)":
    filtered_df = filtered_df[filtered_df['수출입구분'] == 'Export']
elif trade_type == "Import (수입)":
    filtered_df = filtered_df[filtered_df['수출입구분'] == 'Import']


# 4. 상단 요약 지표 (KPI) 영역
st.header("📊 무역 현황 요약 지표")

# 전체 데이터 기준이 아니라 '필터링된 데이터' 기준 지표 계산
total_records = len(filtered_df)

# 수출 데이터만 분리하여 계산
export_df = filtered_df[filtered_df['수출입구분'] == 'Export']
total_export_amt = export_df['수출금액'].sum()
total_export_weight = export_df['중량'].sum()

# 수입 데이터만 분리하여 계산
import_df = filtered_df[filtered_df['수출입구분'] == 'Import']
total_import_weight = import_df['중량'].sum()

# 평균 단가 (수출금액 / 수출중량)
avg_export_unit_price = total_export_amt / total_export_weight if total_export_weight > 0 else 0

# 메트릭 카드 배치
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="총 수출금액",
        value=f"${total_export_amt:,.0f}" if total_export_amt < 1000000 else f"${total_export_amt/1e8:,.2f} 억 달러",
        help="선택한 필터 조건 내의 수출금액 합계입니다."
    )

with col2:
    st.metric(
        label="총 수출중량",
        value=f"{total_export_weight:,.2f} 톤",
        help="선택한 필터 조건 내의 수출물량(중량) 합계입니다."
    )

with col3:
    st.metric(
        label="총 수입중량",
        value=f"{total_import_weight:,.2f} 톤",
        help="선택한 필터 조건 내의 수입물량(중량) 합계입니다."
    )

with col4:
    st.metric(
        label="평균 수출 단가 (중량당)",
        value=f"${avg_export_unit_price:,.2f} / 톤",
        help="총 수출금액을 총 수출중량으로 나눈 값입니다."
    )

st.divider()

# 5. 탭 구성
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 무역 현황 분석", 
    "📈 국가/품목별 세부 분석", 
    "📅 시계열 추이 분석", 
    "🔍 데이터 분석 및 다운로드"
])

# --- Tab 1: 무역 현황 분석 ---
with tab1:
    st.subheader("💡 분석 하이라이트")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.write("#### 🌍 국가별 수출액 비율")
        if len(export_df) > 0:
            country_export = export_df.groupby('국가명')['수출금액'].sum().sort_values(ascending=False)
            
            fig, ax = plt.subplots(figsize=(6, 5))
            country_export.plot(kind='pie', autopct='%1.1f%%', startangle=90, 
                                colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
                                ax=ax, wedgeprops={'edgecolor': 'w'})
            ax.set_ylabel("")
            ax.set_title("국가별 수출액 비중", fontsize=14, weight='bold')
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.warning("선택된 필터 조건에 해당하는 수출 데이터가 없습니다.")

    with col_right:
        st.write("#### 📦 품목별 수출액 비율")
        if len(export_df) > 0:
            item_export = export_df.groupby('품목명')['수출금액'].sum().sort_values(ascending=False)
            
            fig, ax = plt.subplots(figsize=(6, 5))
            item_export.plot(kind='pie', autopct='%1.1f%%', startangle=140,
                              colors=['#2bc0e4', '#eaecc6', '#ffb347', '#ffcc00'],
                              ax=ax, wedgeprops={'edgecolor': 'w'})
            ax.set_ylabel("")
            ax.set_title("품목별 수출액 비중", fontsize=14, weight='bold')
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.warning("선택된 필터 조건에 해당하는 수출 데이터가 없습니다.")

# --- Tab 2: 국가/품목별 세부 분석 ---
with tab2:
    st.subheader("📈 국가 및 품목별 정밀 분석")
    col_sec1, col_sec2 = st.columns(2)
    
    with col_sec1:
        st.write("#### 🏢 품목별 수출금액 및 평균 단가")
        if len(export_df) > 0:
            item_stats = export_df.groupby('품목명').agg(
                수출금액=('수출금액', 'sum'),
                중량=('중량', 'sum')
            )
            item_stats['평균단가'] = item_stats['수출금액'] / item_stats['중량']
            
            fig, ax1 = plt.subplots(figsize=(8, 6))
            ax2 = ax1.twinx()
            
            item_stats['수출금액'].plot(kind='bar', ax=ax1, color='#4F81BD', position=1, width=0.3, label='수출금액 (좌)')
            item_stats['평균단가'].plot(kind='line', ax=ax2, color='#C0504D', marker='o', linewidth=2, label='평균단가 (우)')
            
            ax1.set_ylabel("수출금액 ($)", color='#4F81BD')
            ax2.set_ylabel("평균단가 ($/톤)", color='#C0504D')
            ax1.set_title("품목별 수출금액 및 평균단가 비교", fontsize=14, weight='bold')
            ax1.set_xticklabels(item_stats.index, rotation=0)
            
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.warning("분석할 수출 데이터가 없습니다.")

    with col_sec2:
        st.write("#### ⚖️ 국가별 수출입 중량 비교")
        country_weight = filtered_df.groupby(['국가명', '수출입구분'])['중량'].sum().unstack().fillna(0)
        
        if not country_weight.empty:
            fig, ax = plt.subplots(figsize=(8, 6))
            country_weight.plot(kind='bar', ax=ax, color=['#4682B4', '#CD5C5C'], width=0.6)
            ax.set_ylabel("중량 (톤)")
            ax.set_xlabel("국가명")
            ax.set_title("국가별 수출 및 수입 물동량(중량)", fontsize=14, weight='bold')
            ax.set_xticklabels(country_weight.index, rotation=0)
            ax.legend(["Export (수출)", "Import (수입)"])
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.warning("표시할 수출입 중량 데이터가 없습니다.")

# --- Tab 3: 시계열 추이 분석 ---
with tab3:
    st.subheader("📅 무역 흐름 시계열 트렌드 분석")
    
    ts_df = filtered_df.copy()
    ts_df['년월'] = ts_df['날짜'].dt.to_period('M')
    
    monthly_stats = ts_df.groupby(['년월', '수출입구분']).agg(
        수출금액=('수출금액', 'sum'),
        중량=('중량', 'sum')
    ).unstack().fillna(0)
    
    if not monthly_stats.empty:
        st.write("#### 📈 월별 수출금액 변동 추이")
        
        fig, ax = plt.subplots(figsize=(12, 5))
        
        if 'Export' in monthly_stats['수출금액'].columns:
            monthly_export_amt = monthly_stats['수출금액']['Export']
            if monthly_export_amt.sum() > 0:
                x_labels = [str(x) for x in monthly_export_amt.index]
                ax.plot(x_labels, monthly_export_amt, color='#E46C0A', marker='o', linewidth=2, label='수출금액')
                ax.set_title("월별 수출금액 트렌드", fontsize=14, weight='bold')
                ax.set_xlabel("년월")
                ax.set_ylabel("수출금액 ($)")
                
                if len(x_labels) > 12:
                    plt.xticks(range(0, len(x_labels), 3), x_labels[::3], rotation=45)
                else:
                    plt.xticks(rotation=45)
                    
                ax.grid(True, linestyle='--', alpha=0.5)
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("선택된 필터 하에 수출금액 데이터가 없습니다.")
        else:
            st.info("선택된 필터 하에 수출 데이터가 존재하지 않습니다.")
            
        st.divider()
        
        st.write("#### ⚖️ 월별 수출 및 수입 중량 추이")
        fig, ax = plt.subplots(figsize=(12, 5))
        
        monthly_export_wt = monthly_stats['중량']['Export'] if 'Export' in monthly_stats['중량'].columns else pd.Series(dtype=float)
        monthly_import_wt = monthly_stats['중량']['Import'] if 'Import' in monthly_stats['중량'].columns else pd.Series(dtype=float)
        
        x_labels = [str(x) for x in monthly_stats.index]
        
        if not monthly_export_wt.empty and monthly_export_wt.sum() > 0:
            ax.plot(x_labels, monthly_export_wt, color='#4F81BD', marker='s', linestyle='-', linewidth=2, label='수출 중량 (Export)')
        if not monthly_import_wt.empty and monthly_import_wt.sum() > 0:
            ax.plot(x_labels, monthly_import_wt, color='#C0504D', marker='^', linestyle='--', linewidth=2, label='수입 중량 (Import)')
            
        ax.set_title("월별 수출입 중량(물동량) 추이", fontsize=14, weight='bold')
        ax.set_xlabel("년월")
        ax.set_ylabel("중량 (톤)")
        
        if len(x_labels) > 12:
            plt.xticks(range(0, len(x_labels), 3), x_labels[::3], rotation=45)
        else:
            plt.xticks(rotation=45)
            
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.warning("시계열 분석을 위한 데이터가 부족합니다.")

# --- Tab 4: 데이터 분석 및 다운로드 ---
with tab4:
    st.subheader("🔍 데이터 정밀 탐색 및 내보내기")
    
    st.write(f"ℹ️ **원본 데이터 결측치 정보:** 총 1,200행 중 `중량` 컬럼에 **{nan_count}개**의 결측치(NaN)가 존재합니다.")
    st.write(f"현재 선택된 처리 방식 (**{missing_method}**)으로 보정되었으며, 필터링 후 현재 테이블에는 **{len(filtered_df):,}행**이 존재합니다.")
    
    st.write("#### 📊 기초 통계 요약")
    st.dataframe(filtered_df.describe(), use_container_width=True)
    
    st.write("#### 📋 필터링된 무역 데이터 목록 (최대 100개 행 미리보기)")
    display_df = filtered_df.copy()
    display_df['날짜'] = display_df['날짜'].dt.strftime('%Y-%m-%d')
    st.dataframe(display_df.head(100), use_container_width=True)
    
    csv_data = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 필터링된 데이터 CSV 다운로드",
        data=csv_data,
        file_name=f"filtered_trade_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **대시보드 사용 가이드**\n"
    "1. 왼쪽 사이드바에서 결측치 보정 방식과 데이터 필터를 조정하세요.\n"
    "2. 상단의 KPI 카드로 요약된 수출입 금액과 물량을 한눈에 확인하세요.\n"
    "3. 각 탭을 클릭하여 시각화된 차트와 트렌드, 상세 통계를 확인하세요."
)
