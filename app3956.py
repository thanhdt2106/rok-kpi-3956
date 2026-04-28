import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide", initial_sidebar_state="collapsed")

# --- 2. KHỞI TẠO SESSION STATE ---
if 'lang' not in st.session_state:
    st.session_state.lang = "VN"
if 'selected_index' not in st.session_state:
    st.session_state.selected_index = 0

# --- 3. DỮ LIỆU PHIÊN DỊCH ---
TEXTS = {
    "VN": {
        "header": "HỆ THỐNG KPI - 3956",
        "tab1": "👤 CHI TIẾT", "tab2": "📊 TỔNG QUAN",
        "placeholder": "🔍 Tìm tên hoặc ID...",
        "rank": "🏆 HẠNG", "power_now": "🛡️ SỨC MẠNH", "kpi_kill_pct": "🔥 % KILL", "kpi_dead_pct": "💀 % DEAD",
        "detail_title": "📌 XEM THÔNG SỐ CHI TIẾT", 
        "target_kill": "ĐẠT: ", "target_dead": "ĐẠT: ",
        "general_stats": "📊 TỔNG QUÁT", "kill_stats": "⚔️ KILL", "dead_stats": "💀 DEAD", "rss_stats": "🌾 THU NHẬP",
        "id_label": "ID", "name_label": "Tên"
    },
    "EN": {
        "header": "KPI SYSTEM - 3956",
        "tab1": "👤 PROFILE", "tab2": "📊 OVERVIEW",
        "placeholder": "🔍 Search Name or ID...",
        "rank": "🏆 RANK", "power_now": "🛡️ POWER", "kpi_kill_pct": "🔥 % KILL", "kpi_dead_pct": "💀 % DEAD",
        "detail_title": "📌 FULL STATISTICS", 
        "target_kill": "REACHED: ", "target_dead": "REACHED: ",
        "general_stats": "📊 GENERAL", "kill_stats": "⚔️ KILL", "dead_stats": "💀 DEAD", "rss_stats": "🌾 GATHERED",
        "id_label": "ID", "name_label": "Name"
    }
}

# --- 4. CALLBACKS ---
def change_lang_callback():
    st.session_state.lang = st.session_state.lang_radio_key

def sync_search_callback():
    if 'main_search' in st.session_state:
        try:
            st.session_state.selected_index = options_list.index(st.session_state.main_search)
        except ValueError:
            st.session_state.selected_index = 0

L = TEXTS[st.session_state.lang]

# --- 5. CSS CUSTOM (FIX KHOẢNG ĐEN & STICKY SEARCH) ---
st.markdown(f""

    
    /* Sticky Header: Giữ thanh search luôn ở đỉnh khi cuộn hoặc hiện bàn phím */
    .sticky-nav {{
        position: -webkit-sticky;
        position: sticky;
        top: 0;
        background-color: #0d1117;
        z-index: 1000;
        padding: 10px 0;
        border-bottom: 1px solid #30363d;
    }}
    
    .main-header {{ 
        background: linear-gradient(90deg, #00FFFF, #58a6ff); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        text-align: center; font-size: 24px; font-weight: 900;
    }}
    
    .info-box {{ background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 10px; text-align: center; margin-bottom: 8px; }}
    .info-label {{ color: #8b949e; font-size: 11px; font-weight: bold; text-transform: uppercase; }}
    .info-value {{ color: #ffffff; font-size: 16px; font-weight: 800; }}
    .gauge-footer {{ color: #58a6ff; font-size: 13px; font-weight: 800; text-align: center; margin-top: -35px; }}
    
    /* Thu nhỏ tabs trên mobile */
    button[data-baseweb="tab"] {{ padding: 10px 15px !important; }}
    </style>
"", unsafe_allow_html=True)

# --- 6. DATA ENGINE ---
@st.cache_data(ttl=5)
def load_data():
    try:
        URL = f'https://docs.google.com/spreadsheets/d/1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE/export?format=csv&gid=351056493'
        df = pd.read_csv(URL)
        df.columns = [str(c).strip() for c in df.columns]
        c_id, c_name, c_pow, c_kill, c_rss = "ID nhân vật", "Tên Người Dùng", "Sức Mạnh", "Tổng Điểm Tiêu Diệt", "Thu thập tài nguyên"
        
        kill_cols = [f'Tổng Tiêu Diệt T{i}' for i in range(1, 6)]
        dead_cols = [f'T{i} tử vong' for i in range(1, 6)]
        
        for col in [c_pow, c_kill, c_rss] + kill_cols + dead_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
        df['SUM_DEAD'] = df[dead_cols].sum(axis=1)
        df['K_PCT'] = (df[c_kill] / 300_000_000 * 100).round(1)
        df['D_PCT'] = (df['SUM_DEAD'] / 400_000 * 100).round(1)
        
        df = df.sort_values(by='K_PCT', ascending=False).reset_index(drop=True)
        df.insert(0, 'H_RAW', range(1, len(df) + 1))
        df['Full_Search'] = df[c_name] + " (ID: " + df[c_id].astype(str) + ")"
        return df, c_id, c_name, c_pow, c_kill, c_rss
    except: return None

res = load_data()
if res:
    df, c_id, c_name, c_pow, c_kill, c_rss = res
    options_list = [""] + df['Full_Search'].tolist()
    
    # --- PHẦN ĐỈNH TRANG (STICKY) ---
    with st.container():
        st.markdown(f'<div class="main-header">{L["header"]}</div>', unsafe_allow_html=True)
        col_l, col_s = st.columns([1, 4])
        with col_l:
            st.radio("L", ["VN", "EN"], index=0 if st.session_state.lang == "VN" else 1, 
                     key="lang_radio_key", on_change=change_lang_callback, horizontal=True, label_visibility="collapsed")
        with col_s:
            choice = st.selectbox("S", options=options_list, index=st.session_state.selected_index,
                                  placeholder=L["placeholder"], label_visibility="collapsed", 
                                  key="main_search", on_change=sync_search_callback)

    tab1, tab2 = st.tabs([L["tab1"], L["tab2"]])
    
    with tab1:
        if choice != "":
            d = df[df['Full_Search'] == choice].iloc[0]
            
            # --- 4 HỘP KPI ---
            m = st.columns(4)
            m[0].markdown(f'<div class="info-box"><div class="info-label">{L["rank"]}</div><div class="info-value" style="color:#FFD700;">#{int(d["H_RAW"])}</div></div>', unsafe_allow_html=True)
            m[1].markdown(f'<div class="info-box"><div class="info-label">{L["power_now"]}</div><div class="info-value">{int(d[c_pow]):,}</div></div>', unsafe_allow_html=True)
            m[2].markdown(f'<div class="info-box"><div class="info-label">{L["kpi_kill_pct"]}</div><div class="info-value" style="color:#00FFFF;">{d["K_PCT"]}%</div></div>', unsafe_allow_html=True)
            m[3].markdown(f'<div class="info-box"><div class="info-label">{L["kpi_dead_pct"]}</div><div class="info-value" style="color:#f29b05;">{d["D_PCT"]}%</div></div>', unsafe_allow_html=True)
            
            # --- CHI TIẾT THÔNG SỐ (Bổ sung T1-T5 và RSS) ---
            with st.expander(L["detail_title"], expanded=False):
                st.markdown(f"**{L['general_stats']}**")
                g = st.columns(3)
                g[0].markdown(f'<div class="info-box"><div class="info-label">ID</div><div class="info-value">{d[c_id]}</div></div>', unsafe_allow_html=True)
                g[1].markdown(f'<div class="info-box"><div class="info-label">{L["name_label"]}</div><div class="info-value">{d[c_name]}</div></div>', unsafe_allow_html=True)
                g[2].markdown(f'<div class="info-box"><div class="info-label">{L["rss_stats"]}</div><div class="info-value">{int(d[c_rss]):,}</div></div>', unsafe_allow_html=True)

                st.markdown(f"**{L['kill_stats']}**")
                k_cols = st.columns(5)
                for i in range(5, 0, -1):
                    k_cols[5-i].markdown(f'<div class="info-box"><div class="info-label">T{i} KILL</div><div class="info-value">{int(d[f"Tổng Tiêu Diệt T{i}"]):,}</div></div>', unsafe_allow_html=True)

                st.markdown(f"**{L['dead_stats']}**")
                d_cols = st.columns(5)
                for i in range(5, 0, -1):
                    d_cols[5-i].markdown(f'<div class="info-box"><div class="info-label">T{i} DEAD</div><div class="info-value">{int(d[f"T{i} tử vong"]):,}</div></div>', unsafe_allow_html=True)

            # --- BIỂU ĐỒ GAUGE ---
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
            st.image("https://github.com/thanhdt2106/rok-kpi-3956/blob/main/meme1.png?raw=true", use_column_width=True)

    with tab2:
        v_df = df[['H_RAW', c_name, c_pow, c_kill, 'K_PCT', 'SUM_DEAD', 'D_PCT']].copy()
        v_df.columns = [L['col_rank'], L['col_name'], L['col_power'], L['col_kill'], L['col_kpi_kill'], L['col_dead'], L['col_kpi_dead']]
        st.dataframe(v_df.style.format({L['col_power']: '{:,.0f}', L['col_kill']: '{:,.0f}', L['col_dead']: '{:,.0f}', L['col_kpi_kill']: '{:.1f}%', L['col_kpi_dead']: '{:.1f}%'}), use_container_width=True, height=500)
