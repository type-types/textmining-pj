import os
from dotenv import load_dotenv
from openai import OpenAI
import time
import re

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
            max_tokens=5,  # 0 또는 1만 출력하면 되므로 매우 짧게 설정
            temperature=0.1  # 일관성을 위해 낮은 temperature
        )
        
        result = response.choices[0].message.content.strip()
        
        # 결과가 0 또는 1인지 확인하고 정수로 변환
        if result in ['0', '1']:
            return int(result)
        else:
            # 예상치 못한 응답의 경우 기본적으로 0 (계속 진행)
            print(f"예상치 못한 응답: {result}, 기본값 0 반환")
            return 0
            
    except Exception as e:
        print(f"확인 상태 판단 중 오류: {e}")
        return 0  # 오류 시 기본적으로 0 반환

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
            max_tokens=50,  # 구문 출력을 위해 약간 늘림
            temperature=0.1   # 일관성을 위해 낮은 temperature
        )
        
        summary = response.choices[0].message.content.strip()
        return summary
        
    except Exception as e:
        print(f"요약 생성 중 오류: {e}")
        return "요약 생성 실패"

# 대화 기록을 저장할 리스트 초기화
messages = [
    {"role": "system", "content": "당신은 관공서 민원 챗봇입니다. 민원인이 정확히 무엇을 원하는지 파악하는 것이 임무입니다.\n\n**응답 규칙:**\n1. 한 번에 질문은 반드시 하나만 하세요.\n2. 질문은 짧고 간결하게 하세요.\n3. 여러 질문을 동시에 하지 마세요.\n4. 간단명료한 언어를 사용하세요.\n5. 요청이 파악되면 간단히 요약하고 '맞을까요?'로 확인하세요.\n6. 직접적인 답변이나 해결책은 제공하지 마세요.\n\n**예시:**\n- 좋음: '어떤 종류의 문제인가요?'\n- 나쁨: '어떤 종류의 문제인가요? 언제 발생했나요? 어디에서 일어났나요?'\n\n항상 한국어로 응답하세요."},
]

print("저는 관공서 챗봇 관공이입니다. 무엇을 도와드릴까요?")
print("(종료하려면 'quit' 또는 'exit' 입력)")

# 대화 루프
while True:
    # 사용자 입력 받기
    user_input = input("나: ")

    # 사용자 입력 출력
    print(f"나: {user_input}")

    # 종료 조건 확인
    if user_input.lower() in ['quit', 'exit']:
        print("대화를 종료합니다.")
        break

    # 사용자 메시지를 대화 기록에 추가
    messages.append({"role": "user", "content": user_input})

    # LLM을 통해 다음 단계로 넘어가도 되는지 확인
    confirmation_status = check_confirmation_status(messages)
    
    if confirmation_status == 1:
        # 챗봇이 확인 질문했고 사용자가 짧은 긍정 답변함 - 다음 단계로 진행
        print("챗봇: 요청이 확인되었습니다. 다음 단계로 진행합니다.")
        
        # 요약 LLM 호출하여 핵심 구문 추출
        print("\n--- 요약 진행 중 ---")
        summary_phrase = summarize_conversation(messages)
        print(f"핵심 구문: {summary_phrase}")
        
        # TODO: 이후 추출된 구문을 활용한 추가 처리 로직
        # 예: RAG 시스템에 구문 전달, 관련 문서 검색 등
        
        break  # 대화 종료
        
    else:
        # 아직 확인 조건을 만족하지 않음 - 기존 모델 계속 사용
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=200,  # 짧은 응답을 위해 토큰 수 줄임
                temperature=0.2
            )

            assistant_response = response.choices[0].message.content
            print(f"챗봇: {assistant_response}")

            # 모델 응답을 대화 기록에 추가
            messages.append({"role": "assistant", "content": assistant_response})

            time.sleep(0.5)

        except Exception as e:
            print(f"API 호출 중 오류 발생: {e}")
            break