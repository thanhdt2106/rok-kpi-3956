import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CSS CUSTOM (XOÁ SIDEBAR & PHÓNG TO SỐ LIỆU) ---
st.markdown("""
    <style>
    /* Ẩn Sidebar gốc */
    [data-testid="stSidebar"] {display: none;}
    [data-testid="stHeader"] {background: rgba(0,0,0,0);}
    
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    
    /* Header chính to rõ */
    .main-header { 
        color: #00FFFF; 
        text-align: center; 
        font-size: 40px; 
        font-weight: bold; 
        padding: 15px; 
        border-bottom: 2px solid #58a6ff; 
        margin-bottom: 30px; 
    }

    /* Các thẻ thông tin to khổng lồ */
    .info-box { 
        background: #161b22; 
        border: 2px solid #30363d; 
        border-radius: 15px; 
        padding: 20px; 
        text-align: center; 
        margin-bottom: 10px; 
    }
    .info-label { 
        color: #8b949e; 
        font-size: 16px; 
        font-weight: bold; 
        text-transform: uppercase;
    }
    .info-value { 
        color: #ffffff; 
        font-size: 32px; 
        font-weight: bold; 
        margin-top: 5px;
    }
    
    /* Chỉnh chữ trong Tab to hơn */
    button[data-baseweb="tab"] p {
        font-size: 20px !important;
        font-weight: bold !important;
    }

    /* Mục tiêu to rõ dưới biểu đồ */
    .target-footer { 
        color: #58a6ff; 
        font-size: 20px; 
        font-weight: bold; 
        text-align: center; 
        margin-top: -25px;
        padding: 10px;
        background: rgba(88, 166, 255, 0.1);
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC TÍNH TOÁN (GIỮ NGUYÊN) ---
def get_targets(pow_val):
    p_mil = pow_val / 1_000_000
    if p_mil < 15: return 100_000_000, 200_000
    elif p_mil < 20: return 200_000_000, 250_000
    elif p_mil < 30: return 250_000_000, 300_000
    else: return 300_000_000, 400_000

# --- 4. DATA ENGINE (GIỮ NGUYÊN) ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=351056493'

@st.cache_data(ttl=10)
def load_and_process():
    try:
        df = pd.read_csv(URL)
        df.columns = [str(c).replace('\n', ' ').strip() for c in df.columns]
        
        # Dò cột tự động
        def find_col(keys):
            for c in df.columns:
                if any(k.lower() in c.lower() for k in keys): return c
            return None

        c_name = find_col(['Tên Người Dùng', 'Tên'])
        c_kyluc = find_col(['Kỷ Lục Sức Mạnh', 'Kỷ Lục'])
        c_kill = find_col(['Tổng Điểm Tiêu Diệt', 'Tổng Tiêu'])
        
        # Ép kiểu số
        for col in df.columns:
            if col != c_name:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Tính toán Dead & KPI
        dead_cols = ['T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong']
        df['SUM_DEAD'] = df[dead_cols].sum(axis=1)
        
        targets = df[c_kyluc].apply(get_targets)
        df['T_KILL'] = [x[0] for x in targets]
        df['T_DEAD'] = [x[1] for x in targets]
        
        # Phần trăm và Tổng điểm xếp hạng
        df['K_PCT'] = (df[c_kill] / df['T_KILL'] * 100).clip(upper=200)
        df['D_PCT'] = (df['SUM_DEAD'] / df['T_DEAD'] * 100).clip(upper=200)
        df['TOTAL_KPI_SCORE'] = (df['K_PCT'] + df['D_PCT']) / 2
        
        # Xếp hạng
        df = df.sort_values('TOTAL_KPI_SCORE', ascending=False)
        df.insert(0, 'RANK', range(1, len(df) + 1))
        
        return df, c_name, c_kyluc, c_kill
    except Exception as e:
        st.error(f"Lỗi: {e}")
        return None

# --- 5. GIAO DIỆN (ĐÃ PHÓNG TO) ---
res = load_and_process()
if res:
    df, c_name, c_kyluc, c_kill = res
    st.markdown('<div class="main-header">SHARED HOUSE 3956 - KPI MANAGEMENT</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👤 PROFILE CHI TIẾT", "📊 TỔNG QUAN QUÂN ĐOÀN", "🏆 VINH DANH (>100%)"])
    
    # --- TAB 1: PROFILE ---
    with tab1:
        sel = st.selectbox("🔍 CHỌN CHIẾN BINH:", df[c_name].unique())
        if sel:
            d = df[df[c_name] == sel].iloc[0]
            
            # Hiển thị số liệu chính to hơn
            st.write("")
            c_top1, c_top2, c_top3, c_top4 = st.columns(4)
            with c_top1:
                st.markdown(f'<div class="info-box"><div class="info-label">🏆 RANK</div><div class="info-value" style="color:#f29b05;">#{int(d["RANK"])}</div></div>', unsafe_allow_html=True)
            with c_top2:
                st.markdown(f'<div class="info-box"><div class="info-label">⭐ KỶ LỤC POW</div><div class="info-value">{int(d[c_kyluc]):,}</div></div>', unsafe_allow_html=True)
            with c_top3:
                st.markdown(f'<div class="info-box"><div class="info-label">🔥 TỔNG KILL</div><div class="info-value">{int(d[c_kill]):,}</div></div>', unsafe_allow_html=True)
            with c_top4:
                st.markdown(f'<div class="info-box"><div class="info-label">💀 TỔNG DEAD</div><div class="info-value">{int(d["SUM_DEAD"]):,}</div></div>', unsafe_allow_html=True)

            # Đồ thị KPI phóng to số hiển thị
            st.write("---")
            g1, g2 = st.columns(2)
            with g1:
                fig_k = go.Figure(go.Indicator(mode="gauge+number", value=d['K_PCT'], 
                                              number={'suffix':"%", 'font':{'size': 60}},
                                              gauge={'axis':{'range':[0, 100]}, 'bar':{'color':"#00FFFF"}}))
                fig_k.update_layout(height=400, margin=dict(t=50, b=0), paper_bgcolor="rgba(0,0,0,0)", font={'color':"white"})
                st.plotly_chart(fig_k, use_container_width=True)
                st.markdown(f'<div class="target-footer">MỤC TIÊU KILL: {int(d["T_KILL"]):,}</div>', unsafe_allow_html=True)
            
            with g2:
                fig_d = go.Figure(go.Indicator(mode="gauge+number", value=d['D_PCT'], 
                                              number={'suffix':"%", 'font':{'size': 60}},
                                              gauge={'axis':{'range':[0, 100]}, 'bar':{'color':"#f29b05"}}))
                fig_d.update_layout(height=400, margin=dict(t=50, b=0), paper_bgcolor="rgba(0,0,0,0)", font={'color':"white"})
                st.plotly_chart(fig_d, use_container_width=True)
                st.markdown(f'<div class="target-footer">MỤC TIÊU DEAD: {int(d["T_DEAD"]):,}</div>', unsafe_allow_html=True)

    # --- TAB 2: TỔNG QUAN ---
    with tab2:
        st.subheader("📋 DANH SÁCH TỔNG HỢP")
        show_df = df[['RANK', c_name, c_kyluc, c_kill, 'SUM_DEAD', 'TOTAL_KPI_SCORE']]
        st.dataframe(show_df.style.format({'TOTAL_KPI_SCORE': '{:.1f}%', c_kyluc: '{:,.0f}', c_kill: '{:,.0f}', 'SUM_DEAD': '{:,.0f}'}), 
                     use_container_width=True, height=600)

    # --- TAB 3: VINH DANH ---
    with tab3:
        st.subheader("🔥 CHIẾN BINH XUẤT SẮC (KPI > 100%)")
        vinh_danh = df[df['TOTAL_KPI_SCORE'] >= 100][['RANK', c_name, 'K_PCT', 'D_PCT', 'TOTAL_KPI_SCORE']]
        if not vinh_danh.empty:
            st.balloons()
            st.table(vinh_danh.style.format({'K_PCT': '{:.1f}%', 'D_PCT': '{:.1f}%', 'TOTAL_KPI_SCORE': '{:.1f}%'}))
        else:
            st.info("Chưa có thành viên nào đạt trên 100% KPI.")
