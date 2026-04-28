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
    .info-box { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 10px; text-align: center; margin-bottom: 5px; }
    .info-label { color: #8b949e; font-size: 11px; font-weight: bold; text-transform: uppercase; }
    .info-value { color: #ffffff; font-size: 14px; font-weight: bold; }
    .target-footer { color: #58a6ff; font-size: 16px; font-weight: bold; text-align: center; margin-top: -10px; padding-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC MỐC KPI ---
def get_targets(pow_val):
    p_mil = pow_val / 1_000_000
    if p_mil < 15: return 100_000_000, 200_000
    elif p_mil < 20: return 200_000_000, 250_000
    elif p_mil < 30: return 250_000_000, 300_000
    else: return 300_000_000, 400_000

# --- 4. DATA ENGINE ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=351056493'

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(URL)
        # Làm sạch tên cột: xóa khoảng trắng, xóa xuống dòng
        df.columns = [str(c).replace('\\n', ' ').replace('\n', ' ').strip() for c in df.columns]
        
        # Hàm tìm cột không sợ sai tên chính xác
        def find_col(keywords):
            for c in df.columns:
                if any(k.lower() in c.lower() for k in keywords): return c
            return None

        c_name = find_col(['Tên Người Dùng', 'Tên'])
        c_kyluc = find_col(['Kỷ Lực Sức Mạnh', 'Kỷ Lực'])
        c_kill = find_col(['Tổng Điểm Tiêu Diệt', 'Tổng Tiêu'])

        if not c_kyluc or not c_kill:
            st.error("Không tìm thấy cột 'Kỷ Lực' hoặc 'Tiêu Diệt'. Kiểm tra lại tên cột trên Google Sheet!")
            return None

        # Chuyển đổi dữ liệu số
        for col in df.columns:
            if col != c_name:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Tính Dead Units
        dead_cols = ['T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong']
        df['SUM_DEAD'] = df[[c for c in dead_cols if c in df.columns]].sum(axis=1)

        # Tính KPI
        targets = df[c_kyluc].apply(get_targets)
        df['T_KILL'] = [x[0] for x in targets]
        df['T_DEAD'] = [x[1] for x in targets]
        df['K_PCT'] = (df[c_kill] / df['T_KILL'] * 100).round(1)
        df['D_PCT'] = (df['SUM_DEAD'] / df['T_DEAD'] * 100).round(1)
        df['TOTAL_KPI'] = ((df['K_PCT'] + df['D_PCT']) / 2).round(1)
        
        # Sắp xếp Rank
        df = df.sort_values(by='TOTAL_KPI', ascending=False).reset_index(drop=True)
        df.insert(0, 'RANK', df.index + 1)
        
        return df, c_name, c_kyluc, c_kill
    except Exception as e:
        st.error(f"Lỗi nạp dữ liệu: {e}")
        return None

# --- 5. HIỂN THỊ ---
res = load_data()
if res:
    df, c_name, c_kyluc, c_kill = res
    st.markdown('<div class="main-header">SHARED HOUSE 3956 KPI</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👤 HỒ SƠ", "📊 TỔNG QUAN", "🏆 VINH DANH"])
    
    with tab1:
        sel = st.selectbox("🔍 CHỌN CHIẾN BINH:", df[c_name].unique())
        if sel:
            d = df[df[c_name] == sel].iloc[0]
            
            # Thông số chi tiết
            with st.expander("📊 THÔNG SỐ TỪ SHEET", expanded=True):
                cols = st.columns(5)
                # Chỉ hiện các cột gốc từ Sheet
                display_cols = [c for c in df.columns if c not in ['RANK', 'T_KILL', 'T_DEAD', 'K_PCT', 'D_PCT', 'TOTAL_KPI', 'SUM_DEAD']]
                for i, col in enumerate(display_cols):
                    with cols[i % 5]:
                        val = f"{int(d[col]):,}" if isinstance(d[col], (int, float)) else d[col]
                        st.markdown(f'<div class="info-box"><div class="info-label">{col}</div><div class="info-value">{val}</div></div>', unsafe_allow_html=True)

            # Biểu đồ KPI
            st.write("---")
            k1, k2 = st.columns(2)
            with k1:
                fig_k = go.Figure(go.Indicator(mode="gauge+number", value=d['K_PCT'], number={'suffix': "%"},
                                              title={'text': "KPI TIÊU DIỆT", 'font': {'size': 15}},
                                              gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00FFFF"}}))
                fig_k.update_layout(height=250, margin=dict(t=50, b=0), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_k, use_container_width=True)
                st.markdown(f'<div class="target-footer">Thực tế: {int(d[c_kill]):,}<br>Mục tiêu: {int(d["T_KILL"]):,}</div>', unsafe_allow_html=True)
            
            with k2:
                fig_d = go.Figure(go.Indicator(mode="gauge+number", value=d['D_PCT'], number={'suffix': "%"},
                                              title={'text': "KPI TỬ VONG", 'font': {'size': 15}},
                                              gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#f29b05"}}))
                fig_d.update_layout(height=250, margin=dict(t=50, b=0), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_d, use_container_width=True)
                st.markdown(f'<div class="target-footer">Thực tế: {int(d["SUM_DEAD"]):,}<br>Mục tiêu: {int(d["T_DEAD"]):,}</div>', unsafe_allow_html=True)

    with tab2:
        st.subheader("📋 BẢNG XẾP HẠNG QUÂN ĐOÀN")
        # Dùng st.dataframe thuần túy để không bị lỗi ImportError
        st.dataframe(df[['RANK', c_name, c_kyluc, c_kill, 'SUM_DEAD', 'TOTAL_KPI']], use_container_width=True, height=500)

    with tab3:
        st.subheader("🔥 CHIẾN BINH HOÀN THÀNH >100% KPI")
        winners = df[df['TOTAL_KPI'] >= 100][['RANK', c_name, 'TOTAL_KPI']]
        if not winners.empty:
            st.balloons()
            st.table(winners)
        else:
            st.info("Chưa có ai đạt mốc 100%.")
