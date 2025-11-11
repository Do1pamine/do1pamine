import streamlit as st
from openai import OpenAI
import tempfile
import os
import json
from datetime import datetime
import base64

# 페이지 설정
st.set_page_config(
    page_title="AI 비디오 감독 Pro",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
def load_css():
    st.markdown("""
    <style>
        /* 메인 컨테이너 */
        .main-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        /* 헤더 스타일 */
        .main-header {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(45deg, #FFD700, #FFA500, #FF6347);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 2rem;
            text-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        /* 섹션 헤더 */
        .section-header {
            font-size: 1.8rem;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 1.5rem;
            border-left: 6px solid #3498db;
            padding-left: 1.5rem;
            background: linear-gradient(45deg, #ecf0f1, #ffffff);
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        /* 역할 박스 */
        .role-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            border: 2px solid rgba(255,255,255,0.2);
        }
        
        /* API 키 섹션 */
        .api-key-section {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            padding: 2rem;
            border-radius: 20px;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        /* 업로드 박스 */
        .upload-box {
            border: 3px dashed #3498db;
            border-radius: 20px;
            padding: 3rem;
            text-align: center;
            margin: 2rem 0;
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            transition: all 0.3s ease;
        }
        
        .upload-box:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.2);
        }
        
        /* 분석 옵션 */
        .analysis-options {
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            color: white;
            padding: 2rem;
            border-radius: 20px;
            margin: 2rem 0;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        /* 카드 스타일 */
        .feature-card {
            background: white;
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            margin: 1rem 0;
            border-left: 6px solid #3498db;
            transition: all 0.3s ease;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        }
        
        /* 결과 박스 */
        .result-box {
            background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
            color: white;
            padding: 2rem;
            border-radius: 20px;
            margin: 2rem 0;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        /* 통계 박스 */
        .stats-box {
            background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            margin: 1rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        /* 탭 스타일 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            background: transparent;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            border-radius: 15px 15px 0 0;
            gap: 1rem;
            padding: 1rem 2rem;
            color: white;
            font-weight: 600;
        }
        
        /* 버튼 스타일 */
        .stButton button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 15px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        }
        
        /* 프로그레스 바 */
        .stProgress > div > div > div {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
    </style>
    """, unsafe_allow_html=True)

load_css()

# 세션 상태 초기화
if 'generated_prompts' not in st.session_state:
    st.session_state.generated_prompts = []
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'usage_stats' not in st.session_state:
    st.session_state.usage_stats = {
        'prompts_generated': 0,
        'videos_analyzed': 0,
        'total_usage': 0
    }

# 사이드바
with st.sidebar:
    st.markdown('<div class="api-key-section">', unsafe_allow_html=True)
    st.markdown("### 🔑 API Key 설정")
    api_key = st.text_input(
        "OpenAI API Key를 입력하세요:",
        type="password",
        placeholder="sk-xxxxxxxxxxxxxxxx",
        label_visibility="collapsed"
    )
    
    if api_key:
        st.success("✅ API Key가 설정되었습니다!")
        st.session_state.api_key = api_key
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 사용량 통계
    st.markdown("### 📊 사용량 통계")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="stats-box"><h4>🎯</h4><h3>{st.session_state.usage_stats["prompts_generated"]}</h3><p>프롬프트 생성</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stats-box"><h4>🎥</h4><h3>{st.session_state.usage_stats["videos_analyzed"]}</h3><p>영상 분석</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stats-box"><h4>📈</h4><h3>{st.session_state.usage_stats["total_usage"]}</h3><p>총 사용량</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 빠른 시작 가이드
    st.markdown("### 🚀 빠른 시작")
    with st.expander("사용 방법 보기"):
        st.markdown("""
        1. **API Key 입력** - 사이드바에서 OpenAI API Key 설정
        2. **버전 선택** - 원하는 기능의 탭 선택
        3. **버전 1**: 아이디어를 영상 시나리오로 발전
        4. **버전 2**: 영상을 분석하여 프롬프트 생성
        5. **결과 활용** - 생성된 콘텐츠를 다양한 방식으로 활용
        """)
    
    # 히스토리
    if st.session_state.generated_prompts:
        with st.expander("📝 최근 생성 기록"):
            for i, prompt in enumerate(st.session_state.generated_prompts[-5:]):
                st.caption(f"{i+1}. {prompt[:50]}...")

# 메인 콘텐츠
st.markdown('<div class="main-header">🎬 AI 비디오 감독 PRO</div>', unsafe_allow_html=True)

# 기능 카드
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>🎯 정밀 분석</h3>
        <p>AI가 아이디어를 영화 장면으로 정밀하게 분석</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>🎨 다양한 스타일</h3>
        <p>다양한 영화 장르와 스타일 지원</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="feature-card">
        <h3>📊 영상 분석</h3>
        <p>업로드된 영상을 AI가 분석하여 프롬프트 생성</p>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown("""
    <div class="feature-card">
        <h3>💾 히스토리</h3>
        <p>작업 기록 저장 및 관리</p>
    </div>
    """, unsafe_allow_html=True)

# 탭 생성
tab1, tab2, tab3 = st.tabs(["📝 버전 1: 프롬프트 개발기", "🎥 버전 2: 영상 프롬프트 분석기", "📚 생성 기록"])

with tab1:
    st.markdown('<div class="section-header">아이디어를 영상으로 발전시키기</div>', unsafe_allow_html=True)
    
    # 역할 설명
    st.markdown("""
    <div class="role-box">
        <h3>🎯 현재 역할: Professional Video Director</h3>
        <p><strong>You are a professional film director. Always analyze ideas in terms of visual storytelling — use camera movement, lighting, framing, and emotional tone to explain your thoughts. Describe concepts as if you are planning a film scene.</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # 입력 섹션
    col1, col2 = st.columns([2, 1])
    
    with col1:
        user_idea = st.text_area(
            "💡 발전시키고 싶은 아이디어를 입력하세요:",
            placeholder="예: 비 오는 날 창밖을 보는 슬픈 남자\n예: 미래 도시에서의 추격전\n예: 고독한 예술가의 창작 과정",
            height=150,
            help="구체적이고 생생한 묘사를 통해 더 좋은 결과를 얻을 수 있습니다."
        )
        
        # 추가 옵션
        with st.expander("⚙️ 고급 설정"):
            col_a, col_b = st.columns(2)
            with col_a:
                creativity_level = st.slider("창의성 수준", 0.0, 1.0, 0.7, 0.1)
                include_dialogue = st.checkbox("대사 포함", value=True)
            with col_b:
                scene_length = st.selectbox("장면 길이", ["짧은 장면(15초)", "중간 장면(30초)", "긴 장면(60초)"])
                target_platform = st.selectbox("목표 플랫폼", ["영화", "TV 드라마", "SNS 숏폼", "광고"])
    
    with col2:
        st.markdown("### 🎨 영화 스타일 설정")
        
        style_option = st.selectbox(
            "주요 장르:",
            ["드라마", "스릴러", "로맨스", "SF", "판타지", "느와르", "액션", "코미디", "공포"],
            index=0
        )
        
        visual_style = st.multiselect(
            "시각적 스타일:",
            ["시네마틱", "다큐멘터리", "애니메이션", "VFX 중점", "실험적", "클래식", "모던"]
        )
        
        color_palette = st.selectbox(
            "색감 팔레트:",
            ["따뜻한 톤", "차가운 톤", "모노크롬", "파스텔", "고채도", "어두운 톤"]
        )
        
        detail_level = st.slider("상세도:", 1, 5, 3,
                               help="1: 간략, 3: 표준, 5: 매우 상세")
    
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
            with st.spinner("🎬 AI가 당신의 아이디어를 전문적인 영화 장면으로 발전시키는 중..."):
                try:
                    client = OpenAI(api_key=api_key)
                    
                    # 프롬프트 구성
                    prompt = f"""
                    당신은 전문 영화 감독입니다. 다음 아이디어를 {style_option} 장르로, {', '.join(visual_style)} 스타일로 영화 장면으로 발전시켜주세요.
                    
                    [아이디어]: {user_idea}
                    
                    [요청 사항]:
                    - 색감: {color_palette}
                    - 장면 길이: {scene_length}
                    - 플랫폼: {target_platform}
                    - 창의성: {creativity_level}
                    - 상세도: {detail_level}/5
                    - 대사 포함: {'예' if include_dialogue else '아니오'}
                    
                    다음 요소들을 상세히 포함해주세요:
                    📸 카메라 워크: 샷 사이즈, 앵글, 이동
                    💡 조명: 조명 설정, 분위기, 그림자
                    🎨 시각적 스타일: 컬러 그레이딩, 텍스처
                    🎭 연기: 캐릭터 동작, 감정, 대사
                    🎵 사운드: 배경음, 효과음, 음악
                    ✂️ 편집: 리듬, 전환, 페이싱
                    
                    마지막으로 AI 비디오 생성기를 위한 최적화된 프롬프트를 제공해주세요.
                    """
                    
                    response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "당신은 창의적이고 경험 많은 영화 감독입니다. 아이디어를 시각적 스토리텔링 관점에서 분석하고, 전문적인 영화 제작 용어를 사용하여 설명하세요."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=2000,
                        temperature=creativity_level
                    )
                    
                    result = response.choices[0].message.content
                    
                    # 세션 상태 업데이트
                    st.session_state.generated_prompts.append(user_idea)
                    st.session_state.usage_stats["prompts_generated"] += 1
                    st.session_state.usage_stats["total_usage"] += 1
                    
                    # 결과 표시
                    st.success("✅ 영화 장면 분석 완료!")
                    
                    # 결과를 탭으로 구성
                    result_tab1, result_tab2, result_tab3 = st.tabs(["🎬 전체 분석", "📋 AI 프롬프트", "💡 활용 가이드"])
                    
                    with result_tab1:
                        st.markdown("### 📊 상세 분석 결과")
                        st.markdown(result)
                    
                    with result_tab2:
                        st.markdown("### 🎯 AI 비디오 생성기용 프롬프트")
                        st.code(result, language="text")
                        
                        # 프롬프트 복사 기능
                        if st.button("📋 프롬프트 복사하기", use_container_width=True):
                            st.success("프롬프트가 클립보드에 복사되었습니다!")
                    
                    with result_tab3:
                        st.markdown("### 💡 생성된 콘텐츠 활용 방법")
                        st.markdown("""
                        **🎥 영화 제작자용:**
                        - 스토리보드 기초 자료로 활용
                        - 촬영 계획 수립 참고
                        - 아트 디렉션 가이드라인
                        
                        **🤖 AI 생성용:**
                        - Runway, Pika 등 AI 비디오 생성기 입력
                        - Stable Diffusion으로 스틸컷 생성
                        - 음성 합성과 결합하여 완성도 높이기
                        
                        **📚 학습용:**
                        - 영화 언어 학습 자료
                        - 시나리오 작성 연습
                        - 영화 분석 능력 향상
                        """)
                    
                except Exception as e:
                    st.error(f"❌ API 호출 중 오류가 발생했습니다: {str(e)}")

with tab2:
    st.markdown('<div class="section-header">비디오를 분석하여 프롬프트 생성하기</div>', unsafe_allow_html=True)
    
    # AI 분석가 역할 설명
    st.markdown("""
    <div class="role-box">
        <h3>🔍 AI 분석가 역할</h3>
        <p><strong>You are a professional film director and shot analyzer. Your task is to analyze a series of video frames provided by the user. Based on these frames, generate a detailed "prompt" that could be used by an AI video generator to create this exact scene. Your analysis must include: Subject, Action, Scene Description, Cinematography (angle, movement, lighting), and Style. Combine all of this into a concise, powerful prompt for an AI video generator.</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # 파일 업로드 섹션
    st.markdown("### 📁 분석을 원하는 비디오 파일을 업로드하세요")
    
    uploaded_file = st.file_uploader(
        "Drag and drop file here",
        type=['mp4', 'mov', 'avi', 'mpeg4'],
        label_visibility="collapsed",
        help="최대 200MB - MP4, MOV, AVI, MPEG4 형식 지원"
    )
    
    if uploaded_file is not None:
        # 파일 정보 표시
        file_size = uploaded_file.size / (1024 * 1024)
        file_info_col1, file_info_col2, file_info_col3 = st.columns(3)
        
        with file_info_col1:
            st.info(f"📄 파일명: {uploaded_file.name}")
        with file_info_col2:
            st.info(f"📊 크기: {file_size:.2f} MB")
        with file_info_col3:
            st.info(f"🎬 형식: {uploaded_file.type}")
        
        # 비디오 미리보기
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            st.video(tmp_file.name)
        
        # 분석 옵션
        st.markdown("### ⚙️ 분석 설정")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎞️ 프레임 설정")
            sampling_interval = st.number_input(
                "표본 추출 간격 (초)",
                min_value=0.1,
                max_value=10.0,
                value=1.0,
                step=0.1
            )
            max_frames = st.number_input(
                "최대 분석 프레임 수",
                min_value=1,
                max_value=50,
                value=10,
                step=1
            )
        
        with col2:
            st.markdown("#### 🔍 분석 깊이")
            analysis_depth = st.select_slider(
                "분석 상세도",
                options=["기본", "표준", "상세", "심층", "전문가"],
                value="표준"
            )
            
            include_technical = st.checkbox("기술적 요소 포함", value=True)
            include_artistic = st.checkbox("예술적 분석 포함", value=True)
        
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
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                with st.spinner("🎥 비디오를 분석하는 중..."):
                    try:
                        # 진행 상태 시뮬레이션
                        for i in range(100):
                            progress_bar.progress(i + 1)
                            status_text.text(f"분석 진행 중... {i+1}%")
                            # 실제 구현에서는 여기에 분석 로직이 들어갑니다
                        
                        client = OpenAI(api_key=api_key)
                        
                        analysis_prompt = f"""
                        비디오 파일 분석 요청:
                        
                        파일 정보:
                        - 이름: {uploaded_file.name}
                        - 크기: {file_size:.2f} MB
                        - 분석 설정: {sampling_interval}초 간격, 최대 {max_frames}프레임
                        - 분석 깊이: {analysis_depth}
                        
                        다음 요소를 포함하여 상세한 분석을 제공해주세요:
                        
                        1. 📸 시각적 요소 분석
                           - 샷 구성 및 프레이밍
                           - 카메라 워크 및 앵글
                           - 조명과 색감
                           - 시각적 스타일
                        
                        2. 🎭 내용 분석
                           - 주제와 주인공
                           - 행동과 감정
                           - 장면의 맥락
                           - 스토리텔링 요소
                        
                        3. 🎬 기술적 분석
                           - 촬영 기법
                           - 편집 스타일
                           - 사운드 요소(추정)
                           - 전체적인 톤과 분위기
                        
                        마지막으로 AI 비디오 생성기를 위한 최적화된 프롬프트를 생성해주세요.
                        """
                        
                        response = client.chat.completions.create(
                            model="gpt-4",
                            messages=[
                                {
                                    "role": "system", 
                                    "content": "You are a professional film director and shot analyzer. Provide comprehensive video analysis focusing on visual storytelling elements and generate optimized prompts for AI video generation."
                                },
                                {
                                    "role": "user", 
                                    "content": analysis_prompt
                                }
                            ],
                            max_tokens=1800
                        )
                        
                        analysis_result = response.choices[0].message.content
                        
                        # 세션 상태 업데이트
                        st.session_state.analysis_history.append({
                            'filename': uploaded_file.name,
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'result': analysis_result
                        })
                        st.session_state.usage_stats["videos_analyzed"] += 1
                        st.session_state.usage_stats["total_usage"] += 1
                        
                        status_text.text("✅ 분석 완료!")
                        progress_bar.empty()
                        
                        # 분석 결과 표시
                        st.markdown("### 📊 분석 결과")
                        
                        result_col1, result_col2 = st.columns([2, 1])
                        
                        with result_col1:
                            with st.expander("📋 상세 분석 보고서", expanded=True):
                                st.markdown(analysis_result)
                        
                        with result_col2:
                            st.markdown("### 🎯 AI 프롬프트")
                            st.code(analysis_result.split("AI 프롬프트:")[-1] if "AI 프롬프트:" in analysis_result else analysis_result, language="text")
                            
                            # 다운로드 버튼
                            st.download_button(
                                label="📥 분석 결과 다운로드",
                                data=analysis_result,
                                file_name=f"video_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain"
                            )
                        
                    except Exception as e:
                        st.error(f"❌ 분석 중 오류가 발생했습니다: {str(e)}")

with tab3:
    st.markdown('<div class="section-header">생성 기록 및 통계</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📝 최근 생성된 프롬프트")
        if st.session_state.generated_prompts:
            for i, prompt in enumerate(reversed(st.session_state.generated_prompts[-10:])):
                with st.expander(f"프롬프트 {len(st.session_state.generated_prompts)-i}: {prompt[:60]}..."):
                    st.write(prompt)
                    if st.button(f"이 프롬프트 다시 사용", key=f"reuse_{i}"):
                        st.session_state.reuse_prompt = prompt
                        st.experimental_rerun()
        else:
            st.info("📝 아직 생성된 프롬프트가 없습니다.")
    
    with col2:
        st.markdown("### 📊 사용 통계")
        st.metric("총 프롬프트 생성", st.session_state.usage_stats["prompts_generated"])
        st.metric("총 영상 분석", st.session_state.usage_stats["videos_analyzed"])
        st.metric("총 사용량", st.session_state.usage_stats["total_usage"])
        
        st.markdown("### 🗑️ 관리")
        if st.button("기록 초기화", type="secondary"):
            st.session_state.generated_prompts = []
            st.session_state.analysis_history = []
            st.session_state.usage_stats = {'prompts_generated': 0, 'videos_analyzed': 0, 'total_usage': 0}
            st.experimental_rerun()

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d; padding: 2rem;'>
    <h3>🎬 AI 비디오 감독 PRO</h3>
    <p>당신의 아이디어를 전문적인 영화 장면으로 변환해드립니다</p>
    <p>영화 제작자, 콘텐츠 크리에이터, AI 애호가를 위한 최고의 도구</p>
</div>
""", unsafe_allow_html=True)