import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide", initial_sidebar_state="collapsed")

# --- 2. GIAO DIỆN CSS (DARK MODE & CUSTOM BOX) ---
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

    /* Các ô Box thông số */
    .info-box { 
        background: #161b22; border: 1px solid #30363d; border-radius: 10px; 
        padding: 15px; text-align: center; margin-bottom: 10px;
    }
    .info-label { color: #8b949e; font-size: 14px; font-weight: bold; text-transform: uppercase; margin-bottom: 5px;}
    .info-value { color: #ffffff; font-size: 22px; font-weight: bold; }
    
    /* Footer dưới vòng tròn */
    .gauge-footer { 
        color: #58a6ff; font-size: 20px; font-weight: 800; text-align: center; 
        margin-top: -30px; padding-bottom: 20px;
    }

    /* Bảng dữ liệu */
    [data-testid="stDataFrame"] { border: 1px solid #30363d !important; border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC MỐC KPI ---
def get_targets(pow_val):
    p_mil = pow_val / 1_000_000
    if p_mil < 15: return 100_000_000, 200_000
    elif p_mil < 20: return 200_000_000, 250_000
    elif p_mil < 30: return 250_000_000, 300_000
    else: return 300_000_000, 400_000

# --- 4. DATA ENGINE (FIX LỖI TÊN CỘT) ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=351056493'

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(URL)
        df.columns = [str(c).strip() for c in df.columns]
        
        # Tìm cột thông minh (chứa từ khóa)
        c_name = next((c for c in df.columns if 'Tên' in c), None)
        c_pow = next((c for c in df.columns if 'Kỷ Lục' in c or 'Sức Mạnh' in c), None)
        c_kill = next((c for c in df.columns if 'Tổng Điểm Tiêu Diệt' in c), None)

        if not c_pow or not c_kill:
            st.error(f"Lỗi: Không tìm thấy cột 'Kỷ Lục' hoặc 'Tiêu Diệt'. Kiểm tra lại tên cột trên Google Sheet!")
            return None

        # Chuyển đổi số liệu
        for col in [c_pow, c_kill]:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        dead_cols = ['T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong']
        df['SUM_DEAD_UNITS'] = df[[c for c in dead_cols if c in df.columns]].sum(axis=1)
        
        targets = df[c_pow].apply(get_targets)
        df['T_KILL'] = [x[0] for x in targets]
        df['T_DEAD'] = [x[1] for x in targets]
        df['K_PCT'] = (df[c_kill] / df['T_KILL'] * 100).round(1)
        df['D_PCT'] = (df['SUM_DEAD_UNITS'] / df['T_DEAD'] * 100).round(1)
        
        df = df.sort_values(by='K_PCT', ascending=False).reset_index(drop=True)
        df.insert(0, 'RANK', range(1, len(df) + 1))
        
        return df, c_name, c_pow, c_kill
    except Exception as e:
        st.error(f"Lỗi kết nối: {e}")
        return None

# --- 5. HIỂN THỊ ---
res = load_data()
if res:
    df, c_name, c_pow, c_kill = res
    st.markdown('<div class="main-header">SHARED HOUSE 3956 - KPI MANAGEMENT</div>', unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["👤 PROFILE CHI TIẾT", "📊 TỔNG QUAN QUÂN ĐOÀN", "🏆 BẢNG VINH DANH (>100%)"])
    
    with t1:
        sel = st.selectbox("🔍 CHỌN CHIẾN BINH:", df[c_name].unique())
        d = df[df[c_name] == sel].iloc[0]
        
        # Hàng 1: Rank & KPI %
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="info-box"><div class="info-label">🏆 HẠNG</div><div class="info-value" style="color:#FFD700;">#{int(d["RANK"])}</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="info-box"><div class="info-label">🛡️ SỨC MẠNH</div><div class="info-value">{int(d[c_pow]):,}</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="info-box"><div class="info-label">🔥 % KILL</div><div class="info-value" style="color:#00FFFF;">{d["K_PCT"]}%</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="info-box"><div class="info-label">💀 % DEAD</div><div class="info-value">{d["D_PCT"]}%</div></div>', unsafe_allow_html=True)

        # Hàng 2: Chi tiết thông số (Dạng Box nằm dưới)
        st.markdown("##### 📌 THÔNG SỐ CHI TIẾT TỪ SHEET")
        row_cols = st.columns(6)
        detail_fields = ['ID nhân vật', c_name, 'Sức Mạnh', c_pow, 'T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong', c_kill, 'Tổng Tiêu Diệt T5', 'Tổng Tiêu Diệt T4']
        
        for idx, field in enumerate(detail_fields):
            if field in d:
                val = d[field]
                formatted_val = f"{int(val):,}" if isinstance(val, (int, float)) else val
                row_cols[idx % 6].markdown(f'<div class="info-box"><div class="info-label">{field}</div><div class="info-value" style="font-size:16px;">{formatted_val}</div></div>', unsafe_allow_html=True)

        # Hàng 3: Biểu đồ Gauge
        g1, g2 = st.columns(2)
        with g1:
            fig_k = go.Figure(go.Indicator(mode="gauge+number", value=d['K_PCT'],
                number={'suffix': "%", 'font': {'size': 60}},
                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00FFFF"}}))
            fig_k.update_layout(height=300, margin=dict(t=50, b=0), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_k, use_container_width=True)
            st.markdown(f'<div class="gauge-footer">KILL: {d[c_kill]/1e6:.1f}M / {d["T_KILL"]/1e6:.1f}M</div>', unsafe_allow_html=True)

        with g2:
            fig_d = go.Figure(go.Indicator(mode="gauge+number", value=d['D_PCT'],
                number={'suffix': "%", 'font': {'size': 60}},
                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#f29b05"}}))
            fig_d.update_layout(height=300, margin=dict(t=50, b=0), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
            st.plotly_chart(fig_d, use_container_width=True)
            st.markdown(f'<div class="gauge-footer">DEAD: {int(d["SUM_DEAD_UNITS"]):,} / {int(d["T_DEAD"]):,}</div>', unsafe_allow_html=True)

    with t2:
        st.subheader("📋 BẢNG TỔNG HỢP QUÂN ĐOÀN")
        st.dataframe(df[['RANK', c_name, c_pow, c_kill, 'K_PCT', 'SUM_DEAD_UNITS', 'D_PCT']], use_container_width=True, height=600)

    with t3:
        st.subheader("🎖️ CHIẾN BINH XUẤT SẮC (KPI > 100%)")
        vinh_danh = df[df['K_PCT'] >= 100]
        if not vinh_danh.empty:
            st.table(vinh_danh[['RANK', c_name, 'K_PCT', 'D_PCT']])
        else:
            st.info("Chưa có chiến binh nào đạt 100% KPI Kill.")
