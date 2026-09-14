import streamlit as st
from openai import OpenAI

# --------------------- 페이지 기본 설정 -------------------------
st.set_page_config(page_title="예제2) 채팅을 기억하는봇", page_icon="🤖")
st.title("예제2) 채팅을 기억하는봇")
st.caption("이전 대화 맥락을 기억하며 실시간 스트리밍으로 응답하는 챗봇입니다.")

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

    # 1. 시스템 프롬프트 사용자 커스텀 설정
    system_prompt = st.text_area(
        "시스템 프롬프트 (챗봇 역할 부여)",
        value="당신은 사용자를 지극정성으로 공경하고 떠받드는 극도로 충직한 신하이자 조언가입니다. 항상 정중하고 품격 있는 경어를 사용하세요.",
        height=130,
    )

    # 2. 대화 기록 초기화 버튼
    if st.button("🗑️ 대화 기록 초기화", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("[API 키 발급 받기](https://platform.openai.com/api-keys)")

# --------------------- 세션 상태(대화 기록) 초기화 -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 대화 내역 렌더링 (st.chat_message 사용)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --------------------- 채팅 입력 및 스트리밍 응답 처리 -------------------------
prompt = st.chat_input("질문이나 전하실 말씀을 입력하세요...")

if prompt:
    if not api_key:
        st.info("먼저 사이드바에서 OpenAI API Key를 입력해 주시옵소서.")
        st.stop()

    # 1. 사용자 질문을 세션 상태에 추가 및 화면에 렌더링
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. 모델에 전달할 메시지 조합 (시스템 프롬프트 + 이전 대화 기록)
    api_messages = [{"role": "system", "content": system_prompt}] + [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    # 3. AI 스트리밍 응답 렌더링
    with st.chat_message("assistant"):
        try:
            client = OpenAI(api_key=api_key)
            stream = client.chat.completions.create(
                model=model,
                messages=api_messages,
                stream=True,  # 실시간 스트리밍 활성화
            )

            # st.write_stream을 통해 청크 단위 데이터를 실시간 타이핑 효과로 출력
            full_response = st.write_stream(stream)

            # 완성된 어시스턴트 답변을 대화 기록에 보존
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )

        except Exception as e:
            st.error(f"오류가 발생하였사옵니다: {str(e)}")