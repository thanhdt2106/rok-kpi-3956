import streamlit as st
import pandas as pd

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="ROK KPI 3956 | ELITE UI", layout="wide")

# --- 2. GIAO DIỆN CSS (Xử lý lỗi hiển thị) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #e0e0e0; }
    .cyber-title { color: #f29b05; text-align: center; font-size: 40px; font-weight: bold; padding: 20px; border-bottom: 2px solid #f29b05; }
    .glass-card { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 20px; }
    .stat-label { color: #aaa; font-size: 13px; }
    .stat-value { color: #f29b05; font-size: 22px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. KẾT NỐI & XỬ LÝ DỮ LIỆU (Chống lỗi rác) ---
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
        
        # FIX LỖI 1: Ép tất cả ID và Tên về kiểu Chữ (String), bỏ giá trị trống
        for d in [dt, ds]:
            d['ID'] = d['ID'].astype(str).str.replace('.0', '', regex=False).str.strip()
            d['Tên'] = d['Tên'].fillna('Unknown').astype(str).str.strip()

        # FIX LỖI 3: Sửa cú pháp merge (chỉ dùng suffixes một lần)
        df = pd.merge(dt.drop_duplicates('ID'), ds.drop_duplicates('ID'), on='ID', suffixes=('_1', '_2'))
        
        # FIX LỖI 2: Ép tất cả cột tính toán về kiểu Số (Numeric)
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
        st.error(f"Lỗi hệ thống: {e}")
        return None

df = load()

# --- 4. HIỂN THỊ ---
if df is not None:
    st.markdown('<div class="cyber-title">ROK KPI 3956</div>', unsafe_allow_html=True)

    # FIX LỖI 1: Chuyển tên về list string để sorted() không bị lỗi chữ-số
    names = sorted([str(name) for name in df['Tên_2'].unique() if name != 'Unknown'])
    sel = st.selectbox("🔍 TRA CỨU CHIẾN BINH:", ["--- Chọn tên ---"] + names)
    
    if sel != "--- Chọn tên ---":
        d = df[df['Tên_2'] == sel].iloc[0]
        gk, gd = get_targets(d['Sức Mạnh_2'])
        
        st.markdown(f"""
            <div class="glass-card">
                <div style="display: flex; justify-content: space-between;">
                    <h2 style="color:#f29b05;">👤 {sel}</h2>
                    <h2 style="color:#f29b05;">{d['KPI']}%</h2>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div><span class="stat-label">🚩 LIÊN MINH</span><br><span class="stat-value">{d['Liên Minh_2']}</span></div>
                    <div><span class="stat-label">🛡️ SỨC MẠNH</span><br><span class="stat-value">{int(d['Sức Mạnh_2']):,}</span></div>
                    <div><span class="stat-label">⚔️ TỔNG TIÊU DIỆT</span><br><span class="stat-value">{int(d['Tổng Tiêu Diệt_2']):,}</span></div>
                    <div><span class="stat-label">💀 TỔNG ĐIỂM CHẾT</span><br><span class="stat-value">{int(d['Điểm Chết_2']):,}</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        c1.metric("Tiêu diệt tăng", f"{int(d['K+']):,}")
        c2.metric("Điểm chết tăng", f"{int(d['D+']):,}")

    st.divider()
    
    # FIX LỖI 4: Chỉ dùng gradient nếu máy chủ hỗ trợ, nếu không hiện bảng thường
    st.subheader("📋 DANH SÁCH KPI")
    view_df = df[['Tên_2', 'Liên Minh_2', 'Sức Mạnh_2', 'K+', 'D+', 'KPI']].copy()
    view_df.columns = ['Tên', 'Liên minh', 'Sức mạnh', 'Kill tăng', 'Dead tăng', '% KPI']
    
    try:
        st.dataframe(view_df.style.background_gradient(subset=['% KPI'], cmap='YlOrBr'), use_container_width=True)
    except:
        st.dataframe(view_df, use_container_width=True)
