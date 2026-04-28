import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI | COMMAND CENTER", layout="wide")

# --- 2. GIAO DIỆN CSS (DARK MODE & NEON) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e6ed; }
    .main-header {
        color: #00d4ff; text-align: center; font-size: 30px; font-weight: bold;
        padding: 10px; text-transform: uppercase; text-shadow: 0 0 10px #00d4ff80;
    }
    .metric-box {
        background: #1a1c23; border: 1px solid #00d4ff33; border-radius: 10px;
        padding: 15px; text-align: center; box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    .metric-label { color: #8899a6; font-size: 12px; font-weight: bold; }
    .metric-value { color: #ffffff; font-size: 20px; font-weight: bold; margin-top: 5px; }
    .metric-icon { color: #00d4ff; font-size: 18px; margin-right: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. XỬ LÝ DỮ LIỆU ---
# Gid từ ảnh của bạn là 351056493
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
GID = '351056493' 
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}'

@st.cache_data(ttl=30)
def load_data():
    try:
        df = pd.read_csv(URL)
        df.columns = [str(c).strip() for c in df.columns]
        
        # Chuyển đổi ID (Cột A)
        df['ID nhân vật'] = df['ID nhân vật'].astype(str).str.split('.').str[0]
        
        # Chuyển đổi số liệu (Sức mạnh C, Tổng điểm tiêu diệt J, Tài nguyên R)
        cols_to_fix = ['Sức Mạnh', 'Tổng Điểm Tiêu Diệt', 'Tài Nguyên Thu Thập', 'T2 tử vong', 'T3 tử vong', 'T4 tử vong', 'T5 tử vong']
        for c in cols_to_fix:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

        # Tính DEAD+ (T2+T3+T4+T5)
        df['DEAD_PLUS'] = df['T2 tử vong'] + df['T3 tử vong'] + df['T4 tử vong'] + df['T5 tử vong']
        
        # Tính KPI SCORE (Xếp hạng)
        # Công thức: Kill + (Dead * 10) để phân thứ hạng
        df['KPI_SCORE'] = df['Tổng Điểm Tiêu Diệt'] + (df['DEAD_PLUS'] * 10)
        
        # Sắp xếp Rank
        df = df.sort_values(by='KPI_SCORE', ascending=False).reset_index(drop=True)
        df.insert(0, 'RANK', df.index + 1)
        
        return df
    except Exception as e:
        st.error(f"Lỗi nạp dữ liệu: {e}")
        return None

df = load_data()

# --- 4. HIỂN THỊ ---
if df is not None:
    st.markdown('<div class="main-header">🛡️ FTD COMMAND CENTER - KPI SYSTEM</div>', unsafe_allow_html=True)
    
    # Tìm kiếm
    names = sorted(df['Tên Người Dùng'].dropna().unique())
    sel = st.selectbox("🔍 TRA CỨU CHIẾN BINH:", ["--- Chọn tên chiến binh ---"] + names)
    
    if sel != "--- Chọn tên chiến binh ---":
        d = df[df['Tên Người Dùng'] == sel].iloc[0]
        
        # Row 1: Profile cá nhân dạng Box
        st.markdown(f"### 👤 Hồ sơ: {sel} (Rank #{int(d['RANK'])})")
        c1, c2, c3, c4, c5 = st.columns(5)
        
        with c1:
            st.markdown(f'<div class="metric-box"><div class="metric-label">ID NHÂN VẬT</div><div class="metric-value">🆔 {d["ID nhân vật"]}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-box"><div class="metric-label">SỨC MẠNH</div><div class="metric-value">⚡ {int(d["Sức Mạnh"]):,}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-box"><div class="metric-label">KILL (+)</div><div class="metric-value">⚔️ {int(d["Tổng Điểm Tiêu Diệt"]):,}</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="metric-box"><div class="metric-label">DEAD (+)</div><div class="metric-value">💀 {int(d["DEAD_PLUS"]):,}</div></div>', unsafe_allow_html=True)
        with c5:
            st.markdown(f'<div class="metric-box"><div class="metric-label">TÀI NGUYÊN</div><div class="metric-value">📦 {int(d["Tài Nguyên Thu Thập"]):,}</div></div>', unsafe_allow_html=True)
            
        st.write("") # Khoảng cách

    # --- BẢNG TỔNG HỢP ---
    st.subheader("📋 BẢNG THỐNG KÊ CHIẾN DỊCH")
    
    # Chọn các cột hiển thị đúng thứ tự yêu cầu
    view_df = df[['RANK', 'ID nhân vật', 'Tên Người Dùng', 'Sức Mạnh', 'Tổng Điểm Tiêu Diệt', 'DEAD_PLUS', 'Tài Nguyên Thu Thập']].copy()
    
    # Đổi tên cột cho đẹp
    view_df.columns = ['RANK', 'ID', 'NAME', 'SỨC MẠNH', 'KILL (+)', 'DEAD (+)', 'TÀI NGUYÊN']
    
    # Hiển thị bảng
    st.dataframe(
        view_df.style.format({
            'SỨC MẠNH': '{:,.0f}',
            'KILL (+)': '{:,.0f}',
            'DEAD (+)': '{:,.0f}',
            'TÀI NGUYÊN': '{:,.0f}'
        }),
        use_container_width=True,
        height=500
    )
else:
    st.info("💡 Mẹo: Hãy đảm bảo bạn đã 'Chia sẻ' Google Sheet ở chế độ 'Bất kỳ ai có liên kết đều có thể xem'.")
