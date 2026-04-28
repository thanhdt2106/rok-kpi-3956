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
        "placeholder": "Nhập ID (chính xác) hoặc Tên của bạn vào đây...",
        "rank": "🏆 HẠNG", "power_now": "🛡️ SỨC MẠNH", "kpi_kill_pct": "🔥 % KILL", "kpi_dead_pct": "💀 % DEAD",
        "detail_title": "📌 XEM THÔNG SỐ CHI TIẾT", "target_kill": "ĐẠT: ", "target_dead": "ĐẠT: ",
        "col_rank": "HẠNG 🏆", "col_name": "CHIẾN BINH 🥷", "col_power": "SỨC MẠNH 🛡️",
        "col_kill": "ĐIỂM KILL ⚔️", "col_kpi_kill": "KPI KILL 🔥", "col_dead": "LÍNH CHẾT 💀", "col_kpi_dead": "KPI DEAD ⚰️"
    },
    "EN": {
        "header": "KPI SYSTEM - SHARED HOUSE 3956",
        "tab1": "👤 DETAILED PROFILE", "tab2": "📊 ALLIANCE OVERVIEW",
        "placeholder": "Enter ID (exact) or your Name here...",
        "rank": "🏆 RANK", "power_now": "🛡️ POWER", "kpi_kill_pct": "🔥 % KILL", "kpi_dead_pct": "💀 % DEAD",
        "detail_title": "📌 VIEW DETAILED STATISTICS", "target_kill": "REACHED: ", "target_dead": "REACHED: ",
        "col_rank": "RANK 🏆", "col_name": "COMMANDER 🥷", "col_power": "POWER 🛡️",
        "col_kill": "KILL POINTS ⚔️", "col_kpi_kill": "KPI KILL 🔥", "col_dead": "DEAD UNITS 💀", "col_kpi_dead": "KPI DEAD ⚰️"
    }
}

# --- 3. CSS (XÓA HEADER/SIDEBAR + FIX MOBILE) ---
st.markdown("""
    <style>
    header[data-testid="stHeader"] {display: none !important;}
    [data-testid="stSidebarNav"], [data-testid="collapsedControl"] {display: none;}
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .block-container { padding-top: 1rem !important; }
    .main-header { 
        background: linear-gradient(90deg, #00FFFF, #58a6ff); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        text-align: center; font-size: clamp(20px, 5vw, 32px); font-weight: 900; padding-bottom: 10px;
    }
    .info-box { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 10px; text-align: center; margin-bottom: 5px; }
    .info-label { color: #8b949e; font-size: 11px; font-weight: bold; text-transform: uppercase; }
    .info-value { color: #ffffff; font-size: 18px; font-weight: 800; }
    .gauge-footer { color: #58a6ff; font-size: 12px; font-weight: 800; text-align: center; margin-top: -35px; }
    
    /* Giao diện 2 cột cho mobile */
    @media (max-width: 768px) {
        [data-testid="column"] { width: 50% !important; flex: 1 1 50% !important; min-width: 50% !important; }
        div[data-testid="stHorizontalBlock"] { gap: 0px !important; }
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
        c_name = next((c for c in df.columns if 'Tên' in c or 'Name' in c), "Tên Người Dùng")
        c_pow = next((c for c in df.columns if 'Sức Mạnh' in c or 'Power' in c), "Sức Mạnh")
        c_kill = next((c for c in df.columns if 'Tiêu Diệt' in c or 'Kill' in c), "Tổng Điểm Tiêu Diệt")
        for col in [c_pow, c_kill]: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df['SUM_DEAD'] = df[['T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong']].sum(axis=1)
        df['K_PCT'] = (df[c_kill] / 300_000_000 * 100).round(1)
        df['D_PCT'] = (df['SUM_DEAD'] / 400_000 * 100).round(1)
        df = df.sort_values(by='K_PCT', ascending=False).reset_index(drop=True)
        df.insert(0, 'H_RAW', range(1, len(df) + 1))
        return df, c_id, c_name, c_pow, c_kill
    except: return None

res = load_data()
if res:
    df, c_id, c_name, c_pow, c_kill = res
    st.markdown(f'<div class="main-header">{TEXTS["VN"]["header"]}</div>', unsafe_allow_html=True)
    
    # --- CHỌN NGÔN NGỮ VÀ TÌM KIẾM CHUNG 1 DÒNG ---
    col_lang, col_search = st.columns([1, 4])
    with col_lang:
        lang = st.radio("L:", ["VN", "EN"], horizontal=True, label_visibility="collapsed")
        L = TEXTS[lang]
    
    with col_search:
        search_query = st.text_input("Search", placeholder=L["placeholder"], label_visibility="collapsed")

    # Xử lý Logic Tìm kiếm
    if search_query:
        # Nếu nhập số -> Tìm chính xác ID
        if search_query.isdigit():
            filtered_df = df[df[c_id].astype(str) == search_query]
        # Nếu nhập chữ -> Tìm gợi ý theo tên
        else:
            filtered_df = df[df[c_name].str.contains(search_query, case=False, na=False)]
    else:
        filtered_df = pd.DataFrame() # Để trống nếu chưa nhập

    tab1, tab2 = st.tabs([L["tab1"], L["tab2"]])
    
    with tab1:
        if not filtered_df.empty:
            # Nếu có nhiều kết quả (khi tìm theo tên), cho chọn list gợi ý
            if len(filtered_df) > 1:
                selected_name = st.selectbox("Gợi ý cho bạn:", filtered_df[c_name].tolist())
                d = filtered_df[filtered_df[c_name] == selected_name].iloc[0]
            else:
                d = filtered_df.iloc[0]

            # Hiển thị kết quả
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f'<div class="info-box"><div class="info-label">{L["rank"]}</div><div class="info-value" style="color:#FFD700;">#{int(d["H_RAW"])}</div></div>', unsafe_allow_html=True)
            m2.markdown(f'<div class="info-box"><div class="info-label">{L["power_now"]}</div><div class="info-value">{int(d[c_pow]):,}</div></div>', unsafe_allow_html=True)
            m3.markdown(f'<div class="info-box"><div class="info-label">{L["kpi_kill_pct"]}</div><div class="info-value" style="color:#00FFFF;">{d["K_PCT"]}%</div></div>', unsafe_allow_html=True)
            m4.markdown(f'<div class="info-box"><div class="info-label">{L["kpi_dead_pct"]}</div><div class="info-value" style="color:#f29b05;">{d["D_PCT"]}%</div></div>', unsafe_allow_html=True)
            
            with st.expander(L["detail_title"]):
                det_cols = st.columns(5)
                # ... (Phần thông số chi tiết giữ nguyên như cũ)
            
            g1, g2 = st.columns(2)
            with g1:
                fig_k = go.Figure(go.Indicator(mode="gauge+number", value=d['K_PCT'], number={'suffix': "%", 'font':{'size':24}}, gauge={'bar': {'color': "#00FFFF"}}))
                fig_k.update_layout(height=180, margin=dict(l=10,r=10,t=30,b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_k, use_container_width=True, config={'displayModeBar': False})
                st.markdown(f'<div class="gauge-footer">{L["target_kill"]}{d[c_kill]/1e6:.1f}M</div>', unsafe_allow_html=True)
            with g2:
                fig_d = go.Figure(go.Indicator(mode="gauge+number", value=d['D_PCT'], number={'suffix': "%", 'font':{'size':24}}, gauge={'bar': {'color': "#f29b05"}}))
                fig_d.update_layout(height=180, margin=dict(l=10,r=10,t=30,b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_d, use_container_width=True, config={'displayModeBar': False})
                st.markdown(f'<div class="gauge-footer">{L["target_dead"]}{int(d["SUM_DEAD"]/1000)}K</div>', unsafe_allow_html=True)
        else:
            st.info("👋 " + L["placeholder"])

    with tab2:
        st.markdown("<div class='big-table-container'>", unsafe_allow_html=True)
        v_df = df[['H_RAW', c_name, c_pow, c_kill, 'K_PCT', 'SUM_DEAD', 'D_PCT']].copy()
        v_df.columns = [L['col_rank'], L['col_name'], L['col_power'], L['col_kill'], L['col_kpi_kill'], L['col_dead'], L['col_kpi_dead']]
        st.dataframe(v_df.style.format({L['col_power']: '{:,.0f}', L['col_kill']: '{:,.0f}', L['col_dead']: '{:,.0f}', L['col_kpi_kill']: '{:.1f}%', L['col_kpi_dead']: '{:.1f}%'}), use_container_width=True, height=600)
