import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide")

# --- 2. CSS STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .main-header { color: #00FFFF; text-align: center; font-size: 30px; font-weight: bold; padding: 10px; border-bottom: 2px solid #58a6ff; margin-bottom: 20px; }
    .info-box { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 15px; text-align: center; }
    .info-label { color: #8b949e; font-size: 12px; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }
    .info-value { color: #ffffff; font-size: 18px; font-weight: bold; }
    .target-footer { color: #58a6ff; font-size: 15px; font-weight: bold; text-align: center; margin-top: -10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC MỐC KPI ---
def get_targets(pow_val):
    p_mil = pow_val / 1_000_000
    if p_mil < 15: return 100_000_000, 200_000
    elif p_mil < 20: return 200_000_000, 250_000
    elif p_mil < 30: return 250_000_000, 300_000
    else: return 300_000_000, 400_000

# --- 4. DATA ENGINE (KHỚP CHÍNH XÁC TÊN CỘT) ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=351056493'

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(URL)
        # Làm sạch tên cột: loại bỏ khoảng trắng thừa ở đầu/cuối
        df.columns = [str(c).strip() for c in df.columns]
        
        # Định nghĩa các cột mục tiêu chính xác theo ảnh Sheet
        C_NAME = 'Tên Người Dùng'
        C_POW_MAX = 'Kỷ Lực Sức Mạnh'
        C_POW_NOW = 'Sức Mạnh'
        C_KILL = 'Tổng Điểm Tiêu Diệt'
        C_DEAD_LIST = ['T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong']

        # Kiểm tra sự tồn tại của các cột
        missing = [c for c in [C_NAME, C_POW_MAX, C_POW_NOW, C_KILL] if c not in df.columns]
        if missing:
            st.error(f"Thiếu cột: {missing}. Hãy kiểm tra lại tiêu đề trên Google Sheet.")
            return None

        # Chuyển đổi dữ liệu số (xử lý lỗi nếu có chữ trong cột số)
        cols_to_fix = [C_POW_MAX, C_POW_NOW, C_KILL] + [c for c in C_DEAD_LIST if c in df.columns]
        for col in cols_to_fix:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Tính tổng Tử Vong (SUM_DEAD)
        df['SUM_DEAD'] = df[[c for c in C_DEAD_LIST if c in df.columns]].sum(axis=1)

        # Tính KPI
        targets = df[C_POW_MAX].apply(get_targets)
        df['T_KILL'] = [x[0] for x in targets]
        df['T_DEAD'] = [x[1] for x in targets]
        
        # Tránh chia cho 0
        df['K_PCT'] = (df[C_KILL] / df['T_KILL'] * 100).fillna(0).round(1)
        df['D_PCT'] = (df['SUM_DEAD'] / df['T_DEAD'] * 100).fillna(0).round(1)
        df['TOTAL_KPI'] = ((df['K_PCT'] + df['D_PCT']) / 2).round(1)
        
        # Xếp hạng
        df = df.sort_values(by='TOTAL_KPI', ascending=False).reset_index(drop=True)
        df.insert(0, 'RANK', df.index + 1)
        
        return df, C_NAME, C_POW_MAX, C_POW_NOW, C_KILL
    except Exception as e:
        st.error(f"Lỗi hệ thống: {str(e)}")
        return None

# --- 5. HIỂN THỊ ---
res = load_data()
if res:
    df, C_NAME, C_POW_MAX, C_POW_NOW, C_KILL = res
    st.markdown('<div class="main-header">SHARED HOUSE 3956 KPI</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👤 HỒ SƠ", "📊 TỔNG QUAN", "🏆 VINH DANH"])
    
    with tab1:
        sel = st.selectbox("🔍 CHỌN CHIẾN BINH:", df[C_NAME].unique())
        if sel:
            d = df[df[C_NAME] == sel].iloc[0]
            
            # Chỉ số chính
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.markdown(f'<div class="info-box"><div class="info-label">🏆 RANK</div><div class="info-value">#{int(d["RANK"])}</div></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="info-box"><div class="info-label">💪 POW HIỆN TẠI</div><div class="info-value">{int(d[C_POW_NOW]):,}</div></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="info-box"><div class="info-label">🔥 TỔNG KILL</div><div class="info-value">{int(d[C_KILL]):,}</div></div>', unsafe_allow_html=True)
            with c4: st.markdown(f'<div class="info-box"><div class="info-label">💀 TỔNG DEAD</div><div class="info-value">{int(d["SUM_DEAD"]):,}</div></div>', unsafe_allow_html=True)

            st.write("---")
            
            # Biểu đồ KPI
            k1, k2 = st.columns(2)
            with k1:
                fig_k = go.Figure(go.Indicator(
                    mode="gauge+number", value=d['K_PCT'], number={'suffix': "%"},
                    title={'text': "KPI TIÊU DIỆT", 'font': {'size': 16, 'color': '#00FFFF'}},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00FFFF"}}))
                fig_k.update_layout(height=280, margin=dict(t=50, b=20, l=30, r=30), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_k, use_container_width=True)
                st.markdown(f'<div class="target-footer">Mục tiêu: {int(d["T_KILL"]):,}</div>', unsafe_allow_html=True)
            
            with k2:
                fig_d = go.Figure(go.Indicator(
                    mode="gauge+number", value=d['D_PCT'], number={'suffix': "%"},
                    title={'text': "KPI TỬ VONG", 'font': {'size': 16, 'color': '#f29b05'}},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#f29b05"}}))
                fig_d.update_layout(height=280, margin=dict(t=50, b=20, l=30, r=30), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_d, use_container_width=True)
                st.markdown(f'<div class="target-footer">Mục tiêu: {int(d["T_DEAD"]):,}</div>', unsafe_allow_html=True)

    with tab2:
        st.subheader("📋 DANH SÁCH CHI TIẾT")
        view_df = df[['RANK', C_NAME, C_POW_NOW, C_KILL, 'SUM_DEAD', 'TOTAL_KPI']]
        st.dataframe(view_df.style.format({C_POW_NOW: "{:,}", C_KILL: "{:,}", 'SUM_DEAD': "{:,}"}), use_container_width=True, height=500)

    with tab3:
        winners = df[df['TOTAL_KPI'] >= 100][['RANK', C_NAME, 'TOTAL_KPI']]
        if not winners.empty:
            st.balloons()
            st.table(winners)
        else:
            st.info("Chưa có chiến binh nào đạt >100% KPI.")
