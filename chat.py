import streamlit as st
from openai import OpenAI

# 페이지 기본 설정 (제목과 아이콘)
st.set_page_config(page_title="AI 정보 선생님", page_icon="🤖")

st.title("🤖 친절한 정보 선생님")
st.write("궁금한 점이 있으면 언제든 편하게 물어보세요!")

# 1. 비밀 금고(st.secrets)에서 Gemini API 키 불러오기
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("비밀 금고(secrets.toml)에 GEMINI_API_KEY가 설정되어 있지 않습니다.")
    st.stop()

# 2. OpenAI 라이브러리를 통해 Gemini API에 연결 (base_url과 모델명 고정)
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# 3. AI의 성격 지정 (시스템 프롬프트)
system_prompt = (
    "너는 중고등학생에게 설명하는 친절한 정보 선생님이야. "
    "어려운 말은 쉬운 말로 바꿔 주고, 반드시 순수 한국어로만 답해"
)

# 4. 이전 대화 기억을 위한 세션 상태(st.session_state) 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt}
    ]

# 5. 기존에 나눈 대화 기록 화면에 출력 (시스템 메시지는 제외)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 6. 사용자 입력 받기
if user_input := st.chat_input("선생님께 궁금한 것을 물어보세요!"):
    
    # 사용자가 입력한 메시지를 대화 기록에 추가
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 사용자 말풍선을 화면에 바로 표시
    with st.chat_message("user"):
        st.markdown(user_input)

    # AI의 답변을 출력할 말풍선 준비
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # 7. OpenAI 클라이언트로 스트리밍 응답 요청 (모델 이름 변경 금지)
            response = client.chat.completions.create(
                model="gemini-2.5-flash-lite",
                messages=st.session_state.messages,
                stream=True,  # 글자가 실시간으로 나오도록 설정
            )
            
            # 실시간으로 글자를 받아와 화면에 한 글자씩 이어붙이기
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            # 최종 완성된 답변 표시
            message_placeholder.markdown(full_response)
            
            # 8. AI의 답변도 대화 기록에 추가 (이전 대화 기억용)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            # 9. 오류 발생 시 빨간 화면 대신 친절한 한국어 안내 문구 표시
            message_placeholder.error("죄송해요, 답변을 가져오는 중에 문제가 생겼어요. 잠시 후에 다시 시도해 주세요!")
