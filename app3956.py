import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="ROK KPI SYSTEM", layout="wide")

# --- 2. GIAO DIỆN CSS (DARK MODE & NEON) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e6ed; }
    .main-header {
        color: #ff4b4b; text-align: center; font-size: 30px; font-weight: bold;
        padding: 10px; text-transform: uppercase; border-bottom: 2px solid #ff4b4b;
    }
    .profile-card {
        background: #1a1c23; border: 1px solid #30363d; border-radius: 10px;
        padding: 20px; margin-bottom: 15px;
    }
    .stat-box {
        background: #21262d; border-radius: 8px; padding: 15px;
        text-align: center; border: 1px solid #30363d;
    }
    .stat-label { color: #8b949e; font-size: 12px; margin-bottom: 5px; }
    .stat-value { color: #58a6ff; font-size: 18px; font-weight: bold; }
    .stat-delta { color: #3fb950; font-size: 12px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. XỬ LÝ DỮ LIỆU ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
GID = '351056493'
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}'

@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(URL)
        df.columns = [str(c).strip() for c in df.columns]
        
        # Xử lý các cột số quan trọng
        numeric_cols = ['Sức Mạnh', 'T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 
                        'Tổng Điểm Tiêu Diệt', 'Tài Nguyên Thu Thập']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 1. TÍNH ĐIỂM DEAD THEO TRỌNG SỐ (T5=10, T4=4, T3/T2=1)
        df['DEAD_SCORE'] = (df['T5 tử vong'] * 10) + (df['T4 tử vong'] * 4) + \
                           (df['T3 tử vong'] * 1) + (df['T2 tử vong'] * 1)
        
        # 2. TÍNH KPI TỔNG (Dùng để xếp hạng)
        # KPI = Tổng điểm tiêu diệt + Điểm Dead quy đổi
        df['KPI_SCORE'] = df['Tổng Điểm Tiêu Diệt'] + df['DEAD_SCORE']
        
        # 3. SẮP XẾP VÀ LẤY RANK
        df = df.sort_values(by='KPI_SCORE', ascending=False).reset_index(drop=True)
        df.insert(0, 'RANK', df.index + 1)
        
        return df
    except Exception as e:
        st.error(f"Lỗi nạp dữ liệu: {e}")
        return None

df = load_data()

# --- 4. HIỂN THỊ ---
if df is not None:
    tab1, tab2 = st.tabs(["👤 HỒ SƠ CHI TIẾT", "🏆 BẢNG XẾP HẠNG"])
    
    with tab1:
        names = sorted(df['Tên Người Dùng'].unique())
        sel = st.selectbox("🔍 Tìm kiếm chiến binh:", names)
        
        if sel:
            d = df[df['Tên Người Dùng'] == sel].iloc[0]
            
            st.markdown(f"### 🛡️ CHIẾN BINH: {sel} - RANK #{int(d['RANK'])}")
            
            # Row 1: Các chỉ số chính (Dạng Box)
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f'<div class="stat-box"><div class="stat-label">ID</div><div class="stat-value">🆔 {d["ID nhân vật"]}</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="stat-box"><div class="stat-label">SỨC MẠNH</div><div class="stat-value">⚡ {int(d["Sức Mạnh"]):,}</div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="stat-box"><div class="stat-label">KILL (+)</div><div class="stat-value">⚔️ {int(d["Tổng Điểm Tiêu Diệt"]):,}</div></div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<div class="stat-box"><div class="stat-label">TÀI NGUYÊN</div><div class="stat-value">📦 {int(d["Tài Nguyên Thu Thập"]):,}</div></div>', unsafe_allow_html=True)

            # Row 2: Vòng tròn KPI
            st.write("---")
            ck1, ck2 = st.columns(2)
            
            with ck1:
                # Gauge Kill (Dựa trên max của liên minh để tính tiến độ)
                max_kill = df['Tổng Điểm Tiêu Diệt'].max() if df['Tổng Điểm Tiêu Diệt'].max() > 0 else 100
                fig_k = go.Figure(go.Indicator(
                    mode = "gauge+number", value = d['Tổng Điểm Tiêu Diệt'],
                    title = {'text': "TIẾN ĐỘ KILL", 'font': {'size': 20, 'color': '#58a6ff'}},
                    gauge = {'axis': {'range': [0, max_kill]}, 'bar': {'color': "#58a6ff"}}
                ))
                fig_k.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=280, margin=dict(t=50, b=0))
                st.plotly_chart(fig_k, use_container_width=True)

            with ck2:
                # Gauge Dead (Dựa trên max Dead Score của liên minh)
                max_dead = df['DEAD_SCORE'].max() if df['DEAD_SCORE'].max() > 0 else 100
                fig_d = go.Figure(go.Indicator(
                    mode = "gauge+number", value = d['DEAD_SCORE'],
                    title = {'text': "TIẾN ĐỘ DEAD (Power)", 'font': {'size': 20, 'color': '#ff4b4b'}},
                    gauge = {'axis': {'range': [0, max_dead]}, 'bar': {'color': "#ff4b4b"}}
                ))
                fig_d.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=280, margin=dict(t=50, b=0))
                st.plotly_chart(fig_d, use_container_width=True)

            # Row 3: Xuất đầy đủ tất cả cột từ Sheet
            with st.expander("📊 XEM TẤT CẢ CHỈ SỐ TỪ SHEET"):
                st.table(d.to_frame().T)

    with tab2:
        st.subheader("🏆 BẢNG VÀNG LIÊN MINH")
        # Fix lỗi hiển thị: Chỉ chọn các cột có tồn tại và đổi tên cho chuẩn
        show_df = df[['RANK', 'ID nhân vật', 'Tên Người Dùng', 'Sức Mạnh', 'Tổng Điểm Tiêu Diệt', 'DEAD_SCORE', 'KPI_SCORE']].copy()
        
        # Định dạng style bảng để không bị lỗi background_gradient
        st.dataframe(
            show_df.style.format({
                'Sức Mạnh': '{:,.0f}',
                'Tổng Điểm Tiêu Diệt': '{:,.0f}',
                'DEAD_SCORE': '{:,.0f}',
                'KPI_SCORE': '{:,.0f}'
            }).background_gradient(subset=['KPI_SCORE'], cmap='YlOrRd'),
            use_container_width=True, height=600
        )
