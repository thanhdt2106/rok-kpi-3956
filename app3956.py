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
        "placeholder": "Nhập ID hoặc tên của bạn vào đây...",
        "rank": "🏆 HẠNG", "power_now": "🛡️ SỨC MẠNH", "kpi_kill_pct": "🔥 % KILL", "kpi_dead_pct": "💀 % DEAD",
        "detail_title": "📌 THÔNG SỐ CHI TIẾT", "target_kill": "ĐẠT: ", "target_dead": "ĐẠT: ",
        "col_rank": "HẠNG 🏆", "col_name": "CHIẾN BINH 🥷", "col_power": "SỨC MẠNH 🛡️",
        "col_kill": "ĐIỂM KILL ⚔️", "col_kpi_kill": "KPI KILL 🔥", "col_dead": "LÍNH CHẾT 💀", "col_kpi_dead": "KPI DEAD ⚰️"
    },
    "EN": {
        "header": "KPI SYSTEM - SHARED HOUSE 3956",
        "tab1": "👤 DETAILED PROFILE", "tab2": "📊 ALLIANCE OVERVIEW",
        "placeholder": "Enter ID or Name here...",
        "rank": "🏆 RANK", "power_now": "🛡️ POWER", "kpi_kill_pct": "🔥 % KILL", "kpi_dead_pct": "💀 % DEAD",
        "detail_title": "📌 DETAILED STATISTICS", "target_kill": "REACHED: ", "target_dead": "REACHED: ",
        "col_rank": "RANK 🏆", "col_name": "COMMANDER 🥷", "col_power": "POWER 🛡️",
        "col_kill": "KILL POINTS ⚔️", "col_kpi_kill": "KPI KILL 🔥", "col_dead": "DEAD UNITS 💀", "col_kpi_dead": "KPI DEAD ⚰️"
    }
}

# --- 3. CSS TỔNG LỰC (DỌN DẸP + FIX MOBILE) ---
st.markdown("""
    <style>
    header[data-testid="stHeader"] {display: none !important;}
    [data-testid="stSidebarNav"], [data-testid="collapsedControl"] {display: none;}
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .block-container { padding-top: 1rem !important; }
    .main-header { 
        background: linear-gradient(90deg, #00FFFF, #58a6ff); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        text-align: center; font-size: clamp(22px, 5vw, 32px); font-weight: 900; padding-bottom: 15px;
    }
    .info-box { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 10px; text-align: center; margin-bottom: 5px; }
    .info-label { color: #8b949e; font-size: 11px; font-weight: bold; text-transform: uppercase; }
    .info-value { color: #ffffff; font-size: 18px; font-weight: 800; }
    .gauge-footer { color: #58a6ff; font-size: 13px; font-weight: 800; text-align: center; margin-top: -35px; }
    
    /* Ép 2 cột nằm ngang cho Mobile */
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
        c_id, c_name, c_pow, c_kill = "ID nhân vật", "Tên Người Dùng", "Sức Mạnh", "Tổng Điểm Tiêu Diệt"
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
    
    # --- DÒNG CHUNG: NGÔN NGỮ & TÌM KIẾM ---
    col_lang, col_search = st.columns([1, 3])
    with col_lang:
        lang = st.radio("L", ["VN", "EN"], horizontal=True, label_visibility="collapsed")
        L = TEXTS[lang]
    with col_search:
        search_query = st.text_input("S", placeholder=L["placeholder"], label_visibility="collapsed")

    tab1, tab2 = st.tabs([L["tab1"], L["tab2"]])
    
    with tab1:
        target_commander = None
        
        # LOGIC TÌM KIẾM
        if search_query:
            if search_query.isdigit():
                # ID: Phải nhập đúng mới hiện
                match = df[df[c_id].astype(str) == search_query]
                if not match.empty: target_commander = match.iloc[0]
            else:
                # Tên: Gõ ký tự hiện list gợi ý
                matches = df[df[c_name].str.contains(search_query, case=False, na=False)]
                if not matches.empty:
                    choice = st.selectbox("👇 Chọn chiến binh từ danh sách:", [""] + matches[c_name].tolist())
                    if choice != "":
                        target_commander = matches[matches[c_name] == choice].iloc[0]

        # HIỂN THỊ KẾT QUẢ 100%
        if target_commander is not None:
            d = target_commander
            
            # 4 ô chỉ số chính
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f'<div class="info-box"><div class="info-label">{L["rank"]}</div><div class="info-value" style="color:#FFD700;">#{int(d["H_RAW"])}</div></div>', unsafe_allow_html=True)
            m2.markdown(f'<div class="info-box"><div class="info-label">{L["power_now"]}</div><div class="info-value">{int(d[c_pow]):,}</div></div>', unsafe_allow_html=True)
            m3.markdown(f'<div class="info-box"><div class="info-label">{L["kpi_kill_pct"]}</div><div class="info-value" style="color:#00FFFF;">{d["K_PCT"]}%</div></div>', unsafe_allow_html=True)
            m4.markdown(f'<div class="info-box"><div class="info-label">{L["kpi_dead_pct"]}</div><div class="info-value" style="color:#f29b05;">{d["D_PCT"]}%</div></div>', unsafe_allow_html=True)
            
            # Bảng thông số chi tiết
            with st.expander(L["detail_title"], expanded=True):
                det_cols = st.columns(5)
                details = [
                    ("ID", d[c_id]), ("Tên", d[c_name]), ("Sức mạnh", f"{int(d[c_pow]):,}"),
                    ("T5 Kill", f"{int(d['Tổng Tiêu Diệt T5']):,}"), ("T4 Kill", f"{int(d['Tổng Tiêu Diệt T4']):,}")
                ]
                for i, (lab, val) in enumerate(details):
                    det_cols[i].markdown(f'<div class="info-box"><div class="info-label">{lab}</div><div class="info-value" style="font-size:14px;">{val}</div></div>', unsafe_allow_html=True)

            # 2 VÒNG TRÒN KPI & TIẾN ĐỘ
            g1, g2 = st.columns(2)
            with g1:
                fig_k = go.Figure(go.Indicator(mode="gauge+number", value=d['K_PCT'], number={'suffix': "%", 'font':{'size':24}}, 
                                              gauge={'bar': {'color': "#00FFFF"}, 'axis': {'range': [0, 100]}}))
                fig_k.update_layout(height=200, margin=dict(l=15,r=15,t=40,b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_k, use_container_width=True, config={'displayModeBar': False})
                st.markdown(f'<div class="gauge-footer">{L["target_kill"]}{d[c_kill]/1e6:.1f}M / 300M</div>', unsafe_allow_html=True)
            with g2:
                fig_d = go.Figure(go.Indicator(mode="gauge+number", value=d['D_PCT'], number={'suffix': "%", 'font':{'size':24}}, 
                                              gauge={'bar': {'color': "#f29b05"}, 'axis': {'range': [0, 100]}}))
                fig_d.update_layout(height=200, margin=dict(l=15,r=15,t=40,b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_d, use_container_width=True, config={'displayModeBar': False})
                st.markdown(f'<div class="gauge-footer">{L["target_dead"]}{int(d["SUM_DEAD"]/1000)}K / 400K</div>', unsafe_allow_html=True)
        else:
            # Banner ảnh RoK (Hiện khi chưa tìm kiếm)
            st.image("https://raw.githubusercontent.com/tên-user/tên-repo/main/image_5ca61f.jpg", use_column_width=True)

    with tab2:
        # Bảng Table tổng quan luôn tồn tại
        v_df = df[['H_RAW', c_name, c_pow, c_kill, 'K_PCT', 'SUM_DEAD', 'D_PCT']].copy()
        v_df.columns = [L['col_rank'], L['col_name'], L['col_power'], L['col_kill'], L['col_kpi_kill'], L['col_dead'], L['col_kpi_dead']]
        st.dataframe(v_df.style.format({L['col_power']: '{:,.0f}', L['col_kill']: '{:,.0f}', L['col_dead']: '{:,.0f}', L['col_kpi_kill']: '{:.1f}%', L['col_kpi_dead']: '{:.1f}%'}), use_container_width=True, height=600)
