import streamlit as st
import pandas as pd

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="ROK KPI 3956 | COMMANDER", layout="wide")

# --- 2. GIAO DIỆN (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b1016; color: #f0f2f6; }
    .profile-card {
        background: #1a202c;
        border-radius: 15px;
        padding: 25px;
        border-left: 5px solid #f29b05;
        margin-bottom: 25px;
    }
    .main-header { color: #f29b05; text-align: center; font-size: 35px; font-weight: bold; padding: 10px; }
    [data-testid="stDataFrame"] { background-color: #1a202c; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. XỬ LÝ DỮ LIỆU ---
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
            d['Tên'] = d['Tên'].fillna('Unknown').astype(str)

        df = pd.merge(dt.drop_duplicates('ID'), ds.drop_duplicates('ID'), on='ID', suffixes=('_1', '_2'))
        
        cols = ['Sức Mạnh_2', 'Tổng Tiêu Diệt_2', 'Điểm Chết_2', 'Tổng Tiêu Diệt_1', 'Điểm Chết_1']
        for c in cols:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            
        df['K+'] = df['Tổng Tiêu Diệt_2'] - df['Tổng Tiêu Diệt_1']
        df['D+'] = df['Điểm Chết_2'] - df['Điểm Chết_1']
        
        def calc_kpi(r):
            p = r['Sức Mạnh_2']
            gk, gd = (30e6, 400e3) if p >= 30e6 else (25e6, 300e3) if p >= 20e6 else (20e6, 250e3) if p >= 15e6 else (10e6, 200e3)
            return round(((max(0,min(r['K+']/gk,1)) + max(0,min(r['D+']/gd,1)))/2)*100, 1)
        
        df['KPI %'] = df.apply(calc_kpi, axis=1)
        return df
    except: return None

df = load_data()

# --- 4. HIỂN THỊ ---
if df is not None:
    st.markdown('<div class="main-header">🛡️ ROK KPI MANAGER 3956</div>', unsafe_allow_html=True)

    # Xem chi tiết
    names = sorted([str(n) for n in df['Tên_2'].unique() if n != 'Unknown'])
    sel = st.selectbox("🔍 Tìm kiếm thành viên:", ["--- Chọn tên ---"] + names)
    
    if sel != "--- Chọn tên ---":
        d = df[df['Tên_2'] == sel].iloc[0]
        st.markdown(f"""
            <div class="profile-card">
                <h2 style="margin:0; color:#f29b05;">👤 {sel}</h2>
                <p style="color:#888;">ID: {d['ID']} | Liên minh: {d['Liên Minh_2']}</p>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top:15px;">
                    <div><small>SỨC MẠNH</small><br><b>{int(d['Sức Mạnh_2']):,}</b></div>
                    <div><small>TỔNG KILL</small><br><b>{int(d['Tổng Tiêu Diệt_2']):,}</b></div>
                    <div><small>TIẾN ĐỘ KPI</small><br><b style="color:#f29b05; font-size:20px;">{d['KPI %']}%</b></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Bảng tổng hợp (Khôi phục đầy đủ các cột)
    st.subheader("📋 BẢNG THỐNG KÊ TỔNG HỢP")
    
    main_df = df[['Tên_2', 'ID', 'Liên Minh_2', 'Sức Mạnh_2', 'Tổng Tiêu Diệt_2', 'K+', 'D+', 'KPI %']].copy()
    main_df.columns = ['Tên', 'ID', 'Liên minh', 'Sức mạnh', 'Tổng Kill', 'Kill tăng', 'Dead tăng', 'KPI %']
    
    # Hiển thị bảng dạng chuẩn để tránh lỗi render màu
    st.dataframe(
        main_df.style.format({
            'Sức mạnh': '{:,.0f}',
            'Tổng Kill': '{:,.0f}',
            'Kill tăng': '{:,.0f}',
            'Dead tăng': '{:,.0f}',
            'KPI %': '{:.1f}%'
        }),
        use_container_width=True,
        height=600
    )
