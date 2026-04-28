import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide")

# --- 2. GIAO DIỆN CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .main-header { color: #00FFFF; text-align: center; font-size: 32px; font-weight: bold; padding: 10px; border-bottom: 2px solid #58a6ff; margin-bottom: 20px; }
    .info-box { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 15px; text-align: center; margin-bottom: 10px; min-height: 100px; display: flex; flex-direction: column; justify-content: center; }
    .info-label { color: #8b949e; font-size: 11px; font-weight: bold; text-transform: uppercase; }
    .info-value { color: #ffffff; font-size: 16px; font-weight: bold; margin-top: 5px; }
    .target-text { color: #58a6ff; font-weight: bold; font-size: 14px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC TÍNH KPI THEO MỐC POWER TRƯỚC CHIẾN ---
def get_targets(pow_before):
    p_mil = pow_before / 1_000_000
    if p_mil < 15: return 100_000_000, 200_000
    elif p_mil < 20: return 200_000_000, 250_000
    elif p_mil < 30: return 250_000_000, 300_000
    else: return 300_000_000, 400_000

# --- 4. XỬ LÝ DỮ LIỆU ---
# QUAN TRỌNG: Hãy đảm bảo bạn đã vào Google Sheet -> Chia sẻ -> Bất kỳ ai có link (Người xem)
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid=351056493'

@st.cache_data(ttl=30)
def load_data():
    try:
        df = pd.read_csv(URL)
        # Làm sạch tên cột: Xóa dấu xuống dòng, khoảng trắng thừa
        df.columns = [str(c).replace('\n', ' ').strip() for c in df.columns]
        
        # Hàm hỗ trợ tìm tên cột gần đúng (để tránh lỗi KeyError)
        def find_col(possible_names):
            for name in possible_names:
                if name in df.columns: return name
            return None

        # Định danh lại các cột quan trọng
        col_name = find_col(['Tên Người Dùng', 'Tên'])
        col_pow = find_col(['Sức Mạnh', 'Power'])
        col_max_pow = find_col(['Kỷ Lực Sức Mạnh', 'Kỷ lục Sức mạnh', 'Kỷ Lực'])
        col_kill = find_col(['Tổng Điểm Tiêu Diệt', 'Tổng Tiêu Diệt', 'Kill Points'])
        
        if not col_max_pow or not col_kill:
            st.error(f"⚠️ Không tìm thấy cột cần thiết. Hãy kiểm tra tên cột trong Sheet. (Đang thấy: {list(df.columns[:5])})")
            return None

        # Chuyển đổi dữ liệu số
        numeric_cols = [col_pow, col_max_pow, col_kill, 'T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong']
        for c in numeric_cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

        # Tính toán chỉ số
        df['TOTAL_DEAD_UNITS'] = df[['T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong']].sum(axis=1)
        df['DEAD_POWER_SCORE'] = (df['T5 tử vong']*10 + df['T4 tử vong']*4 + df['T3 tử vong']*3 + df['T2 tử vong']*2 + df['T1 tử vong']*1)
        
        # Áp dụng Target từ Kỷ Lực Sức Mạnh
        targets = df[col_max_pow].apply(get_targets)
        df['T_KILL'] = [x[0] for x in targets]
        df['T_DEAD'] = [x[1] for x in targets]
        
        # Tính % (Giới hạn hiển thị 150%)
        df['K_PCT'] = (df[col_kill] / df['T_KILL'] * 100).clip(upper=150)
        df['D_PCT'] = (df['TOTAL_DEAD_UNITS'] / df['T_DEAD'] * 100).clip(upper=150)
        
        # Lưu lại tên cột gốc để dùng cho hiển thị
        df['_col_name'] = df[col_name]
        df['_col_pow'] = df[col_pow]
        df['_col_max_pow'] = df[col_max_pow]
        df['_col_kill'] = df[col_kill]
        
        return df
    except Exception as e:
        st.error(f"❌ Lỗi nạp dữ liệu: {e}")
        return None

df = load_data()

# --- 5. HIỂN THỊ ---
if df is not None:
    st.markdown('<div class="main-header">SHARED HOUSE 3956 - KPI SYSTEM</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["👤 HỒ SƠ", "🏆 BẢNG XẾP HẠNG"])
    
    with tab1:
        sel = st.selectbox("🔍 CHỌN CHIẾN BINH:", df['_col_name'].unique())
        if sel:
            d = df[df['_col_name'] == sel].iloc[0]
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f'<div class="info-box"><div class="info-label">KỶ LỤC POW</div><div class="info-value">🏆 {int(d["_col_max_pow"]):, Barbarian}</div></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="info-box"><div class="info-label">POW HIỆN TẠI</div><div class="info-value">⚡ {int(d["_col_pow"]):,}</div></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="info-box"><div class="info-label">TỔNG KILL</div><div class="info-value">🔥 {int(d["_col_kill"]):,}</div></div>', unsafe_allow_html=True)
            c4.markdown(f'<div class="info-box"><div class="info-label">TỔNG DEAD</div><div class="info-value">💀 {int(d["TOTAL_DEAD_UNITS"]):,}</div></div>', unsafe_allow_html=True)

            st.write("---")
            ck1, ck2 = st.columns(2)
            with ck1:
                st.markdown(f'<p class="target-text">🎯 MỤC TIÊU KILL: {int(d["T_KILL"]):,}</p>', unsafe_allow_html=True)
                fig_k = go.Figure(go.Indicator(mode="gauge+number", value=d['K_PCT'], number={'suffix': "%"}, gauge={'axis':{'range':[0, 100]},'bar':{'color':"#00FFFF"},'steps':[{'range':[0, 65],'color':"#30363d"}]}))
                st.plotly_chart(fig_k, use_container_width=True)
            with ck2:
                st.markdown(f'<p class="target-text">🎯 MỤC TIÊU DEAD: {int(d["T_DEAD"]):,}</p>', unsafe_allow_html=True)
                fig_d = go.Figure(go.Indicator(mode="gauge+number", value=d['D_PCT'], number={'suffix': "%"}, gauge={'axis':{'range':[0, 100]},'bar':{'color':"#f29b05"},'steps':[{'range':[0, 65],'color':"#30363d"}]}))
                st.plotly_chart(fig_d, use_container_width=True)

    with tab2:
        st.subheader("🏆 XẾP HẠNG HOÀN THÀNH KPI")
        view = df[['_col_name', '_col_max_pow', 'K_PCT', 'D_PCT']].sort_values(by='K_PCT', ascending=False)
        st.dataframe(view.style.format({'K_PCT':'{:.1f}%','D_PCT':'{:.1f}%','_col_max_pow':'{:,.0f}'}), use_container_width=True)
