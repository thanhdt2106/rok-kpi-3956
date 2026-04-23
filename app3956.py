import streamlit as st
import pandas as pd

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="ROK KPI 3956 | COMMAND CENTER", layout="wide")

# --- 2. GIAO DIỆN PHONG CÁCH QUÂN SỰ TỐI GIẢN (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #cfd8dc; }
    
    /* Hồ sơ cá nhân */
    .profile-box {
        background-color: #151921;
        border-radius: 12px;
        padding: 25px;
        border: 1px solid #263238;
        margin-bottom: 30px;
    }
    .player-name { color: #ffa000; font-size: 32px; font-weight: bold; margin-bottom: 5px; }
    .player-sub { color: #78909c; font-size: 14px; margin-bottom: 20px; }
    
    /* Card chỉ số */
    .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; }
    .stat-item {
        background: #1c222d;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        border-bottom: 3px solid #ffa000;
    }
    .label { color: #90a4ae; font-size: 11px; text-transform: uppercase; display: block; }
    .value { color: #ffffff; font-size: 18px; font-weight: bold; }

    /* Tùy chỉnh bảng dữ liệu ở trang chủ */
    [data-testid="stDataFrame"] { background-color: #151921; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. XỬ LÝ DỮ LIỆU ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
URL_T = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=731741617'
URL_S = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=371969335'

@st.cache_data(ttl=30)
def load():
    try:
        dt = pd.read_csv(URL_T).rename(columns=lambda x: x.strip())
        ds = pd.read_csv(URL_S).rename(columns=lambda x: x.strip())
        
        # Làm sạch dữ liệu
        for d in [dt, ds]:
            d['ID'] = d['ID'].astype(str).str.replace('.0', '', regex=False).str.strip()
            d['Tên'] = d['Tên'].fillna('Unknown').astype(str).str.strip()

        # Merge dữ liệu
        df = pd.merge(dt.drop_duplicates('ID'), ds.drop_duplicates('ID'), on='ID', suffixes=('_1', '_2'))
        
        # Chuyển đổi số
        num_cols = ['Sức Mạnh_2', 'Tổng Tiêu Diệt_2', 'Điểm Chết_2', 'Tổng Tiêu Diệt_1', 'Điểm Chết_1']
        for c in num_cols:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            
        df['Kill Tăng'] = df['Tổng Tiêu Diệt_2'] - df['Tổng Tiêu Diệt_1']
        df['Dead Tăng'] = df['Điểm Chết_2'] - df['Điểm Chết_1']
        
        def get_t(p):
            if p < 15e6: return 10e6, 200e3
            if p < 20e6: return 20e6, 250e3
            if p < 30e6: return 25e6, 300e3
            return 30e6, 400e3
            
        def kpi_calc(r):
            gk, gd = get_t(r['Sức Mạnh_2'])
            pk = max(0, min(r['Kill Tăng']/gk, 1.0)) if gk > 0 else 0
            pd_v = max(0, min(r['Dead Tăng']/gd, 1.0)) if gd > 0 else 0
            return round(((pk + pd_v) / 2) * 100, 1)
        
        df['% KPI'] = df.apply(kpi_calc, axis=1)
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return None

df = load()

# --- 4. GIAO DIỆN HIỂN THỊ ---
if df is not None:
    st.markdown("<h1 style='text-align:center; color:#ffa000;'>🛡️ ALLIANCE KPI COMMANDER 3956</h1>", unsafe_allow_html=True)

    # 1. Tra cứu chi tiết
    names = sorted([str(n) for n in df['Tên_2'].unique() if n != 'Unknown'])
    sel = st.selectbox("🔍 TRA CỨU CHIẾN BINH:", ["--- Chọn tên người chơi ---"] + names)
    
    if sel != "--- Chọn tên người chơi ---":
        d = df[df['Tên_2'] == sel].iloc[0]
        st.markdown(f"""
            <div class="profile-box">
                <div class="player-name">👤 {sel}</div>
                <div class="player-sub">ID: {d['ID']} | LIÊN MINH: {d['Liên Minh_2']}</div>
                <div class="stat-grid">
                    <div class="stat-item"><span class="label">Sức Mạnh</span><span class="value">{int(d['Sức Mạnh_2']):,}</span></div>
                    <div class="stat-item"><span class="label">Tổng Kill</span><span class="value">{int(d['Tổng Tiêu Diệt_2']):,}</span></div>
                    <div class="stat-item"><span class="label">Kill Tăng</span><span class="value" style="color:#4caf50;">+{int(d['Kill Tăng']):,}</span></div>
                    <div class="stat-item"><span class="label">Dead Tăng</span><span class="value" style="color:#f44336;">+{int(d['Dead Tăng']):,}</span></div>
                    <div class="stat-item"><span class="label">Tiến Độ KPI</span><span class="value" style="color:#ffa000;">{d['% KPI']}%</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # 2. Bảng tổng hợp trang chủ (Khôi phục đầy đủ các dòng)
    st.subheader("📋 BẢNG THỐNG KÊ TỔNG HỢP")
    
    # Chuẩn bị bảng hiển thị đầy đủ thông tin
    view_df = df[[
        'Tên_2', 'ID', 'Liên Minh_2', 'Sức Mạnh_2', 
        'Tổng Tiêu Diệt_2', 'Kill Tăng', 'Dead Tăng', '% KPI'
    ]].copy()
    
    view_df.columns = [
        'Tên Người Chơi', 'ID', 'Liên Minh', 'Sức Mạnh', 
        'Tổng Kill', 'Kill Tăng (+)', 'Dead Tăng (+)', 'KPI Đạt (%)'
    ]

    # Định dạng hiển thị dấu phẩy và màu sắc
    st.dataframe(
        view_df.style.format({
            'Sức Mạnh': '{:,.0f}',
            'Tổng Kill': '{:,.0f}',
            'Kill Tăng (+)': '{:,.0f}',
            'Dead Tăng (+)': '{:,.0f}',
            'KPI Đạt (%)': '{:.1f}%'
        }).background_gradient(subset=['KPI Đạt (%)'], cmap='YlOrBr'),
        use_container_width=True,
        height=600
    )

    # 3. Chú thích mốc KPI
    with st.expander("ℹ️ Xem quy định mốc KPI"):
        st.write("""
        - **Dưới 15M Power:** 10M Kill | 200K Dead
        - **15M - 20M Power:** 20M Kill | 250K Dead
        - **20M - 30M Power:** 25M Kill | 300K Dead
        - **Trên 30M Power:** 30M Kill | 400K Dead
        """)
