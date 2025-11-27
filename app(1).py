import streamlit as st
import google.generativeai as genai

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="2025 생기부 메이트",
    page_icon="📝",
    layout="centered"
)

# --- 2. [디자인] 숲속 테마 CSS ---
st.markdown("""
    <style>
    html, body, [class*="css"] { 
        font-family: 'Pretendard', 'Apple SD Gothic Neo', sans-serif; 
    }
    .stTextArea textarea { 
        border-radius: 10px; 
        border: 1px solid rgba(85, 124, 100, 0.2); 
    }
    h1 { font-weight: 700; letter-spacing: -1px; color: #2F4F3A; } 
    .subtitle { font-size: 16px; color: #666; margin-top: -15px; margin-bottom: 30px; }
    
    .stButton button { 
        background-color: #557C64 !important; 
        color: white !important;
        border-radius: 8px; font-weight: bold; border: none; 
        transition: all 0.2s ease; padding: 0.6rem 1rem; font-size: 16px !important;
    }
    .stButton button:hover { 
        background-color: #3E5F4A !important; transform: scale(1.02); color: white !important;
    }
    
    /* 슬라이더 색상: 머스터드 */
    div.stSlider > div[data-baseweb="slider"] > div > div { background-color: #D4AC0D !important; }
    div.stSlider > div[data-baseweb="slider"] > div > div > div { background-color: #D4AC0D !important; }
    
    /* 라디오 버튼 스타일 */
    div[data-testid="stRadio"] > div {
        background-color: #F7F9F8;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #E0E5E2;
    }
    
    .guide-box {
        background-color: #F7F9F8; padding: 20px; border-radius: 10px;
        border: 1px solid #E0E5E2; margin-bottom: 20px; font-size: 14px; color: #444; line-height: 1.6;
    }
    .guide-title { font-weight: bold; margin-bottom: 8px; display: block; font-size: 15px; color: #557C64;}
    
    .warning-text { color: #8D6E63; font-size: 14px; margin-top: 5px; font-weight: 500; }
    
    .count-box {
        background-color: #E3EBE6; color: #2F4F3A; padding: 12px; border-radius: 8px;
        font-weight: bold; font-size: 14px; margin-bottom: 10px; text-align: right; border: 1px solid #C4D7CD; 
    }
    
    .analysis-box {
        background-color: #FCFDFD; border-left: 4px solid #557C64; padding: 15px;
        border-radius: 5px; margin-bottom: 20px; font-size: 14px; color: #333;
    }
    
    .footer {
        margin-top: 50px; text-align: center; font-size: 14px; color: #888; border-top: 1px solid #eee; padding-top: 20px;
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

# 작성 팁
st.markdown("""
<div class="guide-box">
    <span class="guide-title">💡 풍성한 생기부를 위한 작성 팁 (3-Point)</span>
    좋은 평가를 위해 아래 3가지 요소가 포함되도록 에피소드를 적어주세요.<br>
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
    st.markdown("<p class='warning-text'>⚠️ 내용이 조금 짧습니다. 3가지 에피소드가 들어갔나요?</p>", unsafe_allow_html=True)

# --- 6. 옵션 영역 ---
st.markdown("### 2. 작성 옵션 설정")

# 모드 선택 기능
mode = st.radio(
    "작성 모드를 선택하세요",
    ["✨ 풍성하게 작성 (내용 보강)", "🛡️ 엄격하게 작성 (팩트 중심)"],
    captions=["입력 내용이 적어도 살을 붙여 자연스럽게 만듭니다.", "입력된 사실 외에는 절대 지어내지 않습니다."]
)

col1, col2 = st.columns([1, 1]) 
filter_options = [
    "👑 AI 입학사정관 자동 판단", "📘 학업 역량", "🤝 공동체 역량", 
    "🚀 진로 역량", "🌱 발전 가능성", "🎨 창의적 문제해결력", 
    "😊 인성/나눔/배려", "⏰ 성실성/규칙준수"
]
with col1:
    st.caption("강조할 핵심 키워드")
    try:
        selected_tags = st.pills("키워드 버튼", options=filter_options, selection_mode="multi", label_visibility="collapsed")
    except:
        selected_tags = st.multiselect("키워드 선택", filter_options, label_visibility="collapsed")

with col2:
    st.caption("희망 분량 (공백 포함)")
    target_length = st.slider(
        "글자 수",
        min_value=300,
        max_value=1000,
        value=500,
        step=50,
        label_visibility="collapsed"
    )

# --- 7. 실행 및 결과 영역 ---
st.markdown("")
if st.button("✨ 생기부 문구 생성하기", use_container_width=True):
    if not api_key:
        st.error("⚠️ API Key가 설정되지 않았습니다.")
    elif not student_input:
        st.warning("⚠️ 학생 관찰 내용을 입력해주세요!")
    else:
        with st.spinner(f'AI가 {mode.split()[1]} 모드로 분석 중입니다...'):
# --- [수정] 들여쓰기 교정된 try 블록 ---
            try:
                genai.configure(api_key=api_key)

                # --- [핵심 수정] 모델 자동 검색 및 안전 선택 ---
                target_model = "gemini-pro" # 최후의 수단 (기본값)
                
                try:
                    # 1. 사용 가능한 모델 목록을 가져옵니다.
                    models = genai.list_models()
                    
                    # 2. 'generateContent' 기능을 지원하는 모델 이름만 뽑습니다.
                    available_names = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
                    
                    # 3. 우선순위에 따라 모델을 선택합니다.
                    # (Pro가 있으면 Pro, 없으면 Flash, 그것도 없으면 기본값)
                    for name in available_names:
                        if 'gemini-1.5-pro' in name:
                            target_model = name
                            break # 제일 좋은 거 찾았으면 멈춤
                        elif 'gemini-1.5-flash' in name:
                            target_model = name
                            # 멈추지 않고 혹시 Pro가 있는지 더 찾아봄
                except Exception as e:
                    # 모델 목록 조회 실패 시 그냥 'gemini-pro' 시도
                    pass
                
                # --- 모드에 따른 설정 분기 ---
                if "엄격하게" in mode:
                    # 엄격 모드: 창의성 낮춤, 팩트 강조
                    temp = 0.2
                    prompt_instruction = """
                    # ★★★ 엄격 작성 원칙 (Strict Mode) ★★★
                    1. **절대 날조 금지 (Zero Hallucination)**: 사용자가 입력한 내용에 없는 구체적 에피소드를 절대 창작하지 마십시오.
                    2. **담백한 서술**: 입력 정보가 부족하면 억지로 늘리지 말고, 일반적인 태도나 성향 위주로 건조하게 서술하십시오.
                    3. 입력된 사실(Fact)에 기반한 교사의 평가 위주로 작성하십시오.
                    """
                else:
                    # 풍성 모드: 창의성 높임, 표현력 강화
                    temp = 0.75
                    prompt_instruction = """
                    # ★★★ 풍성 작성 원칙 (Rich Mode) ★★★
                    1. **내용 보강 (Elaboration)**: 입력된 내용이 다소 짧더라도, 문맥에 맞는 적절한 수식어와 교육적 표현을 사용하여 풍성하게 작성하십시오.
                    2. **자연스러운 연결**: 문장과 문장 사이를 매끄럽게 연결하여 유려한 글이 되도록 하십시오.
                    3. 학생의 잠재력과 성장 가능성을 긍정적인 어조로 구체화하여 서술하십시오.
                    """

                # 설정 적용
                generation_config = genai.types.GenerationConfig(temperature=temp)
                model = genai.GenerativeModel(target_model, generation_config=generation_config)

                if not selected_tags:
                    tags_str = "전체적인 맥락에서 가장 우수한 역량 자동 추출"
                else:
                    tags_str = ", ".join(selected_tags)

                # 공통 프롬프트
                system_prompt = f"""
                당신은 입학사정관 관점을 가진 고등학교 교사입니다.
                입력 정보: {student_input}
                강조 영역: [{tags_str}]
                
                다음 두 가지 파트로 나누어 출력하세요. 구분선: "---SPLIT---"

                [Part 1] 영역별 분석 (개조식)
                - [인성 / 학업 / 진로 / 공동체] 분류하여 요약
                
                ---SPLIT---

                [Part 2] 행동특성 및 종합의견 (서술형 종합본)
                - 문체: ~함, ~임
                - 구조: 사례 -> 행동 -> 성장/평가
                - 목표 분량: 공백 포함 약 {target_length}자 (오차범위 ±10%)
                
                {prompt_instruction}
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
                
                st.caption(f"※ {mode.split()[1]} 모드 동작 중 ({target_model})")
                st.text_area("결과 (복사해서 나이스에 붙여넣으세요)", value=final_text, height=350)

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")

# --- 8. 푸터 ---
st.markdown("""
<div class="footer">
    © 2025 <b>Chaeyun with AI</b>. All rights reserved.<br>
    문의: <a href="inlove11@naver.com" style="color: #888; text-decoration: none;">inlove11@naver.com</a>
</div>
""", unsafe_allow_html=True)



