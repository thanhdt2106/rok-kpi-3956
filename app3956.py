import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI | COMMAND CENTER", layout="wide")

# --- 2. GIAO DIỆN (CSS CUSTOM) ---
st.markdown("""
    <style>
    /* Nền chính màu vàng nhẹ */
    .stApp {
        background-color: #fdf6e3; 
        color: #333;
    }
    
    /* Tiêu đề chính */
    .main-header {
        color: #b58900; text-align: center; font-size: 32px;
        font-weight: bold; padding: 15px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Khung Profile chi tiết - Hiệu ứng phát sáng và bo góc */
    .command-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 25px rgba(181, 137, 0, 0.2), 0 0 10px rgba(181, 137, 0, 0.1);
        border: 2px solid rgba(181, 137, 0, 0.3);
        margin-bottom: 20px;
        transition: 0.3s;
    }
    
    .mini-stat-label { color: #657b83; font-size: 11px; text-transform: uppercase; font-weight: bold; }
    .mini-stat-value { color: #073642; font-size: 17px; font-weight: 900; }
    .target-value { color: #d33682; font-weight: bold; font-size: 18px; }

    /* Bảng tổng hợp - Màu xanh, hiệu ứng nổi 3D */
    [data-testid="stDataFrame"] {
        background-color: #e1e8ed;
        border: 1px solid #002b36;
        border-radius: 15px;
        box-shadow: inset 5px 5px 10px #b8c1c8, inset -5px -5px 10px #ffffff;
        padding: 10px;
    }

    /* Tùy chỉnh thanh tiến độ */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #268bd2, #2aa198);
    }
    
    /* Radio button ngôn ngữ */
    div[data-testid="stRadio"] > label {
        font-weight: bold; color: #b58900;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. QUẢN LÝ NGÔN NGỮ ---
col_t, col_l = st.columns([4, 1]) 
with col_l:
    lang = st.radio("LANG:", ["VN", "EN"], horizontal=True, label_visibility="collapsed")

texts = {
    "VN": {
        "header": "🛡️ HỆ THỐNG QUẢN LÝ KPI",
        "search": "🔍 TRA CỨU CHIẾN BINH:",
        "select": "--- Chọn tên ---",
        "all": "LIÊN MINH", "pow": "SỨC MẠNH", "tk": "TỔNG KILL", "td": "TỔNG DEAD",
        "kt": "MỤC TIÊU KILL", "dt": "MỤC TIÊU DEAD",
        "ki": "Kill tăng", "di": "Dead tăng",
        "table": "📋 BẢNG THỐNG KÊ TỔNG HỢP",
        "cols": ['Tên', 'ID', 'Liên minh', 'Sức mạnh', 'Tổng Kill', 'Kill tăng (+)', 'Dead tăng (+)', 'KPI (%)']
    },
    "EN": {
        "header": "🛡️ KPI MANAGEMENT SYSTEM",
        "search": "🔍 WARRIOR LOOKUP:",
        "select": "--- Select name ---",
        "all": "ALLIANCE", "pow": "POWER", "tk": "TOTAL KILL", "td": "TOTAL DEAD",
        "kt": "TARGET KILL", "dt": "TARGET DEAD",
        "ki": "Kill inc", "di": "Dead inc",
        "table": "📋 SUMMARY STATISTICS TABLE",
        "cols": ['Name', 'ID', 'Alliance', 'Power', 'Total Kill', 'Kill Inc (+)', 'Dead Inc (+)', 'KPI (%)']
    }
}
L = texts[lang]

# --- 4. XỬ LÝ DỮ LIỆU (Giữ nguyên logic Power mới của bạn) ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
URL_T = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=731741617'
URL_S = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=371969335'

@st.cache_data(ttl=30)
def load_data():
    try:
        dt = pd.read_csv(URL_T).rename(columns=lambda x: x.strip())
        ds = pd.read_csv(URL_S).rename(columns=lambda x: x.strip())
        for d in [dt, ds]:
            d['ID'] = d['ID'].astype(str).str.replace('.0', '', regex=False).str.strip()
            d['Tên'] = d['Tên'].fillna('Unknown').astype(str).str.strip()
        df = pd.merge(dt.drop_duplicates('ID'), ds.drop_duplicates('ID'), on='ID', suffixes=('_1', '_2'))
        for c in ['Sức Mạnh_2', 'Tổng Tiêu Diệt_2', 'Điểm Chết_2', 'Tổng Tiêu Diệt_1', 'Điểm Chết_1']:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).astype(float)
        df['KI'] = df['Tổng Tiêu Diệt_2'] - df['Tổng Tiêu Diệt_1']
        df['DI'] = df['Điểm Chết_2'] - df['Điểm Chết_1']
        
        def get_metrics(r):
            p = r['Sức Mạnh_2']
            if p < 15e6: gk = 80e6
            elif p < 20e6: gk = 100e6
            elif p < 25e6: gk = 130e6
            elif p < 30e6: gk = 170e6
            elif p < 35e6: gk = 200e6
            elif p < 40e6: gk = 220e6
            elif p < 45e6: gk = 250e6
            else: gk = 300e6
            gd = 400e3 if p >= 30e6 else 300e3 if p >= 20e6 else 200e3
            pk = max(0.0, min(float(r['KI']) / gk, 1.0)) if gk > 0 else 0.0
            pdv = max(0.0, min(float(r['DI']) / gd, 1.0)) if gd > 0 else 0.0
            return pd.Series([round(((pk + pdv) / 2) * 100, 1), gk, gd])
        
        df[['KPI', 'GK', 'GD']] = df.apply(get_metrics, axis=1)
        return df
    except: return None

df = load_data()

# --- 5. HIỂN THỊ ---
if df is not None:
    st.markdown(f'<div class="main-header">{L["header"]}</div>', unsafe_allow_html=True)
    names = sorted(df['Tên_2'].unique())
    sel = st.selectbox(L["search"], [L["select"]] + names)
    
    if sel != L["select"]:
        d = df[df['Tên_2'] == sel].iloc[0]
        c1, c2 = st.columns([1.3, 1])
        with c1:
            st.markdown(f"""
                <div class="command-card">
                    <h2 style="color:#b58900; margin:0; font-size:28px;">👤 {sel}</h2>
                    <p style="color:#888; font-size:13px; margin-bottom:20px;">ID: {d['ID']}</p>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div><span class="mini-stat-label">{L['all']}</span><br><span class="mini-stat-value">{d['Liên Minh_2']}</span></div>
                        <div><span class="mini-stat-label">{L['pow']}</span><br><span class="mini-stat-value">{int(d['Sức Mạnh_2']):,}</span></div>
                        <div><span class="mini-stat-label">{L['tk']}</span><br><span class="mini-stat-value">{int(d['Tổng Tiêu Diệt_2']):,}</span></div>
                        <div><span class="mini-stat-label">{L['td']}</span><br><span class="mini-stat-value">{int(d['Điểm Chết_2']):,}</span></div>
                        <div style="border-top: 2px solid #eee; padding-top:10px;"><span class="mini-stat-label">{L['kt']}</span><br><span class="target-value">{int(d['GK']):,}</span></div>
                        <div style="border-top: 2px solid #eee; padding-top:10px;"><span class="mini-stat-label">{L['dt']}</span><br><span class="target-value">{int(d['GD']):,}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            cm1, cm2 = st.columns(2)
            with cm1:
                st.caption(f"{L['ki']}: {int(d['KI']):,}")
                st.progress(max(0.0, min(float(d['KI']) / d['GK'], 1.0)) if d['GK'] > 0 else 0.0)
            with cm2:
                st.caption(f"{L['di']}: {int(d['DI']):,}")
                st.progress(max(0.0, min(float(d['DI']) / d['GD'], 1.0)) if d['GD'] > 0 else 0.0)
        with c2:
            fig = go.Figure(go.Indicator(
                mode = "gauge+number", value = float(d['KPI']),
                number = {'suffix': "%", 'font': {'color': '#b58900', 'size': 50}},
                gauge = {
                    'axis': {'range': [0, 100], 'tickcolor': "#b58900"},
                    'bar': {'color': "#268bd2"},
                    'bgcolor': "white",
                    'borderwidth': 2, 'bordercolor': "#eee"
                }
            ))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=300)
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader(L["table"])
    v_df = df[['Tên_2', 'ID', 'Liên Minh_2', 'Sức Mạnh_2', 'Tổng Tiêu Diệt_2', 'KI', 'DI', 'KPI']].copy()
    v_df.columns = L["cols"]
    
    # Hiển thị bảng với style màu xanh nổi
    st.dataframe(v_df.style.format({
        L["cols"][3]: '{:,.0f}', L["cols"][4]: '{:,.0f}', 
        L["cols"][5]: '{:,.0f}', L["cols"][6]: '{:,.0f}', L["cols"][7]: '{:.1f}%'
    }), use_container_width=True, height=500)
