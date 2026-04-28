import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide")

# --- 2. GIAO DIỆN CSS TỐI ƯU ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .main-header { color: #00FFFF; text-align: center; font-size: 30px; font-weight: bold; padding: 10px; border-bottom: 2px solid #58a6ff; margin-bottom: 20px; }
    .info-box { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 10px; text-align: center; margin-bottom: 5px; }
    .info-label { color: #8b949e; font-size: 11px; font-weight: bold; text-transform: uppercase; }
    .info-value { color: #ffffff; font-size: 14px; font-weight: bold; }
    .target-footer { color: #58a6ff; font-size: 16px; font-weight: bold; text-align: center; margin-top: -10px; padding-bottom: 20px; }
    .achievement-100 { color: #ff0000; font-weight: bold; }
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

@st.cache_data(ttl=10)
def load_data():
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
        c_kill = find_col(['Tổng Điểm Tiêu Diệt', 'Tổng Điêu'])
        
        # Làm sạch dữ liệu số
        numeric_cols = [c for c in df.columns if c != c_name]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Tính toán chỉ số lính chết (Dead)
        dead_parts = ['T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong']
        df['SUM_DEAD_UNITS'] = df[[c for c in dead_parts if c in df.columns]].sum(axis=1)
        
        # Trọng số Dead Power (Để tính Rank)
        df['DEAD_POWER'] = (df.get('T5 tử vong', 0)*10 + df.get('T4 tử vong', 0)*4 + 
                            df.get('T3 tử vong', 0)*3 + df.get('T2 tử vong', 0)*2 + df.get('T1 tử vong', 0)*1)

        # Gán Target
        targets = df[c_kyluc].apply(get_targets)
        df['T_KILL'] = [x[0] for x in targets]
        df['T_DEAD'] = [x[1] for x in targets]
        
        # % Hoàn thành
        df['K_PCT'] = (df[c_kill] / df['T_KILL'] * 100).round(1)
        df['D_PCT'] = (df['SUM_DEAD_UNITS'] / df['T_DEAD'] * 100).round(1)
        
        # Tổng KPI trung bình
        df['TOTAL_KPI'] = ((df['K_PCT'] + df['D_PCT']) / 2).round(1)
        
        # Xếp Rank theo TOTAL_KPI
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
    st.markdown('<div class="main-header">SHARED HOUSE 3956 - KPI COMMANDER</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👤 HỒ SƠ CHI TIẾT", "📊 BẢNG TỔNG HỢP", "🏆 VINH DANH (>100%)"])
    
    with tab1:
        sel = st.selectbox("🔍 CHỌN CHIẾN BINH:", df[c_name].unique())
        if sel:
            d = df[df[c_name] == sel].iloc[0]
            
            # --- TẤT CẢ CHỈ SỐ TỪ SHEET ---
            with st.expander("📊 XEM TẤT CẢ CHỈ SỐ TỪ SHEET", expanded=True):
                all_cols = [c for c in df.columns if c not in ['RANK', 'T_KILL', 'T_DEAD', 'K_PCT', 'D_PCT', 'TOTAL_KPI', 'DEAD_POWER', 'SUM_DEAD_UNITS']]
                cols = st.columns(5)
                for i, col in enumerate(all_cols):
                    with cols[i % 5]:
                        val = f"{int(d[col]):,}" if isinstance(d[col], (int, float)) else d[col]
                        st.markdown(f'<div class="info-box"><div class="info-label">{col}</div><div class="info-value">{val}</div></div>', unsafe_allow_html=True)

            # --- VÒNG TRÒN KPI ---
            st.write("---")
            k1, k2 = st.columns(2)
            with k1:
                fig_k = go.Figure(go.Indicator(mode="gauge+number", value=d['K_PCT'], number={'suffix': "%"},
                                              gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00FFFF"}}))
                fig_k.update_layout(height=280, margin=dict(t=30, b=0))
                st.plotly_chart(fig_k, use_container_width=True)
                st.markdown(f'<div class="target-footer">ĐẠT: {int(d[c_kill]):,}/{int(d["T_KILL"]):,} KILL</div>', unsafe_allow_html=True)
                
            with k2:
                fig_d = go.Figure(go.Indicator(mode="gauge+number", value=d['D_PCT'], number={'suffix': "%"},
                                              gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#f29b05"}}))
                fig_d.update_layout(height=280, margin=dict(t=30, b=0))
                st.plotly_chart(fig_d, use_container_width=True)
                st.markdown(f'<div class="target-footer">ĐẠT: {int(d["SUM_DEAD_UNITS"]):,}/{int(d["T_DEAD"]):,} DEAD</div>', unsafe_allow_html=True)

    with tab2:
        st.subheader("📋 BẢNG TỔNG HỢP QUÂN ĐOÀN")
        # Không dùng style.background_gradient để tránh lỗi thư viện matplotlib
        view_df = df[['RANK', c_name, c_kyluc, c_kill, 'SUM_DEAD_UNITS', 'TOTAL_KPI']]
        st.dataframe(view_df.style.format({c_kyluc: '{:,.0f}', c_kill: '{:,.0f}', 'SUM_DEAD_UNITS': '{:,.0f}', 'TOTAL_KPI': '{:.1f}%'}), 
                     use_container_width=True, height=600)

    with tab3:
        st.subheader("🔥 DANH SÁCH HOÀN THÀNH >100% KPI")
        winner_df = df[df['TOTAL_KPI'] >= 100][['RANK', c_name, 'K_PCT', 'D_PCT', 'TOTAL_KPI']]
        if not winner_df.empty:
            st.balloons()
            st.table(winner_df.style.format({'K_PCT': '{:.1f}%', 'D_PCT': '{:.1f}%', 'TOTAL_KPI': '{:.1f}%'}))
        else:
            st.info("Chưa có chiến binh nào vượt mốc 100% KPI.")
