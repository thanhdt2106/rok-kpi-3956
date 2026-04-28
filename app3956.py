import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide", initial_sidebar_state="collapsed")

# --- 2. GIAO DIỆN CSS NÂNG CAO (BẢNG ĐẸP & CÓ ICON) ---
st.markdown("""
    <style>
    /* Ẩn Sidebar và Header */
    [data-testid="stSidebar"] {display: none;}
    [data-testid="stHeader"] {background: rgba(0,0,0,0);}
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    
    /* Tiêu đề chính với hiệu ứng Gradient */
    .main-header { 
        background: linear-gradient(90deg, #00FFFF, #58a6ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center; 
        font-size: 55px; 
        font-weight: 900; 
        padding: 10px 0;
        margin-bottom: 20px;
    }

    /* Tabs thiết kế hiện đại */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        border: none !important;
    }
    button[data-baseweb="tab"] p {
        font-size: 24px !important;
        font-weight: bold !important;
    }

    /* --- STYLE BẢNG TỔNG HỢP SIÊU ĐẸP --- */
    [data-testid="stDataFrame"] {
        border: 1px solid #30363d !important;
        border-radius: 15px !important;
        overflow: hidden !important;
        font-size: 22px !important;
    }
    
    /* Màu nền tiêu đề cột và Icon */
    [data-testid="stDataFrame"] th {
        background-color: #161b22 !important;
        color: #00FFFF !important;
        font-weight: 900 !important;
        text-align: center !important;
        height: 70px !important;
        border-bottom: 2px solid #58a6ff !important;
    }

    /* Hiệu ứng dòng khi di chuột qua */
    [data-testid="stDataFrame"] tr:hover {
        background-color: rgba(88, 166, 255, 0.1) !important;
    }

    /* Bo góc các Info Box ở Tab 1 */
    .info-box { 
        background: #161b22; 
        border: 1px solid #30363d; 
        border-radius: 20px; 
        padding: 20px; 
        text-align: center; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .info-label { color: #8b949e; font-size: 18px; font-weight: bold; }
    .info-value { color: #ffffff; font-size: 30px; font-weight: bold; }
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

@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_csv(URL)
        df.columns = [str(c).replace('\n', ' ').strip() for c in df.columns]
        
        c_name = 'Tên Người Dùng'
        c_kyluc = 'Kỷ Lục Sức Mạnh'
        c_kill = 'Tổng Điểm Tiêu Diệt'
        
        numeric_cols = [c for c in df.columns if c != c_name]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        dead_parts = ['T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong']
        df['SUM_DEAD'] = df[[c for c in dead_parts if c in df.columns]].sum(axis=1)
        
        targets = df[c_kyluc].apply(get_targets)
        df['T_KILL'] = [x[0] for x in targets]
        df['T_DEAD'] = [x[1] for x in targets]
        
        df['K_PCT'] = (df[c_kill] / df['T_KILL'] * 100).round(1)
        df['D_PCT'] = (df['SUM_DEAD'] / df['T_DEAD'] * 100).round(1)
        
        df = df.sort_values(by='K_PCT', ascending=False).reset_index(drop=True)
        df.insert(0, 'HẠNG', range(1, len(df) + 1))
        
        return df, c_name, c_kyluc, c_kill
    except Exception as e:
        return None

# --- 5. HIỂN THỊ ---
res = load_data()
if res:
    df, c_name, c_kyluc, c_kill = res
    st.markdown('<div class="main-header">SHARED HOUSE 3956 KPI</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["👤 CHI TIẾT", "📊 BẢNG TỔNG HỢP QUÂN ĐOÀN"])
    
    with tab1:
        sel = st.selectbox("🔍 CHỌN CHIẾN BINH:", df[c_name].unique())
        if sel:
            d = df[df[c_name] == sel].iloc[0]
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.markdown(f'<div class="info-box"><div class="info-label">🏆 HẠNG</div><div class="info-value" style="color:#FFD700;">#{int(d["HẠNG"])}</div></div>', unsafe_allow_html=True)
            with col2: st.markdown(f'<div class="info-box"><div class="info-label">⭐ KỶ LỤC</div><div class="info-value">{int(d[c_kyluc]):,}</div></div>', unsafe_allow_html=True)
            with col3: st.markdown(f'<div class="info-box"><div class="info-label">🔥 % KILL</div><div class="info-value" style="color:#00FFFF;">{d["K_PCT"]}%</div></div>', unsafe_allow_html=True)
            with col4: st.markdown(f'<div class="info-box"><div class="info-label">💀 % DEAD</div><div class="info-value">{d["D_PCT"]}%</div></div>', unsafe_allow_html=True)

    with tab2:
        st.write("<br>", unsafe_allow_html=True)
        
        # --- BẢNG VỚI TIÊU ĐỀ CÓ ICON ---
        view_df = df[['HẠNG', c_name, c_kyluc, c_kill, 'K_PCT', 'SUM_DEAD', 'D_PCT']].copy()
        view_df.columns = [
            'No. 🏆', 
            'CHIẾN BINH 🥷', 
            'KỶ LỤC POW 🛡️', 
            'ĐIỂM KILL ⚔️', 
            'KPI KILL 🔥', 
            'LÍNH CHẾT 💀', 
            'KPI DEAD ⚰️'
        ]
        
        # Thiết lập màu sắc dựa trên % hoàn thành
        def highlight_kpi(val):
            try:
                num = float(val.replace('%', ''))
                if num >= 100: return 'color: #00FF00; font-weight: bold;' # Xanh lá nếu đạt 100%
                if num < 50: return 'color: #FF4B4B;' # Đỏ nếu quá thấp
                return ''
            except: return ''

        styled_df = view_df.style.format({
            'KỶ LỤC POW 🛡️': '{:,.0f}', 
            'ĐIỂM KILL ⚔️': '{:,.0f}', 
            'KPI KILL 🔥': '{:.1f}%', 
            'LÍNH CHẾT 💀': '{:,.0f}', 
            'KPI DEAD ⚰️': '{:.1f}%'
        }).applymap(highlight_kpi, subset=['KPI KILL 🔥', 'KPI DEAD ⚰️'])
        
        st.dataframe(styled_df, use_container_width=True, height=1000)
