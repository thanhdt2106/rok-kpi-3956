import streamlit as st
import pandas as pd

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="ROK KPI 3956 | ELITE UI", layout="wide", initial_sidebar_state="expanded")

# --- 2. GIAO DIỆN GLASSMORPHISM ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #e0e0e0; font-family: 'Roboto', sans-serif; }
    .cyber-title { font-family: 'Orbitron', sans-serif; color: #f29b05; text-align: center; text-transform: uppercase; letter-spacing: 5px; font-size: 40px !important; padding: 20px; border-bottom: 2px solid #f29b05; margin-bottom: 40px; text-shadow: 0 0 15px rgba(242, 155, 5, 0.5); }
    .glass-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 25px; margin-bottom: 25px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37); }
    .stat-label { color: #aaa; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; }
    .stat-value { color: #f29b05; font-size: 22px; font-weight: bold; font-family: 'Orbitron'; }
    /* Fix table background */
    [data-testid="stDataFrame"] { background: rgba(0, 0, 0, 0.2) !important; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DỮ LIỆU ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
URL_T = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=731741617'
URL_S = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=371969335'

def get_targets(power):
    if power < 15e6: return 10e6, 200e3
    if power < 20e6: return 20e6, 250e3
    if power < 30e6: return 25e6, 300e3
    return 30e6, 400e3

@st.cache_data(ttl=30)
def load():
    try:
        dt = pd.read_csv(URL_T).rename(columns=lambda x: x.strip())
        ds = pd.read_csv(URL_S).rename(columns=lambda x: x.strip())
        
        # Xử lý ID và Tên để tránh lỗi so sánh float/str
        for d in [dt, ds]:
            d['ID'] = d['ID'].astype(str).str.replace('.0', '', regex=False).str.strip()
            d['Tên'] = d['Tên'].fillna('Unknown').astype(str).str.strip()

        df = pd.merge(dt.drop_duplicates('ID'), ds.drop_duplicates('ID'), on='ID', suffixes=('_1', '_2'))
        
        # Ép kiểu số cho các cột tính toán
        num_cols = ['Sức Mạnh_2', 'Tổng Tiêu Diệt_2', 'Điểm Chết_2', 'Tổng Tiêu Diệt_1', 'Điểm Chết_1']
        for c in num_cols:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            
        df['K+'] = df['Tổng Tiêu Diệt_2'] - df['Tổng Tiêu Diệt_1']
        df['D+'] = df['Điểm Chết_2'] - df['Điểm Chết_1']
        
        def kpi_calc(r):
            gk, gd = get_targets(r['Sức Mạnh_2'])
            pk = max(0, min(r['K+']/gk, 1.0)) if gk > 0 else 0
            pd_v = max(0, min(r['D+']/gd, 1.0)) if gd > 0 else 0
            return round(((pk + pd_v) / 2) * 100, 1)
        
        df['KPI'] = df.apply(kpi_calc, axis=1)
        return df
    except Exception as e:
        st.error(f"Lỗi tải dữ liệu: {e}")
        return None

df = load()

# --- 4. HIỂN THỊ ---
if df is not None:
    st.markdown('<h1 class="cyber-title">ROK KPI 3956</h1>', unsafe_allow_html=True)

    # Khắc phục lỗi sắp xếp: Chuyển hết về string và lọc bỏ giá trị rác
    names = sorted([str(name) for name in df['Tên_2'].unique() if name != 'Unknown'])
    sel = st.selectbox("🔍 TRA CỨU CHIẾN BINH:", ["--- Chọn tên người chơi ---"] + names)
    
    if sel != "--- Chọn tên người chơi ---":
        d = df[df['Tên_2'] == sel].iloc[0]
        gk, gd = get_targets(d['Sức Mạnh_2'])
        
        # --- PHẦN CHI TIẾT NÂNG CẤP THEO YÊU CẦU ---
        st.markdown(f"""
            <div class="glass-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h2 style="color:#f29b05; margin:0;">👤 {sel}</h2>
                    <div style="text-align:right;">
                        <span class="stat-label">TIẾN ĐỘ KPI</span><br>
                        <span style="font-size:40px; color:#f29b05; font-family:'Orbitron';">{d['KPI']}%</span>
                    </div>
                </div>
                <p style="opacity:0.6; margin-top:-5px;">ID: {d['ID']}</p>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px;">
                    <div style="background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px;">
                        <span class="stat-label">🚩 LIÊN MINH</span><br>
                        <span class="stat-value" style="font-size:18px;">{d['Liên Minh_2']}</span>
                    </div>
                    <div style="background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px;">
                        <span class="stat-label">🛡️ SỨC MẠNH</span><br>
                        <span class="stat-value">{int(d['Sức Mạnh_2']):,}</span>
                    </div>
                    <div style="background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px;">
                        <span class="stat-label">⚔️ TỔNG TIÊU DIỆT</span><br>
                        <span class="stat-value">{int(d['Tổng Tiêu Diệt_2']):,}</span>
                    </div>
                    <div style="background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px;">
                        <span class="stat-label">💀 TỔNG ĐIỂM CHẾT</span><br>
                        <span class="stat-value">{int(d['Điểm Chết_2']):,}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        c1.metric("Tiêu diệt tăng (K+)", f"{int(d['K+']):,}", f"Mục tiêu: {int(gk/1e6)}M")
        c2.metric("Điểm chết tăng (D+)", f"{int(d['D+']):,}", f"Mục tiêu: {int(gd/1e3)}K")

    st.divider()
    
    # Bảng tổng hợp
    st.subheader("📋 BẢNG THỐNG KÊ CHI TIẾT")
    v_df = df[['Tên_2', 'Liên Minh_2', 'Sức Mạnh_2', 'K+', 'D+', 'KPI']].copy()
    v_df.columns = ['Tên', 'Liên minh', 'Sức mạnh', 'Kill tăng', 'Dead tăng', '% KPI']
    st.dataframe(v_df.style.background_gradient(subset=['% KPI'], cmap='YlOrBr'), use_container_width=True)
