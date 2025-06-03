# 🏛️ 관공서 민원 챗봇 - 관공이

OpenAI GPT를 활용한 스마트한 관공서 민원 상담 시스템입니다.

## ✨ 주요 기능

- **단계적 질문**: 한 번에 하나씩 질문하여 정확한 요구사항 파악
- **확인 시스템**: 사용자 확인을 통한 정확성 보장
- **핵심 구문 추출**: 대화 내용을 간결한 핵심 구문으로 요약
- **직관적 UI**: Streamlit 기반의 사용하기 쉬운 웹 인터페이스

## 🚀 설치 및 실행

### 1. 환경 준비

```bash
# 프로젝트 클론
git clone <repository-url>
cd textmining-pj

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 종속성 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env` 파일을 생성하고 OpenAI API 키를 설정하세요:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 앱 실행

```bash
streamlit run streamlit_app.py
```

앱이 실행되면 브라우저에서 `http://localhost:8501`로 접속하세요.

## 📖 사용법

### 기본 대화 흐름

1. **민원 내용 입력**: 궁금한 민원 사항을 입력하세요
2. **단계별 질문 응답**: 챗봇이 하나씩 질문하면 간단명료하게 답변하세요
3. **확인 단계**: 챗봇이 요약 후 "맞을까요?" 질문하면 "네", "맞아요" 등으로 확인
4. **결과 확인**: 핵심 구문으로 요약된 결과를 확인하세요

### 예시 대화

```
사용자: 전입신고를 하고 싶어요
챗봇: 언제 이사를 하셨나요?
사용자: 이번 주에 했어요
챗봇: 새 주소지가 같은 시/군/구 내인가요?
사용자: 아니요, 다른 시로 이사했어요
챗봇: 타 시군구로 이사하신 전입신고를 원하시는 것 맞을까요?
사용자: 네
챗봇: 요청이 확인되었습니다.
결과: 타 시군구 전입신고
```

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **AI Model**: OpenAI GPT-4o-mini
- **Backend**: Python
- **환경관리**: python-dotenv

## 📋 파일 구조

```
├── streamlit_app.py      # Streamlit 웹 앱
├── app.py               # 원본 콘솔 버전
├── requirements.txt     # 종속성 목록
├── .env                # 환경변수 (사용자가 생성)
└── README.md           # 이 파일
```

## ⚙️ 핵심 기능 설명

### 확인 상태 판단 (`check_confirmation_status`)

- 챗봇의 확인 질문과 사용자의 긍정 답변을 AI로 분석
- 조건 만족 시 다음 단계로 자동 진행

### 대화 요약 (`summarize_conversation`)

- 전체 대화에서 핵심 키워드 추출
- 2-4개 단어로 구성된 간결한 구문 생성
- 관공서 업무 맥락에 맞는 요약

## 🔧 사용자 정의

### 시스템 프롬프트 수정

`streamlit_app.py`의 `messages` 초기화 부분에서 시스템 메시지를 수정하여 챗봇의 행동을 변경할 수 있습니다.

### 스타일 커스터마이징

Streamlit의 `st.set_page_config()`에서 페이지 제목, 아이콘 등을 변경할 수 있습니다.

## 🚨 주의사항

- OpenAI API 키가 필요합니다
- 인터넷 연결이 필요합니다
- API 사용량에 따른 비용이 발생할 수 있습니다

## 🆘 문제 해결

### 일반적인 오류

1. **API 키 오류**: `.env` 파일의 API 키가 정확한지 확인
2. **종속성 오류**: `pip install -r requirements.txt` 재실행
3. **포트 충돌**: `streamlit run streamlit_app.py --server.port=8502` 로 다른 포트 사용

### 문의사항

기술적 문제나 개선사항이 있으면 이슈를 등록해주세요.

---

**개발자**: Your Name  
**버전**: 1.0.0  
**라이선스**: MIT
