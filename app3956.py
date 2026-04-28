import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide")

# --- 2. GIAO DIỆN CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .main-header {
        color: #00FFFF; text-align: center; font-size: 32px; font-weight: bold;
        padding: 10px; border-bottom: 2px solid #58a6ff; margin-bottom: 20px;
    }
    .info-box {
        background: #161b22; border: 1px solid #30363d; border-radius: 10px;
        padding: 15px; text-align: center; margin-bottom: 10px; min-height: 100px;
        display: flex; flex-direction: column; justify-content: center;
    }
    .info-label { color: #8b949e; font-size: 11px; font-weight: bold; text-transform: uppercase; }
    .info-value { color: #ffffff; font-size: 16px; font-weight: bold; margin-top: 5px; }
    .target-text { color: #58a6ff; font-weight: bold; font-size: 14px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC TÍNH KPI THEO MỐC "KỶ LỰC SỨC MẠNH" ---
def get_targets(pow_before):
    p_mil = pow_before / 1_000_000
    if p_mil < 15:
        return 100_000_000, 200_000  # Kill, Dead Units
    elif p_mil < 20:
        return 200_000_000, 250_000
    elif p_mil < 30:
        return 250_000_000, 300_000
    else: # Mốc cao nhất từ 40M+
        return 300_000_000, 400_000

# --- 4. XỬ LÝ DỮ LIỆU ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
GID = '351056493'
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}'

@st.cache_data(ttl=30)
def load_data():
    try:
        # Đọc dữ liệu thô
        df = pd.read_csv(URL)
        
        # --- BƯỚC QUAN TRỌNG: CHUẨN HÓA TÊN CỘT ---
        # Xóa khoảng trắng đầu cuối và xóa ký tự xuống dòng (\n) thường gặp trong Sheet
        df.columns = [str(c).replace('\n', ' ').strip() for c in df.columns]
        
        # Ánh xạ tên cột nếu Sheet dùng tên khác một chút (Dựa trên ảnh image_69c9f5.png)
        rename_map = {
            'Tổng Điểm Tiêu Diệt': 'Tổng Điểm Tiêu Diệt', 
            'Kỷ Lực Sức Mạnh': 'Kỷ Lực Sức Mạnh'
        }
        df = df.rename(columns=rename_map)

        # Danh sách các cột số liệu cần ép kiểu
        numeric_cols = [
            'Sức Mạnh', 'Kỷ Lực Sức Mạnh', 'T5 tử vong', 'T4 tử vong', 'T3 tử vong', 
            'T2 tử vong', 'T1 tử vong', 'Tổng Điểm Tiêu Diệt', 'Tài Nguyên Thu Thập', 'Hỗ Trợ Liên Minh'
        ]
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Tính toán các chỉ số bổ trợ
        df['TOTAL_DEAD_UNITS'] = df.get('T5 tử vong', 0) + df.get('T4 tử vong', 0) + \
                                 df.get('T3 tử vong', 0) + df.get('T2 tử vong', 0) + \
                                 df.get('T1 tử vong', 0)
        
        df['DEAD_POWER_SCORE'] = (df.get('T5 tử vong', 0) * 10) + (df.get('T4 tử vong', 0) * 4) + \
                                 (df.get('T3 tử vong', 0) * 3) + (df.get('T2 tử vong', 0) * 2) + \
                                 (df.get('T1 tử vong', 0) * 1)

        # Áp dụng Target dựa trên Kỷ Lực Sức Mạnh
        targets = df['Kỷ Lực Sức Mạnh'].apply(get_targets)
        df['TARGET_KILL'] = [x[0] for x in targets]
        df['TARGET_DEAD'] = [x[1] for x in targets]
        
        # Tính % hoàn thành
        df['KILL_PCT'] = (df['Tổng Điểm Tiêu Diệt'] / df['TARGET_KILL'] * 100).clip(upper=150)
        df['DEAD_PCT'] = (df['TOTAL_DEAD_UNITS'] / df['TARGET_DEAD'] * 100).clip(upper=150)
        
        # Xếp Rank
        df['TOTAL_SCORE'] = df['Tổng Điểm Tiêu Diệt'] + df['DEAD_POWER_SCORE']
        df = df.sort_values(by='TOTAL_SCORE', ascending=False).reset_index(drop=True)
        df.insert(0, 'RANK', df.index + 1)
        
        return df
    except Exception as e:
        st.error(f"Lỗi nạp dữ liệu: {e}")
        return None

df = load_data()

# --- 5. HIỂN THỊ ---
if df is not None:
    st.markdown('<div class="main-header">SHARED HOUSE 3956 - KPI COMMANDER</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["👤 HỒ SƠ CHI TIẾT", "🏆 BẢNG XẾP HẠNG"])
    
    with tab1:
        # Kiểm tra xem cột Tên Người Dùng có tồn tại không
        name_col = 'Tên Người Dùng' if 'Tên Người Dùng' in df.columns else df.columns[1]
        sel = st.selectbox("🔍 CHỌN CHIẾN BINH:", df[name_col].unique())
        
        if sel:
            d = df[df[name_col] == sel].iloc[0]
            
            # --- PROFILE GRID ---
            st.write("**📌 THÔNG TIN CƠ BẢN**")
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.markdown(f'<div class="info-box"><div class="info-label">KỶ LỤC (KPI BASE)</div><div class="info-value">🏆 {int(d["Kỷ Lực Sức Mạnh"]):,}</div></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="info-box"><div class="info-label">POW HIỆN TẠI</div><div class="info-value">⚡ {int(d["Sức Mạnh"]):,}</div></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="info-box"><div class="info-label">TỔNG KILL</div><div class="info-value">🔥 {int(d["Tổng Điểm Tiêu Diệt"]):,}</div></div>', unsafe_allow_html=True)
            c4.markdown(f'<div class="info-box"><div class="info-label">TÀI NGUYÊN</div><div class="info-value">📦 {int(d["Tài Nguyên Thu Thập"]):,}</div></div>', unsafe_allow_html=True)
            c5.markdown(f'<div class="info-box"><div class="info-label">RANK LM</div><div class="info-value">👑 #{int(d["RANK"])}</div></div>', unsafe_allow_html=True)

            # --- KPI GAUGE ---
            st.write("---")
            st.write(f"**📊 TIẾN ĐỘ KPI (DỰA TRÊN MỐC {int(d['Kỷ Lực Sức Mạnh']/1_000_000)}M POW)**")
            ck1, ck2 = st.columns(2)
            with ck1:
                st.markdown(f'<p class="target-text">🎯 MỤC TIÊU KILL: {int(d["TARGET_KILL"]):,}</p>', unsafe_allow_html=True)
                fig_k = go.Figure(go.Indicator(mode="gauge+number", value=d['KILL_PCT'], number={'suffix': "%"}, gauge={'axis':{'range':[0, 100]},'bar':{'color':"#00FFFF"},'steps':[{'range':[0, 65],'color':"#30363d"}]}))
                st.plotly_chart(fig_k, use_container_width=True)
            with ck2:
                st.markdown(f'<p class="target-text">🎯 MỤC TIÊU DEAD: {int(d["TARGET_DEAD"]):,}</p>', unsafe_allow_html=True)
                fig_d = go.Figure(go.Indicator(mode="gauge+number", value=d['DEAD_PCT'], number={'suffix': "%"}, gauge={'axis':{'range':[0, 100]},'bar':{'color':"#f29b05"},'steps':[{'range':[0, 65],'color':"#30363d"}]}))
                st.plotly_chart(fig_d, use_container_width=True)

    with tab2:
        st.subheader("🏆 CHI TIẾT HOÀN THÀNH")
        view_df = df[['RANK', name_col, 'Kỷ Lực Sức Mạnh', 'Sức Mạnh', 'KILL_PCT', 'DEAD_PCT', 'TOTAL_SCORE']]
        st.dataframe(view_df.style.format({
            'Kỷ Lực Sức Mạnh': '{:,.0f}', 'Sức Mạnh': '{:,.0f}',
            'KILL_PCT': '{:.1f}%', 'DEAD_PCT': '{:.1f}%', 'TOTAL_SCORE': '{:,.0f}'
        }), use_container_width=True, height=600)
