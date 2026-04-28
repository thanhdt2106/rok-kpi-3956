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

# --- 3. LOGIC TÍNH KPI THEO MỐC POWER (ĐÃ CHỈNH ĐƠN VỊ KILL) ---
def get_targets(power):
    p_mil = power / 1_000_000
    # Kill KPI chỉnh về hàng trăm triệu (10M -> 100M, 20M -> 200M,...)
    if p_mil < 15:
        return 100_000_000, 200_000  # Kill, Dead Units
    elif p_mil < 20:
        return 200_000_000, 250_000
    elif p_mil < 30:
        return 250_000_000, 300_000
    else: # > 40M
        return 300_000_000, 400_000

# --- 4. XỬ LÝ DỮ LIỆU ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
GID = '351056493'
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}'

@st.cache_data(ttl=30)
def load_data():
    try:
        df = pd.read_csv(URL)
        df.columns = [str(c).strip() for c in df.columns]
        
        numeric_cols = [
            'Sức Mạnh', 'T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong', 
            'Tổng Điểm Tiêu Diệt', 'Kỷ Lực Sức Mạnh', 'Tài Nguyên Thu Thập', 'Hỗ Trợ Liên Minh'
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Tính Dead Power Score (Trọng số T5=10, T4=4, T3=3, T2=2, T1=1)
        df['DEAD_POWER_SCORE'] = (df['T5 tử vong'] * 10) + (df['T4 tử vong'] * 4) + \
                                 (df['T3 tử vong'] * 3) + (df['T2 tử vong'] * 2) + \
                                 (df['T1 tử vong'] * 1)

        # Áp dụng hàm tính Target
        targets = df['Sức Mạnh'].apply(get_targets)
        df['TARGET_KILL'] = [x[0] for x in targets]
        df['TARGET_DEAD'] = [x[1] for x in targets]
        
        # Tính % Hoàn thành
        df['TOTAL_DEAD_UNITS'] = df['T5 tử vong'] + df['T4 tử vong'] + df['T3 tử vong'] + df['T2 tử vong'] + df['T1 tử vong']
        df['KILL_PCT'] = (df['Tổng Điểm Tiêu Diệt'] / df['TARGET_KILL']) * 100
        df['DEAD_PCT'] = (df['TOTAL_DEAD_UNITS'] / df['TARGET_DEAD']) * 100
        
        # Tính Rank theo Tổng Điểm (Kill + Dead Power)
        df['TOTAL_KPI_SCORE'] = df['Tổng Điểm Tiêu Diệt'] + df['DEAD_POWER_SCORE']
        df = df.sort_values(by='TOTAL_KPI_SCORE', ascending=False).reset_index(drop=True)
        df.insert(0, 'RANK', df.index + 1)
        
        return df
    except Exception as e:
        st.error(f"Lỗi: {e}")
        return None

df = load_data()

# --- 5. HIỂN THỊ ---
if df is not None:
    st.markdown('<div class="main-header">SHARED HOUSE 3956 - KPI SYSTEM</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["👤 HỒ SƠ CHI TIẾT", "🏆 BẢNG XẾP HẠNG"])
    
    with tab1:
        sel = st.selectbox("🔍 CHỌN CHIẾN BINH:", df['Tên Người Dùng'].unique())
        if sel:
            d = df[df['Tên Người Dùng'] == sel].iloc[0]
            st.markdown(f"### 🎖️ {sel} (RANK #{int(d['RANK'])})")
            
            # PROFILE GRID BOX
            st.write("**📌 THÔNG TIN CƠ BẢN**")
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.markdown(f'<div class="info-box"><div class="info-label">SỨC MẠNH</div><div class="info-value">⚡ {int(d["Sức Mạnh"]):,}</div></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="info-box"><div class="info-label">KỶ LỤC POW</div><div class="info-value">🏆 {int(d["Kỷ Lực Sức Mạnh"]):,}</div></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="info-box"><div class="info-label">TỔNG KILL</div><div class="info-value">🔥 {int(d["Tổng Điểm Tiêu Diệt"]):,}</div></div>', unsafe_allow_html=True)
            c4.markdown(f'<div class="info-box"><div class="info-label">TÀI NGUYÊN</div><div class="info-value">📦 {int(d["Tài Nguyên Thu Thập"]):,}</div></div>', unsafe_allow_html=True)
            c5.markdown(f'<div class="info-box"><div class="info-label">HỖ TRỢ LM</div><div class="info-value">🤝 {int(d["Hỗ Trợ Liên Minh"]):,}</div></div>', unsafe_allow_html=True)

            st.write("**🩸 CHI TIẾT TỬ VONG**")
            d1, d2, d3, d4, d5 = st.columns(5)
            d1.markdown(f'<div class="info-box"><div class="info-label">T5 (x10)</div><div class="info-value">💀 {int(d["T5 tử vong"]):,}</div></div>', unsafe_allow_html=True)
            d2.markdown(f'<div class="info-box"><div class="info-label">T4 (x4)</div><div class="info-value">💀 {int(d["T4 tử vong"]):,}</div></div>', unsafe_allow_html=True)
            d3.markdown(f'<div class="info-box"><div class="info-label">T3 (x3)</div><div class="info-value">💀 {int(d["T3 tử vong"]):,}</div></div>', unsafe_allow_html=True)
            d4.markdown(f'<div class="info-box"><div class="info-label">T2 (x2)</div><div class="info-value">💀 {int(d["T2 tử vong"]):,}</div></div>', unsafe_allow_html=True)
            d5.markdown(f'<div class="info-box"><div class="info-label">T1 (x1)</div><div class="info-value">💀 {int(d["T1 tử vong"]):,}</div></div>', unsafe_allow_html=True)

            # TIẾN ĐỘ KPI
            st.write("---")
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
        st.subheader("🏆 BẢNG XẾP HẠNG KPI")
        # Thêm cột TOTAL_KPI_SCORE ở cuối cùng
        view_df = df[['RANK', 'Tên Người Dùng', 'Sức Mạnh', 'Tổng Điểm Tiêu Diệt', 'TOTAL_DEAD_UNITS', 'KILL_PCT', 'DEAD_PCT', 'TOTAL_KPI_SCORE']]
        st.dataframe(view_df.style.format({'Sức Mạnh':'{:,.0f}','Tổng Điểm Tiêu Diệt':'{:,.0f}','TOTAL_DEAD_UNITS':'{:,.0f}','KILL_PCT':'{:.1f}%','DEAD_PCT':'{:.1f}%','TOTAL_KPI_SCORE':'{:,.0f}'}), use_container_width=True, height=600)
