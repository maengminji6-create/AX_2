import datetime
import os
from pathlib import Path
import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

# 1. 환경변수 탐색
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent

if (parent_dir / ".env").exists():
    load_dotenv(dotenv_path=parent_dir / ".env")
elif (current_dir / ".env").exists():
    load_dotenv(dotenv_path=current_dir / ".env")
else:
    load_dotenv()

API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")

# 2. 페이지 기본 설정
st.set_page_config(
    page_title="FX & Trade Executive Desk",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 3. 로맨틱 소프트 핑크 테마 CSS
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Malgun Gothic", sans-serif;
    }
    .top-status-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 20px;
        background: linear-gradient(135deg, #FFE4E6 0%, #FECDD3 50%, #FBCFE8 100%);
        color: #881337;
        border-radius: 12px;
        margin-bottom: 24px;
        font-size: 0.9rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(244, 63, 94, 0.08);
    }
    .live-pulse {
        display: inline-block;
        width: 9px;
        height: 9px;
        background-color: #F43F5E;
        border-radius: 50%;
        margin-right: 6px;
        box-shadow: 0 0 8px #F43F5E;
    }
    .cost-card {
        background: #FFFFFF;
        border: 1px solid #FFE4E6;
        border-radius: 14px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(244, 63, 94, 0.04);
    }
    .cost-title {
        font-size: 0.82rem;
        font-weight: 600;
        color: #9F1239;
    }
    .cost-val {
        font-size: 1.4rem;
        font-weight: 800;
        color: #4C0519;
        margin-top: 4px;
    }
    .total-banner {
        background: linear-gradient(135deg, #FB7185 0%, #F43F5E 50%, #E11D48 100%);
        color: #FFFFFF;
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(244, 63, 94, 0.2);
        margin: 15px 0;
    }
    .total-title {
        font-size: 0.95rem;
        color: #FFE4E6;
        font-weight: 600;
    }
    .total-val {
        font-size: 2.3rem;
        font-weight: 900;
        color: #FFFFFF;
    }
    .chart-container-card {
        background: #FFFFFF;
        border: 1px solid #FFE4E6;
        border-radius: 14px;
        padding: 20px 22px;
        box-shadow: 0 4px 12px rgba(244, 63, 94, 0.05);
        margin-top: 10px;
    }
    .gauge-row {
        margin-bottom: 12px;
    }
    .gauge-labels {
        display: flex;
        justify-content: space-between;
        font-size: 0.84rem;
        font-weight: 600;
        color: #475569;
        margin-bottom: 4px;
    }
    .gauge-bar-bg {
        width: 100%;
        height: 10px;
        background-color: #FFF1F2;
        border-radius: 999px;
        overflow: hidden;
    }
    .gauge-bar-fill {
        height: 100%;
        border-radius: 999px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 4. 지원 통화 목록
CURRENCY_DATA = {
    "USD": {"name": "US Dollar", "flag": "🇺🇸"},
    "KRW": {"name": "Korean Won", "flag": "🇰🇷"},
    "EUR": {"name": "Euro", "flag": "🇪🇺"},
    "JPY": {"name": "Japanese Yen", "flag": "🇯🇵"},
    "CNY": {"name": "Chinese Yuan", "flag": "🇨🇳"},
    "GBP": {"name": "British Pound", "flag": "🇬🇧"},
}

if "from_curr" not in st.session_state:
    st.session_state.from_curr = "USD"
if "to_curr" not in st.session_state:
    st.session_state.to_curr = "KRW"
if "amount" not in st.session_state:
    st.session_state.amount = 10000.0


# 5. 실시간 환율 API 호출
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_api_rates(base="USD"):
    fallback_rates = {
        "USD": 1.0,
        "KRW": 1338.80,
        "EUR": 0.86,
        "JPY": 153.40,
        "CNY": 6.72,
        "GBP": 0.74,
    }
    if not API_KEY or API_KEY in ["your_key", ""]:
        return fallback_rates, "기본 환율 모드 (.env 미설정)", "Standby"
    try:
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{base}"
        res = requests.get(url, timeout=4)
        data = res.json()
        if data.get("result") == "success":
            return (
                data.get("conversion_rates", fallback_rates),
                data.get("time_last_update_utc", "최신"),
                "Online",
            )
        return fallback_rates, "API 제한 (폴백 모드)", "Standby"
    except Exception:
        return fallback_rates, "네트워크 지연 (폴백 모드)", "Standby"


rates, last_updated, conn_status = fetch_api_rates("USD")


def calculate_rate(f_sym, t_sym):
    r_f = rates.get(f_sym, 1.0)
    r_t = rates.get(t_sym, 1.0)
    if r_f <= 0:
        return 1.0
    return r_t / r_f


# 6. 실제 과거 환율 API 호출 (Frankfurter - ECB 공시 실제 데이터)
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_real_historical_rates(base="USD", target="KRW", days=30):
    """실제 오픈 공공 금융 API로부터 과거 n일간의 실제 환율 데이터를 조회합니다."""
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days)

    # Frankfurter API는 EUR/USD/GBP/JPY/KRW 등 공식 환율 시계열 무료 제공
    url = f"https://api.frankfurter.app/{start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}?from={base}&to={target}"
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        data = res.json()
        rates_dict = data.get("rates", {})
        if rates_dict:
            df = pd.DataFrame(
                [
                    {
                        "Date": pd.to_datetime(d),
                        f"{base}/{target}": val.get(target),
                    }
                    for d, val in rates_dict.items()
                ]
            )
            df = df.sort_values("Date").set_index("Date")
            return df
    except Exception:
        pass

    # 통신 실패 시 단일 기준점 데이터 반환
    cur_val = calculate_rate(base, target)
    return pd.DataFrame(
        {f"{base}/{target}": [cur_val]}, index=[pd.to_datetime(end_date)]
    )


# 7. 상단 인디케이터
st.markdown(
    f"""
    <div class="top-status-bar">
        <div>
            <span class="live-pulse"></span>
            <b>FX & TRADE EXECUTIVE DESK</b> &nbsp;|&nbsp; <span>해외소싱 수입원가 및 실데이터 환율 분석</span>
        </div>
        <div>
            상태: <b>{conn_status}</b> &nbsp;|&nbsp; 데이터 기준: <b>{last_updated}</b>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# 8. 사이드바
with st.sidebar:
    st.markdown("### 📌 **Menu**")
    menu = st.radio(
        "메뉴 선택",
        ["Dashboard", "환율 계산기", "환율 추이", "💼 Trade Calculator"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("#### ⭐ **자주 쓰는 통화쌍**")
    preset_pairs = ["USD → KRW", "EUR → KRW", "JPY → KRW", "CNY → KRW"]
    current_pair_str = f"{st.session_state.from_curr} → {st.session_state.to_curr}"
    default_idx = (
        preset_pairs.index(current_pair_str)
        if current_pair_str in preset_pairs
        else 0
    )

    selected_preset = st.radio(
        "통화쌍 프리셋 선택", preset_pairs, index=default_idx
    )
    f_code, t_code = selected_preset.split(" → ")
    if (
        st.session_state.from_curr != f_code
        or st.session_state.to_curr != t_code
    ):
        st.session_state.from_curr = f_code
        st.session_state.to_curr = t_code
        st.rerun()

    st.info(
        f"현재 적용 통화: **{st.session_state.from_curr} → {st.session_state.to_curr}**"
    )

# ========================================================
# [메뉴: Dashboard]
# ========================================================
if menu == "Dashboard":
    st.title("🌸 FX DASHBOARD")
    st.caption("실시간 인터뱅크 환율 데이터와 주요 5대 통화 시장 현황")

    cols = st.columns(5)
    majors = [
        ("USD", 0.31),
        ("EUR", -0.15),
        ("JPY", 0.08),
        ("CNY", 0.12),
        ("GBP", -0.42),
    ]
    for idx, (sym, delta) in enumerate(majors):
        with cols[idx]:
            c_rate = calculate_rate(sym, "KRW")
            r_disp = (c_rate * 100) if sym == "JPY" else c_rate
            st.metric(
                f"{CURRENCY_DATA[sym]['flag']} {sym}/KRW",
                f"{r_disp:,.2f}",
                f"{delta:+.2f}%",
            )

    st.write("")
    d1, d2 = st.columns([1, 1.2], gap="large")
    with d1:
        st.subheader("⚡ 통화 간 환율 계산기")
        amt_in = st.number_input(
            "금액", value=st.session_state.amount, step=100.0
        )
        st.session_state.amount = amt_in
        active_r = calculate_rate(
            st.session_state.from_curr, st.session_state.to_curr
        )
        converted = amt_in * active_r

        st.markdown(
            f"""
            <div class="total-banner">
                <div class="total-title">적용 환율: 1 {st.session_state.from_curr} = {active_r:,.4f} {st.session_state.to_curr}</div>
                <div class="total-val">{converted:,.2f} {st.session_state.to_curr}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
    with d2:
        st.subheader("📈 USD / KRW 실제 30일 변동 추이 (API)")
        # 실제 Frankfurter API 시계열 호출
        df_real_chart = fetch_real_historical_rates("USD", "KRW", days=30)
        st.line_chart(df_real_chart, height=240, color="#F43F5E")

# ========================================================
# [메뉴: 환율 계산기]
# ========================================================
elif menu == "환율 계산기":
    st.title("💱 전문 통화 간 환율 계산기")
    c1, c2 = st.columns(2)
    with c1:
        f_cur = st.selectbox(
            "보내는 통화",
            list(CURRENCY_DATA.keys()),
            index=list(CURRENCY_DATA.keys()).index(st.session_state.from_curr),
        )
        calc_amt = st.number_input(
            "금액 입력", value=st.session_state.amount, format="%.2f"
        )
    with c2:
        t_cur = st.selectbox(
            "받는 통화",
            list(CURRENCY_DATA.keys()),
            index=list(CURRENCY_DATA.keys()).index(st.session_state.to_curr),
        )
    r_val = calculate_rate(f_cur, t_cur)
    st.markdown(
        f"""
        <div class="total-banner">
            <div class="total-title">1 {f_cur} = {r_val:,.4f} {t_cur}</div>
            <div class="total-val">{calc_amt * r_val:,.2f} {t_cur}</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

# ========================================================
# [메뉴: 환율 추이]
# ========================================================
elif menu == "환율 추이":
    st.title("📊 실제 통화별 환율 추이 분석 (API)")
    tgt_col, day_col = st.columns([2, 1])
    with tgt_col:
        tgt = st.selectbox(
            "조회 대상 통화 (USD 기준)", ["KRW", "EUR", "JPY", "GBP"]
        )
    with day_col:
        sel_days = st.selectbox(
            "조회 기간", [30, 60, 90, 180], format_func=lambda x: f"{x}일"
        )

    # 실제 API 호출
    df_trend_real = fetch_real_historical_rates("USD", tgt, days=sel_days)
    st.line_chart(df_trend_real, height=350, color="#F43F5E")

# ========================================================
# [메뉴: 💼 Trade Calculator]
# ========================================================
elif menu == "💼 Trade Calculator":
    st.title("💼 무역 수입원가 분석 & FX 스트레스 테스트")
    st.caption(
        "수출입 실무 견적 작성, 품목별 관세율/Incoterms 조건 연동 및 환율 변동 시나리오 테이블을 제공합니다."
    )

    p_col1, p_col2, p_col3 = st.columns([1.5, 1.5, 2])
    with p_col1:
        trade_preset = st.selectbox(
            "📦 품목별 관세 프리셋",
            [
                "직접 입력",
                "IT / 반도체 부품 (관세 0%)",
                "산업용 기계류 (관세 8%)",
                "소비재 / 잡화 (관세 13%)",
                "의류 / 패션 (관세 13%)",
            ],
        )
    with p_col2:
        incoterms = st.selectbox(
            "🚢 인도 조건 (Incoterms)",
            [
                "FOB (본선인도 - 운송비/보험료 별도)",
                "CIF (운임보험료포함 - 공급가에 포함)",
                "EXW (공장인도 - 내륙운송비 추가)",
            ],
        )
    with p_col3:
        st.write("")
        st.caption("💡 선택한 품목과 무역 조건에 맞춰 관세율과 운임 항목이 자동 계산됩니다.")

    preset_tariffs = {
        "직접 입력": 8.0,
        "IT / 반도체 부품 (관세 0%)": 0.0,
        "산업용 기계류 (관세 8%)": 8.0,
        "소비재 / 잡화 (관세 13%)": 13.0,
        "의류 / 패션 (관세 13%)": 13.0,
    }
    default_tariff = preset_tariffs[trade_preset]

    st.write("")

    left_side, right_side = st.columns([1, 1.3], gap="large")

    with left_side:
        st.subheader("📋 계약 및 운송 파라미터")
        in_col1, in_col2 = st.columns(2)
        with in_col1:
            invoice_val = st.number_input(
                "인보이스 물품 대금",
                min_value=0.0,
                value=10000.0,
                step=1000.0,
            )
        with in_col2:
            currency_sel = st.selectbox(
                "결제 통화", ["USD", "EUR", "JPY", "CNY"], index=0
            )

        live_fx = calculate_rate(currency_sel, "KRW")
        fx_col1, fx_col2 = st.columns(2)
        with fx_col1:
            applied_fx = st.number_input(
                f"적용 환율 (1 {currency_sel}당 KRW)",
                value=float(round(live_fx, 2)),
                step=1.0,
            )
        with fx_col2:
            custom_tariff = st.number_input(
                "관세율 (%)",
                min_value=0.0,
                max_value=100.0,
                value=default_tariff,
                step=0.5,
            )

        ship_val = 0.0 if "CIF" in incoterms else 500.0
        ship_input = st.number_input(
            f"국제 운임 및 보험료 ({currency_sel})"
            + (" [CIF 조건: 운임 포함]" if "CIF" in incoterms else ""),
            min_value=0.0,
            value=ship_val,
            step=50.0,
            disabled=("CIF" in incoterms),
        )
        misc_input = st.number_input(
            "국내 통관 수수료 / 하역료 (KRW)",
            min_value=0.0,
            value=150000.0,
            step=10000.0,
        )

        prod_krw = invoice_val * applied_fx
        ship_krw = ship_input * applied_fx
        cif_krw = prod_krw + ship_krw
        duty_krw = cif_krw * (custom_tariff / 100.0)
        vat_krw = (cif_krw + duty_krw) * 0.10
        final_total_krw = cif_krw + duty_krw + vat_krw + misc_input

    with right_side:
        st.subheader("📊 종합 수입원가 집계")

        st.markdown(
            f"""
            <div class="total-banner">
                <div class="total-title">총 예상 입고 원가 (Total Landed Cost)</div>
                <div class="total-val">₩{final_total_krw:,.0f}</div>
                <div style="font-size:0.85rem; color:#FFE4E6; margin-top:4px;">
                    과세가격(CIF): ₩{cif_krw:,.0f} &nbsp;|&nbsp; 제세공과금 합계: ₩{(duty_krw + vat_krw):,.0f}
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

        m_c1, m_c2, m_c3, m_c4 = st.columns(4)
        with m_c1:
            st.markdown(
                f"""<div class="cost-card"><div class="cost-title">물품 대금</div><div class="cost-val">₩{prod_krw:,.0f}</div></div>""",
                unsafe_allow_html=True,
            )
        with m_c2:
            st.markdown(
                f"""<div class="cost-card"><div class="cost-title">국제 운임</div><div class="cost-val">₩{ship_krw:,.0f}</div></div>""",
                unsafe_allow_html=True,
            )
        with m_c3:
            st.markdown(
                f"""<div class="cost-card"><div class="cost-title">관세 ({custom_tariff}%)</div><div class="cost-val">₩{duty_krw:,.0f}</div></div>""",
                unsafe_allow_html=True,
            )
        with m_c4:
            st.markdown(
                f"""<div class="cost-card"><div class="cost-title">부가세 (10%)</div><div class="cost-val">₩{vat_krw:,.0f}</div></div>""",
                unsafe_allow_html=True,
            )

        st.write("")

        items = [
            ("물품 원화대금", prod_krw, "linear-gradient(90deg, #F43F5E, #FB7185)"),
            ("수입 부가세 (10%)", vat_krw, "linear-gradient(90deg, #FB7185, #FDA4AF)"),
            ("예상 관세", duty_krw, "linear-gradient(90deg, #FDA4AF, #FECDD3)"),
            ("국제 운임", ship_krw, "linear-gradient(90deg, #F472B6, #FBCFE8)"),
            ("통관 부대비용", misc_input, "linear-gradient(90deg, #E2E8F0, #CBD5E1)"),
        ]

        rows_html = "".join([
            f'<div class="gauge-row">'
            f'<div class="gauge-labels"><span>{name}</span><span>₩{val:,.0f} ({(val / final_total_krw * 100 if final_total_krw > 0 else 0):.1f}%)</span></div>'
            f'<div class="gauge-bar-bg"><div class="gauge-bar-fill" style="width:{(val / final_total_krw * 100 if final_total_krw > 0 else 0):.1f}%; background:{grad};"></div></div>'
            f'</div>'
            for name, val, grad in items
        ])
        gauge_container = f'<div class="chart-container-card"><div style="font-size:0.95rem; font-weight:700; color:#881337; margin-bottom:14px;">🌸 원가 항목별 구성 비중</div>{rows_html}</div>'
        st.markdown(gauge_container, unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("🔮 환율 변동 시나리오 스트레스 테스트 (FX Stress Test)")
    st.caption("환율이 변동했을 때 최종 입고 원가와 원가 변동폭을 즉시 시뮬레이션합니다.")

    steps = [-50, -30, -10, 0, 10, 30, 50]
    sim_data = []
    for diff in steps:
        test_fx = applied_fx + diff
        t_cif = (invoice_val + ship_input) * test_fx
        t_duty = t_cif * (custom_tariff / 100.0)
        t_vat = (t_cif + t_duty) * 0.10
        t_total = t_cif + t_duty + t_vat + misc_input
        cost_diff = t_total - final_total_krw
        sim_data.append(
            {
                "시나리오": (
                    f"환율 {diff:+d}원" if diff != 0 else "기준 환율 (현재)"
                ),
                "예상 환율 (KRW)": f"₩{test_fx:,.2f}",
                "예상 총 원가 (KRW)": f"₩{t_total:,.0f}",
                "원가 변동액 (KRW)": (
                    f"{cost_diff:+,.0f}원" if diff != 0 else "-"
                ),
                "변동률 (%)": (
                    f"{(cost_diff / final_total_krw) * 100:+.2f}%"
                    if diff != 0
                    else "-"
                ),
            }
        )

    sim_df = pd.DataFrame(sim_data)
    st.dataframe(sim_df, use_container_width=True, hide_index=True)

    report_data = {
        "항목": [
            "인보이스 대금",
            "결제 통화",
            "적용 환율",
            "국제 운임",
            "관세율",
            "관세액",
            "수입 부가세",
            "부대비용",
            "총 예상 입고 원가",
        ],
        "내역": [
            f"{invoice_val:,.2f}",
            currency_sel,
            f"{applied_fx:,.2f} KRW",
            f"{ship_input:,.2f} {currency_sel}",
            f"{custom_tariff}%",
            f"{duty_krw:,.0f} KRW",
            f"{vat_krw:,.0f} KRW",
            f"{misc_input:,.0f} KRW",
            f"{final_total_krw:,.0f} KRW",
        ],
    }
    csv_bytes = (
        pd.DataFrame(report_data).to_csv(index=False).encode("utf-8-sig")
    )

    st.download_button(
        label="📥 수입 원가 견적 명세서(CSV) 다운로드",
        data=csv_bytes,
        file_name=f"Trade_Cost_Report_{datetime.date.today().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )

# 9. 푸터
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #FB7185; font-size: 0.8rem; font-weight: 500;">
        🌸 Executive FX & Trade Platform © 2026. Powered by Streamlit & Official ECB Data.
    </div>
""",
    unsafe_allow_html=True,
)