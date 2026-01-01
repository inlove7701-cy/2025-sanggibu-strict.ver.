import streamlit as st
import google.generativeai as genai

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="2025 생기부 메이트 (행발)",
    page_icon="📝",
    layout="centered"
)

# --- 2. [디자인] 숲속 테마 CSS ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }
    .stTextArea textarea { border-radius: 12px; border: 1px solid rgba(85, 124, 100, 0.2); background-color: #FAFCFA; }
    h1 { font-weight: 700; letter-spacing: -1px; color: #2F4F3A; } 
    .subtitle { font-size: 16px; color: #666; margin-top: -15px; margin-bottom: 30px; }
    
    .stButton button { 
        background-color: #557C64 !important; color: white !important;
        border-radius: 10px; font-weight: bold; border: none; 
        transition: all 0.2s ease; padding: 0.8rem 1rem; font-size: 16px !important; width: 100%; 
    }
    .stButton button:hover { background-color: #3E5F4A !important; transform: scale(1.01); }
    
    /* 슬라이더 스타일 */
    div[data-testid="stSlider"] div[data-baseweb="slider"] > div { background-color: #E0E0E0 !important; border-radius: 10px; height: 6px !important; }
    div[data-testid="stSlider"] div[data-baseweb="slider"] > div > div { background-color: #D4AC0D !important; height: 6px !important; }
    div[data-testid="stSlider"] div[role="slider"] { background-color: transparent !important; box-shadow: none !important; border: none !important; height: 24px; width: 24px; }
    div[data-testid="stSlider"] div[role="slider"]::after {
        content: "★"; font-size: 32px; color: #D4AC0D !important; position: absolute; top: -18px; left: -5px; text-shadow: 0px 1px 2px rgba(0,0,0,0.2);
    }
    div[data-testid="stSlider"] div[data-testid="stMarkdownContainer"] p { color: #557C64 !important; }

    /* 라디오 버튼 스타일 */
    div[data-testid="stRadio"] { background-color: transparent; }
    div[data-testid="stRadio"] > div[role="radiogroup"] { display: flex; justify-content: space-between; width: 100%; gap: 10px; }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        flex-grow: 1; background-color: #FFFFFF; border: 1px solid #E0E5E2; border-radius: 8px; padding: 12px; justify-content: center;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover { border-color: #557C64; background-color: #F7F9F8; }
    
    .guide-box { background-color: #F7F9F8; padding: 20px; border-radius: 12px; border: 1px solid #E0E5E2; margin-bottom: 25px; font-size: 14px; color: #444; line-height: 1.6; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
    .guide-title { font-weight: bold; margin-bottom: 8px; display: block; font-size: 15px; color: #557C64;}
    .warning-text { color: #8D6E63; font-size: 14px; margin-top: 5px; font-weight: 500; }
    .count-box { background-color: #E3EBE6; color: #2F4F3A; padding: 12px; border-radius: 8px; font-weight: bold; font-size: 14px; margin-bottom: 10px; text-align: right; border: 1px solid #C4D7CD; }
    .analysis-box { background-color: #FCFDFD; border-left: 4px solid #557C64; padding: 15px; border-radius: 5px; margin-bottom: 20px; font-size: 14px; color: #333; }
    .footer { margin-top: 50px; text-align: center; font-size: 14px; color: #888; border-top: 1px solid #eee; padding-top: 20px; }
    .card-title { font-size: 15px; font-weight: 700; color: #557C64; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. API 키 설정 ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
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

# --- 6. 3단계 작성 옵션 ---
st.markdown("### 2. 작성 옵션 설정")

# [카드 1] 모드 선택
with st.container(border=True):
    st.markdown('<p class="card-title">① 작성 모드 선택</p>', unsafe_allow_html=True)
    mode = st.radio(
        "모드",
        ["✨ 풍성하게 (내용 보강)", "🛡️ 엄격하게 (팩트 중심)"],
        captions=["살을 붙여 자연스럽게 만듭니다.", "입력된 사실 외에는 절대 짓지 않습니다."],
        horizontal=True, 
        label_visibility="collapsed"
    )

# [카드 2] 희망 분량
with st.container(border=True):
    st.markdown('<p class="card-title">② 희망 분량 (공백 포함)</p>', unsafe_allow_html=True)
    target_length = st.slider(
        "글자 수",
        min_value=100, max_value=600, value=500, step=10,
        label_visibility="collapsed"
    )

# [카드 3] 키워드 선택
with st.container(border=True):
    st.markdown('<p class="card-title">③ 강조할 핵심 키워드 (다중 선택)</p>', unsafe_allow_html=True)
    filter_options = [
        "👑 AI 자동 판단", "📘 학업 역량", "🤝 공동체 역량", 
        "🚀 진로 역량", "🌱 발전 가능성", "🎨 창의적 문제해결력", 
        "😊 인성/나눔/배려", "⏰ 성실성/규칙준수"
    ]
    try:
        selected_tags = st.pills("키워드 버튼", options=filter_options, selection_mode="multi", label_visibility="collapsed")
    except:
        selected_tags = st.multiselect("키워드 선택", filter_options, label_visibility="collapsed")

# [고급 설정] 모델 선택 (강제 고정)
st.markdown("")
with st.expander("⚙️ AI 모델 선택 (기본값: 1.5-flash)"):
    manual_model = st.selectbox(
        "사용할 모델",
        ["⚡ gemini-1.5-flash (추천/무료)", "🤖 gemini-1.5-pro (고성능)"]
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
            try:
                genai.configure(api_key=api_key)

                # --- [수정 완료] 모델 선택 로직 (에러 원인인 2.5 제거) ---
                if "pro" in manual_model:
                    target_model = "gemini-1.5-pro"
                else:
                    target_model = "gemini-1.5-flash"
                
                # 모드별 프롬프트 설정
                if "엄격하게" in mode:
                    temp = 0.2
                    prompt_instruction = """
                    # ★★★ 엄격 작성 원칙 (Strict Mode) ★★★
                    1. **절대 날조 금지**: 사용자가 입력한 내용에 없는 구체적 에피소드를 절대 창작하지 마십시오.
                    2. **담백한 서술**: 입력 정보가 부족하면 억지로 늘리지 말고, 일반적인 태도나 성향 위주로 건조하게 서술하십시오.
                    """
                else:
                    temp = 0.75
                    prompt_instruction = """
                    # ★★★ 풍성 작성 원칙 (Rich Mode) ★★★
                    1. **내용 보강**: 입력된 내용이 다소 짧더라도, 문맥에 맞는 적절한 수식어와 교육적 표현을 사용하여 풍성하게 작성하십시오.
                    2. **자연스러운 연결**: 문장과 문장 사이를 매끄럽게 연결하여 유려한 글이 되도록 하십시오.
                    """

                generation_config = genai.types.GenerationConfig(temperature=temp)
                model = genai.GenerativeModel(target_model, generation_config=generation_config)

                # 키워드 처리
                if not selected_tags:
                    tags_str = "별도의 키워드 지정 없음. [인성/소통] -> [학업/태도] -> [진로/관심] -> [발전가능성] 순서 권장."
                else:
                    tags_str = f"다음 핵심 키워드를 중심으로 서술: {', '.join(selected_tags)}"

                # 프롬프트
                system_prompt = f"""
                당신은 입학사정관 관점을 가진 고등학교 교사입니다.
                입력 정보: {student_input}
                작성 지침: [{tags_str}]
                
                다음 두 가지 파트로 나누어 출력하세요. 구분선: "---SPLIT---"

                [Part 1] 영역별 분석 (개조식)
                - [인성 / 학업 / 진로 / 공동체] 분류하여 요약
                
                ---SPLIT---

                [Part 2] 행동특성 및 종합의견 (서술형 종합본)
                - 문체: ~함, ~임
                - 구조: 사례 -> 행동 -> 성장/평가
                - 목표 분량: 공백 포함 약 {target_length}자 (오차범위 ±10%)
                
                {prompt_instruction}

                # ★★★ 구조 및 순서 ★★★
                1. **기본 순서 준수**: 특별히 강조할 키워드가 지정되지 않았다면, **[인성/사회성] → [학업역량] → [진로적성] → [발전가능성]** 순서로 배치하십시오.
                2. **유기적 연결**: 각 영역을 딱딱하게 끊지 말고 자연스럽게 연결하십시오.
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
                # 에러 메시지 분석 및 사용자 안내
                error_msg = str(e)
                if "429" in error_msg:
                    st.error("🚨 무료 사용량을 초과했습니다. 잠시 후 다시 시도하거나, API 키를 변경해보세요.")
                elif "404" in error_msg:
                    st.error("🚨 중요: 'requirements.txt' 파일에 'google-generativeai>=0.8.3'이 있는지 확인하고 앱을 [Reboot] 해주세요.")
                else:
                    st.error(f"오류가 발생했습니다: {e}")

# --- 8. 푸터 ---
st.markdown("""
<div class="footer">
    © 2025 <b>Chaeyon with AI</b>. All rights reserved.<br>
</div>
""", unsafe_allow_html=True)
