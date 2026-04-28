import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH ---
st.set_page_config(page_title="FTD KPI SYSTEM", layout="wide")

# CSS Custom
st.markdown("""
    <style>
    .metric-card { background: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; margin-bottom: 10px; }
    .label { color: #8899a6; font-size: 11px; text-transform: uppercase; }
    .value { color: #00d4ff; font-size: 18px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 2. XỬ LÝ DỮ LIỆU ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
GID = '351056493'
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}'

@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(URL)
        df.columns = [str(c).strip() for c in df.columns]
        
        # Làm sạch và định dạng số
        cols_numeric = ['Sức Mạnh', 'T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong', 'Tổng Điểm Tiêu Diệt', 'Tài Nguyên Thu Thập']
        for c in cols_numeric:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            
        # Tính DEAD Weighted Score
        df['DEAD_SCORE'] = (df['T5 tử vong'] * 10) + (df['T4 tử vong'] * 4) + (df['T3 tử vong'] * 1) + (df['T2 tử vong'] * 1)
        
        # KPI Target (Dựa trên Sức mạnh - Ví dụ mỗi 10M Power cần 1M Kill và 500k Dead Score)
        df['KILL_TARGET'] = (df['Sức Mạnh'] / 10000000) * 1000000
        df['DEAD_TARGET'] = (df['Sức Mạnh'] / 10000000) * 500000
        
        # Phần trăm tiến độ
        df['KILL_KPI'] = (df['Tổng Điểm Tiêu Diệt'] / df['KILL_TARGET']) * 100
        df['DEAD_KPI'] = (df['DEAD_SCORE'] / df['DEAD_TARGET']) * 100
        df['TOTAL_KPI'] = (df['KILL_KPI'] + df['DEAD_KPI']) / 2
        
        # Sắp xếp Rank
        df = df.sort_values(by='TOTAL_KPI', ascending=False).reset_index(drop=True)
        df.insert(0, 'RANK', df.index + 1)
        
        return df
    except Exception as e:
        st.error(f"Lỗi tải dữ liệu: {e}")
        return None

df = load_data()

# --- 3. GIAO DIỆN ---
if df is not None:
    st.title("🛡️ COMMAND CENTER: KPI TRACKER")
    
    # Select box
    names = df['Tên Người Dùng'].astype(str).tolist()
    sel = st.selectbox("🔍 CHỌN CHIẾN BINH:", names)
    
    d = df[df['Tên Người Dùng'] == sel].iloc[0]
    
    # Tabs
    tab1, tab2 = st.tabs(["📊 HỒ SƠ CHI TIẾT", "📋 BẢNG XẾP HẠNG"])
    
    with tab1:
        # Gauge KPI
        col1, col2 = st.columns(2)
        
        def create_gauge(title, value):
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=min(value, 100),
                title={'text': title},
                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00d4ff"}}
            ))
            fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)')
            return fig

        with col1: st.plotly_chart(create_gauge("TIẾN ĐỘ KILL (%)", d['KILL_KPI']), use_container_width=True)
        with col2: st.plotly_chart(create_gauge("TIẾN ĐỘ DEAD (WEIGHTED %)", d['DEAD_KPI']), use_container_width=True)
        
        st.divider()
        st.subheader("📝 THÔNG TIN DỮ LIỆU GỐC")
        
        # Hiển thị tất cả các cột
        cols = st.columns(3)
        for i, col_name in enumerate(df.columns):
            if col_name not in ['RANK', 'KILL_KPI', 'DEAD_KPI', 'TOTAL_KPI', 'KILL_TARGET', 'DEAD_TARGET']:
                val = d[col_name]
                # Format số
                disp_val = f"{val:,.0f}" if isinstance(val, (int, float)) else val
                
                with cols[i % 3]:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="label">{col_name}</div>
                            <div class="value">{disp_val}</div>
                        </div>
                    """, unsafe_allow_html=True)

    with tab2:
        st.dataframe(df.style.background_gradient(subset=['TOTAL_KPI'], cmap='Blues'), use_container_width=True)

else:
    st.warning("Vui lòng kiểm tra lại liên kết Google Sheet.")
