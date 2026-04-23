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
        color: #f29b05; text-align: center; font-size: 35px;
        font-weight: bold; padding: 15px; border-bottom: 2px solid #f29b05;
        margin-bottom: 30px; text-transform: uppercase;
    }
    .command-card {
        background: rgba(26, 32, 44, 0.6);
        border-radius: 15px; padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 25px;
    }
    .mini-stat-label { color: #888; font-size: 12px; text-transform: uppercase; }
    .mini-stat-value { color: #fff; font-size: 18px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. QUẢN LÝ NGÔN NGỮ ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'Tiếng Việt'

def toggle_lang():
    st.session_state.lang = st.session_state.lang_select

with st.sidebar:
    st.markdown("<h2 style='color:#f29b05;'>⚙️ SETTINGS</h2>", unsafe_allow_html=True)
    st.selectbox("LANGUAGE / NGÔN NGỮ:", ['Tiếng Việt', 'English'], 
                 key='lang_select', on_change=toggle_lang)
    st.divider()
    st.info("Kingdom 3956 | Alliance FTD")

# Nội dung dịch
texts = {
    'Tiếng Việt': {
        'title': "🛡️ HỆ THỐNG QUẢN LÝ KPI",
        'search': "🔍 TRA CỨU CHIẾN BINH:",
        'select': "--- Chọn tên ---",
        'alliance': "LIÊN MINH",
        'power': "SỨC MẠNH",
        'tkill': "TỔNG KILL",
        'tdead': "TỔNG DEAD",
        'k_inc': "Kill KvK Tăng",
        'd_inc': "Dead KvK Tăng",
        'table_title': "📋 BẢNG THỐNG KÊ TỔNG HỢP",
        'cols': ['Tên Chiến Binh', 'ID', 'Liên Minh', 'Sức Mạnh', 'Tổng Kill', 'Kill Tăng', 'Dead Tăng', '% KPI']
    },
    'English': {
        'title': "🛡️ KPI MANAGEMENT SYSTEM",
        'search': "🔍 WARRIOR LOOKUP:",
        'select': "--- Select Name ---",
        'alliance': "ALLIANCE",
        'power': "POWER",
        'tkill': "TOTAL KILLS",
        'tdead': "TOTAL DEADS",
        'k_inc': "Kills Increased",
        'd_inc': "Deads Increased",
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
        
        def calc(r):
            p = r['Sức Mạnh_2']
            gk, gd = (30e6, 400e3) if p >= 30e6 else (25e6, 300e3) if p >= 20e6 else (20e6, 250e3) if p >= 15e6 else (10e6, 200e3)
            pk = max(0, min(r['KI']/gk, 1.0)) if gk > 0 else 0
            pdv = max(0, min(r['DI']/gd, 1.0)) if gd > 0 else 0
            return round(((pk + pdv) / 2) * 100, 1)
        df['KPI'] = df.apply(calc, axis=1)
        return df
    except: return None

df = load_data()

# --- 5. HÀM VẼ BIỂU ĐỒ ---
def draw_gauge(score, name):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = score,
        title = {'text': f"KPI: {name}", 'font': {'color': '#fff', 'size': 20}},
        number = {'suffix': "%", 'font': {'color': '#f29b05'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickcolor': "#888"},
            'bar': {'color': "#f29b05"},
            'bgcolor': "rgba(0,0,0,0)",
            'steps': [{'range': [0, 100], 'color': "rgba(255,255,255,0.05)"}],
            'threshold': {'line': {'color': "white", 'width': 4}, 'value': 100}
        }
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=300, margin=dict(l=20,r=20,t=50,b=20))
    return fig

# --- 6. HIỂN THỊ ---
if df is not None:
    st.markdown(f'<div class="main-header">{L["title"]}</div>', unsafe_allow_html=True)

    names = sorted([str(n) for n in df['Tên_2'].unique() if n != 'Unknown'])
    sel = st.selectbox(L['search'], [L['select']] + names)
    
    if sel != L['select']:
        d = df[df['Tên_2'] == sel].iloc[0]
        col1, col2 = st.columns([1, 1.2])
        with col1:
            st.markdown(f"""
                <div class="command-card">
                    <h2 style="color:#f29b05; margin:0;">👤 {sel}</h2>
                    <p style="color:#888; margin-bottom:20px;">ID: {d['ID']}</p>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div><span class="mini-stat-label">{L['alliance']}</span><br><span class="mini-stat-value">{d['Liên Minh_2']}</span></div>
                        <div><span class="mini-stat-label">{L['power']}</span><br><span class="mini-stat-value">{int(d['Sức Mạnh_2']):,}</span></div>
                        <div><span class="mini-stat-label">{L['tkill']}</span><br><span class="mini-stat-value">{int(d['Tổng Tiêu Diệt_2']):,}</span></div>
                        <div><span class="mini-stat-label">{L['tdead']}</span><br><span class="mini-stat-value">{int(d['Điểm Chết_2']):,}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.metric(L['k_inc'], f"{int(d['KI']):,}")
            st.metric(L['d_inc'], f"{int(d['DI']):,}")
        with col2:
            st.plotly_chart(draw_gauge(d['KPI'], sel), use_container_width=True)

    st.divider()
    st.subheader(L['table_title'])
    v_df = df[['Tên_2', 'ID', 'Liên Minh_2', 'Sức Mạnh_2', 'Tổng Tiêu Diệt_2', 'KI', 'DI', 'KPI']].copy()
    v_df.columns = L['cols']
    st.dataframe(v_df.style.format({L['cols'][3]: '{:,.0f}', L['cols'][4]: '{:,.0f}', 
                                   L['cols'][5]: '{:,.0f}', L['cols'][6]: '{:,.0f}', 
                                   L['cols'][7]: '{:.1f}%'}), use_container_width=True, height=500)
