import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="나의 첫번째 챗봇", page_icon="🤖")
st.title("예제1) 나의 첫번째 챗봇")
st.caption("질문 하나 입력하면 OpenAI chat completions API 한번 호출, 답변을 받아오는 가장 단순한 방법")

# --------------------- 사이드바 API 및 모델 설정 -------------------------

with st.sidebar:
    st.header("설정")
    api_key = st.text_input("OpenAI API Key", type="password", help="sk-로 시작하는 OpenAI API key를 입력하세요")
    model = st.selectbox("모델 선택", ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"], index=0)
    st.markdown("[API 키 발급 받기](https://platform.openai.com/api-keys)")

# --------------------- 메인 화면 -------------------------

question = st.text_input("질문을 입력하세요", placeholder="예) 거울아 거울아 누가 세상에서 제일 예쁘니?")

if st.button("질문하기", type="primary"):
    if not api_key:
        st.error("OpenAI API Key를 입력하세요.")
    elif not question:
        st.error("질문을 입력하세요.")
    else:
        try:
            client = OpenAI(api_key=api_key)
            
            with st.spinner("답변을 생각하는 중입니다..."):
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "당신은 질문자를 지극정성으로 공경하고 떠받드는 극도로 충직한 신하이자 조언가입니다. 항상 정중하고 품격 있는 경어를 사용하세요."
                        },
                        {
                            "role": "user",
                            "content": question
                        }
                    ]
                )

            # 답변 출력
            answer = response.choices[0].message.content
            st.success("답변이 도착했습니다!")
            st.markdown(answer)

            # 토큰 사용량 정보 표시
            usage = response.usage
            st.divider()
            col1, col2, col3 = st.columns(3)
            col1.metric("입력 토큰 (Prompt)", f"{usage.prompt_tokens:,}개")
            col2.metric("출력 토큰 (Completion)", f"{usage.completion_tokens:,}개")
            col3.metric("총 사용 토큰 (Total)", f"{usage.total_tokens:,}개")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")