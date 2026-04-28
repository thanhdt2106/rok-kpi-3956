import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide", initial_sidebar_state="collapsed")

# --- 2. HỆ THỐNG NGÔN NGỮ (DICTIONARY) ---
lang_option = st.selectbox("🌐 Ngôn ngữ / Language:", ["VN", "EN"])

texts = {
    "VN": {
        "header": "HỆ THỐNG QUẢN LÝ KPI - SHARED HOUSE 3956",
        "tab1": "👤 HỒ SƠ CHI TIẾT",
        "tab2": "📊 TỔNG QUAN QUÂN ĐOÀN",
        "select_player": "🔍 CHỌN CHIẾN BINH:",
        "rank": "🏆 HẠNG (THEO KILL)",
        "power_now": "🛡️ SỨC MẠNH HIỆN TẠI",
        "kpi_kill_pct": "🔥 % HOÀN THÀNH KILL",
        "kpi_dead_pct": "💀 % HOÀN THÀNH DEAD",
        "detail_title": "##### 📌 THÔNG SỐ CHI TIẾT TỪ HỆ THỐNG",
        "target_kill": "ĐẠT",
        "target_dead": "ĐẠT",
        "table_title": "🏆 BẢNG THỐNG KÊ CHI TIẾT TOÀN QUÂN",
        "col_rank": "HẠNG 🏆",
        "col_name": "CHIẾN BINH 🥷",
        "col_power": "SỨC MẠNH 🛡️",
        "col_kill": "ĐIỂM KILL ⚔️",
        "col_kpi_kill": "KPI KILL 🔥",
        "col_dead": "LÍNH CHẾT 💀",
        "col_kpi_dead": "KPI DEAD ⚰️",
        "loading_error": "Lỗi: Không thể tải dữ liệu từ Google Sheet!"
    },
    "EN": {
        "header": "KPI MANAGEMENT SYSTEM - SHARED HOUSE 3956",
        "tab1": "👤 DETAILED PROFILE",
        "tab2": "📊 ALLIANCE OVERVIEW",
        "select_player": "🔍 SELECT COMMANDER:",
        "rank": "🏆 RANK (BY KILL)",
        "power_now": "🛡️ CURRENT POWER",
        "kpi_kill_pct": "🔥 % KILL PROGRESS",
        "kpi_dead_pct": "💀 % DEAD PROGRESS",
        "detail_title": "##### 📌 DETAILED STATISTICS FROM SYSTEM",
        "target_kill": "REACHED",
        "target_dead": "REACHED",
        "table_title": "🏆 ALLIANCE DETAILED STATISTICS TABLE",
        "col_rank": "RANK 🏆",
        "col_name": "COMMANDER 🥷",
        "col_power": "POWER 🛡️",
        "col_kill": "KILL POINTS ⚔️",
        "col_kpi_kill": "KPI KILL 🔥",
        "col_dead": "DEAD UNITS 💀",
        "col_kpi_dead": "KPI DEAD ⚰️",
        "loading_error": "Error: Could not load data from Google Sheet!"
    }
}

L = texts[lang_option]

# --- 3. GIAO DIỆN CSS TỔNG LỰC ---
st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{display: none;}}
    [data-testid="stHeader"] {{background: rgba(0,0,0,0);}}
    .stApp {{ background-color: #0d1117; color: #c9d1d9; }}
    
    .main-header {{ 
        background: linear-gradient(90deg, #00FFFF, #58a6ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; font-size: 45px; font-weight: 900; padding: 10px;
    }}

    .info-box {{ 
        background: #161b22; border: 1px solid #30363d; border-radius: 10px; 
        padding: 15px; text-align: center; margin-bottom: 10px; min-height: 100px;
    }}
    .info-label {{ color: #8b949e; font-size: 13px; font-weight: bold; text-transform: uppercase; margin-bottom: 5px;}}
    .info-value {{ color: #ffffff; font-size: 20px; font-weight: bold; }}
    
    .gauge-footer {{ 
        color: #58a6ff; font-size: 20px; font-weight: 800; text-align: center; 
        margin-top: -30px; padding-bottom: 20px;
    }}

    .big-table-container [data-testid="stDataFrame"] th {{
        background-color: #1f2937 !important;
        color: #00FFFF !important;
        font-size: 24px !important;
        font-weight: 900 !important;
        height: 70px !important;
        text-align: center !important;
    }}
    .big-table-container [data-testid="stDataFrame"] td {{
        font-size: 22px !important;
        font-weight: 700 !important;
        height: 60px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIC MỐC KPI ---
def get_targets(pow_val):
    p_mil = pow_val / 1_000_000
    if p_mil < 15: return 100_000_000, 200_000
    elif p_mil < 20: return 200_000_000, 250_000
    elif p_mil < 30: return 250_000_000, 300_000
    else: return 300_000_000, 400_000

# --- 5. DATA ENGINE ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
URL = f'https://docs.google.com/spreadsheets/d/{{SHEET_ID}}/export?format=csv&gid=351056493'

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(URL.format(SHEET_ID=SHEET_ID))
        df.columns = [str(c).strip() for c in df.columns]
        c_name = next((c for c in df.columns if 'Tên' in c or 'Name' in c), None)
        c_pow = next((c for c in df.columns if 'Kỷ Lục' in c or 'Power' in c or 'Sức Mạnh' in c), None)
        c_kill = next((c for c in df.columns if 'Tổng Điểm Tiêu Diệt' in c or 'Total Kill' in c), None)

        for col in [c_pow, c_kill]:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        dead_cols = ['T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong']
        df['SUM_DEAD'] = df[[c for c in dead_cols if c in df.columns]].sum(axis=1)
        
        targets = df[c_pow].apply(get_targets)
        df['T_KILL'] = [x[0] for x in targets]
        df['T_DEAD'] = [x[1] for x in targets]
        df['K_PCT'] = (df[c_kill] / df['T_KILL'] * 100).round(1)
        df['D_PCT'] = (df['SUM_DEAD'] / df['T_DEAD'] * 100).round(1)
        
        df = df.sort_values(by='K_PCT', ascending=False).reset_index(drop=True)
        df.insert(0, 'HẠNG_RAW', range(1, len(df) + 1))
        return df, c_name, c_pow, c_kill
    except Exception as e:
        return None

res = load_data()
if res:
    df, c_name, c_pow, c_kill = res
    st.markdown(f'<div class="main-header">{L["header"]}</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs([L["tab1"], L["tab2"]])
    
    with tab1:
        sel = st.selectbox(L["select_player"], df[c_name].unique())
        d = df[df[c_name] == sel].iloc[0]
        
        # 4 BOX CHÍNH
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f'<div class="info-box"><div class="info-label">{L["rank"]}</div><div class="info-value" style="color:#FFD700; font-size:30px;">#{int(d["HẠNG_RAW"])}</div></div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="info-box"><div class="info-label">{L["power_now"]}</div><div class="info-value">{{int(d[c_pow]):,}}</div></div>', unsafe_allow_html=True)
        col3.markdown(f'<div class="info-box"><div class="info-label">{L["kpi_kill_pct"]}</div><div class="info-value" style="color:#00FFFF;">{d["K_PCT"]}%</div></div>', unsafe_allow_html=True)
        col4.markdown(f'<div class="info-box"><div class="info-label">{L["kpi_dead_pct"]}</div><div class="info-value" style="color:#f29b05;">{d["D_PCT"]}%</div></div>', unsafe_allow_html=True)
        
        # BOX CHI TIẾT
        st.markdown(L["detail_title"], unsafe_allow_html=True)
        detail_cols = ['ID nhân vật', c_name, 'Sức Mạnh', c_pow, 'T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong', c_kill, 'Tổng Tiêu Diệt T5', 'Tổng Tiêu Diệt T4']
        rows = [detail_cols[i:i + 6] for i in range(0, len(detail_cols), 6)]
        for row in rows:
            cols = st.columns(6)
            for i, field in enumerate(row):
                if field in d:
                    val = d[field]
                    display_val = f"{int(val):,}" if isinstance(val, (int, float)) else val
                    cols[i].markdown(f'<div class="info-box"><div class="info-label">{field}</div><div class="info-value" style="font-size:15px;">{display_val}</div></div>', unsafe_allow_html=True)

        # 2 VÒNG TRÒN
        g1, g2 = st.columns(2)
        with g1:
            fig_k = go.Figure(go.Indicator(mode="gauge+number", value=d['K_PCT'], number={'suffix': "%", 'font': {'size': 80}}, title={'text': "KPI KILL", 'font': {'size': 30}}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00FFFF"}}))
            fig_k.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_k, use_container_width=True)
            st.markdown(f'<div class="gauge-footer">{L["target_kill"]}: {d[c_kill]/1e6:.1f}M / {d["T_KILL"]/1e6:.1f}M KILL</div>', unsafe_allow_html=True)
        with g2:
            fig_d = go.Figure(go.Indicator(mode="gauge+number", value=d['D_PCT'], number={'suffix': "%", 'font': {'size': 80}}, title={'text': "KPI DEAD", 'font': {'size': 30}}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#f29b05"}}))
            fig_d.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_d, use_container_width=True)
            st.markdown(f'<div class="gauge-footer">{L["target_dead"]}: {int(d["SUM_DEAD"]):,} / {int(d["T_DEAD"]):,} DEAD</div>', unsafe_allow_html=True)

    with t2:
        st.markdown("<div class='big-table-container'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center; color: #58a6ff;'>{L['table_title']}</h2>", unsafe_allow_html=True)
        
        view_df = df[['HẠNG_RAW', c_name, c_pow, c_kill, 'K_PCT', 'SUM_DEAD', 'D_PCT']].copy()
        view_df.columns = [L['col_rank'], L['col_name'], L['col_power'], L['col_kill'], L['col_kpi_kill'], L['col_dead'], L['col_kpi_dead']]

        def style_kpi(val):
            try:
                n = float(str(val).replace('%', ''))
                if n >= 100: return 'color: #00FF00;'
                if n < 50: return 'color: #FF4B4B;'
                return ''
            except: return ''

        st.dataframe(
            view_df.style.format({
                L['col_power']: '{:,.0f}', L['col_kill']: '{:,.0f}', 
                L['col_kpi_kill']: '{:.1f}%', L['col_dead']: '{:,.0f}', L['col_kpi_dead']: '{:.1f}%'
            }).map(style_kpi, subset=[L['col_kpi_kill'], L['col_kpi_dead']]),
            use_container_width=True, height=900
        )
        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.error("Error loading data. Please check connection.")
