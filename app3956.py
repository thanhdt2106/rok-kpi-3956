import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide", initial_sidebar_state="collapsed")

# --- 2. HỆ THỐNG NGÔN NGỮ ---
lang_option = st.selectbox("🌐 Ngôn ngữ / Language:", ["VN", "EN"])

texts = {
    "VN": {
        "header": "HỆ THỐNG KPI - SHARED HOUSE 3956",
        "tab1": "👤 HỒ SƠ CHI TIẾT", "tab2": "📊 TỔNG QUAN QUÂN ĐOÀN",
        "select_player": "🔍 CHỌN CHIẾN BINH:", "rank": "🏆 HẠNG",
        "power_now": "🛡️ SỨC MẠNH", "kpi_kill_pct": "🔥 % KILL",
        "kpi_dead_pct": "💀 % DEAD", "detail_title": "##### 📌 THÔNG SỐ CHI TIẾT TỪ SHEET",
        "target_kill": "MỤC TIÊU", "target_dead": "MỤC TIÊU",
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
        "kpi_dead_pct": "💀 % DEAD", "detail_title": "##### 📌 DETAILED STATISTICS",
        "target_kill": "TARGET", "target_dead": "TARGET",
        "col_rank": "RANK 🏆", "col_name": "COMMANDER 🥷", "col_power": "POWER 🛡️",
        "col_kill": "KILL POINTS ⚔️", "col_kpi_kill": "KPI KILL 🔥",
        "col_dead": "DEAD UNITS 💀", "col_kpi_dead": "KPI DEAD ⚰️",
        "map_id": "Character ID", "map_name": "Username", "map_pow": "Power",
        "map_record": "Power Record", "map_kill": "Total Kills",
        "map_t5_k": "T5 Kills", "map_t4_k": "T4 Kills",
        "map_t5_d": "T5 Dead", "map_t4_d": "T4 Dead", "map_t3_d": "T3 Dead"
    }
}
L = texts[lang_option]

# --- 3. GIAO DIỆN CSS TỔNG LỰC ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0d1117; color: #c9d1d9; }}
    
    /* Header chính */
    .main-header {{ 
        background: linear-gradient(90deg, #00FFFF, #58a6ff); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        text-align: center; font-size: clamp(28px, 5vw, 42px); font-weight: 900; padding: 20px 0;
    }}

    /* Container cho Profile */
    .info-box {{ 
        background: #161b22; border: 1px solid #30363d; border-radius: 12px; 
        padding: 15px; text-align: center; margin-bottom: 10px;
        transition: transform 0.2s;
    }}
    .info-box:hover {{ border-color: #58a6ff; transform: translateY(-2px); }}
    .info-label {{ color: #8b949e; font-size: clamp(11px, 2.5vw, 14px); font-weight: bold; text-transform: uppercase; margin-bottom: 8px; }}
    .info-value {{ color: #ffffff; font-size: clamp(18px, 4vw, 24px); font-weight: 800; }}

    /* Gauge Footer */
    .gauge-footer {{ 
        color: #58a6ff; font-size: clamp(16px, 3.5vw, 20px); font-weight: 800; 
        text-align: center; margin-top: -30px; padding-bottom: 10px;
    }}

    /* Bảng dữ liệu */
    .big-table-container [data-testid="stDataFrame"] th {{
        background-color: #1f2937 !important; color: #00FFFF !important;
        font-size: 18px !important; font-weight: 900 !important;
    }}
    .big-table-container [data-testid="stDataFrame"] td {{
        font-size: 17px !important; font-weight: 600 !important;
    }}

    /* Điều chỉnh hiển thị cột trên Mobile */
    @media (max-width: 768px) {{
        [data-testid="column"] {{ width: 50% !important; flex: 1 1 45% !important; }}
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

        dead_list = ['T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong']
        df['SUM_DEAD'] = df[[c for c in dead_list if c in df.columns]].sum(axis=1)
        
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
        
        # --- TOP 4 BIG BOXES ---
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="info-box"><div class="info-label">{L["rank"]}</div><div class="info-value" style="color:#FFD700;">#{int(d["H_RAW"])}</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="info-box"><div class="info-label">{L["power_now"]}</div><div class="info-value">{int(d[c_pow]):,}</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="info-box"><div class="info-label">{L["kpi_kill_pct"]}</div><div class="info-value" style="color:#00FFFF;">{d["K_PCT"]}%</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="info-box"><div class="info-label">{L["kpi_dead_pct"]}</div><div class="info-value" style="color:#f29b05;">{d["D_PCT"]}%</div></div>', unsafe_allow_html=True)
        
        # --- DETAILED PROFILE (10 BOXES) ---
      # --- THÔNG SỐ CHI TIẾT DẠNG ĐÓNG MỞ (EXPANDER) ---
        with st.expander(L["detail_title"], expanded=False): # expanded=False để mặc định là đóng
            box_map = [
                (L["map_id"], "ID nhân vật"), (L["map_name"], c_name), 
                (L["map_pow"], c_pow), (L["map_record"], "Kỷ Lục Sức Mạnh"),
                (L["map_t5_d"], "T5 tử vong"), (L["map_t4_d"], "T4 tử vong"),
                (L["map_t3_d"], "T3 tử vong"), (L["map_kill"], c_kill),
                (L["map_t5_k"], "Tổng Tiêu Diệt T5"), (L["map_t4_k"], "Tổng Tiêu Diệt T4")
            ]
            
            # Chia 5 cột cho PC bên trong expander
            det_cols = st.columns(5)
            for idx, (label, col_key) in enumerate(box_map):
                val = d[col_key] if col_key in d else 0
                txt_val = f"{int(val):,}" if isinstance(val, (int, float)) else val
                
                # Hiển thị box
                det_cols[idx % 5].markdown(
                    f'''
                    <div class="info-box" style="margin-top: 10px;">
                        <div class="info-label">{label}</div>
                        <div class="info-value" style="font-size:16px;">{txt_val}</div>
                    </div>
                    ''', 
                    unsafe_allow_html=True
                )
        # --- GAUGE CHARTS ---
        g1, g2 = st.columns(2)
        with g1:
            fig_k = go.Figure(go.Indicator(mode="gauge+number", value=d['K_PCT'], number={'suffix': "%", 'font':{'size':45}}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00FFFF"}}))
            fig_k.update_layout(height=300, margin=dict(l=30,r=30,t=50,b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_k, use_container_width=True, config={'displayModeBar': False})
            st.markdown(f'<div class="gauge-footer">{L["target_kill"]}: {d[c_kill]/1e6:.1f}M / 300M</div>', unsafe_allow_html=True)
        with g2:
            fig_d = go.Figure(go.Indicator(mode="gauge+number", value=d['D_PCT'], number={'suffix': "%", 'font':{'size':45}}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#f29b05"}}))
            fig_d.update_layout(height=300, margin=dict(l=30,r=30,t=50,b=20), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_d, use_container_width=True, config={'displayModeBar': False})
            st.markdown(f'<div class="gauge-footer">{L["target_dead"]}: {int(d["SUM_DEAD"]):,} / 400K</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='big-table-container'>", unsafe_allow_html=True)
        
        # 1. Lấy dữ liệu
        v_df = df[['H_RAW', c_name, c_pow, c_kill, 'K_PCT', 'SUM_DEAD', 'D_PCT']].copy()
        
        # 2. Đặt tên cột theo ngôn ngữ
        col_rank = L['col_rank']
        col_name = L['col_name']
        col_pow = L['col_power']
        col_kill = L['col_kill']
        col_kpi_k = L['col_kpi_kill']
        col_dead = L['col_dead']
        col_kpi_d = L['col_kpi_dead']
        
        v_df.columns = [col_rank, col_name, col_pow, col_kill, col_kpi_k, col_dead, col_kpi_d]
        
        # 3. Định dạng: Số có dấu phẩy, KPI có đuôi %
        styled_df = v_df.style.format({
            col_pow: '{:,.0f}',
            col_kill: '{:,.0f}',
            col_dead: '{:,.0f}',
            col_kpi_k: '{:.1f}%', # Biến thành % (ví dụ 72.5%)
            col_kpi_d: '{:.1f}%'  # Biến thành % (ví dụ 110.2%)
        })
        
        # 4. (Tùy chọn) Tô màu cho đẹp: KPI >= 100% thì chữ màu xanh Neon
        def highlight_kpi(val):
            try:
                num = float(val)
                if num >= 100: return 'color: #00FF00;' 
                return ''
            except: return ''

        # Áp dụng màu cho 2 cột phần trăm
        styled_df = styled_df.map(highlight_kpi, subset=[col_kpi_k, col_kpi_d])
        
        # 5. Hiển thị bảng
        st.dataframe(styled_df, use_container_width=True, height=1000)
        st.markdown("</div>", unsafe_allow_html=True)
