import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide", initial_sidebar_state="collapsed")

# --- 2. GIAO DIỆN CSS (SIÊU TO & RÕ) ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    [data-testid="stHeader"] {background: rgba(0,0,0,0);}
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    
    .main-header { 
        background: linear-gradient(90deg, #00FFFF, #58a6ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; font-size: 55px; font-weight: 900; padding: 20px;
    }

    /* Tab và Font chữ to */
    button[data-baseweb="tab"] p { font-size: 26px !important; font-weight: bold !important; }
    .stSelectbox label p { font-size: 22px !important; color: #00FFFF !important; }

    /* Info Box hiện đại */
    .info-box { 
        background: #161b22; border: 2px solid #30363d; border-radius: 15px; 
        padding: 20px; text-align: center; margin-bottom: 20px;
    }
    .info-label { color: #8b949e; font-size: 18px; font-weight: bold; text-transform: uppercase; }
    .info-value { color: #ffffff; font-size: 35px; font-weight: bold; }
    
    /* Footer mục tiêu dưới biểu đồ */
    .target-footer { 
        color: #58a6ff; font-size: 28px; font-weight: bold; text-align: center; 
        margin-top: -20px; padding: 15px; background: rgba(88, 166, 255, 0.1); border-radius: 10px;
    }

    /* Bảng dữ liệu siêu to */
    [data-testid="stDataFrame"] td { font-size: 22px !important; height: 60px !important; }
    [data-testid="stDataFrame"] th { font-size: 24px !important; color: #00FFFF !important; background-color: #161b22 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC MỐC KPI ---
def get_targets(pow_val):
    p_mil = pow_val / 1_000_000
    if p_mil < 15: return 100_000_000, 200_000
    elif p_mil < 20: return 200_000_000, 250_000
    elif p_mil < 30: return 250_000_000, 300_000
    else: return 300_000_000, 400_000

# --- 4. DATA ENGINE (TỰ ĐỘNG NHẬN DIỆN CỘT) ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=351056493'

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(URL)
        df.columns = [str(c).strip() for c in df.columns]
        
        # Tìm cột chính
        c_name = next((c for c in df.columns if 'Tên' in c), None)
        c_pow = next((c for c in df.columns if 'Sức Mạnh' in c or 'Kỷ Lục' in c), None)
        c_kill = next((c for c in df.columns if 'Tổng Điểm Tiêu Diệt' in c), None)

        # Chuyển đổi số
        for col in [c_pow, c_kill]:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        dead_cols = ['T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong']
        df['SUM_DEAD'] = df[[c for c in dead_cols if c in df.columns]].sum(axis=1)
        
        # Tính toán KPI
        targets = df[c_pow].apply(get_targets)
        df['T_KILL'] = [x[0] for x in targets]
        df['T_DEAD'] = [x[1] for x in targets]
        df['K_PCT'] = (df[c_kill] / df['T_KILL'] * 100).round(1)
        df['D_PCT'] = (df['SUM_DEAD'] / df['T_DEAD'] * 100).round(1)
        
        df = df.sort_values(by='K_PCT', ascending=False).reset_index(drop=True)
        df.insert(0, 'HẠNG', range(1, len(df) + 1))
        
        return df, c_name, c_pow, c_kill
    except Exception as e:
        st.error(f"Lỗi: {e}")
        return None

# --- 5. HIỂN THỊ ---
res = load_data()
if res:
    df, c_name, c_pow, c_kill = res
    st.markdown('<div class="main-header">SHARED HOUSE 3956 KPI COMMANDER</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["👤 HỒ SƠ CHI TIẾT", "📊 TỔNG HỢP QUÂN ĐOÀN"])
    
    with tab1:
        sel = st.selectbox("🔍 CHỌN TÊN CHIẾN BINH:", df[c_name].unique())
        if sel:
            d = df[df[c_name] == sel].iloc[0]
            
            # Chỉ số tóm tắt
            col1, col2, col3, col4 = st.columns(4)
            col1.markdown(f'<div class="info-box"><div class="info-label">🏆 HẠNG</div><div class="info-value" style="color:#FFD700;">#{int(d["HẠNG"])}</div></div>', unsafe_allow_html=True)
            col2.markdown(f'<div class="info-box"><div class="info-label">🛡️ SỨC MẠNH</div><div class="info-value">{int(d[c_pow]):,}</div></div>', unsafe_allow_html=True)
            col3.markdown(f'<div class="info-box"><div class="info-label">🔥 % KILL</div><div class="info-value" style="color:#00FFFF;">{d["K_PCT"]}%</div></div>', unsafe_allow_html=True)
            col4.markdown(f'<div class="info-box"><div class="info-label">💀 % DEAD</div><div class="info-value">{d["D_PCT"]}%</div></div>', unsafe_allow_html=True)

            # --- 2 VÒNG TRÒN KPI QUAY TRỞ LẠI ---
            g1, g2 = st.columns(2)
            with g1:
                fig_k = go.Figure(go.Indicator(mode="gauge+number", value=d['K_PCT'],
                    number={'suffix': "%", 'font': {'size': 90}},
                    title={'text': "KPI TIÊU DIỆT", 'font': {'size': 35, 'color': '#00FFFF'}},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00FFFF"}}))
                fig_k.update_layout(height=450, paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_k, use_container_width=True)
                st.markdown(f'<div class="target-footer">MỤC TIÊU: {int(d["T_KILL"]):,} KILL</div>', unsafe_allow_html=True)

            with g2:
                fig_d = go.Figure(go.Indicator(mode="gauge+number", value=d['D_PCT'],
                    number={'suffix': "%", 'font': {'size': 90}},
                    title={'text': "KPI TỬ VONG", 'font': {'size': 35, 'color': '#f29b05'}},
                    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#f29b05"}}))
                fig_d.update_layout(height=450, paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_d, use_container_width=True)
                st.markdown(f'<div class="target-footer">MỤC TIÊU: {int(d["T_DEAD"]):,} DEAD</div>', unsafe_allow_html=True)

            # --- BẢNG FULL THÔNG TIN CHI TIẾT TỪ SHEET ---
            st.write("<br>", unsafe_allow_html=True)
            st.subheader("📑 TẤT CẢ THÔNG SỐ CHI TIẾT TỪ SHEET")
            # Loại bỏ các cột phụ tính toán để chỉ hiện data gốc và KPI chính
            full_data_player = df[df[c_name] == sel].drop(columns=['T_KILL', 'T_DEAD'])
            st.dataframe(full_data_player, use_container_width=True)

    with tab2:
        st.markdown("<h2 style='text-align: center; color: #00FFFF;'>BẢNG XẾP HẠNG TOÀN QUÂN</h2>", unsafe_allow_html=True)
        view_df = df[['HẠNG', c_name, c_pow, c_kill, 'K_PCT', 'SUM_DEAD', 'D_PCT']].copy()
        view_df.columns = ['HẠNG 🏆', 'CHIẾN BINH 🥷', 'SỨC MẠNH 🛡️', 'ĐIỂM KILL ⚔️', '% KILL 🔥', 'LÍNH CHẾT 💀', '% DEAD ⚰️']
        
        st.dataframe(view_df.style.format({
            'SỨC MẠNH 🛡️': '{:,.0f}', 'ĐIỂM KILL ⚔️': '{:,.0f}', 
            '% KILL 🔥': '{:.1f}%', 'LÍNH CHẾT 💀': '{:,.0f}', '% DEAD ⚰️': '{:.1f}%'
        }), use_container_width=True, height=800)
