import streamlit as st
from openai import OpenAI
import tempfile
import os

# 페이지 설정
st.set_page_config(
    page_title="AI 비디오 감독",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f1f1f;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1rem;
        border-left: 4px solid #3498db;
        padding-left: 1rem;
    }
    .role-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #e74c3c;
        margin-bottom: 1.5rem;
    }
    .api-key-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .upload-box {
        border: 2px dashed #3498db;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
        background-color: #f8f9fa;
    }
    .analysis-options {
        background-color: #ecf0f1;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 사이드바 - API 키 설정
with st.sidebar:
    st.markdown('<div class="api-key-section">', unsafe_allow_html=True)
    st.markdown("### 🔑 API Key 설정")
    api_key = st.text_input(
        "OpenAI API Key를 입력하세요:",
        type="password",
        placeholder="sk-xxxxxxxxxxxxxxxx",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🎬 AI 비디오 감독")
    st.markdown("원하는 작업을 탭에서 선택하세요")
    
    st.info("""
    **예시:**
    - 버전 1: 프롬프트 개발기
    - 버전 2: 영상 프롬프트 분석기
    """)

# 메인 콘텐츠
st.markdown('<div class="main-header">🎬 AI 비디오 감독</div>', unsafe_allow_html=True)

# 탭 생성
tab1, tab2 = st.tabs(["📝 버전 1: 프롬프트 개발기", "🎥 버전 2: 영상 프롬프트 분석기"])

with tab1:
    st.markdown('<div class="section-header">아이디어를 영상으로 발전시키기</div>', unsafe_allow_html=True)
    
    # 역할 설명 박스
    st.markdown("""
    <div class="role-box">
        <h4>🎯 현재 역할: Video Director</h4>
        <p><strong>You are a professional film director. Always analyze ideas in terms of visual storytelling — use camera movement, lighting, framing, and emotional tone to explain your thoughts. Describe concepts as if you are planning a film scene.</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # 아이디어 입력 섹션
    col1, col2 = st.columns([2, 1])
    
    with col1:
        user_idea = st.text_area(
            "💡 발전시키고 싶은 아이디어를 입력하세요:",
            placeholder="예: 비 오는 날 창밖을 보는 슬픈 남자\n예: 도시의 야경을 배경으로 한 추격 장면\n예: 고독한 예술가의 창작 과정",
            height=120,
            help="구체적이고 생생한 묘사를 통해 더 좋은 결과를 얻을 수 있습니다."
        )
    
    with col2:
        st.markdown("### 🎨 스타일 선택")
        style_option = st.selectbox(
            "영화 장르/스타일:",
            ["드라마", "스릴러", "로맨스", "SF", "판타지", "느와르", "다큐멘터리", "액션", "코미디"],
            index=0
        )
        
        detail_level = st.slider("상세도:", 1, 5, 3)
    
    # 발전 버튼
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        develop_button = st.button(
            "🚀 프롬프트 발전시키기",
            use_container_width=True,
            type="primary"
        )
    
    if develop_button:
        if not api_key:
            st.error("❌ OpenAI API Key를 먼저 입력해주세요.")
        elif not user_idea:
            st.error("❌ 아이디어를 입력해주세요.")
        else:
            with st.spinner("🎬 AI가 당신의 아이디어를 영화 장면으로 발전시키고 있습니다..."):
                try:
                    client = OpenAI(api_key=api_key)
                    
                    # 상세도에 따른 지시사항
                    detail_instructions = {
                        1: "간략한 개요만 제공해주세요.",
                        2: "기본적인 장면 구성을 설명해주세요.",
                        3: "균형잡힌 상세도로 설명해주세요.",
                        4: "세부적인 기술적 요소를 포함해주세요.",
                        5: "매우 상세하게, 모든 시각적 요소를 구체적으로 설명해주세요."
                    }
                    
                    prompt = f"""
                    당신은 전문 영화 감독입니다. 다음 아이디어를 {style_option} 장르/스타일로 영화 장면으로 발전시켜주세요.
                    
                    아이디어: {user_idea}
                    
                    다음 요소들을 포함하여 설명해주세요:
                    - 카메라 움직임과 앵글
                    - 조명과 색감
                    - 프레이밍과 구도
                    - 감정적 톤과 분위기
                    - 배경과 세트 디자인
                    - 캐릭터의 동작과 표정
                    
                    {detail_instructions[detail_level]}
                    
                    마지막으로 이 장면을 생성할 수 있는 AI 비디오 생성기를 위한 간결한 프롬프트를 제공해주세요.
                    """
                    
                    response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "당신은 창의적이고 경험 많은 영화 감독입니다. 아이디어를 시각적 스토리텔링 관점에서 분석하고, 카메라 움직임, 조명, 프레이밍, 감정적 톤을 사용하여 생각을 설명하세요. 영화 장면을 계획하는 것처럼 개념을 설명하세요."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=1500,
                        temperature=0.8
                    )
                    
                    result = response.choices[0].message.content
                    
                    # 결과 표시
                    st.success("✅ 영화 장면 분석 완료!")
                    
                    with st.expander("🎬 발전된 영화 장면 분석", expanded=True):
                        st.markdown(result)
                        
                    # 추가적인 시각화 제안
                    with st.expander("💡 추가 제안", expanded=False):
                        st.markdown("""
                        **다음 단계를 고려해보세요:**
                        - 다른 장르로도 시도해보기
                        - 캐릭터 개발에 집중하기
                        - 대사 추가하기
                        - 음악과 사운드 디자인 고려하기
                        """)
                    
                except Exception as e:
                    st.error(f"❌ API 호출 중 오류가 발생했습니다: {str(e)}")

with tab2:
    st.markdown('<div class="section-header">비디오를 분석하여 프롬프트 생성하기</div>', unsafe_allow_html=True)
    
    # AI 분석가 역할 설명
    st.markdown("""
    <div class="role-box">
        <h4>🔍 AI 분석가 역할</h4>
        <p><strong>You are a professional film director and shot analyzer. Your task is to analyze a series of video frames provided by the user. Based on these frames, generate a detailed "prompt" that could be used by an AI video generator to create this exact scene. Your analysis must include: Subject, Action, Scene Description, Cinematography (angle, movement, lighting), and Style. Combine all of this into a concise, powerful prompt for an AI video generator.</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # 파일 업로드 섹션
    st.markdown("### 📁 분석을 원하는 파일을 업로드하세요 (mp4, mov, avi):")
    
    uploaded_file = st.file_uploader(
        "Drag and drop file here",
        type=['mp4', 'mov', 'avi', 'mpeg4'],
        label_visibility="collapsed",
        help="Limit 200MB per file - MP4, MOV, AVI, MPEG4"
    )
    
    if uploaded_file is not None:
        # 파일 정보 표시
        file_size = uploaded_file.size / (1024 * 1024)  # MB로 변환
        st.success(f"✅ 파일 업로드 완료: {uploaded_file.name} ({file_size:.2f} MB)")
        
        # 임시 파일로 저장 및 비디오 표시
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            st.video(tmp_file.name)
        
        # 분석 옵션
        st.markdown("### ⚙️ 분석 옵션")
        
        col1, col2 = st.columns(2)
        
        with col1:
            sampling_interval = st.number_input(
                "표본 추출 간격 (초)",
                min_value=0.1,
                max_value=10.0,
                value=1.0,
                step=0.1,
                help="비디오에서 프레임을 추출할 시간 간격"
            )
        
        with col2:
            max_frames = st.number_input(
                "최대 표본 프레임 수",
                min_value=1,
                max_value=50,
                value=10,
                step=1,
                help="분석에 사용할 최대 프레임 수"
            )
        
        # 분석 버튼
        analyze_button = st.button(
            "🔍 비디오 분석 및 프롬프트 생성",
            type="primary",
            use_container_width=True
        )
        
        if analyze_button:
            if not api_key:
                st.error("❌ OpenAI API Key를 먼저 입력해주세요.")
            else:
                with st.spinner("🎥 비디오를 분석하고 AI 프롬프트를 생성하는 중..."):
                    try:
                        client = OpenAI(api_key=api_key)
                        
                        # 실제 구현에서는 여기에서 비디오 프레임 추출 및 분석이 이루어집니다
                        # 현재는 텍스트 기반 시뮬레이션으로 대체
                        
                        analysis_prompt = f"""
                        당신은 전문 영화 감독이자 샷 분석가입니다. 사용자가 업로드한 비디오를 분석하고 있습니다.
                        
                        비디오 정보:
                        - 파일명: {uploaded_file.name}
                        - 크기: {file_size:.2f} MB
                        - 분석 설정: {sampling_interval}초 간격, 최대 {max_frames}프레임
                        
                        다음 요소를 포함하여 상세한 AI 비디오 생성기 프롬프트를 생성해주세요:
                        1. 주제 (Subject)
                        2. 행동 (Action)
                        3. 장면 설명 (Scene Description)
                        4- 촬영 기법 (Cinematography - angle, movement, lighting)
                        5. 스타일 (Style)
                        
                        분석적이고 전문적인 관점에서, 이 장면을 재현할 수 있는 강력하고 간결한 프롬프트를 제공해주세요.
                        """
                        
                        response = client.chat.completions.create(
                            model="gpt-4-vision-preview",  # 비전 모델 사용
                            messages=[
                                {
                                    "role": "system", 
                                    "content": "You are a professional film director and shot analyzer. Your task is to analyze video content and generate detailed prompts for AI video generators. Your analysis must be comprehensive yet concise, focusing on visual storytelling elements."
                                },
                                {
                                    "role": "user", 
                                    "content": analysis_prompt
                                }
                            ],
                            max_tokens=1200
                        )
                        
                        analysis_result = response.choices[0].message.content
                        
                        # 분석 결과 표시
                        st.success("✅ 비디오 분석 완료!")
                        
                        with st.expander("📊 상세 분석 결과", expanded=True):
                            st.markdown(analysis_result)
                        
                        # 프롬프트 박스
                        st.markdown("### 🎯 AI 비디오 생성기 프롬프트")
                        st.code(analysis_result, language="text")
                        
                        # 복사 버튼
                        st.button("📋 프롬프트 복사하기", use_container_width=True)
                        
                    except Exception as e:
                        st.error(f"❌ 분석 중 오류가 발생했습니다: {str(e)}")

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d;'>
    <p>🎬 AI 비디오 감독 - 당신의 아이디어를 영화처럼 만들어드립니다</p>
</div>
""", unsafe_allow_html=True)
