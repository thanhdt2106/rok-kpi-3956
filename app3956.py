import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="SHARED HOUSE 3956 KPI", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CSS CUSTOM (ẨN SIDEBAR & LÀM TO SỐ LIỆU) ---
st.markdown("""
    <style>
    /* Ẩn Sidebar và các thành phần thừa */
    [data-testid="stSidebar"] {display: none;}
    [data-testid="stHeader"] {background: rgba(0,0,0,0);}
    
    /* Nền ứng dụng */
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    
    /* Header chính */
    .main-header { 
        color: #00FFFF; 
        text-align: center; 
        font-size: 40px; 
        font-weight: 800; 
        padding: 20px; 
        text-shadow: 2px 2px 10px #00FFFF55;
    }

    /* Thẻ thông tin (Big Numbers) */
    .info-card {
        background: linear-gradient(145deg, #161b22, #1c2128);
        border: 1px solid #30363d;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .info-label { 
        color: #8b949e; 
        font-size: 16px; 
        font-weight: bold; 
        text-transform: uppercase; 
        letter-spacing: 1px;
    }
    .info-value { 
        color: #ffffff; 
        font-size: 32px; 
        font-weight: 800; 
        margin-top: 10px;
    }
    .rank-value { color: #f29b05; font-size: 40px; }
    
    /* Footer mục tiêu */
    .target-footer { 
        background: #161b22;
        padding: 10px;
        border-radius: 8px;
        color: #58a6ff; 
        font-size: 20px; 
        font-weight: bold; 
        text-align: center; 
        margin-top: -30px;
        border: 1px dashed #30363d;
    }
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
        df.columns = [str(c).strip() for c in df.columns]
        
        # Tìm cột thông minh
        def find_col(keywords):
            for col in df.columns:
                if any(k.lower() in col.lower() for k in keywords): return col
            return None

        C_NAME = find_col(['Tên Người Dùng', 'User'])
        C_POW_MAX = find_col(['Kỷ Lực', 'Max Power'])
        C_POW_NOW = find_col(['Sức Mạnh', 'Current Power'])
        C_KILL = find_col(['Tổng Điểm Tiêu Diệt', 'Total Kill'])
        C_DEAD_LIST = [c for c in df.columns if 'tử vong' in c.lower()]

        # Ép kiểu số
        numeric_cols = [C_POW_MAX, C_POW_NOW, C_KILL] + C_DEAD_LIST
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Tính toán
        df['SUM_DEAD'] = df[C_DEAD_LIST].sum(axis=1)
        targets = df[C_POW_MAX].apply(get_targets)
        df['T_KILL'] = [x[0] for x in targets]
        df['T_DEAD'] = [x[1] for x in targets]
        
        df['K_PCT'] = (df[C_KILL] / df['T_KILL'] * 100).fillna(0).round(1)
        df['D_PCT'] = (df['SUM_DEAD'] / df['T_DEAD'] * 100).fillna(0).round(1)
        df['TOTAL_KPI'] = ((df['K_PCT'] + df['D_PCT']) / 2).round(1)
        
        df = df.sort_values(by='TOTAL_KPI', ascending=False).reset_index(drop=True)
        df.insert(0, 'RANK', df.index + 1)
        
        return df, C_NAME, C_POW_MAX, C_POW_NOW, C_KILL
    except Exception as e:
        st.error(f"Lỗi: {e}")
        return None

# --- 5. GIAO DIỆN CHÍNH ---
res = load_data()
if res:
    df, C_NAME, C_POW_MAX, C_POW_NOW, C_KILL = res
    st.markdown('<div class="main-header">SHARED HOUSE 3956 KPI SYSTEM</div>', unsafe_allow_html=True)
    
    # Khu vực chọn chiến binh (To và rõ)
    selected_user = st.selectbox("🔍 CHỌN CHIẾN BINH ĐỂ XEM CHI TIẾT:", df[C_NAME].tolist(), index=0)
    
    if selected_user:
        d = df[df[C_NAME] == selected_user].iloc[0]
        st.write("") 
        
        # --- HÀNG 1: CÁC CON SỐ KHỔNG LỒ ---
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'''<div class="info-card">
                <div class="info-label">🏆 XẾP HẠNG</div>
                <div class="info-value rank-value">#{int(d["RANK"])}</div>
            </div>''', unsafe_allow_html=True)
        with c2:
            st.markdown(f'''<div class="info-card">
                <div class="info-label">⭐ KỶ LỤC POW</div>
                <div class="info-value">{int(d[C_POW_MAX]):,}</div>
            </div>''', unsafe_allow_html=True)
        with c3:
            st.markdown(f'''<div class="info-card">
                <div class="info-label">💪 POW HIỆN TẠI</div>
                <div class="info-value">{int(d[C_POW_NOW]):,}</div>
            </div>''', unsafe_allow_html=True)
        with c4:
            st.markdown(f'''<div class="info-card">
                <div class="info-label">💀 TỔNG TỬ VONG</div>
                <div class="info-value">{int(d["SUM_DEAD"]):,}</div>
            </div>''', unsafe_allow_html=True)

        st.write("---")
        
        # --- HÀNG 2: BIỂU ĐỒ KPI ---
        g1, g2 = st.columns(2)
        with g1:
            fig_k = go.Figure(go.Indicator(
                mode="gauge+number", value=d['K_PCT'], number={'suffix': "%", 'font': {'size': 60}},
                title={'text': "KPI TIÊU DIỆT", 'font': {'size': 24, 'color': '#00FFFF'}},
                gauge={'axis': {'range': [0, 100], 'tickwidth': 1}, 
                       'bar': {'color': "#00FFFF"},
                       'steps': [{'range': [0, 50], 'color': '#161b22'}, {'range': [50, 100], 'color': '#1c2128'}]}))
            fig_k.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", font={'color': "white", 'family': "Arial"})
            st.plotly_chart(fig_k, use_container_width=True)
            st.markdown(f'<div class="target-footer">MỤC TIÊU: {int(d["T_KILL"]):,} KILL</div>', unsafe_allow_html=True)
            
        with g2:
            fig_d = go.Figure(go.Indicator(
                mode="gauge+number", value=d['D_PCT'], number={'suffix': "%", 'font': {'size': 60}},
                title={'text': "KPI TỬ VONG", 'font': {'size': 24, 'color': '#f29b05'}},
                gauge={'axis': {'range': [0, 100], 'tickwidth': 1}, 
                       'bar': {'color': "#f29b05"},
                       'steps': [{'range': [0, 50], 'color': '#161b22'}, {'range': [50, 100], 'color': '#1c2128'}]}))
            fig_d.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", font={'color': "white", 'family': "Arial"})
            st.plotly_chart(fig_d, use_container_width=True)
            st.markdown(f'<div class="target-footer">MỤC TIÊU: {int(d["T_DEAD"]):,} DEAD</div>', unsafe_allow_html=True)

    # --- BẢNG XẾP HẠNG (EXPANDER) ---
    st.write("")
    with st.expander("📊 XEM TOÀN BỘ BẢNG XẾP HẠNG QUÂN ĐOÀN"):
        st.dataframe(
            df[['RANK', C_NAME, C_POW_NOW, C_KILL, 'SUM_DEAD', 'TOTAL_KPI']], 
            use_container_width=True,
            height=400
        )
