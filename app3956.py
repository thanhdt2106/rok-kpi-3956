import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide", initial_sidebar_state="collapsed")

# --- 2. HỆ THỐNG NGÔN NGỮ ---
lang_option = st.selectbox("🌐 Ngôn ngữ / Language:", ["VN", "EN"])

texts = {
    "VN": {
        "header": "HỆ THỐNG KPI - 3956",
        "tab1": "👤 CHI TIẾT", "tab2": "📊 TỔNG QUAN",
        "select_player": "🔍 CHỌN CHIẾN BINH:", "rank": "🏆 HẠNG",
        "power_now": "🛡️ SỨC MẠNH", "kpi_kill_pct": "🔥 % KILL",
        "kpi_dead_pct": "💀 % DEAD", "detail_title": "##### 📌 THÔNG SỐ CHI TIẾT",
        "target_kill": "ĐẠT", "target_dead": "ĐẠT",
        "table_title": "🏆 BẢNG THỐNG KÊ QUÂN ĐOÀN",
        "col_rank": "HẠNG", "col_name": "TÊN", "col_power": "SỨC MẠNH",
        "col_kill": "KILL", "col_kpi_kill": "% KILL",
        "col_dead": "DEAD", "col_kpi_dead": "% DEAD",
        "map_id": "ID", "map_name": "Tên", "map_pow": "Sức Mạnh",
        "map_record": "Kỷ Lục", "map_kill": "Tổng Kill",
        "map_t5_k": "Kill T5", "map_t4_k": "Kill T4",
        "map_t5_d": "Chết T5", "map_t4_d": "Chết T4", "map_t3_d": "Chết T3"
    },
    "EN": {
        "header": "KPI SYSTEM - 3956",
        "tab1": "👤 PROFILE", "tab2": "📊 OVERVIEW",
        "select_player": "🔍 SELECT PLAYER:", "rank": "🏆 RANK",
        "power_now": "🛡️ POWER", "kpi_kill_pct": "🔥 % KILL",
        "kpi_dead_pct": "💀 % DEAD", "detail_title": "##### 📌 DETAILED STATS",
        "target_kill": "HIT", "target_dead": "HIT",
        "table_title": "🏆 ALLIANCE STATISTICS",
        "col_rank": "RANK", "col_name": "NAME", "col_power": "POWER",
        "col_kill": "KILL", "col_kpi_kill": "% KILL",
        "col_dead": "DEAD", "col_kpi_dead": "% DEAD",
        "map_id": "ID", "map_name": "Name", "map_pow": "Power",
        "map_record": "Record", "map_kill": "Total Kills",
        "map_t5_k": "T5 Kills", "map_t4_k": "T4 Kills",
        "map_t5_d": "T5 Dead", "map_t4_d": "T4 Dead", "map_t3_d": "T3 Dead"
    }
}
L = texts[lang_option]

# --- 3. GIAO DIỆN CSS TỰ ĐỘNG KHỚP MÀN HÌNH (RESPONSIVE) ---
st.markdown(f"""
    <style>
    /* Tổng thể app */
    .stApp {{ background-color: #0d1117; color: #c9d1d9; }}
    
    /* Responsive cho các cột */
    [data-testid="column"] {{
        width: 100% !important;
        flex: 1 1 calc(25% - 1rem) !important;
        min-width: 150px !important;
    }}

    /* Header chính to và rõ */
    .main-header {{ 
        background: linear-gradient(90deg, #00FFFF, #58a6ff); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        text-align: center; font-size: clamp(24px, 8vw, 45px); font-weight: 900; 
        padding: 15px 0;
    }}

    /* Box thông tin - Phóng to chữ */
    .info-box {{ 
        background: #161b22; border: 2px solid #30363d; border-radius: 12px; 
        padding: 20px 10px; text-align: center; margin-bottom: 15px;
    }}
    .info-label {{ color: #8b949e; font-size: clamp(12px, 3vw, 15px); font-weight: bold; text-transform: uppercase; }}
    .info-value {{ color: #ffffff; font-size: clamp(18px, 5vw, 26px); font-weight: 800; margin-top: 5px; }}
    
    /* Vòng tròn Gauge */
    .gauge-footer {{ 
        color: #58a6ff; font-size: clamp(16px, 4vw, 22px); font-weight: 800; 
        text-align: center; margin-top: -40px;
    }}

    /* Bảng dữ liệu siêu to */
    .big-table-container [data-testid="stDataFrame"] th {{
        background-color: #1f2937 !important; color: #00FFFF !important;
        font-size: clamp(16px, 3vw, 22px) !important; font-weight: 900 !important;
    }}
    .big-table-container [data-testid="stDataFrame"] td {{
        font-size: clamp(14px, 2.5vw, 20px) !important; font-weight: 600 !important;
    }}

    /* Mobile fix cho Tabs */
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{ 
        font-size: clamp(14px, 4vw, 18px) !important; 
        padding: 10px 20px !important;
    }}
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
        
        for col in [c_pow, c_kill]:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        dead_cols = ['T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong']
        df['SUM_DEAD'] = df[[c for c in dead_cols if c in df.columns]].sum(axis=1)
        
        df['T_KILL'] = 300_000_000
        df['T_DEAD'] = 400_000
        df['K_PCT'] = (df[c_kill] / df['T_KILL'] * 100).round(1)
        df['D_PCT'] = (df['SUM_DEAD'] / df['T_DEAD'] * 100).round(1)
        
        df = df.sort_values(by='K_PCT', ascending=False).reset_index(drop=True)
        df.insert(0, 'H_RAW', range(1, len(df) + 1))
        return df, c_name, c_pow, c_kill
    except: return None

res = load_data()
if res:
    df, c_name, c_pow, c_kill = res
    st.markdown(f'<div class="main-header">{L["header"]}</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs([L["tab1"], L["tab2"]])
    
    with tab1:
        sel = st.selectbox(L["select_player"], df[c_name].unique())
        d = df[df[c_name] == sel].iloc[0]
        
        # 4 BOX CHÍNH - Tự động xuống dòng trên Mobile
        m1, m2, m3, m4 = st.columns([1,1,1,1])
        m1.markdown(f'<div class="info-box"><div class="info-label">{L["rank"]}</div><div class="info-value" style="color:#FFD700;">#{int(d["H_RAW"])}</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="info-box"><div class="info-label">{L["power_now"]}</div><div class="info-value">{int(d[c_pow]):,}</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="info-box"><div class="info-label">{L["kpi_kill_pct"]}</div><div class="info-value" style="color:#00FFFF;">{d["K_PCT"]}%</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="info-box"><div class="info-label">{L["kpi_dead_pct"]}</div><div class="info-value" style="color:#f29b05;">{d["D_PCT"]}%</div></div>', unsafe_allow_html=True)
        
        # CHI TIẾT BOX (Nhỏ hơn một chút để vừa màn hình điện thoại)
        st.markdown(L["detail_title"])
        box_map = [
            (L["map_id"], "ID nhân vật"), (L["map_name"], c_name), 
            (L["map_pow"], c_pow), (L["map_record"], "Kỷ Lục Sức Mạnh"),
            (L["map_t5_d"], "T5 tử vong"), (L["map_t4_d"], "T4 tử vong"),
            (L["map_t3_d"], "T3 tử vong"), (L["map_kill"], c_kill),
            (L["map_t5_k"], "Tổng Tiêu Diệt T5"), (L["map_t4_k"], "Tổng Tiêu Diệt T4")
        ]
        
        detail_cols = st.columns(2) # Chia đôi màn hình trên mobile là đẹp nhất
        for idx, (label, col_key) in enumerate(box_map):
            val = d[col_key] if col_key in d else "0"
            txt_val = f"{int(val):,}" if isinstance(val, (int, float)) else val
            detail_cols[idx % 2].markdown(f'<div class="info-box" style="min-height:80px; padding:10px;"><div class="info-label" style="font-size:11px;">{label}</div><div class="info-value" style="font-size:16px;">{txt_val}</div></div>', unsafe_allow_html=True)

        # GAUGE
        g1, g2 = st.columns(2)
        with g1:
            fig_k = go.Figure(go.Indicator(mode="gauge+number", value=d['K_PCT'], number={'suffix': "%", 'font':{'size':40}}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00FFFF"}}))
            fig_k.update_layout(height=280, margin=dict(l=20,r=20,t=40,b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_k, use_container_width=True, config={'displayModeBar': False})
            st.markdown(f'<div class="gauge-footer">{int(d[c_kill]/1e6)}M / 300M</div>', unsafe_allow_html=True)
        with g2:
            fig_d = go.Figure(go.Indicator(mode="gauge+number", value=d['D_PCT'], number={'suffix': "%", 'font':{'size':40}}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#f29b05"}}))
            fig_d.update_layout(height=280, margin=dict(l=20,r=20,t=40,b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_d, use_container_width=True, config={'displayModeBar': False})
            st.markdown(f'<div class="gauge-footer">{int(d["SUM_DEAD"]):,} / 400K</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='big-table-container'>", unsafe_allow_html=True)
        v_df = df[['H_RAW', c_name, c_pow, c_kill, 'K_PCT', 'SUM_DEAD', 'D_PCT']].copy()
        v_df.columns = [L['col_rank'], L['col_name'], L['col_power'], L['col_kill'], L['col_kpi_kill'], L['col_dead'], L['col_kpi_dead']]
        st.dataframe(v_df.style.format({L['col_power']: '{:,.0f}', L['col_kill']: '{:,.0f}', L['col_dead']: '{:,.0f}'}), use_container_width=True, height=600)
        st.markdown("</div>", unsafe_allow_html=True)
