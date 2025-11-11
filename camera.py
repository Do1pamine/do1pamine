import streamlit as st
from openai import OpenAI
import os

# 页面设置
st.set_page_config(
    page_title="AI视频导演",
    page_icon="🎬",
    layout="wide"
)

# 侧边栏 - API密钥设置
with st.sidebar:
    st.header("API密钥设置")
    api_key = st.text_input("请输入OpenAI API Key:", type="password")
    
    st.markdown("---")
    st.markdown("### AI视频导演")
    st.markdown("请从选项卡中选择所需任务")

# 主要内容
st.title("🎬 AI视频导演")

# 创建选项卡
tab1, tab2 = st.tabs(["愿景1: 提示词开发器", "愿景2: 视频提示词分析器"])

with tab1:
    st.header("愿景1: 将想法发展为视频")
    
    st.subheader("当前角色: 视频导演")
    st.markdown("**您是一名专业电影导演。始终从视觉叙事的角度分析想法**")
    
    # 用户输入
    user_idea = st.text_area(
        "请输入想要发展的想法:",
        placeholder="例如: 下雨天查看设备的习惯男子",
        height=100
    )
    
    # 分析按钮
    if st.button("发展提示词"):
        if not api_key:
            st.error("请先输入OpenAI API Key。")
        elif not user_idea:
            st.error("请输入想法。")
        else:
            with st.spinner("AI正在分析您的想法..."):
                try:
                    # 初始化OpenAI客户端
                    client = OpenAI(api_key=api_key)
                    
                    # 调用OpenAI API
                    response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "您是一名专业电影导演。请从视觉叙事的角度分析想法。请包含具体场景、照明、色彩、摄像机角度、情感等进行描述。"},
                            {"role": "user", "content": f"请将以下想法发展为电影场景: {user_idea}"}
                        ],
                        max_tokens=1000
                    )
                    
                    # 显示结果
                    result = response.choices[0].message.content
                    st.subheader("视频场景分析结果:")
                    st.write(result)
                    
                except Exception as e:
                    st.error(f"API调用出错: {str(e)}")

with tab2:
    st.header("愿景2: 视频提示词分析器")
    
    # 文件上传器
    uploaded_file = st.file_uploader("请上传视频文件（可选）", type=['mp4', 'mov', 'avi'])
    
    if uploaded_file is not None:
        # 保存并显示文件
        with open("temp_video.mp4", "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.video("temp_video.mp4")
        
    # 文本分析
    video_prompt = st.text_area(
        "请输入要分析的视频提示词:",
        placeholder="请输入视频的描述或提示词",
        height=100
    )
    
    if st.button("分析提示词") and video_prompt:
        if not api_key:
            st.error("请先输入OpenAI API Key。")
        else:
            with st.spinner("正在分析视频提示词..."):
                try:
                    # 初始化OpenAI客户端
                    client = OpenAI(api_key=api_key)
                    
                    # 调用OpenAI API
                    response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "您是一名专业电影导演。请分析提供的视频提示词，并从改进点、视觉元素、叙事角度进行评估。"},
                            {"role": "user", "content": f"请分析以下视频提示词: {video_prompt}"}
                        ],
                        max_tokens=800
                    )
                    
                    # 显示结果
                    result = response.choices[0].message.content
                    st.subheader("提示词分析结果:")
                    st.write(result)
                    
                except Exception as e:
                    st.error(f"API调用出错: {str(e)}")

# 页脚
st.markdown("---")
st.markdown("### 使用方法")
st.markdown("""
1. 在侧边栏中输入OpenAI API密钥
2. 在"愿景1"选项卡中输入想法，可将其发展为视频场景
3. 在"愿景2"选项卡中分析视频提示词并查看改进建议
""")
