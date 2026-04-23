import streamlit as st
import pandas as pd

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="ROK KPI 3956 | ELITE UI", layout="wide", initial_sidebar_state="expanded")

# --- GIAO DIỆN GLASSMORPHISM ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #e0e0e0; font-family: 'Roboto', sans-serif; }
    .cyber-title { font-family: 'Orbitron', sans-serif; color: #f29b05; text-align: center; text-transform: uppercase; letter-spacing: 5px; font-size: 50px !important; padding: 20px; border-bottom: 2px solid #f29b05; margin-bottom: 40px; text-shadow: 0 0 15px rgba(242, 155, 5, 0.5); }
    .glass-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 25px; margin-bottom: 25px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37); }
    .stat-label { color: #888; font-size: 14px; text-transform: uppercase; }
    .stat-value { color: #f29b05; font-size: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- XỬ LÝ NGÔN NGỮ ---
if 'lang' not in st.session_state: st.session_state.lang = 'Tiếng Việt'
texts = {
    'Tiếng Việt': {
        'lookup': "🔍 TRA CỨU CHIẾN BINH:", 'alliance': "Liên minh", 'total_kill': "Tổng tiêu diệt hiện tại",
        'power': "Sức mạnh", 'progress': "Tiến độ KPI", 'incr_kill': "Tiêu diệt tăng", 'incr_dead': "Điểm chết tăng"
    },
    'English': {
        'lookup': "🔍 WARRIOR LOOKUP:", 'alliance': "Alliance", 'total_kill': "Total Kill Points",
        'power': "Power", 'progress': "KPI Progress", 'incr_kill': "Kills Increased", 'incr_dead': "Deads Increased"
    }
}
L = texts[st.session_state.lang]

# --- KẾT NỐI DỮ LIỆU ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
URL_T = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=731741617'
URL_S = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=371969335'

@st.cache_data(ttl=30)
def load():
    dt = pd.read_csv(URL_T).rename(columns=lambda x: x.strip())
    ds = pd.read_csv(URL_S).rename(columns=lambda x: x.strip())
    dt['ID'] = dt['ID'].astype(str).str.replace('.0', '', regex=False)
    ds['ID'] = ds['ID'].astype(str).str.replace('.0', '', regex=False)
    df = pd.merge(dt.drop_duplicates('ID'), ds.drop_duplicates('ID'), on='ID', suffixes=('_1', '_2'))
    for c in ['Sức Mạnh_2', 'Tổng Tiêu Diệt_2', 'Điểm Chết_2', 'Tổng Tiêu Diệt_1', 'Điểm Chết_1']:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    df['K+'] = df['Tổng Tiêu Diệt_2'] - df['Tổng Tiêu Diệt_1']
    df['D+'] = df['Điểm Chết_2'] - df['Điểm Chết_1']
    
    def get_targets(power):
        if power < 15e6: return 10e6, 200e3
        if power < 20e6: return 20e6, 250e3
        if power < 30e6: return 25e6, 300e3
        return 30e6, 400e3

    def kpi_calc(r):
        gk, gd = get_targets(r['Sức Mạnh_2'])
        return round(((max(0,min(r['K+']/gk,1)) + max(0,min(r['D+']/gd,1)))/2)*100, 1)
    
    df['KPI'] = df.apply(kpi_calc, axis=1)
    return df

df = load()

# --- HIỂN THỊ ---
if df is not None:
    st.markdown('<h1 class="cyber-title">ROK KPI 3956</h1>', unsafe_allow_html=True)

    names = sorted(df['Tên_2'].unique())
    sel = st.selectbox(L['lookup'], ["---"] + names)
    
    if sel != "---":
        d = df[df['Tên_2'] == sel].iloc[0]
        
        # --- PHẦN HIỂN THỊ CHI TIẾT NÂNG CẤP ---
        st.markdown(f"""
            <div class="glass-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h2 style="color:#f29b05; margin:0;">👤 {sel}</h2>
                    <div style="text-align:right;">
                        <span class="stat-label">{L['progress']}</span><br>
                        <span style="font-size:40px; color:#f29b05; font-family:'Orbitron';">{d['KPI']}%</span>
                    </div>
                </div>
                <p style="opacity:0.6; margin-top:-10px;">ID: {d['ID']}</p>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.1);">
                    <div>
                        <span class="stat-label">🚩 {L['alliance']}</span><br>
                        <span class="stat-value">{d['Liên Minh_2']}</span>
                    </div>
                    <div>
                        <span class="stat-label">🛡️ {L['power']}</span><br>
                        <span class="stat-value">{int(d['Sức Mạnh_2']):,}</span>
                    </div>
                    <div>
                        <span class="stat-label">⚔️ {L['total_kill']}</span><br>
                        <span class="stat-value">{int(d['Tổng Tiêu Diệt_2']):,}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        c1.metric(L['incr_kill'], f"{int(d['K+']):,}")
        c2.metric(L['incr_dead'], f"{int(d['D+']):,}")
    
    # (Phần Tabs và Table giữ nguyên như bản trước...)
    st.divider()
    st.dataframe(df[['Tên_2', 'Liên Minh_2', 'Sức Mạnh_2', 'KPI']].style.background_gradient(cmap='YlOrBr'), use_container_width=True)
