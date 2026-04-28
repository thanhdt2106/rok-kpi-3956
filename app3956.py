import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH ---
st.set_page_config(page_title="SHARED HOUSE 3956 KPI", layout="wide")

# --- 2. CSS STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .main-header { color: #00FFFF; text-align: center; font-size: 30px; font-weight: bold; padding: 10px; border-bottom: 2px solid #58a6ff; margin-bottom: 20px; }
    .info-box { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 15px; text-align: center; }
    .info-label { color: #8b949e; font-size: 12px; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }
    .info-value { color: #ffffff; font-size: 18px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC TÍNH TOÁN KPI ---
def get_targets(pow_val):
    p_mil = pow_val / 1_000_000
    if p_mil < 15: return 100_000_000, 200_000
    elif p_mil < 20: return 200_000_000, 250_000
    elif p_mil < 30: return 250_000_000, 300_000
    else: return 300_000_000, 400_000

# --- 4. ENGINE TẢI DỮ LIỆU ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=351056493'

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(URL)
        # Xử lý tên cột: Xóa khoảng trắng thừa và ép về string
        df.columns = [str(c).strip() for c in df.columns]
        
        # Định nghĩa biến tên cột chuẩn theo ảnh bạn gửi
        C_NAME = 'Tên Người Dùng'
        C_POW_MAX = 'Kỷ Lục Sức Mạnh'
        C_POW_NOW = 'Sức Mạnh'
        C_KILL = 'Tổng Điểm Tiêu Diệt'
        C_DEAD_COLS = ['T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong']

        # Kiểm tra cột bắt buộc
        needed = [C_NAME, C_POW_MAX, C_POW_NOW, C_KILL]
        missing = [c for c in needed if c not in df.columns]
        if missing:
            st.error(f"⚠️ Vẫn thiếu cột: {missing}. Hãy kiểm tra lại tiêu đề trên Sheet.")
            return None

        # Chuyển đổi kiểu dữ liệu số
        for col in needed + [c for c in C_DEAD_COLS if c in df.columns]:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Tính toán các chỉ số KPI
        df['SUM_DEAD'] = df[[c for c in C_DEAD_COLS if c in df.columns]].sum(axis=1)
        
        targets = df[C_POW_MAX].apply(get_targets)
        df['T_KILL'] = [x[0] for x in targets]
        df['T_DEAD'] = [x[1] for x in targets]
        
        df['K_PCT'] = (df[C_KILL] / df['T_KILL'] * 100).fillna(0).round(1)
        df['D_PCT'] = (df['SUM_DEAD'] / df['T_DEAD'] * 100).fillna(0).round(1)
        df['TOTAL_KPI'] = ((df['K_PCT'] + df['D_PCT']) / 2).round(1)
        
        # Xếp hạng
        df = df.sort_values(by='TOTAL_KPI', ascending=False).reset_index(drop=True)
        df.insert(0, 'RANK', df.index + 1)
        
        return df, C_NAME, C_POW_MAX, C_POW_NOW, C_KILL
    except Exception as e:
        st.error(f"Lỗi nạp dữ liệu: {e}")
        return None

# --- 5. GIAO DIỆN CHÍNH ---
data_res = load_data()
if data_res:
    df, C_NAME, C_POW_MAX, C_POW_NOW, C_KILL = data_res
    st.markdown('<div class="main-header">SHARED HOUSE 3956 KPI SYSTEM</div>', unsafe_allow_html=True)
    
    sel_user = st.selectbox("🔍 CHỌN CHIẾN BINH:", df[C_NAME].tolist())
    
    if sel_user:
        d = df[df[C_NAME] == sel_user].iloc[0]
        
        # Dashboard thẻ thông tin
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.markdown(f'<div class="info-box"><div class="info-label">RANK</div><div class="info-value">#{int(d["RANK"])}</div></div>', unsafe_allow_html=True)
        with col2: st.markdown(f'<div class="info-box"><div class="info-label">KỶ LỤC POW</div><div class="info-value">{int(d[C_POW_MAX]):,}</div></div>', unsafe_allow_html=True)
        with col3: st.markdown(f'<div class="info-box"><div class="info-label">POW HIỆN TẠI</div><div class="info-value">{int(d[C_POW_NOW]):,}</div></div>', unsafe_allow_html=True)
        with col4: st.markdown(f'<div class="info-box"><div class="info-label">TỔNG DEAD</div><div class="info-value">{int(d["SUM_DEAD"]):,}</div></div>', unsafe_allow_html=True)

        st.write("---")
        
        # Biểu đồ KPI
        g1, g2 = st.columns(2)
        with g1:
            fig_k = go.Figure(go.Indicator(
                mode="gauge+number", value=d['K_PCT'],
                title={'text': f"KPI KILL (Mục tiêu: {int(d['T_KILL']):,})", 'font': {'size': 14}},
                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00FFFF"}}))
            fig_k.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_k, use_container_width=True)
            
        with g2:
            fig_d = go.Figure(go.Indicator(
                mode="gauge+number", value=d['D_PCT'],
                title={'text': f"KPI DEAD (Mục tiêu: {int(d['T_DEAD']):,})", 'font': {'size': 14}},
                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#f29b05"}}))
            fig_d.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_d, use_container_width=True)
