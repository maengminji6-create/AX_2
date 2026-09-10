import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# 1. 페이지 설정 및 세련된 연두/민트(Light Green & Mint) 스타일링
# ---------------------------------------------------------
st.set_page_config(
    page_title="TRADE-MBTI | 나에게 맞는 무역 직무 찾기",
    page_icon="🌿",
    layout="centered"
)

CUSTOM_CSS = """
<style>
.stApp {
    background-color: #F4FBF7;
    color: #1E293B;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.main-title {
    font-size: 2.3rem;
    font-weight: 800;
    color: #064E3B;
    text-align: center;
    margin-bottom: 6px;
    letter-spacing: -0.02em;
}

.sub-title {
    font-size: 1.05rem;
    color: #4B5563;
    text-align: center;
    margin-bottom: 24px;
}

.question-text {
    font-size: 1.25rem;
    font-weight: 700;
    color: #0F172A;
    line-height: 1.6;
    margin-bottom: 24px;
}

.category-badge {
    display: inline-block;
    padding: 6px 14px;
    background-color: #D1FAE5;
    color: #065F46;
    font-size: 0.85rem;
    font-weight: 700;
    border-radius: 9999px;
    margin-bottom: 12px;
}

.strength-tag {
    display: inline-block;
    padding: 6px 12px;
    background-color: #E8F8F0;
    color: #047857;
    font-size: 0.85rem;
    font-weight: 600;
    border-radius: 8px;
    margin: 4px;
}

.top3-box {
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    height: 100%;
}
.top1-box {
    background-color: #ECFDF5;
    border: 2px solid #10B981;
}
.top2-box {
    background-color: #F9FAFB;
    border: 1.5px solid #CBD5E1;
}
.top3-box-sub {
    background-color: #F9FAFB;
    border: 1.5px solid #E2E8F0;
}

.mbti-dim-card {
    background-color: #FFFFFF;
    border-left: 4px solid #10B981;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 14px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important;
    border-radius: 18px !important;
    border: 1px solid #E5E7EB !important;
    box-shadow: 0 4px 20px rgba(16, 185, 129, 0.08) !important;
    padding: 16px !important;
    margin-bottom: 20px !important;
}

div.stButton > button {
    border-radius: 12px;
    font-weight: 600;
    padding: 14px 20px;
    border: 1.5px solid #A7F3D0;
    background-color: #FFFFFF;
    color: #1F2937;
    transition: all 0.2s ease;
}
div.stButton > button:hover {
    border-color: #10B981;
    background-color: #ECFDF5;
    color: #047857;
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #34D399 0%, #059669 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3) !important;
}
div.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #10B981 0%, #047857 100%) !important;
}

.stProgress > div > div > div > div {
    background-color: #10B981 !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 직무 마스터 정보 및 4축 분석 메타데이터
# ---------------------------------------------------------
JOBS = {
    "해외영업": {
        "icon": "🌎",
        "tagline": "사람과 시장을 연결하는 글로벌 커뮤니케이터",
        "desc": "탁월한 언어 감각과 적극적인 대인관계 능력을 바탕으로 신규 바이어를 발굴하고 가격 및 계약 조건을 능숙하게 이끌어냅니다.",
        "strengths": ["글로벌 소통력", "협상력", "시장 개척 의지", "네트워킹"],
        "tasks": ["해외 바이어 발굴 및 전시회 참가", "가격 및 무역 계약 협상", "수출 오더 수주 및 고객사 관리"]
    },
    "구매/조달": {
        "icon": "🛒",
        "tagline": "데이터와 원가로 최적을 찾는 전략적 네고시에이터",
        "desc": "시장 원가 구조와 공급망 데이터를 면밀히 분석하여 가장 경쟁력 있고 안정적인 글로벌 공급사를 발굴 및 관리합니다.",
        "strengths": ["원가 분석력", "협상 전략", "공급망 모니터링", "손익 감각"],
        "tasks": ["글로벌 원자재/제품 소싱", "단가 협상 및 공급 계약 체결", "공급업체 평가 및 리스크 관리"]
    },
    "수출입관리": {
        "icon": "📦",
        "tagline": "한 치의 오차도 허용치 않는 통관·규제 전문가",
        "desc": "복잡한 관세법령과 FTA 원산지 규정을 숙지하여 제품이 국경을 안전하고 신속하게 통과하도록 이끕니다.",
        "strengths": ["법령/규정 이해", "치밀한 꼼꼼함", "일정 준수", "리스크 사전 예방"],
        "tasks": ["수출입 통관 진행 및 관세 절감 검토", "FTA 원산지 증명서 발급/관리", "외환 수수료 및 무역 대금 결제"]
    },
    "무역사무": {
        "icon": "📄",
        "tagline": "완벽한 서류로 거래를 보증하는 신용의 수호자",
        "desc": "B/L, C/I, P/L, L/C 등 핵심 무역 서류의 철저한 대조와 무결성을 보장하여 네고 하자(Discrepancy) 위험을 원천 차단합니다.",
        "strengths": ["서류 정밀 대조", "정직과 신뢰", "체계적 데이터 정리", "안정적 지원"],
        "tasks": ["선적 서류(B/L, Invoice, P/L) 작성 및 검토", "신용장(L/C) 조건 대조 및 매입", "ERP 무역 데이터 전산 입력"]
    },
    "물류/SCM": {
        "icon": "🚚",
        "tagline": "글로벌 공급망의 흐름을 지휘하는 오케스트레이터",
        "desc": "해상·항공 운임과 적재 공간을 신속히 확보하고, 항만 적체나 지연 상황에서 대안 루트를 빠르게 찾아냅니다.",
        "strengths": ["위기 대응력", "물류 흐름 최적화", "포워더 핸들링", "동시 일정 관리"],
        "tasks": ["포워더 선정 및 선복(Space) 부킹", "리드타임 단축 및 복합운송 설계", "물류비 정산 및 물류 리스크 대응"]
    },
    "해외시장조사": {
        "icon": "🔎",
        "tagline": "숫자와 트렌드 속에서 기회를 찾는 전략 분석가",
        "desc": "글로벌 무역 통계, 현지 소비 트렌드, 경쟁사 동향 데이터를 논리적으로 종합하여 최적의 진출 전략을 수립합니다.",
        "strengths": ["데이터 마이닝", "논리적 사고", "시장 통찰력", "보고서 기획력"],
        "tasks": ["K-stat 등 무역 통계 분석", "타깃 국가 규제 및 인증 사전 조사", "시장 진출 전략 보고서 작성"]
    }
}

MBTI_DIM_DETAILS = {
    "E": {
        "title": "E (외향형) - 현장 주도 및 대인 네트워크",
        "fit_jobs": "해외영업, 물류/SCM",
        "strength": "해외 박람회 부스 유치 및 현지 에이전트·바이어와의 유선 소통, 돌발 상황 시 즉각적인 현장 조율.",
        "weakness": "서류 검토보다 대화와 실행을 앞세우다 계약서의 세부 단서 조항(Penalty Clause, Incoterms 조건)을 간과하지 않도록 주의하세요."
    },
    "I": {
        "title": "I (내향형) - 정밀 검증 및 심층 데이터 마이닝",
        "fit_jobs": "무역사무, 해외시장조사",
        "strength": "B/L, C/I, P/L, L/C 등 복잡한 선적 서류의 독자적 집중 검토, 관세 무역 통계 데이터를 장시간 파고드는 정밀 분석.",
        "weakness": "긴급한 물류 이슈 발생 시 이메일 기록에만 머무르지 않고, 즉각적인 유선 콜이나 메신저로 신속히 해결하려는 적극성이 요구됩니다."
    },
    "S": {
        "title": "S (감각/현실형) - 실무 디테일 및 규정 오차 0%",
        "fit_jobs": "수출입관리, 무역사무, 구매/조달",
        "strength": "관세율표 해설서 기반의 정확한 HS Code 매칭, 원산지 결정 기준(PSR) 대조, 단가 및 환율 변동 마진 관리.",
        "weakness": "당장 눈앞의 서류 규정에만 매몰되어 글로벌 공급망 체계의 장기적 재편이나 거시적 무역 리스크를 놓치지 않아야 합니다."
    },
    "N": {
        "title": "N (직관/통찰형) - 글로벌 트렌드 및 미래 전략",
        "fit_jobs": "해외시장조사, 해외영업 기획",
        "strength": "신흥 시장의 규제 변화 트렌드 포착, 제품 현지화 포지셔닝 및 신규 수출입 거래선 개척 전략 수립.",
        "weakness": "비전과 전략 구상에 비해 세부 무역 서류(Incoterms 규칙, 통관 인증 서류 등)의 사소한 누락으로 선적이 지연되지 않도록 점검해야 합니다."
    },
    "T": {
        "title": "T (사고/논리형) - 원가 분석 및 원칙 중심 네고",
        "fit_jobs": "구매/조달, 수출입관리",
        "strength": "원가 분석표(Cost Breakdown)를 바탕으로 한 객관적 단가 네고, 세관 소명 요구 시 법령과 선례를 동원한 논리적 방어.",
        "weakness": "계약 규정과 숫자만 앞세우면 장기적 신뢰가 중요한 바이어/공급사와의 관계 형성에 마찰이 생길 수 있으므로 소프트 스킬을 보완하세요."
    },
    "F": {
        "title": "F (감정/관계형) - 글로벌 라포 및 신뢰 파트너십",
        "fit_jobs": "해외영업, 고객사(Client) 관리",
        "strength": "바이어의 문화적 맥락(Cultural Context) 이해, 감정적 유대를 통한 장기적 파트너십 구축, 클레임 바이어의 섬세한 케어.",
        "weakness": "친분 관계에 이끌려 무리한 결제 조건(예: O/A 여신 확대, 무리한 단가 인하)을 수용하지 않도록 손익 기준을 엄격히 사수하세요."
    },
    "J": {
        "title": "J (판단/계획형) - 공정 일정 관리 및 SOP 표준화",
        "fit_jobs": "수출입관리, 무역사무, 구매/조달",
        "strength": "선적 기한(Shipment Date)과 신용장 유효기일(Expiry Date)의 철저한 준수, 선적 프로세스 표준화를 통한 리스크 사전 차단.",
        "weakness": "선박 롤오버(Rollover), 항만 파업 등 불가항력 변수 발생 시 유연한 대체 루트로 신속하게 우회하는 순발력을 길러야 합니다."
    },
    "P": {
        "title": "P (인식/유연형) - 기민한 위기 대응 및 상황 적응",
        "fit_jobs": "물류/SCM, 해외영업 현장",
        "strength": "기상 악화나 선박 체선 시 대체 항공편 수배 및 복합운송 루트 확보 등 기민한 위기 대응, 바이어의 급작스러운 변경 요청 대처.",
        "weakness": "체계적인 히스토리 기록과 선적 서류 보관이 미흡해 차후 관세 사후 심사 등에서 문제가 생기지 않도록 업무 규격화 습관이 필요합니다."
    }
}

# ---------------------------------------------------------
# 3. 20문항 데이터
# ---------------------------------------------------------
QUESTIONS = [
    # 1. 커뮤니케이션 성향 (E ↔ I)
    {
        "cat": "커뮤니케이션 성향",
        "q": "해외 박람회 현장에서 부스를 지나가는 바이어를 보았을 때 나의 행동은?",
        "options": [
            ("자신감 있게 먼저 다가가 가벼운 인사와 함께 대화를 시작한다.", {"해외영업": 3, "물류/SCM": 1}, "E"),
            ("부스에 비치된 카탈로그를 정리하며 바이어가 관심을 보일 때까지 차분히 기다린다.", {"무역사무": 2, "해외시장조사": 2}, "I")
        ]
    },
    {
        "cat": "커뮤니케이션 성향",
        "q": "해외 바이어와 첫 비즈니스 연락을 취해야 할 때 선호하는 방식은?",
        "options": [
            ("즉각적인 피드백을 얻기 위해 유선 전화나 화상 미팅을 적극 요청한다.", {"해외영업": 3, "물류/SCM": 1}, "E"),
            ("정확한 근거 자료와 제안서를 완벽히 다듬어 정중한 이메일로 먼저 보낸다.", {"해외시장조사": 2, "무역사무": 2}, "I")
        ]
    },
    {
        "cat": "커뮤니케이션 성향",
        "q": "해외 거래처와의 정기 미팅에서 내가 더 중요하게 챙기는 부분은?",
        "options": [
            ("바이어와의 개인적 친밀감 형성 및 상호 간의 유대감(라포) 강화", {"해외영업": 3, "물류/SCM": 1}, "E"),
            ("준비해 온 거래 실적 및 분기별 데이터 지표를 차분하게 브리핑하는 것", {"구매/조달": 2, "해외시장조사": 2}, "I")
        ]
    },
    {
        "cat": "커뮤니케이션 성향",
        "q": "사내 회의 중 팀원 간 납기 일정에 대한 이견이 첨예하게 부딪힐 때?",
        "options": [
            ("동료들을 직접 찾아가 현장의 고충을 듣고 대화로 접점을 이끌어낸다.", {"해외영업": 2, "물류/SCM": 2}, "E"),
            ("혼자 조용히 프로젝트 현황표와 각자의 작업 속도를 재검토해 수정안을 작성한다.", {"무역사무": 2, "수출입관리": 2}, "I")
        ]
    },
    {
        "cat": "커뮤니케이션 성향",
        "q": "시차가 12시간 나는 해외 지사와 소통할 때 나의 자연스러운 스타일은?",
        "options": [
            ("상대 근무 시간에 맞춰 실시간 메신저로 빠르게 핑퐁 대화를 나눈다.", {"해외영업": 2, "물류/SCM": 2}, "E"),
            ("요점, 참고 서류, 요청 기한을 체계적인 불릿 포인트로 작성해 메일로 남긴다.", {"무역사무": 3, "수출입관리": 2}, "I")
        ]
    },

    # 2. 분석 성향 (S ↔ N)
    {
        "cat": "분석 성향",
        "q": "새로운 해외 시장 진출 검토 보고서를 작성할 때 가장 먼저 집중하는 것은?",
        "options": [
            ("수입 관세율, 필수 인증 목록, 통관 절차 등 구체적이고 현실적인 규제 요건", {"수출입관리": 3, "무역사무": 2}, "S"),
            ("현지 인구 통계 변화, 소비 트렌드, 잠재적인 시장 성장 가능성의 큰 그림", {"해외시장조사": 3, "해외영업": 1}, "N")
        ]
    },
    {
        "cat": "분석 성향",
        "q": "새로운 해외 원자재 공급업체를 평가할 때 더 신뢰하는 지표는?",
        "options": [
            ("품목 규격 공차, 불량률 수치, 과거 납기 준수율 등 실증적인 세부 데이터", {"구매/조달": 3, "수출입관리": 1}, "S"),
            ("공급사의 기술 혁신 로드맵과 향후 글로벌 시장에서의 확장 비전", {"해외시장조사": 2, "해외영업": 2}, "N")
        ]
    },
    {
        "cat": "분석 성향",
        "q": "방대한 무역 데이터를 마주했을 때 나의 업무 접근 방식은?",
        "options": [
            ("단가, 수량, 환율 등 세부 숫자가 정확히 일치하는지 하나하나 대조·검증한다.", {"무역사무": 3, "수출입관리": 2}, "S"),
            ("수치 이면에 숨겨진 글로벌 수요의 흐름과 향후 트렌드 패턴을 읽어낸다.", {"해외시장조사": 3, "해외영업": 2}, "N")
        ]
    },
    {
        "cat": "분석 성향",
        "q": "원/달러 환율이 급등하는 국면에서 내가 가장 먼저 떠올리는 생각은?",
        "options": [
            ("현재 진행 중인 선적 건의 결제 대금 환차손익을 품목별로 즉시 계산한다.", {"구매/조달": 2, "수출입관리": 2}, "S"),
            ("환율 상승으로 인해 우리 제품의 글로벌 가격 경쟁력이 가져올 새로운 수출 기회를 본다.", {"해외영업": 2, "해외시장조사": 2}, "N")
        ]
    },
    {
        "cat": "분석 성향",
        "q": "거래 상대 기업을 분석할 때 나의 시선이 더 머무는 곳은?",
        "options": [
            ("재무제표의 부채비율, 최근 3년간 결제 지연 이력 등 명확한 사실 데이터", {"구매/조달": 2, "무역사무": 2}, "S"),
            ("해당 기업이 속한 현지 산업 생태계와 향후 비즈니스 모델의 잠재력", {"해외시장조사": 3, "해외영업": 2}, "N")
        ]
    },

    # 3. 업무 스타일 (T ↔ F)
    {
        "cat": "업무 스타일",
        "q": "오랜 기간 거래해 온 바이어가 무리한 단가 인하를 요구할 때?",
        "options": [
            ("원자재비와 물류비 인상 내역을 바탕으로 마진 손실을 증명하며 원칙대로 거절한다.", {"구매/조달": 3, "수출입관리": 1}, "T"),
            ("단가는 유지하되 소량 샘플 무상 제공 등 상대의 입장을 배려한 대안을 제시한다.", {"해외영업": 3, "물류/SCM": 1}, "F")
        ]
    },
    {
        "cat": "업무 스타일",
        "q": "팀 내에서 무역 서류의 기재 오류가 발생했을 때 나의 피드백 방식은?",
        "options": [
            ("원인을 객관적으로 짚고, 재발 방지를 위한 명확한 체크리스트 수정을 요구한다.", {"무역사무": 3, "수출입관리": 2}, "T"),
            ("담당자가 겪었을 당혹감에 공감하며, 함께 수습 방안을 차분히 모색한다.", {"해외영업": 2, "물류/SCM": 2}, "F")
        ]
    },
    {
        "cat": "업무 스타일",
        "q": "글로벌 공급사를 최종 선정하는 기준에서 더 결정적인 요소는?",
        "options": [
            ("단가, 품질 인증, 계약상 패널티 수용 여부 등 객관적인 계약 조건", {"구매/조달": 3, "수출입관리": 2}, "T"),
            ("영업 담당자의 성실성과 장기적으로 신뢰할 수 있는 파트너십 태도", {"해외영업": 3, "물류/SCM": 1}, "F")
        ]
    },
    {
        "cat": "업무 스타일",
        "q": "업무 성과를 평가받을 때 나에게 더 와닿는 칭찬은?",
        "options": [
            ("“불필요한 비용을 15% 절감하고 논리적으로 협상을 잘 이끌었습니다.”", {"구매/조달": 3, "해외시장조사": 2}, "T"),
            ("“바이어가 귀하의 진심 어린 응대에 깊이 감동해 계약을 연장했습니다.”", {"해외영업": 3, "물류/SCM": 1}, "F")
        ]
    },
    {
        "cat": "업무 스타일",
        "q": "거래처와 분쟁(Claim)이 발생했을 때 우선적으로 취하는 태도는?",
        "options": [
            ("계약서와 Incoterms 조항을 열람해 책임 소재와 배상 범위를 명확히 규정한다.", {"수출입관리": 3, "무역사무": 2}, "T"),
            ("상대방의 불편에 대해 도의적인 사과를 표하며 신뢰가 깨지지 않도록 소통한다.", {"해외영업": 3, "물류/SCM": 1}, "F")
        ]
    },

    # 4. 문제해결 / 의사결정 (J ↔ P)
    {
        "cat": "문제해결 / 의사결정",
        "q": "선적 기한(Shipment Date)을 3일 앞두고 기상 악화로 결항 통보를 받았다면?",
        "options": [
            ("신용장(L/C) 조건 변경 절차를 즉시 확인하고 바이어와 연장 승인을 서면 조율한다.", {"무역사무": 3, "수출입관리": 2}, "J"),
            ("인근 항구로의 내륙 트럭 운송이나 긴급 대체 항공편을 수배해 출항을 사수한다.", {"물류/SCM": 3, "해외영업": 2}, "P")
        ]
    },
    {
        "cat": "문제해결 / 의사결정",
        "q": "일주일간의 무역 업무 일정을 수립할 때 나의 스타일은?",
        "options": [
            ("요일별, 시간대별 마감 시한(Deadline)을 명확히 캘린더에 고정해 두고 처리한다.", {"무역사무": 2, "수출입관리": 2}, "J"),
            ("우선순위만 대략 잡아두고, 매일 쏟아지는 긴급 오더 현황에 맞춰 유동적으로 움직인다.", {"물류/SCM": 3, "해외영업": 2}, "P")
        ]
    },
    {
        "cat": "문제해결 / 의사결정",
        "q": "해외 바이어가 갑작스럽게 포장 규격과 라벨 디자인 변경을 요청했을 때?",
        "options": [
            ("추가 비용 발생분과 생산 지연 일정을 계산해 계약 변경 승인부터 정식 완료한다.", {"수출입관리": 3, "구매/조달": 2}, "J"),
            ("공장 생산 라인과 바로 통화하여 현재 라인에서 즉시 수정 가능한지 유연하게 알아본다.", {"물류/SCM": 2, "해외영업": 2}, "P")
        ]
    },
    {
        "cat": "문제해결 / 의사결정",
        "q": "내가 선호하는 무역 업무 매뉴얼의 형태는?",
        "options": [
            ("예외 없이 모든 상황이 문서화된 표준 업무 절차서(SOP)", {"무역사무": 3, "수출입관리": 2}, "J"),
            ("기본 원칙만 공유되고 담당자의 기민한 재량권이 넓게 인정되는 가이드라인", {"해외영업": 2, "물류/SCM": 3}, "P")
        ]
    },
    {
        "cat": "문제해결 / 의사결정",
        "q": "통관 서류와 물류 현장 조율이 동시에 긴박하게 돌아갈 때 나의 심리는?",
        "options": [
            ("순서대로 하나씩 끝내지 못하고 흐름이 꼬이면 큰 스트레스를 받는다.", {"무역사무": 3, "수출입관리": 2}, "J"),
            ("오히려 동시다발적인 변수를 순발력 있게 해결해 나갈 때 성취감을 느낀다.", {"물류/SCM": 3, "해외영업": 2}, "P")
        ]
    }
]

# ---------------------------------------------------------
# 4. 세션 상태 관리
# ---------------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = "home"
if "q_idx" not in st.session_state:
    st.session_state.q_idx = 0
if "scores" not in st.session_state:
    st.session_state.scores = {job: 0 for job in JOBS.keys()}
if "mbti_counts" not in st.session_state:
    st.session_state.mbti_counts = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}

# ---------------------------------------------------------
# 5. PAGE 01 — HOME
# ---------------------------------------------------------
if st.session_state.step == "home":
    with st.container(border=True):
        st.markdown(
            """
            <div style="text-align: center; margin-top: 14px; margin-bottom: 8px;">
                <span style="font-size: 1.8rem; margin: 0 6px;">🧭</span>
                <span style="font-size: 2.3rem; margin: 0 6px;">🚢</span>
                <span style="font-size: 1.8rem; margin: 0 6px;">📦</span>
                <span style="font-size: 1.5rem; margin: 0 6px;">✈️</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown('<div class="main-title">TRADE-MBTI</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">20개의 글로벌 무역 실무 상황으로 진단하는 나의 직무 성향</div>', unsafe_allow_html=True)

        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 24px;">
                <span class="category-badge">🌎 해외영업</span>
                <span class="category-badge">🛒 구매/조달</span>
                <span class="category-badge">📦 수출입관리</span>
                <span class="category-badge">📄 무역사무</span>
                <span class="category-badge">🚚 물류/SCM</span>
                <span class="category-badge">🔎 시장조사</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <p style="color: #4B5563; line-height: 1.75; max-width: 540px; margin: 0 auto 32px auto; text-align: center; font-size: 0.96rem;">
            신용장(L/C), 포워더 선복 부킹, 통관 규제, 원가 네고 등<br>
            실제 무역 현장의 20가지 딜레마를 분석하여<br>
            <b>최적 직무(1위)와 확장 직무(2·3위)</b>, 그리고 <b>MBTI 4축 레이더 분석</b>을 도출합니다.
            </p>
            """,
            unsafe_allow_html=True
        )

        if st.button("진단 시작하기 🚀", type="primary", use_container_width=True):
            st.session_state.step = "test"
            st.session_state.q_idx = 0
            st.session_state.scores = {job: 0 for job in JOBS.keys()}
            st.session_state.mbti_counts = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
            st.rerun()

# ---------------------------------------------------------
# 6. PAGE 02 — TEST
# ---------------------------------------------------------
elif st.session_state.step == "test":
    curr_idx = st.session_state.q_idx
    total_q = len(QUESTIONS)
    curr_data = QUESTIONS[curr_idx]

    progress = (curr_idx + 1) / total_q
    st.progress(progress)

    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.caption(f"Question {curr_idx + 1:02d} / {total_q:02d}")
    with col_r:
        st.markdown(f"<p style='text-align: right; color: #4B5563; font-size: 0.85rem; margin: 0;'>{int(progress * 100)}% 진행</p>", unsafe_allow_html=True)

    st.write("")

    with st.container(border=True):
        st.markdown(f'<span class="category-badge">{curr_data["cat"]}</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="question-text">{curr_data["q"]}</div>', unsafe_allow_html=True)

        opt_a_text, opt_a_weights, opt_a_mbti = curr_data["options"][0]
        opt_b_text, opt_b_weights, opt_b_mbti = curr_data["options"][1]

        if st.button(f"① {opt_a_text}", key=f"opt_a_{curr_idx}", use_container_width=True):
            for job, w in opt_a_weights.items():
                st.session_state.scores[job] += w
            st.session_state.mbti_counts[opt_a_mbti] += 1

            if curr_idx + 1 < total_q:
                st.session_state.q_idx += 1
            else:
                st.session_state.step = "result"
            st.rerun()

        st.write("")

        if st.button(f"② {opt_b_text}", key=f"opt_b_{curr_idx}", use_container_width=True):
            for job, w in opt_b_weights.items():
                st.session_state.scores[job] += w
            st.session_state.mbti_counts[opt_b_mbti] += 1

            if curr_idx + 1 < total_q:
                st.session_state.q_idx += 1
            else:
                st.session_state.step = "result"
            st.rerun()

# ---------------------------------------------------------
# 7. PAGE 03 & 04 — RESULT
# ---------------------------------------------------------
elif st.session_state.step == "result":
    st.balloons()

    scores = st.session_state.scores
    mbti_counts = st.session_state.mbti_counts
    max_possible_raw = max(scores.values()) if max(scores.values()) > 0 else 1

    ranked_jobs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top1_name, _ = ranked_jobs[0]
    top2_name, _ = ranked_jobs[1]
    top3_name, _ = ranked_jobs[2]
    top_job_meta = JOBS[top1_name]

    normalized_scores = {}
    for job, raw_val in ranked_jobs:
        score_pct = int((raw_val / max_possible_raw) * 94)
        score_pct = max(score_pct, 48)
        normalized_scores[job] = score_pct

    e_ratio = int((mbti_counts["E"] / 5) * 100)
    s_ratio = int((mbti_counts["S"] / 5) * 100)
    t_ratio = int((mbti_counts["T"] / 5) * 100)
    j_ratio = int((mbti_counts["J"] / 5) * 100)

    mbti_res = ""
    mbti_res += "E" if mbti_counts["E"] >= mbti_counts["I"] else "I"
    mbti_res += "S" if mbti_counts["S"] >= mbti_counts["N"] else "N"
    mbti_res += "T" if mbti_counts["T"] >= mbti_counts["F"] else "F"
    mbti_res += "J" if mbti_counts["J"] >= mbti_counts["P"] else "P"

    # [1] 1순위 대표 직무 카드
    with st.container(border=True):
        st.markdown(
            f"""
            <div id="capture-area" style="background-color: #FFFFFF; padding: 20px; border-radius: 12px;">
                <p style="text-align: center; letter-spacing: 0.15em; font-weight: 700; color: #059669; font-size: 0.85rem; margin: 0 0 6px 0;">✦ YOUR BEST TRADE TYPE ✦</p>
                <div style="text-align: center; font-size: 3.4rem; margin: 4px 0;">{top_job_meta["icon"]}</div>
                <h1 style="text-align: center; font-size: 2.1rem; color: #064E3B; margin: 0 0 4px 0;">{top1_name}형 ({mbti_res})</h1>
                <p style="text-align: center; color: #4B5563; font-weight: 600; font-size: 1.05rem; margin-bottom: 20px;">"{top_job_meta["tagline"]}"</p>
                <div style="background-color: #ECFDF5; border-radius: 12px; padding: 18px; text-align: left; margin-bottom: 18px; border: 1px solid #A7F3D0;">
                    <p style="color: #065F46; line-height: 1.6; margin: 0; font-size: 0.95rem;">
                        {top_job_meta["desc"]}
                    </p>
                </div>
                <div style="text-align: center; margin-bottom: 8px;">
                    {''.join([f'<span class="strength-tag">#{s}</span>' for s in top_job_meta["strengths"]])}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        components.html(
            """
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
            <div style="text-align: center; margin-top: 10px;">
                <button id="download-btn" style="background-color: #10B981; color: white; border: none; padding: 10px 18px; border-radius: 8px; font-weight: 700; cursor: pointer; font-size: 0.9rem; box-shadow: 0 2px 6px rgba(16, 185, 129, 0.3);">
                    📸 결과 카드 이미지 저장하기
                </button>
            </div>
            <script>
            document.getElementById('download-btn').addEventListener('click', function() {
                const target = window.parent.document.getElementById('capture-area');
                if (target) {
                    html2canvas(target, { scale: 2 }).then(canvas => {
                        const link = document.createElement('a');
                        link.download = 'trade_mbti_result.png';
                        link.href = canvas.toDataURL('image/png');
                        link.click();
                    });
                }
            });
            </script>
            """,
            height=60
        )

    # [2] 4축 레이더 차트 (Matplotlib + st.pyplot)
    with st.container(border=True):
        st.markdown('<h3 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 4px; color: #064E3B;">🧭 나의 무역 MBTI 성향 다이어그램</h3>', unsafe_allow_html=True)
        st.caption("각 축의 100%에 가까울수록 해당 지표의 행동 성향이 뚜렷함을 나타냅니다.")

        # 레이더 차트 데이터 생성
        labels = [
            f'E (외향: {e_ratio}%)', 
            f'S (감각: {s_ratio}%)', 
            f'T (사고: {t_ratio}%)', 
            f'J (판단: {j_ratio}%)'
        ]
        values = [e_ratio, s_ratio, t_ratio, j_ratio]
        
        # 각도 계산 (4각 다이어그램)
        num_vars = len(labels)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        
        # 폐곡선 처리
        values += values[:1]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(4.5, 4.5), subplot_kw=dict(polar=True))
        fig.patch.set_facecolor('#FFFFFF')
        ax.set_facecolor('#FFFFFF')
        
        # 12시 방향을 시작점으로 회전
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        
        # 눈금 및 축 설정
        ax.set_ylim(0, 100)
        ax.set_yticks([25, 50, 75, 100])
        ax.set_yticklabels(['25%', '50%', '75%', '100%'], color='#94A3B8', size=8)
        ax.grid(color='#E2E8F0', linestyle='--', linewidth=0.8)
        
        # 각 축 라벨
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, size=9.5, weight='bold', color='#065F46')
        
        # 다각형 및 영역 채우기
        ax.plot(angles, values, color='#059669', linewidth=2.2, linestyle='solid')
        ax.fill(angles, values, color='#10B981', alpha=0.3)
        ax.scatter(angles[:-1], values[:-1], color='#047857', s=45, zorder=10)
        
        st.pyplot(fig)
        plt.close(fig)

    # [3] 추천 직무 맞춤 채용공고 바로가기
    with st.container(border=True):
        st.markdown(f'<h3 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 14px; color: #064E3B;">💼 {top1_name} 실시간 채용공고 보러가기</h3>', unsafe_allow_html=True)
        st.caption(f"주요 채용 포털의 실시간 '{top1_name}' 공고를 즉시 확인해 보세요.")

        url_saramin = f"https://www.saramin.co.kr/zf_user/search?searchword={top1_name}"
        url_jobkorea = f"https://www.jobkorea.co.kr/Search/?stext={top1_name}"
        url_wanted = f"https://www.wanted.co.kr/search?query={top1_name}"

        link_col1, link_col2, link_col3 = st.columns(3)
        with link_col1:
            st.link_button("사람인 공고 🔗", url_saramin, use_container_width=True)
        with link_col2:
            st.link_button("잡코리아 공고 🔗", url_jobkorea, use_container_width=True)
        with link_col3:
            st.link_button("원티드 공고 🔗", url_wanted, use_container_width=True)

    # [4] 상위 1, 2, 3순위 직무 추천
    with st.container(border=True):
        st.markdown('<h3 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 16px; color: #064E3B;">🏆 나의 TOP 3 추천 직무 포트폴리오</h3>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f"""
                <div class="top3-box top1-box">
                    <span style="font-size: 0.8rem; font-weight: 700; color: #059669; background-color: #D1FAE5; padding: 2px 8px; border-radius: 9999px;">1순위 (최적)</span>
                    <div style="font-size: 2rem; margin: 8px 0 4px 0;">{JOBS[top1_name]["icon"]}</div>
                    <div style="font-weight: 800; font-size: 1.05rem; color: #064E3B;">{top1_name}</div>
                    <div style="font-size: 0.95rem; font-weight: 700; color: #059669; margin-top: 4px;">적합도 {normalized_scores[top1_name]}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div class="top3-box top2-box">
                    <span style="font-size: 0.8rem; font-weight: 700; color: #4B5563; background-color: #E2E8F0; padding: 2px 8px; border-radius: 9999px;">2순위 (차선)</span>
                    <div style="font-size: 2rem; margin: 8px 0 4px 0;">{JOBS[top2_name]["icon"]}</div>
                    <div style="font-weight: 800; font-size: 1.05rem; color: #1E293B;">{top2_name}</div>
                    <div style="font-size: 0.95rem; font-weight: 700; color: #4B5563; margin-top: 4px;">적합도 {normalized_scores[top2_name]}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                f"""
                <div class="top3-box top3-box-sub">
                    <span style="font-size: 0.8rem; font-weight: 700; color: #6B7280; background-color: #F1F5F9; padding: 2px 8px; border-radius: 9999px;">3순위 (잠재)</span>
                    <div style="font-size: 2rem; margin: 8px 0 4px 0;">{JOBS[top3_name]["icon"]}</div>
                    <div style="font-weight: 800; font-size: 1.05rem; color: #334155;">{top3_name}</div>
                    <div style="font-size: 0.95rem; font-weight: 700; color: #6B7280; margin-top: 4px;">적합도 {normalized_scores[top3_name]}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # [5] 6대 직무 전체 적합도 그래프
    with st.container(border=True):
        st.markdown('<h3 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 20px; color: #064E3B;">📊 6대 무역 직무 적합도 비교</h3>', unsafe_allow_html=True)
        for rank, (job, pct) in enumerate(normalized_scores.items(), 1):
            medal = "🥇 " if rank == 1 else "🥈 " if rank == 2 else "🥉 " if rank == 3 else f"{rank}. "
            col_name, col_bar = st.columns([2, 5])
            with col_name:
                st.markdown(f"<p style='font-size: 0.95rem; font-weight: 600; margin-top: 4px;'>{medal}{JOBS[job]['icon']} {job}</p>", unsafe_allow_html=True)
            with col_bar:
                st.progress(pct / 100)
                st.caption(f"적합도 **{pct}%**")

    # [6] MBTI 4축 실무 리포트
    with st.container(border=True):
        st.markdown(f'<h3 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 8px; color: #064E3B;">🧭 무역 실무 성향 리포트 ({mbti_res})</h3>', unsafe_allow_html=True)
        st.markdown('<p style="color: #4B5563; font-size: 0.9rem; margin-bottom: 20px;">자기소개서 작성 및 면접 시 아래 실무 강점과 보완 포인트를 활용하세요.</p>', unsafe_allow_html=True)

        for dim in mbti_res:
            info = MBTI_DIM_DETAILS[dim]
            st.markdown(
                f"""
                <div class="mbti-dim-card">
                    <div style="font-size: 0.95rem; font-weight: 700; color: #059669; margin-bottom: 4px;">
                        {info["title"]} <span style="font-size: 0.8rem; color: #6B7280; font-weight: 400;">(어울리는 직무: {info["fit_jobs"]})</span>
                    </div>
                    <div style="font-size: 0.9rem; color: #1F2937; line-height: 1.5; margin-bottom: 6px;">
                        <b>💪 실무 핵심 강점:</b> {info["strength"]}
                    </div>
                    <div style="font-size: 0.9rem; color: #D97706; line-height: 1.5;">
                        <b>⚠️ 주의 및 보완점:</b> {info["weakness"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # [7] 1위 직무 실무 업무 카드
    with st.container(border=True):
        st.markdown(f'<h3 style="font-size: 1.15rem; font-weight: 700; margin-bottom: 16px; color: #064E3B;">💡 {top1_name} 추천 실무 업무</h3>', unsafe_allow_html=True)
        for task in top_job_meta["tasks"]:
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <span style="color: #10B981; margin-right: 8px; font-weight: bold;">✔</span>
                <span style="color: #1F2937; font-size: 0.95rem;">{task}</span>
            </div>
            """, unsafe_allow_html=True)

    # 다시 하기 버튼
    st.write("")
    if st.button("테스트 다시 하기 🔄", use_container_width=True):
        st.session_state.step = "home"
        st.session_state.q_idx = 0
        st.session_state.scores = {job: 0 for job in JOBS.keys()}
        st.session_state.mbti_counts = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
        st.rerun()