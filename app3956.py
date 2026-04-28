import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide")

# --- 2. GIAO DIỆN CSS (DARK MODE & GRID BOX) ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .main-header {
        color: #58a6ff; text-align: center; font-size: 28px; font-weight: bold;
        padding: 10px; border-bottom: 1px solid #30363d; margin-bottom: 20px;
    }
    .info-box {
        background: #161b22; border: 1px solid #30363d; border-radius: 10px;
        padding: 15px; text-align: center; margin-bottom: 10px; height: 100px;
        display: flex; flex-direction: column; justify-content: center;
    }
    .info-label { color: #8b949e; font-size: 11px; font-weight: bold; text-transform: uppercase; }
    .info-value { color: #ffffff; font-size: 16px; font-weight: bold; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. XỬ LÝ DỮ LIỆU ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
GID = '351056493'
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}'

@st.cache_data(ttl=30)
def load_data():
    try:
        df = pd.read_csv(URL)
        # Chuẩn hóa tên cột để tránh lỗi KeyError do khoảng trắng
        df.columns = [str(c).strip() for c in df.columns]
        
        # Danh sách các cột số liệu dựa trên ảnh Sheet của bạn
        numeric_cols = [
            'Sức Mạnh', 'Kỷ Lực Sức Mạnh', 'T5 tử vong', 'T4 tử vong', 'T3 tử vong', 
            'T2 tử vong', 'T1 tử vong', 'Tổng Điểm Tiêu Diệt', 'Tổng Tiêu Diệt T5', 
            'Tổng Tiêu Diệt T4', 'Tổng Tiêu Diệt T3', 'Tổng Tiêu Diệt T2', 
            'Tài Nguyên Thu Thập', 'Hỗ Trợ Liên Minh'
        ]
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # A. TÍNH ĐIỂM DEAD THEO TRỌNG SỐ POWER MỚI
        # T5=10, T4=4, T3=3, T2=2, T1=1
        df['DEAD_POWER_SCORE'] = (df['T5 tử vong'] * 10) + \
                                 (df['T4 tử vong'] * 4) + \
                                 (df['T3 tử vong'] * 3) + \
                                 (df['T2 tử vong'] * 2) + \
                                 (df['T1 tử vong'] * 1)
        
        # B. TÍNH KPI TỔNG (Kill + Dead Power)
        df['TOTAL_KPI'] = df['Tổng Điểm Tiêu Diệt'] + df['DEAD_POWER_SCORE']
        
        # C. SẮP XẾP RANK
        df = df.sort_values(by='TOTAL_KPI', ascending=False).reset_index(drop=True)
        df.insert(0, 'RANK', df.index + 1)
        
        return df
    except Exception as e:
        st.error(f"Lỗi nạp dữ liệu: {e}")
        return None

df = load_data()

# --- 4. HIỂN THỊ ---
if df is not None:
    st.markdown('<div class="main-header">🛡️ FTD KPI COMMAND CENTER</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["👤 HỒ SƠ CHI TIẾT", "📊 BẢNG XẾP HẠNG"])
    
    with tab1:
        names = sorted(df['Tên Người Dùng'].unique())
        sel = st.selectbox("🔍 CHỌN CHIẾN BINH:", names)
        if sel:
            d = df[df['Tên Người Dùng'] == sel].iloc[0]
            st.markdown(f"### 🎖️ {sel} (RANK #{int(d['RANK'])})")
            
            # NHÓM 1: THÔNG TIN CƠ BẢN (Ô BOX)
            st.write("**📌 THÔNG TIN CƠ BẢN**")
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f'<div class="info-box"><div class="info-label">ID NHÂN VẬT</div><div class="info-value">🆔 {d["ID nhân vật"]}</div></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="info-box"><div class="info-label">SỨC MẠNH</div><div class="info-value">⚡ {int(d["Sức Mạnh"]):,}</div></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="info-box"><div class="info-label">KỶ LỤC POW</div><div class="info-value">🏆 {int(d["Kỷ Lực Sức Mạnh"]):,}</div></div>', unsafe_allow_html=True)
            c4.markdown(f'<div class="info-box"><div class="info-label">TÀI NGUYÊN</div><div class="info-value">📦 {int(d["Tài Nguyên Thu Thập"]):,}</div></div>', unsafe_allow_html=True)

            # NHÓM 2: CHỈ SỐ TIÊU DIỆT (Ô BOX)
            st.write("**⚔️ CHỈ SỐ TIÊU DIỆT**")
            k1, k2, k3, k4 = st.columns(4)
            k1.markdown(f'<div class="info-box"><div class="info-label">TỔNG ĐIỂM KILL</div><div class="info-value">🔥 {int(d["Tổng Điểm Tiêu Diệt"]):,}</div></div>', unsafe_allow_html=True)
            k2.markdown(f'<div class="info-box"><div class="info-label">KILL T5/T4</div><div class="info-value">🎖️ {int(d["Tổng Tiêu Diệt T5"]):,}/{int(d["Tổng Tiêu Diệt T4"]):,}</div></div>', unsafe_allow_html=True)
            k3.markdown(f'<div class="info-box"><div class="info-label">KILL T3/T2</div><div class="info-value">⚔️ {int(d["Tổng Tiêu Diệt T3"]):,}/{int(d["Tổng Tiêu Diệt T2"]):,}</div></div>', unsafe_allow_html=True)
            k4.markdown(f'<div class="info-box"><div class="info-label">HỖ TRỢ LIÊN MINH</div><div class="info-value">🤝 {int(d["Hỗ Trợ Liên Minh"]):,}</div></div>', unsafe_allow_html=True)

            # NHÓM 3: CHỈ SỐ TỬ VONG (Ô BOX)
            st.write("**🩸 CHỈ SỐ TỬ VONG (TRỌNG SỐ ĐIỂM)**")
            d1, d2, d3, d4, d5 = st.columns(5)
            d1.markdown(f'<div class="info-box"><div class="info-label">T5 DEAD (x10)</div><div class="info-value">💀 {int(d["T5 tử vong"]):,}</div></div>', unsafe_allow_html=True)
            d2.markdown(f'<div class="info-box"><div class="info-label">T4 DEAD (x4)</div><div class="info-value">💀 {int(d["T4 tử vong"]):,}</div></div>', unsafe_allow_html=True)
            d3.markdown(f'<div class="info-box"><div class="info-label">T3 DEAD (x3)</div><div class="info-value">💀 {int(d["T3 tử vong"]):,}</div></div>', unsafe_allow_html=True)
            d4.markdown(f'<div class="info-box"><div class="info-label">T2 DEAD (x2)</div><div class="info-value">💀 {int(d["T2 tử vong"]):,}</div></div>', unsafe_allow_html=True)
            d5.markdown(f'<div class="info-box"><div class="info-label">T1 DEAD (x1)</div><div class="info-value">💀 {int(d["T1 tử vong"]):,}</div></div>', unsafe_allow_html=True)

            # --- VÒNG TRÒN KPI (KHÔNG GIỚI HẠN) ---
            st.write("---")
            ck1, ck2 = st.columns(2)
            with ck1:
                fig_k = go.Figure(go.Indicator(
                    mode = "gauge+number", value = d['Tổng Điểm Tiêu Diệt'],
                    title = {'text': "TIẾN ĐỘ TIÊU DIỆT", 'font': {'color': '#58a6ff'}},
                    gauge = {'axis': {'range': [0, df['Tổng Điểm Tiêu Diệt'].max()*1.1]}, 'bar': {'color': "#58a6ff"}}
                ))
                st.plotly_chart(fig_k, use_container_width=True)
            
            with ck2:
                fig_d = go.Figure(go.Indicator(
                    mode = "gauge+number", value = d['DEAD_POWER_SCORE'],
                    title = {'text': "TIẾN ĐỘ TỬ VONG (POWER)", 'font': {'color': '#ff4b4b'}},
                    gauge = {'axis': {'range': [0, df['DEAD_POWER_SCORE'].max()*1.1]}, 'bar': {'color': "#ff4b4b"}}
                ))
                st.plotly_chart(fig_d, use_container_width=True)

    with tab2:
        st.subheader("🏆 BẢNG XẾP HẠNG CHIẾN DỊCH")
        # Hiển thị bảng với cột TOTAL_KPI ở cuối cùng
        view_df = df[['RANK', 'ID nhân vật', 'Tên Người Dùng', 'Sức Mạnh', 'Tổng Điểm Tiêu Diệt', 'DEAD_POWER_SCORE', 'Tài Nguyên Thu Thập', 'TOTAL_KPI']]
        st.dataframe(
            view_df.style.format({
                'Sức Mạnh': '{:,.0f}',
                'Tổng Điểm Tiêu Diệt': '{:,.0f}',
                'DEAD_POWER_SCORE': '{:,.0f}',
                'Tài Nguyên Thu Thập': '{:,.0f}',
                'TOTAL_KPI': '{:,.0f}'
            }),
            use_container_width=True, height=600
        )
