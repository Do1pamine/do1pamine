import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz

# 设置页面配置
st.set_page_config(
    page_title="Open-Meteo Interactive Weather",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 应用CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .weather-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .temperature {
        font-size: 2rem;
        font-weight: bold;
        color: #ff4b4b;
    }
    .metric-value {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .city-button {
        width: 100%;
        margin: 0.2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 热门城市数据
POPULAR_CITIES = {
    "Seoul": {"lat": 37.5665, "lon": 126.9780, "country": "South Korea"},
    "Tokyo": {"lat": 35.6895, "lon": 139.6917, "country": "Japan"},
    "New York": {"lat": 40.7128, "lon": -74.0060, "country": "USA"},
    "London": {"lat": 51.5074, "lon": -0.1278, "country": "UK"},
    "Paris": {"lat": 48.8566, "lon": 2.3522, "country": "France"},
    "Beijing": {"lat": 39.9042, "lon": 116.4074, "country": "China"},
    "Sydney": {"lat": -33.8688, "lon": 151.2093, "country": "Australia"},
    "Dubai": {"lat": 25.2048, "lon": 55.2708, "country": "UAE"}
}

# 初始化session state
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = "Seoul"
if 'current_weather' not in st.session_state:
    st.session_state.current_weather = None
if 'hourly_forecast' not in st.session_state:
    st.session_state.hourly_forecast = None

def get_city_coordinates(city_name):
    """通过城市名获取坐标"""
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            'name': city_name,
            'count': 1,
            'language': 'en',
            'format': 'json'
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                result = data['results'][0]
                return {
                    'lat': result['latitude'],
                    'lon': result['longitude'],
                    'name': result['name'],
                    'country': result.get('country', 'Unknown')
                }
        return None
    except Exception as e:
        st.error(f"获取城市坐标时出错: {e}")
        return None

def get_weather_data(lat, lon):
    """获取天气数据"""
    try:
        # 当前天气API
        current_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': lat,
            'longitude': lon,
            'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m',
            'hourly': 'temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m',
            'timezone': 'auto',
            'forecast_days': 1
        }
        
        response = requests.get(current_url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            st.error("获取天气数据失败")
            return None
    except Exception as e:
        st.error(f"获取天气数据时出错: {e}")
        return None

def get_weather_description(weather_code):
    """根据天气代码返回描述"""
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers"
    }
    return weather_codes.get(weather_code, "Unknown")

def get_wind_direction(degrees):
    """将度数转换为风向"""
    directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 
                  'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    index = round(degrees / 22.5) % 16
    return directions[index]

# 主应用标题
st.markdown('<div class="main-header">🌤️ Open-Meteo Interactive Weather</div>', unsafe_allow_html=True)

# 创建两列布局
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("## Location Selection")
    
    # 搜索城市部分
    st.markdown("### Search by City")
    city_name = st.text_input(
        "Enter city name",
        placeholder="e.g., Seoul, Tokyo, New York",
        key="city_search"
    )
    
    if st.button("Search City", use_container_width=True) and city_name:
        with st.spinner(f"搜索 {city_name}..."):
            city_data = get_city_coordinates(city_name)
            if city_data:
                st.session_state.selected_city = city_data['name']
                weather_data = get_weather_data(city_data['lat'], city_data['lon'])
                if weather_data:
                    st.session_state.current_weather = weather_data['current']
                    st.session_state.hourly_forecast = weather_data['hourly']
                    st.success(f"成功获取 {city_data['name']}, {city_data['country']} 的天气数据")
    
    st.markdown("---")
    
    # 坐标输入部分
    st.markdown("### Or Enter Coordinates")
    coord_col1, coord_col2 = st.columns(2)
    with coord_col1:
        latitude = st.number_input(
            "Latitude",
            value=37.5665,
            format="%.4f",
            key="lat_input"
        )
    with coord_col2:
        longitude = st.number_input(
            "Longitude", 
            value=126.9780,
            format="%.4f",
            key="lon_input"
        )
    
    if st.button("Use These Coordinates", use_container_width=True):
        with st.spinner("获取坐标天气数据..."):
            weather_data = get_weather_data(latitude, longitude)
            if weather_data:
                st.session_state.selected_city = f"Custom Location ({latitude}, {longitude})"
                st.session_state.current_weather = weather_data['current']
                st.session_state.hourly_forecast = weather_data['hourly']
                st.success("成功获取坐标位置的天气数据")
    
    st.markdown("---")
    
    # 热门城市部分
    st.markdown("### Popular Cities")
    for city, info in POPULAR_CITIES.items():
        if st.button(f"{city} ↙️", key=f"btn_{city}", use_container_width=True):
            with st.spinner(f"获取 {city} 天气数据..."):
                weather_data = get_weather_data(info['lat'], info['lon'])
                if weather_data:
                    st.session_state.selected_city = city
                    st.session_state.current_weather = weather_data['current']
                    st.session_state.hourly_forecast = weather_data['hourly']
                    st.success(f"成功获取 {city} 的天气数据")

with col2:
    # 显示当前位置信息
    st.markdown(f"### Selected Location: {st.session_state.selected_city}")
    
    if st.session_state.selected_city in POPULAR_CITIES:
        city_info = POPULAR_CITIES[st.session_state.selected_city]
        st.markdown(f"**{city_info['country']}** (Lat: {city_info['lat']}, Lon: {city_info['lon']})")
    else:
        st.markdown(f"(Lat: {latitude}, Lon: {longitude})")
    
    st.markdown("---")
    
    # 显示当前天气
    if st.session_state.current_weather:
        current = st.session_state.current_weather
        weather_desc = get_weather_description(int(current.get('weather_code', 0)))
        
        st.markdown("## Current Weather")
        
        # 天气主信息卡片
        col_weather1, col_weather2, col_weather3 = st.columns(3)
        
        with col_weather1:
            st.markdown('<div class="weather-card">', unsafe_allow_html=True)
            st.markdown(f"**{weather_desc}**")
            st.markdown(f'<div class="temperature">{current.get("temperature_2m", "N/A")}°C</div>', unsafe_allow_html=True)
            st.markdown(f"Feels like: {current.get('apparent_temperature', 'N/A')}°C")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_weather2:
            st.markdown('<div class="weather-card">', unsafe_allow_html=True)
            st.markdown("**Humidity**")
            st.markdown(f'<div class="metric-value">{current.get("relative_humidity_2m", "N/A")}%</div>', unsafe_allow_html=True)
            st.markdown("Humidity")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_weather3:
            st.markdown('<div class="weather-card">', unsafe_allow_html=True)
            st.markdown("**Wind Speed**")
            st.markdown(f'<div class="metric-value">{current.get("wind_speed_10m", "N/A")} km/h</div>', unsafe_allow_html=True)
            wind_dir = get_wind_direction(current.get('wind_direction_10m', 0))
            st.markdown(f"Direction: {wind_dir}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 小时预报图表
        st.markdown("## Hourly Forecast")
        st.info("请在 Models 页面查看所有模拟的属性")
        
        if st.session_state.hourly_forecast:
            # 创建小时预报数据框
            hours = st.session_state.hourly_forecast['time'][:24]
            temperatures = st.session_state.hourly_forecast['temperature_2m'][:24]
            humidity = st.session_state.hourly_forecast['relative_humidity_2m'][:24]
            
            # 转换为本地时间
            try:
                current_time = datetime.now()
                time_labels = [f"{(current_time + timedelta(hours=i)).strftime('%H:%M')}" for i in range(24)]
            except:
                time_labels = [f"{i}:00" for i in range(24)]
            
            # 创建温度图表
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Scatter(
                x=time_labels,
                y=temperatures,
                mode='lines+markers',
                name='Temperature',
                line=dict(color='red', width=3),
                marker=dict(size=6)
            ))
            
            fig_temp.update_layout(
                title="24-Hour Temperature Forecast (°C)",
                xaxis_title="Time",
                yaxis_title="Temperature (°C)",
                height=300,
                showlegend=True
            )
            
            st.plotly_chart(fig_temp, use_container_width=True)
            
            # 创建湿度和风速数据框
            forecast_data = {
                'Time': time_labels,
                'Temperature (°C)': temperatures,
                'Humidity (%)': humidity[:24],
                'Wind Speed (km/h)': st.session_state.hourly_forecast['wind_speed_10m'][:24]
            }
            
            df_forecast = pd.DataFrame(forecast_data)
            st.dataframe(df_forecast, use_container_width=True, hide_index=True)
    
    else:
        st.info("👆 请选择或搜索一个位置来查看天气信息")

# 侧边栏信息
with st.sidebar:
    st.markdown("## ℹ️ About")
    st.markdown("""
    这个应用使用 **Open-Meteo API** 提供实时天气数据。
    
    ### 功能特点：
    - 🔍 按城市名称搜索
    - 📍 输入坐标定位
    - 🏙️ 热门城市快速访问
    - 🌡️ 当前天气状况
    - 📊 24小时天气预报
    
    ### 数据来源：
    [Open-Meteo Weather API](https://open-meteo.com/)
    """)
    
    st.markdown("## 📱 使用提示")
    st.markdown("""
    - 点击热门城市按钮快速查看天气
    - 可以输入任何城市名称（英文）
    - 小时预报显示未来24小时数据
    - 所有温度均为摄氏度
    """)

# 页脚
st.markdown("---")
st.markdown("🌤️ 数据提供: Open-Meteo Weather API | 🚀 构建于 Streamlit")