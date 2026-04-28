import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide", initial_sidebar_state="collapsed")

# --- 2. DỮ LIỆU NGÔN NGỮ ---
TEXTS = {
    "VN": {
        "header": "HỆ THỐNG KPI - SHARED HOUSE 3956",
        "tab1": "👤 HỒ SƠ CHI TIẾT", "tab2": "📊 TỔNG QUAN QUÂN ĐOÀN",
        "search_label": "🔍 TÌM KIẾM CHIẾN BINH:",
        "placeholder": "Gõ tên hoặc ID để hiện danh sách gợi ý...",
        "rank": "🏆 HẠNG", "power_now": "🛡️ SỨC MẠNH", "kpi_kill_pct": "🔥 % KILL", "kpi_dead_pct": "💀 % DEAD",
        "detail_title": "📌 THÔNG SỐ CHI TIẾT", "target_kill": "ĐẠT: ", "target_dead": "ĐẠT: "
    }
}

# --- 3. CSS TỔNG LỰC (ẨN HEADER, FIX MOBILE) ---
st.markdown("""
    <style>
    header[data-testid="stHeader"] {display: none !important;}
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .main-header { 
        background: linear-gradient(90deg, #00FFFF, #58a6ff); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        text-align: center; font-size: clamp(20px, 5vw, 32px); font-weight: 900; padding-bottom: 15px;
    }
    /* Style cho các hộp thông số */
    .info-box { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 10px; text-align: center; margin-bottom: 5px; }
    .info-label { color: #8b949e; font-size: 11px; font-weight: bold; text-transform: uppercase; }
    .info-value { color: #ffffff; font-size: 18px; font-weight: 800; }
    
    @media (max-width: 768px) {
        [data-testid="column"] { width: 50% !important; flex: 1 1 50% !important; min-width: 50% !important; }
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA ENGINE ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=351056493'

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(URL)
        df.columns = [str(c).strip() for c in df.columns]
        c_id = "ID nhân vật"
        c_name = "Tên Người Dùng"
        c_pow = "Sức Mạnh"
        c_kill = "Tổng Điểm Tiêu Diệt"
        
        # Chuyển đổi dữ liệu số
        for col in [c_pow, c_kill]:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
        # Tính toán KPI
        df['SUM_DEAD'] = df[['T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong']].sum(axis=1)
        df['K_PCT'] = (df[c_kill] / 300_000_000 * 100).round(1)
        df['D_PCT'] = (df['SUM_DEAD'] / 400_000 * 100).round(1)
        
        # Sắp xếp hạng
        df = df.sort_values(by='K_PCT', ascending=False).reset_index(drop=True)
        df.insert(0, 'H_RAW', range(1, len(df) + 1))
        return df, c_id, c_name, c_pow, c_kill
    except:
        return None

res = load_data()
if res:
    df, c_id, c_name, c_pow, c_kill = res
    L = TEXTS["VN"]
    
    st.markdown(f'<div class="main-header">{L["header"]}</div>', unsafe_allow_html=True)
    
    # --- LOGIC TÌM KIẾM GỢI Ý ---
    # Danh sách tất cả tên để làm gợi ý
    all_names = df[c_name].tolist()
    
    # Thanh selectbox đóng vai trò là thanh tìm kiếm có gợi ý
    selected_name = st.selectbox(
        L["search_label"],
        options=[""] + all_names, # Thêm khoảng trống ở đầu để mặc định không hiện gì
        format_func=lambda x: L["placeholder"] if x == "" else x,
        index=0
    )

    if selected_name != "":
        # Chỉ khi người dùng chọn một cái tên, Profile mới hiện ra
        d = df[df[c_name] == selected_name].iloc[0]
        
        # --- HIỂN THỊ PROFILE ---
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="info-box"><div class="info-label">{L["rank"]}</div><div class="info-value" style="color:#FFD700;">#{int(d["H_RAW"])}</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="info-box"><div class="info-label">{L["power_now"]}</div><div class="info-value">{int(d[c_pow]):,}</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="info-box"><div class="info-label">{L["kpi_kill_pct"]}</div><div class="info-value" style="color:#00FFFF;">{d["K_PCT"]}%</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="info-box"><div class="info-label">{L["kpi_dead_pct"]}</div><div class="info-value" style="color:#f29b05;">{d["D_PCT"]}%</div></div>', unsafe_allow_html=True)
        
        with st.expander(L["detail_title"], expanded=True):
            det_cols = st.columns(5)
            # Map dữ liệu chi tiết
            details = [
                ("ID", c_id), ("Tên", c_name), ("Sức mạnh", c_pow), 
                ("T5 Kill", "Tổng Tiêu Diệt T5"), ("T4 Kill", "Tổng Tiêu Diệt T4"),
                ("T5 Tử", "T5 tử vong"), ("T4 Tử", "T4 tử vong"), ("T3 Tử", "T3 tử vong"),
                ("Tổng Kill", c_kill)
            ]
            for i, (label, key) in enumerate(details):
                val = d[key] if key in d else 0
                txt = f"{int(val):,}" if isinstance(val, (int, float)) else val
                det_cols[i % 5].markdown(f'<div class="info-box"><div class="info-label">{label}</div><div class="info-value" style="font-size:14px;">{txt}</div></div>', unsafe_allow_html=True)

        # --- BIỂU ĐỒ GAUGES ---
        g1, g2 = st.columns(2)
        with g1:
            fig_k = go.Figure(go.Indicator(mode="gauge+number", value=d['K_PCT'], number={'suffix': "%", 'font':{'size':24}}, gauge={'bar': {'color': "#00FFFF"}}))
            fig_k.update_layout(height=200, margin=dict(l=10,r=10,t=40,b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_k, use_container_width=True)
            st.markdown(f'<div style="text-align:center; color:#00FFFF; font-weight:bold; margin-top:-40px;">{L["target_kill"]}{d[c_kill]/1e6:.1f}M</div>', unsafe_allow_html=True)
        with g2:
            fig_d = go.Figure(go.Indicator(mode="gauge+number", value=d['D_PCT'], number={'suffix': "%", 'font':{'size':24}}, gauge={'bar': {'color': "#f29b05"}}))
            fig_d.update_layout(height=200, margin=dict(l=10,r=10,t=40,b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_d, use_container_width=True)
            st.markdown(f'<div style="text-align:center; color:#f29b05; font-weight:bold; margin-top:-40px;">{L["target_dead"]}{int(d["SUM_DEAD"]/1000)}K</div>', unsafe_allow_html=True)
    else:
        # Khi chưa chọn tên, có thể hiển thị Banner ảnh như bạn muốn ở đây
        st.image("https://raw.githubusercontent.com/tên-user/tên-repo/main/image_5ca61f.jpg", use_column_width=True)
