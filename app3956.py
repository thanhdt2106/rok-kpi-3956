import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_searchbox import st_searchbox

# --- 1. CẤU HÌNH TRANG & CẤU HÌNH BANNER ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide", initial_sidebar_state="collapsed")

# Đường dẫn ảnh trang chủ từ GitHub của bạn:
BANNER_URL = "https://raw.githubusercontent.com/thanhdt2106/rok-kpi-3956/2808e8f9ed167971c44b842ef91dde0c15ce86d8/meme2.png"

# --- 2. KHỞI TẠO SESSION STATE ---
if 'lang' not in st.session_state:
    st.session_state.lang = "VN"

# --- 3. DỮ LIỆU PHIÊN DỊCH TOÀN DIỆN (ĐÃ DỊCH HẾT SANG ANH) ---
TEXTS = {
    "VN": {
        "header": "HỆ THỐNG KPI - SHARED HOUSE 3956",
        "tab1": "👤 HỒ SƠ CHI TIẾT", 
        "tab2": "📊 TỔNG QUAN QUÂN ĐOÀN",
        "placeholder": "🔍 Nhập tên hoặc ID để tìm kiếm chiến binh...",
        "rank": "🏆 HẠNG", 
        "power_now": "🛡️ SỨC MẠNH (GID 1)", 
        "kpi_kill_pct": "🔥 % KILL", 
        "kpi_dead_pct": "💀 % DEAD",
        "detail_title": "📌 XEM THÔNG SỐ CHI TIẾT", 
        "general_stats": "📊 THÔNG SỐ TỔNG QUÁT",
        "kill_stats": "⚔️ ĐIỂM TIÊU DIỆT MÙA GIẢI (T4 + T5)",
        "dead_stats": "💀 ĐIỂM TỬ VONG CHI TIẾT TRONG MÙA GIẢI (GID 2 - GID 1)",
        "col_rank": "HẠNG 🏆", 
        "col_name": "CHIẾN BINH 🥷", 
        "col_alliance": "LIÊN MINH 🛡️", 
        "col_power": "SỨC MẠNH 🛡️",
        "col_kill": "TOTAL KILL ⚔️", 
        "col_kpi_kill": "KPI KILL 🔥", 
        "col_dead": "SEASON DEAD 💀", 
        "col_kpi_dead": "KPI DEAD ⚰️",
        "id_label": "ID nhân vật", 
        "name_label": "Tên Người Dùng",
        "power_label": "Sức Mạnh",
        "season_dead_label": "Season Dead",
        "season_kill_label": "Điểm Tiêu Diệt Mùa Giải (T4+T5)",
        "dead_season_suffix": "(Mùa giải)",
        "kill_achieved_label": "KILL ĐẠT",
        "required_label": "Cần đạt",
        "dead_achieved_label": "DEAD",
        "pass_kpi": "✅ ĐẠT CHỈ TIÊU (>60%K HOẶC >100%D)", 
        "fail_kpi": "⚠️ CHƯA ĐẠT CHỈ TIÊU",
        "search_hint": "💡 Vui lòng tìm kiếm tên hoặc ID chiến binh ở khung phía trên.",
        "load_error": "Lỗi tải dữ liệu: "
    },
    "EN": {
        "header": "KPI SYSTEM - SHARED HOUSE 3956",
        "tab1": "👤 DETAILED PROFILE", 
        "tab2": "📊 ALLIANCE OVERVIEW",
        "placeholder": "🔍 Type name or ID to search warrior...",
        "rank": "🏆 RANK", 
        "power_now": "🛡️ POWER (GID 1)", 
        "kpi_kill_pct": "🔥 % KILL", 
        "kpi_dead_pct": "💀 % DEAD",
        "detail_title": "📌 VIEW FULL STATISTICS", 
        "general_stats": "📊 GENERAL STATISTICS",
        "kill_stats": "⚔️ SEASON KILL POINTS (T4 + T5)",
        "dead_stats": "💀 SEASON DETAILED DEAD (GID 2 - GID 1)",
        "col_rank": "RANK 🏆", 
        "col_name": "COMMANDER 🥷", 
        "col_alliance": "ALLIANCE 🛡️", 
        "col_power": "POWER 🛡️",
        "col_kill": "TOTAL KILL ⚔️", 
        "col_kpi_kill": "KPI KILL 🔥", 
        "col_dead": "SEASON DEAD 💀", 
        "col_kpi_dead": "KPI DEAD ⚰️",
        "id_label": "Character ID", 
        "name_label": "Username",
        "power_label": "Power",
        "season_dead_label": "Season Dead",
        "season_kill_label": "Season Kill Points (T4+T5)",
        "dead_season_suffix": "(Season)",
        "kill_achieved_label": "KILL ACHIEVED",
        "required_label": "Required",
        "dead_achieved_label": "DEAD",
        "pass_kpi": "✅ PASSED (>60%K OR >100%D)", 
        "fail_kpi": "⚠️ INCOMPLETE",
        "search_hint": "💡 Please search for a warrior's name or ID in the box above.",
        "load_error": "Data loading error: "
    }
}

# --- 4. CALLBACKS ---
def change_lang_callback():
    st.session_state.lang = st.session_state.lang_radio_key

L = TEXTS[st.session_state.lang]

# --- 5. CSS CUSTOM NÂNG CAO & RESPONSIVE ---
st.markdown("""
    <style>
    header[data-testid="stHeader"] {display: none !important;}
    .stApp { background-color: #0b0f19; color: #e6edfd; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
    
    .banner-container {
        width: 100%;
        max-height: 500px;
        overflow: hidden;
        border-radius: 14px;
        margin-top: 20px;
        margin-bottom: 15px;
        border: 1px solid rgba(59, 130, 246, 0.3);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .banner-container img {
        width: 100%;
        height: 500px;
        object-fit: cover;
    }

    .main-header { 
        background: linear-gradient(135deg, #00ffff 0%, #3b82f6 50%, #8b5cf6 100%); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        text-align: center; 
        font-size: clamp(20px, 4vw, 36px); 
        font-weight: 800; 
        padding: 5px 0 15px 0;
        letter-spacing: 0.5px;
    }

    .info-box { 
        background: linear-gradient(145deg, #131b2e, #0f172a); 
        border: 1px solid rgba(59, 130, 246, 0.2); 
        border-radius: 12px; 
        padding: 12px 8px; 
        text-align: center; 
        margin-bottom: 10px; 
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .info-box:hover {
        border-color: rgba(0, 255, 255, 0.4);
        transform: translateY(-2px);
    }
    .info-label { 
        color: #94a3b8; 
        font-size: 11px; 
        font-weight: 700; 
        text-transform: uppercase; 
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .info-value { 
        color: #f8fafc; 
        font-size: clamp(14px, 2vw, 18px); 
        font-weight: 800; 
    }

    .gauge-footer { 
        color: #38bdf8; 
        font-size: 12px; 
        font-weight: 700; 
        text-align: center; 
        margin-top: -25px;
        background: rgba(15, 23, 42, 0.6);
        padding: 4px;
        border-radius: 6px;
    }

    .status-list { 
        background: #111827; 
        border-radius: 12px; 
        padding: 15px; 
        border: 1px solid rgba(255, 255, 255, 0.08); 
        height: 380px; 
        overflow-y: auto; 
        box-shadow: inset 0 2px 6px rgba(0,0,0,0.4);
    }
    .status-item {
        padding: 8px 10px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        font-size: 13px;
        display: flex;
        align-items: center;
    }

    div[data-testid="stSearchbox"] input { 
        background-color: #111827 !important; 
        color: #ffffff !important; 
        border: 1px solid rgba(59, 130, 246, 0.4) !important; 
        border-radius: 10px !important; 
        padding: 8px 12px !important;
    }
    
    .stTabs [data-baseweb="tab-list"] { gap: 8px; justify-content: center; }
    .stTabs [data-baseweb="tab"] {
        background-color: #131b2e;
        border-radius: 8px 8px 0 0;
        color: #94a3b8;
        font-weight: 700;
        padding: 10px 20px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1e3a8a, #1e293b);
        color: #38bdf8 !important;
        border-color: rgba(56, 189, 248, 0.4) !important;
    }

    @media (max-width: 768px) {
        .banner-container { max-height: 140px; }
        .banner-container img { height: 140px; }
        .info-box { padding: 8px 4px; min-height: 60px; }
        .info-value { font-size: 13px; }
        .main-header { font-size: 18px; }
    }
    </style>
""", unsafe_allow_html=True)

# --- 6. DATA ENGINE ---
@st.cache_data(ttl=5)
def load_data():
    try:
        sheet_id = "1ylmO5olorIhdgKgejmTRftSLSe6zXXkYn4tYXTCtTSg"
        gid1 = "568389539"
        gid2 = "1577480214"
        
        url1 = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid1}'
        url2 = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid2}'
        
        df1 = pd.read_csv(url1)
        df2 = pd.read_csv(url2)
        
        df1.columns = [str(c).strip() for c in df1.columns]
        df2.columns = [str(c).strip() for c in df2.columns]
        
        c_id = "ID"
        c_name = "Tên"
        c_alliance = "Liên Minh"
        
        c_pow = next((c for c in df1.columns if "sức mạnh" in c.lower() or "power" in c.lower()), "Sức Mạnh")
        c_kill = next((c for c in df1.columns if "tiêu" in c.lower() or "kill" in c.lower()), "Tổng Tiêu Điệt")
        
        dead_cols = ['T1', 'T2', 'T3', 'T4', 'T5']
        
        df1[c_id] = df1[c_id].astype(str).str.strip()
        df2[c_id] = df2[c_id].astype(str).str.strip()
        
        merged = pd.merge(df2, df1, on=c_id, suffixes=('_2', '_1'))
        
        df = pd.DataFrame()
        df[c_id] = merged[c_id]
        df[c_name] = merged[c_name + '_2']
        df[c_alliance] = merged[c_alliance + '_2'] if c_alliance + '_2' in merged.columns else ""
        
        df[c_pow] = pd.to_numeric(merged[c_pow + '_1'], errors='coerce').fillna(0)
        df['TOTAL_KILL'] = pd.to_numeric(merged.get(c_kill + '_2', 0), errors='coerce').fillna(0)
        
        for col in dead_cols:
            val_2 = pd.to_numeric(merged.get(col + '_2', 0), errors='coerce').fillna(0)
            val_1 = pd.to_numeric(merged.get(col + '_1', 0), errors='coerce').fillna(0)
            df[col] = val_2 - val_1
            
        df['TOTAL_DEAD'] = df[dead_cols].sum(axis=1)
        
        kill_t4_col = next((c for c in df1.columns if "t4" in c.lower() and ("kill" in c.lower() or "tiêu" in c.lower())), None)
        kill_t5_col = next((c for c in df1.columns if "t5" in c.lower() and ("kill" in c.lower() or "tiêu" in c.lower())), None)
        
        if kill_t4_col and kill_t5_col:
            df['SEASON_KILL'] = (pd.to_numeric(merged[kill_t4_col + '_2'], errors='coerce').fillna(0) - pd.to_numeric(merged[kill_t4_col + '_1'], errors='coerce').fillna(0)) + \
                                (pd.to_numeric(merged[kill_t5_col + '_2'], errors='coerce').fillna(0) - pd.to_numeric(merged[kill_t5_col + '_1'], errors='coerce').fillna(0))
        else:
            df['SEASON_KILL'] = pd.to_numeric(merged.get(c_kill + '_2', 0), errors='coerce').fillna(0) - pd.to_numeric(merged.get(c_kill + '_1', 0), errors='coerce').fillna(0)

        df['TARGET_KILL'] = df[c_pow] * 3
        df['K_PCT'] = ((df['SEASON_KILL'] / df['TARGET_KILL']) * 100).fillna(0).round(1)
        
        def get_dead_target(pow_val):
            if pow_val >= 50_000_000:
                return 600_000
            elif pow_val >= 40_000_000:
                return 500_000
            elif pow_val >= 30_000_000:
                return 400_000
            else:
                return 250_000

        df['TARGET_DEAD'] = df[c_pow].apply(get_dead_target)
        df['D_PCT'] = ((df['TOTAL_DEAD'] / df['TARGET_DEAD']) * 100).fillna(0).round(1)
        
        df = df.sort_values(by='K_PCT', ascending=False).reset_index(drop=True)
        df.insert(0, 'H_RAW', range(1, len(df) + 1))
        df['Full_Search'] = df[c_name].astype(str) + " (ID: " + df[c_id].astype(str) + ")"
        
        return df, c_id, c_name, c_alliance, c_pow, dead_cols
    except Exception as e:
        st.error(f"{TEXTS[st.session_state.lang]['load_error']}{e}")
        return None

res = load_data()

if res:
    df, c_id, c_name, c_alliance, c_pow, dead_cols = res
    options_list = df['Full_Search'].tolist()

    def search_warriors(search_term: str):
        if search_term is None: 
            return []
        term = str(search_term).lower()
        return [opt for opt in options_list if term in str(opt).lower()][:10]

    # --- HIỂN THỊ TIÊU ĐỀ Ở PHẦN TRÊN ---
    st.markdown(f'<div class="main-header">{L["header"]}</div>', unsafe_allow_html=True)
    
    col_lang, col_search = st.columns([1, 4])
    with col_lang:
        st.radio("L", ["VN", "EN"], index=0 if st.session_state.lang == "VN" else 1, 
                 key="lang_radio_key", on_change=change_lang_callback, horizontal=True, label_visibility="collapsed")
    
    with col_search:
        choice = st_searchbox(search_warriors, placeholder=L["placeholder"], key="warrior_search_box", label=None)

    tab1, tab2 = st.tabs([L["tab1"], L["tab2"]])
    
    with tab1:
        if choice:
            d = df[df['Full_Search'] == choice].iloc[0]
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f'<div class="info-box"><div class="info-label">{L["rank"]}</div><div class="info-value" style="color:#fbbf24;">#{int(d["H_RAW"])}</div></div>', unsafe_allow_html=True)
            m2.markdown(f'<div class="info-box"><div class="info-label">{L["power_now"]}</div><div class="info-value">{int(d[c_pow]):,}</div></div>'.replace(",", "."), unsafe_allow_html=True)
            m3.markdown(f'<div class="info-box"><div class="info-label">{L["kpi_kill_pct"]}</div><div class="info-value" style="color:#22d3ee;">{d["K_PCT"]}%</div></div>', unsafe_allow_html=True)
            m4.markdown(f'<div class="info-box"><div class="info-label">{L["kpi_dead_pct"]}</div><div class="info-value" style="color:#fb923c;">{d["D_PCT"]}%</div></div>', unsafe_allow_html=True)
            
            with st.expander(L["detail_title"], expanded=False):
                st.markdown(f"**{L['general_stats']}**")
                c_cols = st.columns(5)
                c_cols[0].markdown(f'<div class="info-box"><div class="info-label">ID</div><div class="info-value">{d[c_id]}</div></div>', unsafe_allow_html=True)
                c_cols[1].markdown(f'<div class="info-box"><div class="info-label">{L["name_label"]}</div><div class="info-value">{d[c_name]}</div></div>', unsafe_allow_html=True)
                c_cols[2].markdown(f'<div class="info-box"><div class="info-label">{L["power_label"]}</div><div class="info-value">{int(d[c_pow]):,}</div></div>'.replace(",", "."), unsafe_allow_html=True)
                c_cols[3].markdown(f'<div class="info-box"><div class="info-label">Total Kill</div><div class="info-value">{int(d["TOTAL_KILL"]):,}</div></div>'.replace(",", "."), unsafe_allow_html=True)
                c_cols[4].markdown(f'<div class="info-box"><div class="info-label">{L["season_dead_label"]}</div><div class="info-value">{int(d["TOTAL_DEAD"]):,}</div></div>'.replace(",", "."), unsafe_allow_html=True)
                
                st.write("---")
                st.markdown(f"**{L['kill_stats']}**")
                st.markdown(f'<div class="info-box"><div class="info-label">{L["season_kill_label"]}</div><div class="info-value">{int(d["SEASON_KILL"]):,}</div></div>'.replace(",", "."), unsafe_allow_html=True)
                
                st.markdown(f"**{L['dead_stats']}**")
                d_cols_ui = st.columns(len(dead_cols))
                for i, col in enumerate(dead_cols):
                    d_cols_ui[i].markdown(f'<div class="info-box"><div class="info-label">{col} {L["dead_season_suffix"]}</div><div class="info-value">{int(d[col]):,}</div></div>'.replace(",", "."), unsafe_allow_html=True)

            g1, g2 = st.columns(2)
            with g1:
                fig_k = go.Figure(go.Indicator(
                    mode="gauge+number", 
                    value=d['K_PCT'], 
                    number={'suffix': "%", 'font':{'size':22, 'color': '#ffffff'}}, 
                    gauge={
                        'bar': {'color': "#22d3ee"}, 
                        'axis': {'range': [0, max(100, d['K_PCT'])], 'tickcolor': "#94a3b8"},
                        'bgcolor': "#1e293b",
                        'borderwidth': 0
                    }
                ))
                fig_k.update_layout(height=190, margin=dict(l=10,r=10,t=35,b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_k, use_container_width=True, config={'displayModeBar': False})
                
                actual_k = f"{d['SEASON_KILL']:,.0f}".replace(",", ".")
                target_k = f"{d['TARGET_KILL']:,.0f}".replace(",", ".")
                st.markdown(f'<div class="gauge-footer">{L["kill_achieved_label"]}: {actual_k} / {L["required_label"]}: {target_k}</div>', unsafe_allow_html=True)

            with g2:
                fig_d = go.Figure(go.Indicator(
                    mode="gauge+number", 
                    value=d['D_PCT'], 
                    number={'suffix': "%", 'font':{'size':22, 'color': '#ffffff'}}, 
                    gauge={
                        'bar': {'color': "#fb923c"}, 
                        'axis': {'range': [0, max(100, d['D_PCT'])], 'tickcolor': "#94a3b8"},
                        'bgcolor': "#1e293b",
                        'borderwidth': 0
                    }
                ))
                fig_d.update_layout(height=190, margin=dict(l=10,r=10,t=35,b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_d, use_container_width=True, config={'displayModeBar': False})
                
                actual_d = f"{d['TOTAL_DEAD']:,.0f}".replace(",", ".")
                target_d = f"{d['TARGET_DEAD']:,.0f}".replace(",", ".")
                st.markdown(f'<div class="gauge-footer">{L["dead_achieved_label"]}: {actual_d} / {L["required_label"]}: {target_d}</div>', unsafe_allow_html=True)
        else:
            st.info(L["search_hint"])

    with tab2:
        v_df = df[['H_RAW', c_name, c_alliance, c_pow, 'TOTAL_KILL'] + dead_cols + ['K_PCT', 'TOTAL_DEAD', 'D_PCT']].copy()
        v_df.columns = [L['col_rank'], L['col_name'], L['col_alliance'], L['col_power'], L['col_kill']] + dead_cols + [L['col_kpi_kill'], L['col_dead'], L['col_kpi_dead']]
        
        format_dict = {
            L['col_power']: lambda x: f"{int(x):,}".replace(",", "."),
            L['col_kill']: lambda x: f"{int(x):,}".replace(",", "."),
            L['col_dead']: lambda x: f"{int(x):,}".replace(",", "."),
            L['col_kpi_kill']: '{:.1f}%', 
            L['col_kpi_dead']: '{:.1f}%'
        }
        for col in dead_cols:
            format_dict[col] = lambda x: f"{int(x):,}".replace(",", ".")

        st.dataframe(v_df.style.format(format_dict), use_container_width=True, height=420)

        st.write("---")
        
        passed_mask = (df['K_PCT'] > 60) | (df['D_PCT'] >= 100)
        passed_list = df[passed_mask][c_name].tolist()
        failed_list = df[~passed_mask][c_name].tolist()
        
        list_col1, list_col2 = st.columns(2)
        
        with list_col1:
            st.markdown(f"<h4 style='color:#22d3ee; text-align:center; font-size:16px;'>{L['pass_kpi']} ({len(passed_list)})</h4>", unsafe_allow_html=True)
            passed_html = "".join([f"<div class='status-item'>🟢 &nbsp; {name}</div>" for name in passed_list])
            st.markdown(f'<div class="status-list">{passed_html}</div>', unsafe_allow_html=True)
            
        with list_col2:
            st.markdown(f"<h4 style='color:#fb923c; text-align:center; font-size:16px;'>{L['fail_kpi']} ({len(failed_list)})</h4>", unsafe_allow_html=True)
            failed_html = "".join([f"<div class='status-item'>🔴 &nbsp; {name}</div>" for name in failed_list])
            st.markdown(f'<div class="status-list">{failed_html}</div>', unsafe_allow_html=True)

    # --- 7. HIỂN THỊ BANNER Ở PHẦN DƯỚI CÙNG ---
    if BANNER_URL:
        st.markdown(f'<div class="banner-container"><img src="{BANNER_URL}" alt="Footer Banner"></div>', unsafe_allow_html=True)
