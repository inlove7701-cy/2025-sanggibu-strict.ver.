import streamlit as st
import google.generativeai as genai

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="2025 생기부 메이트",
    page_icon="📝",
    layout="centered"
)

# --- 2. [디자인] 반응형 CSS ---
st.markdown("""
    <style>
    html, body, [class*="css"] { 
        font-family: 'Pretendard', 'Apple SD Gothic Neo', sans-serif; 
    }
    
    .stTextArea textarea { 
        border-radius: 10px; 
        border: 1px solid rgba(128, 128, 128, 0.2); 
    }
    
    h1 { font-weight: 700; letter-spacing: -1px; }
    .subtitle { font-size: 16px; color: gray; margin-top: -15px; margin-bottom: 30px; }
    
    .stButton button { 
        border-radius: 8px; font-weight: bold; border: none; transition: all 0.2s ease; 
    }
    .stButton button:hover { transform: scale(1.02); }
    
    .guide-box {
        background-color: rgba(240, 242, 246, 0.5);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.1);
        margin-bottom: 20px;
        font-size: 14px;
        color: #444;
        line-height: 1.6;
    }
    .guide-title { font-weight: bold; margin-bottom: 8px; display: block; font-size: 15px;}
    
    .count-box {
        background-color: #E8F6F3;
        color: #1D8348;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 5px;
        text-align: right;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. API 키 설정 ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except FileNotFoundError:
    api_key = None

# --- 4. 헤더 영역 ---
st.title("📝 2025 1학년부 행발 메이트")
st.markdown("<p class='subtitle'>Gift for 2025 1st Grade Teachers</p>", unsafe_allow_html=True)
st.divider()

if not api_key:
    with st.expander("🔐 관리자 설정 (API Key 입력)"):
        api_key = st.text_input("Google API Key", type="password")

# 작성 팁 헤더
st.markdown("""
<div class="guide-box">
    <span class="guide-title">💡 풍성한 생기부를 위한 작성 팁 (3-Point)</span>
    좋은 평가를 위해 아래 3가지 요소가 포함되도록 에피소드를 적어주세요.<br>
    [예시]<br>
    1. <b>(학업)</b> 수학 점수는 낮으나 오답노트를 꼼꼼히 작성함<br>
    2. <b>(인성)</b> 체육대회 때 뒷정리를 도맡아 함<br>
    3. <b>(진로)</b> 동아리에서 코딩 멘토링 활동을 함
</div>
""", unsafe_allow_html=True)

# --- 5. 입력 영역 ---
st.markdown("### 1. 학생 관찰 내용")
student_input = st.text_area(
    "입력창",
    height=200,
    placeholder="위의 작성 팁을 참고하여, 학생의 구체적인 행동 특성을 자유롭게 적어주세요.", 
    label_visibility="collapsed"
)

if student_input and len(student_input) < 30:
    st.markdown("<p style='color:#e67e22; font-size:14px;'>⚠️ 내용이 조금 짧습니다. 3가지 에피소드가 들어갔나요?</p>", unsafe_allow_html=True)

# --- 6. 필터 영역 ---
st.markdown("### 2. 강조할 핵심 키워드 선택")
filter_options = [
    "👑 AI 입학사정관 자동 판단", "📘 학업 역량", "🤝 공동체 역량", 
    "🚀 진로 역량", "🌱 발전 가능성", "🎨 창의적 문제해결력", 
    "😊 인성/나눔/배려", "⏰ 성실성/규칙준수"
]
try:
    selected_tags = st.pills("이 학생의 강조하고 싶은 역량_가장 앞에 노출됩니다. 미선택시 AI 입학사정관이 판단한 중요도 순으로 노출되요~! ^^", options=filter_options, selection_mode="multi")
except:
    selected_tags = st.multiselect("키워드 선택", filter_options)

# --- 7. 실행 및 결과 영역 ---
st.markdown("")
if st.button("✨ 생기부 문구 생성하기", type="primary", use_container_width=True):
    if not api_key:
        st.error("⚠️ API Key가 설정되지 않았습니다.")
    elif not student_input:
        st.warning("⚠️ 학생 관찰 내용을 입력해주세요!")
    else:
        with st.spinner('선생님의 생각을 AI가 정리중입니다...'):
            try:
                genai.configure(api_key=api_key)

                # 모델 자동 탐색 로직
                target_model = "gemini-pro"
                try:
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    if any('gemini-1.5-pro' in m for m in available_models):
                        target_model = [m for m in available_models if 'gemini-1.5-pro' in m][0]
                    elif any('gemini-1.5-flash' in m for m in available_models):
                        target_model = [m for m in available_models if 'gemini-1.5-flash' in m][0]
                    elif any('gemini-pro' in m for m in available_models):
                        target_model = [m for m in available_models if 'gemini-pro' in m][0]
                except:
                    pass
# [수정 1] generation_config 설정 (창의성 억제)
                # temperature를 0.2로 낮춰서 상상력을 제한합니다.
                generation_config = genai.types.GenerationConfig(
                    temperature=0.2 
                )
                
                model = genai.GenerativeModel(target_model, generation_config=generation_config)

                if not selected_tags:
                    tags_str = "전체적인 맥락에서 가장 우수한 역량 자동 추출"
                else:
                    tags_str = ", ".join(selected_tags)

                # [수정 2] 프롬프트 강력 제약 (없는 내용 작성 금지)
                system_prompt = f"""
                당신은 생활기록부 작성의 원칙을 철저히 준수하는 교사입니다.
                입력 정보: {student_input}
                강조 영역: [{tags_str}]
                
                다음 두 가지 파트로 나누어 출력하세요. 구분선: "---SPLIT---"

                [Part 1] 영역별 분석 (개조식)
                - 입력된 내용을 바탕으로 분류 및 요약
                
                ---SPLIT---

                [Part 2] 행동특성 및 종합의견 (서술형 종합본)
                - 목표 분량: 공백 포함 약 {target_length}자
                
                # ★★★ 매우 중요한 작성 원칙 (Strict Rules) ★★★
                1. **절대 날조 금지 (Zero Hallucination)**: 
                   - 사용자가 입력하지 않은 '구체적인 에피소드(사건)'를 절대 창작하지 마십시오.
                   - 예: 입력값에 '청소함'이 없는데 '환경미화 때 창문을 닦음'이라고 쓰면 안 됨.
                
                2. **입력 내용이 빈약하거나 구체적이지 않은 경우**:
                   - 억지로 구체적인 사례를 만들지 말고, **일반적인 행동 특성이나 태도** 위주로 서술하십시오.
                   - 해당 행동이 학생의 성장에 미치는 긍정적인 영향이나, 교사의 교육적 해석(기대효과)을 덧붙여 분량을 채우십시오.
                   
                3. **작성 스타일**:
                   - 입력된 사실(Fact) -> 교사의 해석/평가(Evaluation) 구조를 따르되, Fact는 입력된 범위 내에서만 인용하십시오.
                """

                response = model.generate_content(system_prompt)
                full_text = response.text
                
                if "---SPLIT---" in full_text:
                    parts = full_text.split("---SPLIT---")
                    analysis_text = parts[0].strip()
                    final_text = parts[1].strip()
                else:
                    analysis_text = "영역별 분석을 생성하지 못했습니다."
                    final_text = full_text

                char_count = len(final_text)
                char_count_no_space = len(final_text.replace(" ", "").replace("\n", ""))
                
                st.success("작성 완료!")
                
                with st.expander("🔍 영역별 분석 내용 확인하기 (클릭)", expanded=True):
                    st.markdown(analysis_text)
                
                st.markdown("---")
                st.markdown("### 📋 최종 제출용 종합본")

                st.markdown(f"""
                <div class="count-box">
                    📊 목표: {target_length}자 | 실제: {char_count}자 (공백제외 {char_count_no_space}자)
                </div>
                """, unsafe_allow_html=True)
                
                st.caption(f"※ 팩트 준수 모드 (상상력 제한됨) ({target_model})")
                st.text_area("결과 (복사해서 나이스에 붙여넣으세요)", value=final_text, height=350)

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")


