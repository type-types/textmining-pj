import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import time

# .env 파일에서 환경변수 불러오기
load_dotenv()

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def check_confirmation_status(messages):
    """
    대화 기록을 분석하여 다음 조건을 모두 만족하는지 판단:
    1. 챗봇이 확인 질문("이게 맞아?", "맞을까요?" 등)을 했는가?
    2. 사용자가 그 직후에 짧은 긍정 대답("응 맞아", "네" 등)을 했는가?
    
    Returns:
        0: 위 조건을 만족하지 않음 (기존 모델 계속 사용)
        1: 위 조건을 모두 만족함 (다음 단계로 진행)
    """
    try:
        # 최소 2개의 메시지가 있어야 함 (챗봇 확인 질문 + 사용자 답변)
        if len(messages) < 2:
            return 0
            
        # 마지막 2개 메시지 확인 (챗봇 질문 -> 사용자 답변)
        last_bot_message = None
        last_user_message = None
        
        # 뒤에서부터 찾기
        for i in range(len(messages) - 1, -1, -1):
            if messages[i]['role'] == 'user' and last_user_message is None:
                last_user_message = messages[i]['content']
            elif messages[i]['role'] == 'assistant' and last_user_message is not None and last_bot_message is None:
                last_bot_message = messages[i]['content']
                break
        
        if not last_bot_message or not last_user_message:
            return 0
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 대화 분석 전문가입니다. 주어진 챗봇의 마지막 메시지와 사용자의 마지막 응답을 분석하여 다음 조건을 모두 만족하는지 판단하세요:\n\n1. 챗봇이 사용자에게 확인을 요청하는 질문을 했는가? (예: '맞을까요?', '이게 맞아?', '확인해 주세요' 등)\n2. 사용자가 그에 대해 짧고 명확한 긍정적 답변을 했는가? (예: '네', '맞아요', '응 맞아', '맞습니다' 등)\n\n두 조건을 모두 만족하면 '1'을, 그렇지 않으면 '0'을 출력하세요. 오직 숫자만 출력하세요."},
                {"role": "user", "content": f"챗봇의 마지막 메시지: {last_bot_message}\n\n사용자의 마지막 응답: {last_user_message}"}
            ],
            max_tokens=5,
            temperature=0.1
        )
        
        result = response.choices[0].message.content.strip()
        
        if result in ['0', '1']:
            return int(result)
        else:
            print(f"예상치 못한 응답: {result}, 기본값 0 반환")
            return 0
            
    except Exception as e:
        st.error(f"확인 상태 판단 중 오류: {e}")
        return 0

def summarize_conversation(messages):
    """
    전체 대화 내역에서 핵심 단어들을 조합한 의미있는 구문으로 요약하는 함수
    
    Args:
        messages: 전체 대화 기록 리스트
        
    Returns:
        str: 핵심 단어들로 조합된 간결한 구문
    """
    try:
        # 시스템 메시지를 제외한 사용자-챗봇 대화만 추출
        conversation_text = ""
        for msg in messages[1:]:  # 첫 번째는 시스템 메시지이므로 제외
            if msg['role'] == 'user':
                conversation_text += f"사용자: {msg['content']}\n"
            elif msg['role'] == 'assistant':
                conversation_text += f"챗봇: {msg['content']}\n"
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 민원 요약 전문가입니다. 주어진 대화에서 사용자의 요청사항을 **핵심 단어들을 조합한 간결한 구문**으로 요약하세요.\n\n**요약 규칙:**\n1. 핵심 단어들을 의미있게 조합하여 하나의 구문을 만드세요\n2. 2-4개의 단어로 구성된 간결한 구문으로 작성하세요\n3. 명사+명사, 명사+동사, 형용사+명사 등의 조합을 활용하세요\n4. 불필요한 조사나 어미는 제거하세요\n5. 관공서 업무와 관련된 구문으로 작성하세요\n\n**예시:**\n- 입력: 고양이가 아파서 보호소에 연락하고 싶어요\n- 출력: 동물보호소 연락\n\n- 입력: 친자확인을 받고 싶어요\n- 출력: 친자확인 문의\n\n- 입력: 전입신고를 하려고 해요\n- 출력: 전입신고 접수\n\n간결하고 명확한 구문만 출력하세요."},
                {"role": "user", "content": f"다음 대화에서 핵심 구문을 추출해주세요:\n\n{conversation_text}"}
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        summary = response.choices[0].message.content.strip()
        return summary
        
    except Exception as e:
        st.error(f"요약 생성 중 오류: {e}")
        return "요약 생성 실패"

# Streamlit 페이지 설정
st.set_page_config(
    page_title="관공서 민원 챗봇",
    page_icon="🏛️",
    layout="wide"
)

# 제목 및 설명
st.title("🏛️ 관공서 민원 챗봇 - 관공이")
st.markdown("민원 내용을 정확히 파악하여 도움을 드리겠습니다.")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "당신은 관공서 민원 챗봇입니다. 민원인이 정확히 무엇을 원하는지 파악하는 것이 임무입니다.\n\n**응답 규칙:**\n1. 한 번에 질문은 반드시 하나만 하세요.\n2. 질문은 짧고 간결하게 하세요.\n3. 여러 질문을 동시에 하지 마세요.\n4. 간단명료한 언어를 사용하세요.\n5. 요청이 파악되면 간단히 요약하고 '맞을까요?'로 확인하세요.\n6. 직접적인 답변이나 해결책은 제공하지 마세요.\n\n**예시:**\n- 좋음: '어떤 종류의 문제인가요?'\n- 나쁨: '어떤 종류의 문제인가요? 언제 발생했나요? 어디에서 일어났나요?'\n\n항상 한국어로 응답하세요."},
    ]

if "conversation_ended" not in st.session_state:
    st.session_state.conversation_ended = False

if "summary_result" not in st.session_state:
    st.session_state.summary_result = None

# 대화 기록 표시 (시스템 메시지 제외)
for message in st.session_state.messages[1:]:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message("assistant"):
            st.write(message["content"])

# 대화가 끝났을 때 요약 결과 표시
if st.session_state.conversation_ended and st.session_state.summary_result:
    st.success("✅ 요청이 확인되었습니다!")
    
    with st.container():
        st.markdown("### 📋 요약 결과")
        st.info(f"**핵심 구문:** {st.session_state.summary_result}")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔄 새로운 대화 시작", type="primary"):
                # 세션 상태 초기화
                st.session_state.messages = [st.session_state.messages[0]]  # 시스템 메시지만 유지
                st.session_state.conversation_ended = False
                st.session_state.summary_result = None
                st.rerun()
        
        with col2:
            if st.button("📄 상세 분석 보기"):
                with st.expander("상세 대화 분석", expanded=True):
                    st.markdown("**전체 대화 기록:**")
                    for i, msg in enumerate(st.session_state.messages[1:], 1):
                        role_name = "사용자" if msg["role"] == "user" else "챗봇"
                        st.markdown(f"**{i}. {role_name}:** {msg['content']}")

# 대화가 진행 중일 때만 입력 필드 표시
if not st.session_state.conversation_ended:
    # 사용자 입력
    if user_input := st.chat_input("무엇을 도와드릴까요?"):
        # 사용자 메시지 표시
        with st.chat_message("user"):
            st.write(user_input)
        
        # 사용자 메시지를 세션에 추가
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # 확인 상태 체크
        confirmation_status = check_confirmation_status(st.session_state.messages)
        
        if confirmation_status == 1:
            # 확인 조건을 만족함 - 다음 단계로 진행
            with st.chat_message("assistant"):
                st.write("요청이 확인되었습니다. 다음 단계로 진행합니다.")
            
            # 어시스턴트 메시지를 세션에 추가
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "요청이 확인되었습니다. 다음 단계로 진행합니다."
            })
            
            # 요약 진행
            with st.spinner("📝 요약을 생성하고 있습니다..."):
                summary_phrase = summarize_conversation(st.session_state.messages)
                st.session_state.summary_result = summary_phrase
                st.session_state.conversation_ended = True
            
            st.rerun()
            
        else:
            # 아직 확인 조건을 만족하지 않음 - 기존 모델 계속 사용
            try:
                with st.spinner("💭 답변을 생성하고 있습니다..."):
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=st.session_state.messages,
                        max_tokens=200,
                        temperature=0.2
                    )
                
                assistant_response = response.choices[0].message.content
                
                # 어시스턴트 메시지 표시
                with st.chat_message("assistant"):
                    st.write(assistant_response)
                
                # 어시스턴트 메시지를 세션에 추가
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                
            except Exception as e:
                st.error(f"API 호출 중 오류 발생: {e}")

# 사이드바에 사용 안내
with st.sidebar:
    st.markdown("## 📋 사용 안내")
    st.markdown("""
    **관공서 민원 챗봇 사용법:**
    
    1️⃣ **민원 내용 입력**
    - 궁금한 민원 사항을 입력해주세요
    
    2️⃣ **단계별 질문 응답**
    - 챗봇이 한 번에 하나씩 질문합니다
    - 간단하고 명확하게 답변해주세요
    
    3️⃣ **확인 단계**
    - 챗봇이 요약하고 "맞을까요?" 질문
    - "네", "맞아요" 등으로 확인
    
    4️⃣ **결과 확인**
    - 핵심 구문으로 요약된 결과 확인
    - 새로운 대화 시작 가능
    """)
    
    st.markdown("---")
    st.markdown("**💡 팁:**")
    st.markdown("""
    - 구체적으로 상황을 설명해주세요
    - 한 번에 여러 내용보다는 하나씩
    - 궁금한 점이 있으면 언제든 질문하세요
    """)
    
    # 대화 초기화 버튼 (사이드바)
    if st.button("🗑️ 대화 초기화", help="현재 대화를 모두 삭제하고 새로 시작합니다"):
        st.session_state.messages = [st.session_state.messages[0]]  # 시스템 메시지만 유지
        st.session_state.conversation_ended = False
        st.session_state.summary_result = None
        st.rerun() 