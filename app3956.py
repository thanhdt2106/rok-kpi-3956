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

# --- 4. DATA ENGINE (FIX LỖI DÒ CỘT) ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=351056493'

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(URL)
        
        # Làm sạch tên cột triệt để (Xóa xuống dòng, xóa khoảng trắng thừa)
        df.columns = [str(c).replace('\n', ' ').strip() for c in df.columns]
        
        # Cơ chế dò cột thông minh dựa trên ảnh Sheet bạn gửi
        def find_col(keywords):
            for c in df.columns:
                if any(k.lower() in c.lower() for k in keywords):
                    return c
            return None

        c_name = find_col(['Tên Người Dùng']) 
        c_kyluc = find_col(['Kỷ Lực Sức Mạnh']) 
        c_kill = find_col(['Tổng Điểm Tiêu Diệt']) 
        c_pow_now = find_col(['Sức Mạnh']) # Cột C trong ảnh

        # Kiểm tra nếu thiếu cột quan trọng
        if not all([c_name, c_kyluc, c_kill]):
            st.error(f"Lỗi: Không tìm thấy các cột cần thiết. Cột đang có: {list(df.columns)}")
            return None

        # Chuyển đổi dữ liệu số an toàn
        numeric_cols = [c for c in df.columns if c != c_name]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Tính toán Dead (Cột E đến I trong ảnh)
        dead_keywords = ['T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong']
        actual_dead_cols = [c for c in df.columns if any(k in c for k in dead_keywords)]
        df['SUM_DEAD'] = df[actual_dead_cols].sum(axis=1)

        # Gán Target và tính % hoàn thành
        targets = df[c_kyluc].apply(get_targets)
        df['T_KILL'] = [x[0] for x in targets]
        df['T_DEAD'] = [x[1] for x in targets]
        
        df['K_PCT'] = (df[c_kill] / df['T_KILL'] * 100).round(1)
        df['D_PCT'] = (df['SUM_DEAD'] / df['T_DEAD'] * 100).round(1)
        df['TOTAL_KPI'] = ((df['K_PCT'] + df['D_PCT']) / 2).round(1)
        
        # Xếp hạng
        df = df.sort_values(by='TOTAL_KPI', ascending=False).reset_index(drop=True)
        df.insert(0, 'RANK', df.index + 1)
        
        return df, c_name, c_kyluc, c_kill, c_pow_now
    except Exception as e:
        st.error(f"Lỗi hệ thống: {e}")
        return None

# --- 5. HIỂN THỊ ---
res = load_data()
if res:
    df, c_name, c_kyluc, c_kill, c_pow_now = res
    st.markdown('<div class="main-header">SHARED HOUSE 3956 KPI SYSTEM</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👤 HỒ SƠ CHIẾN BINH", "📊 BẢNG TỔNG HỢP", "🏆 VINH DANH"])
    
    with tab1:
        sel = st.selectbox("🔍 TÌM TÊN CHIẾN BINH:", df[c_name].unique())
        if sel:
            d = df[df[c_name] == sel].iloc[0]
            
            # Khối thông tin cơ bản
            cols = st.columns(4)
            with cols[0]: st.markdown(f'<div class="info-box"><div class="info-label">Kỷ Lực POW</div><div class="info-value">{int(d[c_kyluc]):,}</div></div>', unsafe_allow_html=True)
            with cols[1]: st.markdown(f'<div class="info-box"><div class="info-label">POW Hiện Tại</div><div class="info-value">{int(d[c_pow_now]):,}</div></div>', unsafe_allow_html=True)
            with cols[2]: st.markdown(f'<div class="info-box"><div class="info-label">Tổng Tiêu Diệt</div><div class="info-value">{int(d[c_kill]):,}</div></div>', unsafe_allow_html=True)
            with cols[3]: st.markdown(f'<div class="info-box"><div class="info-label">Tổng Tử Vong</div><div class="info-value">{int(d["SUM_DEAD"]):,}</div></div>', unsafe_allow_html=True)

            # Biểu đồ Gauge
            st.write("---")
            k1, k2 = st.columns(2)
            with k1:
                fig_k = go.Figure(go.Indicator(mode="gauge+number", value=d['K_PCT'], number={'suffix': "%"},
                                              title={'text': "KPI TIÊU DIỆT", 'font': {'size': 16, 'color': '#00FFFF'}},
                                              gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00FFFF"}}))
                fig_k.update_layout(height=300, margin=dict(t=50, b=0), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_k, use_container_width=True)
                st.markdown(f'<div class="target-footer">Mục tiêu: {int(d["T_KILL"]):,}</div>', unsafe_allow_html=True)
            
            with k2:
                fig_d = go.Figure(go.Indicator(mode="gauge+number", value=d['D_PCT'], number={'suffix': "%"},
                                              title={'text': "KPI TỬ VONG", 'font': {'size': 16, 'color': '#f29b05'}},
                                              gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#f29b05"}}))
                fig_d.update_layout(height=300, margin=dict(t=50, b=0), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_d, use_container_width=True)
                st.markdown(f'<div class="target-footer">Mục tiêu: {int(d["T_DEAD"]):,}</div>', unsafe_allow_html=True)

    with tab2:
        # Bảng tổng hợp rút gọn để tránh rối
        st.dataframe(df[['RANK', c_name, c_pow_now, c_kill, 'SUM_DEAD', 'TOTAL_KPI']], use_container_width=True, height=600)

    with tab3:
        winners = df[df['TOTAL_KPI'] >= 100][['RANK', c_name, 'TOTAL_KPI']]
        if not winners.empty:
            st.balloons()
            st.table(winners)
        else:
            st.info("Đang cập nhật danh sách vinh danh...")
