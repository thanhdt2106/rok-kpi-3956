import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide")

# --- 2. GIAO DIỆN CSS (DARK MODE) ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .main-header {
        color: #58a6ff; text-align: center; font-size: 28px; font-weight: bold;
        padding: 10px; border-bottom: 1px solid #30363d; margin-bottom: 20px;
    }
    .stat-box {
        background: #161b22; border: 1px solid #30363d; border-radius: 10px;
        padding: 15px; text-align: center; height: 100%;
    }
    .stat-label { color: #8b949e; font-size: 13px; font-weight: bold; text-transform: uppercase; }
    .stat-value { color: #ffffff; font-size: 22px; font-weight: bold; margin-top: 8px; }
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
        df.columns = [str(c).strip() for c in df.columns]
        
        # Danh sách cột cần chuyển sang số
        numeric_cols = ['Sức Mạnh', 'T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 
                        'Tổng Điểm Tiêu Diệt', 'Tài Nguyên Thu Thập', 'Tổng Tiêu Diệt T5', 
                        'Tổng Tiêu Diệt T4', 'Tổng Tiêu Diệt T3', 'Tổng Tiêu Diệt T2', 'Hỗ Trợ Liên Minh']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # A. TÍNH ĐIỂM DEAD THEO TRỌNG SỐ POWER (Yêu cầu mới)
        # T5=10, T4=4, T3-T2=1
        df['DEAD_KPI_SCORE'] = (df['T5 tử vong'] * 10) + (df['T4 tử vong'] * 4) + \
                               (df['T3 tử vong'] * 1) + (df['T2 tử vong'] * 1)
        
        # B. TÍNH KPI TỔNG ĐỂ XẾP HẠNG (Kill + Dead Power)
        df['TOTAL_KPI'] = df['Tổng Điểm Tiêu Diệt'] + df['DEAD_KPI_SCORE']
        
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
        sel = st.selectbox("🔍 CHỌN CHIẾN BINH:", df['Tên Người Dùng'].unique())
        if sel:
            d = df[df['Tên Người Dùng'] == sel].iloc[0]
            
            # --- ROW 1: CÁC Ô CHỈ SỐ (BOX) ---
            st.markdown(f"### 🎖️ {sel} (RANK #{int(d['RANK'])})")
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                st.markdown(f'<div class="stat-box"><div class="stat-label">ID</div><div class="stat-value">🆔 {d["ID nhân vật"]}</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="stat-box"><div class="stat-label">SỨC MẠNH</div><div class="stat-value">⚡ {int(d["Sức Mạnh"]):,}</div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="stat-box"><div class="stat-label">KILL (+)</div><div class="stat-value">⚔️ {int(d["Tổng Điểm Tiêu Diệt"]):,}</div></div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<div class="stat-box"><div class="stat-label">DEAD (POWER)</div><div class="stat-value">🩸 {int(d["DEAD_KPI_SCORE"]):,}</div></div>', unsafe_allow_html=True)
            with c5:
                st.markdown(f'<div class="stat-box"><div class="stat-label">TÀI NGUYÊN</div><div class="stat-value">📦 {int(d["Tài Nguyên Thu Thập"]):,}</div></div>', unsafe_allow_html=True)

            # --- ROW 2: VÒNG TRÒN TIẾN ĐỘ ---
            st.write("")
            ck1, ck2 = st.columns(2)
            with ck1:
                fig_k = go.Figure(go.Indicator(
                    mode = "gauge+number", value = d['Tổng Điểm Tiêu Diệt'],
                    title = {'text': "TIẾN ĐỘ TIÊU DIỆT", 'font': {'color': '#58a6ff'}},
                    gauge = {'axis': {'range': [0, df['Tổng Điểm Tiêu Diệt'].max()]}, 'bar': {'color': "#58a6ff"}}
                ))
                fig_k.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=300)
                st.plotly_chart(fig_k, use_container_width=True)
            
            with ck2:
                fig_d = go.Figure(go.Indicator(
                    mode = "gauge+number", value = d['DEAD_KPI_SCORE'],
                    title = {'text': "TIẾN ĐỘ TỬ VONG (POWER)", 'font': {'color': '#ff4b4b'}},
                    gauge = {'axis': {'range': [0, df['DEAD_KPI_SCORE'].max()]}, 'bar': {'color': "#ff4b4b"}}
                ))
                fig_d.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=300)
                st.plotly_chart(fig_d, use_container_width=True)

            # --- ROW 3: ĐẦY ĐỦ TẤT CẢ CỘT ---
            with st.expander("📝 CHI TIẾT TẤT CẢ CHỈ SỐ TỪ SHEET"):
                # Hiển thị tất cả các cột của dòng đó
                st.table(d.to_frame().T)

    with tab2:
        st.subheader("🏆 BẢNG XẾP HẠNG KPI TỔNG")
        # Chỉ lấy các cột cần thiết để bảng gọn gàng
        view_df = df[['RANK', 'ID nhân vật', 'Tên Người Dùng', 'Sức Mạnh', 'Tổng Điểm Tiêu Diệt', 'DEAD_KPI_SCORE', 'TOTAL_KPI', 'Tài Nguyên Thu Thập']]
        
        # Định dạng hiển thị số cho đẹp mà không dùng background_gradient (để tránh lỗi matplotlib)
        st.dataframe(
            view_df.style.format({
                'Sức Mạnh': '{:,.0f}',
                'Tổng Điểm Tiêu Diệt': '{:,.0f}',
                'DEAD_KPI_SCORE': '{:,.0f}',
                'TOTAL_KPI': '{:,.0f}',
                'Tài Nguyên Thu Thập': '{:,.0f}'
            }),
            use_container_width=True, height=600
        )
