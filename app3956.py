import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide", initial_sidebar_state="collapsed")

# --- 2. GIAO DIỆN CSS TỐI ƯU (CHỮ TO & FULL MÀN HÌNH) ---
st.markdown("""
    <style>
    /* Ẩn Sidebar và Header dư thừa */
    [data-testid="stSidebar"] {display: none;}
    [data-testid="stHeader"] {background: rgba(0,0,0,0);}

    /* Nền tối và font chữ cơ bản to hơn */
    .stApp { background-color: #0d1117; color: #c9d1d9; font-size: 18px; }
    
    /* Tiêu đề chính cực đại */
    .main-header { 
        color: #00FFFF; 
        text-align: center; 
        font-size: 50px; 
        font-weight: 900; 
        padding: 20px; 
        border-bottom: 4px solid #58a6ff; 
        margin-bottom: 30px; 
    }

    /* Các thẻ thông số (Info Box) phóng to */
    .info-box { 
        background: #161b22; 
        border: 2px solid #30363d; 
        border-radius: 15px; 
        padding: 20px; 
        text-align: center; 
        margin-bottom: 15px; 
    }
    .info-label { color: #8b949e; font-size: 18px; font-weight: bold; text-transform: uppercase; margin-bottom: 8px; }
    .info-value { color: #ffffff; font-size: 28px; font-weight: bold; }
    
    /* Chỉnh cỡ chữ cho Selectbox và Tabs */
    .stSelectbox label p { font-size: 22px !important; font-weight: bold; color: #00FFFF !important; }
    button[data-baseweb="tab"] p { font-size: 24px !important; font-weight: bold !important; }

    /* Footer mục tiêu dưới biểu đồ */
    .target-footer { 
        color: #58a6ff; 
        font-size: 24px; 
        font-weight: bold; 
        text-align: center; 
        margin-top: -15px; 
        padding: 15px;
        background: rgba(88, 166, 255, 0.1);
        border-radius: 10px;
    }

    /* Ép bảng dữ liệu hiển thị chữ to hơn */
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
        font-size: 20px !important;
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

@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_csv(URL)
        df.columns = [str(c).replace('\n', ' ').strip() for c in df.columns]
        
        def find_col(keys):
            for c in df.columns:
                if any(k.lower() in c.lower() for k in keys): return c
            return None

        c_name = find_col(['Tên Người Dùng', 'Tên'])
        c_kyluc = find_col(['Kỷ Lục Sức Mạnh', 'Kỷ Lục'])
        c_kill = find_col(['Tổng Điểm Tiêu Diệt', 'Tổng Tiêu'])
        
        numeric_cols = [c for c in df.columns if c != c_name]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        dead_parts = ['T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'T1 tử vong']
        df['SUM_DEAD_UNITS'] = df[[c for c in dead_parts if c in df.columns]].sum(axis=1)
        
        targets = df[c_kyluc].apply(get_targets)
        df['T_KILL'] = [x[0] for x in targets]
        df['T_DEAD'] = [x[1] for x in targets]
        
        df['K_PCT'] = (df[c_kill] / df['T_KILL'] * 100).round(1)
        df['D_PCT'] = (df['SUM_DEAD_UNITS'] / df['T_DEAD'] * 100).round(1)
        
        # Xếp hạng chỉ theo % Kill
        df = df.sort_values(by='K_PCT', ascending=False).reset_index(drop=True)
        df.insert(0, 'HẠNG', df.index + 1)
        
        return df, c_name, c_kyluc, c_kill
    except Exception as e:
        st.error(f"Lỗi nạp dữ liệu: {e}")
        return None

# --- 5. HIỂN THỊ ---
res = load_data()
if res:
    df, c_name, c_kyluc, c_kill = res
    st.markdown('<div class="main-header">SHARED HOUSE 3956 - KPI COMMANDER</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👤 HỒ SƠ CHI TIẾT", "📊 BẢNG TỔNG HỢP QUÂN ĐOÀN", "🏆 VINH DANH (>100% KILL)"])
    
    with tab1:
        sel = st.selectbox("🔍 TÌM KIẾM CHIẾN BINH:", df[c_name].unique())
        if sel:
            d = df[df[c_name] == sel].iloc[0]
            
            # --- CÁC CHỈ SỐ CHÍNH (TO RÕ) ---
            st.write("<br>", unsafe_allow_html=True)
            m1, m2, m3, m4 = st.columns(4)
            with m1: st.markdown(f'<div class="info-box"><div class="info-label">🏆 Thứ Hạng</div><div class="info-value" style="color:#f29b05; font-size:45px;">#{int(d["HẠNG"])}</div></div>', unsafe_allow_html=True)
            with m2: st.markdown(f'<div class="info-box"><div class="info-label">⭐ Kỷ Lực Sức Mạnh</div><div class="info-value">{int(d[c_kyluc]):,}</div></div>', unsafe_allow_html=True)
            with m3: st.markdown(f'<div class="info-box"><div class="info-label">🔥 % Hoàn Thành Kill</div><div class="info-value" style="color:#00FFFF;">{d["K_PCT"]}%</div></div>', unsafe_allow_html=True)
            with m4: st.markdown(f'<div class="info-box"><div class="info-label">💀 % Hoàn Thành Dead</div><div class="info-value">{d["D_PCT"]}%</div></div>', unsafe_allow_html=True)

            with st.expander("📝 XEM TẤT CẢ THÔNG SỐ CHI TIẾT", expanded=False):
                all_cols = [c for c in df.columns if c not in ['HẠNG', 'T_KILL', 'T_DEAD', 'K_PCT', 'D_PCT', 'SUM_DEAD_UNITS']]
                cols = st.columns(4)
                for i, col in enumerate(all_cols):
                    with cols[i % 4]:
                        val = f"{int(d[col]):,}" if isinstance(d[col], (int, float)) else d[col]
                        st.markdown(f'<div class="info-box"><div class="info-label">{col}</div><div class="info-value" style="font-size:18px;">{val}</div></div>', unsafe_allow_html=True)

            # --- BIỂU ĐỒ GAUGE LỚN ---
            st.write("---")
            k1, k2 = st.columns(2)
            with k1:
                fig_k = go.Figure(go.Indicator(mode="gauge+number", value=d['K_PCT'], 
                                              number={'suffix': "%", 'font': {'size': 80}},
                                              title={'text': "KPI TIÊU DIỆT", 'font': {'size': 30, 'color': '#00FFFF'}},
                                              gauge={'axis': {'range': [0, 100], 'tickfont': {'size': 20}}, 'bar': {'color': "#00FFFF"}}))
                fig_k.update_layout(height=450, margin=dict(t=80, b=0), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_k, use_container_width=True)
                st.markdown(f'<div class="target-footer">MỤC TIÊU: {int(d["T_KILL"]):,} KILL</div>', unsafe_allow_html=True)
                
            with k2:
                fig_d = go.Figure(go.Indicator(mode="gauge+number", value=d['D_PCT'], 
                                              number={'suffix': "%", 'font': {'size': 80}},
                                              title={'text': "KPI TỬ VONG", 'font': {'size': 30, 'color': '#f29b05'}},
                                              gauge={'axis': {'range': [0, 100], 'tickfont': {'size': 20}}, 'bar': {'color': "#f29b05"}}))
                fig_d.update_layout(height=450, margin=dict(t=80, b=0), paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_d, use_container_width=True)
                st.markdown(f'<div class="target-footer">MỤC TIÊU: {int(d["T_DEAD"]):,} DEAD</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown("<h2 style='text-align: center; color: #00FFFF;'>BẢNG THỐNG KÊ CHI TIẾT QUÂN ĐOÀN</h2>", unsafe_allow_html=True)
        
        # Đổi tên tiêu đề cột rõ ràng
        view_df = df[['HẠNG', c_name, c_kyluc, c_kill, 'K_PCT', 'SUM_DEAD_UNITS', 'D_PCT']].copy()
        view_df.columns = [
            'HẠNG', 
            'TÊN CHIẾN BINH', 
            'KỶ LỤC SỨC MẠNH', 
            'TỔNG ĐIỂM TIÊU DIỆT', 
            '% HOÀN THÀNH KILL', 
            'TỔNG ĐƠN VỊ TỬ VONG', 
            '% HOÀN THÀNH DEAD'
        ]
        
        st.dataframe(
            view_df.style.format({
                'KỶ LỤC SỨC MẠNH': '{:,.0f}', 
                'TỔNG ĐIỂM TIÊU DIỆT': '{:,.0f}', 
                '% HOÀN THÀNH KILL': '{:.1f}%', 
                'TỔNG ĐƠN VỊ TỬ VONG': '{:,.0f}', 
                '% HOÀN THÀNH DEAD': '{:.1f}%'
            }), 
            use_container_width=True, 
            height=800
        )

    with tab3:
        st.subheader("🔥 DANH SÁCH CHIẾN BINH VƯỢT MỐC 100% KILL")
        winner_df = df[df['K_PCT'] >= 100][['HẠNG', c_name, 'K_PCT', 'D_PCT']]
        winner_df.columns = ['HẠNG', 'TÊN CHIẾN BINH', '% KILL', '% DEAD']
        
        if not winner_df.empty:
            st.balloons()
            st.table(winner_df.style.format({'% KILL': '{:.1f}%', '% DEAD': '{:.1f}%'}))
        else:
            st.info("Chưa có chiến binh nào vượt mốc 100% Kill.")
