import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_searchbox import st_searchbox

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide", initial_sidebar_state="collapsed")

# --- 2. KHỞI TẠO SESSION STATE ---
if 'lang' not in st.session_state:
    st.session_state.lang = "VN"

# --- 3. DỮ LIỆU PHIÊN DỊCH TOÀN DIỆN ---
TEXTS = {
    "VN": {
        "header": "HỆ THỐNG KPI - SHARED HOUSE 3956",
        "tab1": "👤 HỒ SƠ CHI TIẾT", "tab2": "📊 TỔNG QUAN QUÂN ĐOÀN",
        "placeholder": "🔍 Nhập tên hoặc ID để tìm kiếm...",
        "rank": "🏆 HẠNG", "power_now": "🛡️ SỨC MẠNH (GID 1)", "kpi_kill_pct": "🔥 % KILL", "kpi_dead_pct": "💀 % DEAD",
        "detail_title": "📌 XEM THÔNG SỐ CHI TIẾT", 
        "general_stats": "📊 THÔNG SỐ TỔNG QUÁT",
        "kill_stats": "⚔️ ĐIỂM TIÊU DIỆT ĐÃ KIẾM ĐƯỢC Ở MÙA GIẢI NÀY (T4 + T5)",
        "dead_stats": "💀 ĐIỂM TỬ VONG CHI TIẾT (GID 2)",
        "col_rank": "HẠNG 🏆", "col_name": "CHIẾN BINH 🥷", "col_alliance": "LIÊN MINH 🛡️", "col_power": "SỨC MẠNH 🛡️",
        "col_kill": "TOTAL KILL ⚔️", "col_kpi_kill": "KPI KILL 🔥", "col_dead": "TOTAL DEAD 💀", "col_kpi_dead": "KPI DEAD ⚰️",
        "id_label": "ID nhân vật", "name_label": "Tên Người Dùng",
        "pass_kpi": "✅ ĐẠT CHỈ TIÊU (>60%K HOẶC >100%D)", "fail_kpi": "⚠️ CHƯA ĐẠT CHỈ TIÊU"
    },
    "EN": {
        "header": "KPI SYSTEM - SHARED HOUSE 3956",
        "tab1": "👤 DETAILED PROFILE", "tab2": "📊 ALLIANCE OVERVIEW",
        "placeholder": "🔍 Type name or ID to search...",
        "rank": "🏆 RANK", "power_now": "🛡️ POWER (GID 1)", "kpi_kill_pct": "🔥 % KILL", "kpi_dead_pct": "💀 % DEAD",
        "detail_title": "📌 VIEW FULL STATISTICS", 
        "general_stats": "📊 GENERAL STATISTICS",
        "kill_stats": "⚔️ SEASON KILL POINTS (T4 + T5)",
        "dead_stats": "💀 DETAILED DEAD (GID 2)",
        "col_rank": "RANK 🏆", "col_name": "COMMANDER 🥷", "col_alliance": "ALLIANCE 🛡️", "col_power": "POWER 🛡️",
        "col_kill": "TOTAL KILL ⚔️", "col_kpi_kill": "KPI KILL 🔥", "col_dead": "TOTAL DEAD 💀", "col_kpi_dead": "KPI DEAD ⚰️",
        "id_label": "Character ID", "name_label": "Username",
        "pass_kpi": "✅ PASSED (>60%K OR >100%D)", "fail_kpi": "⚠️ INCOMPLETE"
    }
}

# --- 4. CALLBACKS ---
def change_lang_callback():
    st.session_state.lang = st.session_state.lang_radio_key

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
    .status-list {{ background: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; height: 350px; overflow-y: auto; }}
    div[data-testid="stSearchbox"] input {{ background-color: #161b22 !important; color: white !important; border: 1px solid #30363d !important; border-radius: 8px !important; }}
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
        
        # Nhận diện cột
        c_pow = next((c for c in df1.columns if "sức mạnh" in c.lower() or "power" in c.lower()), "Sức Mạnh")
        c_kill = next((c for c in df1.columns if "tiêu" in c.lower() or "kill" in c.lower()), "Tổng Tiêu Điệt")
        c_dead_pts = next((c for c in df1.columns if "điểm chết" in c.lower() or "dead" in c.lower()), "Điểm Chết")
        
        dead_cols = ['T1', 'T2', 'T3', 'T4', 'T5']
        
        df1[c_id] = df1[c_id].astype(str).str.strip()
        df2[c_id] = df2[c_id].astype(str).str.strip()
        
        merged = pd.merge(df2, df1, on=c_id, suffixes=('_2', '_1'))
        
        df = pd.DataFrame()
        df[c_id] = merged[c_id]
        df[c_name] = merged[c_name + '_2']
        df[c_alliance] = merged[c_alliance + '_2'] if c_alliance + '_2' in merged.columns else ""
        
        # 1. Sức mạnh lấy từ GID 1 để tính KPI Kill
        df[c_pow] = pd.to_numeric(merged[c_pow + '_1'], errors='coerce').fillna(0)
        
        # 2. Total Kill lấy từ GID 2
        df['TOTAL_KILL'] = pd.to_numeric(merged.get(c_kill + '_2', 0), errors='coerce').fillna(0)
        
        # 3. Total Dead lấy điểm chết từ GID 2[cite: 8]
        df['TOTAL_DEAD'] = pd.to_numeric(merged.get(c_dead_pts + '_2', 0), errors='coerce').fillna(0)
        
        # 4. Chi tiết tử vong hiển thị các cột T1..T5 ở GID 2
        for col in dead_cols:
            col_2 = col + '_2'
            df[col] = pd.to_numeric(merged.get(col_2, 0), errors='coerce').fillna(0)
            
        # 5. Điểm tiêu diệt mùa giải (T4 + T5 hoặc hiệu số GID2 - GID1 cho T4, T5 nếu có, hoặc hiệu số tổng kill)
        # Giả sử bạn có cột T4_kill, T5_kill hoặc tính hiệu số T4, T5 mùa giải. Ở đây nếu chỉ có tổng kill, ta lấy hiệu số tổng kill GID2 - GID1 nhân phần trăm hoặc nếu có cột T4, T5 riêng cho kill thì tính. 
        # Theo yêu cầu: "tính T4 và T5 cộng lại để ra kill đã đạt" từ GID 2 - GID 1:
        t4_diff = pd.to_numeric(merged.get('T4_2', 0), errors='coerce').fillna(0) - pd.to_numeric(merged.get('T4_1', 0), errors='coerce').fillna(0)
        t5_diff = pd.to_numeric(merged.get('T5_2', 0), errors='coerce').fillna(0) - pd.to_numeric(merged.get('T5_1', 0), errors='coerce').fillna(0)
        # Nếu bảng của bạn có cột riêng chứa điểm kill T4, T5 thì thay thế, tạm thời ta tính hiệu số T4 + T5 lính chết hoặc nếu ý bạn là điểm kill T4+T5, ta dùng hiệu số tổng kill nếu không tách cột. 
        # Để an toàn theo ý bạn "lấy điểm Tiêu diệt sau khi lấy GID 2 - GID 1 ở phần này chỉ tính T4 và T5 cộng lại":
        kill_t4_col = next((c for c in df1.columns if "t4" in c.lower() and ("kill" in c.lower() or "tiêu" in c.lower())), None)
        kill_t5_col = next((c for c in df1.columns if "t5" in c.lower() and ("kill" in c.lower() or "tiêu" in c.lower())), None)
        
        if kill_t4_col and kill_t5_col:
            df['SEASON_KILL'] = (pd.to_numeric(merged[kill_t4_col + '_2'], errors='coerce').fillna(0) - pd.to_numeric(merged[kill_t4_col + '_1'], errors='coerce').fillna(0)) + \
                                (pd.to_numeric(merged[kill_t5_col + '_2'], errors='coerce').fillna(0) - pd.to_numeric(merged[kill_t5_col + '_1'], errors='coerce').fillna(0))
        else:
            # Fallback nếu không có cột T4/T5 kill riêng thì lấy hiệu số tổng kill GID2 - GID1
            df['SEASON_KILL'] = pd.to_numeric(merged.get(c_kill + '_2', 0), errors='coerce').fillna(0) - pd.to_numeric(merged.get(c_kill + '_1', 0), errors='coerce').fillna(0)

        # --- TÍNH TOÁN KPI ---
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
        st.error(f"Lỗi tải dữ liệu: {e}")
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
            m1.markdown(f'<div class="info-box"><div class="info-label">{L["rank"]}</div><div class="info-value" style="color:#FFD700;">#{int(d["H_RAW"])}</div></div>', unsafe_allow_html=True)
            m2.markdown(f'<div class="info-box"><div class="info-label">{L["power_now"]}</div><div class="info-value">{int(d[c_pow]):,}</div></div>'.replace(",", "."), unsafe_allow_html=True)
            m3.markdown(f'<div class="info-box"><div class="info-label">{L["kpi_kill_pct"]}</div><div class="info-value" style="color:#00FFFF;">{d["K_PCT"]}%</div></div>', unsafe_allow_html=True)
            m4.markdown(f'<div class="info-box"><div class="info-label">{L["kpi_dead_pct"]}</div><div class="info-value" style="color:#f29b05;">{d["D_PCT"]}%</div></div>', unsafe_allow_html=True)
            
            with st.expander(L["detail_title"], expanded=False):
                st.markdown(f"**{L['general_stats']}**")
                c_cols = st.columns(5)
                c_cols[0].markdown(f'<div class="info-box"><div class="info-label">ID</div><div class="info-value">{d[c_id]}</div></div>', unsafe_allow_html=True)
                c_cols[1].markdown(f'<div class="info-box"><div class="info-label">{L["name_label"]}</div><div class="info-value">{d[c_name]}</div></div>', unsafe_allow_html=True)
                c_cols[2].markdown(f'<div class="info-box"><div class="info-label">Sức Mạnh</div><div class="info-value">{int(d[c_pow]):,}</div></div>'.replace(",", "."), unsafe_allow_html=True)
                c_cols[3].markdown(f'<div class="info-box"><div class="info-label">Total Kill</div><div class="info-value">{int(d["TOTAL_KILL"]):,}</div></div>'.replace(",", "."), unsafe_allow_html=True)
                c_cols[4].markdown(f'<div class="info-box"><div class="info-label">Total Dead</div><div class="info-value">{int(d["TOTAL_DEAD"]):,}</div></div>'.replace(",", "."), unsafe_allow_html=True)
                
                st.write("---")
                st.markdown(f"**{L['kill_stats']}**")
                st.markdown(f'<div class="info-box"><div class="info-label">Điểm Tiêu Diệt Mùa Giải (T4+T5)</div><div class="info-value">{int(d["SEASON_KILL"]):,}</div></div>'.replace(",", "."), unsafe_allow_html=True)
                
                st.markdown(f"**{L['dead_stats']}**")
                d_cols_ui = st.columns(len(dead_cols))
                for i, col in enumerate(dead_cols):
                    d_cols_ui[i].markdown(f'<div class="info-box"><div class="info-label">{col} (GID 2)</div><div class="info-value">{int(d[col]):,}</div></div>'.replace(",", "."), unsafe_allow_html=True)

            g1, g2 = st.columns(2)
            with g1:
                fig_k = go.Figure(go.Indicator(
                    mode="gauge+number", 
                    value=d['K_PCT'], 
                    number={'suffix': "%", 'font':{'size':24}}, 
                    gauge={'bar': {'color': "#00FFFF"}, 'axis': {'range': [0, max(100, d['K_PCT'])]}}
                ))
                fig_k.update_layout(height=200, margin=dict(l=15,r=15,t=40,b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_k, use_container_width=True, config={'displayModeBar': False})
                
                actual_k = f"{d['SEASON_KILL']:,.0f}".replace(",", ".")
                target_k = f"{d['TARGET_KILL']:,.0f}".replace(",", ".")
                st.markdown(f'<div class="gauge-footer">KILL ĐẠT: {actual_k} / Cần đạt: {target_k}</div>', unsafe_allow_html=True)

            with g2:
                fig_d = go.Figure(go.Indicator(
                    mode="gauge+number", 
                    value=d['D_PCT'], 
                    number={'suffix': "%", 'font':{'size':24}}, 
                    gauge={'bar': {'color': "#f29b05"}, 'axis': {'range': [0, max(100, d['D_PCT'])]}}
                ))
                fig_d.update_layout(height=200, margin=dict(l=15,r=15,t=40,b=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_d, use_container_width=True, config={'displayModeBar': False})
                
                actual_d = f"{d['TOTAL_DEAD']:,.0f}".replace(",", ".")
                target_d = f"{d['TARGET_DEAD']:,.0f}".replace(",", ".")
                st.markdown(f'<div class="gauge-footer">DEAD: {actual_d} / Cần đạt: {target_d}</div>', unsafe_allow_html=True)
        else:
            st.info("💡 Vui lòng tìm kiếm tên hoặc ID chiến binh ở khung phía trên.")

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

        st.dataframe(v_df.style.format(format_dict), use_container_width=True, height=400)

        st.write("---")
        
        passed_mask = (df['K_PCT'] > 60) | (df['D_PCT'] >= 100)
        passed_list = df[passed_mask][c_name].tolist()
        failed_list = df[~passed_mask][c_name].tolist()
        
        list_col1, list_col2 = st.columns(2)
        
        with list_col1:
            st.markdown(f"<h4 style='color:#00FFFF; text-align:center;'>{L['pass_kpi']} ({len(passed_list)})</h4>", unsafe_allow_html=True)
            passed_html = "".join([f"<div style='padding:5px; border-bottom:1px solid #30363d;'>🟢 {name}</div>" for name in passed_list])
            st.markdown(f'<div class="status-list">{passed_html}</div>', unsafe_allow_html=True)
            
        with list_col2:
            st.markdown(f"<h4 style='color:#f29b05; text-align:center;'>{L['fail_kpi']} ({len(failed_list)})</h4>", unsafe_allow_html=True)
            failed_html = "".join([f"<div style='padding:5px; border-bottom:1px solid #30363d;'>🔴 {name}</div>" for name in failed_list])
            st.markdown(f'<div class="status-list">{failed_html}</div>', unsafe_allow_html=True)
