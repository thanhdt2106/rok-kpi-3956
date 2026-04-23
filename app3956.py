import streamlit as st
import pandas as pd

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="ROK KPI 3956 | PRO PROFILE", layout="wide")

# --- 2. GIAO DIỆN PHONG CÁCH ROKBOARD (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0f111a; color: #ffffff; }
    /* Khung hồ sơ chính */
    .profile-container {
        background: linear-gradient(180deg, #1a1c2e 0%, #0f111a 100%);
        border-radius: 15px;
        padding: 30px;
        border: 1px solid #2d2f45;
        margin-bottom: 20px;
    }
    /* Avatar tròn */
    .avatar-circle {
        width: 100px;
        height: 100px;
        background: #f29b05;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 40px;
        font-weight: bold;
        color: white;
        border: 4px solid #2d2f45;
        margin-bottom: 10px;
    }
    /* Các ô chỉ số (Cards) */
    .stat-card {
        background: #161826;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        border: 1px solid #2d2f45;
    }
    .stat-label { color: #8e92a4; font-size: 12px; text-transform: uppercase; }
    .stat-value { color: #ffffff; font-size: 18px; font-weight: bold; display: block; margin-top: 5px; }
    .stat-value.gold { color: #f29b05; }
    
    /* Tùy chỉnh Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1c2e;
        border-radius: 5px 5px 0 0;
        padding: 10px 20px;
        color: #8e92a4;
    }
    .stTabs [aria-selected="true"] { background-color: #3d42df !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. XỬ LÝ DỮ LIỆU (Đã fix toàn bộ lỗi cũ) ---
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
        for c in num_cols: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        df['K+'] = df['Tổng Tiêu Diệt_2'] - df['Tổng Tiêu Diệt_1']
        df['D+'] = df['Điểm Chết_2'] - df['Điểm Chết_1']
        def get_t(p):
            if p < 15e6: return 10e6, 200e3
            if p < 20e6: return 20e6, 250e3
            if p < 30e6: return 25e6, 300e3
            return 30e6, 400e3
        def kpi(r):
            gk, gd = get_t(r['Sức Mạnh_2'])
            return round(((max(0,min(r['K+']/gk,1)) + max(0,min(r['D+']/gd,1)))/2)*100, 1)
        df['KPI'] = df.apply(kpi, axis=1)
        return df
    except Exception as e:
        st.error(f"Data Error: {e}")
        return None

df = load_data()

# --- 4. HIỂN THỊ HỒ SƠ ---
if df is not None:
    st.markdown("<h2 style='text-align:center; color:#f29b05;'>KINGDOM MANAGER 3956</h2>", unsafe_allow_html=True)
    
    names = sorted([str(n) for n in df['Tên_2'].unique() if n != 'Unknown'])
    sel = st.selectbox("🔍 Tìm kiếm thống kê người chơi:", ["--- Chọn người chơi ---"] + names)
    
    if sel != "--- Chọn người chơi ---":
        d = df[df['Tên_2'] == sel].iloc[0]
        
        # --- HEADER HỒ SƠ (GIỐNG ROKBOARD) ---
        st.markdown(f"""
            <div class="profile-container">
                <div style="display: flex; align-items: center; gap: 20px;">
                    <div class="avatar-circle">{sel[0].upper()}</div>
                    <div>
                        <h1 style="margin:0; font-size:28px;">{sel} <span style="font-size:16px; color:#3d42df;">✔ Verified</span></h1>
                        <p style="color:#8e92a4; margin:0;">ID: {d['ID']} | {d['Liên Minh_2']}</p>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; margin-top: 25px;">
                    <div class="stat-card"><span class="stat-label">Lực chiến</span><span class="stat-value">{int(d['Sức Mạnh_2']):,}</span></div>
                    <div class="stat-card"><span class="stat-label">Điểm hạ gục</span><span class="stat-value gold">{int(d['Tổng Tiêu Diệt_2']):,}</span></div>
                    <div class="stat-card"><span class="stat-label">Số lính chết</span><span class="stat-value">{int(d['Điểm Chết_2']):,}</span></div>
                    <div class="stat-card"><span class="stat-label">Kill Tăng</span><span class="stat-value" style="color:#47cf73;">+{int(d['K+']):,}</span></div>
                    <div class="stat-card"><span class="stat-label">KPI Đạt</span><span class="stat-value" style="color:#f29b05;">{d['KPI']}%</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # --- BIỂU ĐỒ TIẾN ĐỘ ---
        st.write("### 📊 Performance Progress")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Tiến độ Tiêu diệt (Kills)**")
            st.progress(max(0, min(d['K+'] / 30e6, 1.0))) # Ví dụ mốc 30M
        with col2:
            st.write("**Tiến độ Điểm chết (Deads)**")
            st.progress(max(0, min(d['D+'] / 400e3, 1.0))) # Ví dụ mốc 400K

    # --- BẢNG TỔNG HỢP ---
    st.divider()
    tab1, tab2 = st.tabs(["Danh sách thành viên", "Top cống hiến"])
    with tab1:
        st.dataframe(df[['Tên_2', 'Liên Minh_2', 'Sức Mạnh_2', 'KPI']].rename(columns={'Tên_2':'Tên','KPI':'% KPI'}), use_container_width=True)
