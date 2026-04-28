import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide")

# --- 2. GIAO DIỆN ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .main-header { color: #00FFFF; text-align: center; font-size: 30px; font-weight: bold; padding: 10px; border-bottom: 2px solid #58a6ff; margin-bottom: 20px; }
    .info-box { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 15px; text-align: center; }
    .info-label { color: #8b949e; font-size: 12px; font-weight: bold; }
    .info-value { color: #ffffff; font-size: 18px; font-weight: bold; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HÀM TÍNH TARGET ---
def get_targets(pow_val):
    p_mil = pow_val / 1_000_000
    if p_mil < 15: return 100_000_000, 200_000
    elif p_mil < 20: return 200_000_000, 250_000
    elif p_mil < 30: return 250_000_000, 300_000
    else: return 300_000_000, 400_000

# --- 4. TẢI VÀ XỬ LÝ DỮ LIỆU ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
# Sử dụng GID từ ảnh image_69c1be.jpg
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=351056493'

@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_csv(URL)
        
        # CHUẨN HÓA CỘT: Xóa mọi ký tự xuống dòng, khoảng trắng ở đầu/cuối
        df.columns = [str(c).replace('\n', ' ').strip() for c in df.columns]
        
        # TỰ ĐỘNG TÌM CỘT (Tránh lỗi KeyError)
        def find_column(keywords):
            for col in df.columns:
                if any(k.lower() in col.lower() for k in keywords):
                    return col
            return None

        c_name = find_column(['Tên Người Dùng', 'Tên'])
        c_pow = find_column(['Sức Mạnh', 'Power'])
        c_kyluc = find_column(['Kỷ Lực Sức Mạnh', 'Kỷ Lực', 'Kỷ lục'])
        c_kill = find_column(['Tổng Điểm Tiêu Diệt', 'Tổng Tiêu Diệt', 'Kill'])
        
        if not c_kyluc:
            st.error(f"❌ Không tìm thấy cột 'Kỷ Lực Sức Mạnh'. Danh sách cột hiện có: {list(df.columns)}")
            return None

        # Ép kiểu dữ liệu số
        numeric_fields = [c_pow, c_kyluc, c_kill, 'T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong']
        for f in numeric_fields:
            if f in df.columns:
                df[f] = pd.to_numeric(df[f], errors='coerce').fillna(0)

        # Tính tổng Dead
        dead_cols = ['T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong']
        df['SUM_DEAD'] = df[dead_cols].sum(axis=1)

        # Tính KPI dựa trên cột Kỷ Lực Sức Mạnh
        targets = df[c_kyluc].apply(get_targets)
        df['T_KILL'] = [x[0] for x in targets]
        df['T_DEAD'] = [x[1] for x in targets]
        
        # Tính % Hoàn thành
        df['K_PCT'] = (df[c_kill] / df['T_KILL'] * 100).clip(upper=150)
        df['D_PCT'] = (df['SUM_DEAD'] / df['T_DEAD'] * 100).clip(upper=150)
        
        return df, c_name, c_pow, c_kyluc, c_kill
    except Exception as e:
        st.error(f"Lỗi nạp dữ liệu: {e}")
        return None

data_package = load_data()

# --- 5. HIỂN THỊ ---
if data_package:
    df, c_name, c_pow, c_kyluc, c_kill = data_package
    st.markdown('<div class="main-header">SHARED HOUSE 3956 KPI</div>', unsafe_allow_html=True)
    
    sel = st.selectbox("🔍 CHỌN CHIẾN BINH:", df[c_name].unique())
    
    if sel:
        d = df[df[c_name] == sel].iloc[0]
        
        # Row 1: Thông số chính
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="info-box"><div class="info-label">KỶ LỤC POW</div><div class="info-value">🏆 {int(d[c_kyluc]):,}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="info-box"><div class="info-label">POW HIỆN TẠI</div><div class="info-value">⚡ {int(d[c_pow]):,}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="info-box"><div class="info-label">TỔNG KILL</div><div class="info-value">🔥 {int(d[c_kill]):,}</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="info-box"><div class="info-label">TỔNG DEAD</div><div class="info-value">💀 {int(d["SUM_DEAD"]):,}</div></div>', unsafe_allow_html=True)

        # Row 2: Biểu đồ KPI
        st.write("---")
        g1, g2 = st.columns(2)
        with g1:
            st.write(f"🎯 **KPI KILL (Mục tiêu: {int(d['T_KILL']):,})**")
            st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=d['K_PCT'], number={'suffix':"%"})), use_container_width=True)
        with g2:
            st.write(f"🎯 **KPI DEAD (Mục tiêu: {int(d['T_DEAD']):,})**")
            st.plotly_chart(go.Figure(go.Indicator(mode="gauge+number", value=d['D_PCT'], number={'suffix':"%"})), use_container_width=True)
