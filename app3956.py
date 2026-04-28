import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="FTD KPI | COMMAND CENTER", layout="wide")

# --- 2. GIAO DIỆN (CSS CUSTOM) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e6ed; }
    .main-header {
        color: #00d4ff; text-align: center; font-size: 32px;
        font-weight: bold; padding: 15px;
        text-transform: uppercase;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
    }
    .command-card {
        background: #1a1c23; border-radius: 15px; padding: 25px;
        border: 1px solid rgba(0, 212, 255, 0.2); margin-bottom: 20px;
    }
    .mini-stat-label { color: #8899a6; font-size: 11px; text-transform: uppercase; }
    .mini-stat-value { color: #ffffff; font-size: 17px; font-weight: bold; }
    .target-value { color: #00d4ff; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. QUẢN LÝ NGÔN NGỮ ---
lang = st.sidebar.radio("NGÔN NGỮ / LANGUAGE", ["VN", "EN"])
texts = {
    "VN": {
        "header": "🛡️ HỆ THỐNG QUẢN LÝ KPI FTD",
        "search": "🔍 TRA CỨU CHIẾN BINH:",
        "select": "--- Chọn tên ---",
        "pow": "SỨC MẠNH", "tk": "KILL TĂNG", "td": "DEAD TĂNG (T2-T5)", "res": "TÀI NGUYÊN",
        "table": "📋 BẢNG XẾP HẠNG KPI",
        "cols": ['RANK', 'ID', 'TÊN', 'SỨC MẠNH', 'KILL (+)', 'DEAD (+)', 'TÀI NGUYÊN', 'KPI']
    },
    "EN": {
        "header": "🛡️ FTD KPI COMMAND CENTER",
        "search": "🔍 WARRIOR LOOKUP:",
        "select": "--- Select name ---",
        "pow": "POWER", "tk": "KILL INC", "td": "DEAD INC (T2-T5)", "res": "RESOURCES",
        "table": "📋 KPI RANKING TABLE",
        "cols": ['RANK', 'ID', 'NAME', 'POWER', 'KILL (+)', 'DEAD (+)', 'RESOURCES', 'KPI']
    }
}
L = texts[lang]

# --- 4. XỬ LÝ DỮ LIỆU ---
SHEET_ID = '1MJQSE3siwFWmQNdJmbbJ6RsilvcoxWTu-r6h-UdHugE'
# Gid 371969335 là sheet chứa dữ liệu hiện tại (theo ảnh)
URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=351056493'

@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(URL)
        # Làm sạch tên cột (bỏ khoảng trắng thừa)
        df.columns = [c.strip() for c in df.columns]
        
        # 1. Chuyển đổi ID và số liệu
        df['ID nhân vật'] = df['ID nhân vật'].astype(str).str.split('.').str[0]
        
        # 2. Tính DEAD (+) = T2 + T3 + T4 + T5 (Các cột E, F, G, H trong sheet)
        # Chú ý: Dựa theo ảnh, T5 tử vong (E), T4 (F), T3 (G), T2 (H)
        dead_cols = ['T5 tử vong', 'T4 tử vong', 'T3 tử vong', 'T2 tử vong']
        for col in dead_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        df['DEAD_TOTAL'] = df[dead_cols].sum(axis=1)
        
        # 3. Lấy KILL (+) - Giả định là cột 'Tổng Tiêu Diệt T4' hoặc 'Tổng Tiêu Diệt' tùy kỳ
        # Ở đây tôi lấy 'Tổng Tiêu Diệt' (Cột L) làm mốc tăng trưởng
        df['KILL_TOTAL'] = pd.to_numeric(df['Tổng Tiêu Diệt'], errors='coerce').fillna(0)
        
        # 4. Tài nguyên (Cột R)
        df['RESOURCES'] = pd.to_numeric(df['Tài Nguyên Thu Thập'], errors='coerce').fillna(0)
        
        # 5. Tính KPI Tổng (Kill + Dead) để xếp hạng
        # Công thức: KPI = (Kill / Target_K) + (Dead / Target_D) -> Ở đây dùng tổng đơn giản để Rank
        df['KPI_SCORE'] = df['KILL_TOTAL'] + (df['DEAD_TOTAL'] * 10) # Trọng số Dead thường cao hơn
        
        # 6. Sắp xếp RANK
        df = df.sort_values(by='KPI_SCORE', ascending=False).reset_index(drop=True)
        df['RANK'] = df.index + 1
        
        return df
    except Exception as e:
        st.error(f"Lỗi nạp dữ liệu: {e}")
        return None

df = load_data()

# --- 5. HIỂN THỊ ---
if df is not None:
    st.markdown(f'<div class="main-header">{L["header"]}</div>', unsafe_allow_html=True)
    
    # --- BOX TRA CỨU ---
    names = sorted(df['Tên Người Dùng'].unique())
    sel = st.selectbox(L["search"], [L["select"]] + names)
    
    if sel != L["select"]:
        d = df[df['Tên Người Dùng'] == sel].iloc[0]
        c1, c2 = st.columns([1.5, 1])
        
        with c1:
            st.markdown(f"""
                <div class="command-card">
                    <h2 style="color:#00d4ff; margin:0;">👤 {d['Tên Người Dùng']}</h2>
                    <p style="color:#8899a6;">ID: {d['ID nhân vật']} | RANK: #{int(d['RANK'])}</p>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div><span class="mini-stat-label">{L['pow']}</span><br><span class="mini-stat-value">{int(d['Sức Mạnh']):,}</span></div>
                        <div><span class="mini-stat-label">{L['res']}</span><br><span class="mini-stat-value">{int(d['RESOURCES']):,}</span></div>
                        <div style="border-top:1px solid #333; padding-top:10px;"><span class="mini-stat-label">{L['tk']}</span><br><span class="target-value">{int(d['KILL_TOTAL']):,}</span></div>
                        <div style="border-top:1px solid #333; padding-top:10px;"><span class="mini-stat-label">{L['td']}</span><br><span class="target-value">{int(d['DEAD_TOTAL']):,}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Hiển thị chi tiết Dead từng loại
            st.write("📊 **Chi tiết quân tử vong:**")
            st.info(f"T2: {int(d['T2 tử vong']):,} | T3: {int(d['T3 tử vong']):,} | T4: {int(d['T4 tử vong']):,} | T5: {int(d['T5 tử vong']):,}")

        with c2:
            # Gauge KPI dựa trên Rank (Top % trong liên minh)
            percentile = (1 - (d['RANK'] / len(df))) * 100
            fig = go.Figure(go.Indicator(
                mode = "gauge+number", value = percentile,
                number = {'suffix': "%", 'font': {'color': '#00d4ff'}},
                title = {'text': "Bậc Chiến Đấu", 'font': {'size': 15}},
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#00d4ff"}}
            ))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=250, margin=dict(l=20,r=20,t=40,b=20))
            st.plotly_chart(fig, use_container_width=True)

    # --- BẢNG TỔNG HỢP ---
    st.divider()
    st.subheader(L["table"])
    
    # Chuẩn bị bảng hiển thị
    v_df = df[['RANK', 'ID nhân vật', 'Tên Người Dùng', 'Sức Mạnh', 'KILL_TOTAL', 'DEAD_TOTAL', 'RESOURCES', 'KPI_SCORE']].copy()
    v_df.columns = L["cols"]
    
    # Định dạng bảng
    st.dataframe(
        v_df.style.format({
            L["cols"][3]: '{:,.0f}', 
            L["cols"][4]: '{:,.0f}', 
            L["cols"][5]: '{:,.0f}', 
            L["cols"][6]: '{:,.0f}',
            L["cols"][7]: '{:,.0f}'
        }), 
        use_container_width=True, 
        height=600
    )
else:
    st.warning("⚠️ Không thể kết nối với Google Sheet. Vui lòng kiểm tra quyền chia sẻ Link (Anyone with the link).")
