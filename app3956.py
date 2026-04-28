import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide", initial_sidebar_state="collapsed")

# --- 2. HỆ THỐNG NGÔN NGỮ ---
lang_option = st.selectbox("🌐 Ngôn ngữ / Language:", ["VN", "EN"])

texts = {
    "VN": {
        "header": "HỆ THỐNG QUẢN LÝ KPI - SHARED HOUSE 3956",
        "tab1": "👤 HỒ SƠ CHI TIẾT", "tab2": "📊 TỔNG QUAN QUÂN ĐOÀN",
        "select_player": "🔍 CHỌN CHIẾN BINH:", "rank": "🏆 HẠNG",
        "power_now": "🛡️ SỨC MẠNH", "kpi_kill_pct": "🔥 % KILL",
        "kpi_dead_pct": "💀 % DEAD", "detail_title": "##### 📌 THÔNG SỐ CHI TIẾT",
        "table_title": "🏆 BẢNG THỐNG KÊ CHI TIẾT TOÀN QUÂN",
        "col_rank": "HẠNG 🏆", "col_name": "CHIẾN BINH 🥷", "col_power": "SỨC MẠNH 🛡️",
        "col_kill": "ĐIỂM KILL ⚔️", "col_kpi_kill": "KPI KILL 🔥",
        "col_dead": "LÍNH CHẾT 💀", "col_kpi_dead": "KPI DEAD ⚰️"
    },
    "EN": {
        "header": "KPI MANAGEMENT SYSTEM - SHARED HOUSE 3956",
        "tab1": "👤 DETAILED PROFILE", "tab2": "📊 ALLIANCE OVERVIEW",
        "select_player": "🔍 SELECT COMMANDER:", "rank": "🏆 RANK",
        "power_now": "🛡️ POWER", "kpi_kill_pct": "🔥 % KILL",
        "kpi_dead_pct": "💀 % DEAD", "detail_title": "##### 📌 DETAILED STATISTICS",
        "table_title": "🏆 ALLIANCE DETAILED STATISTICS TABLE",
        "col_rank": "RANK 🏆", "col_name": "COMMANDER 🥷", "col_power": "POWER 🛡️",
        "col_kill": "KILL POINTS ⚔️", "col_kpi_kill": "KPI KILL 🔥",
        "col_dead": "DEAD UNITS 💀", "col_kpi_dead": "KPI DEAD ⚰️"
    }
}
L = texts[lang_option]

# --- 3. GIAO DIỆN CSS NÂNG CẤP (CHO BẢNG ĐẸP VÀ TO) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0d1117; color: #c9d1d9; }}
    
    /* Làm đẹp Header */
    .main-header {{ 
        background: linear-gradient(90deg, #00FFFF, #58a6ff); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        text-align: center; font-size: 40px; font-weight: 900; padding: 10px; 
    }}

    /* CSS CHO BẢNG SIÊU TO VÀ ĐẸP */
    .big-table-container [data-testid="stDataFrame"] {{
        border: 2px solid #30363d;
        border-radius: 15px;
        overflow: hidden;
    }}
    
    /* Phóng to font chữ tiêu đề cột */
    .big-table-container [data-testid="stDataFrame"] th {{
        background-color: #1f2937 !important;
        color: #00FFFF !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        padding: 15px !important;
        text-transform: uppercase;
    }}

    /* Phóng to font chữ nội dung hàng */
    .big-table-container [data-testid="stDataFrame"] td {{
        font-size: 20px !important;
        font-weight: 700 !important;
        padding: 12px !important;
        color: #ffffff;
    }}

    /* Hiệu ứng Box cho Profile */
    .info-box {{ 
        background: #161b22; border: 1px solid #30363d; border-radius: 10px; 
        padding: 20px; text-align: center; margin-bottom: 10px;
    }}
    .info-label {{ color: #8b949e; font-size: 14px; font-weight: bold; }}
    .info-value {{ color: #ffffff; font-size: 24px; font-weight: bold; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA ENGINE ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=351056493'

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(URL)
        df.columns = [str(c).strip() for c in df.columns]
        
        # Nhận diện cột thông minh
        c_name = next((c for c in df.columns if 'Tên' in c or 'Name' in c), "Tên Người Dùng")
        c_pow = next((c for c in df.columns if 'Sức Mạnh' in c or 'Power' in c), "Sức Mạnh")
        c_kill = next((c for c in df.columns if 'Tiêu Diệt' in c or 'Kill' in c), "Tổng Điểm Tiêu Diệt")

        for col in [c_pow, c_kill]:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Tính toán KPI (Mẫu)
        df['SUM_DEAD'] = df[['T5 tử vong', 'T4 tử vong', 'T3 tử vong']].sum(axis=1)
        df['K_PCT'] = (df[c_kill] / 300_000_000 * 100).round(1)
        df['D_PCT'] = (df['SUM_DEAD'] / 400_000 * 100).round(1)
        
        df = df.sort_values(by='K_PCT', ascending=False).reset_index(drop=True)
        df.insert(0, 'H_RAW', range(1, len(df) + 1))
        return df, c_name, c_pow, c_kill
    except: return None

res = load_data()
if res:
    df, c_name, c_pow, c_kill = res
    st.markdown(f'<div class="main-header">{L["header"]}</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs([L["tab1"], L["tab2"]])
    
    with tab1:
        # Giữ nguyên phần Hồ sơ chi tiết nhưng với CSS mới đẹp hơn
        sel = st.selectbox(L["select_player"], df[c_name].unique())
        d = df[df[c_name] == sel].iloc[0]
        
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="info-box"><div class="info-label">{L["rank"]}</div><div class="info-value">#{int(d["H_RAW"])}</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="info-box"><div class="info-label">{L["power_now"]}</div><div class="info-value">{int(d[c_pow]):,}</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="info-box"><div class="info-label">{L["kpi_kill_pct"]}</div><div class="info-value" style="color:#00FFFF;">{d["K_PCT"]}%</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="info-box"><div class="info-label">{L["kpi_dead_pct"]}</div><div class="info-value" style="color:#f29b05;">{d["D_PCT"]}%</div></div>', unsafe_allow_html=True)

    with tab2:
        # PHẦN BẢNG TỔNG HỢP NÂNG CẤP
        st.markdown("<div class='big-table-container'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center; color: #58a6ff;'>{L['table_title']}</h2>", unsafe_allow_html=True)
        
        # Chọn các cột hiển thị quan trọng
        view_df = df[['H_RAW', c_name, c_pow, c_kill, 'K_PCT', 'SUM_DEAD', 'D_PCT']].copy()
        
        # Đổi tên cột có Icon
        view_df.columns = [
            L['col_rank'], L['col_name'], L['col_power'], 
            L['col_kill'], L['col_kpi_kill'], L['col_dead'], L['col_kpi_dead']
        ]
        
        # Định dạng hiển thị số có dấu phẩy cho dễ đọc
        formatted_df = view_df.style.format({
            L['col_power']: '{:,.0f}',
            L['col_kill']: '{:,.0f}',
            L['col_dead']: '{:,.0f}',
            L['col_kpi_kill']: '{:.1f}%',
            L['col_kpi_dead']: '{:.1f}%'
        })
        
        st.dataframe(formatted_df, use_container_width=True, height=800)
        st.markdown("</div>", unsafe_allow_html=True)
