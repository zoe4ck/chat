import streamlit as st
from openai import OpenAI

# 1. 핑구 분위기(북극과 얼음)를 내기 위한 페이지 설정
st.set_page_config(
    page_title="핑구의 북극 대화방", 
    page_icon="🐧"
)

# 북극의 귀여운 느낌을 주는 제목과 안내 문구
st.title("🧊 펭귄 도시의 핑구 🐧")
st.markdown("### *Noot noot!* 핑구와 즐거운 대화를 나눠봐요! ❄️")

# 2. 비밀 금고(st.secrets)에서 Gemini API 키 불러오기
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("비밀 금고(secrets.toml)에 GEMINI_API_KEY가 설정되어 있지 않습니다.")
    st.stop()

# 3. OpenAI 라이브러리를 통해 Gemini API 연결
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# 4. 핑구의 성격과 말투(핑구어)를 지정하는 시스템 프롬프트
system_prompt = (
    "너는 만화 '핑구'의 주인공 핑구야. "
    "대답할 때는 반드시 펭귄 언어인 'Noot noot!' (또는 핑구 특유의 의아해하는 펭귄 소리)과 "
    "귀여운 이모지(🐧, 🧊, ❄️ 등)를 섞어서 핑구어 느낌으로만 대답해야 해. "
    "말끝마다 펭귄처럼 행동하고, 사람이 말을 걸면 신나거나 당황한 핑구처럼 핑구어로만 대답해 줘."
)

# 5. 이전 대화 기억을 위한 세션 상태 초기화
if "pingu_messages" not in st.session_state:
    st.session_state.pingu_messages = [
        {"role": "system", "content": system_prompt}
    ]

# 6. 이전 대화 기록 화면에 출력 (시스템 메시지 제외)
for message in st.session_state.pingu_messages:
    if message["role"] != "system":
        with st.chat_message(message["role"], avatar="🐧" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])

# 7. 사용자 입력 받기
if user_input := st.chat_input("핑구에게 말을 걸어보세요! (Noot noot!)"):
    
    # 사용자 메시지 기록 및 화면 표시
    st.session_state.pingu_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # 핑구(AI)의 답변 말풍선 준비
    with st.chat_message("assistant", avatar="🐧"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # 8. 핑구 캐릭터로 스트리밍 응답 요청 (모델 이름 유지)
            response = client.chat.completions.create(
                model="gemini-2.5-flash-lite",
                messages=st.session_state.pingu_messages,
                stream=True,
            )
            
            # 실시간으로 글자 출력
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            # 최종 완성된 답변 표시
            message_placeholder.markdown(full_response)
            
            # 대화 기록에 핑구 답변 추가
            st.session_state.pingu_messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            # 9. 오류 발생 시 핑구 감성에 맞는 친절한 안내 문구 표시
            message_placeholder.error("🐧💦 Noot... (앗, 얼음 나라 통신에 문제가 생겼어요! 잠시 후에 다시 시도해 주세요!)")
