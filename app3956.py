import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide")

# --- 2. CSS CUSTOM ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .main-header { color: #00FFFF; text-align: center; font-size: 30px; font-weight: bold; padding: 10px; border-bottom: 2px solid #58a6ff; margin-bottom: 20px; }
    .info-box { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 10px; text-align: center; margin-bottom: 5px; }
    .info-label { color: #8b949e; font-size: 11px; font-weight: bold; }
    .info-value { color: #ffffff; font-size: 14px; font-weight: bold; }
    .target-footer { color: #58a6ff; font-size: 16px; font-weight: bold; text-align: center; margin-top: -20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC TÍNH TOÁN ---
def get_targets(pow_val):
    p_mil = pow_val / 1_000_000
    if p_mil < 15: return 100_000_000, 200_000
    elif p_mil < 20: return 200_000_000, 250_000
    elif p_mil < 30: return 250_000_000, 300_000
    else: return 300_000_000, 400_000

# --- 4. DATA ENGINE ---
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

# --- 5. GIAO DIỆN ---
res = load_and_process()
if res:
    df, c_name, c_kyluc, c_kill = res
    st.markdown('<div class="main-header">SHARED HOUSE 3956 - KPI MANAGEMENT</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👤 PROFILE CHI TIẾT", "📊 TỔNG QUAN QUÂN ĐOÀN", "🏆 BẢNG VINH DANH (>100%)"])
    
    # --- TAB 1: PROFILE ---
    with tab1:
        sel = st.selectbox("🔍 CHỌN CHIẾN BINH:", df[c_name].unique())
        if sel:
            d = df[df[c_name] == sel].iloc[0]
            
            # Hiển thị tất cả các cột từ Sheet dưới dạng thẻ nhỏ
            st.write("📌 **THÔNG SỐ CHI TIẾT TỪ SHEET**")
            cols = st.columns(6)
            for i, column in enumerate(df.columns[1:13]): # Lấy 12 cột đầu tiên để hiển thị thẻ
                with cols[i % 6]:
                    val = f"{int(d[column]):,}" if isinstance(d[column], (int, float)) else d[column]
                    st.markdown(f'<div class="info-box"><div class="info-label">{column}</div><div class="info-value">{val}</div></div>', unsafe_allow_html=True)

            # Đồ thị KPI
            st.write("---")
            g1, g2 = st.columns(2)
            with g1:
                fig_k = go.Figure(go.Indicator(mode="gauge+number", value=d['K_PCT'], number={'suffix':"%"},
                                              gauge={'axis':{'range':[0, 100]}, 'bar':{'color':"#00FFFF"}}))
                fig_k.update_layout(height=300, margin=dict(t=0, b=0))
                st.plotly_chart(fig_k, use_container_width=True)
                st.markdown(f'<div class="target-footer">KILL: {int(d[c_kill])/1_000_000:.1f}M / {int(d["T_KILL"])/1_000_000:.1f}M</div>', unsafe_allow_html=True)
            
            with g2:
                fig_d = go.Figure(go.Indicator(mode="gauge+number", value=d['D_PCT'], number={'suffix':"%"},
                                              gauge={'axis':{'range':[0, 100]}, 'bar':{'color':"#f29b05"}}))
                fig_d.update_layout(height=300, margin=dict(t=0, b=0))
                st.plotly_chart(fig_d, use_container_width=True)
                st.markdown(f'<div class="target-footer">DEAD: {int(d["SUM_DEAD"]):,} / {int(d["T_DEAD"]):,}</div>', unsafe_allow_html=True)

    # --- TAB 2: TỔNG QUAN ---
    with tab2:
        st.subheader("📋 DANH SÁCH TỔNG HỢP")
        show_df = df[['RANK', c_name, c_kyluc, c_kill, 'SUM_DEAD', 'TOTAL_KPI_SCORE']]
        st.dataframe(show_df.style.format({'TOTAL_KPI_SCORE': '{:.1f}%', c_kyluc: '{:,.0f}', c_kill: '{:,.0f}', 'SUM_DEAD': '{:,.0f}'}), 
                     use_container_width=True, height=500)

    # --- TAB 3: VINH DANH ---
    with tab3:
        st.subheader("🔥 CHIẾN BINH XUẤT SẮC (KPI > 100%)")
        vinh_danh = df[df['TOTAL_KPI_SCORE'] >= 100][['RANK', c_name, 'K_PCT', 'D_PCT', 'TOTAL_KPI_SCORE']]
        if not vinh_danh.empty:
            st.balloons()
            st.table(vinh_danh.style.format({'K_PCT': '{:.1f}%', 'D_PCT': '{:.1f}%', 'TOTAL_KPI_SCORE': '{:.1f}%'}))
        else:
            st.info("Chưa có thành viên nào đạt trên 100% KPI.")
