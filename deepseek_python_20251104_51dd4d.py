import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

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
        border-left: 5px solid #1f77b4;
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
    .hourly-forecast {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 1px solid #ddd;
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
        st.error(f"Error getting city coordinates: {e}")
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
            st.error("Failed to get weather data")
            return None
    except Exception as e:
        st.error(f"Error getting weather data: {e}")
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

def create_simple_chart(temperatures, times):
    """创建简单的文本图表"""
    max_temp = max(temperatures)
    min_temp = min(temperatures)
    
    chart_lines = []
    for i, (temp, time_str) in enumerate(zip(temperatures, times)):
        # 创建简单的条形图
        bar_length = int((temp - min_temp) / (max_temp - min_temp) * 20) if max_temp != min_temp else 10
        bar = "█" * bar_length
        chart_lines.append(f"{time_str}: {bar} {temp:.1f}°C")
    
    return "\n".join(chart_lines)

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
        with st.spinner(f"Searching for {city_name}..."):
            city_data = get_city_coordinates(city_name)
            if city_data:
                st.session_state.selected_city = city_data['name']
                weather_data = get_weather_data(city_data['lat'], city_data['lon'])
                if weather_data:
                    st.session_state.current_weather = weather_data['current']
                    st.session_state.hourly_forecast = weather_data['hourly']
                    st.success(f"Successfully got weather data for {city_data['name']}, {city_data['country']}")
    
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
        with st.spinner("Getting weather data for coordinates..."):
            weather_data = get_weather_data(latitude, longitude)
            if weather_data:
                st.session_state.selected_city = f"Custom Location ({latitude}, {longitude})"
                st.session_state.current_weather = weather_data['current']
                st.session_state.hourly_forecast = weather_data['hourly']
                st.success("Successfully got weather data for coordinates")
    
    st.markdown("---")
    
    # 热门城市部分
    st.markdown("### Popular Cities")
    for city, info in POPULAR_CITIES.items():
        if st.button(f"{city} ↙️", key=f"btn_{city}", use_container_width=True):
            with st.spinner(f"Getting weather data for {city}..."):
                weather_data = get_weather_data(info['lat'], info['lon'])
                if weather_data:
                    st.session_state.selected_city = city
                    st.session_state.current_weather = weather_data['current']
                    st.session_state.hourly_forecast = weather_data['hourly']
                    st.success(f"Successfully got weather data for {city}")

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
        
        # 小时预报
        st.markdown("## Hourly Forecast")
        st.info("Please check the Models page for all simulated properties")
        
        if st.session_state.hourly_forecast:
            # 创建小时预报数据框
            hours = st.session_state.hourly_forecast['time'][:24]
            temperatures = st.session_state.hourly_forecast['temperature_2m'][:24]
            humidity = st.session_state.hourly_forecast['relative_humidity_2m'][:24]
            wind_speed = st.session_state.hourly_forecast['wind_speed_10m'][:24]
            
            # 简化时间显示
            time_labels = []
            for hour in hours:
                try:
                    # 解析时间字符串
                    time_obj = datetime.fromisoformat(hour.replace('Z', '+00:00'))
                    time_labels.append(time_obj.strftime('%H:%M'))
                except:
                    time_labels.append(hour)
            
            # 显示简单的文本图表
            st.markdown("### Temperature Trend")
            chart_text = create_simple_chart(temperatures, time_labels[:12])  # 只显示前12小时
            st.text(chart_text)
            
            # 创建详细数据表格
            st.markdown("### Detailed Forecast Data")
            forecast_data = {
                'Time': time_labels[:12],
                'Temp (°C)': [f"{temp:.1f}" for temp in temperatures[:12]],
                'Humidity (%)': [f"{hum:.0f}" for hum in humidity[:12]],
                'Wind (km/h)': [f"{wind:.1f}" for wind in wind_speed[:12]]
            }
            
            df_forecast = pd.DataFrame(forecast_data)
            st.dataframe(df_forecast, use_container_width=True, hide_index=True)
            
            # 显示统计信息
            st.markdown("### Statistics")
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("Max Temperature", f"{max(temperatures):.1f}°C")
            with col_stat2:
                st.metric("Min Temperature", f"{min(temperatures):.1f}°C")
            with col_stat3:
                st.metric("Average", f"{sum(temperatures)/len(temperatures):.1f}°C")
    
    else:
        st.info("👆 Please select or search for a location to view weather information")

# 侧边栏信息
with st.sidebar:
    st.markdown("## ℹ️ About")
    st.markdown("""
    This app uses the **Open-Meteo API** to provide real-time weather data.
    
    ### Features:
    - 🔍 Search by city name
    - 📍 Input coordinates
    - 🏙️ Quick access to popular cities
    - 🌡️ Current weather conditions
    - 📊 24-hour weather forecast
    
    ### Data Source:
    [Open-Meteo Weather API](https://open-meteo.com/)
    """)
    
    st.markdown("## 📱 Tips")
    st.markdown("""
    - Click popular city buttons for quick access
    - Enter any city name (in English)
    - Hourly forecast shows next 24 hours
    - All temperatures in Celsius
    """)

# 页脚
st.markdown("---")
st.markdown("🌤️ Data provided by: Open-Meteo Weather API | 🚀 Built with Streamlit")