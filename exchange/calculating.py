import datetime
import math
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
    page_title="FX Platform & Trade Analysis",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 3. 로맨틱 소프트 핑크 & 피치 그라데이션 CSS 테마
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Malgun Gothic", sans-serif;
    }
    
    /* 상단 상태 바: 부드러운 로즈 핑크 그라데이션 */
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
    
    /* 카드 컴포넌트: 은은한 핑크 테두리와 그림자 */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #FFE4E6;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 4px 12px rgba(251, 113, 133, 0.06);
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #FDA4AF;
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #9F1239;
    }
    .metric-val {
        font-size: 1.5rem;
        font-weight: 800;
        color: #4C0519;
        margin: 6px 0;
    }
    .badge-up {
        color: #E11D48;
        background-color: #FFF1F2;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.8rem;
    }
    .badge-down {
        color: #2563EB;
        background-color: #EFF6FF;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.8rem;
    }
    
    /* 대형 계산기 결과 박스: 핑크 그라데이션 */
    .calc-display {
        background: linear-gradient(135deg, #FB7185 0%, #F43F5E 50%, #E11D48 100%);
        color: #FFFFFF;
        border-radius: 18px;
        padding: 26px;
        text-align: center;
        margin: 18px 0;
        box-shadow: 0 10px 25px rgba(244, 63, 94, 0.25);
    }
    .calc-subtext {
        color: #FFE4E6;
        font-size: 0.95rem;
        font-weight: 500;
    }
    .calc-main-result {
        font-size: 2.3rem;
        font-weight: 900;
        color: #FFFFFF;
        margin: 8px 0;
        letter-spacing: -0.5px;
    }
    
    /* 무역 카드 */
    .trade-card {
        background-color: #FFF5F7;
        border: 1px solid #FECDD3;
        border-left: 5px solid #FB7185;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 15px;
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
    "AUD": {"name": "Australian Dollar", "flag": "🇦🇺"},
    "CAD": {"name": "Canadian Dollar", "flag": "🇨🇦"},
    "SGD": {"name": "Singapore Dollar", "flag": "🇸🇬"},
    "HKD": {"name": "Hong Kong Dollar", "flag": "🇭🇰"},
}

# 5. 세션 상태 초기화
if "from_curr" not in st.session_state:
    st.session_state.from_curr = "USD"
if "to_curr" not in st.session_state:
    st.session_state.to_curr = "KRW"
if "amount" not in st.session_state:
    st.session_state.amount = 10000.0


def swap_currencies():
    temp = st.session_state.from_curr
    st.session_state.from_curr = st.session_state.to_curr
    st.session_state.to_curr = temp


# 6. 실시간 환율 API 호출 함수
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_api_rates(base="USD"):
    fallback_rates = {
        "USD": 1.0,
        "KRW": 1338.80,
        "EUR": 0.86,
        "JPY": 153.40,
        "CNY": 6.72,
        "GBP": 0.74,
        "AUD": 1.51,
        "CAD": 1.36,
        "SGD": 1.34,
        "HKD": 7.81,
    }

    if not API_KEY or API_KEY in ["your_key", ""]:
        return fallback_rates, "기본 환율 모드 (.env 키 미설정)", "Standby"

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


# 7. 상단 글로벌 인디케이터 헤더
st.markdown(
    f"""
    <div class="top-status-bar">
        <div>
            <span class="live-pulse"></span>
            <b>FX & TRADE PLATFORM</b> &nbsp;|&nbsp; <span>실시간 외환/무역 금융 분석 데스크</span>
        </div>
        <div>
            상태: <b>{conn_status}</b> &nbsp;|&nbsp; 동기화 시각: <b>{last_updated}</b>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# 8. 사이드바 - 확실한 선택 상태 뱃지 제공
with st.sidebar:
    st.markdown("### 📌 **Menu**")
    menu = st.radio(
        "메뉴 선택",
        ["Dashboard", "환율 계산기", "환율 추이", "💼 Trade Calculator"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("#### ⭐ **자주 쓰는 통화쌍**")

    # 현재 선택된 통화쌍을 세션 상태와 동기화된 라디오 버튼으로 표시 (선택 상태가 명확히 남음)
    preset_pairs = ["USD → KRW", "EUR → KRW", "JPY → KRW", "CNY → KRW"]
    current_pair_str = f"{st.session_state.from_curr} → {st.session_state.to_curr}"
    default_idx = (
        preset_pairs.index(current_pair_str)
        if current_pair_str in preset_pairs
        else None
    )

    selected_preset = st.radio(
        "통화쌍 프리셋 선택",
        preset_pairs,
        index=default_idx if default_idx is not None else 0,
        label_visibility="collapsed",
    )

    # 사용자가 프리셋을 클릭하면 상태 즉시 변경
    f_code, t_code = selected_preset.split(" → ")
    if (
        st.session_state.from_curr != f_code
        or st.session_state.to_curr != t_code
    ):
        st.session_state.from_curr = f_code
        st.session_state.to_curr = t_code
        st.rerun()

    # 현재 활성화된 통화쌍을 핑크 뱃지로 명시
    st.info(
        f"현재 적용 통화: **{st.session_state.from_curr} → {st.session_state.to_curr}**"
    )

# ========================================================
# [메뉴 1] DASHBOARD
# ========================================================
if menu == "Dashboard":
    st.title("🌸 FX CALCULATOR")
    st.caption("Real-time Exchange Rate & Financial Platform")

    # 주요 5대 통화 카드
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
            curr_rate = calculate_rate(sym, "KRW")
            badge = "badge-up" if delta >= 0 else "badge-down"
            icon = "▲" if delta >= 0 else "▼"
            rate_disp = (curr_rate * 100) if sym == "JPY" else curr_rate
            title_disp = f"{CURRENCY_DATA[sym]['flag']} {sym}/KRW" + (
                "(100엔)" if sym == "JPY" else ""
            )

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">{title_disp}</div>
                    <div class="metric-val">{rate_disp:,.2f}</div>
                    <div><span class="{badge}">{icon} {abs(delta):.2f}%</span></div>
                </div>
            """,
                unsafe_allow_html=True,
            )

    st.write("")
    c_left, c_right = st.columns([1.1, 1], gap="large")

    with c_left:
        st.subheader("⚡ 실시간 환전 계산기")
        row1, row2, row3 = st.columns([5, 1, 5])
        with row1:
            from_sel = st.selectbox(
                "FROM",
                list(CURRENCY_DATA.keys()),
                index=list(CURRENCY_DATA.keys()).index(
                    st.session_state.from_curr
                ),
                format_func=lambda x: f"{CURRENCY_DATA[x]['flag']} {x} - {CURRENCY_DATA[x]['name']}",
            )
        with row2:
            st.write("")
            st.write("")
            st.button("⇄", on_click=swap_currencies, use_container_width=True)
        with row3:
            to_sel = st.selectbox(
                "TO",
                list(CURRENCY_DATA.keys()),
                index=list(CURRENCY_DATA.keys()).index(
                    st.session_state.to_curr
                ),
                format_func=lambda x: f"{CURRENCY_DATA[x]['flag']} {x} - {CURRENCY_DATA[x]['name']}",
            )

        amt_input = st.number_input(
            "금액",
            min_value=0.0,
            value=st.session_state.amount,
            step=100.0,
            format="%.2f",
        )
        st.session_state.amount = amt_input
        st.session_state.from_curr = from_sel
        st.session_state.to_curr = to_sel

        applied_rate = calculate_rate(from_sel, to_sel)
        calc_result = amt_input * applied_rate

        st.markdown(
            f"""
            <div class="calc-display">
                <div class="calc-subtext">적용 환율: 1 {from_sel} = {applied_rate:,.4f} {to_sel}</div>
                <div class="calc-main-result">{calc_result:,.2f} {to_sel}</div>
                <div class="calc-subtext">입력 금액: {amt_input:,.2f} {from_sel}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

        copy_val = f"{amt_input:,.2f} {from_sel} = {calc_result:,.2f} {to_sel}"
        st.code(copy_val, language="text")

    with c_right:
        st.subheader("📈 USD / KRW 30일 환율 변동 추이")
        base_val = rates.get("KRW", 1338.80)
        dates = [
            datetime.date.today() - datetime.timedelta(days=i)
            for i in range(30, -1, -1)
        ]
        rates_trend = [
            round(base_val + (math.sin(i / 3.0) * 10.0) - ((i % 4) * 1.2), 2)
            for i in range(len(dates))
        ]
        df_chart = pd.DataFrame({"USD/KRW": rates_trend}, index=dates)
        st.line_chart(df_chart, height=260)

        m1, m2, m3 = st.columns(3)
        m1.metric("최고 환율", f"₩{max(rates_trend):,.2f}")
        m2.metric("최저 환율", f"₩{min(rates_trend):,.2f}")
        diff_30d = rates_trend[-1] - rates_trend[0]
        m3.metric("30일 변동폭", f"{diff_30d:+,.2f}원")

# ========================================================
# [메뉴 2] 환율 계산기
# ========================================================
elif menu == "환율 계산기":
    st.title("💱 전문 통화 간 환율 계산기")
    b1, b2, b3 = st.columns([5, 1, 5])
    with b1:
        f_curr = st.selectbox(
            "FROM 통화",
            list(CURRENCY_DATA.keys()),
            index=list(CURRENCY_DATA.keys()).index(st.session_state.from_curr),
            format_func=lambda x: f"{CURRENCY_DATA[x]['flag']} {x} - {CURRENCY_DATA[x]['name']}",
        )
        in_amt = st.number_input(
            "입력 금액",
            min_value=0.0,
            value=st.session_state.amount,
            format="%.2f",
        )
    with b2:
        st.write("")
        st.write("")
        st.button("⇄", on_click=swap_currencies, use_container_width=True)
    with b3:
        t_curr = st.selectbox(
            "TO 통화",
            list(CURRENCY_DATA.keys()),
            index=list(CURRENCY_DATA.keys()).index(st.session_state.to_curr),
            format_func=lambda x: f"{CURRENCY_DATA[x]['flag']} {x} - {CURRENCY_DATA[x]['name']}",
        )

    st.session_state.from_curr = f_curr
    st.session_state.to_curr = t_curr
    st.session_state.amount = in_amt

    rate_val = calculate_rate(f_curr, t_curr)
    total_val = in_amt * rate_val

    st.markdown(
        f"""
        <div class="calc-display">
            <div class="calc-subtext">1 {f_curr} = {rate_val:,.4f} {t_curr}</div>
            <div class="calc-main-result">{total_val:,.2f} {t_curr}</div>
            <div class="calc-subtext">환산 기준: {in_amt:,.2f} {f_curr}</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

# ========================================================
# [메뉴 3] 환율 추이
# ========================================================
elif menu == "환율 추이":
    st.title("📊 통화별 환율 추이 분석")
    t_c1, t_c2 = st.columns([2, 1])
    with t_c1:
        target_pair = st.selectbox(
            "조회 통화쌍 (기준: USD)", ["KRW", "EUR", "JPY", "CNY", "GBP"]
        )
    with t_c2:
        days_range = st.selectbox(
            "기간", [7, 30, 90], index=1, format_func=lambda x: f"{x}일"
        )

    cur_val = calculate_rate("USD", target_pair)
    dates_list = [
        datetime.date.today() - datetime.timedelta(days=i)
        for i in range(days_range, -1, -1)
    ]
    trend_vals = [
        round(cur_val + (math.sin(i / 2.5) * (cur_val * 0.008)), 4)
        for i in range(len(dates_list))
    ]
    df_trend = pd.DataFrame(
        {f"USD/{target_pair}": trend_vals}, index=dates_list
    )
    st.line_chart(df_trend, height=350)

# ========================================================
# [메뉴 4] 무역 계산기 & 시뮬레이션
# ========================================================
elif menu == "💼 Trade Calculator":
    st.title("💼 무역 거래 비용 계산기 & 환율 시뮬레이터")
    st.caption("해외 구매 및 수출입 실무에서 통관 원가와 환위험 노출액을 즉각 산출합니다.")

    tc1, tc2 = st.columns(2, gap="large")
    with tc1:
        st.subheader("📋 계약 및 수입 정보 입력")
        goods_cost = st.number_input(
            "상품 인보이스 금액", min_value=0.0, value=10000.0, step=1000.0
        )
        curr_choice = st.selectbox(
            "결제 통화", ["USD", "EUR", "JPY", "CNY"], index=0
        )

        auto_rate = calculate_rate(curr_choice, "KRW")
        trade_rate = st.number_input(
            f"적용 환율 (1 {curr_choice} 당 원화)",
            value=float(round(auto_rate, 2)),
        )
        freight_cost = st.number_input(
            f"국제 운송비 ({curr_choice})", min_value=0.0, value=500.0, step=100.0
        )
        tariff_rate = st.number_input(
            "관세율 (%)", min_value=0.0, max_value=100.0, value=8.0, step=0.5
        )
        extra_krw = st.number_input(
            "기타 국내 통관/운송 부대비용 (KRW)", min_value=0.0, value=0.0
        )

        goods_krw = goods_cost * trade_rate
        freight_krw = freight_cost * trade_rate
        cif_krw = goods_krw + freight_krw
        tariff_krw = cif_krw * (tariff_rate / 100.0)
        vat_krw = (cif_krw + tariff_krw) * 0.10
        total_trade_cost = cif_krw + tariff_krw + vat_krw + extra_krw

    with tc2:
        st.subheader("🏷️ 수입 원가 정산 내역")
        st.markdown(
            f"""
            <div class="trade-card">
                <p>• <b>상품 원화 금액:</b> ₩{goods_krw:,.0f}</p>
                <p>• <b>국제 운송비:</b> ₩{freight_krw:,.0f}</p>
                <p>• <b>과세가격 (CIF 기준):</b> ₩{cif_krw:,.0f}</p>
                <p>• <b>예상 관세 ({tariff_rate}%):</b> ₩{tariff_krw:,.0f}</p>
                <p>• <b>수입 부가세 (10%):</b> ₩{vat_krw:,.0f}</p>
                <hr style="margin: 8px 0; border: 0; border-top: 1px solid #FECDD3;">
                <h4 style="color:#9F1239; margin:0;">총 예상 원가: ₩{total_trade_cost:,.0f}</h4>
            </div>
        """,
            unsafe_allow_html=True,
        )

        st.write("")
        st.subheader("🔮 환율 변동 시뮬레이션")
        expected_rate = st.number_input(
            "결제 시점 예상 환율 (KRW)",
            value=float(round(trade_rate * 1.03, 2)),
            step=1.0,
        )

        base_settle = (goods_cost + freight_cost) * trade_rate
        exp_settle = (goods_cost + freight_cost) * expected_rate
        diff_fx = exp_settle - base_settle
        diff_rate_pct = ((expected_rate - trade_rate) / trade_rate) * 100.0

        color_fx = "#E11D48" if diff_fx > 0 else "#2563EB"
        sign_fx = "+" if diff_fx > 0 else ""

        st.markdown(
            f"""
            <div style="background-color: #FFFFFF; border: 1px solid #FFE4E6; padding: 16px; border-radius: 12px; box-shadow: 0 2px 8px rgba(244,63,94,0.05);">
                <div>기준 환율 결제 원가: <b>₩{base_settle:,.0f}</b></div>
                <div>예상 환율 결제 원가: <b>₩{exp_settle:,.0f}</b></div>
                <div style="font-size: 1.15rem; margin-top: 8px; font-weight: 800; color: {color_fx};">
                    환율 변동 영향: {sign_fx}₩{diff_fx:,.0f} ({sign_fx}{diff_rate_pct:.2f}%)
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

# 9. 하단 푸터
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #FB7185; font-size: 0.8rem; font-weight: 500;">
        🌸 Soft Pink FX Platform & Trade Analysis Desk © 2026. Powered by Streamlit.
    </div>
""",
    unsafe_allow_html=True,
)