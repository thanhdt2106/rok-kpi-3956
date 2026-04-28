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
        "header": "HỆ THỐNG KPI - SHARED HOUSE 3956",
        "tab1": "👤 HỒ SƠ CHI TIẾT", "tab2": "📊 TỔNG QUAN QUÂN ĐOÀN",
        "placeholder": "🔍 Gõ để tìm kiếm (tự động gợi ý)...",
        "rank": "🏆 HẠNG", "power_now": "🛡️ SỨC MẠNH", "kpi_kill_pct": "🔥 % KILL", "kpi_dead_pct": "💀 % DEAD",
        "detail_title": "📌 XEM THÔNG SỐ CHI TIẾT", 
        "target_kill": "ĐẠT: ", "target_dead": "ĐẠT: ",
        "general_stats": "📊 THÔNG SỐ TỔNG QUÁT",
        "col_rank": "HẠNG 🏆", "col_name": "CHIẾN BINH 🥷", "col_power": "SỨC MẠNH 🛡️",
        "col_kill": "ĐIỂM KILL ⚔️", "col_kpi_kill": "KPI KILL 🔥", "col_dead": "LÍNH CHẾT 💀", "col_kpi_dead": "KPI DEAD ⚰️",
        "id_label": "ID nhân vật", "name_label": "Tên Người Dùng"
    },
    "EN": {
        "header": "KPI SYSTEM - SHARED HOUSE 3956",
        "tab1": "👤 DETAILED PROFILE", "tab2": "📊 ALLIANCE OVERVIEW",
        "placeholder": "🔍 Type to search (auto-suggest)...",
        "rank": "🏆 RANK", "power_now": "🛡️ POWER", "kpi_kill_pct": "🔥 % KILL", "kpi_dead_pct": "💀 % DEAD",
        "detail_title": "📌 VIEW FULL STATISTICS", 
        "target_kill": "REACHED: ", "target_dead": "REACHED: ",
        "general_stats": "📊 GENERAL STATISTICS",
        "col_rank": "RANK 🏆", "col_name": "COMMANDER 🥷", "col_power": "POWER 🛡️",
        "col_kill": "KILL POINTS ⚔️", "col_kpi_kill": "KPI KILL 🔥", "col_dead": "DEAD UNITS 💀", "col_kpi_dead": "KPI DEAD ⚰️",
        "id_label": "Character ID", "name_label": "Username"
    }
}

# --- 4. CALLBACKS ---
def change_lang_callback():
    st.session_state.lang = st.session_state.lang_radio_key

def sync_search_callback():
    if 'main_search' in st.session_state:
        # Không cần xử lý index phức tạp vì danh sách lọc sẽ thay đổi liên tục
        pass

L = TEXTS[st.session_state.lang]

# --- 5. CSS CUSTOM ---
st.markdown(f"""
    <style>
    header[data-testid="stHeader"] {{display: none !important;}}
    .stApp {{ background-color: #0d1117; color: #c9d1d9; }}
    .main-header {{ 
        background: linear-gradient(90deg, #00FFFF, #58a6ff); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        text-align: center; font-size: clamp(22px, 5vw, 32px); font-weight: 900; padding-bottom: 15px;
    }}
    .info-box {{ background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 10px; text-align: center; margin-bottom: 8px; min-height: 70px; }}
    .info-label {{ color: #8b949e; font-size: 11px; font-weight: bold; text-transform: uppercase; }}
    .info-value {{ color: #ffffff; font-size: 16px; font-weight: 800; }}
    .gauge-footer {{ color: #58a6ff; font-size: 13px; font-weight: 800; text-align: center; margin-top: -35px; }}
    </style>
""", unsafe_allow_html=True)

# --- 6. DATA ENGINE ---
@st.cache_data(ttl=5)
def load_data():
    try:
        URL = 'https://docs.google.com/spreadsheets/d/1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE/export?format=csv&gid=351056493'
        df = pd.read_csv(URL)
        df.columns = [str(c).strip() for c in df.columns]
        c_id, c_name, c_pow, c_kill = "ID nhân vật", "Tên Người Dùng", "Sức Mạnh", "Tổng Điểm Tiêu Diệt"
        dead_cols = ['T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong']
        for col in [c_pow, c_kill] + dead_cols: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df['SUM_DEAD'] = df[dead_cols].sum(axis=1)
        df['K_PCT'] = (df[c_kill] / 300_000_000 * 100).round(1)
        df['D_PCT'] = (df['SUM_DEAD'] / 400_000 * 100).round(1)
        df = df.sort_values(by='K_PCT', ascending=False).reset_index(drop=True)
        df.insert(0, 'H_RAW', range(1, len(df) + 1))
        df['Full_Search'] = df[c_name] + " (ID: " + df[c_id].astype(str) + ")"
        return df, c_id, c_name, c_pow, c_kill
    except Exception as e:
        st.error(f"Lỗi tải dữ liệu: {e}")
        return None

res = load_data()

if res:
    df, c_id, c_name, c_pow, c_kill = res
    options_list = df['Full_Search'].tolist()
    
    st.markdown(f'<div class="main-header">{L["header"]}</div>', unsafe_allow_html=True)
    
    col_lang, col_search = st.columns([1, 4])
    with col_lang:
        st.radio("L", ["VN", "EN"], 
                 index=0 if st.session_state.lang == "VN" else 1, 
                 key="lang_radio_key", on_change=change_lang_callback,
                 horizontal=True, label_visibility="collapsed")
    
   with col_search:
        # 1. Tạo danh sách gợi ý (luôn đầy đủ để Streamlit có thể lọc khi gõ)
        # Thêm một khoảng trắng ở đầu để làm giá trị mặc định
        search_options = [""] + options_list
        
        # 2. CSS để ẩn danh sách menu xổ xuống khi chưa gõ gì
        # Nếu giá trị là "" (trống), menu sẽ bị ẩn đi bằng CSS
        current_val = st.session_state.get("main_search", "")
        if current_val == "" or current_val is None:
            st.markdown("""
                <style>
                    div[data-baseweb="popover"] { display: none; }
                </style>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <style>
                    div[data-baseweb="popover"] { display: block; }
                </style>
            """, unsafe_allow_html=True)

        # 3. Widget Selectbox
        choice = st.selectbox(
            "Search",
            options=search_options,
            index=0,
            placeholder=L["placeholder"],
            label_visibility="collapsed",
            key="main_search"
        )

    tab1, tab2 = st.tabs([L["tab1"], L["tab2"]])
    
    with tab1:
        if choice and choice != "":
            d = df[df['Full_Search'] == choice].iloc[0]
            
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f'<div class="info-box"><div class="info-label">{L["rank"]}</div><div class="info-value" style="color:#FFD700;">#{int(d["H_RAW"])}</div></div>', unsafe_allow_html=True)
            m2.markdown(f'<div class="info-box"><div class="info-label">{L["power_now"]}</div><div class="info-value">{int(d[c_pow]):,}</div></div>', unsafe_allow_html=True)
            m3.markdown(f'<div class="info-box"><div class="info-label">{L["kpi_kill_pct"]}</div><div class="info-value" style="color:#00FFFF;">{d["K_PCT"]}%</div></div>', unsafe_allow_html=True)
            m4.markdown(f'<div class="info-box"><div class="info-label">{L["kpi_dead_pct"]}</div><div class="info-value" style="color:#f29b05;">{d["D_PCT"]}%</div></div>', unsafe_allow_html=True)
            
            with st.expander(L["detail_title"], expanded=False):
                st.markdown(f"**{L['general_stats']}**")
                c_cols = st.columns(5)
                c_cols[0].markdown(f'<div class="info-box"><div class="info-label">ID</div><div class="info-value">{d[c_id]}</div></div>', unsafe_allow_html=True)
                c_cols[1].markdown(f'<div class="info-box"><div class="info-label">{L["name_label"]}</div><div class="info-value">{d[c_name]}</div></div>', unsafe_allow_html=True)
                c_cols[2].markdown(f'<div class="info-box"><div class="info-label">{L["power_now"]}</div><div class="info-value">{int(d[c_pow]):,}</div></div>', unsafe_allow_html=True)
                c_cols[3].markdown(f'<div class="info-box"><div class="info-label">Total Kill</div><div class="info-value">{int(d[c_kill]):,}</div></div>', unsafe_allow_html=True)
                c_cols[4].markdown(f'<div class="info-box"><div class="info-label">Total Dead</div><div class="info-value">{int(d["SUM_DEAD"]):,}</div></div>', unsafe_allow_html=True)

            g1, g2 = st.columns(2)
            with g1:
                fig_k = go.Figure(go.Indicator(mode="gauge+number", value=d['K_PCT'], number={'suffix': "%", 'font':{'size':24}}, gauge={'bar': {'color': "#00FFFF"}, 'axis': {'range': [0, 100]}}))
                fig_k.update_layout(height=200, margin=dict(l=15,r=15,t=40,b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_k, use_container_width=True, config={'displayModeBar': False})
                st.markdown(f'<div class="gauge-footer">{L["target_kill"]}{d[c_kill]/1e6:.1f}M / 300M</div>', unsafe_allow_html=True)
            with g2:
                fig_d = go.Figure(go.Indicator(mode="gauge+number", value=d['D_PCT'], number={'suffix': "%", 'font':{'size':24}}, gauge={'bar': {'color': "#f29b05"}, 'axis': {'range': [0, 100]}}))
                fig_d.update_layout(height=200, margin=dict(l=15,r=15,t=40,b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_d, use_container_width=True, config={'displayModeBar': False})
                st.markdown(f'<div class="gauge-footer">{L["target_dead"]}{int(d["SUM_DEAD"]/1000)}K / 400K</div>', unsafe_allow_html=True)
        else:
            st.image("https://github.com/thanhdt2106/rok-kpi-3956/blob/main/meme2.png?raw=true", use_container_width=True)

    with tab2:
        v_df = df[['H_RAW', c_name, c_pow, c_kill, 'K_PCT', 'SUM_DEAD', 'D_PCT']].copy()
        v_df.columns = [L['col_rank'], L['col_name'], L['col_power'], L['col_kill'], L['col_kpi_kill'], L['col_dead'], L['col_kpi_dead']]
        st.dataframe(v_df.style.format({
            L['col_power']: '{:,.0f}', 
            L['col_kill']: '{:,.0f}', 
            L['col_dead']: '{:,.0f}', 
            L['col_kpi_kill']: '{:.1f}%', 
            L['col_kpi_dead']: '{:.1f}%'
        }), use_container_width=True, height=600)
