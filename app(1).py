import streamlit as st
import google.generativeai as genai
import time

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="2025 생기부 메이트 (무중단 버전)",
    page_icon="🛡️",
    layout="centered"
)

# --- 2. CSS 스타일 ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }
    .stTextArea textarea { border-radius: 12px; background-color: #FAFCFA; border: 1px solid #ddd; }
    .stButton button { 
        background-color: #2E7D32 !important; color: white !important; 
        font-weight: bold; border-radius: 10px; border: none; padding: 0.8rem; width: 100%;
    }
    .stButton button:hover { background-color: #1B5E20 !important; transform: scale(1.02); }
    .guide-box { background-color: #E8F5E9; padding: 15px; border-radius: 10px; border: 1px solid #C8E6C9; margin-bottom: 20px; color: #1B5E20; }
    .success-box { background-color: #E3F2FD; color: #0D47A1; padding: 10px; border-radius: 5px; font-size: 0.9em; margin-bottom: 10px; border-left: 4px solid #1976D2; }
    .error-log { font-size: 0.8em; color: #999; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. API 키 설정 ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = None

# --- 4. [핵심 기능] 무조건 성공하는 AI 함수 ---
def generate_with_fallback(prompt, user_selected_model):
    """
    사용자가 선택한 모델이 실패하면, 자동으로 다른 모델들을 순차적으로 시도하여
    어떻게든 결과를 만들어내는 함수입니다.
    """
    # 시도할 모델 순서 (사용자 선택 모델 -> 1.5 Flash -> 1.5 Pro -> 1.0 Pro)
    # 1.5 Flash가 무료 사용량이 가장 많고 안정적이라 우선순위가 높습니다.
    candidate_models = [
        user_selected_model,    # 1순위: 사용자가 고른 거
        "gemini-1.5-flash",     # 2순위: 가장 빠르고 튼튼한 놈
        "gemini-1.5-pro",       # 3순위: 성능 좋은 놈
        "gemini-1.0-pro"        # 4순위: 구버전 (최후의 보루)
    ]
    
    # 중복 제거 (사용자가 고른 게 1.5-flash면 리스트에 두 번 들어가는 것 방지)
    candidate_models = sorted(set(candidate_models), key=candidate_models.index)

    logs = []
    
    genai.configure(api_key=api_key)

    for model_name in candidate_models:
        try:
            # 모델 생성 시도
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            
            # 성공하면 바로 반환 (성공한 모델 이름과 함께)
            return response.text, model_name, logs
            
        except Exception as e:
            # 실패하면 로그 남기고 다음 모델로 넘어감 (continue)
            error_msg = str(e)
            logs.append(f"❌ {model_name} 실패: {error_msg[:50]}...")
            time.sleep(1) # 1초 숨 고르기
            continue
            
    # 모든 모델이 다 실패했을 경우
    return None, None, logs

# --- 5. UI 구성 ---
st.title("🛡️ 2025 생기부 메이트")
st.markdown("##### 오류 없이 무조건 결과를 뽑아내는 강력한 버전")
st.divider()

if not api_key:
    with st.expander("🔐 관리자 설정"):
        api_key = st.text_input("Google API Key", type="password")

st.markdown("""
<div class="guide-box">
    <b>💡 안심하세요!</b><br>
    이 버전은 "사용량 초과"나 "모델 오류"가 발생해도 
    <b>자동으로 다른 모델을 찾아내서</b> 끝까지 글을 써줍니다.
</div>
""", unsafe_allow_html=True)

# 입력 영역
st.subheader("1. 1학기 내용 (요약)")
sem1_input = st.text_area("1학기 내용 입력", height=100, placeholder="기존 생기부 내용", label_visibility="collapsed")

st.subheader("2. 2학기 활동 키워드")
st.caption("※ 기고문, 북리뷰, AI 활용 활동으로 자동 확장됩니다.")
sem2_input = st.text_area("2학기 주제 입력", height=100, placeholder="예: AI 의료 윤리, 독서, 토론 등", label_visibility="collapsed")

# 옵션
col1, col2 = st.columns(2)
with col1:
    mode = st.radio("작성 모드", ["✨ 풍성하게", "🛡️ 엄격하게"], horizontal=True)
with col2:
    target_length = st.slider("목표 글자 수", 300, 1000, 500, 50)

# 모델 선택 (실패 시 자동 우회하므로 선호도만 조사)
manual_model = st.selectbox("선호하는 모델 (실패 시 자동 변경됨)", ["gemini-1.5-flash", "gemini-1.5-pro"])

# --- 6. 실행 ---
if st.button("✨ 무조건 생성하기", use_container_width=True):
    if not api_key:
        st.error("API Key가 없습니다.")
    elif not sem1_input and not sem2_input:
        st.warning("내용을 입력해주세요.")
    else:
        with st.spinner("AI가 최적의 경로를 찾아 작성 중입니다..."):
            
            # 프롬프트 구성
            if "엄격하게" in mode:
                style = "사실 기반의 건조하고 객관적인 문체."
                temp = 0.2
            else:
                style = "학생의 성장을 구체적으로 묘사하는 풍성한 문체."
                temp = 0.75

            prompt = f"""
            당신은 고등학교 교사입니다. 아래 내용을 바탕으로 과목 세특을 작성하세요.

            [입력 데이터]
            - 1학기: {sem1_input}
            - 2학기 주제: {sem2_input}
            - 목표 분량: {target_length}자
            - 스타일: {style}

            [필수 포함 활동 (2학기)]
            1. **신문기사 기고문**: 관련 기사 분석 및 기고문 작성.
            2. **원서 북리뷰**: 원서 독서 후 비평문 작성.
            3. **AI 도구 활용**: AI를 활용한 탐구 및 한계점 분석.

            [작성 지침]
            - 1학기 내용은 30%로 요약, 2학기 활동은 70%로 구체적 서술.
            - 두 내용을 자연스럽게 연결.
            - 문체: '~함', '~임' (생기부 표준).

            [출력]
            1. 요약
            ---SPLIT---
            2. 본문
            """

            # ★★★ 무조건 성공하는 함수 호출 ★★★
            result_text, success_model, error_logs = generate_with_fallback(prompt, manual_model)

            if result_text:
                # 성공 시
                st.success("작성 완료!")
                
                # 어떤 모델이 성공했는지, 실패한 모델은 무엇인지 알려줌
                st.markdown(f"<div class='success-box'>✅ <b>{success_model}</b> 모델로 작성되었습니다.</div>", unsafe_allow_html=True)
                
                if error_logs:
                    with st.expander("⚠️ 우회 기록 (클릭하여 확인)"):
                        for log in error_logs:
                            st.text(log)
                            
                # 결과 분리 및 출력
                if "---SPLIT---" in result_text:
                    parts = result_text.split("---SPLIT---")
                    summary = parts[0].strip()
                    body = parts[1].strip()
                else:
                    summary = "요약 없음"
                    body = result_text

                st.markdown("### 📝 최종 결과")
                st.text_area("결과 복사", value=body, height=400)
                
            else:
                # 정말 모든 모델이 다 실패했을 때 (거의 일어날 수 없음)
                st.error("🚨 모든 AI 모델이 응답하지 않습니다. 잠시 후 다시 시도하거나 API 키를 확인해주세요.")
                with st.expander("상세 에러 로그"):
                    for log in error_logs:
                        st.text(log)
