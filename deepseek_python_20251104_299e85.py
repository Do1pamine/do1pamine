import streamlit as st
import requests
import json
from PIL import Image
import io

# 设置页面配置
st.set_page_config(
    page_title="MET Museum Explorer",
    page_icon="🏛️",
    layout="wide"
)

# 应用标题和描述
st.title("🏛️ MET Museum Explorer")
st.markdown("### Search the collection")
st.markdown("*e.g., flower, Van Gogh, Chinese ceramics...*")

# 初始化session state
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'search_term' not in st.session_state:
    st.session_state.search_term = ""

# 搜索框
search_term = st.text_input(
    "Enter a search term above to explore the MET Museum collection",
    value=st.session_state.search_term,
    placeholder="e.g., flower, Van Gogh, Chinese ceramics..."
)

# 搜索按钮
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    search_clicked = st.button("Search", use_container_width=True)

# 快速搜索建议
st.markdown("## Try searching for:")

# 创建两列布局
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Impressionism**")
    if st.button("Van Gogh", use_container_width=True):
        search_term = "Van Gogh"
        search_clicked = True
    if st.button("Flowers", use_container_width=True):
        search_term = "Flowers"
        search_clicked = True
        
    st.markdown("**Ancient Egypt**")
    if st.button("Chinese porcelain", use_container_width=True):
        search_term = "Chinese porcelain"
        search_clicked = True
    if st.button("Sculpture", use_container_width=True):
        search_term = "Sculpture"
        search_clicked = True

with col2:
    st.markdown("**Samurai**")
    if st.button("Samurai", use_container_width=True):
        search_term = "Samurai"
        search_clicked = True
    st.markdown("**Renaissance**")
    if st.button("Renaissance", use_container_width=True):
        search_term = "Renaissance"
        search_clicked = True
    if st.button("Landscape", use_container_width=True):
        search_term = "Landscape"
        search_clicked = True

# 搜索功能
def search_met_collection(query):
    """搜索MET博物馆藏品"""
    try:
        # MET博物馆API端点
        url = f"https://collectionapi.metmuseum.org/public/collection/v1/search"
        params = {
            'q': query,
            'hasImages': True  # 只返回有图片的结果
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            st.error("Failed to fetch data from MET Museum API")
            return None
    except Exception as e:
        st.error(f"Error occurred: {e}")
        return None

def get_object_details(object_id):
    """获取特定藏品的详细信息"""
    try:
        url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

# 执行搜索
if search_clicked and search_term:
    st.session_state.search_term = search_term
    with st.spinner(f"Searching for '{search_term}'..."):
        results = search_met_collection(search_term)
        st.session_state.search_results = results

# 显示搜索结果
if st.session_state.search_results and st.session_state.search_results.get('total', 0) > 0:
    st.markdown(f"## Search Results for '{st.session_state.search_term}'")
    st.markdown(f"Found {st.session_state.search_results.get('total', 0)} results")
    
    # 获取前20个结果的详细信息
    object_ids = st.session_state.search_results.get('objectIDs', [])[:20]
    
    # 创建网格布局显示结果
    cols = st.columns(4)
    for idx, object_id in enumerate(object_ids):
        col = cols[idx % 4]
        with col:
            with st.spinner(f"Loading item {idx+1}..."):
                details = get_object_details(object_id)
                if details and details.get('primaryImageSmall'):
                    st.image(details['primaryImageSmall'], use_column_width=True)
                    st.markdown(f"**{details.get('title', 'Unknown Title')}**")
                    st.caption(f"Artist: {details.get('artistDisplayName', 'Unknown')}")
                    st.caption(f"Date: {details.get('objectDate', 'Unknown')}")
                    st.caption(f"Department: {details.get('department', 'Unknown')}")
                    st.markdown("---")
elif st.session_state.search_results and st.session_state.search_results.get('total', 0) == 0:
    st.info(f"No results found for '{st.session_state.search_term}'. Try a different search term.")

# 侧边栏信息
with st.sidebar:
    st.markdown("## About")
    st.markdown("""
    This app allows you to explore the collection of the Metropolitan Museum of Art.
    
    Search for artworks, artists, or themes to discover amazing pieces from one of the world's finest museums.
    
    Data provided by the [MET Museum API](https://metmuseum.github.io/).
    """)
    
    st.markdown("## Tips")
    st.markdown("""
    - Use specific terms for better results
    - Try artist names, art movements, or materials
    - Not all objects have images available
    """)

# 页脚
st.markdown("---")
st.markdown("Data provided by the Metropolitan Museum of Art API")