import streamlit as st
import openai
import os

# 페이지 설정
st.set_page_config(
    page_title="AI 비디오 감독",
    page_icon="🎬",
    layout="wide"
)

# 사이드바 - API 키 설정
with st.sidebar:
    st.header("API Key 설정")
    api_key = st.text_input("OpenAI API Key를 입력하세요:", type="password")
    
    if api_key:
        openai.api_key = api_key
        st.success("API Key가 설정되었습니다!")
    
    st.markdown("---")
    st.markdown("### AI 비디오 감독")
    st.markdown("원하는 작업을 탭에서 선택하세요")

# 메인 콘텐츠
st.title("🎬 AI 비디오 감독")

# 탭 생성
tab1, tab2 = st.tabs(["비전 1: 프롬프트 디벨로퍼", "비전 2: 영상 프롬프트 분석기"])

with tab1:
    st.header("비전 1: 아이디어를 영상으로 발전시키기")
    
    st.subheader("현재 역할: Video Director")
    st.markdown("**You are a professional film director. Always analyze ideas in terms of visual storytelling**")
    
    # 사용자 입력
    user_idea = st.text_area(
        "발전시키고 싶은 아이디어를 입력하세요:",
        placeholder="예: 이·비 오는 날 장비를 보는 습득 남자"
    )
    
    # 분석 버튼
    if st.button("프롬프트 발전시키기"):
        if not api_key:
            st.error("OpenAI API Key를 먼저 입력해주세요.")
        elif not user_idea:
            st.error("아이디어를 입력해주세요.")
        else:
            with st.spinner("AI가 아이디어를 분석하고 있습니다..."):
                try:
                    # OpenAI API 호출
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "당신은 전문 영화 감독입니다. 아이디어를 시각적 스토리텔링 관점에서 분석하세요. 구체적인 장면, 조명, 색감, 카메라 앵글, 감정 등을 포함하여 설명해주세요."},
                            {"role": "user", "content": f"다음 아이디어를 영화 장면으로 발전시켜주세요: {user_idea}"}
                        ],
                        max_tokens=1000
                    )
                    
                    # 결과 표시
                    result = response.choices[0].message.content
                    st.subheader("영상 시나리오 분석 결과:")
                    st.write(result)
                    
                except Exception as e:
                    st.error(f"API 호출 중 오류가 발생했습니다: {str(e)}")

with tab2:
    st.header("비전 2: 영상 프롬프트 분석기")
    st.info("이 기능은 아직 개발 중입니다. 추후 영상 프롬프트를 분석하는 기능이 추가될 예정입니다.")
    
    # 파일 업로더
    uploaded_file = st.file_uploader("영상 파일을 업로드하세요 (선택사항)", type=['mp4', 'mov', 'avi'])
    
    if uploaded_file is not None:
        st.video(uploaded_file)
        
    # 텍스트 분석
    video_prompt = st.text_area(
        "분석할 영상 프롬프트를 입력하세요:",
        placeholder="영상에 대한 설명이나 프롬프트를 입력해주세요"
    )
    
    if st.button("프롬프트 분석하기") and video_prompt:
        if not api_key:
            st.error("OpenAI API Key를 먼저 입력해주세요.")
        else:
            with st.spinner("영상 프롬프트를 분석하고 있습니다..."):
                try:
                    # OpenAI API 호출
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "당신은 전문 영화 감독입니다. 제공된 영상 프롬프트를 분석하고, 개선점, 시각적 요소, 스토리텔링 측면에서 평가해주세요."},
                            {"role": "user", "content": f"다음 영상 프롬프트를 분석해주세요: {video_prompt}"}
                        ],
                        max_tokens=800
                    )
                    
                    # 결과 표시
                    result = response.choices[0].message.content
                    st.subheader("프롬프트 분석 결과:")
                    st.write(result)
                    
                except Exception as e:
                    st.error(f"API 호출 중 오류가 발생했습니다: {str(e)}")

# 푸터
st.markdown("---")
st.markdown("### 사용 방법")
st.markdown("""
1. 사이드바에서 OpenAI API Key를 입력하세요
2. '비전 1' 탭에서 아이디어를 입력하고 영상 시나리오로 발전시킬 수 있습니다
3. '비전 2' 탭에서 영상 프롬프트를 분석하고 개선점을 확인할 수 있습니다
""")