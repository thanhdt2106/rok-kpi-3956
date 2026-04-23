import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI | COMMAND CENTER", layout="wide")

# --- 2. GIAO DIỆN (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0f15; color: #e0e6ed; }
    .main-header {
        color: #f29b05; text-align: center; font-size: 30px;
        font-weight: bold; padding: 15px; border-bottom: 2px solid #f29b05;
        margin-bottom: 30px; text-transform: uppercase;
    }
    .command-card {
        background: rgba(26, 32, 44, 0.8);
        border-radius: 15px; padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .mini-stat-label { color: #888; font-size: 11px; text-transform: uppercase; }
    .mini-stat-value { color: #fff; font-size: 16px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HỆ THỐNG NGÔN NGỮ ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'Tiếng Việt'

with st.sidebar:
    st.markdown("<h3 style='color:#f29b05;'>LANGUAGE / NGÔN NGỮ</h3>", unsafe_allow_html=True)
    lang_choice = st.selectbox("Select Language", ['Tiếng Việt', 'English'], label_visibility="collapsed")
    st.session_state.lang = lang_choice

texts = {
    'Tiếng Việt': {
        'title': "🛡️ HỆ THỐNG QUẢN LÝ KPI",
        'search': "🔍 TRA CỨU CHIẾN BINH:",
        'select': "--- Chọn tên ---",
        'alliance': "LIÊN MINH", 'power': "SỨC MẠNH", 'tkill': "TỔNG KILL", 'tdead': "TỔNG DEAD",
        'k_inc': "Kill KvK Tăng", 'd_inc': "Dead KvK Tăng",
        'table_title': "📋 BẢNG THỐNG KÊ TỔNG HỢP",
        'cols': ['Tên Chiến Binh', 'ID', 'Liên Minh', 'Sức Mạnh', 'Tổng Kill', 'Kill Tăng', 'Dead Tăng', '% KPI']
    },
    'English': {
        'title': "🛡️ KPI MANAGEMENT SYSTEM",
        'search': "🔍 WARRIOR LOOKUP:",
        'select': "--- Select Name ---",
        'alliance': "ALLIANCE", 'power': "POWER", 'tkill': "TOTAL KILLS", 'tdead': "TOTAL DEADS",
        'k_inc': "Kills Increased", 'd_inc': "Deads Increased",
        'table_title': "📋 SUMMARY STATISTICS TABLE",
        'cols': ['Warrior Name', 'ID', 'Alliance', 'Power', 'Total Kills', 'Kills (+)', 'Deads (+)', 'KPI %']
    }
}
L = texts[st.session_state.lang]

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
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        df['KI'] = df['Tổng Tiêu Diệt_2'] - df['Tổng Tiêu Diệt_1']
        df['DI'] = df['Điểm Chết_2'] - df['Điểm Chết_1']
        
        def calc_kpi(r):
            p = r['Sức Mạnh_2']
            if p >= 30e6: gk, gd = 30e6, 400e3
            elif p >= 20e6: gk, gd = 25e6, 300e3
            elif p >= 15e6: gk, gd = 20e6, 250e3
            else: gk, gd = 10e6, 200e3
            pk = max(0, min(r['KI']/gk, 1.0)) if gk > 0 else 0
            pdv = max(0, min(r['DI']/gd, 1.0)) if gd > 0 else 0
            return round(((pk + pdv) / 2) * 100, 1)
        df['KPI'] = df.apply(calc_kpi, axis=1)
        return df
    except: return None

df = load_data()

# --- 5. HIỂN THỊ ---
if df is not None:
    st.markdown(f'<div class="main-header">{L["title"]}</div>', unsafe_allow_html=True)

    names = sorted([str(n) for n in df['Tên_2'].unique() if n != 'Unknown'])
    sel = st.selectbox(L['search'], [L['select']] + names)
    
    if sel != L['select']:
        d = df[df['Tên_2'] == sel].iloc[0]
        c1, c2 = st.columns([1, 1.2])
        with c1:
            st.markdown(f"""
                <div class="command-card">
                    <h2 style="color:#f29b05; margin:0;">👤 {sel}</h2>
                    <p style="color:#888; font-size:13px;">ID: {d['ID']}</p>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                        <div><span class="mini-stat-label">{L['alliance']}</span><br><span class="mini-stat-value">{d['Liên Minh_2']}</span></div>
                        <div><span class="mini-stat-label">{L['power']}</span><br><span class="mini-stat-value">{int(d['Sức Mạnh_2']):,}</span></div>
                        <div><span class="mini-stat-label">{L['tkill']}</span><br><span class="mini-stat-value">{int(d['Tổng Tiêu Diệt_2']):,}</span></div>
                        <div><span class="mini-stat-label">{L['tdead']}</span><br><span class="mini-stat-value">{int(d['Điểm Chết_2']):,}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            col_m1, col_m2 = st.columns(2)
            col_m1.metric(L['k_inc'], f"{int(d['KI']):,}")
            col_m2.metric(L['d_inc'], f"{int(d['DI']):,}")
        with c2:
            fig = go.Figure(go.Indicator(
                mode = "gauge+number", value = d['KPI'],
                number = {'suffix': "%", 'font': {'color': '#f29b05'}},
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#f29b05"}, 'bgcolor': "rgba(0,0,0,0)"}
            ))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=280, margin=dict(l=20,r=20,t=20,b=20))
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader(L['table_title'])
    v_df = df[['Tên_2', 'ID', 'Liên Minh_2', 'Sức Mạnh_2', 'Tổng Tiêu Diệt_2', 'KI', 'DI', 'KPI']].copy()
    v_df.columns = L['cols']
    # Định dạng bảng an toàn, không dùng style.background_gradient để tránh lỗi thư viện
    st.dataframe(v_df.style.format({
        L['cols'][3]: '{:,.0f}', L['cols'][4]: '{:,.0f}', 
        L['cols'][5]: '{:,.0f}', L['cols'][6]: '{:,.0f}', L['cols'][7]: '{:.1f}%'
    }), use_container_width=True, height=500)
