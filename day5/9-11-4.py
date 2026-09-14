import streamlit as st
import pandas as pd
from openai import OpenAI

# --------------------- 페이지 기본 설정 -------------------------
st.set_page_config(page_title="예제3: 파일 업로드 문서 요약 앱", page_icon="📄")
st.title("📄 예제3: 파일 업로드 문서 요약 앱")
st.caption("CSV 또는 Markdown 문서를 업로드하고, 내용 요약 및 데이터 분석에 대해 자유롭게 질문해 보세요.")

# --------------------- 사이드바 설정 -------------------------
with st.sidebar:
    st.header("⚙️ 챗봇 설정")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="sk-로 시작하는 OpenAI API key를 입력하세요",
    )
    model = st.selectbox(
        "모델 선택",
        ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"],
        index=0,
    )

    # 1. 파일 업로드 위젯 (CSV, MD 지원)
    uploaded_file = st.file_uploader(
        "문서 업로드 (CSV, MD)",
        type=["csv", "md"],
        help="요약 및 분석할 파일을 업로드하세요",
    )

    # 2. 시스템 프롬프트 사용자 커스텀 설정
    default_system_prompt = (
        "당신은 문서 분석 및 데이터 요약 전문가이자, 사용자를 지극정성으로 공경하는 충직한 조언가입니다. "
        "제공된 문서 내용을 바탕으로 사용자의 질문에 정확하고 명쾌하게 답변하며, 항상 정중하고 품격 있는 경어를 사용하세요."
    )
    system_prompt = st.text_area(
        "시스템 프롬프트 (역할 부여)",
        value=default_system_prompt,
        height=130,
    )

    # 3. 대화 기록 초기화 버튼
    if st.button("🗑️ 대화 기록 초기화", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("[API 키 발급 받기](https://platform.openai.com/api-keys)")

# --------------------- 업로드된 파일 내용 파싱 -------------------------
file_context = ""
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            st.write(f"📊 **업로드된 파일:** `{uploaded_file.name}` (총 {len(df):,}개 행, {len(df.columns)}개 열)")
            with st.expander("데이터 미리보기 (상위 5개 행)", expanded=False):
                st.dataframe(df.head())
            # LLM 컨텍스트 전달용 요약 정보 (기본 정보 + 상위 데이터)
            file_context = (
                f"파일명: {uploaded_file.name}\n"
                f"데이터 구조: 총 {len(df)}행, {len(df.columns)}열\n"
                f"컬럼 목록: {list(df.columns)}\n\n"
                f"[데이터 내용 샘플]\n{df.head(50).to_markdown(index=False)}"
            )
        elif uploaded_file.name.endswith(".md"):
            raw_text = uploaded_file.read().decode("utf-8")
            st.write(f"📝 **업로드된 파일:** `{uploaded_file.name}` ({len(raw_text):,} 자)")
            with st.expander("문서 내용 미리보기", expanded=False):
                st.markdown(raw_text)
            file_context = (
                f"파일명: {uploaded_file.name}\n\n"
                f"[문서 전문]\n{raw_text}"
            )
    except Exception as e:
        st.error(f"파일을 읽는 도중 오류가 발생했습니다: {str(e)}")
else:
    st.info("👈 좌측 사이드바에서 분석하실 CSV 또는 MD 파일을 먼저 업로드해 주시옵소서.")

# --------------------- 세션 상태(대화 기록) 초기화 -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 대화 내역 렌더링 (st.chat_message 사용)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --------------------- 채팅 입력 및 스트리밍 응답 처리 -------------------------
prompt = st.chat_input("문서 요약 요청이나 궁금한 점을 입력하세요 (예: 전체 핵심 내용 요약해줘)...")

if prompt:
    if not api_key:
        st.info("먼저 사이드바에서 OpenAI API Key를 입력해 주시옵소서.")
        st.stop()

    if not file_context:
        st.warning("분석할 파일이 업로드되지 않았사옵니다. 사이드바에서 파일을 먼저 올려주시옵소서.")
        st.stop()

    # 1. 사용자 질문을 세션 상태에 추가 및 화면에 렌더링
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. 문서 컨텍스트를 결합한 시스템 프롬프트 구성
    combined_system_prompt = (
        f"{system_prompt}\n\n"
        f"--- [참고 문서 정보] ---\n"
        f"{file_context}\n"
        f"------------------------\n"
        "위 문서 정보를 토대로 사용자의 질문에 정확하고 상세히 답변하세요."
    )

    # 3. 모델에 전달할 메시지 조합 (시스템 프롬프트 + 이전 대화 기록)
    api_messages = [{"role": "system", "content": combined_system_prompt}] + [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    # 4. AI 스트리밍 응답 렌더링
    with st.chat_message("assistant"):
        try:
            client = OpenAI(api_key=api_key)
            stream = client.chat.completions.create(
                model=model,
                messages=api_messages,
                stream=True,  # 실시간 스트리밍 활성화
            )

            # st.write_stream을 통해 실시간 스트리밍 출력
            full_response = st.write_stream(stream)

            # 완성된 답변을 대화 기록에 보존
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )

        except Exception as e:
            st.error(f"오류가 발생하였사옵니다: {str(e)}")