import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import random
from scipy import ndimage
import pandas as pd
import io

st.set_page_config(page_title="🌌 Cosmic Nebula Generator", layout="wide")

# -----------------------------------
# 色板管理器
# -----------------------------------
class ColorPaletteManager:
    def __init__(self):
        self.default_palettes = [
            ["#0b0b2b", "#1a1a4b", "#2d2d7a", "#4a4ab8", "#6b6bff", "#9d9dff"],
            ["#1a0033", "#330066", "#6600cc", "#9966ff", "#ccb3ff", "#e6d9ff"],
            ["#00264d", "#004d99", "#0080ff", "#66b3ff", "#b3d9ff", "#e6f2ff"],
            ["#330033", "#660066", "#990099", "#cc00cc", "#ff66ff", "#ffb3ff"],
            ["#003300", "#006600", "#009900", "#00cc00", "#66ff66", "#b3ffb3"],
        ]
        self.custom_palettes = []
        self.palette_names = [f"默认色板 {i+1}" for i in range(len(self.default_palettes))]
        self.palette_names_custom = []
        self.current_palette_idx = 0
    
    def get_all_palettes(self):
        return self.default_palettes + [p['colors'] for p in self.custom_palettes]
    
    def get_palette_names(self):
        return self.palette_names + self.palette_names_custom
    
    def get_palette(self, idx):
        return self.get_all_palettes()[idx]
    
    def add_palette(self, name, colors):
        if len([c for c in colors if self.is_valid_color(c)]) >= 3:
            self.custom_palettes.append({'name': name, 'colors': colors})
            self.palette_names_custom.append(f"自定义: {name}")
            return True
        return False

    def delete_palette(self, idx):
        if idx < len(self.default_palettes):
            return False
        custom_idx = idx - len(self.default_palettes)
        if 0 <= custom_idx < len(self.custom_palettes):
            del self.custom_palettes[custom_idx]
            del self.palette_names_custom[custom_idx]
            return True
        return False

    def is_valid_color(self, color):
        return (isinstance(color, str) and color.startswith('#') and len(color) in [7, 9])
    
    def export_as_csv(self):
        if not self.custom_palettes:
            return None
        csv_data = "PaletteName,Color1,Color2,Color3,Color4,Color5,Color6\n"
        for item in self.custom_palettes:
            colors = item['colors'] + [''] * (6 - len(item['colors']))
            row = [item['name']] + colors[:6]
            csv_data += ','.join([f'"{i}"' for i in row]) + "\n"
        return csv_data.encode("utf-8")

    def import_csv(self, csv_bytes):
        content = csv_bytes.decode("utf-8")
        try:
            df = pd.read_csv(io.StringIO(content))
            imported = 0
            for _, row in df.iterrows():
                name = str(row.iloc[0])
                colors = [str(row.iloc[i]) for i in range(1,7) if pd.notna(row.iloc[i]) and self.is_valid_color(str(row.iloc[i]))]
                if len(colors) >= 3 and name and name not in self.palette_names_custom:
                    self.add_palette(name, colors)
                    imported += 1
            return imported
        except Exception as e:
            return 0

palette_manager = ColorPaletteManager()

# -----------------------------------
# Nebula Core Functions
# -----------------------------------
def generate_fractal_noise(resolution, octaves=4, persistence=0.5):
    noise = np.zeros((resolution, resolution))
    frequency = 1
    amplitude = 1
    max_amplitude = 0
    for _ in range(octaves):
        octave_noise = np.random.normal(0, 1, (resolution, resolution))
        octave_noise = ndimage.gaussian_filter(octave_noise, sigma=1/frequency)
        noise += octave_noise * amplitude
        max_amplitude += amplitude
        amplitude *= persistence
        frequency *= 2
    return noise / max_amplitude

def create_nebula_density(center=(0.5, 0.5), size=0.4, resolution=200):
    x = np.linspace(0, 1, resolution)
    y = np.linspace(0, 1, resolution)
    X, Y = np.meshgrid(x, y)
    dist_from_center = np.sqrt((X - center[0]) ** 2 + (Y - center[1]) ** 2)
    density = np.zeros_like(X)
    main_body = np.exp(-(dist_from_center ** 2) / (2 * (size / 3) ** 2))
    num_clumps = random.randint(8, 15)
    for _ in range(num_clumps):
        clump_x = center[0] + random.uniform(-size*0.8, size*0.8)
        clump_y = center[1] + random.uniform(-size*0.8, size*0.8)
        clump_size = random.uniform(size/8, size/4)
        clump_dist = np.sqrt((X - clump_x) ** 2 + (Y - clump_y) ** 2)
        clump = np.exp(-(clump_dist ** 2) / (2 * clump_size ** 2)) * random.uniform(0.3, 0.7)
        density += clump
    num_filaments = random.randint(3, 6)
    for _ in range(num_filaments):
        angle = random.uniform(0, 2 * np.pi)
        length = random.uniform(size * 0.5, size * 1.2)
        width = random.uniform(size / 15, size / 8)
        filament_x = center[0] + np.cos(angle) * length * np.linspace(-0.5, 0.5, resolution)[:, np.newaxis]
        filament_y = center[1] + np.sin(angle) * length * np.linspace(-0.5, 0.5, resolution)[np.newaxis, :]
        filament_dist = np.sqrt((X - filament_x) ** 2 + (Y - filament_y) ** 2)
        filament = np.exp(-(filament_dist ** 2) / (2 * width ** 2)) * random.uniform(0.4, 0.8)
        density += filament
    density = main_body * 0.6 + density * 0.4
    fractal_noise = generate_fractal_noise(resolution, octaves=4)
    density += fractal_noise * 0.2
    density = ndimage.gaussian_filter(density, sigma=1.2)
    density = (density - density.min()) / (density.max() - density.min())
    return X, Y, density

def create_nebula_colormap(colors):
    return LinearSegmentedColormap.from_list("nebula_cmap", colors)

def create_starfield(resolution=800, num_stars=600, brightness_factor=1.0):
    starfield = np.zeros((resolution, resolution))
    for _ in range(num_stars):
        x = random.randint(0, resolution-1)
        y = random.randint(0, resolution-1)
        base_brightness = random.uniform(0.5, 1.2) * brightness_factor
        size = random.randint(1, 4)
        for i in range(max(0, x-size), min(resolution, x+size+1)):
            for j in range(max(0, y-size), min(resolution, y+size+1)):
                dist = np.sqrt((i-x)**2 + (j-y)**2)
                if dist <= size:
                    star_intensity = base_brightness * (1 - dist/size)
                    starfield[j, i] = max(starfield[j, i], star_intensity)
    tiny_stars = np.random.random((resolution, resolution)) * 0.2 * brightness_factor
    tiny_stars = tiny_stars * (tiny_stars > 0.06)
    starfield += tiny_stars
    for _ in range(20):
        x = random.randint(0, resolution-1)
        y = random.randint(0, resolution-1)
        bright_star_intensity = random.uniform(1.5, 2.5) * brightness_factor
        size = random.randint(2, 5)
        for i in range(max(0, x-size), min(resolution, x+size+1)):
            for j in range(max(0, y-size), min(resolution, y+size+1)):
                dist = np.sqrt((i-x)**2 + (j-y)**2)
                if dist <= size:
                    intensity = bright_star_intensity * (1 - dist/size)
                    starfield[j, i] = max(starfield[j, i], intensity)
    starfield = np.clip(starfield, 0, 1.0)
    return starfield

def draw_nebula(X, Y, density, colors, brightness=0.8, star_brightness=1.0, with_starfield=True):
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    cmap = create_nebula_colormap(colors)
    adjusted_density = density * brightness
    im = ax.imshow(adjusted_density, extent=[0, 1, 0, 1], cmap=cmap,
                   origin='lower', alpha=0.9, vmin=0, vmax=1)
    if with_starfield:
        starfield = create_starfield(brightness_factor=star_brightness)
        ax.imshow(starfield, extent=[0, 1, 0, 1], cmap='gray',
                  origin='lower', alpha=0.8, vmin=0, vmax=1)
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    plt.tight_layout()
    return fig

# -----------------------------------
# Streamlit UI
# -----------------------------------

st.title("🌌 宇宙云气体（Nebula）生成器 · 支持色板CSV管理")
tab1, tab2 = st.tabs(["生成器", "色板管理 (CSV)"])

with tab2:
    st.markdown("### 🎨 自定义色板管理")
    with st.form("palette_form", clear_on_submit=False):
        new_name = st.text_input("色板名称", "我的色板")
        cols = st.columns(6)
        new_colors = [cols[i].color_picker(f"色{i+1}", "#ff6b6b" if i == 0 else "#ffffff") for i in range(6)]
        submitted = st.form_submit_button("➕ 添加色板")
        if submitted:
            ok = palette_manager.add_palette(new_name, new_colors)
            if ok:
                st.success(f"添加色板「{new_name}」成功！")
            else:
                st.error("至少需要 3 个有效色！")
    # 展示和删除自定义色板
    if palette_manager.custom_palettes:
        st.markdown("**自定义色板列表（点击删除）**")
        for i, item in enumerate(palette_manager.custom_palettes):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"🎨 {item['name']}: {', '.join(item['colors'])}")
            with col2:
                if st.button("🗑️ 删除", key=f"delpal{i}"):
                    idx = i + len(palette_manager.default_palettes)
                    palette_manager.delete_palette(idx)
                    st.experimental_rerun()

    # 导出CSV
    pal_csv = palette_manager.export_as_csv()
    if pal_csv:
        st.download_button("📁 导出自定义色板为CSV", pal_csv, file_name="nebula_palettes.csv", mime="text/csv")
    # 导入CSV
    uploaded = st.file_uploader("📂 导入色板CSV", type="csv")
    if uploaded:
        count = palette_manager.import_csv(uploaded.read())
        if count > 0:
            st.success(f"导入 {count} 个色板成功！")
            st.experimental_rerun()
        else:
            st.error("未能导入任何有效色板。")

with tab1:
    st.markdown("#### 设置参数并生成你的专属宇宙云气体图片")
    c1, c2 = st.columns([3, 2])
    with c2:
        st.markdown("##### 参数控制")
        density = st.slider("云气体密度", 0.1, 1.0, 0.3, 0.05)
        brightness = st.slider("云气体亮度", 0.3, 1.5, 0.8, 0.05)
        star_brightness = st.slider("星空亮度", 0.5, 2.5, 1.0, 0.1)
        center_x = st.slider("中心 X", 0.1, 0.9, 0.5, 0.01)
        center_y = st.slider("中心 Y", 0.1, 0.9, 0.5, 0.01)
        size = st.slider("云气体尺寸", 0.2, 0.8, 0.4, 0.01)
        palette_names = palette_manager.get_palette_names()
        palette_idx = st.selectbox("色板选择", range(len(palette_names)), format_func=lambda x: palette_names[x])
        btn_new = st.button("🔄 生成新云气体")
        btn_rand = st.button("🎲 随机参数生成")

    with c1:
        if 'nebula' not in st.session_state or btn_new or btn_rand:
            if btn_rand:
                center_x = round(random.uniform(0.2, 0.8), 2)
                center_y = round(random.uniform(0.2, 0.8), 2)
                size = round(random.uniform(0.3, 0.6), 2)
                st.session_state['rand_params'] = (center_x, center_y, size)
            elif 'rand_params' in st.session_state:
                center_x, center_y, size = st.session_state['rand_params']
            X, Y, density_map = create_nebula_density(center=(center_x, center_y), size=size)
            st.session_state['nebula'] = (X, Y, density_map)
        else:
            X, Y, density_map = st.session_state['nebula']
        colors = palette_manager.get_palette(palette_idx)
        nebula_fig = draw_nebula(X, Y, density_map * density, colors, brightness, star_brightness)
        st.pyplot(nebula_fig, use_container_width=True)
        st.caption(f"色板：{palette_names[palette_idx]} | 密度: {density}, 亮度: {brightness}, 星亮度: {star_brightness}")

st.markdown("""
---
**功能说明**  
- 支持自定义色板、色板CSV导入导出、色板删除  
- 支持中心/尺寸/密度/亮度/星空等参数自由调节  
- 所有操作一键实时可见，适合科学/艺术创作或壁纸生成！
""")