import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="3956 KPI | COMMAND CENTER", layout="wide")

# --- 2. GIAO DIỆN (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0f15; color: #e0e6ed; }
    .main-header {
        color: #f29b05; text-align: center; font-size: 30px;
        font-weight: bold; padding: 10px; border-bottom: 2px solid #f29b05;
        margin-bottom: 20px; text-transform: uppercase;
    }
    .command-card {
        background: rgba(26, 32, 44, 0.8);
        border-radius: 15px; padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .mini-stat-label { color: #888; font-size: 11px; text-transform: uppercase; }
    .mini-stat-value { color: #fff; font-size: 15px; font-weight: bold; }
    .target-value { color: #f29b05; font-weight: bold; }
    /* Màu thanh tiến độ */
    .stProgress > div > div > div > div { background-color: #f29b05; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. QUẢN LÝ NGÔN NGỮ (GÓC PHẢI) ---
col_t, col_l = st.columns([4, 1]) # Chia tỉ lệ để đẩy nút ngôn ngữ sang phải

with col_l:
    lang = st.radio("LANGUAGE:", ["VN", "EN"], horizontal=True, label_visibility="collapsed")

# Nội dung dịch thuật
texts = {
    "VN": {
        "header": "🛡️ HỆ THỐNG QUẢN LÝ KPI",
        "search": "🔍 TRA CỨU CHIẾN BINH:",
        "select": "--- Chọn tên ---",
        "all": "LIÊN MINH", "pow": "SỨC MẠNH", "tk": "TỔNG KILL", "td": "TỔNG DEAD",
        "kt": "KILL CẦN ĐẠT", "dt": "DEAD CẦN ĐẠT",
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

# --- 4. XỬ LÝ DỮ LIỆU ---
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
        num_cols = ['Sức Mạnh_2', 'Tổng Tiêu Diệt_2', 'Điểm Chết_2', 'Tổng Tiêu Diệt_1', 'Điểm Chết_1']
        for c in num_cols:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).astype(float)
        df['KI'] = df['Tổng Tiêu Diệt_2'] - df['Tổng Tiêu Diệt_1']
        df['DI'] = df['Điểm Chết_2'] - df['Điểm Chết_1']
        def get_metrics(r):
            p = r['Sức Mạnh_2']
            if p >= 30e6: gk, gd = 30e6, 400e3
            elif p >= 20e6: gk, gd = 25e6, 300e3
            elif p >= 15e6: gk, gd = 20e6, 250e3
            else: gk, gd = 10e6, 200e3
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
        c1, c2 = st.columns([1.2, 1])
        with c1:
            st.markdown(f"""
                <div class="command-card">
                    <h2 style="color:#f29b05; margin:0;">👤 {sel}</h2>
                    <p style="color:#888; font-size:12px; margin-bottom:15px;">ID: {d['ID']}</p>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div><span class="mini-stat-label">{L['all']}</span><br><span class="mini-stat-value">{d['Liên Minh_2']}</span></div>
                        <div><span class="mini-stat-label">{L['pow']}</span><br><span class="mini-stat-value">{int(d['Sức Mạnh_2']):,}</span></div>
                        <div><span class="mini-stat-label">{L['tk']}</span><br><span class="mini-stat-value">{int(d['Tổng Tiêu Diệt_2']):,}</span></div>
                        <div><span class="mini-stat-label">{L['td']}</span><br><span class="mini-stat-value">{int(d['Điểm Chết_2']):,}</span></div>
                        <div style="border-top: 1px solid #444; padding-top:8px;"><span class="mini-stat-label">{L['kt']}</span><br><span class="target-value">{int(d['GK']):,}</span></div>
                        <div style="border-top: 1px solid #444; padding-top:8px;"><span class="mini-stat-label">{L['dt']}</span><br><span class="target-value">{int(d['GD']):,}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.write("")
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.caption(f"{L['ki']}: {int(d['KI']):,}")
                st.progress(max(0.0, min(float(d['KI']) / d['GK'], 1.0)) if d['GK'] > 0 else 0.0)
            with col_m2:
                st.caption(f"{L['di']}: {int(d['DI']):,}")
                st.progress(max(0.0, min(float(d['DI']) / d['GD'], 1.0)) if d['GD'] > 0 else 0.0)
        with c2:
            fig = go.Figure(go.Indicator(
                mode = "gauge+number", value = float(d['KPI']),
                number = {'suffix': "%", 'font': {'color': '#f29b05', 'size': 50}},
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#f29b05"}, 'bgcolor': "rgba(0,0,0,0)"}
            ))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=280, margin=dict(l=20,r=20,t=40,b=20))
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader(L["table"])
    v_df = df[['Tên_2', 'ID', 'Liên Minh_2', 'Sức Mạnh_2', 'Tổng Tiêu Diệt_2', 'KI', 'DI', 'KPI']].copy()
    v_df.columns = L["cols"]
    st.dataframe(v_df.style.format({L["cols"][3]: '{:,.0f}', L["cols"][4]: '{:,.0f}', L["cols"][5]: '{:,.0f}', L["cols"][6]: '{:,.0f}', L["cols"][7]: '{:.1f}%'}), use_container_width=True, height=500)
