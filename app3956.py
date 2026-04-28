import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide", initial_sidebar_state="collapsed")

# --- 2. GIAO DIỆN CSS (TABLE & ICON OPTIMIZED) ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    [data-testid="stHeader"] {background: rgba(0,0,0,0);}
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    
    .main-header { 
        background: linear-gradient(90deg, #00FFFF, #58a6ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center; font-size: 50px; font-weight: 900; padding: 10px;
    }

    /* Định dạng bảng đẹp hơn */
    [data-testid="stDataFrame"] { 
        border: 1px solid #30363d !important; 
        border-radius: 10px !important; 
    }

    .info-box { 
        background: #161b22; border: 1px solid #30363d; border-radius: 15px; 
        padding: 15px; text-align: center; margin-bottom: 10px;
    }
    .info-label { color: #8b949e; font-size: 16px; font-weight: bold; }
    .info-value { color: #ffffff; font-size: 26px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC MỐC KPI ---
def get_targets(pow_val):
    p_mil = pow_val / 1_000_000
    if p_mil < 15: return 100_000_000, 200_000
    elif p_mil < 20: return 200_000_000, 250_000
    elif p_mil < 30: return 250_000_000, 300_000
    else: return 300_000_000, 400_000

# --- 4. DATA ENGINE (FIX LỖI NẠP CỘT) ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=351056493'

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(URL)
        df.columns = [str(c).strip() for c in df.columns]
        
        # Ánh xạ cột linh hoạt
        col_map = {
            'name': next((c for c in df.columns if 'Tên' in c), None),
            'power': next((c for c in df.columns if 'Kỷ Lục' in c), None),
            'kill': next((c for c in df.columns if 'Tổng Điểm Tiêu Diệt' in c), None)
        }
        
        if not all(col_map.values()):
            st.error(f"Thiếu cột cần thiết! Cột hiện có: {list(df.columns)}")
            return None

        # Xử lý số liệu
        for col in [col_map['power'], col_map['kill']]:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        dead_cols = ['T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong']
        df['SUM_DEAD'] = df[[c for c in dead_cols if c in df.columns]].sum(axis=1)
        
        targets = df[col_map['power']].apply(get_targets)
        df['T_KILL'] = [x[0] for x in targets]
        df['T_DEAD'] = [x[1] for x in targets]
        
        df['K_PCT'] = (df[col_map['kill']] / df['T_KILL'] * 100).round(1)
        df['D_PCT'] = (df['SUM_DEAD'] / df['T_DEAD'] * 100).round(1)
        
        df = df.sort_values(by='K_PCT', ascending=False).reset_index(drop=True)
        df.insert(0, 'HẠNG', range(1, len(df) + 1))
        
        return df, col_map
    except Exception as e:
        st.error(f"Lỗi hệ thống: {e}")
        return None

# --- 5. HIỂN THỊ ---
data_res = load_data()
if data_res:
    df, c = data_res
    st.markdown('<div class="main-header">SHARED HOUSE 3956 KPI</div>', unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["👤 HỒ SƠ", "📊 TỔNG HỢP QUÂN ĐOÀN"])
    
    with t1:
        sel = st.selectbox("🔍 CHIẾN BINH:", df[c['name']].unique())
        d = df[df[c['name']] == sel].iloc[0]
        
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="info-box"><div class="info-label">🏆 HẠNG</div><div class="info-value">#{int(d["HẠNG"])}</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="info-box"><div class="info-label">🛡️ POW</div><div class="info-value">{int(d[c["power"]]):,}</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="info-box"><div class="info-label">🔥 % KILL</div><div class="info-value">{d["K_PCT"]}%</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="info-box"><div class="info-label">💀 % DEAD</div><div class="info-value">{d["D_PCT"]}%</div></div>', unsafe_allow_html=True)

    with t2:
        # Chuẩn bị bảng với Icon tiêu đề
        view_df = df[['HẠNG', c['name'], c['power'], c['kill'], 'K_PCT', 'SUM_DEAD', 'D_PCT']].copy()
        view_df.columns = [
            'Hạng 🏆', 'Chiến Binh 🥷', 'Sức Mạnh 🛡️', 'Điểm Kill ⚔️', 
            'KPI Kill 🔥', 'Lính Chết 💀', 'KPI Dead ⚰️'
        ]

        # Sửa lỗi AttributeError bằng cách dùng map() thay cho applymap()
        def color_kpi(val):
            try:
                v = float(str(val).replace('%', ''))
                if v >= 100: return 'color: #00FF00; font-weight: bold'
                if v < 50: return 'color: #FF4B4B'
                return ''
            except: return ''

        # Render bảng đẹp
        st.dataframe(
            view_df.style.format({
                'Sức Mạnh 🛡️': '{:,.0f}',
                'Điểm Kill ⚔️': '{:,.0f}',
                'KPI Kill 🔥': '{:.1f}%',
                'Lính Chết 💀': '{:,.0f}',
                'KPI Dead ⚰️': '{:.1f}%'
            }).map(color_kpi, subset=['KPI Kill 🔥', 'KPI Dead ⚰️']),
            use_container_width=True,
            height=800
        )
