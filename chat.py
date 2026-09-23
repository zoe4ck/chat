import streamlit as st
from openai import OpenAI

# 1. 우사기 분위기(노란 토끼와 활기찬 느낌)를 위한 페이지 설정
st.set_page_config(
    page_title="우사기의 대화방", 
    page_icon="🐰"
)

# 먼작귀 우사기 느낌을 주는 제목과 안내 문구
st.title("💛 토끼 소동쟁이 우사기 🐰")
st.markdown("### *야하~!* 우사기와 신나는 대화를 나눠봐요! ✨")

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

# 4. 우사기의 성격과 말투(우사기어)를 지정하는 시스템 프롬프트
system_prompt = (
    "너는 만화 '먼작귀(치이카와)'의 캐릭터 '우사기'야. "
    "대답할 때는 반드시 우사기 특유의 추임새인 '야하~!', '우라!', '삐릿-', '으챠-' 같은 감탄사와 "
    "귀여운 이모지(🐰, 💛, ✨, 🪄 등)를 섞어서 우사기어 느낌으로만 대답해야 해. "
    "말이 짧고 장난스럽고 자유로우며, 엉뚱한 행동을 하거나 기분 내키는 대로 대답하는 토끼처럼 행동해 줘."
)

# 5. 이전 대화 기억을 위한 세션 상태 초기화
if "usagi_messages" not in st.session_state:
    st.session_state.usagi_messages = [
        {"role": "system", "content": system_prompt}
    ]

# 6. 이전 대화 기록 화면에 출력 (시스템 메시지 제외)
for message in st.session_state.usagi_messages:
    if message["role"] != "system":
        with st.chat_message(message["role"], avatar="🐰" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])

# 7. 사용자 입력 받기
if user_input := st.chat_input("우사기에게 말을 걸어보세요! (야하~!)"):
    
    # 사용자 메시지 기록 및 화면 표시
    st.session_state.usagi_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # 우사기(AI)의 답변 말풍선 준비
    with st.chat_message("assistant", avatar="🐰"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # 8. 우사기 캐릭터로 스트리밍 응답 요청 (모델 이름 원본 유지)
            response = client.chat.completions.create(
                model="gemini-3.5-flash-lite",
                messages=st.session_state.usagi_messages,
                stream=True,
            )
            
            # 실시간으로 글자 출력
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            # 최종 완성된 답변 표시
            message_placeholder.markdown(full_response)
            
            # 대화 기록에 우사기 답변 추가
            st.session_state.usagi_messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            # 9. 오류 발생 시 우사기 감성에 맞는 친절한 안내 문구 표시
            message_placeholder.error("🐰💦 야하... (앗, 풀숲 연결이 이상해! 잠시 후에 다시 해라!)")
