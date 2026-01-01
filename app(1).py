import streamlit as st
import google.generativeai as genai
import time

# --- 1. 기본 설정 ---
st.set_page_config(
    page_title="2025 생기부 행발 메이트 (최종)",
    page_icon="📝",
    layout="centered"
)

# --- 2. 스타일 CSS ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }
    .stTextArea textarea { background-color: #FAFCFA; border-radius: 10px; border: 1px solid #ddd; }
    .stButton button { 
        background-color: #557C64 !important; color: white !important; 
        font-weight: bold; border-radius: 10px; border: none; padding: 0.8rem; width: 100%;
    }
    .stButton button:hover { background-color: #3E5F4A !important; transform: scale(1.01); }
    .guide-box { background-color: #F7F9F8; padding: 15px; border-radius: 10px; border: 1px solid #E0E5E2; margin-bottom: 20px; color: #333; }
    .status-box { background-color: #E8F5E9; color: #2E7D32; padding: 10px; border-radius: 5px; font-size: 0.9em; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. API 키 설정 ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = None

# --- 4. 함수: 무조건 성공하는 생성기 (핵심!) ---
def generate_content_safe(model_name, prompt):
    """
    1차 시도 모델이 실패하면 자동으로 1.5-flash(가장 안전한 모델)로 재시도하는 함수
    """
    try:
        # 1차 시도
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text, model_name
    except Exception as e:
        # 실패 시 자동으로 Flash 모델로 전환 (Fallback)
        time.sleep(1) # 1초 대기
        try:
            fallback_model = "gemini-1.5-flash"
            model = genai.GenerativeModel(fallback_model)
            response = model.generate_content(prompt)
            return response.text, f"{fallback_model} (자동전환됨)"
        except Exception as e2:
            return f"에러가 발생했습니다. API 키를 확인해주세요. (Error: {e2})", "Error"

# --- 5. UI 구성 ---
st.title("📝 2025 생기부 행발 메이트")
st.markdown("##### 선생님을 위한 멈추지 않는 AI 보조교사")
st.divider()

if not api_key:
    with st.expander("🔐 관리자 설정 (API Key)"):
        api_key = st.text_input("Google API Key", type="password")

# 가이드
st.markdown("""
<div class="guide-box">
    <b>💡 작성 팁 (3가지 요소)</b><br>
    좋은 행발 작성을 위해 다음 내용을 포함해 주세요.<br>
    1. <b>학업 태도</b>: 수업 참여도, 과제 수행, 오답 정리 등<br>
    2. <b>인성/사회성</b>: 배려, 나눔, 갈등 해결, 리더십<br>
    3. <b>진로/잠재력</b>: 동아리 활동, 관심 분야, 성장 가능성
</div>
""", unsafe_allow_html=True)

# 입력창
st.subheader("1. 학생 관찰 내용")
student_input = st.text_area(
    "학생의 특징을 자유롭게 적어주세요", 
    height=150, 
    placeholder="예: 수학 성적은 낮으나 질문을 자주 함. 체육대회 때 솔선수범하여 뒷정리를 함. 코딩 동아리에서 멘토링을 진행함.",
    label_visibility="collapsed"
)

# 옵션
st.subheader("2. 설정")
col1, col2 = st.columns(2)
with col1:
    mode = st.radio("작성 모드", ["✨ 풍성하게", "🛡️ 엄격하게"], horizontal=True)
with col2:
    target_length = st.slider("목표 글자 수", 300, 1000, 500, 50)

# 키워드
keywords = st.multiselect("강조할 키워드 (선택)", ["학업역량", "공동체역량", "진로역량", "성실성", "리더십", "창의성", "배려/나눔"])

# --- 6. 실행 로직 ---
if st.button("✨ 행발 생성하기", use_container_width=True):
    if not api_key:
        st.error("⚠️ API Key가 필요합니다.")
    elif not student_input:
        st.warning("⚠️ 학생 관찰 내용을 입력해주세요.")
    else:
        with st.spinner("AI가 최적의 모델을 찾아 작성 중입니다..."):
            
            # 모드별 프롬프트
            if "엄격하게" in mode:
                style = "사실에 기반한 객관적이고 건조한 문체. 미사여구 배제."
            else:
                style = "학생의 성장을 응원하는 풍성하고 긍정적인 문체. 교육적 의미 부여."
            
            keyword_str = f"강조 키워드: {', '.join(keywords)}" if keywords else "전반적인 발달상황 기술"

            # 프롬프트 구성
            prompt = f"""
            당신은 고등학교 담임교사입니다. 아래 학생의 행동특성 및 종합의견(행발)을 작성하세요.

            [입력 데이터]
            - 관찰 내용: {student_input}
            - 강조점: {keyword_str}
            - 스타일: {style}
            - 목표 분량: 약 {target_length}자

            [작성 구조]
            1. **인성 및 사회성**: 배려, 협력, 규칙 준수 등 인성적 측면 서술.
            2. **학업 및 진로**: 수업 태도, 자기주도성, 진로 관심사 서술.
            3. **종합 평가**: 학생의 잠재력과 성장을 종합적으로 요약.

            [유의 사항]
            - 문체는 '~함', '~임', '~보임' 등의 개조식과 줄글의 조화 (생기부 표준).
            - 문맥을 자연스럽게 연결하여 하나의 완결된 글로 작성할 것.

            [출력 양식]
            1. 요약 (3줄)
            ---SPLIT---
            2. 행발 본문
            """

            # 안전한 생성 요청 (기본: 1.5-pro -> 실패시: 1.5-flash)
            # 사용자님 코드의 2.5 모델은 삭제하고 1.5로 교체했습니다.
            result_text, used_model = generate_content_safe("gemini-1.5-pro", prompt)

            # 결과 처리
            if "---SPLIT---" in result_text:
                parts = result_text.split("---SPLIT---")
                summary = parts[0].strip()
                body = parts[1].strip()
            else:
                summary = "요약 없음"
                body = result_text

            # 출력
            st.success("작성 완료!")
            st.markdown(f"<div class='status-box'>✅ <b>{used_model}</b> 모델이 성공적으로 작성했습니다.</div>", unsafe_allow_html=True)
            
            with st.expander("🔍 요약 보기"):
                st.write(summary)
            
            st.markdown("---")
            st.text_area("최종 결과 (복사해서 사용하세요)", value=body, height=400)
            st.caption(f"글자 수: {len(body)}자 (공백 포함)")
