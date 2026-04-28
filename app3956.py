import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide", initial_sidebar_state="collapsed")

# --- 2. GIAO DIỆN CSS TỔNG LỰC (BOX CHI TIẾT + BẢNG SIÊU CẤP) ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    [data-testid="stHeader"] {background: rgba(0,0,0,0);}
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    
    .main-header { 
        background: linear-gradient(90deg, #00FFFF, #58a6ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; font-size: 45px; font-weight: 900; padding: 10px;
    }

    /* 2.1. STYLE CHO CÁC Ô BOX TRONG PROFILE */
    .info-box { 
        background: #161b22; border: 1px solid #30363d; border-radius: 10px; 
        padding: 15px; text-align: center; margin-bottom: 10px; min-height: 100px;
    }
    .info-label { color: #8b949e; font-size: 13px; font-weight: bold; text-transform: uppercase; margin-bottom: 5px;}
    .info-value { color: #ffffff; font-size: 20px; font-weight: bold; }
    
    .gauge-footer { 
        color: #58a6ff; font-size: 20px; font-weight: 800; text-align: center; 
        margin-top: -30px; padding-bottom: 20px;
    }

    /* 2.2. STYLE RIÊNG CHO BẢNG TỔNG QUAN (SIÊU TO) */
    .big-table-container [data-testid="stDataFrame"] th {
        background-color: #1f2937 !important;
        color: #00FFFF !important;
        font-size: 24px !important;
        font-weight: 900 !important;
        height: 70px !important;
        text-align: center !important;
    }
    .big-table-container [data-testid="stDataFrame"] td {
        font-size: 22px !important;
        font-weight: 700 !important;
        height: 60px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC MỐC KPI ---
def get_targets(pow_val):
    p_mil = pow_val / 1_000_000
    if p_mil < 15: return 100_000_000, 200_000
    elif p_mil < 20: return 200_000_000, 250_000
    elif p_mil < 30: return 250_000_000, 300_000
    else: return 300_000_000, 400_000

# --- 4. DATA ENGINE ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=351056493'

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(URL)
        df.columns = [str(c).strip() for c in df.columns]
        c_name = next((c for c in df.columns if 'Tên' in c), None)
        c_pow = next((c for c in df.columns if 'Kỷ Lục' in c or 'Sức Mạnh' in c), None)
        c_kill = next((c for c in df.columns if 'Tổng Điểm Tiêu Diệt' in c), None)

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
        df.insert(0, 'HẠNG', range(1, len(df) + 1))
        return df, c_name, c_pow, c_kill
    except Exception as e:
        return None

res = load_data()
if res:
    df, c_name, c_pow, c_kill = res
    st.markdown('<div class="main-header">SHARED HOUSE 3956 KPI COMMANDER</div>', unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["👤 HỒ SƠ CHI TIẾT", "📊 TỔNG QUAN QUÂN ĐOÀN"])
    
    with t1:
        sel = st.selectbox("🔍 CHỌN CHIẾN BINH:", df[c_name].unique())
        d = df[df[c_name] == sel].iloc[0]
        
        # --- PHẦN 1: 4 CHỈ SỐ CHÍNH ---
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f'<div class="info-box"><div class="info-label">🏆 HẠNG (THEO KILL)</div><div class="info-value" style="color:#FFD700; font-size:30px;">#{int(d["HẠNG"])}</div></div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="info-box"><div class="info-label">🛡️ SỨC MẠNH HIỆN TẠI</div><div class="info-value">{int(d[c_pow]):,}</div></div>', unsafe_allow_html=True)
        col3.markdown(f'<div class="info-box"><div class="info-label">🔥 % HOÀN THÀNH KILL</div><div class="info-value" style="color:#00FFFF;">{d["K_PCT"]}%</div></div>', unsafe_allow_html=True)
        col4.markdown(f'<div class="info-box"><div class="info-label">💀 % HOÀN THÀNH DEAD</div><div class="info-value" style="color:#f29b05;">{d["D_PCT"]}%</div></div>', unsafe_allow_html=True)
        
        # --- PHẦN 2: PROFILE CHI TIẾT (DẠNG BOX) ---
        st.markdown("##### 📌 THÔNG SỐ CHI TIẾT TỪ SHEET")
        # Danh sách các cột muốn hiển thị dạng box
        detail_cols = ['ID nhân vật', 'Tên Người Dùng', 'Sức Mạnh', 'Kỷ Lục Sức Mạnh', 'T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong', 'Tổng Điểm Tiêu Diệt', 'Tổng Tiêu Diệt T5', 'Tổng Tiêu Diệt T4']
        
        # Chia làm 6 cột để hiển thị các box nhỏ
        rows = [detail_cols[i:i + 6] for i in range(0, len(detail_cols), 6)]
        for row in rows:
            cols = st.columns(6)
            for i, field in enumerate(row):
                if field in d:
                    val = d[field]
                    display_val = f"{int(val):,}" if isinstance(val, (int, float)) else val
                    cols[i].markdown(f'<div class="info-box"><div class="info-label">{field}</div><div class="info-value" style="font-size:15px;">{display_val}</div></div>', unsafe_allow_html=True)

        # --- PHẦN 3: 2 VÒNG TRÒN KPI ---
        g1, g2 = st.columns(2)
        with g1:
            fig_k = go.Figure(go.Indicator(mode="gauge+number", value=d['K_PCT'], number={'suffix': "%", 'font': {'size': 80}}, title={'text': "KPI KILL", 'font': {'size': 30}}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00FFFF"}}))
            fig_k.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_k, use_container_width=True)
            st.markdown(f'<div class="gauge-footer">ĐẠT: {d[c_kill]/1e6:.1f}M / {d["T_KILL"]/1e6:.1f}M KILL</div>', unsafe_allow_html=True)
        with g2:
            fig_d = go.Figure(go.Indicator(mode="gauge+number", value=d['D_PCT'], number={'suffix': "%", 'font': {'size': 80}}, title={'text': "KPI DEAD", 'font': {'size': 30}}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#f29b05"}}))
            fig_d.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_d, use_container_width=True)
            st.markdown(f'<div class="gauge-footer">ĐẠT: {int(d["SUM_DEAD"]):,} / {int(d["T_DEAD"]):,} DEAD</div>', unsafe_allow_html=True)

    with t2:
        st.markdown("<div class='big-table-container'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #58a6ff;'>🏆 BẢNG THỐNG KÊ CHI TIẾT TOÀN QUÂN</h2>", unsafe_allow_html=True)
        
        view_df = df[['HẠNG', c_name, c_pow, c_kill, 'K_PCT', 'SUM_DEAD', 'D_PCT']].copy()
        view_df.columns = ['HẠNG 🏆', 'CHIẾN BINH 🥷', 'SỨC MẠNH 🛡️', 'ĐIỂM KILL ⚔️', 'KPI KILL 🔥', 'LÍNH CHẾT 💀', 'KPI DEAD ⚰️']

        def style_kpi(val):
            try:
                n = float(str(val).replace('%', ''))
                if n >= 100: return 'color: #00FF00;'
                if n < 50: return 'color: #FF4B4B;'
                return ''
            except: return ''

        st.dataframe(
            view_df.style.format({
                'SỨC MẠNH 🛡️': '{:,.0f}', 'ĐIỂM KILL ⚔️': '{:,.0f}', 
                'KPI KILL 🔥': '{:.1f}%', 'LÍNH CHẾT 💀': '{:,.0f}', 'KPI DEAD ⚰️': '{:.1f}%'
            }).map(style_kpi, subset=['KPI KILL 🔥', 'KPI DEAD ⚰️']),
            use_container_width=True, height=900
        )
        st.markdown("</div>", unsafe_allow_html=True)
