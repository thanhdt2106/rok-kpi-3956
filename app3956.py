import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide", initial_sidebar_state="collapsed")

# --- 2. HỆ THỐNG NGÔN NGỮ ---
lang_option = st.selectbox("🌐 Ngôn ngữ / Language:", ["VN", "EN"])

texts = {
    "VN": {
        "header": "HỆ THỐNG QUẢN LÝ KPI - SHARED HOUSE 3956",
        "tab1": "👤 HỒ SƠ CHI TIẾT", "tab2": "📊 TỔNG QUAN QUÂN ĐOÀN",
        "select_player": "🔍 CHỌN CHIẾN BINH:", "rank": "🏆 HẠNG (THEO KILL)",
        "power_now": "🛡️ SỨC MẠNH HIỆN TẠI", "kpi_kill_pct": "🔥 % HOÀN THÀNH KILL",
        "kpi_dead_pct": "💀 % HOÀN THÀNH DEAD", "detail_title": "##### 📌 THÔNG SỐ CHI TIẾT",
        "target_kill": "ĐẠT", "target_dead": "ĐẠT",
        "table_title": "🏆 BẢNG THỐNG KÊ CHI TIẾT TOÀN QUÂN",
        "col_rank": "HẠNG 🏆", "col_name": "CHIẾN BINH 🥷", "col_power": "SỨC MẠNH 🛡️",
        "col_kill": "ĐIỂM KILL ⚔️", "col_kpi_kill": "KPI KILL 🔥",
        "col_dead": "LÍNH CHẾT 💀", "col_kpi_dead": "KPI DEAD ⚰️",
        # Mapping chi tiết cho Box
        "map_id": "ID nhân vật", "map_name": "Tên Người Dùng", "map_pow": "Sức Mạnh",
        "map_record": "Kỷ Lục Sức Mạnh", "map_kill": "Tổng Điểm Tiêu Diệt",
        "map_t5_k": "Tổng Tiêu Diệt T5", "map_t4_k": "Tổng Tiêu Diệt T4",
        "map_t5_d": "T5 tử vong", "map_t4_d": "T4 tử vong", "map_t3_d": "T3 tử vong"
    },
    "EN": {
        "header": "KPI MANAGEMENT SYSTEM - SHARED HOUSE 3956",
        "tab1": "👤 DETAILED PROFILE", "tab2": "📊 ALLIANCE OVERVIEW",
        "select_player": "🔍 SELECT COMMANDER:", "rank": "🏆 RANK (BY KILL)",
        "power_now": "🛡️ CURRENT POWER", "kpi_kill_pct": "🔥 % KILL PROGRESS",
        "kpi_dead_pct": "💀 % DEAD PROGRESS", "detail_title": "##### 📌 DETAILED STATISTICS",
        "target_kill": "REACHED", "target_dead": "REACHED",
        "table_title": "🏆 ALLIANCE DETAILED STATISTICS TABLE",
        "col_rank": "RANK 🏆", "col_name": "COMMANDER 🥷", "col_power": "POWER 🛡️",
        "col_kill": "KILL POINTS ⚔️", "col_kpi_kill": "KPI KILL 🔥",
        "col_dead": "DEAD UNITS 💀", "col_kpi_dead": "KPI DEAD ⚰️",
        # Mapping chi tiết cho Box
        "map_id": "Character ID", "map_name": "Username", "map_pow": "Power",
        "map_record": "Power Record", "map_kill": "Total Kills",
        "map_t5_k": "T5 Kills", "map_t4_k": "T4 Kills",
        "map_t5_d": "T5 Dead", "map_t4_d": "T4 Dead", "map_t3_d": "T3 Dead"
    }
}
L = texts[lang_option]

# --- 3. GIAO DIỆN CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0d1117; color: #c9d1d9; }}
    .main-header {{ background: linear-gradient(90deg, #00FFFF, #58a6ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; font-size: 40px; font-weight: 900; padding: 10px; }}
    .info-box {{ background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 15px; text-align: center; margin-bottom: 10px; min-height: 100px; }}
    .info-label {{ color: #8b949e; font-size: 13px; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }}
    .info-value {{ color: #ffffff; font-size: 19px; font-weight: bold; }}
    .gauge-footer {{ color: #58a6ff; font-size: 20px; font-weight: 800; text-align: center; margin-top: -30px; padding-bottom: 20px; }}
    .big-table-container [data-testid="stDataFrame"] th {{ background-color: #1f2937 !important; color: #00FFFF !important; font-size: 22px !important; font-weight: 900 !important; }}
    .big-table-container [data-testid="stDataFrame"] td {{ font-size: 20px !important; font-weight: 700 !important; }}
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
        # Tìm cột thông minh
        c_name = next((c for c in df.columns if 'Tên' in c or 'Name' in c), "Tên Người Dùng")
        c_pow = next((c for c in df.columns if 'Sức Mạnh' in c or 'Power' in c), "Sức Mạnh")
        c_kill = next((c for c in df.columns if 'Tiêu Diệt' in c or 'Kill' in c), "Tổng Điểm Tiêu Diệt")
        
        for col in [c_pow, c_kill]:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        dead_cols = ['T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong']
        df['SUM_DEAD'] = df[[c for c in dead_cols if c in df.columns]].sum(axis=1)
        
        # Mốc KPI đơn giản
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
        
        # 4 BOX CHÍNH
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="info-box"><div class="info-label">{L["rank"]}</div><div class="info-value" style="color:#FFD700; font-size:28px;">#{int(d["H_RAW"])}</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="info-box"><div class="info-label">{L["power_now"]}</div><div class="info-value">{int(d[c_pow]):,}</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="info-box"><div class="info-label">{L["kpi_kill_pct"]}</div><div class="info-value" style="color:#00FFFF;">{d["K_PCT"]}%</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="info-box"><div class="info-label">{L["kpi_dead_pct"]}</div><div class="info-value" style="color:#f29b05;">{d["D_PCT"]}%</div></div>', unsafe_allow_html=True)
        
        # BOX CHI TIẾT (ĐÃ DỊCH NHÃN)
        st.markdown(L["detail_title"], unsafe_allow_html=True)
        # Cấu trúc: (Tên hiển thị từ Dictionary, Tên cột gốc trong DataFrame)
        box_map = [
            (L["map_id"], "ID nhân vật"), (L["map_name"], c_name), 
            (L["map_pow"], c_pow), (L["map_record"], "Kỷ Lục Sức Mạnh"),
            (L["map_t5_d"], "T5 tử vong"), (L["map_t4_d"], "T4 tử vong"),
            (L["map_t3_d"], "T3 tử vong"), (L["map_kill"], c_kill),
            (L["map_t5_k"], "Tổng Tiêu Diệt T5"), (L["map_t4_k"], "Tổng Tiêu Diệt T4")
        ]
        
        cols = st.columns(5)
        for idx, (label, col_key) in enumerate(box_map):
            val = d[col_key] if col_key in d else "N/A"
            txt_val = f"{int(val):,}" if isinstance(val, (int, float)) else val
            cols[idx % 5].markdown(f'<div class="info-box"><div class="info-label">{label}</div><div class="info-value" style="font-size:15px;">{txt_val}</div></div>', unsafe_allow_html=True)

        # VÒNG TRÒN
        g1, g2 = st.columns(2)
        with g1:
            fig_k = go.Figure(go.Indicator(mode="gauge+number", value=d['K_PCT'], number={'suffix': "%"}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00FFFF"}}))
            fig_k.update_layout(height=350, paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_k, use_container_width=True)
            st.markdown(f'<div class="gauge-footer">{L["target_kill"]}: {d[c_kill]/1e6:.1f}M / 300.0M KILL</div>', unsafe_allow_html=True)
        with g2:
            fig_d = go.Figure(go.Indicator(mode="gauge+number", value=d['D_PCT'], number={'suffix': "%"}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#f29b05"}}))
            fig_d.update_layout(height=350, paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_d, use_container_width=True)
            st.markdown(f'<div class="gauge-footer">{L["target_dead"]}: {int(d["SUM_DEAD"]):,} / 400,000 DEAD</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='big-table-container'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center; color: #58a6ff;'>{L['table_title']}</h2>", unsafe_allow_html=True)
        v_df = df[['H_RAW', c_name, c_pow, c_kill, 'K_PCT', 'SUM_DEAD', 'D_PCT']].copy()
        v_df.columns = [L['col_rank'], L['col_name'], L['col_power'], L['col_kill'], L['col_kpi_kill'], L['col_dead'], L['col_kpi_dead']]
        st.dataframe(v_df.style.format({L['col_power']: '{:,.0f}', L['col_kill']: '{:,.0f}', L['col_dead']: '{:,.0f}'}), use_container_width=True, height=800)
        st.markdown("</div>", unsafe_allow_html=True)
