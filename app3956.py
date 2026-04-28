import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide", initial_sidebar_state="collapsed")

# --- 2. KHỞI TẠO SESSION STATE ---
if 'lang' not in st.session_state:
    st.session_state.lang = "VN"
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'selected_member' not in st.session_state:
    st.session_state.selected_member = None

# --- 3. DỮ LIỆU PHIÊN DỊCH ---
TEXTS = {
    "VN": {
        "header": "HỆ THỐNG KPI - 3956",
        "tab1": "👤 CHI TIẾT", "tab2": "📊 TỔNG QUAN",
        "placeholder": "🔍 Nhập tên hoặc ID...",
        "rank": "🏆 HẠNG", "power_now": "🛡️ SỨC MẠNH", "kpi_kill_pct": "🔥 % KILL", "kpi_dead_pct": "💀 % DEAD",
        "detail_title": "📌 THÔNG SỐ CHI TIẾT", 
        "target_kill": "ĐẠT: ", "target_dead": "ĐẠT: ",
        "general_stats": "📊 TỔNG QUÁT", "kill_stats": "⚔️ KILL", "dead_stats": "💀 DEAD", "rss_stats": "🌾 THU NHẬP",
        "col_rank": "HẠNG", "col_name": "TÊN", "col_power": "POW", "col_kill": "KILL", "col_kpi_kill": "%K", "col_dead": "DEAD", "col_kpi_dead": "%D",
        "id_label": "ID", "name_label": "Tên"
    },
    "EN": {
        "header": "KPI SYSTEM - 3956",
        "tab1": "👤 PROFILE", "tab2": "📊 OVERVIEW",
        "placeholder": "🔍 Enter Name or ID...",
        "rank": "🏆 RANK", "power_now": "🛡️ POWER", "kpi_kill_pct": "🔥 % KILL", "kpi_dead_pct": "💀 % DEAD",
        "detail_title": "📌 STATISTICS", 
        "target_kill": "REACHED: ", "target_dead": "REACHED: ",
        "general_stats": "📊 GENERAL", "kill_stats": "⚔️ KILL", "dead_stats": "💀 DEAD", "rss_stats": "🌾 GATHERED",
        "col_rank": "RANK", "col_name": "NAME", "col_power": "POW", "col_kill": "KILL", "col_kpi_kill": "%K", "col_dead": "DEAD", "col_kpi_dead": "%D",
        "id_label": "ID", "name_label": "Name"
    }
}

L = TEXTS[st.session_state.lang]

# --- 4. CSS TỐI GIẢN (LOẠI BỎ CÁC THÀNH PHẦN GÂY ĐEN MÀN HÌNH) ---
st.markdown("""
    <style>
    header[data-testid="stHeader"] {display: none !important;}
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    
    /* Chỉ giữ màu sắc cơ bản, không dùng sticky phức tạp trên mobile */
    .main-header { 
        color: #00FFFF; 
        text-align: center; 
        font-size: 24px; 
        font-weight: 900; 
        padding: 10px 0;
    }
    
    .info-box { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 8px; text-align: center; margin-bottom: 5px; }
    .info-label { color: #8b949e; font-size: 10px; font-weight: bold; }
    .info-value { color: #ffffff; font-size: 14px; font-weight: 800; }
    .gauge-footer { color: #58a6ff; font-size: 12px; font-weight: 800; text-align: center; margin-top: -30px; }
    
    /* Nút gợi ý rõ ràng */
    div.stButton > button {
        width: 100%;
        background-color: #1c2128;
        border: 1px solid #30363d;
        color: #58a6ff;
        text-align: left;
    }
    </style>
""", unsafe_allow_html=True)

# --- 5. DATA ENGINE ---
@st.cache_data(ttl=5)
def load_data():
    try:
        URL = f'https://docs.google.com/spreadsheets/d/1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE/export?format=csv&gid=351056493'
        df = pd.read_csv(URL)
        df.columns = [str(c).strip() for c in df.columns]
        c_id, c_name, c_pow, c_kill, c_rss = "ID nhân vật", "Tên Người Dùng", "Sức Mạnh", "Tổng Điểm Tiêu Diệt", "Thu thập tài nguyên"
        
        k_cols = [f'Tổng Tiêu Diệt T{i}' for i in range(1, 6)]
        d_cols = [f'T{i} tử vong' for i in range(1, 6)]
        
        for col in [c_pow, c_kill, c_rss] + k_cols + d_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
        df['SUM_DEAD'] = df[d_cols].sum(axis=1)
        df['K_PCT'] = (df[c_kill] / 300_000_000 * 100).round(1)
        df['D_PCT'] = (df['SUM_DEAD'] / 400_000 * 100).round(1)
        
        df = df.sort_values(by='K_PCT', ascending=False).reset_index(drop=True)
        df.insert(0, 'H_RAW', range(1, len(df) + 1))
        df['Full_Search'] = df[c_name].astype(str) + " (ID: " + df[c_id].astype(str) + ")"
        return df, c_id, c_name, c_pow, c_kill, c_rss
    except: return None

res = load_data()
if res:
    df, c_id, c_name, c_pow, c_kill, c_rss = res

    # --- GIAO DIỆN CHÍNH ---
    st.markdown(f'<div class="main-header">{L["header"]}</div>', unsafe_allow_html=True)

    # Phần chọn ngôn ngữ và tìm kiếm
    col_l, col_s = st.columns([1, 3])
    with col_l:
        st.session_state.lang = st.radio("L", ["VN", "EN"], index=0 if st.session_state.lang == "VN" else 1, horizontal=True, label_visibility="collapsed")
    with col_s:
        search_input = st.text_input("S", value=st.session_state.search_query, placeholder=L["placeholder"], label_visibility="collapsed")

    # Logic gợi ý: Chỉ hiện khi gõ
    if search_input and not st.session_state.selected_member:
        matches = df[df['Full_Search'].str.contains(search_input, case=False, na=False)].head(5)
        for _, row in matches.iterrows():
            if st.button(row['Full_Search'], key=f"s_{row[c_id]}"):
                st.session_state.selected_member = row['Full_Search']
                st.rerun()

    tab1, tab2 = st.tabs([L["tab1"], L["tab2"]])

    with tab1:
        if st.session_state.selected_member:
            if st.button("⬅️ " + ("Tìm người khác" if st.session_state.lang == "VN" else "New Search")):
                st.session_state.selected_member = None
                st.rerun()

            d = df[df['Full_Search'] == st.session_state.selected_member].iloc[0]
            
            # Hộp chỉ số nhanh
            m = st.columns(4)
            m[0].markdown(f'<div class="info-box"><div class="info-label">{L["rank"]}</div><div class="info-value" style="color:#FFD700;">#{int(d["H_RAW"])}</div></div>', unsafe_allow_html=True)
            m[1].markdown(f'<div class="info-box"><div class="info-label">{L["power_now"]}</div><div class="info-value">{int(d[c_pow]):,}</div></div>', unsafe_allow_html=True)
            m[2].markdown(f'<div class="info-box"><div class="info-label">{L["kpi_kill_pct"]}</div><div class="info-value" style="color:#00FFFF;">{d["K_PCT"]}%</div></div>', unsafe_allow_html=True)
            m[3].markdown(f'<div class="info-box"><div class="info-label">{L["kpi_dead_pct"]}</div><div class="info-value" style="color:#f29b05;">{d["D_PCT"]}%</div></div>', unsafe_allow_html=True)
            
            with st.expander(L["detail_title"], expanded=True):
                st.write(f"**ID:** {d[c_id]} | **{L['name_label']}:** {d[c_name]}")
                st.write(f"**{L['rss_stats']}:** {int(d[c_rss]):,}")
                
                k_stats = ", ".join([f"T{i}: {int(d[f'Tổng Tiêu Diệt T{i}']):,}" for i in range(5, 1, -1)])
                st.write(f"**{L['kill_stats']}:** {k_stats}")
                
                d_stats = ", ".join([f"T{i}: {int(d[f'T{i} tử vong']):,}" for i in range(5, 0, -1)])
                st.write(f"**{L['dead_stats']}:** {d_stats}")

            # Biểu đồ KPI
            g1, g2 = st.columns(2)
            with g1:
                fig_k = go.Figure(go.Indicator(mode="gauge+number", value=d['K_PCT'], number={'suffix': "%", 'font':{'size':20}}, gauge={'bar': {'color': "#00FFFF"}, 'axis': {'range': [0, 100]}}))
                fig_k.update_layout(height=150, margin=dict(l=10,r=10,t=30,b=0), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_k, use_container_width=True, config={'displayModeBar': False})
            with g2:
                fig_d = go.Figure(go.Indicator(mode="gauge+number", value=d['D_PCT'], number={'suffix': "%", 'font':{'size':20}}, gauge={'bar': {'color': "#f29b05"}, 'axis': {'range': [0, 100]}}))
                fig_d.update_layout(height=150, margin=dict(l=10,r=10,t=30,b=0), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_d, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Nhập tên hoặc ID để bắt đầu tra cứu." if st.session_state.lang == "VN" else "Enter Name or ID to start searching.")

    with tab2:
        v_df = df[['H_RAW', c_name, c_pow, 'K_PCT', 'D_PCT']].copy()
        v_df.columns = [L['col_rank'], L['col_name'], L['col_power'], L['col_kpi_kill'], L['col_kpi_dead']]
        st.dataframe(v_df, use_container_width=True, height=400)
