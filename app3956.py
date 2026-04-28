import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide")

# --- 2. GIAO DIỆN CSS (ICON & GRID BOX) ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .main-header {
        color: #58a6ff; text-align: center; font-size: 28px; font-weight: bold;
        padding: 10px; border-bottom: 1px solid #30363d; margin-bottom: 20px;
    }
    .info-box {
        background: #161b22; border: 1px solid #30363d; border-radius: 10px;
        padding: 15px; text-align: center; margin-bottom: 10px; min-height: 100px;
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
        # CHUẨN HÓA CỘT: Xóa khoảng trắng và ký tự lạ
        df.columns = [str(c).strip() for c in df.columns]
        
        # Danh sách cột số liệu cần xử lý
        numeric_cols = [
            'Sức Mạnh', 'Kỷ Lực Sức Mạnh', 'T5 tử vong', 'T4 tử vong', 'T3 tử vong', 
            'T2 tử vong', 'T1 tử vong', 'Tổng Điểm Tiêu Diệt', 'Tổng Tiêu Diệt T5', 
            'Tổng Tiêu Diệt T4', 'Tổng Tiêu Diệt T3', 'Tổng Tiêu Diệt T2', 
            'Tài Nguyên Thu Thập', 'Hỗ Trợ Liên Minh'
        ]
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # TÍNH TOÁN THEO TRỌNG SỐ POW YÊU CẦU
        # T5=10, T4=4, T3=3, T2=2, T1=1
        df['DEAD_POWER_SCORE'] = (df['T5 tử vong'] * 10) + (df['T4 tử vong'] * 4) + \
                                 (df['T3 tử vong'] * 3) + (df['T2 tử vong'] * 2) + \
                                 (df['T1 tử vong'] * 1)
        
        df['TOTAL_KPI'] = df['Tổng Điểm Tiêu Diệt'] + df['DEAD_POWER_SCORE']
        
        # Sắp xếp Rank
        df = df.sort_values(by='TOTAL_KPI', ascending=False).reset_index(drop=True)
        df.insert(0, 'RANK', df.index + 1)
        
        return df
    except Exception as e:
        st.error(f"Lỗi nạp dữ liệu: {e}")
        return None

df = load_data()

# --- 4. HIỂN THỊ ---
if df is not None:
    tab1, tab2 = st.tabs(["👤 HỒ SƠ CHI TIẾT", "📊 BẢNG XẾP HẠNG"])
    
    with tab1:
        sel = st.selectbox("🔍 CHỌN CHIẾN BINH:", df['Tên Người Dùng'].unique())
        if sel:
            # Sử dụng .get() để tránh lỗi KeyError
            d = df[df['Tên Người Dùng'] == sel].iloc[0]
            st.markdown(f"### 🎖️ {sel} (RANK #{int(d['RANK'])})")
            
            # KHỐI 1: CƠ BẢN
            st.write("**📌 THÔNG TIN CƠ BẢN**")
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f'<div class="info-box"><div class="info-label">ID</div><div class="info-value">🆔 {d.get("ID nhân vật", "N/A")}</div></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="info-box"><div class="info-label">SỨC MẠNH</div><div class="info-value">⚡ {int(d.get("Sức Mạnh", 0)):,}</div></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="info-box"><div class="info-label">KỶ LỤC POW</div><div class="info-value">🏆 {int(d.get("Kỷ Lực Sức Mạnh", 0)):,}</div></div>', unsafe_allow_html=True)
            c4.markdown(f'<div class="info-box"><div class="info-label">TÀI NGUYÊN</div><div class="info-value">📦 {int(d.get("Tài Nguyên Thu Thập", 0)):,}</div></div>', unsafe_allow_html=True)

            # KHỐI 2: TỬ VONG (T5-T1)
            st.write("**🩸 CHI TIẾT TỬ VONG (TRỌNG SỐ)**")
            d1, d2, d3, d4, d5 = st.columns(5)
            d1.markdown(f'<div class="info-box"><div class="info-label">T5 (x10)</div><div class="info-value">💀 {int(d.get("T5 tử vong", 0)):,}</div></div>', unsafe_allow_html=True)
            d2.markdown(f'<div class="info-box"><div class="info-label">T4 (x4)</div><div class="info-value">💀 {int(d.get("T4 tử vong", 0)):,}</div></div>', unsafe_allow_html=True)
            d3.markdown(f'<div class="info-box"><div class="info-label">T3 (x3)</div><div class="info-value">💀 {int(d.get("T3 tử vong", 0)):,}</div></div>', unsafe_allow_html=True)
            d4.markdown(f'<div class="info-box"><div class="info-label">T2 (x2)</div><div class="info-value">💀 {int(d.get("T2 tử vong", 0)):,}</div></div>', unsafe_allow_html=True)
            d5.markdown(f'<div class="info-box"><div class="info-label">T1 (x1)</div><div class="info-value">💀 {int(d.get("T1 tử vong", 0)):,}</div></div>', unsafe_allow_html=True)

            # BIỂU ĐỒ KPI VÒNG TRÒN
            st.write("---")
            ck1, ck2 = st.columns(2)
            with ck1:
                fig_k = go.Figure(go.Indicator(mode="gauge+number", value=d['Tổng Điểm Tiêu Diệt'], title={'text': "TIẾN ĐỘ KILL"}, gauge={'axis':{'range':[0, df['Tổng Điểm Tiêu Diệt'].max()*1.1]},'bar':{'color':"#58a6ff"}}))
                st.plotly_chart(fig_k, use_container_width=True)
            with ck2:
                fig_d = go.Figure(go.Indicator(mode="gauge+number", value=d['DEAD_POWER_SCORE'], title={'text': "TIẾN ĐỘ DEAD POW"}, gauge={'axis':{'range':[0, df['DEAD_POWER_SCORE'].max()*1.1]},'bar':{'color':"#ff4b4b"}}))
                st.plotly_chart(fig_d, use_container_width=True)

    with tab2:
        st.subheader("🏆 BẢNG XẾP HẠNG TỔNG")
        view_df = df[['RANK', 'ID nhân vật', 'Tên Người Dùng', 'Sức Mạnh', 'Tổng Điểm Tiêu Diệt', 'DEAD_POWER_SCORE', 'Tài Nguyên Thu Thập', 'TOTAL_KPI']]
        st.dataframe(view_df.style.format({'Sức Mạnh':'{:,.0f}','Tổng Điểm Tiêu Diệt':'{:,.0f}','DEAD_POWER_SCORE':'{:,.0f}','Tài Nguyên Thu Thập':'{:,.0f}','TOTAL_KPI':'{:,.0f}'}), use_container_width=True, height=600)
