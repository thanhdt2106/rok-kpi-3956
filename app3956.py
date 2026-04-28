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
        "header": "HỆ THỐNG KPI - SHARED HOUSE 3956",
        "tab1": "👤 HỒ SƠ CHI TIẾT", "tab2": "📊 TỔNG QUAN QUÂN ĐOÀN",
        "placeholder": "🔍 Nhập tên hoặc ID để tìm kiếm...",
        "rank": "🏆 HẠNG", "power_now": "🛡️ SỨC MẠNH", "kpi_kill_pct": "🔥 % KILL", "kpi_dead_pct": "💀 % DEAD",
        "detail_title": "📌 XEM THÔNG SỐ CHI TIẾT", 
        "target_kill": "ĐẠT: ", "target_dead": "ĐẠT: ",
        "general_stats": "📊 THÔNG SỐ TỔNG QUÁT", "kill_stats": "⚔️ KILL", "dead_stats": "💀 DEAD", "rss_stats": "🌾 THU NHẬP",
        "col_rank": "HẠNG 🏆", "col_name": "CHIẾN BINH 🥷", "col_power": "SỨC MẠNH 🛡️",
        "col_kill": "ĐIỂM KILL ⚔️", "col_kpi_kill": "KPI KILL 🔥", "col_dead": "LÍNH CHẾT 💀", "col_kpi_dead": "KPI DEAD ⚰️",
        "id_label": "ID nhân vật", "name_label": "Tên Người Dùng"
    },
    "EN": {
        "header": "KPI SYSTEM - SHARED HOUSE 3956",
        "tab1": "👤 DETAILED PROFILE", "tab2": "📊 ALLIANCE OVERVIEW",
        "placeholder": "🔍 Enter Name or ID to search...",
        "rank": "🏆 RANK", "power_now": "🛡️ POWER", "kpi_kill_pct": "🔥 % KILL", "kpi_dead_pct": "💀 % DEAD",
        "detail_title": "📌 VIEW FULL STATISTICS", 
        "target_kill": "REACHED: ", "target_dead": "REACHED: ",
        "general_stats": "📊 GENERAL STATISTICS", "kill_stats": "⚔️ KILL", "dead_stats": "💀 DEAD", "rss_stats": "🌾 GATHERED",
        "col_rank": "RANK 🏆", "col_name": "COMMANDER 🥷", "col_power": "POWER 🛡️",
        "col_kill": "KILL POINTS ⚔️", "col_kpi_kill": "KPI KILL 🔥", "col_dead": "DEAD UNITS 💀", "col_kpi_dead": "KPI DEAD ⚰️",
        "id_label": "Character ID", "name_label": "Username"
    }
}

L = TEXTS[st.session_state.lang]

# --- 4. CSS CUSTOM (FIX MOBILE SEARCH & UI) ---
st.markdown(f"""
    <style>
    header[data-testid="stHeader"] {{display: none !important;}}
    .stApp {{ background-color: #0d1117; color: #c9d1d9; }}
    
    /* Cố định Header và Search ở đỉnh - Không bị đẩy khi hiện bàn phím */
    .sticky-wrapper {{
        position: sticky;
        top: 0;
        z-index: 1000;
        background-color: #0d1117;
        padding-bottom: 10px;
    }}
    
    .main-header {{ 
        background: linear-gradient(90deg, #00FFFF, #58a6ff); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        text-align: center; font-size: clamp(20px, 5vw, 28px); font-weight: 900; padding: 10px 0;
    }}

    .info-box {{ background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 10px; text-align: center; margin-bottom: 8px; }}
    .info-label {{ color: #8b949e; font-size: 11px; font-weight: bold; text-transform: uppercase; }}
    .info-value {{ color: #ffffff; font-size: 16px; font-weight: 800; }}
    .gauge-footer {{ color: #58a6ff; font-size: 13px; font-weight: 800; text-align: center; margin-top: -35px; }}
    
    /* Tối ưu nút gợi ý tìm kiếm */
    .stButton > button {{
        width: 100%;
        text-align: left;
        background-color: #1c2128;
        border: 1px solid #30363d;
        color: #ffffff;
        margin-bottom: 2px;
    }}
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

    # --- HEADER & SEARCH (STICKY) ---
    st.markdown('<div class="sticky-wrapper">', unsafe_allow_html=True)
    st.markdown(f'<div class="main-header">{L["header"]}</div>', unsafe_allow_html=True)
    
    col_l, col_s = st.columns([1, 4])
    with col_l:
        new_lang = st.radio("L", ["VN", "EN"], index=0 if st.session_state.lang == "VN" else 1, horizontal=True, label_visibility="collapsed")
        if new_lang != st.session_state.lang:
            st.session_state.lang = new_lang
            st.rerun()
    with col_s:
        search_input = st.text_input("S", value=st.session_state.search_query, placeholder=L["placeholder"], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    # Logic gợi ý: Chỉ hiện khi gõ
    if search_input and st.session_state.selected_member is None:
        suggestions = df[df['Full_Search'].str.contains(search_input, case=False, na=False)].head(6)
        for _, row in suggestions.iterrows():
            if st.button(row['Full_Search'], key=f"sug_{row[c_id]}"):
                st.session_state.selected_member = row['Full_Search']
                st.session_state.search_query = "" 
                st.rerun()

    tab1, tab2 = st.tabs([L["tab1"], L["tab2"]])

    with tab1:
        if st.session_state.selected_member:
            # Nút xóa để tìm người khác
            if st.button("🔍 " + ( "Tìm người khác" if st.session_state.lang == "VN" else "Search another")):
                st.session_state.selected_member = None
                st.rerun()

            d = df[df['Full_Search'] == st.session_state.selected_member].iloc[0]
            
            # --- 4 HỘP KPI ---
            m = st.columns(4)
            m[0].markdown(f'<div class="info-box"><div class="info-label">{L["rank"]}</div><div class="info-value" style="color:#FFD700;">#{int(d["H_RAW"])}</div></div>', unsafe_allow_html=True)
            m[1].markdown(f'<div class="info-box"><div class="info-label">{L["power_now"]}</div><div class="info-value">{int(d[c_pow]):,}</div></div>', unsafe_allow_html=True)
            m[2].markdown(f'<div class="info-box"><div class="info-label">{L["kpi_kill_pct"]}</div><div class="info-value" style="color:#00FFFF;">{d["K_PCT"]}%</div></div>', unsafe_allow_html=True)
            m[3].markdown(f'<div class="info-box"><div class="info-label">{L["kpi_dead_pct"]}</div><div class="info-value" style="color:#f29b05;">{d["D_PCT"]}%</div></div>', unsafe_allow_html=True)
            
            # --- CHI TIẾT ---
            with st.expander(L["detail_title"], expanded=True):
                st.markdown(f"**{L['general_stats']}**")
                g = st.columns(3)
                g[0].markdown(f'<div class="info-box"><div class="info-label">ID</div><div class="info-value">{d[c_id]}</div></div>', unsafe_allow_html=True)
                g[1].markdown(f'<div class="info-box"><div class="info-label">{L["name_label"]}</div><div class="info-value">{d[c_name]}</div></div>', unsafe_allow_html=True)
                g[2].markdown(f'<div class="info-box"><div class="info-label">{L["rss_stats"]}</div><div class="info-value">{int(d[c_rss]):,}</div></div>', unsafe_allow_html=True)

                st.markdown(f"**{L['kill_stats']} (T5-T1)**")
                k_cols = st.columns(5)
                for i in range(5, 0, -1):
                    k_cols[5-i].markdown(f'<div class="info-box"><div class="info-label">T{i}</div><div class="info-value">{int(d[f"Tổng Tiêu Diệt T{i}"]):,}</div></div>', unsafe_allow_html=True)

                st.markdown(f"**{L['dead_stats']} (T5-T1)**")
                d_cols = st.columns(5)
                for i in range(5, 0, -1):
                    d_cols[5-i].markdown(f'<div class="info-box"><div class="info-label">T{i}</div><div class="info-value">{int(d[f"T{i} tử vong"]):,}</div></div>', unsafe_allow_html=True)

            # --- BIỂU ĐỒ ---
            g1, g2 = st.columns(2)
            with g1:
                fig_k = go.Figure(go.Indicator(mode="gauge+number", value=d['K_PCT'], number={'suffix': "%", 'font':{'size':24}}, gauge={'bar': {'color': "#00FFFF"}, 'axis': {'range': [0, 100]}}))
                fig_k.update_layout(height=180, margin=dict(l=20,r=20,t=30,b=0), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_k, use_container_width=True, config={'displayModeBar': False})
                st.markdown(f'<div class="gauge-footer">{L["target_kill"]}{d[c_kill]/1e6:.1f}M / 300M</div>', unsafe_allow_html=True)
            with g2:
                fig_d = go.Figure(go.Indicator(mode="gauge+number", value=d['D_PCT'], number={'suffix': "%", 'font':{'size':24}}, gauge={'bar': {'color': "#f29b05"}, 'axis': {'range': [0, 100]}}))
                fig_d.update_layout(height=180, margin=dict(l=20,r=20,t=30,b=0), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_d, use_container_width=True, config={'displayModeBar': False})
                st.markdown(f'<div class="gauge-footer">{L["target_dead"]}{int(d["SUM_DEAD"]/1000)}K / 400K</div>', unsafe_allow_html=True)
        else:
            st.image("https://github.com/thanhdt2106/rok-kpi-3956/blob/main/meme2.png?raw=true", use_container_width=True)

    with tab2:
        v_df = df[['H_RAW', c_name, c_pow, c_kill, 'K_PCT', 'SUM_DEAD', 'D_PCT']].copy()
        v_df.columns = [L['col_rank'], L['col_name'], L['col_power'], L['col_kill'], L['col_kpi_kill'], L['col_dead'], L['col_kpi_dead']]
        st.dataframe(v_df.style.format({L['col_power']: '{:,.0f}', L['col_kill']: '{:,.0f}', L['col_dead']: '{:,.0f}', L['col_kpi_kill']: '{:.1f}%', L['col_kpi_dead']: '{:.1f}%'}), use_container_width=True, height=600)
