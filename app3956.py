import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide")

# --- 2. GIAO DIỆN CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .main-header { color: #00FFFF; text-align: center; font-size: 32px; font-weight: bold; padding: 10px; border-bottom: 2px solid #58a6ff; margin-bottom: 20px; }
    .info-box { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 15px; text-align: center; margin-bottom: 10px; }
    .info-label { color: #8b949e; font-size: 11px; font-weight: bold; text-transform: uppercase; }
    .info-value { color: #ffffff; font-size: 16px; font-weight: bold; margin-top: 5px; }
    .target-text { color: #58a6ff; font-weight: bold; font-size: 14px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC MỤC TIÊU (Kill tính bằng hàng trăm triệu) ---
def get_targets(pow_before):
    p_mil = pow_before / 1_000_000
    if p_mil < 15: return 100_000_000, 200_000
    elif p_mil < 20: return 200_000_000, 250_000
    elif p_mil < 30: return 250_000_000, 300_000
    else: return 300_000_000, 400_000

# --- 4. XỬ LÝ DỮ LIỆU ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
# Sử dụng phương thức xuất trực tiếp để tránh lỗi HTTP 400
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=351056493'

@st.cache_data(ttl=30)
def load_data():
    try:
        df = pd.read_csv(URL)
        # Làm sạch tên cột (xóa khoảng trắng và dấu xuống dòng)
        df.columns = [str(c).replace('\n', ' ').strip() for c in df.columns]
        
        # Tự động dò tìm các cột quan trọng dựa trên ảnh thực tế
        col_name = 'Tên Người Dùng'
        col_pow = 'Sức Mạnh'
        col_max_pow = 'Kỷ Lực Sức Mạnh' # Cột D trong ảnh
        col_kill = 'Tổng Điểm Tiêu Diệt' # Cột J trong ảnh

        # Chuyển đổi các cột lính tử vong (Cột E đến I)
        dead_cols = ['T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong']
        for c in dead_cols + [col_pow, col_max_pow, col_kill]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

        # Tính tổng tử vong và điểm quy đổi
        df['SUM_DEAD'] = df[dead_cols].sum(axis=1)
        df['DEAD_SCORE'] = (df['T5 tử vong']*10 + df['T4 tử vong']*4 + df['T3 tử vong']*3 + df['T2 tử vong']*2 + df['T1 tử vong']*1)

        # Áp dụng mục tiêu từ mốc "Kỷ Lực Sức Mạnh" (Power trước khi đánh)
        targets = df[col_max_pow].apply(get_targets)
        df['T_KILL'] = [x[0] for x in targets]
        df['T_DEAD'] = [x[1] for x in targets]
        
        # Tính % hoàn thành (Giới hạn tối đa 150%)
        df['K_PCT'] = (df[col_kill] / df['T_KILL'] * 100).clip(upper=150)
        df['D_PCT'] = (df['SUM_DEAD'] / df['T_DEAD'] * 100).clip(upper=150)
        
        return df, col_name, col_pow, col_max_pow, col_kill
    except Exception as e:
        st.error(f"Lỗi: {e}")
        return None, None, None, None, None

df, c_name, c_pow, c_max_pow, c_kill = load_data()

# --- 5. HIỂN THỊ ---
if df is not None:
    st.markdown('<div class="main-header">3956 KPI COMMANDER</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["👤 CHI TIẾT", "🏆 BẢNG XẾP HẠNG"])

    with tab1:
        sel = st.selectbox("🔍 CHỌN CHIẾN BINH:", df[c_name].unique())
        if sel:
            d = df[df[c_name] == sel].iloc[0]
            st.write(f"### 🛡️ {sel}")
            cols = st.columns(4)
            cols[0].markdown(f'<div class="info-box"><div class="info-label">KPI DỰA TRÊN POW</div><div class="info-value">{int(d[c_max_pow]):,}</div></div>', unsafe_allow_html=True)
            cols[1].markdown(f'<div class="info-box"><div class="info-label">POW HIỆN TẠI</div><div class="info-value">{int(d[c_pow]):,}</div></div>', unsafe_allow_html=True)
            cols[2].markdown(f'<div class="info-box"><div class="info-label">TỔNG KILL</div><div class="info-value">{int(d[c_kill]):,}</div></div>', unsafe_allow_html=True)
            cols[3].markdown(f'<div class="info-box"><div class="info-label">TỔNG DEAD</div><div class="info-value">{int(d["SUM_DEAD"]):,}</div></div>', unsafe_allow_html=True)

            # Biểu đồ KPI
            ck1, ck2 = st.columns(2)
            with ck1:
                st.markdown(f'<p class="target-text">🎯 MỤC TIÊU KILL: {int(d["T_KILL"]):,}</p>', unsafe_allow_html=True)
                st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=d['K_PCT'], number={'suffix': "%"}, gauge={'bar':{'color':"#00FFFF"}})), use_container_width=True)
            with ck2:
                st.markdown(f'<p class="target-text">🎯 MỤC TIÊU DEAD: {int(d["T_DEAD"]):,}</p>', unsafe_allow_html=True)
                st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=d['D_PCT'], number={'suffix': "%"}, gauge={'bar':{'color':"#f29b05"}})), use_container_width=True)

    with tab2:
        st.subheader("🏆 DANH SÁCH HOÀN THÀNH KPI")
        st.dataframe(df[[c_name, c_max_pow, 'K_PCT', 'D_PCT']].sort_values(by='K_PCT', ascending=False), use_container_width=True)
