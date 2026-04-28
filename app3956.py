import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="FTD KPI SYSTEM", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. HỆ THỐNG NGÔN NGỮ ---
TEXTS = {
    "VN": {
        "header": "HỆ THỐNG KPI - SHARED HOUSE 3956",
        "tab1": "👤 HỒ SƠ CHI TIẾT", "tab2": "📊 TỔNG QUAN QUÂN ĐOÀN",
        "select_player": "🔍 CHỌN CHIẾN BINH:", "rank": "🏆 HẠNG",
        "power_now": "🛡️ SỨC MẠNH", "kpi_kill_pct": "🔥 % KILL",
        "kpi_dead_pct": "💀 % DEAD", "detail_title": "📌 XEM THÔNG SỐ CHI TIẾT",
        "target_kill": "ĐẠT: ", "target_dead": "ĐẠT: ",
        "col_rank": "HẠNG 🏆", "col_name": "CHIẾN BINH 🥷", "col_power": "SỨC MẠNH 🛡️",
        "col_kill": "ĐIỂM KILL ⚔️", "col_kpi_kill": "KPI KILL 🔥",
        "col_dead": "LÍNH CHẾT 💀", "col_kpi_dead": "KPI DEAD ⚰️",
        "map_id": "ID nhân vật", "map_name": "Tên Người Dùng", "map_pow": "Sức Mạnh",
        "map_record": "Kỷ Lục Sức Mạnh", "map_kill": "Tổng Điểm Tiêu Diệt",
        "map_t5_k": "Tổng Tiêu Diệt T5", "map_t4_k": "Tổng Tiêu Diệt T4",
        "map_t5_d": "T5 tử vong", "map_t4_d": "T4 tử vong", "map_t3_d": "T3 tử vong"
    },
    "EN": {
        "header": "KPI SYSTEM - SHARED HOUSE 3956",
        "tab1": "👤 DETAILED PROFILE", "tab2": "📊 ALLIANCE OVERVIEW",
        "select_player": "🔍 SELECT COMMANDER:", "rank": "🏆 RANK",
        "power_now": "🛡️ POWER", "kpi_kill_pct": "🔥 % KILL",
        "kpi_dead_pct": "💀 % DEAD", "detail_title": "📌 VIEW DETAILED STATISTICS",
        "target_kill": "REACHED: ", "target_dead": "REACHED: ",
        "col_rank": "RANK 🏆", "col_name": "COMMANDER 🥷", "col_power": "POWER 🛡️",
        "col_kill": "KILL POINTS ⚔️", "col_kpi_kill": "KPI KILL 🔥",
        "col_dead": "DEAD UNITS 💀", "col_kpi_dead": "KPI DEAD ⚰️",
        "map_id": "Character ID", "map_name": "Username", "map_pow": "Power",
        "map_record": "Power Record", "map_kill": "Total Kills",
        "map_t5_k": "T5 Kills", "map_t4_k": "T4 Kills",
        "map_t5_d": "T5 Dead", "map_t4_d": "T4 Dead", "map_t3_d": "T3 Dead"
    }
}

# --- 3. GIAO DIỆN CSS TỔNG LỰC (XÓA HEADER/SIDEBAR + FIX MOBILE 2 CỘT) ---
st.markdown("""
    <style>
    /* 1. Xóa sạch Header và Sidebar */
    header[data-testid="stHeader"] {display: none !important;}
    [data-testid="stSidebarNav"] {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    
    /* 2. Màu nền và Layout */
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }

    /* 3. Tiêu đề chính */
    .main-header { 
        background: linear-gradient(90deg, #00FFFF, #58a6ff); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        text-align: center; font-size: clamp(22px, 5vw, 36px); font-weight: 900; padding: 10px 0;
    }

    /* 4. Info Boxes */
    .info-box { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 10px; text-align: center; margin-bottom: 5px; }
    .info-label { color: #8b949e; font-size: clamp(10px, 2.5vw, 12px); font-weight: bold; text-transform: uppercase; }
    .info-value { color: #ffffff; font-size: clamp(15px, 4vw, 20px); font-weight: 800; }

    /* 5. Gauge Footer */
    .gauge-footer { color: #58a6ff; font-size: clamp(11px, 3vw, 14px); font-weight: 800; text-align: center; margin-top: -35px; }

    /* 6. Bảng dữ liệu */
    .big-table-container [data-testid="stDataFrame"] th { background-color: #1f2937 !important; color: #00FFFF !important; font-size: 16px !important; }
    .big-table-container [data-testid="stDataFrame"] td { font-size: 15px !important; }

    /* 7. FIX QUAN TRỌNG: 2 CỘT TRÊN MOBILE */
    @media (max-width: 768px) {
        [data-testid="column"] {
            width: 50% !important; 
            flex: 1 1 50% !important;
            min-width: 50% !important;
        }
        div[data-testid="stHorizontalBlock"] { gap: 0px !important; }
        .js-plotly-plot .plotly .main-svg { transform: scale(1.0); transform-origin: center; }
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
        c_name = next((c for c in df.columns if 'Tên' in c or 'Name' in c), "Tên Người Dùng")
        c_pow = next((c for c in df.columns if 'Sức Mạnh' in c or 'Power' in c), "Sức Mạnh")
        c_kill = next((c for c in df.columns if 'Tiêu Diệt' in c or 'Kill' in c), "Tổng Điểm Tiêu Diệt")
        for col in [c_pow, c_kill]: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        dead_list = ['T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong']
        df['SUM_DEAD'] = df[[c for c in dead_list if c in df.columns]].sum(axis=1)
        df['K_PCT'] = (df[c_kill] / 300_000_000 * 100).round(1)
        df['D_PCT'] = (df['SUM_DEAD'] / 400_000 * 100).round(1)
        df = df.sort_values(by='K_PCT', ascending=False).reset_index(drop=True)
        df.insert(0, 'H_RAW', range(1, len(df) + 1))
        return df, c_name, c_pow, c_kill
    except: return None

res = load_data()
if res:
    df, c_name, c_pow, c_kill = res
    st.markdown(f'<div class="main-header">{TEXTS["VN"]["header"]}</div>', unsafe_allow_html=True)
    
    # Chọn ngôn ngữ (Radio nhỏ)
    lang = st.radio("Lang:", ["VN", "EN"], horizontal=True, label_visibility="collapsed")
    L = TEXTS[lang]
    
    tab1, tab2 = st.tabs([L["tab1"], L["tab2"]])
    
    with tab1:
        sel = st.selectbox(L["select_player"], df[c_name].unique())
        d = df[df[c_name] == sel].iloc[0]
        
        # 4 Chỉ số chính (2 cột trên mobile)
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="info-box"><div class="info-label">{L["rank"]}</div><div class="info-value" style="color:#FFD700;">#{int(d["H_RAW"])}</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="info-box"><div class="info-label">{L["power_now"]}</div><div class="info-value">{int(d[c_pow]):,}</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="info-box"><div class="info-label">{L["kpi_kill_pct"]}</div><div class="info-value" style="color:#00FFFF;">{d["K_PCT"]}%</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="info-box"><div class="info-label">{L["kpi_dead_pct"]}</div><div class="info-value" style="color:#f29b05;">{d["D_PCT"]}%</div></div>', unsafe_allow_html=True)
        
        # Expander thông số
        with st.expander(L["detail_title"], expanded=False):
            box_map = [(L["map_id"], "ID nhân vật"), (L["map_name"], c_name), (L["map_pow"], c_pow), (L["map_record"], "Kỷ Lục Sức Mạnh"), (L["map_t5_d"], "T5 tử vong"), (L["map_t4_d"], "T4 tử vong"), (L["map_t3_d"], "T3 tử vong"), (L["map_kill"], c_kill), (L["map_t5_k"], "Tổng Tiêu Diệt T5"), (L["map_t4_k"], "Tổng Tiêu Diệt T4")]
            det_cols = st.columns(5)
            for idx, (label, col_key) in enumerate(box_map):
                val = d[col_key] if col_key in d else 0
                txt = f"{int(val):,}" if isinstance(val, (int, float)) else val
                det_cols[idx % 5].markdown(f'<div class="info-box"><div class="info-label">{label}</div><div class="info-value" style="font-size:14px;">{txt}</div></div>', unsafe_allow_html=True)

        # 2 Vòng tròn KPI (ÉP NẰM NGANG TRÊN MOBILE)
        g1, g2 = st.columns(2)
        with g1:
            fig_k = go.Figure(go.Indicator(mode="gauge+number", value=d['K_PCT'], number={'suffix': "%", 'font':{'size':24}}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00FFFF"}}))
            fig_k.update_layout(height=180, margin=dict(l=10,r=10,t=30,b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_k, use_container_width=True, config={'displayModeBar': False})
            st.markdown(f'<div class="gauge-footer">{L["target_kill"]}{d[c_kill]/1e6:.1f}M</div>', unsafe_allow_html=True)
        with g2:
            fig_d = go.Figure(go.Indicator(mode="gauge+number", value=d['D_PCT'], number={'suffix': "%", 'font':{'size':24}}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#f29b05"}}))
            fig_d.update_layout(height=180, margin=dict(l=10,r=10,t=30,b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_d, use_container_width=True, config={'displayModeBar': False})
            st.markdown(f'<div class="gauge-footer">{L["target_dead"]}{int(d["SUM_DEAD"]/1000)}K</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='big-table-container'>", unsafe_allow_html=True)
        v_df = df[['H_RAW', c_name, c_pow, c_kill, 'K_PCT', 'SUM_DEAD', 'D_PCT']].copy()
        v_df.columns = [L['col_rank'], L['col_name'], L['col_power'], L['col_kill'], L['col_kpi_kill'], L['col_dead'], L['col_kpi_dead']]
        
        # Format bảng: Số có dấu phẩy, KPI có %
        styled_df = v_df.style.format({
            L['col_power']: '{:,.0f}', L['col_kill']: '{:,.0f}', L['col_dead']: '{:,.0f}',
            L['col_kpi_kill']: '{:.1f}%', L['col_kpi_dead']: '{:.1f}%'
        })
        # Tô màu KPI >= 100%
        styled_df = styled_df.map(lambda x: 'color: #00FF00;' if isinstance(x, (float, int)) and x >= 100 else '', subset=[L['col_kpi_kill'], L['col_kpi_dead']])
        
        st.dataframe(styled_df, use_container_width=True, height=800)
        st.markdown("</div>", unsafe_allow_html=True)
